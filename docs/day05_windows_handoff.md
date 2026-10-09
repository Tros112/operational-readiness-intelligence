# Day 5 — verify SQL exports in your existing Windows project

Day 5 implementation is verified on Linux on October 9, 2026, ahead of its October 11 schedule. **Windows Day 5 reproduction and your SQL explanation remain pending.** All operational results are simulated; readiness is a fictional proxy. Your Day 4 Windows checks and report availability are already confirmed. Reuse that same Git folder and `.venv`; no setup, regeneration, reload, or new dependency is required for a working Day 4 snapshot.

The assistant's delivery message supplies the verified Day 5 commit SHA. This guide becomes actionable after publication verification. Local CSVs are created by the exporter, not included in the Git update. Your existing Power BI report stays in place; no new import or report build is part of this check.

## 1. Update the same checkout

Open PowerShell in the existing project root you used for Day 4. Its folder name may still be `Day 3`; keep using it. Check:

```powershell
git rev-parse --show-toplevel
git status --short --branch
git remote get-url origin
git branch --show-current
```

Expected branch `main`, origin `https://github.com/Tros112/operational-readiness-intelligence.git`. Review tracked local edits before pulling. The previously observed untracked root `progress.md` is your local file; keep it. If Git reports conflicting changes or an unexpected checkout, return the exact output before updating.

```powershell
git pull --ff-only origin main
if ($LASTEXITCODE -ne 0) { throw 'Git update stopped. Keep local files and return the exact output.' }
git rev-parse HEAD
Test-Path .\src\export_metrics.py
Test-Path .\.venv\Scripts\python.exe
```

Compare HEAD with the delivery SHA; both path checks should be True. This update contains code, SQL, tests, and text documentation. `.git`, `.venv`, generated datasets/databases, local images, and Power BI binaries are preserved. Do not overlay a project archive or run reset/clean commands.

## 2. Export from the saved Day 4 database

```powershell
$oriDbBefore = (Get-FileHash .\data\processed\readiness.sqlite3 -Algorithm SHA256).Hash

.\.venv\Scripts\python.exe src\export_metrics.py
$oriExportExit = $LASTEXITCODE
if ($oriExportExit -ne 0) { throw 'Export did not pass. Return its output; do not refresh Power BI.' }
$oriFirstExport = Get-Content .\data\processed\dashboard\export_manifest.json -Raw | ConvertFrom-Json
$oriFirstExport | Select-Object status, exit_code, exports_ready, as_of_date, database_matches_passed_source, cross_query_reconciliation
$oriFirstExport.files.PSObject.Properties | ForEach-Object {
    [PSCustomObject]@{File=$_.Name; Rows=$_.Value.rows; SHA256=$_.Value.sha256}
} | Format-Table -AutoSize
$oriFirstExport.global_components | Format-List
```

Expected process exit 0, `status = passed`, `exports_ready = true`, `as_of_date = 2026-10-07`, database match true, and cross-query reconciliation passed.

| Generated file under `data/processed/dashboard/` | Rows |
| --- | ---: |
| `unit_summary.csv` | 6 |
| `qualification_detail.csv` | 48 |
| `expiration_detail.csv` | 193 |

Global components: available **254**, required **250**, staffing gap **10**, staffing ratio **1.016**; capped qualification slots **88**, required slots **95**, qualification gap **7**, ratio approximately **0.9263157895**. Ratios become 101.6% and 92.63% when formatted as percentages.

If blocked because source/validation/database contents differ, return the exact error. Do not manually edit the report/hash or skip the gate. The exporter explains which preflight failed. A missing source, moved validation path, or stale approved bundle may require the existing validate/load steps after diagnosis; a correct saved snapshot needs neither.

## 3. Prove the repeat and preserve the database

