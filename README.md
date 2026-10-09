# Operational Readiness Intelligence

**Status: Day 3 validation implemented October 8, 2026, ahead of its October 9 schedule.** Six synthetic source tables have separate clean/dirty inputs and visible validation/rejection evidence. All 22 tests pass on Linux. Clean input passes (1,227 accepted / 0 rejected); all 16 injected defects are detected and dirty input is blocked (1,229 = 1,210 accepted + 19 rejected). Windows Day 3 reproduction remains pending. Persistent database loading, analytical SQL/marts, and the production operational Power BI report remain scheduled work. No PBIX has been created or inspected by the assistant.

Windows access is confirmed by the user: Desktop **2.158.1177.0, 64-bit (September 2026)**. Day 2 staffing screenshots show matching global/Unit C slicer results and the intended relationship; populated-report save/reopen is user-confirmed. Evidence: `docs/verification_day02.md`. Full SQL/Power BI reconciliation remains pending.

This portfolio project supports a fictional operations manager deciding where to review staffing, qualification renewals, backup coverage, and administrative processes. All operational data and findings will be **simulated**. Readiness measures are fictional proxies; they are not official Navy rules or statements about deployability.

The project demonstrates Python, relational SQL, data quality, and Power BI explanation for analyst/BI interviews. It does not establish production implementation experience or real-world predictive validity.

## Current scope and gates

- Six fictional units, 300 fictional people, eight qualification types.
- A single staffing snapshot fixed at **2026-10-07**; 90-day qualification outlook and 90-day administrative case window.
- Python → validation → SQLite → SQL-generated CSV → Power BI Desktop on Windows.
- Visible prototype: October 13. Interview-ready MVP: Monday, October 19. Polished flagship: October 30.
- HoH interview window: October 20–December 3. These dates and HoH events are supplied planning inputs, not independently verified event schedules.

The brainstorming chat remains the master record for priorities and major scope changes. This workspace uses decisions/checkpoints that the user brings between chats; it does not assume access to that chat.

## Start or resume

Read [charter](docs/charter.md), [progress](docs/progress.md), and [decisions](docs/decisions.md) before making changes. The attached schedule is preserved in [source_execution_plan.md](docs/source_execution_plan.md).

Use Python 3.11 or later from the project root:

```bash
python -m pip install -r requirements.txt
python src/check_environment.py
python src/generate_data.py
python src/inject_defects.py
python src/validate_data.py
python src/validate_data.py --input-dir data/raw/dirty --output-dir data/rejected/day03_dirty
python -m unittest discover -s tests -v
```

The environment checker executes the schema in an empty in-memory database. The generator creates `data/raw/clean/`; the injector writes `data/raw/dirty/` separately. Clean validation exits 0; the intentional dirty validation exits **1**, blocks loading, and records raw rejected cells/reasons. Tests use memory-only schema probes; no persistent project database is created. Generated datasets/validation exports are excluded from Git and included in the Day 3 package. Windows steps: [day03_windows_handoff.md](docs/day03_windows_handoff.md).

Future scripts (`load_data.py`, `export_marts.py`) and `sql/analytics.sql` will be created at their milestones. Loading must require a passed validation report and matching accepted-file hashes. Accepted rows in a failed diagnostic bundle are not approved readiness inputs. The end-to-end pipeline is not complete.

## Clean reference and planted evidence

All counts here are **simulated source audits**. CSV rows: 6 units, 300 people, 8 qualification types, 265 certificates, 48 unit/qualification requirements, 600 cases.

- Unit C: 40 available / 50 required (80%); a deliberately planted staffing shortfall.
- Unit B/Q03: one valid available holder for one required; deliberately fragile coverage.
- Unit D/Q04: six available holders all expiring within 30 days; an explicit no-renewal scenario leaves no holders at day 30.
- Unit F: 27 corrections / 70 completed cases (38.6%), from a configured 30% probability; elsewhere 18/372 (4.8%) from 6%. The rates were not forced to match the probabilities.

Verification: [verification_day02.md](docs/verification_day02.md). Field meanings: [data_dictionary.md](docs/data_dictionary.md). Code explanation and ownership checks: [generator_walkthrough.md](docs/generator_walkthrough.md). These audits are not real-world findings or completed SQL/Power BI reconciliation.

## Where the work lives

| Path | Current purpose |
| --- | --- |
| `config/project.yml` | Fixed seed, date, scope, and explicitly planted fictional scenarios |
| `src/check_environment.py` | Implemented Day 1 access/configuration/schema check |
| `src/generate_data.py` | Implemented fixed-seed clean generator with four explicit scenario overrides |
| `src/inject_defects.py` | Sixteen deterministic defects in a separate source copy; exact catalog and hashes |
| `src/validate_data.py` | Key/required/FK/date/type/lifecycle/completeness validation; explicit quarantine and whole-batch gate |
| `tests/test_generate_data.py` | Eight clean-reference integration/reproducibility checks |
| `tests/test_validate_data.py` | Fourteen quality, reconciliation, preservation, and failure checks |
| `sql/schema.sql` | Executable SQLite schema scaffold; loader pending Day 4 |
| `data/raw/`, `data/processed/`, `data/rejected/` | Clean/dirty inputs, passed clean records, and blocked dirty diagnostics |
| `tests/` | Reserved for meaningful data and metric checks as those implementations exist |
| `powerbi/build_instructions.md` | Completed Windows access check and report handoff for Day 6 |
| `docs/metric_contract.md` | Finalized v1.0 definitions, output grains, boundaries, and worked examples |
| `docs/schema_sketch.md`, `docs/data_dictionary.md` | Grain, joins, keys, and field meanings |
| `docs/environment.md`, `docs/verification_day01.md` | Observed access and verified limits |
| `docs/validation_rules.md`, `docs/defect_catalog.md`, `docs/verification_day03.md` | Rejection contract, injected errors, verified counts and limits |
| `docs/progress.md`, `docs/decisions.md`, `docs/interview_feedback.md` | Daily state, decisions, and actual employer feedback |

## Limits and ownership

Staffing and qualification coverage are separate measures. A person can hold multiple qualifications, so qualification coverage cannot establish simultaneous assignment capacity. The no-renewal outlook will be a deterministic scenario. No ML, cloud, dbt, optimization, or extra project is included in this MVP.

The assistant prepares code, SQL, documentation, and build instructions. The user reviews and explains the work, builds/inspects the Power BI report locally, and supplies access results and employer feedback. Independent understanding is checked explicitly; it is not assumed from coursework or generated documentation.
