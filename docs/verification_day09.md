# Day 9 verification — implementation and Windows handoff

Day 9 started October 17, 2026 at 11:36 PDT under the user's instruction. Source schedule was October 15; dates/audience/synthetic scope remain unchanged. Day 8 is complete. **Day 9 is not complete:** Windows reproduction and the process page remain pending.

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