```powershell
.\.venv\Scripts\python.exe src\export_metrics.py
if ($LASTEXITCODE -ne 0) { throw 'Repeat export did not pass. Return the output.' }
$oriSecondExport = Get-Content .\data\processed\dashboard\export_manifest.json -Raw | ConvertFrom-Json
$oriCsvNames = 'unit_summary.csv', 'qualification_detail.csv', 'expiration_detail.csv'
$oriRepeatMatches = foreach ($oriCsvName in $oriCsvNames) {
    $oriFirstExport.files.PSObject.Properties[$oriCsvName].Value.sha256 -eq $oriSecondExport.files.PSObject.Properties[$oriCsvName].Value.sha256
}
$oriRepeatOk = @($oriRepeatMatches | Where-Object { $_ -eq $false }).Count -eq 0
$oriRepeatOk
$oriDbBefore -eq (Get-FileHash .\data\processed\readiness.sqlite3 -Algorithm SHA256).Hash

$oriFileMatches = foreach ($oriCsvName in $oriCsvNames) {
    $oriActualHash = (Get-FileHash (Join-Path .\data\processed\dashboard $oriCsvName) -Algorithm SHA256).Hash
    $oriActualHash -eq $oriSecondExport.files.PSObject.Properties[$oriCsvName].Value.sha256
}
@($oriFileMatches | Where-Object { $_ -eq $false }).Count -eq 0
```

Expected **True / True / True**: repeat CSV hashes, unchanged local database hash, and actual files matching the manifest. Do not compare the Windows database's physical SHA to Linux's; compare your own before/after hash. The logical data digest is expected to match `fc5ee84198bee07dcc0e90bcf4fcf1f242fd640eb08116ff3bdc6f55b8bf8a66`.

The three CSV replacements are not one filesystem transaction. Only use a passed manifest with `exports_ready = true`, the expected date, and matching file hashes. If a run fails, leave Power BI unrefreshed and rerun successfully after resolving it. Old CSVs alone are not proof of a successful current export.

## 4. Inspect Unit C and run the suite

```powershell
Import-Csv .\data\processed\dashboard\unit_summary.csv |
    Where-Object unit_id -eq 'U03' |
    Select-Object unit_name, available_personnel_count, required_personnel_count, staffing_gap, staffing_coverage_ratio, capped_holder_slots, required_holder_slots, qualification_gap, qualification_coverage_ratio |
    Format-List

Import-Csv .\data\processed\dashboard\qualification_detail.csv |
    Where-Object unit_id -eq 'U03' |
    Select-Object qualification_id, valid_available_holder_count, required_holder_count, capped_holder_count, current_gap, is_fragile |
    Format-Table -AutoSize

.\.venv\Scripts\python.exe -m unittest discover -s tests -v
$oriTestExit = $LASTEXITCODE
$oriTestExit
if ($oriTestExit -ne 0) { throw 'Tests did not pass. Return the exact failing output.' }
```

Expected Unit C: staffing **40/50**, ratio **0.8**, gap **10**; qualification slots **15/16**, ratio **0.9375**, gap **1**. Q06 has one valid available holder against two required, gap one, fragile flag zero. The whole suite should end **42 tests, OK**, process exit **0**. This includes the ten new analytical/export tests; it does not rebuild your Power BI report.

## 5. Return the Day 5 completion evidence

Paste the following as text; no screenshot upload is needed:

```text
HEAD:
Export status / exports_ready / as_of_date:
Rows — units / qualification pairs / valid certificates:
Repeat CSV hashes / database preserved / manifest hashes match:
Unit C — staffing counts/gap and qualification counts/gap:
Tests / process exit:
Blocker, if any:
```

Read `docs/sql_walkthrough.md` beside the three SQL files. Explain independently why the requirement-to-holder join is a LEFT JOIN, and why a person holding three certificates must not count as three staff. Then explain why Unit C/Q06 is unmet rather than fragile. Your Day 2 aggregate/local and Day 4 transaction explanations are already confirmed; these are the new Day 5 ownership checks.

Stop after the Day 5 evidence and explanation. The next requested milestone will be Day 6: build the executive Power BI page from the verified unit summary and reconcile global/Unit C filter results. No SQL/Power BI reconciliation or actual PBIX verification is claimed today.
