# Day 4 — update and run in the existing Windows project

Day 4 was implemented October 9, 2026, ahead of its October 10 schedule under the user's instruction to continue. All operational data and findings are simulated; readiness is a fictional proxy. The assistant's Linux checks pass. Your Windows Day 4 run and independent transaction explanation remain pending.

Delivery gate: publication is pending in this draft. Start the update commands only after the assistant supplies the verified published commit SHA. An earlier successful push of Day 3 does not establish that Day 4 is available remotely.

## 1. Update the folder you already use

Open PowerShell in your existing Git-connected project root, containing `.git`, `src`, and `config`. Keep this same folder for later milestones. The last observed Day 3 working directory was under your OneDrive project; use your current Git folder if it has since been renamed.

```powershell
git rev-parse --show-toplevel
git status --short --branch
git remote get-url origin
git branch --show-current
```

Expected: your existing folder, branch `main`, and origin `https://github.com/Tros112/operational-readiness-intelligence.git`. Review any tracked local edits before updating. If these checks differ, return the output before running the update.

```powershell
git pull --ff-only origin main
if ($LASTEXITCODE -ne 0) { throw 'Git update stopped. Return the exact output; keep your local changes.' }
git rev-parse HEAD

Test-Path .\src\load_data.py
Test-Path .\.venv\Scripts\python.exe
git status --short --branch
```

Compare HEAD with the published SHA provided for this update; a later verified descendant can also contain the milestone. Both path checks should be **True**. The update contains code, SQL, and text documentation only; images, generated data/databases, `.venv`, and PBIX/PBIT are excluded. Git keeps the existing `.git` history and local ignored files. Your `.venv` is reused; no new dependency or environment recreation is required. Keep your local Power BI report where it already lives. Do not extract a complete project archive over this folder or use reset/clean commands to obtain the update. If Git reports a conflict or local edits, stop and return its exact output.

## 2. Validate, load, and prove the repeat

Your existing clean sources remain local. Rerun clean validation so the report records the current Windows path and current source/export hashes:

```powershell
.\.venv\Scripts\python.exe src\validate_data.py
if ($LASTEXITCODE -ne 0) { throw 'Clean validation did not pass. Return the output before loading.' }

.\.venv\Scripts\python.exe src\load_data.py
if ($LASTEXITCODE -ne 0) { throw 'First load did not pass. Return the output.' }
$oriFirstLoad = Get-Content .\data\processed\load_report.json -Raw | ConvertFrom-Json

.\.venv\Scripts\python.exe src\load_data.py
if ($LASTEXITCODE -ne 0) { throw 'Second load did not pass. Return the output.' }
$oriSecondLoad = Get-Content .\data\processed\load_report.json -Raw | ConvertFrom-Json

$oriSecondLoad.database_counts | Format-List
$oriFirstLoad.logical_data_sha256 -eq $oriSecondLoad.logical_data_sha256
```

Expected on both loads: status **loaded**, exit **0**, total **1,227**, counts_reconciled **true**, foreign_key_check **passed**, integrity_check **ok**. Digest comparison: **True**.

| Table | Expected rows |
| --- | ---: |
| units | 6 |
| personnel | 300 |
| qualification_types | 8 |
| personnel_qualifications | 265 |
| unit_qualification_requirements | 48 |
| admin_cases | 600 |
| Total | **1,227** |

The database is `data/processed/readiness.sqlite3`. The audit is `data/processed/load_report.json`. These generated local artifacts are excluded from Git. If clean CSVs are actually missing, run the existing generator once, then repeat validation; do not regenerate a working reference just to update code.

## 3. Verify the dirty guard and tests

Use a separate audit path for the intentional failure:

```powershell
$oriDbBefore = (Get-FileHash .\data\processed\readiness.sqlite3 -Algorithm SHA256).Hash
.\.venv\Scripts\python.exe src\load_data.py --bundle-dir data\rejected\day03_dirty --report-path data\processed\load_report_dirty.json
$LASTEXITCODE
$oriDbBefore -eq (Get-FileHash .\data\processed\readiness.sqlite3 -Algorithm SHA256).Hash

.\.venv\Scripts\python.exe -m unittest discover -s tests -v
$LASTEXITCODE
```

Expected dirty result: **blocked**, database_updated **false**, exit **1 intentionally**, and unchanged database-hash comparison **True**. Expected suite: **32 tests, OK**, exit **0**. If the existing dirty validation bundle is missing, reproduce it with the injector and dirty-validator commands in the Day 3 handoff first; do not change the clean sources.

## 4. Return the completion evidence

Return the six database counts, the repeat-digest comparison, dirty-load exit/hash comparison, and the 32-test result. Open your existing Power BI report and confirm that it remains available; no report rebuild or new PBIX is part of Day 4.

Then explain independently: **Why should deleting the old snapshot and inserting all six tables happen inside one transaction, rather than committing after each table?** Read `docs/loader_walkthrough.md` beside `src/load_data.py` to prepare. A supplied walkthrough is guidance, not confirmation that you can explain it independently.

Completion closes Day 4's Windows check. The next implementation milestone is Day 5 analytical SQL and CSV exports; do not import new Power BI tables or begin styling during this loader check.
