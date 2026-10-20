# Day 9 verification — implementation and Windows handoff

**Current October 19 status:** Windows setup and core Desktop scopes are accepted. Final filter removal/restoration, both table-row tests, reopening and own process explanations remain pending. The initial implementation record below is dated October 17; the final section records the new evidence.

Initial October 17 record: Day 9 started at 11:36 PDT under the user's instruction. Source schedule was October 15; dates/audience/synthetic scope remain unchanged. Day 8 is complete. **Day 9 is not complete:** Windows reproduction and the process page remain pending.

Implemented two SQL queries, a separate read-only process exporter, a no-write hash/grain/lifecycle preflight, eleven process tests, two Power Query imports, ten ORI P measures, a model/page guide, and exact reconciliation references. No source table or existing Python/SQL/M/DAX asset was changed. No new package is required.

## Executed evidence

- Targeted process suite: **11 tests, OK**, 6.112 seconds, exit 0. Full suite: **60 tests, OK**, 17.102 seconds, exit 0. The full run includes all earlier generator/validator/loader/current-metric/preflight tests.
- Exported twice from the existing six-table SQLite snapshot using mode=ro, PRAGMA query_only, and one read transaction per run. Both process CSV SHA-256 values match between runs. Passed process manifests gate both files; a failed rerun cannot leave a passed manifest.
- Actual process outputs: 600 unique cases/16 columns and six unique unit summaries/14 columns. Global 600 opened, 442 completed, 45 corrections, 45/442=10.18%, median completed cycle 7.0 days, 158 open, median open age 27.0, oldest 88. Date October 7; period start July 10.
- SQL totals and every detail field reconcile against independent source-calendar calculations. Unit F is 27/70=38.57%; other units 18/372=4.84%. SQL multi-selection A+F/onboarding+transfer matches the independent selected-case reference: 86 opened, 57 completed, 14 corrections, 24.56%, median cycle 7.0, open 29, median age 35.0, oldest 84.
- Both the new process preflight and existing three-file preflight pass. Before/after SHA-256 comparison covers **21 existing files**, including database, raw clean files, accepted validation bundle, old three dashboard CSVs and their manifest; every hash is unchanged. Only the separate new process output folder is written. Generated data/DB/manifests remain excluded from publication.
- Isolated tests cover inclusive opening/completion dates, older backlog, future openings, future completion/outcome masking, same-day zero, odd/even/combined medians, no eligible completions, empty units/selections, safe bound filters, blocked/changed/missing inputs, protected folders/report-file sentinel, repeat/preservation, interrupted replacement, and hash/semantic tampering. Test fixtures are not synthetic-reference findings.

## Prepared, not executed

M checks the approved 600-row schema/grain/date/unit labels, integer values before Int64 conversion, null outcomes, status/flags, and calendar durations. process_filter derives four case types from that fact without a new operational source. Ten ORI P measures sum flags, divide matched completed-cohort counts, and use MEDIAN on nullable case-level duration columns. The SQL per-unit medians are reference-only and are not imported.

Windows PowerShell, M/DAX, model relationships, visual results, filter/interactions, reopening, and process ownership have not been executed/established here. User builds the Desktop page. The handoff retains old reports and adds only two 1:* Single lookup links. Exact prepared-asset consistency checks are recorded in process_check.json; they are not Desktop execution. Official SQLite window/read-only and Microsoft MEDIAN/KEEPFILTERS documentation informs implementation; it does not prove project outputs.

No new event attendance, employer feedback, focused hours, MVP/polish pass, or Day 10 scenario is claimed. Resume wording may describe verified process SQL; a finished process dashboard is still pending. First next action: [Windows handoff](day09_windows_handoff.md) sections 1–2, returning the 60-test summary, repeat/preservation results, and passed process checker before import/model review.

## October 19, 19:55 PDT — setup evidence and core Desktop cases accepted

