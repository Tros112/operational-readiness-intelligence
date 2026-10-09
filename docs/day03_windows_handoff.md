# Day 3 Windows reproduction

The assistant verified Day 3 on Linux. On October 9, Windows screenshots confirmed both validation reports and the target rejections, and you reported 22 tests, OK after clearing the terminal. Core Day 3 reproduction and the duplicate-authority ownership check are complete with that evidence distinction. Power BI's populated staffing report was already saved/reopened by you; this handoff covers Python validation.

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

Open `data/rejected/day03_dirty/rejected_rows.csv`, its `validation_report.json`, and `data/raw/dirty/defect_manifest.json`. All these records and defects are synthetic. Match the following **table plus source record number**, rather than the line number in the rejection export:

| Defect | Source table | Source record number | Key | Expected rejection |
| --- | --- | --- | --- | --- |
| D01 | personnel_qualifications | 2 and 267 | P0003 / Q04 | DUPLICATE_KEY on both records |
| D07 | personnel | 8 | P0007 | FOREIGN_KEY: unit UX99 does not exist |
| D07 dependent record | personnel_qualifications | 9 | P0007 / Q07 | REJECTED_PARENT: its personnel record failed validation |

The source header is record 1. For example, certificate source record 2 appears on a different line in `rejected_rows.csv`; a personnel record numbered 2 is a separate record in a separate table.

D01 is an **identical** duplicate: both certificates have valid_from `2026-02-08` and expiration_date `2026-10-25`. The current policy rejects all versions of a duplicate key, including identical copies. Do not describe this fixture as two conflicting expiration dates. Conflicting dates are covered separately by a validator test.

For a readable view, run this in PowerShell from the working project root (the folder containing `src` and `config`):

```powershell
$oriRejected = Import-Csv .\data\rejected\day03_dirty\rejected_rows.csv

$oriRejected |
    Where-Object {
        $_.table -eq 'personnel_qualifications' -and
        $_.record_number -in @('2', '267')
    } |
    Format-Table table, record_number, key_json, reason_codes -AutoSize

$oriRejected |
    Where-Object {
        ($_.table -eq 'personnel' -and $_.record_number -eq '8') -or
        ($_.table -eq 'personnel_qualifications' -and $_.record_number -eq '9')
    } |
    Format-Table table, record_number, key_json, reason_codes -AutoSize
```

The dirty report's `MISSING_REQUIREMENT_PAIRS` error for U01/Q01, U01/Q02, and U01/Q03 is expected: D13-D15 invalidated those requirement records. The validator blocks the batch so those missing requirements cannot silently shrink a coverage denominator.

Read the two report summaries:

```powershell
$oriClean = Get-Content .\data\processed\validation_clean\validation_report.json -Raw | ConvertFrom-Json
$oriDirty = Get-Content .\data\rejected\day03_dirty\validation_report.json -Raw | ConvertFrom-Json

$oriClean | Select-Object status, load_allowed, exit_code, input_directory
$oriClean.totals
$oriDirty | Select-Object status, load_allowed, exit_code, input_directory
$oriDirty.totals
```

Return those summaries plus the terminal's existing **22 tests, OK** result and the command exit codes from action 3. The report input directories should identify your Windows project; an untouched packaged Linux report does not establish a Windows run. If a command has not been run locally, run just that missing command from action 3. Do not repeat successful tests solely to inspect these files.

Then answer in your own words: **If duplicate certificate records disagreed on expiration date, why would keeping the first record be insufficient evidence for choosing the trustworthy date?** The supplied fixture and this guide do not establish your independent explanation; that remains pending until you answer.

The October 8, 23:44 PDT screenshot confirms that you opened the rejection export, D01 manifest entry, and a dirty report containing a Windows input directory, expected missing pairs, and exit code 1. Totals, load_allowed, the clean report, and the test summary are outside the visible area; full Windows reproduction remains pending.

### Completion update — October 9

The later screenshots confirm D01's two DUPLICATE_KEY records, D07's FOREIGN_KEY personnel record and REJECTED_PARENT certificate, clean 1,227/1,227/0 with load_allowed true and report exit 0, and dirty 1,229/1,210/19 with load_allowed false and report exit 1. Both reports show reconciled counts and Windows input-directory prefixes.

You also reported **22 tests, OK** after clearing the terminal result. This is accepted as user-reported test evidence; the assistant has not inspected its raw output, execution duration, interpreter, or test-command exit code. Successful tests do not need to be repeated to restore the cleared display.

The duplicate-authority explanation has been supplied independently, with a clarification recorded in `docs/validator_walkthrough.md`. Action 4's core checks are complete. Other ownership prompts remain practice items. No infrastructure blocker is reported. Next implementation milestone: Day 4's atomic, repeatable SQLite load when requested; do not rerun setup or successful validation solely to close this checklist.

If an actual command fails differently, return its exact text before editing clean records or quality rules. Next implementation milestone is Day 4's atomic, repeatable SQLite load; it is not implemented in this package.
