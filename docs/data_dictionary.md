# Data dictionary

Documentation version 1.1 · Day 11 review, October 20, 2026; source schemas/rules remain unchanged from Day 2. **All operational records and numbers are synthetic.** Analysis date is 2026-10-07; seed is 20261007. No official Navy requirements are represented. Read the [runbook](reproduce.md), [export dictionary](export_dictionary.md) and [limitations](limitations.md) alongside these source fields.

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

Open source cases have both closed_date and correction_required blank. CSV has no intrinsic null type; the implemented validator/loader interprets blank only in these nullable fields as NULL. Critical IDs/dates cannot be silently filled. A known no-correction outcome is explicit 0. The as-of process export separately masks any source completion/outcome after D; an allowed source value is not automatically an eligible current outcome.

There are **442 completed and 158 open cases** in this reference. Completion dates never exceed D. Random candidate completions beyond D are left open; this increases the realized open share above the configured 20% open draw. Outcome flags are sampled only for cases completed by D.

## Generator settings and intentional scenarios

All background probabilities/ranges and four overrides are in `config/project.yml`. Background certificate assignment is 12%; assigned records draw valid/expired/future-start categories with probabilities 75%/15%/10%. These are generation settings, not estimated real-world rates. Holder requirements use all 48 unit/qualification pairs and total 95 qualification slots.

For valid background certificates, age since valid-from is 30–365 days and remaining life is 1–180 days; these are separate settings. Expired/future-start records use a full certificate term of 30–365 days. Expired dates fall 0–60 days before D; future starts fall 1–30 days after D. Integer day-range endpoints are included. These fictional distributions are not qualification-policy claims.

Unit C is forced to 40 available out of 50 required. Other units have a documented availability floor at their requirement. Unit B/Q03 is replaced by exactly one valid available holder. Unit D/Q04 is replaced by six valid available holders expiring after 7, 10, 14, 20, 25, and 30 days. Overrides remove the previous background records in the targeted qualification group and use distinct available people.

Unit F's completed-case correction probability is 30%, compared with 6% elsewhere. The realized rates are **27/70 = 38.6%** in Unit F and **18/372 = 4.8%** pooled elsewhere. The generator does not resample to force a prettier rate or exact quota. These are planted simulation outcomes, not empirical or causal findings.

## Lineage and current limits

config/project.yml → generator → six clean CSVs/manifest → separate dirty copy/catalog → validation accepted/quarantined records and batch gate → atomic six-table SQLite load. Read-only SQL exporters derive original, process and scenario bundles with explicit grains. Full 72-test Linux/Windows evidence and report acceptance through Day 10 are recorded; Day 11's focused twelve existing tests pass separately. Source column definitions and metric eligibility rules remain unchanged.

The clean reference remains unchanged. Clean input passes with 1,227 accepted and no rejected rows. Dirty input reconciles 1,229 = 1,210 accepted + 19 rejected and is blocked; its accepted subset is diagnostic only. Rules/reasons: [validation rules](validation_rules.md); exact injected records are generated in data/raw/dirty/defect_manifest.json. [Export fields/types/aggregation](export_dictionary.md) cover the implemented process and no-renewal bundles. User-operated report reconciliation/reopening is accepted through Day 10; exact installed definitions/PBIX remain uninspected by the assistant. No real names, military IDs, system extracts or production deployment are used.

## Key relationships and history scope

| Child field | Referenced key | Cardinality / meaning |
| --- | --- | --- |
| personnel.unit_id | units.unit_id | Many people to one current unit; no dated assignment history. |
| personnel_qualifications.person_id | personnel.person_id | Many qualifications to one person. The person/qualification key allows one recorded certificate per pair, not successive renewal history. |
| personnel_qualifications.qualification_id | qualification_types.qualification_id | Many person records to one qualification type. |
| unit_qualification_requirements.unit_id | units.unit_id | Eight required qualification pairs per unit in this reference. |
| unit_qualification_requirements.qualification_id | qualification_types.qualification_id | The unit/qualification key defines demand independently of certificate presence. |
| admin_cases.unit_id | units.unit_id | Many cases to one owning unit; no case-to-person assignment is modeled. |

Keys identify records; display names do not replace them. Source uniqueness rejects duplicate keys, while defensive SQL fixtures separately check distinct-holder behavior after joins. LEFT JOIN preserves requirements with no matched holder; it does not itself guarantee uniqueness. See [schema](../sql/schema.sql), [metric contract](metric_contract.md) and [remaining SQL learning](sql_review_backlog.md).

## Files after validation and loading

| Location | Meaning / authorization |
| --- | --- |
| data/raw/clean/ | Generated six-table synthetic reference. |
| data/raw/dirty/ | Separate fault-injection copy; clean input is preserved. |
| data/processed/validation_clean/accepted/ | Loader input only when the containing validation_report.json is passed, load_allowed true, and source/output hashes and values agree. |
| data/rejected/day03_dirty/ | Runbook's diagnostic dirty bundle: accepted CSVs, rejected_rows.csv, validation_issues.csv and blocked validation_report.json. Accepted rows here grant no load permission. |
| data/processed/readiness.sqlite3 | Verified six source tables; no extra operational source or historical readiness table. |
| data/processed/dashboard/ | Original and separate process/scenario bundles; [export dictionary](export_dictionary.md) specifies seven CSV grains and report/reference uses. |

Dates are ISO strings in CSV/SQLite and become Date in the supplied M queries. Flags/counts become Whole Number, ratios Decimal Number. Positive-demand and unique-key constraints apply to approved source data. Zero-demand/duplicate/zero-holder fixtures do not broaden that source contract. The [focused checks](day11_boundary_checks.md) make these distinctions executable.
