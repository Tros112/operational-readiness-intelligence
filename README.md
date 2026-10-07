# Operational Readiness Intelligence

**Status: Day 2 clean generator completed on October 7, 2026, ahead of its October 8 schedule.** Six synthetic CSV tables are generated and eight clean-reference checks pass. Dirty-input validation, persistent database loading, analytical SQL/marts, and the operational Power BI report remain scheduled work. No PBIX has been created or inspected by the assistant.

Windows access is confirmed by the user: Desktop **2.158.1177.0, 64-bit (September 2026)**; blank report opens, saves, and reopens; no blocker reported. Evidence: `docs/powerbi_access.json`. This establishes local setup access only.

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
python -m unittest discover -s tests -v
```

The environment checker prints JSON and executes the schema in an empty in-memory database. The generator creates `data/raw/clean/` with six CSVs and a deterministic manifest. Tests verify the clean reference, including a separate populated memory-only schema probe and two independent generator runs. No persistent project database is created. Generated CSVs are excluded from Git and can be regenerated; the Day 2 download package includes them.

Future pipeline scripts (`validate_data.py`, `load_data.py`, `export_marts.py`) and `sql/analytics.sql` will be created on their scheduled days. The generator does not yet complete the end-to-end pipeline.

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
| `tests/test_generate_data.py` | Eight clean-reference integration/reproducibility checks |
| `sql/schema.sql` | Executable SQLite schema scaffold; loader pending Day 4 |
| `data/raw/`, `data/processed/`, `data/rejected/` | Reserved for generated input, accepted/output data, and rejection evidence |
| `tests/` | Reserved for meaningful data and metric checks as those implementations exist |
| `powerbi/build_instructions.md` | Completed Windows access check and report handoff for Day 6 |
| `docs/metric_contract.md` | Finalized v1.0 definitions, output grains, boundaries, and worked examples |
| `docs/schema_sketch.md`, `docs/data_dictionary.md` | Grain, joins, keys, and field meanings |
| `docs/environment.md`, `docs/verification_day01.md` | Observed access and verified limits |
| `docs/progress.md`, `docs/decisions.md`, `docs/interview_feedback.md` | Daily state, decisions, and actual employer feedback |

## Limits and ownership

Staffing and qualification coverage are separate measures. A person can hold multiple qualifications, so qualification coverage cannot establish simultaneous assignment capacity. The no-renewal outlook will be a deterministic scenario. No ML, cloud, dbt, optimization, or extra project is included in this MVP.

The assistant prepares code, SQL, documentation, and build instructions. The user reviews and explains the work, builds/inspects the Power BI report locally, and supplies access results and employer feedback. Independent understanding is checked explicitly; it is not assumed from coursework or generated documentation.
