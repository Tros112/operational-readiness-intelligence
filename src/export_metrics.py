"""Export current synthetic staffing/qualification metrics from a verified database.

Exit 0: complete CSV bundle. Exit 1: blocked input/output. Exit 2: config, I/O,
SQL, or manifest error. A non-passed manifest must not feed a Power BI refresh.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import sqlite3
import tempfile

import yaml

from check_environment import check_config
from generate_data import COLUMNS, KEYS
from load_data import BlockedLoad, prepare_bundle, protect_output, require, sha256, typed_values

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_KEYS = {
    "unit_summary": ["unit_id", "as_of_date"],
    "qualification_detail": ["unit_id", "qualification_id", "as_of_date"],
    "expiration_detail": ["person_id", "qualification_id", "as_of_date"],
}


def protect_directory(output: Path, bundle: Path, source: Path | None = None) -> None:
    require(not output.is_file(), "Export output must be a directory, not an existing file")
    for name in OUTPUT_KEYS:
        protect_output(output / f"{name}.csv", {".csv"}, bundle, source)
    protect_output(output / "export_manifest.json", {".json"}, bundle, source)


def verify_database(connection: sqlite3.Connection, records: dict) -> dict:
    """Compare all six persisted tables with the passed in-memory accepted source."""
    counts, snapshot = {}, {}
    tables = {row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    require(tables == set(COLUMNS), "Database must contain exactly six source tables")
    for table in COLUMNS:
        actual = [tuple(row) for row in connection.execute(
            f"SELECT {','.join(COLUMNS[table])} FROM {table} ORDER BY {','.join(KEYS[table])}")]
        indexes = [COLUMNS[table].index(key) for key in KEYS[table]]
        expected = sorted([typed_values(table, r.raw) for r in records[table]],
                          key=lambda row: tuple(row[i] for i in indexes))
        require(actual == expected, f"Database differs from passed source: {table}; rerun clean load")
        counts[table], snapshot[table] = len(actual), actual
    require(not connection.execute("PRAGMA foreign_key_check").fetchall(), "Database FK audit failed")
    require([row[0] for row in connection.execute("PRAGMA integrity_check")] == ["ok"],
            "Database integrity audit failed")
    return {"source_table_counts": counts, "database_matches_passed_source": True,
            "logical_data_sha256": sha256(json.dumps(snapshot, sort_keys=True,
                                                     separators=(",", ":")).encode())}


def query_metrics(connection: sqlite3.Connection, as_of_date: str) -> tuple[dict, dict, dict]:
    outputs, columns, sql_hashes = {}, {}, {}
    for name in OUTPUT_KEYS:
        sql_bytes = (ROOT / "sql" / f"{name}.sql").read_bytes()
        cursor = connection.execute(sql_bytes.decode("utf-8"), {"as_of_date": as_of_date})
        columns[name] = [field[0] for field in cursor.description]
        outputs[name] = [dict(zip(columns[name], row)) for row in cursor.fetchall()]
        sql_hashes[name] = sha256(sql_bytes)
    return outputs, columns, sql_hashes


def reconcile_outputs(outputs: dict, records: dict, config: dict) -> None:
    date = config["as_of_date"]
    for name, keys in OUTPUT_KEYS.items():
        rows = outputs[name]
        require(len({tuple(row[key] for key in keys) for row in rows}) == len(rows),
                f"Export grain is not unique: {name}")
        require(all(row["as_of_date"] == date and row["data_classification"] == "synthetic_only"
                    for row in rows), f"Export date/classification differs: {name}")
    units = {row["unit_id"]: row for row in outputs["unit_summary"]}
    require(set(units) == {r.values["unit_id"] for r in records["units"]}, "Unit export is incomplete")
    pairs = {(r.values["unit_id"], r.values["qualification_id"])
             for r in records["unit_qualification_requirements"]}
    require({(r["unit_id"], r["qualification_id"]) for r in outputs["qualification_detail"]} == pairs,
            "Qualification export lost a requirement pair")
    valid_keys = {(r.values["person_id"], r.values["qualification_id"])
                  for r in records["personnel_qualifications"]
                  if r.values["valid_from"] <= date < r.values["expiration_date"]}
    require({(r["person_id"], r["qualification_id"]) for r in outputs["expiration_detail"]} == valid_keys,
            "Expiration export differs from the current valid inventory")
    for unit_id, unit in units.items():
        detail = [r for r in outputs["qualification_detail"] if r["unit_id"] == unit_id]
        for summary, field in (("required_holder_slots", "required_holder_count"),
                               ("capped_holder_slots", "capped_holder_count"),
                               ("qualification_gap", "current_gap")):
            require(unit[summary] == sum(r[field] for r in detail),
                    f"Unit/qualification aggregates disagree: {unit_id}/{summary}")
        certs = [r for r in outputs["expiration_detail"] if r["unit_id"] == unit_id]
        for horizon in (30, 60, 90):
            selected = [r for r in certs if r[f"expires_within_{horizon}_days"]]
            require(unit[f"certificates_expiring_{horizon}_days"] == len(selected)
                    and unit[f"people_affected_{horizon}_days"] == len({r["person_id"] for r in selected}),
                    f"Unit/expiration aggregates disagree: {unit_id}/{horizon}")


def export_snapshot(bundle: Path, database: Path, output: Path, config: dict) -> dict:
    check_config(config)
    records, metadata = prepare_bundle(bundle, config)
    protect_directory(output, bundle, Path(metadata["source_directory"]))
    # mode=ro never creates a missing database. One read transaction holds the same
    # snapshot across verification and all three queries, even during a later reload.
    connection = sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True, isolation_level=None)
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.execute("BEGIN")
        verified = verify_database(connection, records)
        outputs, columns, sql_hashes = query_metrics(connection, config["as_of_date"])
        reconcile_outputs(outputs, records, config)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    output.mkdir(parents=True, exist_ok=True)
    files = {}
    # Prepare every CSV first; then replace the three fixed targets. This is not a
    # filesystem transaction. The CLI only writes a passed manifest after all replacements.
    with tempfile.TemporaryDirectory(prefix="ori-export-", dir=output) as staging:
        for name, rows in outputs.items():
            path = Path(staging) / f"{name}.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=columns[name], lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)  # None becomes blank, retaining undefined ratios.
            files[path.name] = {"rows": len(rows), "columns": columns[name],
                                "grain": OUTPUT_KEYS[name], "sha256": sha256(path.read_bytes())}
        for filename in files:
            os.replace(Path(staging) / filename, output / filename)
    units = outputs["unit_summary"]
    available = sum(r["available_personnel_count"] for r in units)
    required = sum(r["required_personnel_count"] for r in units)
    capped = sum(r["capped_holder_slots"] for r in units)
    slots = sum(r["required_holder_slots"] for r in units)
    return {"export_version": 1, "status": "passed", "exit_code": 0, "exports_ready": True,
            "data_classification": "synthetic_only", "as_of_date": config["as_of_date"],
            "database_path": str(database.resolve()), "output_directory": str(output.resolve()),
            **verified, "validation_report_sha256": metadata["validation_report_sha256"],
            "sql_sha256": sql_hashes, "files": files, "cross_query_reconciliation": "passed",
            "global_components": {"available_personnel_count": available,
                "required_personnel_count": required, "staffing_gap": sum(r["staffing_gap"] for r in units),
                "staffing_coverage_ratio": available / required if required else None,
                "capped_holder_slots": capped, "required_holder_slots": slots,
                "qualification_gap": sum(r["qualification_gap"] for r in units),
                "qualification_coverage_ratio": capped / slots if slots else None}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/project.yml")
    parser.add_argument("--database", type=Path)
    parser.add_argument("--bundle-dir", type=Path, default=ROOT / "data/processed/validation_clean")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed/dashboard")
    args = parser.parse_args(argv)
    manifest = args.output_dir / "export_manifest.json"
    result = {"export_version": 1, "status": "in_progress", "exports_ready": False,
              "data_classification": "synthetic_only"}
    manifest_ready = False
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
        manifest_ready = True  # A failed rerun cannot leave an old passed authorization.
        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        check_config(config)
        database = args.database if args.database is not None else ROOT / config["database"]["path"]
        result = export_snapshot(args.bundle_dir, database, args.output_dir, config)
    except BlockedLoad as error:
        result = {"status": "blocked", "exit_code": 1, "exports_ready": False, "error": str(error)}
    except (OSError, ValueError, TypeError, KeyError, sqlite3.DatabaseError, yaml.YAMLError) as error:
        result = {"status": "export_failed", "exit_code": 2, "exports_ready": False, "error": str(error)}
    if manifest_ready:
        try:
            manifest.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except OSError as error:
            result.update(status="manifest_write_failed", exit_code=2, exports_ready=False, error=str(error))
    print(json.dumps(result, indent=2, sort_keys=True))
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
