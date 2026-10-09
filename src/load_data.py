"""Load a passed synthetic snapshot into SQLite in one transaction.

Exit 0: loaded and verified. Exit 1: blocked preflight. Exit 2: configuration,
I/O, database, or audit-report error. Never load a failed diagnostic subset.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3

import yaml

from check_environment import check_config
from generate_data import COLUMNS, KEYS
from validate_data import COUNT_FIELDS, DEPENDENCY_ORDER, read_sources, validate_records

ROOT = Path(__file__).resolve().parents[1]


class BlockedLoad(ValueError):
    """The bundle or output is not approved for a load."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BlockedLoad(message)


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def protect_output(path: Path, suffixes: set[str], bundle: Path, source: Path | None = None) -> None:
    path = path.resolve()
    require(path.suffix.lower() in suffixes, f"Output must use {sorted(suffixes)}: {path}")
    require(not {".git", ".venv"}.intersection(part.lower() for part in path.parts),
            "Output must not be inside .git or .venv")
    for directory in (bundle.resolve(), ROOT / "data/raw", source):
        if directory is not None:
            directory = directory.resolve()
            require(not path.is_relative_to(directory), "Output must not overwrite input/bundle files")


def prepare_bundle(bundle: Path, config: dict) -> tuple[dict, dict]:
    """Read/hash CSVs once; keep the verified records in memory for insertion."""
    report_bytes = (bundle / "validation_report.json").read_bytes()
    report = json.loads(report_bytes)
    require(isinstance(report, dict), "Validation report must be a JSON object")
    require(report.get("validation_version") == 1, "Unsupported validation report version")
    require(report.get("status") == "passed" and report.get("load_allowed") is True
            and report.get("exit_code") == 0, "Validation bundle is blocked or unfinished")
    require(report.get("data_classification") == config["data_classification"] == "synthetic_only",
            "Synthetic-only classification required")
    require(report.get("as_of_date") == config["as_of_date"], "Validation/config analysis dates differ")
    require(not any(report.get(key) for key in ("issues", "file_errors", "batch_errors", "issue_counts"))
            and report.get("row_issue_count") == 0, "Passed report contains validation errors")
    require(isinstance(report.get("tables"), dict) and set(report["tables"]) == set(COLUMNS),
            "Report must describe exactly six tables")
    require(isinstance(report.get("input_directory"), str) and bool(report["input_directory"]),
            "Source directory is missing; rerun validation locally")
    source = Path(report["input_directory"])
    accepted, accepted_meta, accepted_errors = read_sources(bundle / "accepted")
    originals, source_meta, source_errors = read_sources(source)
    require(not accepted_errors and not source_errors, "Source/accepted CSV structure is invalid or missing")
    require(not validate_records(accepted) and not validate_records(originals)
            and not any(r.issues for tables in (accepted, originals) for rows in tables.values() for r in rows),
            "Source/accepted records no longer pass the validation rules")
    outputs = report.get("outputs", {})
    require(isinstance(outputs, dict), "Report output metadata is invalid")
    counts, hashes = {}, {}
    for table, columns in COLUMNS.items():
        summary = report["tables"][table]
        require(isinstance(summary, dict), f"Invalid table metadata: {table}")
        count = summary.get("accepted_rows")
        require(type(count) is int and count >= 0, f"Invalid accepted count: {table}")
        require(summary.get("counts_reconciled") is True and summary.get("rejected_rows") == 0
                and summary.get("input_rows") == count and summary.get("header") == columns,
                f"Inconsistent passed table metadata: {table}")
        exported = outputs.get(f"accepted/{table}.csv", {})
        require(isinstance(exported, dict), f"Invalid export metadata: {table}")
        require(exported.get("rows") == count == len(accepted[table]) == len(originals[table]),
                f"CSV/report row counts differ: {table}")
        require(summary.get("input_sha256") == source_meta[table]["input_sha256"],
                f"Source changed after validation: {table}; rerun validation")
        require(exported.get("sha256") == accepted_meta[table]["input_sha256"],
                f"Accepted export changed after validation: {table}; rerun validation")
        require([r.raw for r in originals[table]] == [r.raw for r in accepted[table]],
                f"Accepted values differ from the passed source: {table}")
        counts[table] = count
        hashes[table] = {"source": source_meta[table]["input_sha256"],
                         "accepted": accepted_meta[table]["input_sha256"]}
    total = sum(counts.values())
    require(report.get("totals") == {"input_rows": total, "accepted_rows": total,
                                     "rejected_rows": 0, "counts_reconciled": True},
            "Report totals do not reconcile to the six accepted files")
    expected = {"units": config["scope"]["unit_count"], "personnel": config["scope"]["personnel_count"],
                "qualification_types": config["scope"]["qualification_type_count"],
                "admin_cases": config["scope"]["admin_case_count"]}
    require(all(counts[table] == count for table, count in expected.items()),
            "Snapshot counts differ from configured scope")
    require({r.values["unit_id"] for r in accepted["units"]} == {u["unit_id"] for u in config["units"]}
            and {r.values["qualification_id"] for r in accepted["qualification_types"]}
            == {q["qualification_id"] for q in config["qualification_types"]},
            "Snapshot parent IDs differ from configured scope")
    metadata = {"validation_report_sha256": sha256(report_bytes), "source_directory": str(source.resolve()),
                "accepted_counts": counts, "file_hashes": hashes}
    return accepted, metadata


