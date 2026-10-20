"""Export the synthetic no-renewal scenario without changing prior bundles.

Exit 0: passed scenario bundle. Exit 1: blocked inputs/output. Exit 2: I/O,
configuration, SQL, or manifest error. A failed manifest never permits refresh.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
from pathlib import Path
import sqlite3
import tempfile

import yaml

from check_environment import check_config
from export_metrics import verify_database
from load_data import BlockedLoad, prepare_bundle, protect_output, require, sha256

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data/processed/dashboard/scenario"
MANIFEST_NAME = "scenario_export_manifest.json"
HORIZONS = (30, 60, 90)
ASSUMPTIONS = {
    "no_renewals": True,
    "staffing_unit_membership_and_availability": "held_at_as_of_date",
    "eligible_cohort": "available_and_currently_valid_at_as_of_date",
    "future_start_certificates": "excluded",
    "expiration_rule": "expiration_date_on_or_before_horizon_is_removed",
    "simultaneous_assignments": "not_modeled",
}
DETAIL_COLUMNS = ["data_classification", "scenario", "as_of_date", "horizon_days", "horizon_date",
    "unit_id", "unit_name", "qualification_id", "qualification_name", "required_holder_count",
    "current_eligible_holder_count", "projected_eligible_holder_count", "eligible_holders_lost",
    "current_capped_holder_count", "projected_capped_holder_count", "current_gap", "projected_gap",
    "additional_gap", "current_coverage_ratio", "projected_coverage_ratio", "current_is_gap",
    "projected_is_gap", "is_new_gap", "current_is_fragile", "projected_is_fragile"]
SUM_FIELDS = {
    "required_holder_slots": "required_holder_count",
    "current_eligible_holder_slots": "current_eligible_holder_count",
    "projected_eligible_holder_slots": "projected_eligible_holder_count",
    "eligible_holder_slots_lost": "eligible_holders_lost",
    "current_capped_holder_slots": "current_capped_holder_count",
    "projected_capped_holder_slots": "projected_capped_holder_count",
    "current_gap": "current_gap", "projected_gap": "projected_gap", "additional_gap": "additional_gap",
    "current_pairs_with_gap": "current_is_gap", "projected_pairs_with_gap": "projected_is_gap",
    "new_gap_pairs": "is_new_gap", "current_fragile_pairs": "current_is_fragile",
    "projected_fragile_pairs": "projected_is_fragile",
}
RATIO_COLUMNS = ["current_coverage_ratio", "projected_coverage_ratio"]
METRIC_COLUMNS = ["qualification_pair_count", *SUM_FIELDS, *RATIO_COLUMNS]
SUMMARY_COLUMNS = ["data_classification", "scenario", "as_of_date", "horizon_days", "horizon_date",
                   "unit_id", "unit_name", *METRIC_COLUMNS]
OUTPUT_KEYS = {
    "qualification_scenario": ["unit_id", "qualification_id", "horizon_days", "as_of_date"],
    "scenario_unit_summary": ["unit_id", "horizon_days", "as_of_date"],
}
OUTPUT_COLUMNS = {"qualification_scenario": DETAIL_COLUMNS, "scenario_unit_summary": SUMMARY_COLUMNS}


def check_horizons(config: dict) -> None:
    require(config["scope"]["outlook_days"] == list(HORIZONS),
            "Scenario horizons must be the contracted 30, 60, and 90 days")


def protect_directory(output: Path, bundle: Path, source: Path | None = None) -> None:
    require(not output.is_file(), "Scenario output must be a directory")
    for name in OUTPUT_KEYS:
        protect_output(output / f"{name}.csv", {".csv"}, bundle, source)
    protect_output(output / MANIFEST_NAME, {".json"}, bundle, source)


def pair_snapshot(unit: dict, qualification: dict, requirement: dict, current: int,
                  projected: int, date: str, horizon: int) -> dict:
    """Independent arithmetic shared by source reconciliation and CSV semantics."""
    required = int(requirement["required_holder_count"])
    current_cap, projected_cap = min(current, required), min(projected, required)
    current_gap, projected_gap = max(required - current, 0), max(required - projected, 0)
    horizon_date = (dt.date.fromisoformat(date) + dt.timedelta(days=horizon)).isoformat()
    return dict(zip(DETAIL_COLUMNS, ["synthetic_only", "no_renewal", date, horizon, horizon_date,
        unit["unit_id"], unit["unit_name"], qualification["qualification_id"],
        qualification["qualification_name"], required, current, projected, current - projected,
        current_cap, projected_cap, current_gap, projected_gap, projected_gap - current_gap,
        current_cap / required if required else None, projected_cap / required if required else None,
        int(current_gap > 0), int(projected_gap > 0), int(current_gap == 0 and projected_gap > 0),
        int(required > 0 and current == required), int(required > 0 and projected == required)]))


def selection_totals(rows: list[dict]) -> dict:
    require(len({r["horizon_days"] for r in rows}) <= 1,
            "Select one scenario horizon; requirements repeat across horizons")
    totals = {"qualification_pair_count": len(rows)}
    totals.update({name: sum(r[field] for r in rows) for name, field in SUM_FIELDS.items()})
    required = totals["required_holder_slots"]
    totals.update({f"{scope}_coverage_ratio": totals[f"{scope}_capped_holder_slots"] / required
                   if required else None for scope in ("current", "projected")})
    return totals


def detail_sql() -> str:
    return (ROOT / "sql/qualification_scenario.sql").read_text(encoding="utf-8").rstrip().rstrip(";")


def query_totals(connection: sqlite3.Connection, date: str, horizon: int,
                 unit_ids: list[str] | None = None,
                 qualification_ids: list[str] | None = None) -> dict:
    require(type(horizon) is int and horizon in HORIZONS, "Unsupported scenario horizon")
    sql = (ROOT / "sql/qualification_scenario_totals.sql").read_text(encoding="utf-8")
    sql = sql.replace("/*SCENARIO_DETAIL*/", detail_sql())
    params, conditions = {"as_of_date": date, "horizon_days": horizon}, []
    for field, values in (("unit_id", unit_ids), ("qualification_id", qualification_ids)):
        if values is None:
            continue
        names = [f"{field}_{i}" for i in range(len(values))]
        params.update(zip(names, values))
        conditions.append(f"d.{field} IN ({','.join(':' + n for n in names)})" if names else "0")
    sql = sql.replace("/*SCOPE*/ 1 = 1", " AND ".join(conditions) if conditions else "1 = 1")
    cursor = connection.execute(sql, params)
    require([c[0] for c in cursor.description] == METRIC_COLUMNS, "Unexpected scenario totals schema")
    return dict(zip(METRIC_COLUMNS, cursor.fetchone()))


def query_outputs(connection: sqlite3.Connection, date: str) -> tuple[dict, dict]:
    detail, summary, totals = [], [], {}
    units = list(connection.execute("SELECT unit_id, unit_name FROM units ORDER BY unit_id"))
    for horizon in HORIZONS:
        cursor = connection.execute(detail_sql(), {"as_of_date": date, "horizon_days": horizon})
        require([c[0] for c in cursor.description] == DETAIL_COLUMNS, "Unexpected scenario detail schema")
        detail.extend(dict(zip(DETAIL_COLUMNS, row)) for row in cursor.fetchall())
        for unit_id, unit_name in units:
            summary.append({"data_classification": "synthetic_only", "scenario": "no_renewal",
                "as_of_date": date, "horizon_days": horizon,
                "horizon_date": (dt.date.fromisoformat(date) + dt.timedelta(days=horizon)).isoformat(),
                "unit_id": unit_id, "unit_name": unit_name,
                **query_totals(connection, date, horizon, [unit_id])})
        totals[str(horizon)] = query_totals(connection, date, horizon)
    return {"qualification_scenario": detail, "scenario_unit_summary": summary}, totals


def reconcile_outputs(outputs: dict, totals: dict, records: dict, config: dict) -> None:
    date = config["as_of_date"]
    day = dt.date.fromisoformat(date)
    units = {r.values["unit_id"]: r.values for r in records["units"]}
    qualifications = {r.values["qualification_id"]: r.values for r in records["qualification_types"]}
    people = {r.values["person_id"]: r.values for r in records["personnel"]}
    current, surviving = {}, {h: {} for h in HORIZONS}
    for record in records["personnel_qualifications"]:
        certificate = record.values
        person = people[certificate["person_id"]]
        expiry = dt.date.fromisoformat(certificate["expiration_date"])
        if int(person["is_available"]) != 1 or not (
                dt.date.fromisoformat(certificate["valid_from"]) <= day < expiry):
            continue
        key = person["unit_id"], certificate["qualification_id"]
        current.setdefault(key, set()).add(person["person_id"])
        for horizon in HORIZONS:
            if expiry > day + dt.timedelta(days=horizon):
                surviving[horizon].setdefault(key, set()).add(person["person_id"])
    expected = []
    for horizon in HORIZONS:
        for record in records["unit_qualification_requirements"]:
            requirement = record.values
            key = requirement["unit_id"], requirement["qualification_id"]
            expected.append(pair_snapshot(units[key[0]], qualifications[key[1]], requirement,
                len(current.get(key, set())), len(surviving[horizon].get(key, set())), date, horizon))
    order = lambda r: (r["horizon_days"], r["unit_id"], r["qualification_id"])
    require(sorted(outputs["qualification_scenario"], key=order) == sorted(expected, key=order),
            "Scenario SQL differs from independent current-cohort/date calculations")
    summary = outputs["scenario_unit_summary"]
    require(len(summary) == len(units) * len(HORIZONS)
            and {(r["unit_id"], r["horizon_days"]) for r in summary}
                == {(u, h) for u in units for h in HORIZONS}, "Scenario unit summary is incomplete")
    for row in summary:
        selected = [r for r in expected if r["horizon_days"] == row["horizon_days"]
                    and r["unit_id"] == row["unit_id"]]
        require({k: row[k] for k in METRIC_COLUMNS} == selection_totals(selected),
                "Scenario unit totals differ from independent pair calculations")
    for horizon in HORIZONS:
        require(totals[str(horizon)] == selection_totals([r for r in expected if r["horizon_days"] == horizon]),
                "Scenario global totals differ from independent pair calculations")
    for name, keys in OUTPUT_KEYS.items():
        rows = outputs[name]
        require(len({tuple(r[k] for k in keys) for r in rows}) == len(rows), f"Duplicate scenario grain: {name}")
        require(all(r["as_of_date"] == date and r["data_classification"] == "synthetic_only"
                    and r["scenario"] == "no_renewal" for r in rows), "Wrong scenario metadata")


def export_snapshot(bundle: Path, database: Path, output: Path, config: dict) -> dict:
    check_config(config)
    check_horizons(config)
    records, metadata = prepare_bundle(bundle, config)
    protect_directory(output, bundle, Path(metadata["source_directory"]))
    connection = sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True, isolation_level=None)
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.execute("BEGIN")
        verified = verify_database(connection, records)
        outputs, totals = query_outputs(connection, config["as_of_date"])
        reconcile_outputs(outputs, totals, records, config)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    output.mkdir(parents=True, exist_ok=True)
    files = {}
    with tempfile.TemporaryDirectory(prefix="ori-scenario-export-", dir=output) as staging:
        for name, rows in outputs.items():
            path = Path(staging) / f"{name}.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=OUTPUT_COLUMNS[name], lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
            files[path.name] = {"rows": len(rows), "columns": OUTPUT_COLUMNS[name],
                "grain": OUTPUT_KEYS[name], "sha256": sha256(path.read_bytes())}
        for filename in files:
            os.replace(Path(staging) / filename, output / filename)
    return {"export_version": 1, "bundle_kind": "qualification_scenario", "scenario": "no_renewal",
        "status": "passed", "exit_code": 0, "exports_ready": True, "data_classification": "synthetic_only",
        "as_of_date": config["as_of_date"], "horizons_days": list(HORIZONS), "assumptions": ASSUMPTIONS,
        "database_path": str(database.resolve()), "output_directory": str(output.resolve()), **verified,
        "validation_report_sha256": metadata["validation_report_sha256"],
        "sql_sha256": {n: sha256((ROOT / "sql" / f"{n}.sql").read_bytes())
                       for n in ("qualification_scenario", "qualification_scenario_totals")},
        "files": files, "cross_query_reconciliation": "passed", "global_components_by_horizon": totals}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/project.yml")
    parser.add_argument("--database", type=Path)
    parser.add_argument("--bundle-dir", type=Path, default=ROOT / "data/processed/validation_clean")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    manifest, ready = args.output_dir / MANIFEST_NAME, False
    result = {"export_version": 1, "bundle_kind": "qualification_scenario",
              "status": "in_progress", "exports_ready": False}
    try:
        protect_directory(args.output_dir, args.bundle_dir)
        try:
            envelope = json.loads((args.bundle_dir / "validation_report.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            envelope = {}
        if isinstance(envelope, dict) and isinstance(envelope.get("input_directory"), str):
            protect_directory(args.output_dir, args.bundle_dir, Path(envelope["input_directory"]))
        args.output_dir.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps(result) + "\n", encoding="utf-8")
        ready = True
        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        check_config(config)
        database = args.database if args.database is not None else ROOT / config["database"]["path"]
        result = export_snapshot(args.bundle_dir, database, args.output_dir, config)
    except BlockedLoad as error:
        result = {"status": "blocked", "exit_code": 1, "exports_ready": False, "error": str(error)}
    except (OSError, ValueError, TypeError, KeyError, sqlite3.DatabaseError, yaml.YAMLError) as error:
        result = {"status": "export_failed", "exit_code": 2, "exports_ready": False, "error": str(error)}
    if ready:
        try:
            manifest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except OSError as error:
            result.update(status="manifest_write_failed", exit_code=2, exports_ready=False, error=str(error))
    print(json.dumps(result, indent=2, sort_keys=True))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
