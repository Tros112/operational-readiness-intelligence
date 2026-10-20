"""Read-only scenario CSV/hash/grain/arithmetic check before Power BI refresh.

Exit 0 passed, 1 blocked input, 2 configuration/I/O error. Does not export,
write the database, or execute M/DAX. Keep inputs stable through refresh.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import math
from pathlib import Path

import yaml

from check_environment import check_config
from export_qualification_scenario import (ASSUMPTIONS, DEFAULT_OUTPUT, DETAIL_COLUMNS,
    HORIZONS, MANIFEST_NAME, METRIC_COLUMNS, OUTPUT_COLUMNS, OUTPUT_KEYS, RATIO_COLUMNS,
    check_horizons, pair_snapshot, selection_totals)
from load_data import BlockedLoad, require, sha256

ROOT = Path(__file__).resolve().parents[1]
TEXT_COLUMNS = {"data_classification", "scenario", "unit_id", "unit_name", "qualification_id",
                "qualification_name"}
DATE_COLUMNS = {"as_of_date", "horizon_date"}
DETAIL_INTS = set(DETAIL_COLUMNS) - TEXT_COLUMNS - DATE_COLUMNS - set(RATIO_COLUMNS)


def integer(value: str) -> int:
    require(value.isascii() and value.isdecimal(), "Expected a nonnegative scenario integer")
    return int(value)


def ratio(value: str) -> float | None:
    number = float(value) if value else None
    require(number is None or math.isfinite(number) and 0 <= number <= 1,
            "Scenario coverage must be a finite capped ratio or blank")
    return number


def check_exports(directory: Path, config: dict) -> dict:
    check_horizons(config)
    date = config["as_of_date"]
    manifest = json.loads((directory / MANIFEST_NAME).read_text(encoding="utf-8"))
    require(isinstance(manifest, dict) and manifest.get("status") == "passed"
            and manifest.get("exports_ready") is True and type(manifest.get("exit_code")) is int
            and manifest["exit_code"] == 0 and manifest.get("bundle_kind") == "qualification_scenario",
            "Scenario manifest is not passed/ready; do not refresh")
    require(manifest.get("as_of_date") == date and manifest.get("scenario") == "no_renewal"
            and manifest.get("data_classification") == "synthetic_only"
            and manifest.get("horizons_days") == list(HORIZONS)
            and manifest.get("assumptions") == ASSUMPTIONS
            and manifest.get("database_matches_passed_source") is True
            and manifest.get("cross_query_reconciliation") == "passed", "Scenario metadata/assumptions differ")
    metadata = manifest.get("files")
    require(isinstance(metadata, dict) and set(metadata) == {f"{n}.csv" for n in OUTPUT_KEYS},
            "Scenario manifest must identify exactly two CSVs")
    outputs, counts = {}, {}
    for name, keys in OUTPUT_KEYS.items():
        filename, entry = f"{name}.csv", metadata[f"{name}.csv"]
        require(isinstance(entry, dict) and type(entry.get("rows")) is int and entry["rows"] >= 0
                and entry.get("columns") == OUTPUT_COLUMNS[name] and entry.get("grain") == keys,
                f"Invalid scenario file metadata: {filename}")
        raw = (directory / filename).read_bytes()
        require(sha256(raw) == entry.get("sha256"), f"Scenario file/manifest hash mismatch: {filename}")
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8")))
        require(reader.fieldnames == OUTPUT_COLUMNS[name], f"Unexpected scenario CSV header: {filename}")
        rows, seen = list(reader), set()
        require(len(rows) == entry["rows"], f"Scenario row/manifest mismatch: {filename}")
        for row in rows:
            require(None not in row and all(v is not None for v in row.values()), "Malformed scenario CSV row")
            key = tuple(row[k] for k in keys)
            require(all(key) and key not in seen, f"Empty/duplicate scenario grain: {filename}")
            seen.add(key)
            require(row["as_of_date"] == date and row["data_classification"] == "synthetic_only"
                    and row["scenario"] == "no_renewal", "Wrong scenario date/classification")
        outputs[name], counts[filename] = rows, len(rows)
    units = {r["unit_id"]: r for r in config["units"]}
    qualifications = {r["qualification_id"]: r for r in config["qualification_types"]}
    detail = []
    for row in outputs["qualification_scenario"]:
        require(all(row[k].strip() for k in TEXT_COLUMNS), "Missing scenario text value")
        require(row["unit_id"] in units and row["qualification_id"] in qualifications,
                "Unknown scenario unit/qualification")
        typed = {k: integer(v) if k in DETAIL_INTS else ratio(v) if k in RATIO_COLUMNS else v
                 for k, v in row.items()}
        require(typed["horizon_days"] in HORIZONS, "Unsupported scenario horizon")
        require(typed["required_holder_count"] > 0, "Approved scenario requirements must be positive")
        require(typed["projected_eligible_holder_count"] <= typed["current_eligible_holder_count"],
                "No-renewal projected holders cannot increase")
        canonical = pair_snapshot(units[row["unit_id"]], qualifications[row["qualification_id"]],
            typed, typed["current_eligible_holder_count"], typed["projected_eligible_holder_count"],
            date, typed["horizon_days"])
        require(typed == canonical, "Scenario labels/flags/caps/gaps/ratios disagree with holder counts")
        detail.append(typed)
    require(len(detail) == len(units) * len(qualifications) * len(HORIZONS)
            and {(r["unit_id"], r["qualification_id"], r["horizon_days"]) for r in detail}
            == {(u, q, h) for u in units for q in qualifications for h in HORIZONS},
            "Scenario must retain every unit/qualification at all three horizons")
    current_fields = ["required_holder_count", "current_eligible_holder_count", "current_gap",
                      "current_capped_holder_count", "current_coverage_ratio", "current_is_gap", "current_is_fragile"]
    for unit in units:
        for qualification in qualifications:
            rows = sorted((r for r in detail if r["unit_id"] == unit and r["qualification_id"] == qualification),
                          key=lambda r: r["horizon_days"])
            require(all([r[k] for k in current_fields] == [rows[0][k] for k in current_fields] for r in rows),
                    "Current baseline must be identical across scenario horizons")
            require(all(a["projected_eligible_holder_count"] >= b["projected_eligible_holder_count"]
                        for a, b in zip(rows, rows[1:])), "No-renewal holders cannot increase at later horizons")
    summary = outputs["scenario_unit_summary"]
    require(len(summary) == len(units) * len(HORIZONS)
            and {(r["unit_id"], integer(r["horizon_days"])) for r in summary}
            == {(u, h) for u in units for h in HORIZONS}, "Scenario unit/horizon summary is incomplete")
    for row in summary:
        horizon = integer(row["horizon_days"])
        require(row["unit_name"] == units[row["unit_id"]]["unit_name"]
                and row["horizon_date"] == (dt.date.fromisoformat(date) + dt.timedelta(days=horizon)).isoformat(),
                "Wrong scenario summary labels/horizon date")
        numeric = {k: ratio(row[k]) if k in RATIO_COLUMNS else integer(row[k]) for k in METRIC_COLUMNS}
        selected = [r for r in detail if r["unit_id"] == row["unit_id"] and r["horizon_days"] == horizon]
        require(numeric == selection_totals(selected), "Scenario unit totals differ from pair rows")
    totals = {str(h): selection_totals([r for r in detail if r["horizon_days"] == h]) for h in HORIZONS}
    require(manifest.get("global_components_by_horizon") == totals, "Scenario global/manifest totals differ")
    selections = {
        "All": lambda r: True,
        "Unit D / Q04": lambda r: r["unit_id"] == "U04" and r["qualification_id"] == "Q04",
        "Unit C / Q06": lambda r: r["unit_id"] == "U03" and r["qualification_id"] == "Q06",
        "Unit B / Q03": lambda r: r["unit_id"] == "U02" and r["qualification_id"] == "Q03",
        "A+C / Q01+Q02": lambda r: r["unit_id"] in ("U01", "U03") and r["qualification_id"] in ("Q01", "Q02"),
        "Empty": lambda r: False,
    }
    return {"status": "passed", "exit_code": 0, "data_classification": "synthetic_only",
        "scenario": "no_renewal", "as_of_date": date, "horizons_days": list(HORIZONS),
        "files_checked": len(counts), "rows": counts, "csv_hashes_match_manifest": True,
        "output_grains_unique": True, "scenario_semantics_monotonicity_and_unit_totals_match": True,
        "file_writes": 0, "powerbi_execution_verified": False,
        "expected_selections_by_horizon": {str(h): {name: selection_totals(
            [r for r in detail if r["horizon_days"] == h and predicate(r)])
            for name, predicate in selections.items()} for h in HORIZONS}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--config", type=Path, default=ROOT / "config/project.yml")
    args = parser.parse_args(argv)
    try:
        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        check_config(config)
        result = check_exports(args.export_dir, config)
    except BlockedLoad as error:
        result = {"status": "blocked", "exit_code": 1, "error": str(error), "file_writes": 0}
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as error:
        result = {"status": "check_failed", "exit_code": 2, "error": str(error), "file_writes": 0}
    print(json.dumps(result, indent=2, sort_keys=True))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
