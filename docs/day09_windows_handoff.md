# Day 9 — process metrics and Power BI page

Started October 17, 2026 at the user's instruction; original source schedule October 15. Day 8 is complete. Metric date stays **October 7**, and opening/completion period is **July 10–October 7 inclusive**. MVP and polish remain October 19/30, not yet passed.

**October 19, 20:13 PDT review:** all Day 9 technical/report checks are accepted, including restoration, both selected-data-row interactions, and user-confirmed PBIX reopening/function. The completed-case denominator and Open-only blank-rate explanations are accepted. **Only the own combined-median explanation needs refinement. Continue at section 6.** The build/reproduction commands below remain references; no repeat screenshot, reopening, setup, or test is required. The assistant has not operated the PBIX or inspected every installed M/DAX definition. Preserve all previous assets; no installation/regeneration/reload or new pipeline/test run is needed for this review.

## 1. Update and run the changed suite once

Open PowerShell in the existing project root containing `src`, `data`, and `powerbi`, rather than in its powerbi subfolder. The continuing Windows root is `C:\Users\dolai\OneDrive\Documents\Data Science 2027\Projects\Operational Readiness Intelligence OPI\Day 3`.

```powershell
& {
    $ErrorActionPreference = 'Stop'
    git pull --ff-only
    if ($LASTEXITCODE -ne 0) { throw 'Update stopped. Preserve local work and return the output.' }
    .\.venv\Scripts\python.exe -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Tests did not pass. Return the summary/error before continuing.' }
}
```

**Accepted:** the October 17 screenshot shows **Ran 60 tests in 44.115s / OK**, reviewed October 19. No separate exit-code line is visible. Eleven process checks supplement the earlier 49. These commands are a reproduction reference; no unchanged-suite rerun is requested. Python tests do not execute Power BI.

## 2. Export, repeat, preserve, and check

The new files are local under `data/processed/dashboard/process/`: `process_case_detail.csv` (600 rows/16 columns), `process_unit_summary.csv` (6/14), and `process_export_manifest.json`. The unit summary is a SQL reference, **not a Power BI import**: filtering case type requires case-level records to recompute medians.

