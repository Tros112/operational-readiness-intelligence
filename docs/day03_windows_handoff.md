# Day 3 Windows reproduction

The assistant verified Day 3 on Linux. Your Windows Day 3 run remains pending. Power BI's populated staffing report was already saved/reopened by you; this session's local task is Python validation.

## 1. Extract and select the project

Download `Operational_Readiness_Intelligence_Day03.zip`. Use File Explorer **Extract All** into:

`C:\Users\dolai\OneDrive\Documents\Data Science 2027\Projects\Operational Readiness Intelligence OPI\Day 3`

The ZIP contains the `operational_readiness_intelligence` folder. Open PowerShell and run:

```powershell
Set-Location -LiteralPath 'C:\Users\dolai\OneDrive\Documents\Data Science 2027\Projects\Operational Readiness Intelligence OPI\Day 3\operational_readiness_intelligence'
Get-Location
Test-Path .\src\validate_data.py
```

Expected path check: **True**. The folder containing `README.md`, `src`, and `config` is the project root. If you extract elsewhere, change only the quoted path. Use the same project folder in VS Code; select its `.venv` after creating it.

## 2. Create the project environment

Your earlier Windows Python 3.11.4 is supported. From that project root:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The explicit environment executable ensures the commands use the installed project dependencies. Python 3.11 or later is required. If this extracted project already has a working environment, use its executable.

## 3. Run the milestone

```powershell
.\.venv\Scripts\python.exe src\inject_defects.py
$LASTEXITCODE

.\.venv\Scripts\python.exe src\validate_data.py
$LASTEXITCODE

.\.venv\Scripts\python.exe src\validate_data.py --input-dir data\raw\dirty --output-dir data\rejected\day03_dirty
$LASTEXITCODE

.\.venv\Scripts\python.exe -m unittest discover -s tests -v
$LASTEXITCODE
```

| Command | Expected result |
| --- | --- |
| Injector | 16 defects; personnel 301, certificates 266, other source counts unchanged; exit 0 |
| Clean validator | passed; load_allowed true; 1,227 input = 1,227 accepted + 0 rejected; exit 0 |
| Dirty validator | validation_failed; load_allowed false; 1,229 input = 1,210 accepted + 19 rejected; exit **1 intentionally** |
| Tests | **22 tests, OK**; exit 0 |

The dirty exit 1 is the expected quality-control behavior. Its accepted CSVs are diagnostics inside a blocked bundle. Do not use them for the staffing report or upcoming database load.

## 4. Inspect and return evidence

Open `data/rejected/day03_dirty/rejected_rows.csv` and `validation_report.json`. Find D01's two certificate records using `data/raw/dirty/defect_manifest.json`; both have `DUPLICATE_KEY`. Find D07's person with `FOREIGN_KEY` and its certificate with `REJECTED_PARENT`.

Return the clean/dirty totals and exit codes plus the test summary. Then explain in your own words why keeping the first duplicate certificate record would be an unsupported choice. This confirms local reproduction and helps establish interview ownership; those are not assumed from the assistant's test run.

If an actual command fails differently, return its exact text before editing clean records or quality rules. Next implementation milestone is Day 4's atomic, repeatable SQLite load; it is not implemented in this package.
