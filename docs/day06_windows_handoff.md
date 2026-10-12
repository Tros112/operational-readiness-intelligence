# Day 6 — build the executive Power BI page

Started **October 11, 2026**, at your request, ahead of the October 12 schedule. Use the existing Git project, `.venv`, database, exports, and Power BI learning report. The metric date remains **October 7**. All operational values are **synthetic**; readiness is a fictional proxy.

Day 5 Windows technical verification is complete: the corrected repeat/hash check, database preservation, Unit C results, and 42 tests passed. Your SQL explanation remains a review item; your explicit Day 6 instruction allows the build to proceed. No technical rerun of Day 5 setup, generation, validation, or loading is required.

The assistant prepares the import query, measures, layout, and expected values. **You run Power BI Desktop locally.** October 11 follow-up evidence verifies the displayed executive-page values/table/date and global/single/multiple/clear/empty filters, a passed input check, and 49 Windows tests. The user confirms reopening/all pages work and the combined A+C calculation. Final labels/interactions and working-file/import/preservation details remain open. Exact Desktop definitions and an actual PBIX file have not been inspected by the assistant. These files remain reusable build instructions; they do not contain a finished PBIX.

## 1. Update this same project and check the saved exports

Review `git status --short --branch` first. Keep any local files. If a pull reports conflicting changes, stop and return its output; do not reset, clean, or replace the folder.

