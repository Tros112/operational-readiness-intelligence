"""Create a deterministic, separately stored dirty synthetic demonstration."""

from __future__ import annotations

from collections import Counter
import copy
import datetime as dt
import json
from pathlib import Path
import argparse

import yaml

from generate_data import COLUMNS
from validate_data import require_separate_output, validate_directory, write_csv

ROOT = Path(__file__).resolve().parents[1]


def build_dirty(input_dir: Path, output_dir: Path, as_of_date: str) -> dict:
    require_separate_output(input_dir, output_dir)
    report, records = validate_directory(input_dir, as_of_date)
    if not report["load_allowed"]:
        raise ValueError("Defect injection requires a valid clean baseline")
    tables = {table: [dict(r.values) for r in rows] for table, rows in records.items()}
    defects = []

    def edit(defect_id, table, index, column, value, code):
        row = tables[table][index]
        before = copy.deepcopy(row)
        row[column] = value
        defects.append({"defect_id": defect_id, "table": table, "record_numbers": [index + 2],
                        "expected_code": code, "before": before, "after": copy.deepcopy(row)})

    def duplicate(defect_id, table, index):
        row = copy.deepcopy(tables[table][index])
        tables[table].append(row)
        defects.append({"defect_id": defect_id, "table": table,
                        "record_numbers": [index + 2, len(tables[table]) + 1],
                        "expected_code": "DUPLICATE_KEY", "before": row, "after": copy.deepcopy(row)})

    people = tables["personnel"]
    certificates = tables["personnel_qualifications"]
    counts = Counter(row["person_id"] for row in certificates)
    no_certificates = [i for i, row in enumerate(people) if counts[row["person_id"]] == 0]
    edited_certificate_people = {row["person_id"] for row in certificates[:5]}
    parent_index = next(i for i, row in enumerate(people)
                        if counts[row["person_id"]] == 1 and row["person_id"] not in edited_certificate_people)
    cascade_person = people[parent_index]["person_id"]
    cascade_record = next(i + 2 for i, row in enumerate(certificates) if row["person_id"] == cascade_person)
    cases = tables["admin_cases"]
    completed = [i for i, row in enumerate(cases) if row["closed_date"]]
    opened = [i for i, row in enumerate(cases) if not row["closed_date"]]
    missing_type = next(i for i in range(len(cases)) if i not in {completed[0], completed[1], opened[0]})

    duplicate("D01", "personnel_qualifications", 0)
    edit("D02", "personnel", no_certificates[0], "person_id", "", "MISSING_REQUIRED")
    edit("D03", "personnel_qualifications", 1, "expiration_date", "", "MISSING_REQUIRED")
    edit("D04", "personnel_qualifications", 2, "valid_from", "2026-02-30", "INVALID_DATE")
    edit("D05", "personnel_qualifications", 3, "expiration_date", certificates[3]["valid_from"], "CERTIFICATE_DATE_ORDER")
    edit("D06", "personnel_qualifications", 4, "person_id", "PX9999", "FOREIGN_KEY")
    edit("D07", "personnel", parent_index, "unit_id", "UX99", "FOREIGN_KEY")
    edit("D08", "personnel", no_certificates[1], "is_available", "2", "INVALID_FLAG")
    edit("D09", "admin_cases", missing_type, "case_type", "", "MISSING_REQUIRED")
    before_open = (dt.date.fromisoformat(cases[completed[0]]["opened_date"]) - dt.timedelta(days=1)).isoformat()
    edit("D10", "admin_cases", completed[0], "closed_date", before_open, "CASE_DATE_ORDER")
    edit("D11", "admin_cases", opened[0], "correction_required", "0", "CASE_OUTCOME_STATE")
    edit("D12", "admin_cases", completed[1], "correction_required", "", "CASE_OUTCOME_STATE")
    edit("D13", "unit_qualification_requirements", 0, "required_holder_count", "0", "NONPOSITIVE_COUNT")
    edit("D14", "unit_qualification_requirements", 1, "required_holder_count", "2.5", "INVALID_INTEGER")
    edit("D15", "unit_qualification_requirements", 2, "qualification_id", "Q99", "FOREIGN_KEY")
    duplicate("D16", "personnel", no_certificates[2])

    output_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for table, rows in tables.items():
        files[f"{table}.csv"] = write_csv(output_dir / f"{table}.csv", COLUMNS[table],
                                        [[row[column] for column in COLUMNS[table]] for row in rows])
    expected_rejected = len({(item["table"], number) for item in defects for number in item["record_numbers"]}) + 1
    expected_input = sum(file["rows"] for file in files.values())
    manifest = {
        "data_classification": "synthetic_only", "as_of_date": as_of_date,
        "source_sha256": {f"{t}.csv": m["input_sha256"] for t, m in report["tables"].items()},
        "files": files, "defects": defects,
        "expected_cascades": [{"table": "personnel_qualifications", "record_number": cascade_record,
                               "expected_code": "REJECTED_PARENT", "parent_person_id": cascade_person}],
        "expected_totals": {"input_rows": expected_input, "accepted_rows": expected_input - expected_rejected,
                            "rejected_rows": expected_rejected},
        "limits": "Bounded demonstration based on the Day 2 six-table reference. No critical value is repaired.",
    }
    (output_dir / "defect_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/project.yml")
    parser.add_argument("--input-dir", type=Path, default=ROOT / "data/raw/clean")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/raw/dirty")
    args = parser.parse_args()
    try:
        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        manifest = build_dirty(args.input_dir, args.output_dir, config["as_of_date"])
    except (OSError, ValueError, IndexError, StopIteration, KeyError, TypeError, yaml.YAMLError) as exc:
        print(json.dumps({"status": "run_error", "error": str(exc)}))
        return 2
    print(json.dumps({"status": "dirty_fixture_created", "data_classification": "synthetic_only",
                      "defect_count": len(manifest["defects"]),
                      "row_counts": {name: value["rows"] for name, value in manifest["files"].items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