Read all nine current attachments directly from scratch. Recover/read eight earlier October 17 user screenshots to close the unrecorded setup state instead of requesting repetition. Files were not changed or published; only text evidence/status is updated.

Earlier setup evidence:

| Image | Observation / acceptance |
| --- | --- |
| image(20261017-185858).png | Windows terminal shows Ran 60 tests in 44.115s / OK. Count/duration are visually verified. Separate exit-code line is not visible. |
| image(20261017-185937).png | Process checker passed: files_checked 2, rows 600/6, output grains unique, semantics/unit totals match, file_writes 0. Both CSV repeat/manifest comparisons True; database and prior dashboard bundle preserved True. |
| image(20261017-190522).png; image(20261017-190615).png | Process query, expected date/classification/labels, nullable open outcomes, date/text/whole-number icons. Final scrolled preview shows 600 rows/16 columns; the earlier 99+ preview is not treated as its final row total. |
| image(20261017-190632).png | Four-row/one-column text lookup: evaluation, onboarding, records_update, transfer. |
| image(20261017-190937).png; image(20261017-191035).png | Exactly seven active 1:* Single relationships: the two intended process links plus the five preserved prior links. No unintended fact link or Both direction observed. |
| image(20261017-191400).png | Ten ORI P measures with calculator icons in the process fact. Exact full installed formulas are not inspected. |

Current displayed cases, all reconciled at shown precision:

| Image | Scope | Opened / completed / corrections | Rate | Median cycle | Open / median age / oldest |
| --- | --- | --- | --- | --- | --- |
| image(20261020-024502).png | Global, with all six comparison rows/totals | 600 / 442 / 45 | 10.18% | 7.0 | 158 / 27.0 / 88 |
| image(20261020-024626).png | Units A–E, F excluded | 502 / 372 / 18 | 4.84% | 7.0 | 130 / 26.0 / 88 |
| image(20261020-024646).png | Unit F only | 98 / 70 / 27 | 38.57% | 7.5 | 28 / 33.0 / 87 |
| image(20261020-024714).png | evaluation only | 161 / 109 / 11 | 10.09% | 8.0 | 52 / 38.5 / 88 |
| image(20261020-024749).png | onboarding only | 148 / 111 / 11 | 9.91% | 7.0 | 37 / 35.0 / 87 |
| image(20261020-024826).png | A+F, all case types | 194 / 141 / 28 | 19.86% | 8.0 | 53 / 35.0 / 87 |
| image(20261020-024906).png | A+F and onboarding+transfer | 86 / 57 / 14 | 24.56% | 7.0 | 29 / 35.0 / 84 |
| image(20261020-025243).png | Basic page filter status_at_as_of is Open | 158 / 0 / 0 | blank | blank | 158 / 27.0 / 88 |
| image(20261020-025342).png | Advanced page filter status_at_as_of is empty | 0 / 0 / 0 | blank | blank | 0 / blank / blank |

All nonempty dates show October 7; the full-empty analysis date is blank. The period caption remains July 10–October 7, with backlog open at October 7. Open-only case rows have blank completion/outcome/cycle fields and known ages. Plain date columns, no raw-case totals, synthetic title, limitation footer and earlier report tabs are visible. The empty test's six unit lookup rows retain zero counts exactly as expected. Accept this equivalent empty condition; a second test with NO_SUCH_PROCESS adds no required evidence.

The final submitted state is still empty. No subsequent filter removal/global restoration is shown. No image shows an actual selected data row in each table; an active visual border is not sufficient. No new save/reopen or own process explanation was supplied. These four groups remain open, with the exact next steps in handoff section 6. Do not repeat setup, 60 tests, export/preflight, model/import, or accepted numeric cases solely for evidence.

This follow-up does not run tests/checkers/exports/pipeline, access/write operational data/DB, change Python/SQL/M/DAX/metrics/scope, operate Power BI, infer event/employer feedback/hours, close Day 9, or start Day 10. The October 19 scheduled MVP status is recorded separately as not yet passed; dates/scope are unchanged.
