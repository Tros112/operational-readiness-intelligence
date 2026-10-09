"""Day 5 independent metric, join, boundary, and export-preservation checks."""
from contextlib import closing, redirect_stdout
import csv
import datetime as dt
import hashlib
import io
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
import export_metrics
from generate_data import COLUMNS
from inject_defects import build_dirty
from load_data import load_bundle
from validate_data import validate_directory, write_result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def fixture(units, people, requirements, certificates):
    """Unconstrained, memory-only SQL fixture; never an approved loader input.

    Permits deliberate duplicate and zero-demand rows to test defensive SQL.
    The real validator/loader still reject these records.
    """
    connection = sqlite3.connect(":memory:")
    numeric = {"required_personnel_count", "is_available", "required_holder_count",
               "correction_required"}
    for table, columns in COLUMNS.items():
        fields = ",".join(f"{name} {'INTEGER' if name in numeric else 'TEXT'}" for name in columns)
        connection.execute(f"CREATE TABLE {table} ({fields})")
    qualifications = sorted({row[1] for row in requirements + certificates})
    tables = {"units": units, "personnel": people,
              "qualification_types": [(key, key) for key in qualifications],
              "unit_qualification_requirements": requirements,
              "personnel_qualifications": certificates}
    for table, rows in tables.items():
        connection.executemany(f"INSERT INTO {table} VALUES ({','.join('?' for _ in COLUMNS[table])})", rows)
    return connection


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ori-export-tests-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.source, self.bundle = self.work / "raw", self.work / "bundle"
        self.database, self.output = self.work / "readiness.sqlite3", self.work / "dashboard"
        shutil.copytree(ROOT / "data/raw/clean", self.source)
        self.config = yaml.safe_load((ROOT / "config/project.yml").read_text())
        self.date = self.config["as_of_date"]
        self.validate(self.source, self.bundle)
        load_bundle(self.bundle, self.database, self.config)

    def validate(self, source, bundle):
        report, records = validate_directory(source, self.date)
        write_result(bundle, report, records)
        return report

    def cli(self, bundle=None, database=None, output=None):
        return subprocess.run([sys.executable, str(ROOT / "src/export_metrics.py"),
            "--bundle-dir", str(bundle or self.bundle), "--database", str(database or self.database),
            "--output-dir", str(output or self.output)], capture_output=True, text=True, cwd=ROOT)

    def csv_hashes(self):
        return {name: digest(self.output / f"{name}.csv") for name in export_metrics.OUTPUT_KEYS}

    def queries(self, connection):
        return export_metrics.query_metrics(connection, self.date)[0]

    def test_full_reference_matches_independent_source_calculations_and_hand_checks(self):
        with closing(sqlite3.connect(self.database)) as connection:
            output = self.queries(connection)
        people = {r["person_id"]: r for r in read_csv(self.source / "personnel.csv")}
        units = read_csv(self.source / "units.csv")
        requirements = read_csv(self.source / "unit_qualification_requirements.csv")
        date = dt.date.fromisoformat(self.date)
        valid = [r for r in read_csv(self.source / "personnel_qualifications.csv")
                 if dt.date.fromisoformat(r["valid_from"]) <= date < dt.date.fromisoformat(r["expiration_date"])]
        holders = {}
        for certificate in valid:
            person = people[certificate["person_id"]]
            if person["is_available"] == "1":
                holders.setdefault((person["unit_id"], certificate["qualification_id"]), set()).add(person["person_id"])
        pair_results = {}
        for requirement in requirements:
            key = (requirement["unit_id"], requirement["qualification_id"])
            count, required = len(holders.get(key, set())), int(requirement["required_holder_count"])
            pair_results[key] = {"required_holder_count": required, "valid_available_holder_count": count,
                "capped_holder_count": min(count, required), "current_gap": max(required - count, 0),
                "qualification_coverage_ratio": min(count, required) / required,
                "is_fragile": int(count == required), "is_single_holder_dependency": int(count == required == 1)}
        self.assertEqual(len(output["qualification_detail"]), len(requirements))
        for row in output["qualification_detail"]:
            expected = pair_results[(row["unit_id"], row["qualification_id"])]
            self.assertEqual({name: row[name] for name in expected}, expected)
        self.assertEqual(len(output["expiration_detail"]), len(valid))
        valid_by_key = {(r["person_id"], r["qualification_id"]): r for r in valid}
        for row in output["expiration_detail"]:
            certificate = valid_by_key[(row["person_id"], row["qualification_id"])]
            self.assertEqual(row["unit_id"], people[row["person_id"]]["unit_id"])
            self.assertEqual(row["is_available"], int(people[row["person_id"]]["is_available"]))
            self.assertEqual(row["days_until_expiration"], (dt.date.fromisoformat(certificate["expiration_date"]) - date).days)
            for horizon in (30, 60, 90):
                self.assertEqual(row[f"expires_within_{horizon}_days"], int(row["days_until_expiration"] <= horizon))
        summaries = {row["unit_id"]: row for row in output["unit_summary"]}
        self.assertEqual(len(summaries), len(units))
        for unit in units:
            key, required = unit["unit_id"], int(unit["required_personnel_count"])
            members = [p for p in people.values() if p["unit_id"] == key]
            available = sum(p["is_available"] == "1" for p in members)
            pairs = [v for (unit_id, _), v in pair_results.items() if unit_id == key]
            capped, slots = sum(p["capped_holder_count"] for p in pairs), sum(p["required_holder_count"] for p in pairs)
            gap = sum(p["current_gap"] for p in pairs)
            expected = {"total_personnel_count": len(members), "available_personnel_count": available,
                "required_personnel_count": required, "staffing_gap": max(required - available, 0),
                "staffing_coverage_ratio": available / required, "required_holder_slots": slots,
                "capped_holder_slots": capped, "qualification_coverage_ratio": capped / slots,
                "qualification_gap": gap, "qualification_pair_count": len(pairs),
                "qualification_pairs_with_gap": sum(p["current_gap"] > 0 for p in pairs),
                "fragile_qualification_pairs": sum(p["is_fragile"] for p in pairs),
                "single_holder_dependency_pairs": sum(p["is_single_holder_dependency"] for p in pairs),
                "unit_attention_flag": int(available < required or gap > 0)}
            for horizon in (30, 60, 90):
                expiring = [c for c in valid if people[c["person_id"]]["unit_id"] == key
                            and dt.date.fromisoformat(c["expiration_date"]) <= date + dt.timedelta(days=horizon)]
                expected[f"certificates_expiring_{horizon}_days"] = len(expiring)
                expected[f"people_affected_{horizon}_days"] = len({c["person_id"] for c in expiring})
            self.assertEqual({name: summaries[key][name] for name in expected}, expected)
        self.assertEqual([summaries["U03"][name] for name in (
            "available_personnel_count", "required_personnel_count", "staffing_gap",
            "capped_holder_slots", "required_holder_slots", "qualification_gap")], [40, 50, 10, 15, 16, 1])
        self.assertEqual(pair_results[("U02", "Q03")]["is_single_holder_dependency"], 1)
        cluster = [r for r in output["expiration_detail"] if r["unit_id"] == "U04" and r["qualification_id"] == "Q04"]
        self.assertEqual(sorted(r["days_until_expiration"] for r in cluster), [7, 10, 14, 20, 25, 30])
        self.assertEqual(sum(r["is_available"] == 0 for r in output["expiration_detail"]), 21)

    def test_duplicate_certificates_do_not_inflate_staffing_holders_or_inventory(self):
        certificate = ("P1", "Q1", "2026-09-01", "2026-10-20")
        with closing(fixture([("U1", "Unit", 2)], [("P1", "U1", 1), ("P2", "U1", 1)],
                [("U1", "Q1", 1), ("U1", "Q2", 2)],
                [certificate, certificate, ("P2", "Q1", "2026-09-01", "2026-10-20"),
                 ("P1", "Q2", "2026-09-01", "2026-10-20")])) as connection:
            output = self.queries(connection)
        unit, pairs = output["unit_summary"][0], output["qualification_detail"]
        self.assertEqual((unit["total_personnel_count"], unit["available_personnel_count"]), (2, 2))
        self.assertEqual([r["valid_available_holder_count"] for r in pairs], [2, 1])
        self.assertEqual((unit["capped_holder_slots"], unit["required_holder_slots"], unit["qualification_gap"]), (2, 3, 1))
        self.assertEqual(len(output["expiration_detail"]), 3)
        self.assertEqual((unit["certificates_expiring_30_days"], unit["people_affected_30_days"]), (3, 2))

    def test_zero_holder_pairs_survive_and_unavailable_inventory_is_separate(self):
        with closing(fixture([("U1", "Unit", 2)], [("P1", "U1", 1), ("P2", "U1", 0)],
                [("U1", f"Q{i}", 1) for i in range(1, 5)],
                [("P1", "Q1", "2026-09-01", self.date),
                 ("P1", "Q2", "2026-10-08", "2026-11-01"),
                 ("P2", "Q3", self.date, "2026-11-01")])) as connection:
            output = self.queries(connection)
        self.assertEqual(len(output["qualification_detail"]), 4)
        self.assertEqual([r["valid_available_holder_count"] for r in output["qualification_detail"]], [0] * 4)
        self.assertEqual([r["current_gap"] for r in output["qualification_detail"]], [1] * 4)
        self.assertEqual([(r["person_id"], r["qualification_id"], r["is_available"])
                          for r in output["expiration_detail"]], [("P2", "Q3", 0)])
        self.assertEqual(output["unit_summary"][0]["unit_attention_flag"], 1)

    def test_expiration_windows_are_inclusive_cumulative_and_count_distinct_people(self):
        date = dt.date.fromisoformat(self.date)
        offsets = [0, 30, 31, 60, 61, 90, 91]
        certificates = [("P1", f"Q{i}", "2026-09-01", (date + dt.timedelta(days=offset)).isoformat())
                        for i, offset in enumerate(offsets)]
        with closing(fixture([("U1", "Unit", 1)], [("P1", "U1", 1)],
                [("U1", f"Q{i}", 1) for i in range(7)], certificates)) as connection:
            output = self.queries(connection)
        self.assertEqual([r["days_until_expiration"] for r in output["expiration_detail"]], offsets[1:])
        for horizon, count in ((30, 1), (60, 3), (90, 5)):
            unit = output["unit_summary"][0]
            self.assertEqual(unit[f"certificates_expiring_{horizon}_days"], count)
            self.assertEqual(unit[f"people_affected_{horizon}_days"], 1)
        boundary = output["expiration_detail"][0]
        self.assertEqual([boundary[f"expires_within_{n}_days"] for n in (30, 60, 90)], [1, 1, 1])

    def test_undefined_denominators_remain_null_while_empty_counts_are_zero(self):
        with closing(fixture([("U1", "Zero demand", 0), ("U2", "No people", 2)], [],
                [("U1", "Q1", 0)], [])) as connection:
            output = self.queries(connection)
        first, second = output["unit_summary"]
        self.assertIsNone(first["staffing_coverage_ratio"])
        self.assertIsNone(first["qualification_coverage_ratio"])
        self.assertIsNone(output["qualification_detail"][0]["qualification_coverage_ratio"])
        self.assertEqual(first["available_personnel_count"], 0)
        self.assertEqual(first["certificates_expiring_30_days"], 0)
        self.assertEqual((second["staffing_coverage_ratio"], second["staffing_gap"]), (0.0, 2))
        self.assertIsNone(second["qualification_coverage_ratio"])

    def test_repeat_cli_exports_identical_csvs_and_preserves_database_and_sources(self):
        before = digest(self.database)
        source_hashes = {p.name: digest(p) for p in self.source.iterdir() if p.is_file()}
        first = self.cli()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        hashes = self.csv_hashes()
        second = self.cli()
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(self.csv_hashes(), hashes)
        self.assertEqual(digest(self.database), before)
        self.assertEqual({p.name: digest(p) for p in self.source.iterdir() if p.is_file()}, source_hashes)
        manifest = json.loads((self.output / "export_manifest.json").read_text())
        self.assertEqual((manifest["status"], manifest["exports_ready"], manifest["as_of_date"]), ("passed", True, self.date))
        for name, count in (("unit_summary", 6), ("qualification_detail", 48), ("expiration_detail", 193)):
            rows = read_csv(self.output / f"{name}.csv")
            self.assertEqual(len(rows), count)
            self.assertEqual(len({tuple(r[k] for k in export_metrics.OUTPUT_KEYS[name]) for r in rows}), count)
            self.assertEqual(manifest["files"][f"{name}.csv"]["sha256"], hashes[name])
            self.assertTrue(all(r["data_classification"] == "synthetic_only" and r["as_of_date"] == self.date for r in rows))

    def test_dirty_stale_and_changed_bundles_block_before_csv_replacement(self):
        self.assertEqual(self.cli().returncode, 0)
        hashes, db_before = self.csv_hashes(), digest(self.database)
        dirty, rejected = self.work / "dirty", self.work / "rejected"
        build_dirty(self.source, dirty, self.date)
        self.assertFalse(self.validate(dirty, rejected)["load_allowed"])
        attempts = [(rejected, None), (self.bundle, self.bundle / "validation_report.json"),
                    (self.bundle, self.source / "units.csv"), (self.bundle, self.bundle / "accepted/units.csv")]
        for bundle, changed in attempts:
            with self.subTest(changed=str(changed)):
                original = changed.read_bytes() if changed else None
                if changed and changed.suffix == ".json":
                    report = json.loads(original)
                    report["as_of_date"] = "2026-10-08"
                    changed.write_text(json.dumps(report))
                elif changed:
                    changed.write_bytes(original.replace(b"Unit A", b"Changed fictional unit"))
                try:
                    run = self.cli(bundle=bundle)
                    self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
                    manifest = json.loads((self.output / "export_manifest.json").read_text())
                    self.assertEqual((manifest["status"], manifest["exports_ready"]), ("blocked", False))
                    self.assertEqual(self.csv_hashes(), hashes)
                    self.assertEqual(digest(self.database), db_before)
                finally:
                    if changed:
                        changed.write_bytes(original)

    def test_mismatched_or_missing_database_cannot_supply_an_export(self):
        self.assertEqual(self.cli().returncode, 0)
        hashes = self.csv_hashes()
        altered = self.work / "altered.sqlite3"
        shutil.copyfile(self.database, altered)
        with closing(sqlite3.connect(altered)) as connection:
            connection.execute("UPDATE personnel SET is_available=1-is_available WHERE person_id='P0001'")
            connection.commit()
        changed_before = digest(altered)
        run = self.cli(database=altered)
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn("Database differs", run.stdout)
        self.assertEqual(digest(altered), changed_before)
        absent = self.work / "absent.sqlite3"
        run = self.cli(database=absent)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertFalse(absent.exists())
        self.assertEqual(self.csv_hashes(), hashes)
        self.assertFalse(json.loads((self.output / "export_manifest.json").read_text())["exports_ready"])

    def test_protected_folders_and_existing_report_file_are_untouched(self):
        for directory in (self.work / ".git", self.work / ".venv", self.source, self.bundle, ROOT / "data/raw"):
            with self.subTest(directory=directory):
                before = {p: digest(p) for p in directory.rglob("*") if p.is_file()} if directory.exists() else {}
                run = self.cli(output=directory)
                self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
                after = {p: digest(p) for p in directory.rglob("*") if p.is_file()} if directory.exists() else {}
                self.assertEqual(after, before)
                self.assertFalse((directory / "export_manifest.json").exists())
        report = self.work / "my_report.pbix"
        report.write_bytes(b"unrelated report sentinel, not a PBIX build")
        self.assertEqual(self.cli(output=report).returncode, 1)
        self.assertEqual(report.read_bytes(), b"unrelated report sentinel, not a PBIX build")

    def test_failed_csv_replacement_invalidates_prior_passed_manifest(self):
        self.assertEqual(self.cli().returncode, 0)
        before = digest(self.database)
        replace = export_metrics.os.replace
        calls = []

        def fail_second(source, target):
            calls.append(target)
            if len(calls) == 2:
                raise OSError("simulated interrupted CSV replacement")
            return replace(source, target)

        with patch("export_metrics.os.replace", side_effect=fail_second), redirect_stdout(io.StringIO()):
            exit_code = export_metrics.main(["--bundle-dir", str(self.bundle), "--database", str(self.database),
                                             "--output-dir", str(self.output)])
        self.assertEqual(exit_code, 2)
        manifest = json.loads((self.output / "export_manifest.json").read_text())
        self.assertEqual((manifest["status"], manifest["exports_ready"]), ("export_failed", False))
        self.assertEqual(digest(self.database), before)


if __name__ == "__main__":
    unittest.main()
