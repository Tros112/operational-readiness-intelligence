"""Read-only process CSV/hash/grain/semantic check before Power BI refresh.

Does not export, change the database, or execute M/DAX. Exit 0 passed,
1 blocked input, 2 configuration/I/O error. Keep files stable through refresh.
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
from export_process_metrics import (DEFAULT_OUTPUT, MANIFEST_NAME, DETAIL_COLUMNS,
    METRIC_COLUMNS, OUTPUT_COLUMNS, OUTPUT_KEYS, case_snapshot, period_start, selection_totals)
from load_data import BlockedLoad, require, sha256

ROOT = Path(__file__).resolve().parents[1]
DETAIL_INTS = {"correction_required", "opened_in_period", "completed_in_period", "open_at_as_of",
               "completed_cycle_days", "open_age_days"}
NULLABLE = {"closed_date", "correction_required", "completed_cycle_days", "open_age_days"}
SUMMARY_COUNTS = {"known_case_count", "opened_case_count", "completed_case_count",
                  "correction_case_count", "open_case_count"}


def integer(value: str) -> int:
    require(value.isascii() and value.isdecimal(), "Expected a nonnegative integer")
    return int(value)


def check_exports(directory: Path, config: dict) -> dict:
    date, start = config["as_of_date"], period_start(config)
    manifest = json.loads((directory / MANIFEST_NAME).read_text(encoding="utf-8"))
    require(isinstance(manifest, dict) and manifest.get("status") == "passed"
            and manifest.get("exports_ready") is True and type(manifest.get("exit_code")) is int
            and manifest["exit_code"] == 0 and manifest.get("bundle_kind") == "process",
            "Process manifest is not passed/ready; do not refresh")
    require(manifest.get("as_of_date") == date and manifest.get("period_start") == start
            and manifest.get("data_classification") == "synthetic_only"
            and manifest.get("database_matches_passed_source") is True
            and manifest.get("cross_query_reconciliation") == "passed",
            "Process manifest date/classification/reconciliation differs")
    metadata = manifest.get("files")
    require(isinstance(metadata, dict) and set(metadata) == {f"{n}.csv" for n in OUTPUT_KEYS},
            "Process manifest must identify exactly two CSVs")
    outputs, counts = {}, {}
    for name, keys in OUTPUT_KEYS.items():
        filename, entry = f"{name}.csv", metadata[f"{name}.csv"]
        require(isinstance(entry, dict) and type(entry.get("rows")) is int and entry["rows"] >= 0
                and entry.get("columns") == OUTPUT_COLUMNS[name] and entry.get("grain") == keys,
                f"Invalid process file metadata: {filename}")
        raw = (directory / filename).read_bytes()
        require(sha256(raw) == entry.get("sha256"), f"Process file/manifest hash mismatch: {filename}")
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8")))
        require(reader.fieldnames == OUTPUT_COLUMNS[name], f"Unexpected process header: {filename}")
        rows, seen = list(reader), set()
        require(len(rows) == entry["rows"], f"Process row/manifest mismatch: {filename}")
        for row in rows:
            require(None not in row and all(v is not None for v in row.values()), "Malformed process CSV row")
            key = tuple(row[k] for k in keys)
            require(all(key) and key not in seen, f"Empty/duplicate process grain: {filename}")
            seen.add(key)
            require(row["as_of_date"] == date and row["period_start"] == start
                    and row["data_classification"] == "synthetic_only", "Wrong process date/classification")
        outputs[name], counts[filename] = rows, len(rows)
    units = {r["unit_id"]: r["unit_name"] for r in config["units"]}
    detail = []
    for row in outputs["process_case_detail"]:
        for field in DETAIL_COLUMNS:
            require(field in NULLABLE or bool(row[field].strip()), f"Missing process value: {field}")
        require(row["unit_id"] in units and row["unit_name"] == units[row["unit_id"]], "Unknown process unit/label")
        for field in ("opened_date", "closed_date"):
            if row[field]:
                require(dt.date.fromisoformat(row[field]).isoformat() == row[field], "Process dates must be ISO")
        require(row["opened_date"] <= date and (not row["closed_date"]
                or row["opened_date"] <= row["closed_date"] <= date), "Invalid as-of process lifecycle")
        typed = {k: None if k in NULLABLE and v == "" else integer(v) if k in DETAIL_INTS else v
                 for k, v in row.items()}
        require(typed["correction_required"] in (None, 0, 1), "Invalid process outcome")
        require((typed["closed_date"] is None) == (typed["correction_required"] is None),
                "Open outcomes must remain unknown; completed outcomes must be known")
        canonical = case_snapshot(row, units[row["unit_id"]], date, start)
        require(typed == canonical, "Process flags/cycle/age/status disagree with dates")
        detail.append(typed)
    summary = outputs["process_unit_summary"]
    require(len(summary) == len(units) and {r["unit_id"] for r in summary} == set(units),
            "Process unit summary must retain exactly the configured units")
    for row in summary:
        require(row["unit_name"] == units[row["unit_id"]], "Process summary unit label differs")
        numeric = {}
        for field in METRIC_COLUMNS:
            text = row[field]
            value = integer(text) if field in SUMMARY_COUNTS else float(text) if text else None
            require(value is None or (math.isfinite(value) and value >= 0), "Invalid process summary number")
            numeric[field] = value
        require(numeric == selection_totals([r for r in detail if r["unit_id"] == row["unit_id"]]),
                "Process unit summary differs from case rows")
    totals = selection_totals(detail)
    require(manifest.get("global_components") == totals, "Process manifest/global case totals differ")
    selections = {"All": detail, "Unit F": [r for r in detail if r["unit_id"] == "U06"],
        "Other units": [r for r in detail if r["unit_id"] != "U06"],
        "Units A and F": [r for r in detail if r["unit_id"] in ("U01", "U06")],
        "Empty": []}
    selections.update({f"Type: {t}": [r for r in detail if r["case_type"] == t]
                       for t in sorted({r["case_type"] for r in detail})})
    return {"status": "passed", "exit_code": 0, "data_classification": "synthetic_only",
        "as_of_date": date, "period_start": start, "files_checked": len(counts), "rows": counts,
        "csv_hashes_match_manifest": True, "output_grains_unique": True,
        "process_semantics_and_unit_totals_match": True, "file_writes": 0,
        "powerbi_execution_verified": False,
        "expected_selections": {n: selection_totals(rows) for n, rows in selections.items()}}


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
