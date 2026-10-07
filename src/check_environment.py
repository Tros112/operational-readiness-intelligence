"""Check the Day 1 foundation without generating or loading operational data.

Run from any directory: python path/to/src/check_environment.py
Only package names/versions and presence of connection keys are reported.
No credentials or environment variable values are printed.
"""

from __future__ import annotations

import datetime as dt
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TABLES = {
    "units", "personnel", "qualification_types", "personnel_qualifications",
    "unit_qualification_requirements", "admin_cases",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_config(config: dict) -> dict:
    require(config["data_classification"] == "synthetic_only", "Synthetic-only classification required")
    require(config["database"]["engine"] == "sqlite", "Recorded fallback is SQLite")
    analysis_date = dt.date.fromisoformat(config["as_of_date"])
    require(analysis_date.isoformat() == config["as_of_date"], "Use canonical ISO analysis date")
    require(type(config["seed"]) is int, "Seed must be an integer")
    units, qualifications, scope = config["units"], config["qualification_types"], config["scope"]
    require(len(units) == scope["unit_count"] == 6, "Expected six units")
    require(len(qualifications) == scope["qualification_type_count"] == 8, "Expected eight qualifications")
    unit_ids = {row["unit_id"] for row in units}
    qualification_ids = {row["qualification_id"] for row in qualifications}
    require(len(unit_ids) == len(units), "Duplicate configured unit IDs")
    require(len(qualification_ids) == len(qualifications), "Duplicate configured qualification IDs")
    require(sum(row["personnel_count"] for row in units) == scope["personnel_count"] == 300,
            "Personnel allocations must total 300")
    require(all(0 < row["required_personnel_count"] <= row["personnel_count"] for row in units),
            "Staffing requirements must be positive and within configured population")
    require(scope["outlook_days"] == [30, 60, 90], "Expected cumulative 30/60/90 horizons")
    require(scope["admin_lookback_days"] == 90 and scope["admin_case_count"] > 0,
            "Expected positive case count and 90-day lookback")
    scenarios = config["scenarios"]
    require(set(scenarios) == {
        "staffing_shortfall", "fragile_qualification", "renewal_cluster", "discrepancy_hotspot"
    }, "Expected the four documented planted scenarios")
    for scenario in scenarios.values():
        require(scenario["unit_id"] in unit_ids, "Scenario references an unknown unit")
        if "qualification_id" in scenario:
            require(scenario["qualification_id"] in qualification_ids, "Unknown scenario qualification")
    shortfall = scenarios["staffing_shortfall"]
    unit = next(row for row in units if row["unit_id"] == shortfall["unit_id"])
    require(0 <= shortfall["available_personnel_count"] < unit["required_personnel_count"],
            "Staffing scenario must actually define a shortfall")
    fragile = scenarios["fragile_qualification"]
    require(fragile["required_holder_count"] == fragile["valid_available_holder_count"] == 1,
            "Fragile scenario must define a single-holder dependency")
    cluster = scenarios["renewal_cluster"]
    require(len(cluster["expiration_offsets_days"]) == cluster["valid_available_holder_count"],
            "Renewal cluster count and offsets disagree")
    require(all(0 < offset <= 30 for offset in cluster["expiration_offsets_days"]),
            "Renewal offsets must be within the inclusive 30-day window")
    for probability in (
        config["background"]["availability_probability"],
        config["background"]["open_case_probability"],
        config["background"]["completed_case_correction_probability"],
        scenarios["discrepancy_hotspot"]["completed_case_correction_probability"],
    ):
        require(0 <= probability <= 1, "Probabilities must be in [0, 1]")
    return {
        "status": "passed", "as_of_date": analysis_date.isoformat(),
        "unit_count": len(units), "personnel_target": scope["personnel_count"],
        "qualification_type_count": len(qualifications),
        "case_target": scope["admin_case_count"], "scenario_count": len(scenarios),
        "administrative_window_start": (analysis_date - dt.timedelta(days=89)).isoformat(),
        "horizon_end_dates": {
            str(days): (analysis_date + dt.timedelta(days=days)).isoformat()
            for days in scope["outlook_days"]
        },
    }


def check_schema() -> dict:
    require(sqlite3.sqlite_version_info >= (3, 37, 0), "SQLite >= 3.37 is required for STRICT tables")
    ddl = (ROOT / "sql/schema.sql").read_text(encoding="utf-8")
    with sqlite3.connect(":memory:") as connection:
        connection.executescript(ddl)
        # Repeat DDL only; this does not prove the future loader is idempotent.
        connection.executescript(ddl)
        actual = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )}
        require(actual == TABLES, "Schema must contain exactly the six source tables")
        foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()[0]
        require(foreign_keys == 1, "Foreign-key enforcement must be enabled")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        require(integrity == "ok", "Empty schema integrity check failed")
    return {"status": "passed", "table_names": sorted(actual), "foreign_keys_enabled": True,
            "repeated_ddl": "passed", "database": "empty in-memory scaffold only"}


def package_versions() -> dict:
    versions = {}
    for name in ("PyYAML", "pandas", "numpy", "psycopg", "psycopg2", "pytest"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def git_inventory() -> dict:
    if not shutil.which("git"):
        return {"available": False, "project_worktree": False}
    version = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
    worktree = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                              cwd=ROOT, capture_output=True, text=True)
    return {"available": True, "version": version.stdout.strip(),
            "project_worktree": worktree.returncode == 0 and worktree.stdout.strip() == "true"}


def postgres_inventory() -> dict:
    with socket.socket() as connection:
        connection.settimeout(1)
        reachable = connection.connect_ex(("127.0.0.1", 5432)) == 0
    return {
        "executables": {name: bool(shutil.which(name)) for name in ("psql", "postgres", "pg_ctl", "pg_isready")},
        "localhost_5432_accepting_connections": reachable,
        "connection_environment_keys_present": [
            name for name in ("DATABASE_URL", "PGHOST", "PGPORT", "PGDATABASE", "PGUSER")
            if name in os.environ
        ],
        "authentication_verified": False,
        "selected_project_engine": "sqlite",
    }


def main() -> int:
    report = {
        "checked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "schedule_timezone": "America/Los_Angeles", "operating_system": platform.system(),
        "python": {"version": platform.python_version(), "executable": sys.executable},
        "sqlite_version": sqlite3.sqlite_version, "packages": package_versions(),
        "powerbi": {"assistant_report_created": False, "assistant_pbix_verified": False,
                    "user_windows_access": "pending confirmation",
                    "report_build_owner": "user on Windows"},
    }
    try:
        require(sys.version_info >= (3, 11), "Python >= 3.11 is required")
        import yaml

        config = yaml.safe_load((ROOT / "config/project.yml").read_text(encoding="utf-8"))
        report["configuration"] = check_config(config)
        report["schema"] = check_schema()
        report["git"] = git_inventory()
        report["postgresql"] = postgres_inventory()
        report["status"] = "passed"
    except (ImportError, ValueError, KeyError, OSError, sqlite3.DatabaseError,
            subprocess.SubprocessError) as error:
        report["status"] = "failed"
        report["error"] = str(error)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
