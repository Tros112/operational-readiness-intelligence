"""Day 6 read-only refresh prerequisite; these are not DAX/M runtime tests."""
import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from check_powerbi_input import check_exports, main, SUMMARY_COMPONENTS
from export_metrics import OUTPUT_KEYS
from load_data import BlockedLoad


class PowerBIInputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.date = "2026-10-07"
        self.rows = {}
        self.manifest = {
            "status": "passed", "exports_ready": True, "exit_code": 0,
            "as_of_date": self.date, "data_classification": "synthetic_only",
            "database_matches_passed_source": True, "cross_query_reconciliation": "passed", "files": {}
        }
        for name, keys in OUTPUT_KEYS.items():
            fields = list(dict.fromkeys(["data_classification"] + keys))
            if name == "unit_summary":
                fields += list(SUMMARY_COMPONENTS)
                rows = []
                for unit, available, required, capped, slots, gaps, flag in (
                        ("U01", 41, 40, 16, 16, 0, 0), ("U03", 40, 50, 15, 16, 1, 1)):
                    row = {"data_classification": "synthetic_only", "as_of_date": self.date, "unit_id": unit,
                           "available_personnel_count": available, "required_personnel_count": required,
                           "staffing_gap": max(required - available, 0), "capped_holder_slots": capped,
                           "required_holder_slots": slots, "qualification_gap": slots - capped,
                           "qualification_pairs_with_gap": gaps, "unit_attention_flag": flag}
                    rows.append(row)
            else:
                rows = [{field: ("synthetic_only" if field == "data_classification" else
                                  self.date if field == "as_of_date" else "U01" if field == "unit_id"
                                  else "P0001" if field == "person_id" else "Q01") for field in fields}]
            self.rows[name] = rows
            self.manifest["files"][f"{name}.csv"] = {"columns": fields, "grain": keys}
            self.rewrite(name)
        self.save_manifest()

    def save_manifest(self):
        (self.directory / "export_manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def rewrite(self, name):
        entry = self.manifest["files"][f"{name}.csv"]
        path = self.directory / f"{name}.csv"
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=entry["columns"], lineterminator="\n")
            writer.writeheader()
            writer.writerows(self.rows[name])
        entry.update(rows=len(self.rows[name]), sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        self.save_manifest()

    def test_reference_selections_use_weighted_components_and_check_writes_nothing(self):
        before = {path.name: path.read_bytes() for path in self.directory.iterdir()}
        result = check_exports(self.directory, self.date)
        selected = result["expected_selections"]["Units A and C"]
        self.assertEqual((selected["available_personnel_count"], selected["required_personnel_count"]), (81, 90))
        self.assertEqual(selected["staffing_coverage_ratio"], 0.9)
        self.assertEqual((selected["staffing_gap"], selected["flagged_units"]), (10, 1))
        self.assertEqual(selected["qualification_coverage_ratio"], 31 / 32)
        self.assertEqual(result["expected_selections"]["Unit A"]["flagged_units"], 0)
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.directory.iterdir()})

    def test_changed_csv_blocks_even_when_manifest_still_says_passed(self):
        path = self.directory / "unit_summary.csv"
        path.write_bytes(path.read_bytes().replace(b",41,40,", b",99,40,"))
        with self.assertRaisesRegex(BlockedLoad, "hash mismatch"):
            check_exports(self.directory, self.date)

    def test_unready_wrong_date_and_wrong_reconciliation_manifests_block(self):
        for field, value in (("status", "blocked"), ("exports_ready", False), ("exit_code", 1),
                             ("as_of_date", "2026-10-08"), ("data_classification", "real"),
                             ("database_matches_passed_source", False), ("cross_query_reconciliation", "failed")):
            with self.subTest(field=field):
                old = self.manifest[field]
                self.manifest[field] = value
                self.save_manifest()
                with self.assertRaises(BlockedLoad):
                    check_exports(self.directory, self.date)
                self.manifest[field] = old
        self.save_manifest()

    def test_missing_file_or_manifest_entry_blocks(self):
        path = self.directory / "expiration_detail.csv"
        raw = path.read_bytes()
        path.unlink()
        with self.assertRaisesRegex(BlockedLoad, "Missing CSV"):
            check_exports(self.directory, self.date)
        path.write_bytes(raw)
        del self.manifest["files"]["expiration_detail.csv"]
        self.save_manifest()
        with self.assertRaisesRegex(BlockedLoad, "exactly three"):
            check_exports(self.directory, self.date)

    def test_duplicate_grain_and_wrong_record_date_block_despite_updated_hashes(self):
        for name in OUTPUT_KEYS:
            with self.subTest(name=name):
                original = [dict(row) for row in self.rows[name]]
                self.rows[name].append(dict(original[0]))
                self.rewrite(name)
                with self.assertRaisesRegex(BlockedLoad, "duplicate grain"):
                    check_exports(self.directory, self.date)
                self.rows[name] = [dict(row) for row in original]
                self.rows[name][0]["as_of_date"] = "2026-10-08"
                self.rewrite(name)
                with self.assertRaisesRegex(BlockedLoad, "Wrong date"):
                    check_exports(self.directory, self.date)
                self.rows[name] = original
                self.rewrite(name)

    def test_invalid_count_or_inconsistent_gap_blocks(self):
        row = self.rows["unit_summary"][0]
        for field, value in (("available_personnel_count", "41.5"), ("staffing_gap", -1),
                             ("staffing_gap", 3), ("unit_attention_flag", 2)):
            with self.subTest(field=field, value=value):
                old = row[field]
                row[field] = value
                self.rewrite("unit_summary")
                with self.assertRaises(BlockedLoad):
                    check_exports(self.directory, self.date)
                row[field] = old
        self.rewrite("unit_summary")

    def test_missing_manifest_cli_reports_blocked_without_creating_files(self):
        (self.directory / "export_manifest.json").unlink()
        before = {path.name: path.read_bytes() for path in self.directory.iterdir()}
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            exit_code = main(["--export-dir", str(self.directory)])
        result = json.loads(capture.getvalue())
        self.assertEqual((exit_code, result["status"], result["file_writes"]), (1, "blocked", 0))
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.directory.iterdir()})


if __name__ == "__main__":
    unittest.main()
