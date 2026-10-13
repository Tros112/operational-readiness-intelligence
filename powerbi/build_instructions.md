# Power BI build index

**Current status, October 13, 2026 — Day 8:** the executive prototype gate passed October 12. Qualification/expiration import queries, measures, model and page/reconciliation instructions are prepared. The local execution environment is unavailable, and the new M/DAX/PowerShell/Desktop build remains pending. Prior 49-test Python evidence stays recorded; no Python/SQL/test change is made. The assistant has not operated or inspected an actual PBIX.

## Continue in the same Windows project

Use [day08_windows_handoff.md](../docs/day08_windows_handoff.md). Retain the existing interpreter, exports/database, working PBIX, and original learning report.

1. Pull the verified update and run `src/check_powerbi_input.py` before import/refresh.
2. Add `qualification_detail` (48 rows/13 columns), `qualification_filter` (8/2), and `expiration_detail` (193/14) using their same-named .pq files.
3. Configure the four active 1:* Single relationships in the guide. Unit and qualification lookup selections reach both detail tables; the facts are not joined together.
4. Create sixteen ORI Q measures from [qualification_measures.dax](qualification_measures.dax), one at a time.
5. Build **Qualification — simulated**, then reconcile current slots/gaps/fragility, distinct inventory people, and overlapping 30/60/90 windows.
6. Check selected units/qualifications, clear/empty behavior, the November 6 endpoint, and report save/reopen including prior pages. Return evidence before claiming Day 8 complete.

The M imports check approved manifest/schema/types/date/grains and values. Python preflight supplies file hashes; keep inputs stable between it and import/refresh. Failed refreshes can leave cached values visible.

## Completed and preserved references

- [day06_windows_handoff.md](../docs/day06_windows_handoff.md), [unit_summary.pq](unit_summary.pq), and [executive_measures.dax](executive_measures.dax): accepted executive page at October 7; original ORI definitions stay intact.
- [day07_windows_handoff.md](../docs/day07_windows_handoff.md), [verification_day07.md](../docs/verification_day07.md), and [prototype checkpoint](../docs/checkpoints/2026-10-12_day07.md): accepted short explanation and prototype gate.
- [day02_staffing_review.md](day02_staffing_review.md): original learning report/relationship reference.
- [day08_reconciliation.md](../docs/day08_reconciliation.md): known SQL counts and a read-only selected-CSV reference.
- [export_dictionary.md](../docs/export_dictionary.md): unchanged input schemas, types, and grains.
- [sql_review_backlog.md](../docs/sql_review_backlog.md): carried independent join/grain/fragility learning items.

Day 8 reuses the six-row unit_summary as the unit lookup for new facts; it remains independent of the older raw units/personnel learning model. Use qualification_filter for the new qualification slicer and ORI Q formulas for qualification-specific calculations. Fixed date and fictional readiness rules stay unchanged. No Power BI cloud publishing, process view, or no-renewal scenario is included in this milestone.
