# Day 10 — no-renewal qualification scenario

Started October 19, 2026 at 20:33 PDT under the user's instruction; source schedule October 16. Day 9 remains complete. Fixed analysis date is **October 7, 2026**. This milestone implements the already contracted deterministic scenario, not a forecast of actual renewals or future staffing. Release dates/scope remain unchanged; the scheduled MVP gate is open.

**Prepared and verified on Linux:** 72 tests pass, including twelve new scenario checks. Two scenario exports match, all three input checkers pass without writes, and all 48 pre-existing data files retain their hashes. SQL reference results are in [reconciliation](day10_reconciliation.md); three initial simulated findings are in [findings](day10_findings.md). **Windows reproduction, M/DAX execution, scenario visuals, and Day 10 acceptance remain pending.** Start with sections 1–2 and return their results before the import/model review.

Preserve the existing Windows checkout, .git, .venv, report and earlier pages/measures. No installation, source generation, validation rerun, or database reload is required for the saved passed snapshot. The continuing root is `C:\Users\dolai\OneDrive\Documents\Data Science 2027\Projects\Operational Readiness Intelligence OPI\Day 3`, not its powerbi subfolder.

## 1. Update the existing checkout and run the changed suite

```powershell
& {
    $ErrorActionPreference = 'Stop'
    git pull --ff-only
    if ($LASTEXITCODE -ne 0) { throw 'Git update failed. Return the output.' }
    .\.venv\Scripts\python.exe -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed. Return the output.' }
}
```

Expected: **72 tests, OK**, exit 0. Return the final test summary. Do not use reset/clean or replace the environment/report to resolve a local Git problem.

## 2. Export, repeat, preserve, and run the three read-only preflights

