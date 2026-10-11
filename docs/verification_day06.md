# Day 6 verification

Started **October 11, 2026**, at the user's explicit request, ahead of the October 12 schedule. Metric date **2026-10-07**, synthetic data, fictional readiness proxies, and release gates are unchanged. Day 5 Windows technical verification is complete; its independent SQL explanation remains a review item at the user's request to proceed.

## Prepared implementation

| File | Purpose | Verification boundary |
| --- | --- | --- |
| `src/check_powerbi_input.py` | Read-only manifest/hash/row/grain/date check and expected selection totals | Runs in Python; does not operate Power BI or recheck database/source |
| `tests/test_powerbi_input.py` | Seven meaningful success/failure/preservation checks | Does not execute DAX or M |
| `powerbi/unit_summary.pq` | Import gate, explicit types, six-unit single-date unique grain | Reviewed against Microsoft documentation; Desktop execution pending |
| `powerbi/executive_measures.dax` | Eleven distinct ORI measures; summed components, local gaps, blank undefined rates | Prepared definitions; DAX execution pending |
| `docs/day06_windows_handoff.md` | Existing-folder update, report preservation, import/build/filter/save checks | Windows build pending |
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

Desktop M/DAX execution, the actual page, all-unit/Unit C/Unit A/multi-unit/empty filter behavior, save/reopen, report preservation, and updated Windows Python tests remain pending. The assistant has not created, opened, or verified an actual PBIX. No prototype/MVP release gate has passed.

Next: pull the verified text-only update into the existing Windows project, run `src/check_powerbi_input.py` with the existing interpreter, save a working copy of the learning report, and import `unit_summary` using the provided M query. Then create the measures/page and return the exact reconciliation evidence in the handoff. No generation, validation, SQLite reload, installation, or daily folder is needed.

The user explicitly chose to continue while reviewing SQL basics. Carry forward zero-holder LEFT JOIN, person versus certificate grain, and unmet versus fragile coverage in `docs/sql_review_backlog.md`; do not claim independent mastery from the assistant's correction.

## Publication verified

Implementation commit **4d704ca3b6226c7250e916573c21cfe234b05ffc** directly follows **646c88526c40b6e19e44d946432ee23bd132ac06**. Its tree **43e6ab3a3a2c9382a92202b19c24d6c3807948d0** equals the locally tested checkpoint. GitHub API inspection and native fetch independently confirm the SHA; all 21 changed text-file blobs match, including the carried Day 5 Windows evidence. Existing remote history/assets and all 19 local baseline hashes are preserved. No image, generated dataset/database, environment, Power BI binary, or private history was published; the denied screenshot upload was not retried. Original local commits remain on private `execution/day06-local-history`; do not push archive branches or all branches.

A normal text-only documentation delivery follows this implementation to record verification. No code changed after the 49-test pass; no successful tests/exports/loads were repeated for these notes. The final delivery SHA is supplied after verification. Windows Day 6 M/DAX/page/filter/save/tests remain pending.

## Primary references checked October 11

Microsoft Learn: [measure creation](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures), [DIVIDE](https://learn.microsoft.com/en-us/dax/divide-function-dax), [COALESCE](https://learn.microsoft.com/en-us/dax/coalesce-function-dax), [SELECTEDVALUE](https://learn.microsoft.com/en-us/dax/selectedvalue-function-dax), [Text/CSV](https://learn.microsoft.com/en-us/power-query/connectors/text-csv), [column types](https://learn.microsoft.com/en-us/powerquery-m/table-transformcolumntypes), [error records](https://learn.microsoft.com/en-us/powerquery-m/error-record), and [visual interactions](https://learn.microsoft.com/en-us/power-bi/create-reports/service-reports-visual-interactions). The fixed date, metric rules, layout, and acceptance values are project decisions, not Microsoft policies.
