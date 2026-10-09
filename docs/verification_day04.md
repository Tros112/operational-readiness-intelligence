# Day 4 verification

Executed October 9, 2026, America/Los_Angeles, ahead of the October 10 schedule under the user's instruction to continue in the existing Git-connected project. Actual user-focused hours remain unreported; provisional capacity remains two-hour weekdays and three-to-four-hour weekends. Metric date remains October 7. All records/findings are simulated; readiness is a fictional proxy.

## Persistent load and repeat

Both Linux CLI loads exited **0** and produced the same exact records and logical data hash:

`fc5ee84198bee07dcc0e90bcf4fcf1f242fd640eb08116ff3bdc6f55b8bf8a66`

| Source table | Accepted input | First database load | Second database load |
| --- | ---: | ---: | ---: |
| units | 6 | 6 | 6 |
| personnel | 300 | 300 | 300 |
| qualification_types | 8 | 8 | 8 |
| personnel_qualifications | 265 | 265 | 265 |
| unit_qualification_requirements | 48 | 48 | 48 |
| admin_cases | 600 | 600 | 600 |
| Total | **1,227** | **1,227** | **1,227** |

Foreign keys were enabled for each loader connection before its transaction. Both loads pass foreign_key_check and integrity_check and compare every stored value with typed accepted input. SQL preserves **158 open cases with NULL outcomes**, **397 known zero correction outcomes**, **49 expired certificates**, and **23 future-start certificates**. These storage checks do not apply readiness eligibility or perform Day 5 analytics.

Persistent artifacts: `data/processed/readiness.sqlite3`, `data/processed/load_report.json`, `data/processed/load_report_second.json`. Generated databases and audits stay local and are excluded from Git. Machine evidence: `docs/load_check.json`.

## Failure and preservation evidence

The dirty bundle load exits **1**, status blocked, database_updated false. `data/processed/load_report_dirty.json` records the rejection. The existing database's SHA256 is identical before and after this blocked CLI attempt. All six original clean CSVs and the generation manifest retain their pre-session SHA256 values.

**32 tests pass on Linux**: the prior eight generator and fourteen validator checks, plus ten loader checks. The loader checks cover exact persisted records/counts/nulls/inactive certificates; repeat identity; blocked dirty input before a new database is created or a good one touched; source/export mutation; a rehashed export still differing from its source; unfinished/wrong-date/bad-count/invalid metadata; a real SQLite PK failure after deletes and partial inserts with full rollback; PK/FK/flag constraints; preservation of unrelated databases and simulated `.git`/`.venv`/PBIX assets; and failed CLI reruns invalidating old success audits. A source-side JSON output path is also refused before overwrite. Latest suite after checkpoint inspection: **32 tests in 4.010 seconds, OK**, Python 3.12.14 / SQLite 3.53.1 / PyYAML 6.0.3. No implementation was rebuilt or clean input regenerated.

The resumed check opened the saved database read-only and reconfirmed all six counts, foreign-key integrity, and SQLite integrity. Its physical SHA256 still matches the saved pre-dirty-attempt baseline, `16d3119d57fd7ba6195fa372b9f970819a6397010162cab11119c2ce7014fe46`. The original source hashes and both saved successful load audits remain consistent. This inspection confirms the saved checkpoint rather than claiming a new CLI load.

The output-protection asset checks use temporary fixtures. This Linux checkout has no .venv or PBIX/PBIT; the assistant has not inspected or operated the user's actual Windows assets. The authorized Git update contains only code, tests, and text documentation, with no images, generated datasets/databases, .venv, PBIX, or PBIT path. Existing Git history is retained. Windows Day 4 execution, actual local report availability, and independent transaction explanation remain pending in `docs/day04_windows_handoff.md`.

## Scope and next action

No dependencies, generator rules, metric definitions, analysis date, six-table source scope, or release dates changed. `.gitignore` excludes local PBIX/PBIT files at any folder depth. SQL changes are the source-table scaffold comment; the loader uses the existing constraints. No analytical marts, extra datasets, ML, cloud, dbt, or report styling were added. No assistant PBIX creation/open/verification is claimed.

Delivery is authorized but remains pending verification of the published commit. After the assistant provides that verified SHA, pull the update into the existing Windows Git folder and run `docs/day04_windows_handoff.md`. Next implementation milestone, when requested: Day 5 staffing, qualification coverage/gap/fragility/expiration SQL with a hand check, zero-holder preservation, distinct-holder counting, and explicit export grains. The next master-chat release gate remains October 13; no prototype/MVP gate passes from this database alone.
