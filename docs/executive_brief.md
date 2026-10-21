# Operational Readiness Intelligence — executive brief

**Synthetic portfolio prototype · snapshot October 7, 2026 · brief prepared October 20.** Audience: a fictional operations manager deciding where to review staffing, qualification coverage and administrative processes. Python validates six source tables, SQLite calculates the metrics, and Power BI displays accepted comparisons. These are fictional rules and planted scenarios, with no real deployment or measured impact.

## Decision context

Global staffing is **254 available / 250 required = 101.6%**, while Unit C is **40/50**, ten people short. Staffing surplus also does not establish qualification coverage: Unit D has **47/40 = 117.5%** staffing but **14/16 = 87.5%** capped qualification coverage. Global qualification coverage is **88/95 = 92.63%**, with seven required holder slots missing. [Staffing/current-qualification SQL](../sql/unit_summary.sql), [metric definitions](metric_contract.md) and [accepted report evidence](verification_day06.md) provide the trace.

## Five proposed reviews

The sequence supports discussion; it is not an optimized or official mission-priority ranking. Every action below is proposed, not performed.

| Review | Observed simulated evidence | Proposed action | What remains unproven |
| --- | --- | --- | --- |
| Unit C staffing allocation | 40 available for 50 required; local gap **10** despite the global surplus. [SQL](../sql/unit_summary.sql) | Review demand, availability and feasible staffing options at the unit level. | Staff elsewhere may lack the right skills or transfer authority; adding headcount has not been shown to resolve particular qualification gaps. |
| C/Q06 current and additional qualification gap | One eligible holder for two required: current gap **1**. With no renewal at 30 days, holders fall to zero: projected gap **2**, additional **1**, new-pair flag **0**. [Reconciliation](day10_reconciliation.md#required-selected-pair-checks) | Review current backup coverage and the approaching certificate expiry as two distinct issues. | An unavailable certificate holder's renewal ability or intent is unknown; no additional eligible holder or simultaneous assignment capacity is established. |
| D/Q04 clustered renewal exposure | Six eligible holders for two required; all six expire by November 6, including day 30. No renewal leaves **2** missing slots and **1** newly affected pair. [SQL](../sql/qualification_scenario.sql) | Review the clustered dates and options to maintain the two required eligible slots. | This cluster was planted. Renewal feasibility, scheduling, actual renewals and resulting operational benefit are untested. |
| B/Q03 backup dependency | One eligible holder for one required; coverage **100%**, gap **0**, fragile flag **1**. That holder survives all three scenario horizons. [Evidence](day10_reconciliation.md#required-selected-pair-checks) | Review whether backup qualification coverage is warranted under the fictional requirement. | Fragility is not an observed outage or projected gap here. Training capacity, skill criticality and the benefit of a second holder are not estimated. |
| Unit F administrative process | **27/70 = 38.57%** of eligible completed cases require correction, versus **18/372 = 4.84%** elsewhere. [Case-level SQL](../sql/process_case_detail.sql), [selected references](day09_reconciliation.md) | Review case samples and workflow before proposing a targeted process change. | The higher correction probability was intentionally generated. The comparison establishes no real cause, employee performance judgment or demonstrated improvement. |

## Scenario interpretation and limits

With no renewals, a frozen October 7 eligible cohort and fixed units/staffing/availability/demand, qualification coverage becomes **85.26%, 82.11% and 70.53%** at 30/60/90 days. The 90-day total gap **28** contains today's **7** plus **21 additional** slots; **90 lost holder slots** can count one person across qualifications. [Scenario evidence](day10_findings.md) supports these conditional calculations. It does not predict actual renewals, official operational severity, downsizing effects or simultaneous assignments.

All report checks and Day 10 explanations are accepted. Day 11 adds reproducibility instructions and this brief; the fresh-checkout/demo/backup release evidence remains for Day 12 and the separately open MVP gate. Read the [limitations](limitations.md) and [runbook](reproduce.md) before using or reproducing the prototype. Actual employer feedback, focused hours and real-world outcomes are unreported.
