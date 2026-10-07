# Explain the generator in your own words

Day 2 · All examples and outcomes are simulated. Review this alongside `src/generate_data.py` and `config/project.yml`; generated prose alone does not establish interview ownership.

## What you can accurately say now

"I'm developing a reproducible synthetic operations dataset with six related tables. The current generator uses configuration for dates, sizes, and scenario assumptions. Eight checks verify keys, relationships, dates, scenarios, and identical output from separate runs. Dirty-input validation, dashboard marts, and the operational Power BI report are the next implementation stages."

This describes the current implementation; it is not a claim of production experience. Describe your personal contribution and local checks according to what you actually reviewed, changed, or ran. Independent explanations are still pending.

## Follow the code

1. `generate_tables()` checks configuration, creates `np.random.default_rng(seed)`, and passes that local generator through the functions. A seed lets the same code/configuration/dependency versions reproduce the same draws. Changing call order or code can change output, so the manifest also hashes the generator/configuration and records versions.
2. `make_personnel()` creates 50 people per unit with invented IDs. It draws availability, then applies the documented Unit C override and other-unit minimums. The final availability distribution is deliberately constructed; it is not a Navy staffing estimate.
3. `make_certificates()` draws recorded qualifications and valid/expired/future-start dates. The dictionary key `(person_id, qualification_id)` maintains one source record per pair. It then replaces the two targeted unit/qualification groups with their explicit scenarios. Selected people are available and sampled without replacement.
4. The requirement table is the full six-unit/eight-qualification cross product. It exists separately from certificate observations, so a qualification can still be required when no one holds it. Later SQL must start from requirements and preserve zero-holder pairs.
5. `make_cases()` picks fictional units/types and dates in the 90-day window. A candidate completion after D stays open. It samples the correction outcome only when completed by D. Open outcomes remain unknown. The Unit F scenario changes the probability; it does not force the realized rate to exactly 30%.
6. `write_tables()` sorts keys and writes CSVs without a dataframe index. The nullable integer outcome column writes 0/1 or blank, never decimal flags or a manufactured zero. The manifest has no wall-clock timestamp, allowing identical metadata bytes across repeat runs in this environment.

## Three calculations to understand

**Staffing:** Unit C has 40 available / 50 required = **80%**, a local gap of 10. Across all units, 254 / 250 = **101.6%**. The aggregate ratio does not authorize moving staff between units or erase Unit C's local gap. The dashboard must retain unit-level results alongside the total.

**Qualifications:** Unit B/Q03 has 1 valid available holder / 1 required. Coverage is met, but there is no spare holder. Unit D/Q04 has 6 / 2, but its capped contribution is only 2 / 2. If no renewals occur, all six expire by November 6, leaving 0 / 2 and a gap of 2 at day 30. This is a rule-based scenario, not an ML prediction.

**Process discrepancy:** Unit F has 27 corrections / 70 completed = **38.6%**. Its 28 open cases are excluded from that denominator because their outcomes are unknown. The configured probability was 30%; a finite random sample can realize another rate. This planted pattern demonstrates calculation behavior, not real operational causes.

## Why grain matters

If one available person has three certificates, joining personnel to certificates produces three joined rows for that person. Staffing must aggregate at person grain before that join, or count distinct person IDs within the correctly filtered unit. Qualification counts are per person/qualification pair; the same person can legitimately count for multiple qualifications. Neither measure establishes simultaneous assignment capacity.

## Try these checks without reading the answers

- Explain why the overall staffing ratio can exceed 100% while Unit C is short 10 people.
- A certificate expires November 6. At D = October 7, is it in the 30-day expiration window, and does it survive the no-renewal day-30 scenario?
- Why is an open case's correction flag blank instead of 0?
- Which function applies a planted scenario, and which checks would catch a broken foreign key or duplicate key?

Owner answers are still pending. No ML label or professional implementation claim follows from passing the generator checks.