Run this self-contained block. It captures the first export before comparing the repeat and verifies both actual CSV hashes each time. No previous PowerShell variables are required.

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $oriDay9Output = '.\data\processed\dashboard\process'
    $oriDay9Names = @('process_case_detail.csv', 'process_unit_summary.csv')
    $oriDay9Rows = @{'process_case_detail.csv'=600; 'process_unit_summary.csv'=6}
    $oriDay9LegacyNames = @('unit_summary.csv', 'qualification_detail.csv', 'expiration_detail.csv', 'export_manifest.json')
    $oriDay9LegacyBefore = @{}
    foreach ($oriName in $oriDay9LegacyNames) {
        $oriDay9LegacyBefore[$oriName] = (Get-FileHash (Join-Path '.\data\processed\dashboard' $oriName) -Algorithm SHA256).Hash
    }
    $oriDay9DbBefore = (Get-FileHash '.\data\processed\readiness.sqlite3' -Algorithm SHA256).Hash

    function Read-OriDay9Manifest {
        $oriManifest = Get-Content (Join-Path $oriDay9Output 'process_export_manifest.json') -Raw | ConvertFrom-Json
        if ($oriManifest.status -ne 'passed' -or $oriManifest.exports_ready -ne $true -or
            $oriManifest.exit_code -ne 0 -or $oriManifest.bundle_kind -ne 'process' -or
            $oriManifest.as_of_date -ne '2026-10-07' -or $oriManifest.period_start -ne '2026-07-10' -or
            $oriManifest.data_classification -ne 'synthetic_only' -or $null -eq $oriManifest.files) {
            throw 'Process manifest is not passed/ready for the fixed period. Return its contents.'
        }
        foreach ($oriName in $oriDay9Names) {
            $oriEntry = $oriManifest.files.PSObject.Properties[$oriName]
            if ($null -eq $oriEntry -or $oriEntry.Value.rows -ne $oriDay9Rows[$oriName] -or
                $oriEntry.Value.sha256 -notmatch '^[0-9a-fA-F]{64}$') {
                throw "Missing/invalid process manifest entry: $oriName"
            }
            $oriActual = (Get-FileHash (Join-Path $oriDay9Output $oriName) -Algorithm SHA256).Hash
            if ($oriActual -ne $oriEntry.Value.sha256) { throw "File/manifest mismatch: $oriName" }
        }
        return $oriManifest
    }

    .\.venv\Scripts\python.exe src\export_process_metrics.py
    if ($LASTEXITCODE -ne 0) { throw 'First process export did not pass. Return the output.' }
    $oriDay9First = Read-OriDay9Manifest
    .\.venv\Scripts\python.exe src\export_process_metrics.py
    if ($LASTEXITCODE -ne 0) { throw 'Repeat process export did not pass. Return the output.' }
    $oriDay9Second = Read-OriDay9Manifest
    $oriDay9Results = @(foreach ($oriName in $oriDay9Names) {
        [PSCustomObject]@{
            File = $oriName
            Rows = $oriDay9Second.files.PSObject.Properties[$oriName].Value.rows
            Repeat = $oriDay9First.files.PSObject.Properties[$oriName].Value.sha256 -eq $oriDay9Second.files.PSObject.Properties[$oriName].Value.sha256
            ManifestMatches = $true
        }
    })
    if ($oriDay9Results.Count -ne 2 -or $oriDay9Results.Repeat -contains $false) {
        throw 'Process repeat comparison failed or is incomplete.'
    }
    $oriDay9DbPreserved = $oriDay9DbBefore -eq (Get-FileHash '.\data\processed\readiness.sqlite3' -Algorithm SHA256).Hash
    $oriDay9LegacyPreserved = $true
    foreach ($oriName in $oriDay9LegacyNames) {
        if ($oriDay9LegacyBefore[$oriName] -ne (Get-FileHash (Join-Path '.\data\processed\dashboard' $oriName) -Algorithm SHA256).Hash) {
            $oriDay9LegacyPreserved = $false
        }
    }
    if (-not $oriDay9DbPreserved -or -not $oriDay9LegacyPreserved) { throw 'Database or prior exports changed.' }
    .\.venv\Scripts\python.exe src\check_powerbi_input.py
    if ($LASTEXITCODE -ne 0) { throw 'Prior dashboard inputs failed. Return the output.' }
    .\.venv\Scripts\python.exe src\check_process_input.py
    if ($LASTEXITCODE -ne 0) { throw 'Process input check failed. Return the output.' }
    $oriDay9Results | Format-Table -AutoSize
    "Database preserved: $oriDay9DbPreserved"
    "Prior dashboard bundle preserved: $oriDay9LegacyPreserved"
}
```

Expected: both rows have Repeat/ManifestMatches True, both preservation lines True; process checker passed, files_checked 2, rows 600/6, file_writes 0. The original checker still reports three files/6/48/193. The earlier October 17 evidence establishes this first checkpoint; no repeat submission is required for those passed results. Do not import on an error or a non-passed manifest. Before every later refresh, run both checkers and keep files stable through refresh; a failed refresh may leave cached values visible.

## 3. Import two queries and add two relationships

In the working PBIX, **Transform data → New Source → Blank Query → Advanced Editor**:

1. Paste the entire `powerbi/process_case_detail.pq`; replace only `PASTE_EXISTING_PROJECT_ROOT_HERE` with the project root above. Name it **process_case_detail**.
2. Paste the entire `powerbi/process_filter.pq` into another blank query named **process_filter**.
3. Close & Apply. Expected imports: **600 rows/16 columns** and **4 rows/1 column**. The type lookup contains evaluation, onboarding, records_update, transfer.

The M query checks the pinned reference date/schema/counts, unique case grain, unit labels, nullable outcomes, and date/flag/duration agreement. It does not compute SHA-256. Keep nulls in closed_date, correction_required, completed_cycle_days, and open_age_days; do not replace them with zero. Date fields are Date, flags/outcome/durations Whole Number, keys/labels/status Text. The final median measure may have half-day values even though individual durations are integer calendar days.

Add exactly these active **1:* Single** relationships, filtering from lookup to detail:

| One side | Many side |
| --- | --- |
| unit_summary[unit_id] | process_case_detail[unit_id] |
| process_filter[case_type] | process_case_detail[case_type] |

Preserve the five accepted relationships from Day 8, giving **seven total** in the existing report. Remove only unintended new auto-detected links to personnel, old units, qualification/expiration facts, or raw admin_cases. No Both direction or fact-to-fact join is needed. Return the import counts/type confirmation and relationship view if a setup issue appears.

## 4. Create ten measures and one page

Create **one measure at a time** from `powerbi/process_measures.dax`, with process_case_detail as home table. Keep all ORI/ORI Q and learning definitions intact.

| Measure group | Format |
| --- | --- |
| ORI P Opened Cases; Completed Cases; Correction Cases; Open Cases | Whole Number, display units None |
| ORI P Discrepancy Rate | Percentage, two decimals; undefined blank |
| ORI P Median Cycle Days; Median Open Age Days | Decimal Number, one decimal; undefined blank |
| ORI P Oldest Open Age Days | Whole Number; undefined blank |
| ORI P Analysis Date; Period Start | Date only |

New page: **Process — simulated**. Title: **Administrative process review — synthetic**. Show an ORI P Analysis Date card and a text caption: **Openings/completions: July 10–October 7, 2026. Backlog: open at October 7.** No date/status slicer is needed for this fixed-period MVP.

Use page-local, unsynced, multiple-select slicers from **unit_summary[unit_name]** and **process_filter[case_type]**. Both filter every new card/table. Use two simple rows of four cards: opened, completed, corrections, discrepancy rate; median cycle days, open cases, median open age, oldest open age.

Unit comparison table: unit_summary[unit_name], then the eight measures above. Totals may remain on because each rate/median is a measure recomputed from selected cases; never import or average unit-summary median columns.

Case table: process_case_detail[case_id], unit_name, case_type, status_at_as_of, opened_date, closed_date, correction_required, completed_cycle_days, open_age_days. Use plain date columns, not automatic hierarchies. Hide totals and choose Don't summarize for raw outcome/day fields. Open correction outcomes remain blank, while known completed outcomes are 0 or 1.

For both tables as source visuals, **top Format → Edit interactions → None** over cards, other table, date, and slicers. Keep each slicer as source set to Filter on all new cards/tables. Exit Edit interactions.

Footer: **Synthetic cases; corrections are a fictional discrepancy proxy. Open outcomes are unknown. Completed cycle time and current backlog age are separate calendar-day measures.** Unit F is a deliberately planted process hotspot, not a discovered real-world cause.

## 5. Reconcile and finish Day 9

Use `docs/day09_reconciliation.md`. Start with the unfiltered page: opened **600**, completed **442**, corrections **45**, rate **10.18%**, median cycle **7.0 days**, open **158**, median open age **27.0**, oldest **88**, analysis date October 7.

Global, F/non-F, evaluation/onboarding, A+F, A+F/onboarding+transfer, Open-only and empty outputs now reconcile. The actual empty test used status_at_as_of is empty, which is equivalent; six zero-count lookup-unit rows are expected. Passing these displayed cases does not establish the remaining restoration, data-row interaction, reopening, or own-explanation checks.

Include brief own explanations of why the discrepancy denominator is completed cases, why an Open-only selection has a blank rate instead of 0%, and why the combined median uses case durations rather than unit medians. These are new process concepts; the accepted Day 8 questions do not need repeating. Add one verified process finding to your earlier short pitch after page acceptance; no new recording/timer requirement is introduced. Source-plan elevator-pitch attendance, actual hours, and employer feedback remain unreported unless supplied.

Stop after Day 9 completion. The no-renewal scenario is Day 10; ML/cloud/deployment remain outside this milestone. Primary references: [SQLite window functions](https://www.sqlite.org/windowfunctions.html), [SQLite read-only URI](https://sqlite.org/uri.html), [DAX MEDIAN and blank handling](https://learn.microsoft.com/en-us/dax/median-function-dax), and [KEEPFILTERS](https://learn.microsoft.com/en-us/dax/keepfilters-function-dax).

## 6. Remaining completion checks

Accepted from the 20:13 PDT submission: temporary-filter removal/global restoration; Unit C and C00004 selected rows leaving cards/date/other table global; user-confirmed PBIX reopening/function; and own completed-denominator/Open-only blank-rate reasoning. No repeat of those checks is needed.

**One remaining action:** explain in your own words why the combined median must be computed from eligible individual case durations rather than the unit medians. A unit median also respects the selected case-type filter; the issue is the loss of case counts/distributions when a whole unit is reduced to one value. For a small teaching example, unit A durations [1,2,3] and unit B [20] have medians 2 and 20. The four cases together have median 2.5, while the two unit medians have median 11. This is illustrative data, not an ORI finding.

Everything in the Day 9 setup/numeric/edge/report checklist is accepted. No code/metric/data change or new test/checker/export run is indicated. Day 9 remains open only for that existing own explanation. The scheduled October 19 MVP gate is still open in [its status checkpoint](checkpoints/2026-10-19_mvp_status.md); no deadline/scope change or Day 10 work is inferred.
