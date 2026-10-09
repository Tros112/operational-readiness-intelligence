# Metric contract

Version 1.0 · Finalized for Day 2 on October 7, 2026 (scheduled October 8; executed early at user request).

All operational measures describe a **fictional simulation**. The definitions below govern generation checks and the future analytical SQL/Power BI implementation. Clean-reference verification does not complete the dashboard or metric-reconciliation gate.

## Shared date and eligibility rules

- `D = config/project.yml: as_of_date`, initially **2026-10-07**. Use this explicit value; do not use the computer's current date inside metrics.
- Dates are calendar dates encoded as ISO `YYYY-MM-DD`. Certificate eligibility is `valid_from <= D AND D < expiration_date`: expiration takes effect at the start of the expiration date.
- Available means the person's current snapshot `is_available = 1`. Each person belongs to exactly one unit. No historical availability is implied.
- Qualification holders must be distinct people for each unit/qualification pair, available and currently valid. Reject duplicate source keys; defensive distinct counting also protects analytical joins.
- A 90-day administrative reporting period is **[D - 89 days, D]**, both endpoints included. Case-open volume uses `opened_date`; completion metrics use `closed_date` in the selected period and `opened_date <= D`.
- Cases opened after D are excluded. Cases with `closed_date IS NULL` or `closed_date > D` are open at D; future outcomes do not enter completion metrics. Clean generation will contain no future actual openings/completions.
- Counts show zero when the eligible set is empty. Ratios and medians with no eligible denominator/observations show SQL NULL and Power BI blank / not applicable. Do not replace an undefined rate with zero.
- Every export carries `as_of_date`. Filters must preserve the same numerator/denominator scope. Aggregate ratios from their counts, not from averages of percentages.
- Raw CSVs keep the six-table source schema; the single analysis date is stored in configuration/manifest. Future dashboard exports include the date explicitly. A missing certificate record means no recorded qualification; it is not a missing-date value to impute.
- Administrative cycle time uses calendar days, without a working-day adjustment. Its selected period applies to completion date, even if the case was opened earlier. The MVP's generated cases all open in the 90-day window, so older backlog is not represented.
- Staffing gap is `max(required_personnel_count - available_personnel_count, 0)` at unit grain. Preserve unit gaps separately from the aggregate uncapped staffing ratio: surplus elsewhere cannot remove a unit's local shortfall.
- Expiration inventory counts all currently valid certificates in the selected unit, including unavailable people; report availability separately when useful. Projected qualification coverage uses available holders only. Do not silently change the expiration denominator to available holders.

## Definitions

| Metric | Grain and calculation | Interpretation / check |
| --- | --- | --- |
| Staffing coverage | Unit: available people / required personnel count. Total: sum(available people) / sum(requirement). | Uncapped; show both counts. Count people before joining certificates. |
| Current qualification holders | Unit/qualification: distinct available people with a currently valid certificate. | Start from requirements and LEFT JOIN holder totals so zero-holder pairs remain visible. |
| Qualification coverage | Pair: capped holders = min(valid available holders, required holders). Selected total: sum(capped holders) / sum(required holders). | Surplus in one qualification cannot offset another's shortage. One person can hold several qualifications. |
| Current gap | Pair: max(required holders - valid available holders, 0). | Show missing holder count and affected pair; units with a gap count once. |
| Fragile coverage | Pair is met and holders = required holders. | No surplus. Separately flag single-holder dependency when both counts are 1. |
| 30/60/90-day expirations | Certificate is currently valid and expiration <= D + N days. Report certificate rows and distinct affected people separately. | Cumulative windows overlap; never sum the three window counts. Include the endpoint; exclude already-expired/future-start certificates. |
| Projected qualification gap | Current eligible cohort minus certificates expiring on/before D + N; recalculate holders, capped coverage, and gaps. | No-renewal scenario with unchanged units/availability and no future certificate activations. A deterministic scenario, not prediction. |
| Completed-case discrepancy rate | Completed cases with correction_required = 1 / all completed cases with closed_date in selected period. | Open/after-D completions have unknown outcomes at D and are excluded. A required correction is this project's discrepancy proxy. |
| Completed-case cycle time | Median of (closed_date - opened_date) calendar days over the same eligible completed cases. | Actual median, not mean or median of unit medians. Same-day completion = 0 days. |
| Open-case backlog / age | Cases opened <= D that are not closed by D; age = D - opened_date. | Current backlog covers all known eligible open cases; age is separate from completed cycle time. |
| Unit attention flag | Staffing below requirement OR at least one current qualification gap. | Fictional readiness proxy, evaluated by unit. Fragile coverage appears separately and does not silently change this rule. |

## Worked checks for ownership

These are tiny teaching fixtures, **not results from the generated dataset**.

1. Staffing: Unit A has 8 available / 10 required and Unit B has 18 / 30. Combined coverage is **26 / 40 = 65%**. The denominator weights the contribution of each unit. Staffing counts must come from personnel grain; joining three certificates to one person must not turn that person into three staff.
2. Qualifications: one pair needs 1 holder and has 3; another needs 3 and has 2. Capped coverage is **(1 + 2) / (1 + 3) = 75%**, with one missing holder in the second pair. Surplus cannot erase that gap.
3. Expiration: at D = October 7, a certificate expiring October 7 is already invalid. A currently valid certificate expiring **November 6** counts in the inclusive 30-day window and is removed in the no-renewal 30-day scenario. November 7 falls outside that window.
4. Discrepancy: 2 corrections among 10 completed cases yields **20%**, regardless of 5 additional open cases. With zero completed cases, the rate is **not applicable**.
5. Median: cycle times [1, 2, 10] have median **2 days**. Combining unit-level medians would lose case-level information.

Ownership evidence, October 8: the user independently explained aggregate versus local staffing by identifying the 14-person combined surplus in A/B/D/E and the persistent 10-person shortfall in C. This specific explanation is confirmed. Staffing grain/join counting, the exclusive expiration boundary, and treatment of open cases remain to be explained independently.

## Derived output grains (planned)

| Output | Grain | Rule |
| --- | --- | --- |
| Executive unit summary | One unit at D | Staffing totals and summed qualification slots share unit scope; sum count components across units |
| Qualification detail | One unit/qualification at D | All 48 requirements retained, including zero holders; current holders, gaps, fragile flag, and projected horizons |
| Expiration detail | One current valid person/qualification certificate at D | Distinct affected people must be recomputed for the selection, not summed across qualifications |
| Process case detail | One case eligible as of D | Completion/age/calendar-period filters applied before rates or median |

These are derived marts scheduled for later milestones. No extra operational source table is added. Source rows and dashboard tables must not be mixed in joins that multiply counts.

## Day 2 completion check

Definitions and output grains are fixed above. Generator verification must check source grain, key/date integrity, and the documented scenarios. Later checks reconcile the same eligible record sets and counts across SQL and Power BI, including filtered units and empty selections. Aggregate versus local staffing ownership is confirmed; remaining explanations are pending. Implementation definitions alone are not evidence of independent understanding.

## Day 3 integrity enforcement

Implemented October 8 under the early Day 3 instruction. `docs/validation_rules.md` governs source acceptance and whole-batch blocking. Duplicate versions, invalid parents/children, missing critical values, invalid calendars/lifecycles, flags/counts, and missing requirement pairs block loading. Valid expired/future-start certificates and future case dates remain source records; the eligibility rules above still determine metric inclusion. Clean/dirty validation evidence is in `docs/verification_day03.md`. Metric definitions and output grains are unchanged; no analytical SQL/Power BI reconciliation is claimed by source validation.
