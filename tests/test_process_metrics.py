"""Process chronology, correct medians/denominators, and export failure gates."""
from contextlib import closing, redirect_stdout
import csv
import datetime as dt
import io
import json
from pathlib import Path
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import check_process_input
import export_process_metrics as process
from load_data import BlockedLoad, load_bundle, sha256
from validate_data import validate_directory, write_result

DATE, START = "2026-10-07", "2026-07-10"


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def fixture(cases):
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE units(unit_id TEXT, unit_name TEXT)")
    connection.executemany("INSERT INTO units VALUES (?,?)", [("U01", "Unit A"), ("U02", "Unit B")])
    connection.execute("CREATE TABLE admin_cases(case_id TEXT, unit_id TEXT, case_type TEXT, "
                       "opened_date TEXT, closed_date TEXT, correction_required INTEGER)")
    connection.executemany("INSERT INTO admin_cases VALUES (?,?,?,?,?,?)", cases)
    return connection


class ProcessSQLTests(unittest.TestCase):
    def test_period_boundaries_older_backlog_and_future_events(self):
        cases = [("old_closed", "U01", "x", "2026-06-01", "2026-07-09", 1),
            ("first_completion", "U01", "x", "2026-07-08", START, 1),
            ("same_day", "U01", "x", START, START, 0),
            ("last_completion", "U01", "x", DATE, DATE, 0),
            ("older_backlog", "U01", "x", "2026-06-01", None, None),
            ("open_today", "U01", "x", DATE, None, None),
            ("future_close", "U01", "x", "2026-10-06", "2026-10-08", 1),
            ("future_open", "U01", "x", "2026-10-08", None, None)]
        with closing(fixture(cases)) as connection:
            output, total = process.query_outputs(connection, DATE, START)
        rows = {r["case_id"]: r for r in output["process_case_detail"]}
        self.assertNotIn("future_open", rows)
        self.assertEqual((total["known_case_count"], total["opened_case_count"], total["completed_case_count"]), (7, 4, 3))
        self.assertEqual((total["correction_case_count"], total["discrepancy_rate"]), (1, 1 / 3))
        self.assertEqual((total["median_completed_cycle_days"], total["open_case_count"],
                          total["median_open_age_days"], total["max_open_age_days"]), (0, 3, 1, 128))
        self.assertEqual(rows["first_completion"]["completed_cycle_days"], 2)
        self.assertIsNone(rows["old_closed"]["completed_cycle_days"])
        self.assertEqual(rows["future_close"]["status_at_as_of"], "Open")
        self.assertIsNone(rows["future_close"]["closed_date"])
        self.assertIsNone(rows["future_close"]["correction_required"])
        self.assertEqual(rows["older_backlog"]["opened_in_period"], 0)

    def test_actual_even_and_odd_medians_recomputed_for_selected_cases(self):
        end = dt.date.fromisoformat(DATE)
        cases = [(str(i), unit, "x", (end - dt.timedelta(days=days)).isoformat(), DATE, 0)
                 for i, (unit, days) in enumerate([("U01", 0), ("U01", 1), ("U01", 2), ("U02", 100)])]
        with closing(fixture(cases)) as connection:
            output, total = process.query_outputs(connection, DATE, START)
            selected = process.query_totals(connection, DATE, START, ["U01", "U02"], ["x"])
        medians = [r["median_completed_cycle_days"] for r in output["process_unit_summary"]]
        self.assertEqual(medians, [1, 100])
        self.assertEqual(total["median_completed_cycle_days"], 1.5)
        self.assertEqual(selected, total)
        self.assertNotEqual(statistics.median(medians), total["median_completed_cycle_days"])
        self.assertNotEqual(statistics.mean([0, 1, 2, 100]), total["median_completed_cycle_days"])
        self.assertIsNone(total["median_open_age_days"])

    def test_zero_completed_empty_units_and_bound_selection_values(self):
        with closing(fixture([("open", "U01", "x", DATE, None, None)])) as connection:
            output, total = process.query_outputs(connection, DATE, START)
            empty = process.query_totals(connection, DATE, START, [])
            injected = process.query_totals(connection, DATE, START, ["U01') OR 1=1 --"])
        self.assertEqual(total["open_case_count"], 1)
        self.assertIsNone(total["discrepancy_rate"])
        self.assertIsNone(total["median_completed_cycle_days"])
        self.assertEqual(total["median_open_age_days"], 0)
        self.assertEqual(len(output["process_unit_summary"]), 2)
        self.assertEqual(output["process_unit_summary"][1]["known_case_count"], 0)
        self.assertEqual(empty["known_case_count"], 0)
        self.assertEqual(injected, empty)
        self.assertIsNone(empty["max_open_age_days"])


class ProcessExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ori-process-tests-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.source, self.bundle = self.work / "raw", self.work / "bundle"
        self.database, self.legacy = self.work / "readiness.sqlite3", self.work / "dashboard"
        self.output = self.legacy / "process"
        shutil.copytree(ROOT / "data/raw/clean", self.source)
        self.config = yaml.safe_load((ROOT / "config/project.yml").read_text())
        report, records = validate_directory(self.source, DATE)
        write_result(self.bundle, report, records)
        load_bundle(self.bundle, self.database, self.config)
        self.legacy.mkdir()
        for name in ("unit_summary.csv", "qualification_detail.csv", "expiration_detail.csv", "export_manifest.json"):
            shutil.copyfile(ROOT / "data/processed/dashboard" / name, self.legacy / name)

    def cli(self, database=None, output=None):
        return subprocess.run([sys.executable, str(ROOT / "src/export_process_metrics.py"),
            "--bundle-dir", str(self.bundle), "--database", str(database or self.database),
            "--output-dir", str(output or self.output)], cwd=ROOT, capture_output=True, text=True)

    def hashes(self, directory):
        return {str(p.relative_to(directory)): sha256(p.read_bytes())
                for p in directory.rglob("*") if p.is_file()}

    def good(self):
        run = self.cli()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        return json.loads((self.output / process.MANIFEST_NAME).read_text())

    def test_reference_sql_and_checker_match_independent_source_calculations(self):
        manifest = self.good()
        raw = read_csv(self.source / "admin_cases.csv")
        completed = [r for r in raw if r["closed_date"] and START <= r["closed_date"] <= DATE]
        cycles = [(dt.date.fromisoformat(r["closed_date"]) - dt.date.fromisoformat(r["opened_date"])).days for r in completed]
        corrections = sum(int(r["correction_required"]) for r in completed)
        expected = manifest["global_components"]
        self.assertEqual((expected["opened_case_count"], expected["completed_case_count"], corrections,
                          expected["open_case_count"]), (600, 442, 45, 158))
        self.assertEqual(expected["discrepancy_rate"], corrections / len(completed))
        self.assertEqual(expected["median_completed_cycle_days"], statistics.median(cycles))
        self.assertEqual((expected["median_open_age_days"], expected["max_open_age_days"]), (27, 88))
        checked = check_process_input.check_exports(self.output, self.config)
        self.assertEqual(checked["expected_selections"]["All"], expected)
        f = checked["expected_selections"]["Unit F"]
        self.assertEqual((f["correction_case_count"], f["completed_case_count"], f["median_completed_cycle_days"]), (27, 70, 7.5))
        self.assertIsNone(checked["expected_selections"]["Empty"]["discrepancy_rate"])

    def test_repeated_exports_preserve_database_sources_and_accepted_legacy_bundle(self):
        before_db, before_source = sha256(self.database.read_bytes()), self.hashes(self.source)
        before_legacy = {p.name: sha256(p.read_bytes()) for p in self.legacy.iterdir() if p.is_file()}
        first = self.good()
        first_hashes = {n: e["sha256"] for n, e in first["files"].items()}
        second = self.good()
        self.assertEqual(first_hashes, {n: e["sha256"] for n, e in second["files"].items()})
        self.assertEqual(sha256(self.database.read_bytes()), before_db)
        self.assertEqual(self.hashes(self.source), before_source)
        self.assertEqual({p.name: sha256(p.read_bytes()) for p in self.legacy.iterdir() if p.is_file()}, before_legacy)
        self.assertEqual([(n, e["rows"]) for n, e in sorted(first["files"].items())],
                         [("process_case_detail.csv", 600), ("process_unit_summary.csv", 6)])

    def test_blocked_validation_invalidates_prior_pass_without_replacing_csvs(self):
        manifest = self.good()
        p = self.bundle / "validation_report.json"
        report = json.loads(p.read_text()); report["load_allowed"] = False
        p.write_text(json.dumps(report))
        self.assertEqual(self.cli().returncode, 1)
        self.assertFalse(json.loads((self.output / process.MANIFEST_NAME).read_text())["exports_ready"])
        for n, e in manifest["files"].items():self.assertEqual(sha256((self.output / n).read_bytes()), e["sha256"])

    def test_changed_source_or_database_blocks_before_csv_replacement(self):
        self.good()
        db = self.work / "changed.sqlite3"; shutil.copyfile(self.database, db)
        with closing(sqlite3.connect(db)) as connection:
            connection.execute("UPDATE admin_cases SET correction_required=1-correction_required WHERE closed_date IS NOT NULL")
            connection.commit()
        before = sha256(db.read_bytes())
        self.assertEqual(self.cli(database=db).returncode, 1)
        self.assertEqual(sha256(db.read_bytes()), before)
        p = self.source / "units.csv";p.write_bytes(p.read_bytes().replace(b"Unit A", b"Changed fictional unit"))
        self.assertEqual(self.cli().returncode, 1)

    def test_missing_database_is_not_created_and_no_old_pass_survives(self):
        self.good()
        missing = self.work / "missing.sqlite3"
        self.assertEqual(self.cli(database=missing).returncode, 2)
        self.assertFalse(missing.exists())
        self.assertFalse(json.loads((self.output / process.MANIFEST_NAME).read_text())["exports_ready"])

    def test_protected_output_and_report_file_remain_untouched(self):
        for folder in (self.source, self.bundle, self.work / ".git", self.work / ".venv"):
            before = self.hashes(folder) if folder.exists() else {}
            self.assertEqual(self.cli(output=folder).returncode, 1)
            self.assertEqual(self.hashes(folder) if folder.exists() else {}, before)
        report = self.work / "saved.pbix";report.write_bytes(b"unrelated saved report sentinel")
        self.assertEqual(self.cli(output=report).returncode, 1)
        self.assertEqual(report.read_bytes(), b"unrelated saved report sentinel")

    def test_interrupted_replacement_invalidates_manifest(self):
        self.good(); original_replace = process.os.replace; calls = []
        def fail_second(source, target):
            calls.append(target)
            if len(calls) == 2:raise OSError("simulated interrupted process export")
            return original_replace(source, target)
        with patch("export_process_metrics.os.replace", side_effect=fail_second), redirect_stdout(io.StringIO()):
            code = process.main(["--bundle-dir", str(self.bundle), "--database", str(self.database), "--output-dir", str(self.output)])
        self.assertEqual(code, 2)
        self.assertFalse(json.loads((self.output / process.MANIFEST_NAME).read_text())["exports_ready"])

    def test_checker_is_read_only_and_blocks_hash_or_semantic_tampering(self):
        self.good();before = self.hashes(self.output)
        check_process_input.check_exports(self.output, self.config)
        self.assertEqual(self.hashes(self.output), before)
        path = self.output / "process_case_detail.csv";original = path.read_bytes()
        path.write_bytes(original + b"\n")
        with self.assertRaises(BlockedLoad):check_process_input.check_exports(self.output, self.config)
        rows = read_csv(io_path := self.output / "process_case_detail.csv")
        next(r for r in rows if r["status_at_as_of"] == "Open")["correction_required"] = "0"
        with io_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=process.DETAIL_COLUMNS, lineterminator="\n")
            writer.writeheader();writer.writerows(rows)
        mp = self.output / process.MANIFEST_NAME;manifest=json.loads(mp.read_text())
        manifest["files"][path.name]["sha256"]=sha256(path.read_bytes());mp.write_text(json.dumps(manifest))
        with self.assertRaises(BlockedLoad):check_process_input.check_exports(self.output, self.config)


if __name__ == "__main__":
    unittest.main()
