"""No-renewal cohort/boundary/aggregation and separate export failure gates."""
from contextlib import closing, redirect_stdout
import csv
import datetime as dt
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
import check_scenario_input
import export_qualification_scenario as scenario
from load_data import BlockedLoad, load_bundle, sha256
from test_export_metrics import fixture
from validate_data import validate_directory, write_result

DATE = "2026-10-07"


def offset(days):
    return (dt.date.fromisoformat(DATE) + dt.timedelta(days=days)).isoformat()


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


class ScenarioSQLTests(unittest.TestCase):
    def test_expiration_endpoints_current_cohort_and_unavailable_people(self):
        units = [("U01", "A", 10), ("U02", "B", 2), ("U03", "C", 1)]
        people = [(f"P{i}", "U01", int(i != 8)) for i in range(10)]
        days = [0, 30, 31, 60, 61, 90, 91, 100, 100, 91]
        certificates = [(f"P{i}", "Q01", offset(1 if i == 7 else 0 if i == 9 else -30), offset(days[i]))
                        for i in range(10)]
        with closing(fixture(units, people, [("U01", "Q01", 8), ("U02", "Q01", 2)], certificates)) as connection:
            outputs, _ = scenario.query_outputs(connection, DATE)
        detail = outputs["qualification_scenario"]
        for horizon, projected in [(30, 6), (60, 4), (90, 2)]:
            a = next(r for r in detail if r["unit_id"] == "U01" and r["horizon_days"] == horizon)
            self.assertEqual(a["current_eligible_holder_count"], 7)
            self.assertEqual(a["projected_eligible_holder_count"], projected)
            self.assertEqual(a["projected_gap"], 8 - projected)
            self.assertEqual(a["additional_gap"], 7 - projected)
            self.assertEqual(a["is_new_gap"], 0)
            zero = next(r for r in detail if r["unit_id"] == "U02" and r["horizon_days"] == horizon)
            self.assertEqual((zero["current_eligible_holder_count"], zero["projected_gap"]), (0, 2))
        empty_unit = next(r for r in outputs["scenario_unit_summary"] if r["unit_id"] == "U03")
        self.assertEqual(empty_unit["qualification_pair_count"], 0)
        self.assertIsNone(empty_unit["projected_coverage_ratio"])

    def test_duplicates_surplus_multiple_qualifications_and_zero_demand(self):
        certificates = [("P1", "Q01", offset(-30), offset(30)),
            ("P1", "Q01", offset(-30), offset(30)),
            ("P2", "Q01", offset(-30), offset(91)),
            ("P3", "Q01", offset(-30), offset(91)),
            ("P1", "Q02", offset(-30), offset(91))]
        with closing(fixture([("U01", "A", 3), ("U02", "B", 1)],
                [("P1", "U01", 1), ("P2", "U01", 1), ("P3", "U01", 1)],
                [("U01", "Q01", 1), ("U01", "Q02", 1), ("U02", "Q01", 0)], certificates)) as connection:
            output, totals = scenario.query_outputs(connection, DATE)
        row = next(r for r in output["qualification_scenario"] if r["unit_id"] == "U01"
                   and r["qualification_id"] == "Q01" and r["horizon_days"] == 30)
        self.assertEqual((row["current_eligible_holder_count"], row["projected_eligible_holder_count"]), (3, 2))
        self.assertEqual((row["eligible_holders_lost"], row["additional_gap"], row["is_new_gap"]), (1, 0, 0))
        self.assertEqual(totals["30"]["current_eligible_holder_slots"], 4)
        self.assertEqual(totals["30"]["projected_coverage_ratio"], 1)
        zero = next(r for r in output["qualification_scenario"] if r["unit_id"] == "U02")
        self.assertIsNone(zero["current_coverage_ratio"])
        self.assertIsNone(zero["projected_coverage_ratio"])
        self.assertEqual((zero["current_is_fragile"], zero["projected_is_fragile"]), (0, 0))

    def test_new_gap_distinguished_from_worsening_existing_gap(self):
        certificates = [(p, "Q01", offset(-30), offset(expiry))
                        for p, expiry in [("P1", 30), ("P2", 91), ("P3", 30)]]
        with closing(fixture([("U01", "A", 2), ("U02", "B", 2)],
                [("P1", "U01", 1), ("P2", "U01", 1), ("P3", "U02", 1)],
                [("U01", "Q01", 2), ("U02", "Q01", 2)], certificates)) as connection:
            output, totals = scenario.query_outputs(connection, DATE)
        rows = {r["unit_id"]: r for r in output["qualification_scenario"] if r["horizon_days"] == 30}
        self.assertEqual((rows["U01"]["current_gap"], rows["U01"]["projected_gap"], rows["U01"]["is_new_gap"]), (0, 1, 1))
        self.assertEqual((rows["U02"]["current_gap"], rows["U02"]["projected_gap"], rows["U02"]["is_new_gap"]), (1, 2, 0))
        self.assertEqual((totals["30"]["current_gap"], totals["30"]["projected_gap"],
                          totals["30"]["additional_gap"], totals["30"]["new_gap_pairs"]), (1, 3, 2, 1))

    def test_weighted_selected_totals_empty_bound_values_and_mixed_horizon_guard(self):
        certs = [(p, "Q01", offset(-30), offset(expiry))
                 for p, expiry in [("P1", 91), ("P2", 91), ("P3", 30), ("P4", 91)]]
        with closing(fixture([("U01", "A", 2), ("U02", "B", 2)],
                [("P1", "U01", 1), ("P2", "U01", 1), ("P3", "U02", 1), ("P4", "U02", 1)],
                [("U01", "Q01", 1), ("U02", "Q01", 3)], certs)) as connection:
            output, _ = scenario.query_outputs(connection, DATE)
            selected = scenario.query_totals(connection, DATE, 30, ["U01", "U02"], ["Q01"])
            empty = scenario.query_totals(connection, DATE, 30, [])
            injected = scenario.query_totals(connection, DATE, 30, ["U01') OR 1=1 --"])
            with self.assertRaises(BlockedLoad): scenario.query_totals(connection, DATE, 31)
        self.assertEqual(selected["projected_coverage_ratio"], 2 / 4)
        self.assertNotAlmostEqual(selected["projected_coverage_ratio"], (1 + 1 / 3) / 2)
        self.assertEqual(empty, injected)
        self.assertEqual(empty["projected_gap"], 0)
        self.assertIsNone(empty["projected_coverage_ratio"])
        with self.assertRaises(BlockedLoad): scenario.selection_totals(output["qualification_scenario"])


class ScenarioExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ori-scenario-tests-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.source, self.bundle = self.work / "raw", self.work / "bundle"
        self.database, self.legacy = self.work / "readiness.sqlite3", self.work / "dashboard"
        self.output = self.legacy / "scenario"
        shutil.copytree(ROOT / "data/raw/clean", self.source)
        self.config = yaml.safe_load((ROOT / "config/project.yml").read_text())
        report, records = validate_directory(self.source, DATE)
        write_result(self.bundle, report, records)
        load_bundle(self.bundle, self.database, self.config)
        dashboard = ROOT / "data/processed/dashboard"
        for path in dashboard.rglob("*"):
            if path.is_file() and "scenario" not in path.relative_to(dashboard).parts:
                target = self.legacy / path.relative_to(dashboard)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)

    def cli(self, database=None, output=None):
        return subprocess.run([sys.executable, str(ROOT / "src/export_qualification_scenario.py"),
            "--bundle-dir", str(self.bundle), "--database", str(database or self.database),
            "--output-dir", str(output or self.output)], cwd=ROOT, capture_output=True, text=True)

    def hashes(self, directory, exclude_scenario=False):
        return {str(p.relative_to(directory)): sha256(p.read_bytes()) for p in directory.rglob("*")
                if p.is_file() and not (exclude_scenario and "scenario" in p.relative_to(directory).parts)}

    def good(self):
        run = self.cli()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        return json.loads((self.output / scenario.MANIFEST_NAME).read_text())

    def rewrite(self, rows):
        path = self.output / "qualification_scenario.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=scenario.DETAIL_COLUMNS, lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
        manifest_path = self.output / scenario.MANIFEST_NAME
        manifest = json.loads(manifest_path.read_text())
        manifest["files"][path.name].update(sha256=sha256(path.read_bytes()), rows=len(rows))
        manifest_path.write_text(json.dumps(manifest))

    def test_reference_matches_independent_sources_baseline_and_planted_pairs(self):
        manifest = self.good()
        detail = read_csv(self.output / "qualification_scenario.csv")
        people = {r["person_id"]: r for r in read_csv(self.source / "personnel.csv")}
        certs = read_csv(self.source / "personnel_qualifications.csv")
        baseline = {(r["unit_id"], r["qualification_id"]): r
                    for r in read_csv(self.legacy / "qualification_detail.csv")}
        for row in detail:
            current = {c["person_id"] for c in certs if c["qualification_id"] == row["qualification_id"]
                and people[c["person_id"]]["unit_id"] == row["unit_id"]
                and people[c["person_id"]]["is_available"] == "1"
                and c["valid_from"] <= DATE < c["expiration_date"]}
            survivors = {c["person_id"] for c in certs if c["person_id"] in current
                and c["qualification_id"] == row["qualification_id"] and c["expiration_date"] > row["horizon_date"]}
            self.assertEqual(int(row["current_eligible_holder_count"]), len(current))
            self.assertEqual(int(row["projected_eligible_holder_count"]), len(survivors))
            old = baseline[row["unit_id"], row["qualification_id"]]
            self.assertEqual(row["current_eligible_holder_count"], old["valid_available_holder_count"])
            self.assertEqual(row["current_gap"], old["current_gap"])
        checked = check_scenario_input.check_exports(self.output, self.config)
        expected = checked["expected_selections_by_horizon"]
        for horizon in ("30", "60", "90"):
            d = expected[horizon]["Unit D / Q04"]
            self.assertEqual((d["current_eligible_holder_slots"], d["projected_eligible_holder_slots"],
                d["current_gap"], d["projected_gap"], d["additional_gap"], d["new_gap_pairs"]), (6, 0, 0, 2, 2, 1))
            c = expected[horizon]["Unit C / Q06"]
            self.assertEqual((c["current_gap"], c["projected_gap"], c["additional_gap"], c["new_gap_pairs"]), (1, 2, 1, 0))
            b = expected[horizon]["Unit B / Q03"]
            self.assertEqual((b["current_gap"], b["projected_gap"], b["projected_fragile_pairs"]), (0, 0, 1))
            self.assertEqual(expected[horizon]["All"], manifest["global_components_by_horizon"][horizon])

    def test_repeat_preserves_all_prior_bundles_database_and_sources(self):
        before = sha256(self.database.read_bytes()), self.hashes(self.source), self.hashes(self.legacy)
        first, second = self.good(), self.good()
        self.assertEqual({n: e["sha256"] for n, e in first["files"].items()},
                         {n: e["sha256"] for n, e in second["files"].items()})
        self.assertEqual(sha256(self.database.read_bytes()), before[0])
        self.assertEqual(self.hashes(self.source), before[1])
        self.assertEqual(self.hashes(self.legacy, True), before[2])
        self.assertEqual({n: e["rows"] for n, e in first["files"].items()},
                         {"qualification_scenario.csv": 144, "scenario_unit_summary.csv": 18})

    def test_blocked_validation_invalidates_old_pass_without_replacing_csvs(self):
        manifest = self.good()
        path = self.bundle / "validation_report.json"
        report = json.loads(path.read_text()); report["load_allowed"] = False
        path.write_text(json.dumps(report))
        self.assertEqual(self.cli().returncode, 1)
        self.assertFalse(json.loads((self.output / scenario.MANIFEST_NAME).read_text())["exports_ready"])
        for name, entry in manifest["files"].items():
            self.assertEqual(sha256((self.output / name).read_bytes()), entry["sha256"])

    def test_changed_database_or_source_is_blocked_and_database_unchanged(self):
        self.good()
        db = self.work / "changed.sqlite3"; shutil.copyfile(self.database, db)
        with closing(sqlite3.connect(db)) as connection:
            connection.execute("UPDATE personnel SET is_available=1-is_available WHERE person_id='P0001'")
            connection.commit()
        before = sha256(db.read_bytes())
        self.assertEqual(self.cli(database=db).returncode, 1)
        self.assertEqual(sha256(db.read_bytes()), before)
        path = self.source / "units.csv"
        path.write_bytes(path.read_bytes().replace(b"Unit A", b"Changed fictional unit"))
        self.assertEqual(self.cli().returncode, 1)

    def test_missing_database_is_not_created_and_invalidates_prior_pass(self):
        self.good(); missing = self.work / "missing.sqlite3"
        self.assertEqual(self.cli(database=missing).returncode, 2)
        self.assertFalse(missing.exists())
        self.assertFalse(json.loads((self.output / scenario.MANIFEST_NAME).read_text())["exports_ready"])

    def test_protected_inputs_environment_and_report_file_remain_untouched(self):
        for folder in (self.source, self.bundle, self.work / ".git", self.work / ".venv"):
            before = self.hashes(folder) if folder.exists() else {}
            self.assertEqual(self.cli(output=folder).returncode, 1)
            self.assertEqual(self.hashes(folder) if folder.exists() else {}, before)
        report = self.work / "saved.pbix"; report.write_bytes(b"saved report sentinel")
        self.assertEqual(self.cli(output=report).returncode, 1)
        self.assertEqual(report.read_bytes(), b"saved report sentinel")

    def test_interrupted_second_replacement_disables_refresh(self):
        self.good(); replace = scenario.os.replace; calls = []
        def fail_second(source, target):
            calls.append(target)
            if len(calls) == 2: raise OSError("simulated interrupted scenario export")
            return replace(source, target)
        with patch("export_qualification_scenario.os.replace", side_effect=fail_second), redirect_stdout(io.StringIO()):
            code = scenario.main(["--bundle-dir", str(self.bundle), "--database", str(self.database),
                                  "--output-dir", str(self.output)])
        self.assertEqual(code, 2)
        self.assertFalse(json.loads((self.output / scenario.MANIFEST_NAME).read_text())["exports_ready"])

    def test_checker_is_read_only_and_blocks_hash_grain_and_cross_horizon_tampering(self):
        self.good(); before = self.hashes(self.output)
        check_scenario_input.check_exports(self.output, self.config)
        self.assertEqual(self.hashes(self.output), before)
        path = self.output / "qualification_scenario.csv"; original = path.read_bytes()
        path.write_bytes(original + b"\n")
        with self.assertRaises(BlockedLoad): check_scenario_input.check_exports(self.output, self.config)
        path.write_bytes(original)
        rows = read_csv(path); rows.append(rows[0].copy()); self.rewrite(rows)
        with self.assertRaises(BlockedLoad): check_scenario_input.check_exports(self.output, self.config)
        self.good(); rows = read_csv(path)
        row = next(r for r in rows if r["horizon_days"] == "60" and int(r["current_eligible_holder_count"]) > 0)
        unit = next(u for u in self.config["units"] if u["unit_id"] == row["unit_id"])
        qualification = next(q for q in self.config["qualification_types"] if q["qualification_id"] == row["qualification_id"])
        row.update(scenario.pair_snapshot(unit, qualification, row, int(row["current_eligible_holder_count"]) + 1,
                                         int(row["projected_eligible_holder_count"]), DATE, 60))
        self.rewrite(rows)
        with self.assertRaises(BlockedLoad): check_scenario_input.check_exports(self.output, self.config)
        self.good(); rows = read_csv(path)
        key = next((r["unit_id"], r["qualification_id"]) for r in rows if int(r["current_eligible_holder_count"]) > 0)
        for row in rows:
            if (row["unit_id"], row["qualification_id"]) == key:
                h = int(row["horizon_days"])
                row.update(scenario.pair_snapshot(
                    next(u for u in self.config["units"] if u["unit_id"] == key[0]),
                    next(q for q in self.config["qualification_types"] if q["qualification_id"] == key[1]),
                    row, int(row["current_eligible_holder_count"]), int(h == 60), DATE, h))
        self.rewrite(rows)
        with self.assertRaises(BlockedLoad): check_scenario_input.check_exports(self.output, self.config)


if __name__ == "__main__":
    unittest.main()
