# Day 6 verification

Started **October 11, 2026**, at the user's explicit request, ahead of the October 12 schedule. Metric date **2026-10-07**, synthetic data, fictional readiness proxies, and release gates are unchanged. Day 5 Windows technical verification is complete; its independent SQL explanation remains a review item at the user's request to proceed.

## Prepared implementation

| File | Purpose | Verification boundary |
| --- | --- | --- |
| `src/check_powerbi_input.py` | Read-only manifest/hash/row/grain/date check and expected selection totals | Runs in Python; does not operate Power BI or recheck database/source |
| `tests/test_powerbi_input.py` | Seven meaningful success/failure/preservation checks | Does not execute DAX or M |
| `powerbi/unit_summary.pq` | Import gate, explicit types, six-unit single-date unique grain | Six-row Desktop import visible; exact query/all types uninspected |
| `powerbi/executive_measures.dax` | Eleven distinct ORI measures; summed components, local gaps, blank undefined rates | Displayed KPI/table/filter results verified; exact Desktop definitions uninspected |
| `docs/day06_windows_handoff.md` | Existing-folder update, report preservation, import/build/filter/save checks | Displayed reconciliation passes; final report acceptance pending |
| `docs/powerbi_check.json` | Local preparation evidence and expected simulated comparisons | Expected values do not establish observed BI results |

The first page uses only the disconnected `unit_summary` table. Source-table learning measures/relationships stay intact; ORI measure names avoid collisions. The working PBIX is saved under an unused name so the original learning report remains intact. No PBIX, screenshot, cloud dashboard, or detail page has been created/operated by the assistant.

The Python checker verifies all three exported file hashes, manifest readiness/date/classification/reconciliation, exact file membership, headers/counts/unique grains, and summary count/gap/flag consistency. It writes no files. The M query separately blocks a bad manifest, wrong schema/types/date/classification/count/grain. **It does not calculate SHA-256.** Every import/refresh requires the Python hash check immediately beforehand and stable input files until refresh. This is a two-step workflow, not an atomic file transaction or a claim that Power BI runs the Python checker automatically. Existing cached BI values can remain visible after a failed refresh.

## Expected synthetic reconciliation

| Selection | Staffing | Coverage | Local gap | Qualification slots | Coverage | Missing slots | Flagged units |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All units | 254 / 250 | 101.6% | 10 | 88 / 95 | 92.63% | 7 | 4 |
| Unit C | 40 / 50 | 80.0% | 10 | 15 / 16 | 93.75% | 1 | 1 |
| Unit A | 41 / 40 | 102.5% | 0 | 16 / 16 | 100.00% | 0 | 0 |
| Unit A + C | 81 / 90 | 90.0% | 10 | 31 / 32 | 96.88% | 1 | 1 |

An empty filter should yield zero count measures, blank coverage measures, and a blank selected analysis date. Clearing filters must restore global totals. Multi-unit weighted components distinguish correct division from an average of row percentages. Unit A checks zero-gap/zero-flag rendering. Flagged units have current staffing or qualification gaps; fragile-but-met coverage and expiration inventory are separate questions.

## Completion boundary and next action

Local verification: **49 tests, OK, process exit 0**, 8.851 seconds on Linux. The live read-only check returns passed/exit 0, three matching-hash files with 6/48/193 rows and unique grains. Static review verifies the M schema matches all 24 exported columns, all eleven ORI measure names are unique, and every DAX source-column reference exists. This is not an M/DAX parser or runtime check. All 19 baseline files retain identical SHA-256 values, including the database, clean sources/manifest, dashboard exports/manifest, and existing local images. No live regeneration/reload was performed. JSON parsing and Git whitespace checks are complete for the prepared text artifacts. Details: `docs/powerbi_check.json`.

October 11 screenshots establish Windows input/import/model setup, displayed global/table/date/single/multiple/clear/empty/restoration results, and all 49 Windows tests. The user confirms reopening/all pages work and correctly calculates combined A+C coverage. Final page labels/interaction configuration, working path, import/type confirmation, and original-file preservation remain open. Exact M/DAX definitions/all types and unrounded rates are not inferred from displayed outputs. The assistant has not created, opened, or verified an actual PBIX file. No prototype/MVP release gate has passed.

Next: return the final page and remaining working-path/import/preservation/table-interaction confirmations. The tests, displayed filters, reopening confirmation, and combined calculation do not need repetition. No generation, validation, SQLite reload, installation, daily folder, or repeated input check is needed solely to use visuals on already imported data; run the checker again before any later import/refresh.

