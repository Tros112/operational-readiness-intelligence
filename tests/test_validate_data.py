"""Day 3 checks for meaningful data-loss, key, date, and load-blocking risks."""

import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from generate_data import COLUMNS
from inject_defects import build_dirty
from validate_data import Record, validate_directory, validate_records, write_csv, write_result

D = "2026-10-07"


def fixture():
    return {
        "units": [["U1", "Unit One", "1"]],
        "personnel": [["P1", "U1", "1"], ["P2", "U1", "0"]],
        "qualification_types": [["Q1", "Qualification One"]],
        "personnel_qualifications": [["P1", "Q1", "2020-01-01", D],
                                     ["P2", "Q1", "2026-12-01", "2027-12-01"]],
        "unit_qualification_requirements": [["U1", "Q1", "1"]],
        "admin_cases": [["C1", "U1", "Review", D, D, "0"], ["C2", "U1", "Review", D, "", ""]],
    }


def as_records(raw):
    return {table: [Record(index + 2, row.copy(), dict(zip(COLUMNS[table], row)))
                    for index, row in enumerate(rows)] for table, rows in raw.items()}


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="ori-validation-tests-")
        cls.dirty = Path(cls.temp.name) / "dirty"
        cls.manifest = build_dirty(ROOT / "data/raw/clean", cls.dirty, D)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_clean_reference_passes_without_changing_values(self):
        report, tables = validate_directory(ROOT / "data/raw/clean", D)
        self.assertTrue(report["load_allowed"])
        self.assertEqual(report["totals"], {"input_rows": 1227, "accepted_rows": 1227,
                                          "rejected_rows": 0, "counts_reconciled": True})
        self.assertEqual(report["issues"], [])
        for table, rows in tables.items():
            with (ROOT / f"data/raw/clean/{table}.csv").open(newline="", encoding="utf-8") as stream:
                self.assertEqual([row.raw for row in rows], list(csv.reader(stream))[1:])

    def test_every_injected_defect_and_cascade_is_detected(self):
        report, _ = validate_directory(self.dirty, D)
        found = {(issue["table"], issue["record_number"], issue["code"]) for issue in report["issues"]}
        self.assertEqual(len(self.manifest["defects"]), 16)
        for defect in self.manifest["defects"]:
            for number in defect["record_numbers"]:
                with self.subTest(defect=defect["defect_id"], record=number):
                    self.assertIn((defect["table"], number, defect["expected_code"]), found)
        for child in self.manifest["expected_cascades"]:
            self.assertIn((child["table"], child["record_number"], child["expected_code"]), found)
        self.assertFalse(report["load_allowed"])
        self.assertEqual(report["exit_code"], 1)
        self.assertEqual(report["totals"], {"input_rows": 1229, "accepted_rows": 1210,
                                          "rejected_rows": 19, "counts_reconciled": True})
        self.assertEqual(len(report["batch_errors"][0]["pairs"]), 3)

    def test_accepted_dirty_subset_obeys_database_keys_and_foreign_keys(self):
        _, tables = validate_directory(self.dirty, D)
        with sqlite3.connect(":memory:") as connection:
            connection.executescript((ROOT / "sql/schema.sql").read_text())
            for table, rows in tables.items():
                values = [tuple(None if value == "" else value for value in row.raw)
                          for row in rows if not row.issues]
                placeholders = ",".join("?" for _ in COLUMNS[table])
                connection.executemany(f"INSERT INTO {table} VALUES ({placeholders})", values)
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
            self.assertEqual(connection.execute("SELECT SUM(n) FROM (" + " UNION ALL ".join(
                f"SELECT COUNT(*) AS n FROM {table}" for table in COLUMNS) + ")").fetchone()[0], 1210)

    def test_conflicting_parent_duplicates_reject_all_versions_and_descendants(self):
        raw = fixture()
        raw["units"].append(["U1", "Conflicting Unit Name", "2"])
        tables = as_records(raw)
        validate_records(tables)
        self.assertTrue(all(any(i["code"] == "DUPLICATE_KEY" for i in row.issues) for row in tables["units"]))
        for table in ("personnel", "personnel_qualifications", "unit_qualification_requirements", "admin_cases"):
            self.assertTrue(all(any(i["code"] == "REJECTED_PARENT" for i in row.issues) for row in tables[table]), table)
        self.assertFalse(tables["qualification_types"][0].issues)

    def test_expired_future_and_same_day_completed_rows_are_valid_records(self):
        tables = as_records(fixture())
        self.assertEqual(validate_records(tables), [])
        self.assertTrue(all(not row.issues for rows in tables.values() for row in rows))
        self.assertEqual(tables["admin_cases"][1].values["correction_required"], "")

    def test_real_calendar_and_exact_iso_format(self):
        for value, valid in [("2024-02-29", True), ("2026-02-29", False),
                             ("2026-02-30", False), ("20261007", False), ("2026-1-01", False)]:
            with self.subTest(date=value):
                raw = fixture()
                raw["personnel_qualifications"][0][2] = value
                tables = as_records(raw)
                validate_records(tables)
                codes = {i["code"] for i in tables["personnel_qualifications"][0].issues}
                self.assertEqual("INVALID_DATE" not in codes, valid)

    def test_positive_integer_and_storage_range(self):
        for value, code in [("0", "NONPOSITIVE_COUNT"), ("-1", "INVALID_INTEGER"),
                            ("2.5", "INVALID_INTEGER"), (str(2**63), "INTEGER_RANGE"),
                            ("9" * 5000, "INTEGER_RANGE")]:
            with self.subTest(value=value[:25]):
                raw = fixture()
                raw["units"][0][2] = value
                tables = as_records(raw)
                validate_records(tables)
                self.assertIn(code, {i["code"] for i in tables["units"][0].issues})

    def test_critical_identifier_whitespace_is_rejected_not_trimmed(self):
        raw = fixture()
        raw["personnel"][0][0] = " P1 "
        tables = as_records(raw)
        validate_records(tables)
        self.assertIn("PADDED_IDENTIFIER", {i["code"] for i in tables["personnel"][0].issues})
        self.assertEqual(tables["personnel"][0].raw[0], " P1 ")

    def test_missing_requirement_pair_blocks_load_even_without_bad_rows(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            raw = fixture()
            raw["unit_qualification_requirements"] = []
            self.write_fixture(folder, raw)
            report, _ = validate_directory(folder, D)
            self.assertEqual(report["totals"]["rejected_rows"], 0)
            self.assertFalse(report["load_allowed"])
            self.assertEqual(report["batch_errors"][0]["code"], "MISSING_REQUIREMENT_PAIRS")

    def test_multiple_issues_on_one_record_count_as_one_rejection(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            raw = fixture()
            raw["personnel"][0][1] = "UX99"
            raw["personnel"][0][2] = "2"
            self.write_fixture(folder, raw)
            report, _ = validate_directory(folder, D)
            self.assertEqual(report["totals"], {"input_rows": 9, "accepted_rows": 7,
                                              "rejected_rows": 2, "counts_reconciled": True})
            self.assertEqual(report["row_issue_count"], 3)
            self.assertEqual(report["tables"]["personnel"]["rejected_rows"], 1)

    @staticmethod
    def write_fixture(folder, raw=None):
        for table, rows in (fixture() if raw is None else raw).items():
            write_csv(folder / f"{table}.csv", COLUMNS[table], rows)

    def test_missing_unparseable_or_malformed_sources_cannot_pass(self):
        for failure in ("missing", "quoting", "utf8", "header", "width", "extra"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                self.write_fixture(folder)
                path = folder / "units.csv"
                if failure == "missing":
                    path.unlink()
                elif failure == "quoting":
                    path.write_text('unit_id,unit_name,required_personnel_count\n"unterminated', encoding="utf-8")
                elif failure == "utf8":
                    path.write_bytes(b"\xff")
                elif failure == "header":
                    path.write_text("unit_id,unit_id,required_personnel_count\nU1,Unit One,1\n", encoding="utf-8")
                elif failure == "width":
                    path.write_text("unit_id,unit_name,required_personnel_count\nU1,Unit One,1,extra\n", encoding="utf-8")
                else:
                    (folder / "unexpected.csv").write_text("x\n1\n", encoding="utf-8")
                report, _ = validate_directory(folder, D)
                self.assertFalse(report["load_allowed"])
                self.assertEqual(report["exit_code"], 2)
                if failure in ("missing", "quoting", "utf8"):
                    self.assertIsNone(report["totals"]["input_rows"])
                    self.assertFalse(report["totals"]["counts_reconciled"])

    def test_export_counts_hashes_and_raw_rejected_values(self):
        report, tables = validate_directory(self.dirty, D)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            write_result(output, report, tables)
            saved = json.loads((output / "validation_report.json").read_text())
            for name, details in saved["outputs"].items():
                path = output / name
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), details["sha256"])
                with path.open(newline="", encoding="utf-8") as stream:
                    self.assertEqual(len(list(csv.DictReader(stream))), details["rows"])
            with (output / "rejected_rows.csv").open(newline="", encoding="utf-8") as stream:
                rejected = list(csv.DictReader(stream))
            self.assertEqual(len(rejected), 19)
            self.assertEqual(len({(r["table"], r["record_number"]) for r in rejected}), 19)
            missing = next(d for d in self.manifest["defects"] if d["defect_id"] == "D02")
            row = next(r for r in rejected if r["table"] == missing["table"] and int(r["record_number"]) == missing["record_numbers"][0])
            self.assertEqual(json.loads(row["raw_record_json"])[0], "")

    def test_dirty_creation_is_repeatable_and_preserves_clean_hashes(self):
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "data/raw/clean").iterdir() if p.is_file()}
        second = Path(self.temp.name) / "dirty_repeat"
        build_dirty(ROOT / "data/raw/clean", second, D)
        for path in self.dirty.iterdir():
            self.assertEqual(path.read_bytes(), (second / path.name).read_bytes(), path.name)
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "data/raw/clean").iterdir() if p.is_file()}
        self.assertEqual(before, after)
        with self.assertRaisesRegex(ValueError, "overlap"):
            build_dirty(ROOT / "data/raw/clean", ROOT / "data/raw/clean", D)

    def test_cli_exit_codes_and_failed_rerun_block_stale_success(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "output"
            command = [sys.executable, str(ROOT / "src/validate_data.py"), "--output-dir", str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = subprocess.run(command + ["--config", str(Path(temp) / "missing.yml")], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(json.loads((output / "validation_report.json").read_text())["load_allowed"])
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = subprocess.run(command + ["--input-dir", str(self.dirty)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertFalse(json.loads((output / "validation_report.json").read_text())["load_allowed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
