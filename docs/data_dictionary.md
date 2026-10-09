# Data dictionary

Version 1.0 · Day 2, executed October 7, 2026. **All operational records and numbers are synthetic.** Analysis date is 2026-10-07; seed is 20261007. No official Navy requirements are represented.

## Files and grain

Six clean reference CSVs live in `data/raw/clean/`. UTF-8, comma-delimited, header row, no index column, LF line endings. Rows are sorted by primary key. `generation_manifest.json` records source/configuration hashes, row counts, versions, seed, and scenario settings; it is metadata, not a seventh source table.

| File | Row grain | Actual rows | Key |
| --- | --- | --- | --- |
| `units.csv` | One fictional unit | 6 | unit_id |
| `personnel.csv` | One person at D | 300 | person_id |
| `qualification_types.csv` | One fictional qualification | 8 | qualification_id |
| `personnel_qualifications.csv` | One person's recorded certificate for a qualification | 265 | person_id + qualification_id |
| `unit_qualification_requirements.csv` | One unit/qualification requirement | 48 | unit_id + qualification_id |
| `admin_cases.csv` | One administrative case | 600 | case_id |

## Fields

| Table | Field | Type / nullable | Meaning and rule |
| --- | --- | --- | --- |
| units | unit_id | TEXT / no | U01–U06; unique, invented unit key |
| units | unit_name | TEXT / no | Unit A–Unit F; fictional display label |
| units | required_personnel_count | INTEGER / no | Positive staffing requirement; 50 for Unit C, 40 for other units |
| personnel | person_id | TEXT / no | P0001–P0300; unique, invented person key, no real identifier |
| personnel | unit_id | TEXT / no | FK to units; exactly one current unit per person |
| personnel | is_available | INTEGER / no | Snapshot flag: 1 available, 0 unavailable; no reason/history implied |
| qualification_types | qualification_id | TEXT / no | Q01–Q08; unique qualification key |
| qualification_types | qualification_name | TEXT / no | Fictional skill/qualification label from configuration |
| personnel_qualifications | person_id | TEXT / no | FK to personnel; part of composite key |
| personnel_qualifications | qualification_id | TEXT / no | FK to qualification_types; part of composite key |
| personnel_qualifications | valid_from | ISO date TEXT / no | Inclusive first valid date; must be a real calendar date |
| personnel_qualifications | expiration_date | ISO date TEXT / no | Exclusive first invalid date; strictly later than valid_from |
| unit_qualification_requirements | unit_id | TEXT / no | FK to units; part of composite key |
| unit_qualification_requirements | qualification_id | TEXT / no | FK to qualification_types; part of composite key |
| unit_qualification_requirements | required_holder_count | INTEGER / no | Positive fictional requirement; normally 2, Unit B/Q03 set to 1 |
| admin_cases | case_id | TEXT / no | C00001–C00600; unique invented case key |
| admin_cases | unit_id | TEXT / no | Unit owning the case; FK to units |
| admin_cases | case_type | TEXT / no | onboarding, records_update, transfer, or evaluation |
| admin_cases | opened_date | ISO date TEXT / no | Actual simulated opening; generated July 10–October 7 inclusive |
| admin_cases | closed_date | ISO date TEXT / yes | Completion; must be on/after opening. Blank CSV field represents SQL NULL |
| admin_cases | correction_required | INTEGER / yes | Completed: 1 correction required, 0 no correction. Open: unknown, represented by blank/NULL |

## Date, eligibility, and null rules

All dates use `YYYY-MM-DD`. Python checks actual calendar validity. Date eligibility at D is `valid_from <= D < expiration_date` and is distinct from source quality: an expired or not-yet-active certificate can be a perfectly clean record. A missing certificate row represents no recorded certificate for that pair; never invent certificate dates.

The reference contains **193 currently valid certificates**, **49 expired certificates**, and **23 with a future valid-from date**. Among the 193 valid records, 172 belong to currently available people. Certificate totals are not headcounts. Availability is only the one configured snapshot; cases do not reconstruct personnel history.

Open cases have both `closed_date` and `correction_required` blank. CSV has no intrinsic null type; the future validator/loader must interpret blank only in these nullable fields as NULL. Critical IDs/dates cannot be silently filled. A known no-correction outcome is the explicit value 0, not a blank.

There are **442 completed and 158 open cases** in this reference. Completion dates never exceed D. Random candidate completions beyond D are left open; this increases the realized open share above the configured 20% open draw. Outcome flags are sampled only for cases completed by D.

## Generator settings and intentional scenarios

All background probabilities/ranges and four overrides are in `config/project.yml`. Background certificate assignment is 12%; assigned records draw valid/expired/future-start categories with probabilities 75%/15%/10%. These are generation settings, not estimated real-world rates. Holder requirements use all 48 unit/qualification pairs and total 95 qualification slots.

For valid background certificates, age since valid-from is 30–365 days and remaining life is 1–180 days; these are separate settings. Expired/future-start records use a full certificate term of 30–365 days. Expired dates fall 0–60 days before D; future starts fall 1–30 days after D. Integer day-range endpoints are included. These fictional distributions are not qualification-policy claims.

Unit C is forced to 40 available out of 50 required. Other units have a documented availability floor at their requirement. Unit B/Q03 is replaced by exactly one valid available holder. Unit D/Q04 is replaced by six valid available holders expiring after 7, 10, 14, 20, 25, and 30 days. Overrides remove the previous background records in the targeted qualification group and use distinct available people.

Unit F's completed-case correction probability is 30%, compared with 6% elsewhere. The realized rates are **27/70 = 38.6%** in Unit F and **18/372 = 4.8%** pooled elsewhere. The generator does not resample to force a prettier rate or exact quota. These are planted simulation outcomes, not empirical or causal findings.

## Lineage and current limits

`config/project.yml` → `src/generate_data.py` → six clean CSVs/manifest → generator checks. Day 3 adds `src/inject_defects.py` → separate dirty copy/catalog and `src/validate_data.py` → accepted records, quarantined raw cells/reasons, and a batch gate. Day 4 adds the verified, atomic six-table SQLite load. Day 5 reads that database without changing it and exports current staffing/qualification/expiration metrics with explicit grains. All 42 tests pass on Linux; Day 4's 32-test Windows suite was inspected, while Windows Day 5 remains pending. Source column definitions and metric eligibility rules are unchanged.

The clean reference remains unchanged. Clean input passes with 1,227 accepted and no rejected rows. Dirty input reconciles 1,229 = 1,210 accepted + 19 rejected and is blocked; its accepted subset is diagnostic only. Rules/reasons: `docs/validation_rules.md`; exact injected records: `data/raw/dirty/defect_manifest.json`. Dashboard fields/types/aggregation rules: `docs/export_dictionary.md`. Process metrics, no-renewal projections, the production Power BI report, and SQL/Power BI reconciliation remain later milestones. No real names, military IDs, or system extracts are used.
