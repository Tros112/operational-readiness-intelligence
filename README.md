# Operational Readiness Intelligence

**Status: Day 1 foundation, October 7, 2026.** The charter, metric outline, configuration, and six-table SQL scaffold exist. Data generation, validation, database loading, analytical SQL, and the Power BI report are scheduled work and have not been implemented. No PBIX has been created or inspected by the assistant.

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

For the Day 1 check, use Python 3.11 or later from the project root:

```bash
python -m pip install -r requirements.txt
python src/check_environment.py
```

The checker prints JSON, reads the configuration, and executes the six-table schema in an **empty in-memory database**. It does not generate operational data or create a populated project database. The current workspace's installed Python dependencies already suffice for this check.

Future pipeline scripts (`generate_data.py`, `validate_data.py`, `load_data.py`, `export_marts.py`) and `sql/analytics.sql` will be created on their scheduled days. Do not infer that the pipeline runs from the presence of these directories.

## Where the work lives

| Path | Current purpose |
| --- | --- |
| `config/project.yml` | Fixed seed, date, scope, and explicitly planted fictional scenarios |
| `src/check_environment.py` | Implemented Day 1 access/configuration/schema check |
| `sql/schema.sql` | Executable SQLite schema scaffold; loader pending Day 4 |
| `data/raw/`, `data/processed/`, `data/rejected/` | Reserved for generated input, accepted/output data, and rejection evidence |
| `tests/` | Reserved for meaningful data and metric checks as those implementations exist |
| `powerbi/build_instructions.md` | Completed Windows access check and report handoff for Day 6 |
| `docs/metric_contract.md` | Metric outline, boundaries, and worked examples |
| `docs/schema_sketch.md`, `docs/data_dictionary.md` | Grain, joins, keys, and field meanings |
| `docs/environment.md`, `docs/verification_day01.md` | Observed access and verified limits |
| `docs/progress.md`, `docs/decisions.md`, `docs/interview_feedback.md` | Daily state, decisions, and actual employer feedback |

## Limits and ownership

Staffing and qualification coverage are separate measures. A person can hold multiple qualifications, so qualification coverage cannot establish simultaneous assignment capacity. The no-renewal outlook will be a deterministic scenario. No ML, cloud, dbt, optimization, or extra project is included in this MVP.

The assistant prepares code, SQL, documentation, and build instructions. The user reviews and explains the work, builds/inspects the Power BI report locally, and supplies access results and employer feedback. Independent understanding is checked explicitly; it is not assumed from coursework or generated documentation.