def sql_statements(ddl: str) -> list[str]:
    """The checked-in scaffold has one statement ending per line, plus comments."""
    statements, pending = [], ""
    for line in ddl.splitlines(keepends=True):
        pending += line
        if sqlite3.complete_statement(pending):
            statements.append(pending)
            pending = ""
    require(not pending.strip(), "Schema contains an unfinished SQL statement")
    return statements


def table_schema(connection: sqlite3.Connection) -> dict:
    return {name: re.sub(r"\s+", " ", sql).strip() for name, sql in connection.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}


def expected_schema(statements: list[str]) -> dict:
    connection = sqlite3.connect(":memory:", isolation_level=None)
    try:
        for statement in statements:
            connection.execute(statement)
        schema = table_schema(connection)
        require(set(schema) == set(COLUMNS), "Schema must define exactly the six project tables")
        return schema
    finally:
        connection.close()


def typed_values(table: str, raw: list[str]) -> tuple:
    numbers = {COUNT_FIELDS.get(table)}
    if table == "personnel":
        numbers.add("is_available")
    elif table == "admin_cases":
        numbers.add("correction_required")
    # Only the two optional case fields can be blank after successful validation.
    return tuple(None if value == "" else int(value.lstrip("0") or "0") if column in numbers else value
                 for column, value in zip(COLUMNS[table], raw))


def insert_records(connection: sqlite3.Connection, table: str, values: list[tuple]) -> None:
    columns = ",".join(COLUMNS[table])
    placeholders = ",".join("?" for _ in COLUMNS[table])
    connection.executemany(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)


