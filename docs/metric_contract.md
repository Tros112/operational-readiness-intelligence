# Metric contract outline

Version 0.1 · Day 1 outline; finalize on Day 2 before generating data.

All measures describe a **fictional simulation**. No measures have been calculated from project data yet. The definitions below govern the future SQL and Power BI implementations.

## Shared date and eligibility rules

- `D = config/project.yml: as_of_date`, initially **2026-10-07**. Use this explicit value; do not use the computer's current date inside metrics.
- Dates are calendar dates encoded as ISO `YYYY-MM-DD`. Certificate eligibility is `valid_from <= D AND D < expiration_date`: expiration takes effect at the start of the expiration date.
- Available means the person's current snapshot `is_available = 1`. Each person belongs to exactly one unit. No historical availability is implied.
- Qualification holders must be distinct people for each unit/qualification pair, available and currently valid. Reject duplicate source keys; defensive distinct counting also protects analytical joins.
- A 90-day administrative reporting period is **[D - 89 days, D]**, both endpoints included. Case-open volume uses `opened_date`; completion metrics use `closed_date` in the selected period and `opened_date <= D`.
- Cases opened after D are excluded. Cases with `closed_date IS NULL` or `closed_date > D` are open at D; future outcomes do not enter completion metrics. Clean generation will contain no future actual openings/completions.
- Counts show zero when the eligible set is empty. Ratios and medians with no eligible denominator/observations show SQL NULL and Power BI blank / not applicable. Do not replace an undefined rate with zero.
- Every export carries `as_of_date`. Filters must preserve the same numerator/denominator scope. Aggregate ratios from their counts, not from averages of percentages.

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

Owner check pending: explain the staffing denominator, exclusive expiration boundary, and treatment of open cases in your own words. No independent understanding has yet been confirmed.

## Day 2 completion check

Confirm these definitions and the export grains before writing the generator. Record any clarification in decisions. Later checks must reconcile the same eligible record sets and counts across SQL and Power BI, including filtered units and empty selections.
