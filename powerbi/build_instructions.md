# Power BI build index

**Current status, October 17, 2026 — Day 9:** executive/qualification pages and the prototype are accepted. Process SQL/export/preflight and the full 60-test Linux suite pass; Windows reproduction and the new process M/DAX/model/page are pending. The assistant has not operated an actual PBIX.

## Continue in the same Windows project

Use [day09_windows_handoff.md](../docs/day09_windows_handoff.md) and [day09_reconciliation.md](../docs/day09_reconciliation.md). Retain the existing interpreter, source/bundle/database, working PBIX, and original learning report.

1. Pull the verified update; run the changed 60-test suite and separate process repeat/preservation/preflight block in sections 1–2.
2. Add [process_case_detail.pq](process_case_detail.pq) as process_case_detail (600/16) and [process_filter.pq](process_filter.pq) as process_filter (4/1). Do not import the SQL unit-median summary.
3. Add two active 1:* Single links: unit_summary to process case detail on unit_id, and process_filter to case detail on case_type. Preserve the prior five links.
4. Create ten ORI P measures from [process_measures.dax](process_measures.dax), one at a time. Counts/rates/medians use case rows; prior ORI/ORI Q measures remain unchanged.
5. Build Process — simulated, then reconcile global/F/type/multi/clear, Open-only zero denominator, full empty scope, table selections, and save/reopen old/new pages. Return evidence before claiming Day 9 complete.

Run both Python input checkers immediately before import/refresh; they verify hashes without writing. M checks shape/types/date/grain/lifecycle and does not hash. Keep files stable; a failed refresh can retain cached results. Slicers stay page-local/unsynced, lookup relationships Single, and table-source interactions None.

## Completed and preserved references

- [Day 8 handoff](../docs/day08_windows_handoff.md), [reconciliation](../docs/day08_reconciliation.md), and [completion checkpoint](../docs/checkpoints/2026-10-17_day08.md): accepted qualification/expiration page and own explanations.
- [Day 6 handoff](../docs/day06_windows_handoff.md), [unit_summary.pq](unit_summary.pq), and [executive_measures.dax](executive_measures.dax): accepted executive page at October 7.
- [Prototype checkpoint](../docs/checkpoints/2026-10-12_day07.md): accepted short explanation/prototype gate.
- [Original learning reference](day02_staffing_review.md): retained units/personnel model.
- [Export dictionary](../docs/export_dictionary.md): original and separate process schemas/grains.
- [SQL review](../docs/sql_review_backlog.md): remaining LEFT JOIN/staffing row-multiplication learning.

No no-renewal scenario, cloud publishing, or ML is implemented by Day 9. Dates, six operational sources, synthetic/fictional scope, and SQLite/CSV transport remain unchanged.
