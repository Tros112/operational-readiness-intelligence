"""Day 4 persistence, blocked-input, rollback, and local-asset protection checks."""

from contextlib import closing
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import load_data
from generate_data import COLUMNS, KEYS
from inject_defects import build_dirty
from validate_data import validate_directory, write_result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(path):
    with closing(sqlite3.connect(path)) as con:
        return {table: con.execute(f"SELECT * FROM {table} ORDER BY {','.join(KEYS[table])}").fetchall()
                for table in COLUMNS}


class LoaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ori-loader-tests-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.source = self.work / "raw"
        shutil.copytree(ROOT / "data/raw/clean", self.source)
        self.config = yaml.safe_load((ROOT / "config/project.yml").read_text())
        self.bundle = self.work / "bundle"
        self.database = self.work / "readiness.sqlite3"
        self.validate(self.source, self.bundle)

    def validate(self, source, bundle):
        report, records = validate_directory(source, self.config["as_of_date"])
        write_result(bundle, report, records)
        return report

    def load(self, bundle=None, database=None):
        return load_data.load_bundle(bundle or self.bundle, database or self.database, self.config)

    def change_cell(self, file, index, column, value):
        with file.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        rows[index][column] = value
        with file.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def test_load_persists_exact_counts_null_outcomes_and_inactive_certificates(self):
        result = self.load()
        self.assertEqual(result["database_counts"], {
            "units": 6, "personnel": 300, "qualification_types": 8,
            "personnel_qualifications": 265, "unit_qualification_requirements": 48, "admin_cases": 600})
        self.assertEqual(result["total_rows"], 1227)
        self.assertTrue(result["counts_reconciled"])
        self.assertEqual(result["open_cases_with_null_outcomes"], 158)
        with closing(sqlite3.connect(self.database)) as con:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(con.execute("SELECT COUNT(*) FROM admin_cases WHERE closed_date IS NOT NULL "
                                         "AND correction_required IS NULL").fetchone()[0], 0)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM admin_cases WHERE correction_required=0").fetchone()[0], 397)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM personnel_qualifications WHERE expiration_date<=?",
                                         (self.config["as_of_date"],)).fetchone()[0], 49)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM personnel_qualifications WHERE valid_from>?",
                                         (self.config["as_of_date"],)).fetchone()[0], 23)
        self.assertEqual(sum(len(rows) for rows in snapshot(self.database).values()), 1227)

    def test_second_load_has_identical_records_and_logical_digest(self):
        first = self.load()
        before = snapshot(self.database)
        second = self.load()
        self.assertEqual(snapshot(self.database), before)
        self.assertEqual(second["database_counts"], first["database_counts"])
        self.assertEqual(second["logical_data_sha256"], first["logical_data_sha256"])

    def test_dirty_bundle_is_blocked_before_new_or_existing_database_is_touched(self):
        dirty = self.work / "dirty"
        build_dirty(self.source, dirty, self.config["as_of_date"])
        rejected = self.work / "rejected"
        self.assertFalse(self.validate(dirty, rejected)["load_allowed"])
        new_database = self.work / "never_created.sqlite3"
        with self.assertRaises(load_data.BlockedLoad):
            self.load(rejected, new_database)
        self.assertFalse(new_database.exists())
        self.load()
        before = digest(self.database)
        with self.assertRaises(load_data.BlockedLoad):
            self.load(rejected)
        self.assertEqual(digest(self.database), before)

    def test_source_or_accepted_mutation_blocks_load_and_preserves_good_database(self):
        self.load()
        before = digest(self.database)
        for file in (self.source / "units.csv", self.bundle / "accepted/units.csv"):
            with self.subTest(file=file.name, parent=file.parent.name):
                original = file.read_bytes()
                self.change_cell(file, 0, "unit_name", "A changed fictional name")
                with self.assertRaises(load_data.BlockedLoad):
                    self.load()
                self.assertEqual(digest(self.database), before)
                file.write_bytes(original)

    def test_rehashed_modified_export_still_cannot_disagree_with_the_source(self):
        self.load()
        before = snapshot(self.database)
        export = self.bundle / "accepted/units.csv"
        self.change_cell(export, 0, "unit_name", "A changed fictional name")
        report_file = self.bundle / "validation_report.json"
        report = json.loads(report_file.read_text())
        report["outputs"]["accepted/units.csv"]["sha256"] = digest(export)
        report_file.write_text(json.dumps(report))
        with self.assertRaisesRegex(load_data.BlockedLoad, "Accepted values differ"):
            self.load()
        self.assertEqual(snapshot(self.database), before)

    def test_unfinished_wrong_date_or_bad_count_metadata_is_not_authorization(self):
        self.load()
        before = digest(self.database)
        file = self.bundle / "validation_report.json"
        original = file.read_text()
        for change in ({"status": "in_progress"}, {"load_allowed": False}, {"as_of_date": "2026-10-08"},
                       {"totals": {"input_rows": 0}}, {"validation_version": 99},
                       {"tables": []}, {"outputs": []}):
            with self.subTest(change=change):
                report = json.loads(original)
                report.update(change)
                file.write_text(json.dumps(report))
                with self.assertRaises(load_data.BlockedLoad):
                    self.load()
                self.assertEqual(digest(self.database), before)
        file.write_text(original)

    def test_real_constraint_failure_after_deletion_rolls_back_the_whole_reload(self):
        self.load()
        before = snapshot(self.database)
        self.change_cell(self.source / "personnel.csv", 0, "is_available", "0")
        self.validate(self.source, self.bundle)
        original_insert = load_data.insert_records

        def fail_mid_load(con, table, values):
            original_insert(con, table, values)
            if table == "personnel":
                # Actual SQLite PK failure after DELETE and several tables have been inserted.
                con.execute("INSERT INTO personnel SELECT * FROM personnel LIMIT 1")

        with patch.object(load_data, "insert_records", side_effect=fail_mid_load):
            with self.assertRaises(sqlite3.IntegrityError):
                self.load()
        self.assertEqual(snapshot(self.database), before)
        with closing(sqlite3.connect(self.database)) as con:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")

    def test_database_constraints_reject_duplicate_orphan_and_invalid_flag(self):
        self.load()
        with closing(sqlite3.connect(self.database)) as con:
            con.execute("PRAGMA foreign_keys=ON")
            for statement, params in (
                ("INSERT INTO personnel SELECT * FROM personnel LIMIT 1", ()),
                ("INSERT INTO personnel VALUES (?, ?, ?)", ("NEW", "NO_SUCH_UNIT", 1)),
                ("INSERT INTO personnel VALUES (?, ?, ?)", ("NEW", "U01", 2)),
            ):
                with self.subTest(statement=statement, params=params):
                    with self.assertRaises(sqlite3.IntegrityError):
                        con.execute(statement, params)
                    con.rollback()
            self.assertEqual(con.execute("SELECT COUNT(*) FROM personnel").fetchone()[0], 300)

    def test_unrelated_database_and_protected_local_assets_are_preserved(self):
        with closing(sqlite3.connect(self.database)) as con:
            con.execute("CREATE TABLE personal_notes (note TEXT)")
            con.execute("INSERT INTO personal_notes VALUES ('keep this')")
            con.commit()
        before = digest(self.database)
        with self.assertRaisesRegex(load_data.BlockedLoad, "compatible project schema"):
            self.load()
        self.assertEqual(digest(self.database), before)
        for relative in (".git/keep.sqlite3", ".venv/keep.sqlite3", "powerbi/keep.pbix"):
            path = self.work / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"local asset must stay unchanged")
            with self.subTest(path=relative):
                with self.assertRaises(load_data.BlockedLoad):
                    self.load(database=path)
                self.assertEqual(path.read_bytes(), b"local asset must stay unchanged")

    def test_cli_failed_rerun_invalidates_old_success_and_preserves_database(self):
        report_path = self.work / "load_report.json"
        cmd = [sys.executable, str(ROOT / "src/load_data.py"), "--database", str(self.database),
               "--bundle-dir", str(self.bundle), "--report-path", str(report_path)]
        clean = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
        self.assertTrue(json.loads(report_path.read_text())["database_updated"])
        before = digest(self.database)
        dirty = self.work / "dirty"
        build_dirty(self.source, dirty, self.config["as_of_date"])
        rejected = self.work / "rejected"
        self.validate(dirty, rejected)
        dirty_cmd = cmd.copy()
        dirty_cmd[dirty_cmd.index("--bundle-dir") + 1] = str(rejected)
        failed = subprocess.run(dirty_cmd, capture_output=True, text=True)
        self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
        self.assertEqual(json.loads(report_path.read_text())["status"], "blocked")
        self.assertFalse(json.loads(report_path.read_text())["database_updated"])
        self.assertEqual(digest(self.database), before)
        # A report path must not overwrite a source-side JSON file either.
        source_json = self.source / "generation_manifest.json"
        source_before = source_json.read_bytes()
        guarded_cmd = cmd.copy()
        guarded_cmd[guarded_cmd.index("--report-path") + 1] = str(source_json)
        guarded = subprocess.run(guarded_cmd, capture_output=True, text=True)
        self.assertEqual(guarded.returncode, 1)
        self.assertEqual(source_json.read_bytes(), source_before)
        self.assertEqual(digest(self.database), before)
        # A missing config must not leave the earlier success report in place either.
        bad_config = subprocess.run(cmd + ["--config", str(self.work / "missing.yml")],
                                    capture_output=True, text=True)
        self.assertEqual(bad_config.returncode, 2)
        self.assertFalse(json.loads(report_path.read_text())["database_updated"])
        self.assertEqual(digest(self.database), before)


if __name__ == "__main__":
    unittest.main()