Run the whole block in the existing project root:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    git status --short --branch
    git pull --ff-only origin main
    if ($LASTEXITCODE -ne 0) { throw 'Update stopped; retain local files and return the output.' }
    git rev-parse HEAD

    .\.venv\Scripts\python.exe src\check_powerbi_input.py
    if ($LASTEXITCODE -ne 0) { throw 'Power BI input check stopped; do not import/refresh. Return the output.' }

    (Get-Location).Path
    notepad .\docs\day06_windows_handoff.md
}
```

Expected checker: `status: passed`, exit 0, three files checked, row counts **6 / 48 / 193**, `csv_hashes_match_manifest: true`, `output_grains_unique: true`, and `file_writes: 0`. Its `expected_selections` section is a reference calculated from the saved SQL output, not a Power BI observation.

The checker reads all three CSVs and their manifest. It does not regenerate/export data, open SQLite, or change audit files. If source/database contents have changed intentionally, rerun the existing exporter successfully first; this checker does not recheck the database against the source. Never edit hashes to make a check pass.

**Before every later import/refresh**, rerun this checker immediately beforehand. Do not change/re-export the CSVs between the check and refresh. The M query checks manifest state, schema, six-row grain, date, types, and classification. It does **not** compute SHA-256; the Python preflight supplies that check. This is a documented two-step local refresh procedure, not an atomic filesystem transaction. An unsuccessful refresh can leave old imported data visible in Power BI; do not call that a successful new refresh.

## 2. Keep your learning report and create a working report

1. Open the existing PBIX that already contains your staffing learning page.
2. Before editing, use **File → Save as** to save a working copy as `powerbi\ORI_Demo.pbix` in this same project. Use an unused filename if that file already exists. The original report stays intact. Continue with this working copy for later pages; do not make daily project folders.
3. Add a **new blank page** and name it **Executive — simulated**. Keep the earlier page, its units/personnel relationship, and its existing measures.

The `ORI` prefix on new measures prevents name collisions with the earlier `Available Personnel`, `Required Personnel`, and coverage measures. Use the new measures on the new page.

## 3. Import only the unit summary with the provided query

1. In Power BI, choose **Home → Get data → Blank query** (under **Other** in the full Get data dialog).
2. In Power Query Editor, name the new query **`unit_summary`**.
3. Open `powerbi\unit_summary.pq` in Notepad. Copy the **entire query**, including `let` and its final `in` expression, into **Advanced Editor**.
4. Replace only the `ProjectRoot` value with the exact path printed by `(Get-Location).Path`. In M, Windows backslashes are literal: do not double them. Do not paste the path into the Git-tracked source file.
5. Select **Done**. The preview should contain exactly **six rows and 24 columns**. Verify IDs U01–U06, names Unit A–F, `synthetic_only`, and October 7 for every row. Count fields are Whole Number; ratio fields are Decimal Number; `as_of_date` is Date; names/IDs/classification are Text. Blank ratios stay null, rather than becoming zero.
6. If the query returns an error, return the exact error. Do not use Remove Errors, replace critical values, or bypass its gate.
7. Select **Close & Apply**. In Model view, keep `unit_summary` **disconnected** for this page. No relationship is needed because every visual uses this one table. If auto-detection created a relationship involving this new table, remove only that new relationship. Preserve the existing units-to-personnel relationship.

Use **`unit_summary[unit_name]`** for the new slicer and comparison table. The earlier page's `units[unit_name]` slicer does not filter a disconnected summary. Do not sync the learning-page slicer to this page or mix its source-table measures into the executive visuals.

Microsoft documents the [Text/CSV connector](https://learn.microsoft.com/en-us/power-query/connectors/text-csv), [explicit type conversion](https://learn.microsoft.com/en-us/powerquery-m/table-transformcolumntypes), and [error records](https://learn.microsoft.com/en-us/powerquery-m/error-record). The project-specific gates and fixed schema are in the supplied query; the query still needs Desktop execution.

**First review point:** if you want guided steps, return a screenshot of this six-row preview/model before building visuals. It verifies the import stage only.

## 4. Create the eleven measures, one at a time

Select the `unit_summary` table, then choose **Modeling → New measure**. Copy **one complete definition at a time** from `powerbi\executive_measures.dax`. Do not paste all definitions into one measure or create calculated columns.

| Measure | Format | Role |
| --- | --- | --- |
| `ORI Available Personnel` | Whole number, 0 decimals | Staffing numerator |
| `ORI Required Personnel` | Whole number, 0 decimals | Staffing denominator |
| `ORI Staffing Gap` | Whole number, 0 decimals | Sum of local staffing gaps |
| `ORI Staffing Coverage` | Percentage, 1 decimal | Summed available / summed required |
| `ORI Covered Qualification Slots` | Whole number, 0 decimals | Already capped per requirement pair in SQL |
| `ORI Required Qualification Slots` | Whole number, 0 decimals | Qualification denominator |
| `ORI Qualification Gap` | Whole number, 0 decimals | Missing holder slots, not a person headcount |
| `ORI Qualification Coverage` | Percentage, 2 decimals | Summed covered / summed required slots |
| `ORI Units Needing Attention` | Whole number, 0 decimals | Units with a current staffing or qualification gap |
| `ORI Analysis Date` | Date, `MMM d, yyyy` | Single October 7 snapshot in the selection |
| `ORI Qualification Pairs With Gap` | Whole number, 0 decimals | Required pairs currently unmet |

Counts use `COALESCE(..., 0)` so an empty selection shows zero. `DIVIDE` has no alternate zero result: an undefined rate stays blank. `SELECTEDVALUE` returns the single analysis date and stays blank with no rows. These are prepared DAX definitions; Python tests do not execute them.

**Two rules to keep visible:** staffing coverage is uncapped, so 101.6% is valid. Staffing Gap is the sum of per-unit gaps already calculated by SQL; it is not `MAX(total required - total available, 0)`, which would incorrectly hide Unit C's shortage.

Microsoft references: [measures](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures), [DIVIDE](https://learn.microsoft.com/en-us/dax/divide-function-dax), [COALESCE](https://learn.microsoft.com/en-us/dax/coalesce-function-dax), and [SELECTEDVALUE](https://learn.microsoft.com/en-us/dax/selectedvalue-function-dax). Checked October 11, 2026.

## 5. Build a readable page

Use a 16:9 page, approximately **1280 × 720**. First verify plain visuals; styling can be kept simple.

| Region | Visual and fields | User-facing label |
| --- | --- | --- |
| Header | Text box | Operational Readiness Intelligence |
| Header | Text box | Synthetic staffing and qualification snapshot |
| Top right | Card: `ORI Analysis Date` | Analysis date |
| Under header | List slicer: `unit_summary[unit_name]` | Unit |
| First KPI row | Four separate cards: available, required, staffing coverage, staffing gap | Available personnel; Required personnel; Staffing coverage; Local staffing gap |
| Second KPI row | Three separate cards: qualification coverage, qualification gap, units needing attention | Qualification coverage; Missing holder slots; Units with current gaps |
| Lower section | Table with the fields listed below | Unit comparison |
| Footer | Text box | Synthetic data. Qualification slots do not establish simultaneous assignments. Unit flags are fictional proxies. |

Set every count card's **Display units to None**, with zero decimal places. Use one decimal for staffing coverage and two for qualification coverage. Counts are not percentages. Keep the date visible even though today's calendar date is October 11: the analysis date is October 7.

The comparison table uses:

1. `unit_summary[unit_name]`
2. `ORI Available Personnel`
3. `ORI Required Personnel`
4. `ORI Staffing Coverage`
5. `ORI Staffing Gap`
6. `ORI Qualification Coverage`
7. `ORI Qualification Gap`
8. `ORI Qualification Pairs With Gap`

Rename table headers for readability without renaming source columns. Sort Unit A through F. Enable the totals row; measures recalculate ratios from total components, rather than averaging the displayed percentages. You can temporarily add covered/required qualification-slot measures to see their components during reconciliation.

Configure the slicer as a list with checkboxes, **Single select off**. If available, turn **Multi-select with CTRL off** so two checkbox selections are easy to test. Select the slicer, use **Format → Edit interactions**, and confirm it filters every card and the table. For the table's interactions, choose **None** on the cards and slicer so clicking a table row cannot silently change the KPI cards. The slicer remains the filter control for this page. Microsoft documents these [interaction controls](https://learn.microsoft.com/en-us/power-bi/create-reports/service-reports-visual-interactions).

The current-gap flag is exactly: staffing gap > 0 OR at least one qualification pair has a gap. It does not include upcoming expirations or fragile-but-met coverage. Unit B can have a fragile qualification while its current-gap flag is zero. Later pages handle those separate questions.

## 6. Reconcile slicer results before calling the page complete

Clear any table selection and page/report filters on `unit_summary`. First use the **slicer checkbox**, then clear it. Do not substitute selecting a table row for the slicer test.

| Selection | Available / required | Staffing coverage | Staffing gap | Covered / required slots | Qualification coverage | Missing slots | Units with gaps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All units | 254 / 250 | 101.6% | 10 | 88 / 95 | 92.63% | 7 | 4 |
| Unit C | 40 / 50 | 80.0% | 10 | 15 / 16 | 93.75% | 1 | 1 |
| Unit A | 41 / 40 | 102.5% | 0 | 16 / 16 | 100.00% | 0 | 0 |
| Unit A + Unit C | 81 / 90 | 90.0% | 10 | 31 / 32 | 96.88% | 1 | 1 |
| Clear slicer | Restored all-unit values | 101.6% | 10 | 88 / 95 | 92.63% | 7 | 4 |

All these are **expected simulated SQL values**, not observed Desktop results. The two-unit test catches averages-of-percentages: (102.5% + 80%) / 2 = 91.25%, which is wrong; 81 / 90 = 90% is correct. Confirm the analysis date stays October 7 throughout.

Expected unfiltered table rows:

| Unit | Available | Required | Staffing coverage | Staffing gap | Qualification coverage | Missing slots | Pairs with gaps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 41 | 40 | 102.5% | 0 | 100.00% | 0 | 0 |
| B | 44 | 40 | 110.0% | 0 | 100.00% | 0 | 0 |
| C | 40 | 50 | 80.0% | 10 | 93.75% | 1 | 1 |
| D | 47 | 40 | 117.5% | 0 | 87.50% | 2 | 2 |
| E | 42 | 40 | 105.0% | 0 | 87.50% | 2 | 2 |
| F | 40 | 40 | 100.0% | 0 | 87.50% | 2 | 2 |

One empty-selection check: temporarily add a **page filter** on `unit_summary[unit_name]` using Advanced filtering with an exact value that does not exist, such as `No such unit`. The count cards should show zero; coverage and analysis-date measures should be blank. Remove that temporary filter and confirm all-unit totals return. This tests blank-rate behavior without altering CSVs or injecting dirty records.

If any result differs, return the selected units and the actual values. Do not adjust a measure to force a target number before diagnosing field choice, relationships, filters, and formatting.

## 7. Save, reopen, and return evidence

Save the **working** PBIX, close it, reopen it, and confirm the new executive page and earlier learning page still work. Record the working file's local path; keep PBIX/PBIT files and screenshots out of Git publication. A filename is not report verification evidence.

Run the updated Python suite once with the existing interpreter:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
$oriDay6TestExit = $LASTEXITCODE
$oriDay6TestExit
if ($oriDay6TestExit -ne 0) { throw 'Tests did not pass; return the exact error.' }
```

The suite now contains **49 tests**: the prior 42 plus seven read-only input-check tests. These do not test DAX or M execution.

Return readable **all-unit and Unit C slicer screenshots**, plus:

```text
Input checker status / exit:
Power Query import: 6 rows / 24 columns / correct types:
All-unit values match / Unit C values match:
Unit A zero-gap check / A+C weighted-coverage check:
Clear-slicer totals restored / empty selection zero counts and blank rates:
Analysis date:
Working report saves/reopens / learning page preserved:
Python tests / exit:
Any exact error or blocker:
```

For today's explanation, describe why the all-unit staffing gap can remain 10 when staffing coverage exceeds 100%, and what the Unit A + C calculation demonstrates. Your earlier aggregate/local explanation is already established; build on it. The SQL LEFT JOIN/grain/fragility review remains a carried learning item, not falsely marked mastered.

Stop at Day 6. Qualification and expiration detail pages are later milestones. A verified executive page will support the October 13 prototype gate; the gate is not passed by this handoff or by screenshots that have not yet been reviewed.
