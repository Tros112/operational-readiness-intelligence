"""Day 2 clean-generator checks, not the Day 3 dirty-input validator."""

import copy
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from generate_data import COLUMNS, KEYS, generate_tables


def current_available_certificates(tables, D):
    certificates = tables["personnel_qualifications"].merge(
        tables["personnel"], on="person_id", how="left", validate="many_to_one"
    )
    date = D.isoformat()
    return certificates.loc[
        (certificates["is_available"] == 1)
        & (certificates["valid_from"] <= date)
        & (certificates["expiration_date"] > date)
    ]


class CleanGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = yaml.safe_load((ROOT / "config/project.yml").read_text())
        cls.D = dt.date.fromisoformat(cls.config["as_of_date"])
        cls.tables = generate_tables(cls.config)

    def test_source_counts_keys_and_foreign_keys(self):
        expected = {"units": 6, "personnel": 300, "qualification_types": 8,
                    "unit_qualification_requirements": 48, "admin_cases": 600}
        for name, count in expected.items():
            self.assertEqual(len(self.tables[name]), count, name)
        for name, frame in self.tables.items():
            self.assertEqual(list(frame.columns), COLUMNS[name], name)
            self.assertFalse(frame.duplicated(KEYS[name]).any(), name)
            self.assertFalse(frame[KEYS[name]].isna().any().any(), name)
        # Populated memory-only schema probe verifies the six-table integration.
        with sqlite3.connect(":memory:") as connection:
            connection.executescript((ROOT / "sql/schema.sql").read_text())
            for name, frame in self.tables.items():
                values = [tuple(None if pd.isna(value) else int(value) if isinstance(value, np.integer) else value
                                for value in row) for row in frame.itertuples(index=False, name=None)]
                columns = ", ".join(COLUMNS[name])
                placeholders = ", ".join("?" for _ in COLUMNS[name])
                connection.executemany(f"INSERT INTO {name} ({columns}) VALUES ({placeholders})", values)
                self.assertEqual(connection.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0], len(frame))
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_calendar_dates_and_case_lifecycle(self):
        for row in self.tables["personnel_qualifications"].itertuples(index=False):
            valid_from = dt.date.fromisoformat(row.valid_from)
            expiration = dt.date.fromisoformat(row.expiration_date)
            self.assertLess(valid_from, expiration)
        start = self.D - dt.timedelta(days=self.config["scope"]["admin_lookback_days"] - 1)
        for row in self.tables["admin_cases"].itertuples(index=False):
            opened = dt.date.fromisoformat(row.opened_date)
            self.assertTrue(start <= opened <= self.D)
            self.assertIn(row.case_type, self.config["background"]["case_types"])
            if row.closed_date is None:
                self.assertTrue(pd.isna(row.correction_required))
            else:
                closed = dt.date.fromisoformat(row.closed_date)
                self.assertTrue(opened <= closed <= self.D)
                self.assertIn(int(row.correction_required), (0, 1))
                self.assertLessEqual((closed - opened).days, self.config["background"]["case_cycle_time_days"][1])

    def test_staffing_shortfall_is_exact_and_local(self):
        staffing = self.tables["personnel"].groupby("unit_id")["is_available"].sum()
        requirements = self.tables["units"].set_index("unit_id")["required_personnel_count"]
        scenario = self.config["scenarios"]["staffing_shortfall"]
        self.assertEqual(int(staffing[scenario["unit_id"]]), scenario["available_personnel_count"])
        self.assertEqual(list(staffing.index[staffing < requirements]), [scenario["unit_id"]])

    def test_fragile_certificate_has_one_available_holder(self):
        scenario = self.config["scenarios"]["fragile_qualification"]
        eligible = current_available_certificates(self.tables, self.D)
        pair = eligible.loc[(eligible["unit_id"] == scenario["unit_id"])
                            & (eligible["qualification_id"] == scenario["qualification_id"])]
        self.assertEqual(pair["person_id"].nunique(), 1)
        requirement = self.tables["unit_qualification_requirements"].loc[
            (self.tables["unit_qualification_requirements"]["unit_id"] == scenario["unit_id"])
            & (self.tables["unit_qualification_requirements"]["qualification_id"] == scenario["qualification_id"])
        ]
        self.assertEqual(int(requirement["required_holder_count"].iloc[0]), 1)

    def test_renewal_cluster_matches_inclusive_30_day_boundary(self):
        scenario = self.config["scenarios"]["renewal_cluster"]
        eligible = current_available_certificates(self.tables, self.D)
        pair = eligible.loc[(eligible["unit_id"] == scenario["unit_id"])
                            & (eligible["qualification_id"] == scenario["qualification_id"])]
        self.assertEqual(pair["person_id"].nunique(), 6)
        offsets = sorted((dt.date.fromisoformat(date) - self.D).days for date in pair["expiration_date"])
        self.assertEqual(offsets, sorted(scenario["expiration_offsets_days"]))
        self.assertEqual(sum(pair["expiration_date"] <= (self.D + dt.timedelta(days=30)).isoformat()), 6)
        self.assertEqual(sum(pair["expiration_date"] > (self.D + dt.timedelta(days=30)).isoformat()), 0)

    def test_hotspot_probability_is_explicit_and_outcomes_are_observable(self):
        scenario = self.config["scenarios"]["discrepancy_hotspot"]
        self.assertGreater(scenario["completed_case_correction_probability"],
                           self.config["background"]["completed_case_correction_probability"])
        cases = self.tables["admin_cases"]
        completed = cases.loc[cases["closed_date"].notna()]
        self.assertGreater(len(completed.loc[completed["unit_id"] == scenario["unit_id"]]), 0)
        self.assertGreater(len(completed.loc[completed["unit_id"] != scenario["unit_id"]]), 0)
        # A probability is not a quota; do not resample to force an attractive rate.

    def test_two_cold_cli_runs_produce_identical_files_and_nulls(self):
        with tempfile.TemporaryDirectory(prefix="ori-repeatability-") as temp:
            folders = [Path(temp) / "first", Path(temp) / "second"]
            for folder in folders:
                subprocess.run([sys.executable, str(ROOT / "src/generate_data.py"),
                                "--config", str(ROOT / "config/project.yml"), "--output-dir", str(folder)],
                               check=True, capture_output=True, text=True)
            names = {f"{name}.csv" for name in COLUMNS} | {"generation_manifest.json"}
            self.assertEqual({path.name for path in folders[0].iterdir()}, names)
            for name in names:
                self.assertEqual((folders[0] / name).read_bytes(), (folders[1] / name).read_bytes(), name)
            manifest = json.loads((folders[0] / "generation_manifest.json").read_text())
            for name, details in manifest["files"].items():
                self.assertEqual(hashlib.sha256((folders[0] / name).read_bytes()).hexdigest(), details["sha256"])
            with (folders[0] / "admin_cases.csv").open(newline="") as stream:
                cases = list(csv.DictReader(stream))
            self.assertTrue(any(row["closed_date"] == "" for row in cases))
            for case in cases:
                self.assertEqual(case["correction_required"] == "", case["closed_date"] == "")
                if case["closed_date"]:
                    self.assertIn(case["correction_required"], ("0", "1"))

    def test_different_seed_changes_random_tables_and_bad_configuration_fails(self):
        different = copy.deepcopy(self.config)
        different["seed"] += 1
        other = generate_tables(different)
        for name in ("personnel", "personnel_qualifications", "admin_cases"):
            self.assertFalse(self.tables[name].equals(other[name]), name)
        bad = copy.deepcopy(self.config)
        bad["background"]["certificate_status_probabilities"]["valid"] = 0.80
        with self.assertRaisesRegex(ValueError, "sum to one"):
            generate_tables(bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
