"""Generate six clean, reproducible synthetic source tables. No database load.

Background draws happen first; documented scenario overrides happen second.
The manifest has no wall-clock timestamp, so repeated runs can match byte for byte.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import pandas as pd
import yaml

from check_environment import check_config

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = {
    "units": ["unit_id", "unit_name", "required_personnel_count"],
    "personnel": ["person_id", "unit_id", "is_available"],
    "qualification_types": ["qualification_id", "qualification_name"],
    "personnel_qualifications": ["person_id", "qualification_id", "valid_from", "expiration_date"],
    "unit_qualification_requirements": ["unit_id", "qualification_id", "required_holder_count"],
    "admin_cases": ["case_id", "unit_id", "case_type", "opened_date", "closed_date", "correction_required"],
}
KEYS = {
    "units": ["unit_id"], "personnel": ["person_id"],
    "qualification_types": ["qualification_id"],
    "personnel_qualifications": ["person_id", "qualification_id"],
    "unit_qualification_requirements": ["unit_id", "qualification_id"],
    "admin_cases": ["case_id"],
}


def inclusive_days(rng: np.random.Generator, bounds: list[int]) -> int:
    return int(rng.integers(bounds[0], bounds[1] + 1))


def make_personnel(config: dict, rng: np.random.Generator) -> list[dict]:
    rows = []
    shortfall = config["scenarios"]["staffing_shortfall"]
    for unit in sorted(config["units"], key=lambda row: row["unit_id"]):
        size = unit["personnel_count"]
        flags = rng.random(size) < config["background"]["availability_probability"]
        if unit["unit_id"] == shortfall["unit_id"]:
            flags[:] = False
            flags[rng.choice(size, size=shortfall["available_personnel_count"], replace=False)] = True
        elif flags.sum() < unit["required_personnel_count"]:
            # A documented floor keeps the non-shortfall units staffed in this simulation.
            missing = unit["required_personnel_count"] - int(flags.sum())
            flags[rng.choice(np.flatnonzero(~flags), size=missing, replace=False)] = True
        for flag in flags:
            rows.append({"person_id": f"P{len(rows) + 1:04d}", "unit_id": unit["unit_id"],
                         "is_available": int(flag)})
    return rows


def make_certificates(config: dict, people: list[dict], rng: np.random.Generator) -> list[dict]:
    D = dt.date.fromisoformat(config["as_of_date"])
    background = config["background"]
    status_names = ["valid", "expired", "future_start"]
    probabilities = [background["certificate_status_probabilities"][name] for name in status_names]
    qualification_ids = sorted(row["qualification_id"] for row in config["qualification_types"])
    certificates = {}
    for person in people:
        for qualification_id in qualification_ids:
            if rng.random() >= background["qualification_assignment_probability"]:
                continue
            status = str(rng.choice(status_names, p=probabilities))
            age_or_duration = inclusive_days(
                rng, background["valid_certificate_age_days"] if status == "valid"
                else background["inactive_certificate_duration_days"]
            )
            if status == "valid":
                valid_from = D - dt.timedelta(days=age_or_duration)
                expiration = D + dt.timedelta(days=inclusive_days(rng, background["valid_certificate_remaining_days"]))
            elif status == "expired":
                expiration = D - dt.timedelta(days=inclusive_days(rng, background["expired_days_ago"]))
                valid_from = expiration - dt.timedelta(days=age_or_duration)
            else:
                valid_from = D + dt.timedelta(days=inclusive_days(rng, background["future_start_days"]))
                expiration = valid_from + dt.timedelta(days=age_or_duration)
            key = (person["person_id"], qualification_id)
            certificates[key] = {"person_id": key[0], "qualification_id": key[1],
                                 "valid_from": valid_from.isoformat(), "expiration_date": expiration.isoformat()}

    # Replace the targeted groups explicitly, rather than hoping random draws create them.
    for name in ("fragile_qualification", "renewal_cluster"):
        scenario = config["scenarios"][name]
        unit_people = [p for p in people if p["unit_id"] == scenario["unit_id"]]
        for person in unit_people:
            certificates.pop((person["person_id"], scenario["qualification_id"]), None)
        candidates = sorted(p["person_id"] for p in unit_people if p["is_available"] == 1)
        selected = sorted(str(p) for p in rng.choice(candidates, size=scenario["valid_available_holder_count"], replace=False))
        offsets = ([scenario["expiration_offset_days"]] if name == "fragile_qualification"
                   else scenario["expiration_offsets_days"])
        for person_id, offset in zip(selected, offsets, strict=True):
            key = (person_id, scenario["qualification_id"])
            certificates[key] = {"person_id": key[0], "qualification_id": key[1],
                                 "valid_from": (D - dt.timedelta(days=background["scenario_valid_from_days_ago"])).isoformat(),
                                 "expiration_date": (D + dt.timedelta(days=offset)).isoformat()}
    return list(certificates.values())


def make_cases(config: dict, rng: np.random.Generator) -> list[dict]:
    D = dt.date.fromisoformat(config["as_of_date"])
    background = config["background"]
    hotspot = config["scenarios"]["discrepancy_hotspot"]
    unit_ids = sorted(row["unit_id"] for row in config["units"])
    rows = []
    for number in range(1, config["scope"]["admin_case_count"] + 1):
        unit_id = str(rng.choice(unit_ids))
        case_type = str(rng.choice(background["case_types"]))
        days_ago = int(rng.integers(0, config["scope"]["admin_lookback_days"]))
        opened = D - dt.timedelta(days=days_ago)
        closed = None
        correction = None
        if rng.random() >= background["open_case_probability"]:
            candidate = opened + dt.timedelta(days=inclusive_days(rng, background["case_cycle_time_days"]))
            if candidate <= D:
                closed = candidate.isoformat()
                probability = (hotspot["completed_case_correction_probability"] if unit_id == hotspot["unit_id"]
                               else background["completed_case_correction_probability"])
                correction = int(rng.random() < probability)
        # A candidate completion after D stays open; do not invent an earlier completion.
        rows.append({"case_id": f"C{number:05d}", "unit_id": unit_id, "case_type": case_type,
                     "opened_date": opened.isoformat(), "closed_date": closed,
                     "correction_required": correction})
    return rows


def generate_tables(config: dict) -> dict[str, pd.DataFrame]:
    check_config(config)
    rng = np.random.default_rng(config["seed"])
    unit_specs = sorted(config["units"], key=lambda row: row["unit_id"])
    qualification_specs = sorted(config["qualification_types"], key=lambda row: row["qualification_id"])
    people = make_personnel(config, rng)
    fragile = config["scenarios"]["fragile_qualification"]
    requirements = []
    for unit in unit_specs:
        for qualification in qualification_specs:
            pair = (unit["unit_id"], qualification["qualification_id"])
            count = (fragile["required_holder_count"] if pair == (fragile["unit_id"], fragile["qualification_id"])
                     else config["background"]["default_required_holder_count"])
            requirements.append({"unit_id": pair[0], "qualification_id": pair[1], "required_holder_count": count})
    rows = {
        "units": [{key: unit[key] for key in COLUMNS["units"]} for unit in unit_specs],
        "personnel": people,
        "qualification_types": qualification_specs,
        "personnel_qualifications": make_certificates(config, people, rng),
        "unit_qualification_requirements": requirements,
        "admin_cases": make_cases(config, rng),
    }
    tables = {}
    for name, columns in COLUMNS.items():
        frame = pd.DataFrame.from_records(rows[name], columns=columns)
        if name == "admin_cases":
            frame["correction_required"] = frame["correction_required"].astype("Int64")
        tables[name] = frame.sort_values(KEYS[name], kind="stable").reset_index(drop=True)
    return tables


def write_tables(tables: dict[str, pd.DataFrame], output_dir: Path, config: dict, config_path: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for name, frame in tables.items():
        path = output_dir / f"{name}.csv"
        frame.to_csv(path, index=False, encoding="utf-8", lineterminator="\n", na_rep="")
        files[path.name] = {"rows": len(frame), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "columns": list(frame.columns), "primary_key": KEYS[name]}
    manifest = {
        "data_classification": "synthetic_only", "as_of_date": config["as_of_date"], "seed": config["seed"],
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "versions": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__},
        "random_generator": "NumPy default_rng (PCG64)", "files": files,
        "scenario_settings": config["scenarios"],
        "limits": "Clean synthetic reference only. Dirty-input handling, persistent loading, analytical marts, and Power BI reconciliation are pending.",
    }
    (output_dir / "generation_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/project.yml")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/raw/clean")
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    tables = generate_tables(config)
    manifest = write_tables(tables, args.output_dir, config, args.config)
    print(json.dumps({"status": "generated", "data_classification": "synthetic_only", "as_of_date": config["as_of_date"],
                      "output_dir": str(args.output_dir.resolve()),
                      "row_counts": {name.removesuffix(".csv"): details["rows"] for name, details in manifest["files"].items()}}, indent=2))


if __name__ == "__main__":
    main()