The user explicitly chose to continue while reviewing SQL basics. Carry forward zero-holder LEFT JOIN, person versus certificate grain, and unmet versus fragile coverage in `docs/sql_review_backlog.md`; do not claim independent mastery from the assistant's correction.

## Publication verified

Implementation commit **4d704ca3b6226c7250e916573c21cfe234b05ffc** directly follows **646c88526c40b6e19e44d946432ee23bd132ac06**. Its tree **43e6ab3a3a2c9382a92202b19c24d6c3807948d0** equals the locally tested checkpoint. GitHub API inspection and native fetch independently confirm the SHA; all 21 changed text-file blobs match, including the carried Day 5 Windows evidence. Existing remote history/assets and all 19 local baseline hashes are preserved. No image, generated dataset/database, environment, Power BI binary, or private history was published; the denied screenshot upload was not retried. Original local commits remain on private `execution/day06-local-history`; do not push archive branches or all branches.

A normal text-only documentation delivery, **5e8e66d06b8f7e33512dab56a8c14f5a9c00bebc**, follows this implementation and records its verification. No code changed after the 49-test pass; no successful tests/exports/loads were repeated for these notes. The user screenshots show the Windows fast-forward to this delivery. The following partial-progress supplement is recorded locally; it does not claim a new publication.

## Windows evidence reviewed October 11, 12:25 PDT

Seven attachments were read from their supplied scratch paths. No screenshot was copied into or published from the repository.

| Evidence | Established | Remaining boundary |
| --- | --- | --- |
| Terminal update/checker, 184726 / 184741 / 184758 | Fast-forward to 5e8e66d; passed/exit 0; matching hashes, unique grains, 6/48/193 rows, zero writes | Expected selections are Python calculations; the old test-exit line does not establish the updated 49-test Windows suite |
| Model view, 190256 | unit_summary disconnected; existing units-to-personnel 1:* single-direction relationship visible | Original PBIX and save/reopen not inspected |
| Data view, 190319 | Six units U01–U06; synthetic_only; October 7; visible staffing and covered/required qualification components match SQL | Screenshot does not expose the exact M query, all 24 columns/types, or every derived field |
| Canvas/slicer, 190507 | Slicer field is unit_summary[unit_name] | Filtering of cards/table not yet shown |
| Canvas/measure list, 192531 | Eleven ORI calculator-icon measures listed; slicer has no selected unit | Exact DAX definitions, formatting, and displayed results not inspected |

At this review point, the user was at block 5 and the staffing-card row was the next step. The following submission supersedes that next action; the executive page remains in progress. SQL ownership review and all remaining Desktop completion checks stay open.

## Staffing cards reviewed October 11, 19:10 PDT

Attachment image(20261012-021017).png shows Executive — simulated with no unit selected and four staffing cards. Available 254, required 250, and gap 10 match the SQL reference. Staffing coverage displays **1.02** as a rounded decimal; expected 254/250 = 1.016 is compatible with this display, but the exact underlying DAX result is not established. Set the measure format to Percentage with one decimal and confirm **101.6%**. No DAX implementation change is justified by the screenshot alone.

The earlier Executive Summary and Staffing Review page tabs are visible, which does not verify the original PBIX file or save/reopen behavior. Qualification results, the date card, table, unit/empty/clear filter checks, Windows 49-test suite, and report-preservation completion remain pending. Next add separate qualification coverage, qualification gap, and units-needing-attention cards; unfiltered expected values are **92.63%, 7, and 4**. This screenshot was read only, outside the repository; the supplement remains a local text checkpoint, with remote delivery unchanged.

## Seven unfiltered KPI cards reviewed October 11, 19:36 PDT

Attachment image(20261012-023640).png shows no unit selected and all seven cards matching the SQL reference: **254, 250, 101.6%, 10, 92.63%, 7, 4**. This supersedes the earlier pending staffing percentage display. Agreement is established for the displayed all-unit metrics at the specified precision; exact formulas/unrounded results and filter behavior are not established. The screenshot is read-only evidence outside the repository and was not copied or published.

Next add the analysis-date card and eight-field unit comparison table from the handoff, sorted Unit A–F with totals. Date/table/labels, unit/clear/empty checks, updated Windows tests, original-file preservation, and save/reopen remain pending. This local text checkpoint does not pass Day 6 or a release gate and does not change the remote delivery.

## Global table/date and Unit A/C filters reviewed October 11, 20:04 PDT

Read three attachments from their supplied scratch paths; no screenshot was copied or published.

