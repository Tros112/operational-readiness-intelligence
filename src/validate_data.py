"""Validate six synthetic CSV sources; quarantine errors and block bad batches.

Exit 0: passed. Exit 1: row/batch failures. Exit 2: input/output structure error.
No persistent database is created and no critical value is repaired.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass, field
import datetime as dt
import hashlib
import io
import itertools
import json
from pathlib import Path
import re

import yaml

from generate_data import COLUMNS, KEYS

ROOT = Path(__file__).resolve().parents[1]
FOREIGN_KEYS = {
    "personnel": [("unit_id", "units", "unit_id")],
    "personnel_qualifications": [("person_id", "personnel", "person_id"),
                                 ("qualification_id", "qualification_types", "qualification_id")],
    "unit_qualification_requirements": [("unit_id", "units", "unit_id"),
                                        ("qualification_id", "qualification_types", "qualification_id")],
    "admin_cases": [("unit_id", "units", "unit_id")],
}
DEPENDENCY_ORDER = ["units", "qualification_types", "personnel",
                    "personnel_qualifications", "unit_qualification_requirements", "admin_cases"]
COUNT_FIELDS = {"units": "required_personnel_count",
                "unit_qualification_requirements": "required_holder_count"}
DATE_FIELDS = {"personnel_qualifications": ["valid_from", "expiration_date"],
               "admin_cases": ["opened_date", "closed_date"]}


@dataclass
class Record:
    number: int
    raw: list[str]
    values: dict[str, str]
    issues: list[dict] = field(default_factory=list)

    def reject(self, code: str, column: str, message: str) -> None:
        if not any(issue["code"] == code and issue["field"] == column for issue in self.issues):
            self.issues.append({"code": code, "field": column, "message": message})


def parse_date(value: str) -> dt.date:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("Expected YYYY-MM-DD")
    return dt.date.fromisoformat(value)


def read_sources(input_dir: Path) -> tuple[dict, dict, list]:
    tables, metadata, errors = {}, {}, []
    for table, columns in COLUMNS.items():
        path = input_dir / f"{table}.csv"
        tables[table] = []
        metadata[table] = {"input_rows": None, "input_sha256": None}
        try:
            content = path.read_bytes()
            metadata[table]["input_sha256"] = hashlib.sha256(content).hexdigest()
            rows = list(csv.reader(io.StringIO(content.decode("utf-8"), newline=""), strict=True))
        except (OSError, UnicodeError, csv.Error) as exc:
            errors.append({"table": table, "code": "INPUT_READ_ERROR", "message": str(exc)})
            continue
        header = rows[0] if rows else []
        metadata[table].update(input_rows=max(len(rows) - 1, 0), header=header)
        if header != columns:
            errors.append({"table": table, "code": "FILE_SCHEMA", "message": "Headers must match exactly"})
        for number, raw in enumerate(rows[1:], start=2):
            usable = header == columns and len(raw) == len(columns)
            record = Record(number, raw, dict(zip(columns, raw)) if usable else {})
            if header != columns:
                record.reject("FILE_SCHEMA", "", "Cannot interpret records under an invalid header")
            elif len(raw) != len(columns):
                record.reject("ROW_WIDTH", "", f"Expected {len(columns)} cells, received {len(raw)}")
                errors.append({"table": table, "code": "ROW_WIDTH", "record_number": number,
                               "message": "Record has the wrong number of cells"})
            tables[table].append(record)
    if input_dir.is_dir():
        for path in sorted(input_dir.iterdir()):
            if path.is_file() and path.suffix.lower() == ".csv" and path.name not in {
                f"{table}.csv" for table in COLUMNS
            }:
                errors.append({"table": "", "code": "EXTRA_CSV", "message": path.name})
    return tables, metadata, errors


def check_local_fields(table: str, record: Record) -> None:
    values = record.values
    if not values:  # Structural errors already explain why this record is unusable.
        return
    optional = {"closed_date", "correction_required"} if table == "admin_cases" else set()
    for column, value in values.items():
        if column not in optional and not value.strip():
            record.reject("MISSING_REQUIRED", column, "Required value is blank")
        if column.endswith("_id") and value.strip() and value != value.strip():
            record.reject("PADDED_IDENTIFIER", column, "Identifier has surrounding whitespace")
    count_field = COUNT_FIELDS.get(table)
    if count_field and values[count_field].strip():
        value = values[count_field]
        if not re.fullmatch(r"[0-9]+", value):
            record.reject("INVALID_INTEGER", count_field, "Expected a positive integer string")
        elif not value.strip("0"):
            record.reject("NONPOSITIVE_COUNT", count_field, "Requirement must be greater than zero")
        elif len(value.lstrip("0")) > 19 or (len(value.lstrip("0")) == 19 and value.lstrip("0") > str(2**63 - 1)):
            record.reject("INTEGER_RANGE", count_field, "Value exceeds SQLite signed 64-bit range")
    flag_field = "is_available" if table == "personnel" else "correction_required" if table == "admin_cases" else None
    if flag_field and values[flag_field] != "" and values[flag_field] not in ("0", "1"):
        record.reject("INVALID_FLAG", flag_field, "Known flags must be exactly 0 or 1")
    dates = {}
    for column in DATE_FIELDS.get(table, []):
        value = values[column]
        if not value.strip() and column not in optional:
            continue  # Already recorded as missing.
        if column in optional and value == "":
            continue
        try:
            dates[column] = parse_date(value)
        except ValueError:
            record.reject("INVALID_DATE", column, "Expected a real calendar date in YYYY-MM-DD")
    if table == "personnel_qualifications" and len(dates) == 2:
        if dates["expiration_date"] <= dates["valid_from"]:
            record.reject("CERTIFICATE_DATE_ORDER", "expiration_date", "Expiration must follow valid_from")
    if table == "admin_cases":
        if len(dates) == 2 and dates["closed_date"] < dates["opened_date"]:
            record.reject("CASE_DATE_ORDER", "closed_date", "Completion precedes opening")
        if (values["closed_date"] == "") != (values["correction_required"] == ""):
            record.reject("CASE_OUTCOME_STATE", "correction_required", "Open outcome must be blank; closed outcome must be known")


def validate_records(tables: dict) -> list[dict]:
    for table, records in tables.items():
        groups = defaultdict(list)
        for record in records:
            check_local_fields(table, record)
            key = tuple(record.values.get(column, "") for column in KEYS[table])
            if all(value.strip() for value in key):
                groups[key].append(record)
        for records_with_key in groups.values():
            if len(records_with_key) > 1:
                for record in records_with_key:
                    record.reject("DUPLICATE_KEY", ",".join(KEYS[table]), "Every record sharing this key is quarantined")
    for table in DEPENDENCY_ORDER:
        for column, parent, parent_column in FOREIGN_KEYS.get(table, []):
            known = {r.values[parent_column] for r in tables[parent] if r.values.get(parent_column, "").strip()}
            accepted = {r.values[parent_column] for r in tables[parent] if not r.issues}
            for record in tables[table]:
                value = record.values.get(column, "")
                if value.strip() and value not in accepted:
                    code = "REJECTED_PARENT" if value in known else "FOREIGN_KEY"
                    record.reject(code, column, f"Reference does not resolve to an accepted {parent} record")
    batch_errors = []
    for table in ("units", "qualification_types"):
        if not any(not record.issues for record in tables[table]):
            batch_errors.append({"table": table, "code": "EMPTY_REQUIRED_TABLE", "message": "No accepted parent records"})
    units = {r.values["unit_id"] for r in tables["units"] if not r.issues}
    qualifications = {r.values["qualification_id"] for r in tables["qualification_types"] if not r.issues}
    required = {(r.values["unit_id"], r.values["qualification_id"])
                for r in tables["unit_qualification_requirements"] if not r.issues}
    missing = sorted(set(itertools.product(units, qualifications)) - required)
    if missing:
        batch_errors.append({"table": "unit_qualification_requirements", "code": "MISSING_REQUIREMENT_PAIRS",
                             "pairs": [list(pair) for pair in missing], "message": "Required pairs are missing or rejected"})
    return batch_errors


def validate_directory(input_dir: Path, as_of_date: str) -> tuple[dict, dict]:
    parse_date(as_of_date)
    tables, metadata, file_errors = read_sources(input_dir)
    batch_errors = validate_records(tables)
    summaries, issues = {}, []
    for table, records in tables.items():
        accepted = sum(not record.issues for record in records)
        rejected = len(records) - accepted
        source_count = metadata[table]["input_rows"]
        summaries[table] = {**metadata[table], "accepted_rows": accepted, "rejected_rows": rejected,
                            "counts_reconciled": source_count is not None and source_count == accepted + rejected}
        for record in records:
            issues.extend({"table": table, "record_number": record.number, **issue} for issue in record.issues)
    total_accepted = sum(s["accepted_rows"] for s in summaries.values())
    total_rejected = sum(s["rejected_rows"] for s in summaries.values())
    known_counts = all(s["input_rows"] is not None for s in summaries.values())
    input_count = sum(s["input_rows"] for s in summaries.values()) if known_counts else None
    passed = not (file_errors or batch_errors or total_rejected)
    exit_code = 2 if file_errors else 0 if passed else 1
    report = {
        "validation_version": 1, "data_classification": "synthetic_only", "as_of_date": as_of_date,
        "input_directory": str(input_dir.resolve()), "status": "passed" if passed else "input_error" if file_errors else "validation_failed",
        "load_allowed": passed, "exit_code": exit_code, "tables": summaries,
        "totals": {"input_rows": input_count, "accepted_rows": total_accepted, "rejected_rows": total_rejected,
                   "counts_reconciled": all(s["counts_reconciled"] for s in summaries.values())},
        "row_issue_count": len(issues), "issue_counts": dict(sorted(Counter(i["code"] for i in issues).items())),
        "file_errors": file_errors, "batch_errors": batch_errors, "issues": issues,
    }
    return report, tables


def require_separate_output(input_dir: Path, output_dir: Path) -> None:
    output = output_dir.resolve()
    for source in (input_dir.resolve(), (ROOT / "data/raw/clean").resolve()):
        if output == source or output.is_relative_to(source) or source.is_relative_to(output):
            raise ValueError("Output must not overlap the input or canonical clean-reference directory")


def write_csv(path: Path, columns: list[str], rows: list[list]) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)
    return {"rows": len(rows), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def write_result(output_dir: Path, report: dict, tables: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "validation_report.json"
    report_path.write_text(json.dumps({"status": "in_progress", "load_allowed": False}) + "\n", encoding="utf-8")
    outputs, rejected = {}, []
    for table, records in tables.items():
        relative = f"accepted/{table}.csv"
        outputs[relative] = write_csv(output_dir / relative, COLUMNS[table], [r.raw for r in records if not r.issues])
        for record in records:
            if record.issues:
                key = {column: record.values.get(column) for column in KEYS[table]}
                rejected.append([table, record.number, json.dumps(key, sort_keys=True),
                                 "|".join(sorted({i["code"] for i in record.issues})), json.dumps(record.raw)])
    outputs["rejected_rows.csv"] = write_csv(output_dir / "rejected_rows.csv",
        ["table", "record_number", "key_json", "reason_codes", "raw_record_json"], rejected)
    outputs["validation_issues.csv"] = write_csv(output_dir / "validation_issues.csv",
        ["table", "record_number", "code", "field", "message"],
        [[i[c] for c in ["table", "record_number", "code", "field", "message"]] for i in report["issues"]])
    report["outputs"] = outputs
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/project.yml")
    parser.add_argument("--input-dir", type=Path, default=ROOT / "data/raw/clean")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed/validation_clean")
    args = parser.parse_args()
    output_ready = False
    try:
        require_separate_output(args.input_dir, args.output_dir)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "validation_report.json").write_text(
            json.dumps({"status": "in_progress", "load_allowed": False}) + "\n", encoding="utf-8")
        output_ready = True
        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        report, tables = validate_directory(args.input_dir, config["as_of_date"])
        write_result(args.output_dir, report, tables)
    except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
        failure = {"status": "run_error", "load_allowed": False, "exit_code": 2, "error": str(exc)}
        if output_ready:
            try:
                (args.output_dir / "validation_report.json").write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
            except OSError:
                pass  # The console still reports failure if the output folder becomes unwritable.
        print(json.dumps(failure))
        return 2
    print(json.dumps({k: report[k] for k in ["status", "data_classification", "as_of_date", "load_allowed", "exit_code", "totals"]}, indent=2))
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
