# Environment inventory

Observed October 7, 2026 in the assistant's execution workspace. Machine-readable evidence: `docs/environment_inventory.json`.

| Component | Observation | Working decision |
| --- | --- | --- |
| Operating system | Linux, x86_64 | Build Python/SQL here; Desktop on user's Windows computer |
| Python | 3.12.14 | Available; project requires 3.11+ |
| pandas / NumPy | 2.2.3 / 2.3.5 installed | Used by Day 2 tables/CSV and seeded generation; pinned in requirements |
| PyYAML | 6.0.3 installed | Used by configuration checker and generator; pinned in requirements |
| SQLite | Python sqlite3, engine 3.53.1; no CLI | Available; CLI unnecessary. STRICT schema requires SQLite 3.37+ |
| Git | 2.51.1 installed | Local checkpoint; no intended remote supplied |
| PostgreSQL | No psql/postgres/pg_ctl/pg_isready executable; localhost:5432 closed; no configured connection keys | Use charter-approved SQLite plus SQL-generated CSV fallback immediately; no installation session spent |
| PostgreSQL Python drivers | psycopg / psycopg2 not installed | Not needed for SQLite; migration deferred |
| pytest | Not installed | No test-runner installation needed for Day 1; use standard library checks |
| Power BI Desktop | Unavailable in Linux; user reports Windows Desktop 2.158.1177.0, 64-bit (September 2026), blank report opens/saves/reopens, no blocker | Local access confirmed by user on October 7; operational report build remains scheduled |

No project instructions or implementation existed at session start; only the supplied plan was present. No `AGENTS.md` was found in the workspace or its ancestor directories. Project instructions now live in the project root.

## Recheck

From the project folder:

```bash
python src/check_environment.py
```

To refresh the saved inventory intentionally:

```bash
python src/check_environment.py > docs/environment_inventory.json
```

The checker reports connection-key presence only; it never prints connection strings, usernames, or passwords. It creates the schema in memory and does not produce operational data or a populated database. PostgreSQL port reachability would not prove authentication even if present.

Windows confirmation is recorded in `docs/powerbi_access.json`, from the user's October 7, 14:16 America/Los_Angeles message. The checker reads this record so future inventory refreshes preserve the reported access status. This is user-reported evidence; the assistant has not opened or inspected a PBIX. No installation or further access check is required now.

## User Windows Python check — October 7, 16:02 America/Los_Angeles

Evidence: user-supplied terminal screenshots. These observations are separate from the assistant-machine inventory above and do not replace `docs/environment_inventory.json`.

- Python reports **3.11.4**, meeting the project's Python 3.11+ requirement.
- The extracted project is in the user's OneDrive **Day 2** folder; `Test-Path .\src\generate_data.py` returns `True`.
- `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` completes with **8 tests in 2.230s, OK**. No local test-run blocker is visible.
- Windows package versions and the SQLite engine version were not separately reported. No Power BI report or PBIX inspection is implied by the Python result.

## VS Code follow-up — October 7, 16:28 America/Los_Angeles

The user initially opened an individual test file with VS Code's global Python selected; the 16:18 screenshot shows `ModuleNotFoundError: No module named 'pandas'`. The existing project `.venv` had already passed all eight tests. The 16:28 screenshots confirm the Day 2 folder open as the workspace, **Python 3.11.4 (.venv)** selected, and successful standalone generation of all six synthetic tables. The active generator file shows zero error/warning indicators. The observed editor interpreter issue is resolved; generation code and dependencies are unchanged.

For this Windows workspace, open the Day 2 project folder and use **Python: Select Interpreter** to select `.venv/Scripts/python.exe`. The run command should use that executable. This project environment selection is separate from the system-wide `python` command. The terminal screenshots provide runtime evidence; the assistant did not operate VS Code on the user's computer.
