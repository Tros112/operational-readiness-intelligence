# Power BI build index

**Current status, October 20, 2026 — Day 10 Windows/model and core scenario displays accepted; final checks remain.** Day 9 remains complete. Windows 72 tests/OK, repeat/manifest/preservation/preflights, ten Single links, seventeen measures and the displayed global/selected/empty results are accepted. PBIX reopening/function is user-confirmed. The multiple-horizon date card incorrectly retains November 6. The scheduled MVP gate remains open.

## Continue in the same Windows project

Use only the [remaining Day 10 items](../docs/day10_windows_handoff.md#remaining-items-after-the-screenshot-review): use existing ORI S Horizon Date in the date card, clarify the holder-slot-loss label, finish no/multiple-horizon date behavior, A+C/Q01+Q02 at 90, both actual data-row interactions, final default restoration/save and three own explanations. Preserve the report/interpreter/data and all earlier pages/measures. Accepted setup/export/tests/reopening and report cases need no repeat.

The retained build specification is 144/25 qualification_scenario and 3/2 scenario_horizon, three new active 1:* Single links (ten total), seventeen ORI S measures and one selected horizon. Relationship/measure-list and runtime value evidence are accepted; exact imported type metadata/installed definitions were not directly inspected, with no new proof gate added. Compare [exact references](../docs/day10_reconciliation.md). Only the new scenario fact/derived selector are imported; scenario_unit_summary stays SQL reference-only. Do not start Day 11 before Day 10 completion.

Prepared scenario assets: [qualification_scenario.pq](qualification_scenario.pq), [scenario_horizon.pq](scenario_horizon.pq), and [scenario_measures.dax](scenario_measures.dax). Default to single-select 30 days. All numerical/date results require one horizon; a valid horizon with no matching pairs gives zero counts/blank ratios-dates. Both table sources use None; slicers use Filter. Current baseline M checks refer to accepted qualification_detail without a fact-to-fact model link.

Run all three Python input checkers immediately before import/refresh; they verify hashes without writes. M checks shape/types/date/grain/assumptions/arithmetic and does not hash. Keep files stable; a failed refresh can retain cached results. Slicers remain page-local/unsynced and lookup relationships Single.

## Completed and preserved references

- [Day 9 handoff](../docs/day09_windows_handoff.md), [reconciliation](../docs/day09_reconciliation.md), and [completion checkpoint](../docs/checkpoints/2026-10-19_day09.md): accepted process reporting and all three own explanations.

- [Day 8 handoff](../docs/day08_windows_handoff.md), [reconciliation](../docs/day08_reconciliation.md), and [completion checkpoint](../docs/checkpoints/2026-10-17_day08.md): accepted qualification/expiration page and own explanations.
- [Day 6 handoff](../docs/day06_windows_handoff.md), [unit_summary.pq](unit_summary.pq), and [executive_measures.dax](executive_measures.dax): accepted executive page at October 7.
- [Prototype checkpoint](../docs/checkpoints/2026-10-12_day07.md): accepted short explanation/prototype gate.
- [Original learning reference](day02_staffing_review.md): retained units/personnel model.
- [Export dictionary](../docs/export_dictionary.md): original and separate process schemas/grains.
- [SQL review](../docs/sql_review_backlog.md): remaining LEFT JOIN/staffing row-multiplication learning.

The no-renewal scenario has matching core Desktop displays and remains pending its final report/own-explanation checks. Cloud publishing and ML remain outside this milestone. Fixed date, six operational sources, synthetic/fictional scope, and SQLite/CSV transport are unchanged.