| Attachment | Displayed evidence | Result |
| --- | --- | --- |
| image(20261012-025301).png | Eight table columns, six rows sorted A–F, matching row metrics and totals; seven matching global cards; analysis date October 7 | Global displayed table/cards/date pass |
| image(20261012-025404).png | Unit A checkbox selected; cards and one-row table 41/40, 102.5%, gap 0, qualification 100.00%, missing 0, attention 0, pairs-gap 0; date October 7 | Unit A slicer result passes |
| image(20261012-025424).png | Unit C checkbox selected; cards and one-row table 40/50, 80.0%, gap 10, qualification 93.75%, missing 1, attention 1, pairs-gap 1; date October 7 | Unit C slicer result passes |

The date is displayed as 10/7/2026 12:00:00 AM; its value is correct and a date-only display is still needed. Observed selected results establish slicer filtering for the cards/table; explicit table-to-card None settings are not shown. Next select A+C together and inspect weighted totals, then clear and confirm restoration. Multi/clear/empty, labels, updated Windows tests, original-file preservation, save/reopen, and ownership remain open. No complete Day 6 or release-gate claim.

## Combined A+C reviewed October 11, 20:08 PDT

The new attachment image(20261012-030820).png arrived during the active review and was read from its scratch copy. Both A and C checkboxes are selected. Cards and two correct table rows/totals reconcile: 81/90 = 90.0% staffing, local gap 10, qualification 96.88%, missing slots 1, attention 1, and pairs-gap total 1. Date remains October 7. The combined weighted-display check passes; no averaging-of-row-percentages behavior is observed in this selection. Exact formula/unrounded-result inspection is not claimed. No screenshot was copied or published.

Next confirm clear-slicer restoration and the temporary empty page-filter behavior. Page formatting/labels/interactions, updated Windows tests, original-report preservation, and save/reopen remain open. This is another local text checkpoint; remote delivery and release gates are unchanged.

## Clear/empty/restoration reviewed October 11, 20:27 PDT

| Attachment | Observed behavior | Result |
| --- | --- | --- |
| image(20261012-031324).png | Slicer has no selected unit; all six rows/global KPI values return after combined selection | Clear/restoration passes |
| image(20261012-032142).png | Visible page-level unit_name Advanced filter is No such unit; five displayed count cards zero; both coverage/date cards blank dashes; no table data rows | Empty-selection displayed behavior passes |
| image(20261012-032705).png | Global cards, all six rows/totals restored; date October 7, 2026 with no time | Post-empty restoration and date-only display pass |

All required displayed selection/date checks pass. Exact removal method of the temporary filter is not shown; restored results are. Screenshots were read outside the repository and were not copied/published. No actual PBIX file inspection, exact Desktop definitions/all-type confirmation, Windows 49-test pass, final labels/interactions, preservation/save/reopen, or independent ownership is inferred. Day 6 and release gates remain open for final acceptance.

## Windows tests and user confirmation reviewed October 11, 21:18 PDT

Three terminal attachments 040225 / 040257 / 040321 show all **49 Windows tests pass in 25.374 seconds, OK, Test exit: 0**, including the seven new input-check cases. No screenshot was copied or published. This is Python verification; it does not substitute for the separately inspected BI outputs.

The user confirms the PBIX reopens and all pages work. Reopening/earlier-page functionality is user-confirmed, not actual file inspection or original-file byte preservation. The user supplies the correct A+C calculation, 81/90 from the two units' components. The assistant clarifies the term coverage versus gap; arithmetic/component ownership is confirmed. The prior Day 5 SQL review remains open.

Final page labels/footer and table None settings are not visible in these terminal images. Request the final page and working path/original preservation/import types/table-click confirmation only; do not repeat completed tests, filters, reopening, or explanations. Day 6 final acceptance and release gates remain open pending that evidence.

## Primary references checked October 11

Microsoft Learn: [measure creation](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures), [DIVIDE](https://learn.microsoft.com/en-us/dax/divide-function-dax), [COALESCE](https://learn.microsoft.com/en-us/dax/coalesce-function-dax), [SELECTEDVALUE](https://learn.microsoft.com/en-us/dax/selectedvalue-function-dax), [Text/CSV](https://learn.microsoft.com/en-us/power-query/connectors/text-csv), [column types](https://learn.microsoft.com/en-us/powerquery-m/table-transformcolumntypes), [error records](https://learn.microsoft.com/en-us/powerquery-m/error-record), and [visual interactions](https://learn.microsoft.com/en-us/power-bi/create-reports/service-reports-visual-interactions). The fixed date, metric rules, layout, and acceptance values are project decisions, not Microsoft policies.