def load_bundle(bundle: Path, database: Path, config: dict, schema_path: Path | None = None) -> dict:
    check_config(config)
    protect_output(database, {".sqlite3", ".sqlite", ".db"}, bundle)
    require(sqlite3.sqlite_version_info >= (3, 37, 0), "SQLite >= 3.37 is required for STRICT tables")
    records, metadata = prepare_bundle(bundle, config)
    protect_output(database, {".sqlite3", ".sqlite", ".db"}, bundle, Path(metadata["source_directory"]))
    schema_bytes = (schema_path or ROOT / "sql/schema.sql").read_bytes()
    statements = sql_statements(schema_bytes.decode("utf-8"))
    expected = expected_schema(statements)
    values = {table: [typed_values(table, r.raw) for r in rows] for table, rows in records.items()}
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database, isolation_level=None)
    try:
        connection.execute("PRAGMA foreign_keys = ON")  # Must precede BEGIN on every connection.
        require(connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1, "Foreign keys are disabled")
        connection.execute("BEGIN IMMEDIATE")
        existing = table_schema(connection)
        require(not existing or existing == expected, "Existing database is not the compatible project schema")
        # executescript() can commit a pending transaction; execute each DDL statement instead.
        for statement in statements:
            connection.execute(statement)
        for table in reversed(DEPENDENCY_ORDER):
            connection.execute(f"DELETE FROM {table}")
        for table in DEPENDENCY_ORDER:
            insert_records(connection, table, values[table])
        counts, snapshot = {}, {}
        for table in COLUMNS:
            rows = connection.execute(f"SELECT {','.join(COLUMNS[table])} FROM {table} "
                                      f"ORDER BY {','.join(KEYS[table])}").fetchall()
            indexes = [COLUMNS[table].index(key) for key in KEYS[table]]
            require(rows == sorted(values[table], key=lambda row: tuple(row[i] for i in indexes)),
                    f"Database values differ from verified accepted records: {table}")
            counts[table], snapshot[table] = len(rows), rows
        require(counts == metadata["accepted_counts"], "Database/accepted counts differ")
        require(connection.execute("PRAGMA foreign_key_check").fetchall() == [], "Foreign-key audit failed")
        integrity = [row[0] for row in connection.execute("PRAGMA integrity_check")]
        require(integrity == ["ok"], "SQLite integrity check failed")
        open_cases = connection.execute("SELECT COUNT(*) FROM admin_cases WHERE closed_date IS NULL "
                                        "AND correction_required IS NULL").fetchone()[0]
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return {"status": "loaded", "exit_code": 0, "database_updated": True,
            "data_classification": "synthetic_only", "as_of_date": config["as_of_date"],
            "database_path": str(database.resolve()), "bundle_path": str(bundle.resolve()),
            "load_mode": "replace_all_six_tables_in_one_transaction", **metadata,
            "schema_sha256": sha256(schema_bytes), "database_counts": counts,
            "total_rows": sum(counts.values()), "counts_reconciled": True,
            "foreign_keys_enabled_for_load_connection": True, "foreign_key_check": "passed",
            "integrity_check": "ok", "open_cases_with_null_outcomes": open_cases,
            "logical_data_sha256": sha256(json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode())}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/project.yml")
    parser.add_argument("--bundle-dir", type=Path, default=ROOT / "data/processed/validation_clean")
    parser.add_argument("--database", type=Path)
    parser.add_argument("--report-path", type=Path, default=ROOT / "data/processed/load_report.json")
    args = parser.parse_args(argv)
    result = {"status": "in_progress", "database_updated": False, "data_classification": "synthetic_only"}
    report_ready = False
    try:
        protect_output(args.report_path, {".json"}, args.bundle_dir)
        # Also guard custom source folders before invalidating the previous audit.
        try:
            envelope = json.loads((args.bundle_dir / "validation_report.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            envelope = {}
        if isinstance(envelope, dict) and isinstance(envelope.get("input_directory"), str):
            protect_output(args.report_path, {".json"}, args.bundle_dir, Path(envelope["input_directory"]))
        args.report_path.parent.mkdir(parents=True, exist_ok=True)
        args.report_path.write_text(json.dumps(result) + "\n", encoding="utf-8")
        report_ready = True  # Invalidate old success before configuration/preflight.
        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        check_config(config)
        database = args.database if args.database is not None else ROOT / config["database"]["path"]
        require(database.resolve() != args.report_path.resolve(), "Database and report paths must differ")
        result = load_bundle(args.bundle_dir, database, config)
    except BlockedLoad as error:
        result = {"status": "blocked", "exit_code": 1, "database_updated": False, "error": str(error)}
    except (OSError, ValueError, TypeError, KeyError, sqlite3.DatabaseError, yaml.YAMLError) as error:
        result = {"status": "load_failed", "exit_code": 2, "database_updated": False, "error": str(error)}
    if report_ready:
        try:
            args.report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except OSError as error:
            result.update(status="audit_report_error", exit_code=2, error=str(error))
            # If commit already succeeded, retain database_updated=True in console output.
    print(json.dumps(result, indent=2, sort_keys=True))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
