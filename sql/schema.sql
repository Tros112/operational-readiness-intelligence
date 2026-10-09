-- Six source tables used by the Day 4 loader. SQLite >= 3.37 (STRICT tables).
-- Synthetic operational data only; no analytical marts are defined here.
-- Calendar validity is checked in Python before load; TEXT dates use ISO YYYY-MM-DD.
-- The loader must enable foreign keys on every connection, outside a transaction.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS units (
    unit_id TEXT PRIMARY KEY NOT NULL CHECK (length(trim(unit_id)) > 0),
    unit_name TEXT NOT NULL CHECK (length(trim(unit_name)) > 0),
    required_personnel_count INTEGER NOT NULL CHECK (required_personnel_count > 0)
) STRICT;

CREATE TABLE IF NOT EXISTS personnel (
    person_id TEXT PRIMARY KEY NOT NULL CHECK (length(trim(person_id)) > 0),
    unit_id TEXT NOT NULL REFERENCES units(unit_id),
    is_available INTEGER NOT NULL CHECK (is_available IN (0, 1))
) STRICT;

CREATE TABLE IF NOT EXISTS qualification_types (
    qualification_id TEXT PRIMARY KEY NOT NULL CHECK (length(trim(qualification_id)) > 0),
    qualification_name TEXT NOT NULL CHECK (length(trim(qualification_name)) > 0)
) STRICT;

CREATE TABLE IF NOT EXISTS personnel_qualifications (
    person_id TEXT NOT NULL REFERENCES personnel(person_id),
    qualification_id TEXT NOT NULL REFERENCES qualification_types(qualification_id),
    valid_from TEXT NOT NULL CHECK (length(valid_from) = 10),
    expiration_date TEXT NOT NULL CHECK (length(expiration_date) = 10),
    PRIMARY KEY (person_id, qualification_id),
    CHECK (expiration_date > valid_from)
) STRICT;

CREATE TABLE IF NOT EXISTS unit_qualification_requirements (
    unit_id TEXT NOT NULL REFERENCES units(unit_id),
    qualification_id TEXT NOT NULL REFERENCES qualification_types(qualification_id),
    required_holder_count INTEGER NOT NULL CHECK (required_holder_count > 0),
    PRIMARY KEY (unit_id, qualification_id)
) STRICT;

CREATE TABLE IF NOT EXISTS admin_cases (
    case_id TEXT PRIMARY KEY NOT NULL CHECK (length(trim(case_id)) > 0),
    unit_id TEXT NOT NULL REFERENCES units(unit_id),
    case_type TEXT NOT NULL CHECK (length(trim(case_type)) > 0),
    opened_date TEXT NOT NULL CHECK (length(opened_date) = 10),
    closed_date TEXT CHECK (closed_date IS NULL OR length(closed_date) = 10),
    correction_required INTEGER CHECK (correction_required IN (0, 1)),
    CHECK (closed_date IS NULL OR closed_date >= opened_date),
    CHECK (
        (closed_date IS NULL AND correction_required IS NULL)
        OR (closed_date IS NOT NULL AND correction_required IS NOT NULL)
    )
) STRICT;
