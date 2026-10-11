"""Read-only Day 6 export check before importing or refreshing Power BI.

Exit 0: passed manifest, file hashes, and output grains. Exit 1: blocked inputs.
Exit 2: configuration/I/O error. This does not run Power BI, re-export data,
verify the database again, or authorize a file changed after the check.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

import yaml

from check_environment import check_config
from export_metrics import OUTPUT_KEYS
from load_data import BlockedLoad, require, sha256

ROOT = Path(__file__).resolve().parents[1]
SUMMARY_COMPONENTS = (
    "available_personnel_count", "required_personnel_count", "staffing_gap",
    "capped_holder_slots", "required_holder_slots", "qualification_gap",
    "qualification_pairs_with_gap", "unit_attention_flag",
)


def selection_totals(rows: list[dict]) -> dict:
    totals = {name: sum(row[name] for row in rows) for name in SUMMARY_COMPONENTS}
    totals["staffing_coverage_ratio"] = (
        totals["available_personnel_count"] / totals["required_personnel_count"]
        if totals["required_personnel_count"] else None)
    totals["qualification_coverage_ratio"] = (
        totals["capped_holder_slots"] / totals["required_holder_slots"]
        if totals["required_holder_slots"] else None)
    totals["flagged_units"] = totals.pop("unit_attention_flag")
    totals["unit_count"] = len(rows)
    return totals


def check_exports(directory: Path, as_of_date: str) -> dict:
    """Verify the saved export bundle without writing any file."""
    manifest_path = directory / "export_manifest.json"
    require(manifest_path.is_file(), "Missing export_manifest.json; do not refresh")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(isinstance(manifest, dict), "Export manifest must be an object")
    require(manifest.get("status") == "passed" and manifest.get("exports_ready") is True
            and type(manifest.get("exit_code")) is int and manifest["exit_code"] == 0,
            "Export manifest is not passed/ready; do not refresh")
    require(manifest.get("as_of_date") == as_of_date
            and manifest.get("data_classification") == "synthetic_only"
            and manifest.get("database_matches_passed_source") is True
            and manifest.get("cross_query_reconciliation") == "passed",
            "Export date/classification/reconciliation is not approved")
    metadata = manifest.get("files")
    require(isinstance(metadata, dict)
            and set(metadata) == {f"{name}.csv" for name in OUTPUT_KEYS},
            "Manifest must identify exactly three dashboard CSVs")
    outputs, counts = {}, {}
    for name, keys in OUTPUT_KEYS.items():
        filename = f"{name}.csv"
        entry = metadata[filename]
        require(isinstance(entry, dict) and entry.get("grain") == keys
                and type(entry.get("rows")) is int and entry["rows"] >= 0,
                f"Invalid manifest entry: {filename}")
        path = directory / filename
        require(path.is_file(), f"Missing CSV: {filename}")
        raw = path.read_bytes()
        require(sha256(raw) == entry.get("sha256"), f"File/manifest hash mismatch: {filename}")
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8")))
        fields = reader.fieldnames
        require(isinstance(fields, list) and fields == entry.get("columns")
                and len(set(fields)) == len(fields)
                and set(keys + ["data_classification"]).issubset(fields),
                f"Header/manifest mismatch: {filename}")
        rows = list(reader)
        require(len(rows) == entry["rows"], f"Row/manifest mismatch: {filename}")
        seen = set()
        for row in rows:
            require(None not in row and all(value is not None for value in row.values()),
                    f"Malformed CSV record: {filename}")
            require(row["as_of_date"] == as_of_date
                    and row["data_classification"] == "synthetic_only",
                    f"Wrong date/classification: {filename}")
            key = tuple(row[field] for field in keys)
            require(all(key) and key not in seen, f"Empty or duplicate grain: {filename}")
            seen.add(key)
        outputs[name], counts[filename] = rows, len(rows)

    summary = outputs["unit_summary"]
    require(bool(summary), "Unit summary is empty")
    for row in summary:
        for field in SUMMARY_COMPONENTS:
            text = row.get(field, "")
            require(text.isascii() and text.isdecimal(), f"Invalid nonnegative count: {field}")
            row[field] = int(text)
        require(row["unit_attention_flag"] in (0, 1), "Attention flag must be zero or one")
        require(row["capped_holder_slots"] <= row["required_holder_slots"],
                "Covered qualification slots exceed demand")
        require(row["staffing_gap"] == max(
                    row["required_personnel_count"] - row["available_personnel_count"], 0)
                and row["qualification_gap"] == (
                    row["required_holder_slots"] - row["capped_holder_slots"]),
                "Summary count/gap components disagree")
        require(row["unit_attention_flag"] == int(
                    row["staffing_gap"] > 0 or row["qualification_pairs_with_gap"] > 0),
                "Attention flag disagrees with current gaps")

    selections = {
        "All units": summary,
        "Unit A": [row for row in summary if row["unit_id"] == "U01"],
        "Unit C": [row for row in summary if row["unit_id"] == "U03"],
        "Units A and C": [row for row in summary if row["unit_id"] in ("U01", "U03")],
    }
    return {"status": "passed", "exit_code": 0, "data_classification": "synthetic_only",
            "as_of_date": as_of_date, "files_checked": len(counts), "rows": counts,
            "csv_hashes_match_manifest": True, "output_grains_unique": True,
            "file_writes": 0, "powerbi_execution_verified": False,
            "expected_selections": {name: selection_totals(rows) for name, rows in selections.items()}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-dir", type=Path, default=ROOT / "data/processed/dashboard")
    parser.add_argument("--config", type=Path, default=ROOT / "config/project.yml")
    args = parser.parse_args(argv)
    try:
        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        check_config(config)
        result = check_exports(args.export_dir, config["as_of_date"])
    except BlockedLoad as error:
        result = {"status": "blocked", "exit_code": 1, "error": str(error), "file_writes": 0}
    except (OSError, ValueError, yaml.YAMLError, TypeError, KeyError) as error:
        result = {"status": "check_failed", "exit_code": 2, "error": str(error), "file_writes": 0}
    print(json.dumps(result, indent=2, sort_keys=True))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
