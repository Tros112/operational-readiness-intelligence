"""Read-only Day 9 process export, separate from the accepted Day 5 bundle.

Exit 0: passed process bundle. Exit 1: blocked inputs/output. Exit 2: I/O,
configuration, SQL, or manifest error. Never refresh from a non-passed manifest.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
from pathlib import Path
import sqlite3
import statistics
import tempfile

import yaml

from check_environment import check_config
from export_metrics import verify_database
from load_data import BlockedLoad, prepare_bundle, protect_output, require, sha256

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data/processed/dashboard/process"
MANIFEST_NAME = "process_export_manifest.json"
DETAIL_COLUMNS = ["data_classification", "as_of_date", "period_start", "case_id", "unit_id",
    "unit_name", "case_type", "opened_date", "closed_date", "correction_required", "status_at_as_of",
    "opened_in_period", "completed_in_period", "open_at_as_of", "completed_cycle_days", "open_age_days"]
METRIC_COLUMNS = ["known_case_count", "opened_case_count", "completed_case_count", "correction_case_count",
    "discrepancy_rate", "median_completed_cycle_days", "open_case_count", "median_open_age_days", "max_open_age_days"]
SUMMARY_COLUMNS = ["data_classification", "as_of_date", "period_start", "unit_id", "unit_name"] + METRIC_COLUMNS
OUTPUT_KEYS = {"process_case_detail": ["case_id", "as_of_date"],
               "process_unit_summary": ["unit_id", "as_of_date"]}
OUTPUT_COLUMNS = {"process_case_detail": DETAIL_COLUMNS, "process_unit_summary": SUMMARY_COLUMNS}


def period_start(config: dict) -> str:
    return (dt.date.fromisoformat(config["as_of_date"])
            - dt.timedelta(days=config["scope"]["admin_lookback_days"] - 1)).isoformat()


def protect_directory(output: Path, bundle: Path, source: Path | None = None) -> None:
    require(not output.is_file(), "Process output must be a directory")
    for name in OUTPUT_KEYS:
        protect_output(output / f"{name}.csv", {".csv"}, bundle, source)
    protect_output(output / MANIFEST_NAME, {".json"}, bundle, source)


def case_snapshot(raw: dict, unit_name: str, date: str, start: str) -> dict:
    """Independent calendar calculation used to reconcile SQL against source rows."""
    opened = dt.date.fromisoformat(raw["opened_date"])
    end, first = dt.date.fromisoformat(date), dt.date.fromisoformat(start)
    closed = dt.date.fromisoformat(raw["closed_date"]) if raw["closed_date"] else None
    completed = closed is not None and closed <= end
    in_period = completed and first <= closed
    return dict(zip(DETAIL_COLUMNS, ["synthetic_only", date, start, raw["case_id"], raw["unit_id"],
        unit_name, raw["case_type"], opened.isoformat(), closed.isoformat() if completed else None,
        int(raw["correction_required"]) if completed else None, "Completed" if completed else "Open",
        int(first <= opened <= end), int(in_period), int(not completed),
        (closed - opened).days if in_period else None, (end - opened).days if not completed else None]))


def selection_totals(rows: list[dict]) -> dict:
    """Recompute rates/medians from selected case rows, never unit medians."""
    completed = [r for r in rows if r["completed_in_period"] == 1]
    ages = [r["open_age_days"] for r in rows if r["open_at_as_of"] == 1]
    cycles = [r["completed_cycle_days"] for r in completed]
    corrections = sum(r["correction_required"] for r in completed)
    return dict(zip(METRIC_COLUMNS, [len(rows), sum(r["opened_in_period"] for r in rows),
        len(completed), corrections, corrections / len(completed) if completed else None,
        statistics.median(cycles) if cycles else None, len(ages),
        statistics.median(ages) if ages else None, max(ages) if ages else None]))


def query_totals(connection: sqlite3.Connection, date: str, start: str,
                 unit_ids: list[str] | None = None, case_types: list[str] | None = None) -> dict:
    sql = (ROOT / "sql/process_metrics.sql").read_text(encoding="utf-8")
    params, conditions = {"as_of_date": date, "period_start": start}, []
    for field, values in (("unit_id", unit_ids), ("case_type", case_types)):
        if values is None:
            continue
        names = [f"{field}_{i}" for i in range(len(values))]
        params.update(zip(names, values))
        conditions.append(f"c.{field} IN ({','.join(':' + n for n in names)})" if names else "0")
    sql = sql.replace("/*SCOPE*/ 1 = 1", " AND ".join(conditions) if conditions else "1 = 1")
    cursor = connection.execute(sql, params)
    return dict(zip([c[0] for c in cursor.description], cursor.fetchone()))


def query_outputs(connection: sqlite3.Connection, date: str, start: str) -> tuple[dict, dict]:
    sql = (ROOT / "sql/process_case_detail.sql").read_text(encoding="utf-8")
    cursor = connection.execute(sql, {"as_of_date": date, "period_start": start})
    require([c[0] for c in cursor.description] == DETAIL_COLUMNS, "Unexpected process SQL schema")
    detail = [dict(zip(DETAIL_COLUMNS, row)) for row in cursor.fetchall()]
    summary = []
    for unit_id, unit_name in connection.execute("SELECT unit_id, unit_name FROM units ORDER BY unit_id"):
        summary.append({"data_classification": "synthetic_only", "as_of_date": date,
            "period_start": start, "unit_id": unit_id, "unit_name": unit_name,
            **query_totals(connection, date, start, [unit_id])})
    return {"process_case_detail": detail, "process_unit_summary": summary}, query_totals(connection, date, start)


def reconcile_outputs(outputs: dict, totals: dict, records: dict, config: dict) -> None:
    date, start = config["as_of_date"], period_start(config)
    units = {r.values["unit_id"]: r.values["unit_name"] for r in records["units"]}
    expected = [case_snapshot(r.values, units[r.values["unit_id"]], date, start)
                for r in records["admin_cases"] if r.values["opened_date"] <= date]
    detail = outputs["process_case_detail"]
    require(sorted(detail, key=lambda r: r["case_id"]) == sorted(expected, key=lambda r: r["case_id"]),
            "Process case SQL differs from independent source-date calculations")
    require(totals == selection_totals(expected), "Global process SQL/reference differs")
    summary = outputs["process_unit_summary"]
    require({r["unit_id"] for r in summary} == set(units) and len(summary) == len(units),
            "Process unit summary must retain every unit, including units with no cases")
    for row in summary:
        require({k: row[k] for k in METRIC_COLUMNS}
                == selection_totals([r for r in expected if r["unit_id"] == row["unit_id"]]),
                f"Unit process SQL/reference differs: {row['unit_id']}")
    for name, rows in outputs.items():
        require(len({tuple(r[k] for k in OUTPUT_KEYS[name]) for r in rows}) == len(rows),
                f"Process grain is not unique: {name}")
        require(all(r["as_of_date"] == date and r["period_start"] == start
                    and r["data_classification"] == "synthetic_only" for r in rows),
                f"Process date/classification differs: {name}")


def export_snapshot(bundle: Path, database: Path, output: Path, config: dict) -> dict:
    check_config(config)
    records, metadata = prepare_bundle(bundle, config)
    protect_directory(output, bundle, Path(metadata["source_directory"]))
    connection = sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True, isolation_level=None)
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.execute("BEGIN")
        verified = verify_database(connection, records)
        outputs, totals = query_outputs(connection, config["as_of_date"], period_start(config))
        reconcile_outputs(outputs, totals, records, config)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    output.mkdir(parents=True, exist_ok=True)
    files = {}
    with tempfile.TemporaryDirectory(prefix="ori-process-export-", dir=output) as staging:
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
    return {"export_version": 1, "bundle_kind": "process", "status": "passed", "exit_code": 0,
        "exports_ready": True, "as_of_date": config["as_of_date"], "period_start": period_start(config),
        "data_classification": "synthetic_only", "database_path": str(database.resolve()),
        "output_directory": str(output.resolve()), **verified,
        "validation_report_sha256": metadata["validation_report_sha256"],
        "sql_sha256": {n: sha256((ROOT / "sql" / f"{n}.sql").read_bytes())
                       for n in ("process_case_detail", "process_metrics")},
        "files": files, "cross_query_reconciliation": "passed", "global_components": totals}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/project.yml")
    parser.add_argument("--database", type=Path)
    parser.add_argument("--bundle-dir", type=Path, default=ROOT / "data/processed/validation_clean")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    manifest, ready = args.output_dir / MANIFEST_NAME, False
    result = {"export_version": 1, "bundle_kind": "process", "status": "in_progress", "exports_ready": False}
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
