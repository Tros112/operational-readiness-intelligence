# Power BI build index

**Current status, October 11, 2026 — Day 6:** the user requested the executive page. Day 5 Windows technical reproduction is complete; SQL ownership review is carried forward. The assistant prepared the import query, eleven ORI measures, input check, and page/reconciliation steps. Actual Desktop import, DAX/M execution, filters, and report save/reopen remain pending. No PBIX has been created or inspected by the assistant.

## Continue in the existing project

Use [day06_windows_handoff.md](../docs/day06_windows_handoff.md) as the complete guide. Its first action pulls into the same Windows checkout and checks all three saved CSV hashes with the existing interpreter. It does not regenerate/reload data or replace the environment.

1. Run `src/check_powerbi_input.py` before import/refresh.
2. Open the existing learning report and save a working copy under an unused filename.
3. Add a new Executive — simulated page. Keep earlier pages/measures/relationships intact.
4. Import the disconnected `unit_summary` table with [unit_summary.pq](unit_summary.pq), changing only the local ProjectRoot value in Power Query.
5. Create the eleven ORI-prefixed measures one at a time from [executive_measures.dax](executive_measures.dax).
6. Build the cards, unit-name slicer, and comparison table; verify global, Unit C, Unit A, multi-unit, clear-filter, and empty-filter behavior.
7. Save/reopen and return evidence. No Power BI cloud publishing is part of this milestone.

The M query gates manifest state, schema, types, fixed date, and unique six-row grain. It does not calculate SHA-256: the Python prerequisite checks all three file hashes before every refresh. Keep files stable between the check and refresh. A failed refresh can leave cached prior BI values visible, which does not establish a successful new refresh.

## Reference values — synthetic, not observed BI results

| Selection | Available / required | Staffing coverage | Local staffing gap | Qualification coverage | Missing slots | Units with gaps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| All units | 254 / 250 | 101.6% | 10 | 92.63% | 7 | 4 |
| Unit C | 40 / 50 | 80.0% | 10 | 93.75% | 1 | 1 |
| Unit A | 41 / 40 | 102.5% | 0 | 100.00% | 0 | 0 |
| Unit A + C | 81 / 90 | 90.0% | 10 | 96.88% | 1 | 1 |

Metric date: October 7, 2026. The unit flag is a fictional current-gap proxy; it does not include fragile-but-met coverage or upcoming expirations. Coverage does not establish simultaneous assignment capacity.

## Preserved access and learning evidence

Power BI Desktop 2.158.1177.0, 64-bit (September 2026), is user-confirmed. Day 1 blank-report access/save/reopen was confirmed October 7. Day 2 staffing screenshots and user explanation showed the expected global and Unit C results and active Single units-to-personnel relationship; report save/reopen was user-confirmed. The user confirmed that learning report still worked at Day 4 closure.

The original learning guide remains [day02_staffing_review.md](day02_staffing_review.md). Day 6's new measures and slicer use `unit_summary`; the old source-table slicer should not be reused on the disconnected executive page. No assistant inspection of the actual PBIX is inferred from screenshots or reported availability.

Current preparation evidence and pending items: [verification_day06.md](../docs/verification_day06.md). Definition/reference fields: [export_dictionary.md](../docs/export_dictionary.md). Carried ownership review: [sql_review_backlog.md](../docs/sql_review_backlog.md).