This block captures actual pre-existing files before the first scenario export, validates both nonempty manifests and both actual CSV hashes, requires two repeat results, and checks every protected file afterward. New scenario outputs have their own folder/manifest; neither earlier bundle is re-exported.

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $oriPython = '.\.venv\Scripts\python.exe'
    $oriOutput = '.\data\processed\dashboard\scenario'
    $oriScenarioFull = Join-Path (Get-Location).Path 'data\processed\dashboard\scenario'
    $oriNames = @('qualification_scenario.csv', 'scenario_unit_summary.csv')
    $oriRows = @{'qualification_scenario.csv'=144; 'scenario_unit_summary.csv'=18}
    if (-not (Test-Path '.\data\processed\readiness.sqlite3' -PathType Leaf)) {
        throw 'The accepted database is missing. Return the output; do not regenerate it.'
    }
    $oriBefore = @{}
    @(Get-ChildItem '.\data' -File -Recurse | Where-Object {
        -not $_.FullName.StartsWith(
            $oriScenarioFull + [IO.Path]::DirectorySeparatorChar,
            [StringComparison]::OrdinalIgnoreCase)
    }) | ForEach-Object { $oriBefore[$_.FullName] = (Get-FileHash $_.FullName -Algorithm SHA256).Hash }
    if ($oriBefore.Count -eq 0) { throw 'No protected files were captured.' }

    function Read-OriScenarioManifest {
        $oriManifest = Get-Content (Join-Path $oriOutput 'scenario_export_manifest.json') -Raw | ConvertFrom-Json
        if ($oriManifest.status -ne 'passed' -or $oriManifest.exports_ready -ne $true -or
            $oriManifest.exit_code -ne 0 -or $oriManifest.as_of_date -ne '2026-10-07' -or
            $oriManifest.bundle_kind -ne 'qualification_scenario' -or $oriManifest.scenario -ne 'no_renewal' -or
            $oriManifest.data_classification -ne 'synthetic_only' -or
            ($oriManifest.horizons_days -join ',') -ne '30,60,90' -or $null -eq $oriManifest.files) {
            throw 'Scenario manifest is not passed/ready for the contracted date/horizons. Return its contents.'
        }
        if (@($oriManifest.files.PSObject.Properties).Count -ne 2) { throw 'Expected exactly two scenario CSV entries.' }
        foreach ($oriName in $oriNames) {
            $oriEntry = $oriManifest.files.PSObject.Properties[$oriName]
            if ($null -eq $oriEntry -or $oriEntry.Value.rows -ne $oriRows[$oriName] -or
                $oriEntry.Value.sha256 -notmatch '^[0-9a-fA-F]{64}$') {
                throw "Missing or invalid scenario entry: $oriName"
            }
            if ((Get-FileHash (Join-Path $oriOutput $oriName) -Algorithm SHA256).Hash -ne $oriEntry.Value.sha256) {
                throw "Scenario file/manifest mismatch: $oriName"
            }
        }
        return $oriManifest
    }

    $oriLog = @(& $oriPython src\export_qualification_scenario.py)
    if ($LASTEXITCODE -ne 0) { $oriLog; throw 'First scenario export failed.' }
    $oriFirst = Read-OriScenarioManifest
    $oriLog = @(& $oriPython src\export_qualification_scenario.py)
    if ($LASTEXITCODE -ne 0) { $oriLog; throw 'Repeat scenario export failed.' }
    $oriSecond = Read-OriScenarioManifest
    $oriResults = @(foreach ($oriName in $oriNames) {
        [PSCustomObject]@{
            File = $oriName
            Rows = $oriSecond.files.PSObject.Properties[$oriName].Value.rows
            Repeat = $oriFirst.files.PSObject.Properties[$oriName].Value.sha256 -eq $oriSecond.files.PSObject.Properties[$oriName].Value.sha256
            ManifestMatches = $true
        }
    })
    if ($oriResults.Count -ne 2 -or $oriResults.Repeat -contains $false) { throw 'Repeat verification failed or is incomplete.' }
    $oriChecks = @(foreach ($oriScript in @('src\check_powerbi_input.py', 'src\check_process_input.py', 'src\check_scenario_input.py')) {
        $oriLog = @(& $oriPython $oriScript)
        if ($LASTEXITCODE -ne 0) { $oriLog; throw "Input check failed: $oriScript" }
        $oriCheck = ($oriLog -join "`n") | ConvertFrom-Json
        if ($oriCheck.status -ne 'passed' -or $oriCheck.file_writes -ne 0) { throw "Input check did not pass without writes: $oriScript" }
        [PSCustomObject]@{Check=$oriScript; Status=$oriCheck.status; Files=$oriCheck.files_checked; Writes=$oriCheck.file_writes}
    })
    foreach ($oriPath in $oriBefore.Keys) {
        if ((Get-FileHash $oriPath -Algorithm SHA256).Hash -ne $oriBefore[$oriPath]) {
            throw "Protected file changed: $oriPath"
        }
    }
    $oriResults | Format-Table -AutoSize
    $oriChecks | Format-Table -AutoSize
    "Database and all prior data files preserved: True ($($oriBefore.Count) files checked)"
}
```

Expected two rows: **144/18**, both Repeat and ManifestMatches True; checker statuses passed, files **3/2/2**, writes **0/0/0**; preservation True. Return these tables and the preservation line. A failed export invalidates its manifest even if old CSVs remain. Correct the reported cause and rerun; do not refresh from an unpassed manifest.

## 3. Import only the scenario fact and derived horizon lookup

Run all three preflights immediately before import/refresh and keep files stable through refresh. Their Python checks include SHA-256; M does not hash. A failed Desktop refresh can retain cached results.

1. In the existing PBIX, add a Blank Query named **qualification_scenario**. Paste the whole [M query](../powerbi/qualification_scenario.pq), replacing only ProjectRoot with the same existing root. It references the accepted qualification_detail query to check every current baseline pair. Expected **144 rows / 25 columns**: 48 pairs at each of three horizons.
2. Add **scenario_horizon** using [its M query](../powerbi/scenario_horizon.pq). Expected **3 rows / 2 columns**: horizon_days 30/60/90 and Text labels 30 days/60 days/90 days.
3. Text IDs/labels/classification/scenario remain Text; as_of_date/horizon_date are Date; horizons/counts/flags Whole Number; coverage ratios Decimal Number. M rejects fractional integer values before converting to Int64. Keep errors visible rather than dropping rows.
4. Close & Apply. **Do not import scenario_unit_summary.csv**: it is a SQL comparison reference, not another report fact. Preserve all earlier queries.

Add only these three active **1:* Single**, lookup-to-fact relationships:

| One side | Many side |
| --- | --- |
| unit_summary[unit_id] | qualification_scenario[unit_id] |
| qualification_filter[qualification_id] | qualification_scenario[qualification_id] |
| scenario_horizon[horizon_days] | qualification_scenario[horizon_days] |

Retain all seven accepted prior links: target **ten** total. Remove only unintended new auto-detected links. No fact-to-fact, old-units/personnel, or Both-direction link belongs in this scenario model. Return import counts/type confirmation and Manage relationships before the measure/page review.

## 4. Measures and page

Create the **17 ORI S measures**, one at a time, from [scenario_measures.dax](../powerbi/scenario_measures.dax), home table qualification_scenario. Keep every existing measure. Coverage: Percentage/two decimals; counts: Whole Number/no display-unit abbreviation; dates: date only.

Create **Scenario — no renewal** with title **Qualification coverage if no certificates renew — synthetic**. Show a concise assumption caption: **October 7 eligible cohort; staffing, units, and availability fixed; no renewals or future certificate activations.** Add Analysis Date and Horizon Date cards and the ORI S Scenario Status text card. Footer: **Deterministic scenario, not a prediction. Holder slots are not unique people or simultaneous assignment capacity.**

Three page-local, unsynced slicers:

- unit_summary[unit_name], multiple selection allowed;
- qualification_filter[qualification_id], multiple selection allowed;
- scenario_horizon[horizon_label], **Single select On**, Select all Off; select **30 days** and save that default. Sort by horizon_days if needed.

Eight main cards: Current Coverage; Projected Coverage; Current Missing Slots; Projected Missing Slots; Additional Missing Slots; New Gap Pairs; Projected Gap Pairs; Eligible Holder Slots Lost. Label the last explicitly as **holder slots**, not people. Helper measures provide required/capped counts for reconciliation; no extra card is required.

Unit comparison: unit_summary[unit_name] plus current/projected coverage, current/projected/additional missing slots, and new gap pairs. Use measures, so totals divide summed capped/required counts. Pair detail uses qualification_scenario columns: unit_id, qualification_id, required_holder_count, current_eligible_holder_count, projected_eligible_holder_count, current_gap, projected_gap, additional_gap, eligible_holders_lost, is_new_gap, projected_is_fragile. Use Don't summarize for raw integer fields and hide this raw table's totals. Add **ORI S Horizon Days** to Filters on this visual and require **is not blank**, so detail rows disappear if the horizon selection is invalid.

All three slicers should Filter all scenario cards/tables. For each table separately: select the table visual → top-ribbon Format → Edit interactions → **None** on all cards/date/status cards, the other table, and all three slicers. Retain slicer-source Filter interactions. Exit Edit interactions before selecting a data row. Relationships stay Single; interaction changes do not require model changes.

## 5. Reconcile and finish only Day 10

Follow [the reference checklist](day10_reconciliation.md): global 30/60/90; D/Q04, C/Q06, B/Q03; A+C/Q01+Q02; clear unit/qualification filters and restore 30-day global. Validate the no/ambiguous-horizon guard, then the full empty qualification scope with one valid horizon. Remove temporary filters, restore global, and test a selected data row in each table. Save/reopen and confirm Scenario and the previously accepted pages function. No repeat Day 8/9 cases are requested solely for evidence.

The horizon guard deliberately returns blank when no single horizon is defined; otherwise repeated requirements could be added across alternative scenarios. With one valid horizon but no matching pairs, counts are zero and ratios/dates blank. These are different states. To exercise no selection, temporarily turn Single select Off and clear the horizon slicer; then select 30+60. Both states should show Select one horizon, blank numerical cards, and no raw pair rows. Restore Single select On and 30 days afterward.

Supply three short own explanations:

1. Why do D/Q04's six lost eligible holders create **two** missing slots?
2. Why is C/Q06 projected gap **2**, additional gap **1**, and new-gap flag **0**?
3. Which fixed assumptions make this a conditional no-renewal scenario rather than a prediction of actual future coverage?

The initial [three findings](day10_findings.md) have SQL evidence; their scenario-page display and the user's explanations remain pending. Day 10 closes only after its Windows/report/ownership checks. The broader MVP acceptance/backup-demo work stays separately open; do not start Day 11 in this milestone.

Primary implementation references: [SQLite calendar date modifiers](https://www.sqlite.org/lang_datefunc.html), [DAX HASONEVALUE](https://learn.microsoft.com/en-us/dax/hasonevalue-function-dax), and [DAX DIVIDE](https://learn.microsoft.com/en-us/dax/divide-function-dax). These document functions, not the project's simulated findings or Desktop execution.
