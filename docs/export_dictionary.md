# Dashboard export dictionary — Days 5, 9 and 10

Implemented for the fixed **2026-10-07** snapshot. Every value is **simulated**; readiness is a fictional proxy. Source tables and fields remain unchanged. These three derived CSVs are generated locally under `data/processed/dashboard/`, with a successful `export_manifest.json` as the refresh precondition. No database connection driver or new Python dependency is required.

| CSV | Unique grain | Reference rows | Purpose |
| --- | --- | ---: | --- |
| `unit_summary.csv` | `unit_id`, `as_of_date` | 6 | Staffing and qualification components plus cumulative unit expiration counts |
| `qualification_detail.csv` | `unit_id`, `qualification_id`, `as_of_date` | 48 | Every required pair, available holders, capped coverage, gap, fragility |
| `expiration_detail.csv` | `person_id`, `qualification_id`, `as_of_date` | 193 | All currently valid certificates, including unavailable people |

`data_classification` is Text, always `synthetic_only`; `as_of_date` is Date; IDs/names are Text. Counts, day offsets, and 0/1 flags are Whole Number. Coverage ratios are Decimal Number, formatted as Percentage; undefined ratios are blank, not zero. Dates use ISO `YYYY-MM-DD`. Exact headers, grains, row counts, and hashes are recorded in the manifest and `docs/analytics_check.json`.

## Unit summary fields

Shared fields: `data_classification`, `as_of_date`, `unit_id`, `unit_name`.

| Field | Meaning / aggregation rule |
| --- | --- |
| `total_personnel_count` | All people assigned to the current unit; sum across units |
| `available_personnel_count` | People with `is_available = 1`; sum across units |
| `required_personnel_count` | Unit staffing demand; sum across units |
| `staffing_gap` | max(required - available, 0) per unit; sum unit gaps |
| `staffing_coverage_ratio` | available / required; uncapped. For selections, divide summed counts, never average ratios |
| `required_holder_slots` | Sum of required holders across the unit's requirement pairs |
| `capped_holder_slots` | Sum of min(eligible distinct holders, demand) per pair |
| `qualification_coverage_ratio` | capped slots / required slots; divide summed components for selections |
| `qualification_gap` | Sum of missing holder slots; not a missing-person headcount |
| `qualification_pair_count` | Number of required qualification pairs in the unit |
| `qualification_pairs_with_gap` | Number of required pairs with current gap > 0 |
| `fragile_qualification_pairs` | Met pairs with no holder surplus |
| `single_holder_dependency_pairs` | Pairs with one required and one eligible holder |
| `unit_attention_flag` | 1 when staffing gap > 0 OR at least one current qualification pair has a gap; fictional proxy |
| `certificates_expiring_30_days`, `certificates_expiring_60_days`, `certificates_expiring_90_days` | Currently valid certificate rows expiring on/before D + N; cumulative windows |
| `people_affected_30_days`, `people_affected_60_days`, `people_affected_90_days` | Distinct people with at least one certificate in that window, within the unit |

All count components can be summed across disjoint units at this single date; each person belongs to one unit. People counts must be recomputed from expiration detail for qualification filters. The unit summary does not support qualification-specific staffing or holder calculations. Do not sum count components over repeated snapshots or join them to detail rows before aggregating.

## Qualification detail fields

Shared fields: `data_classification`, `as_of_date`, `unit_id`, `unit_name`, `qualification_id`, `qualification_name`.

| Field | Meaning |
| --- | --- |
| `required_holder_count` | Demand for the pair; denominator retained with no holders |
| `valid_available_holder_count` | Distinct available people with `valid_from <= D < expiration_date` |
| `capped_holder_count` | min(holders, required); sum for coverage numerator |
| `current_gap` | max(required - holders, 0); sum missing slots |
| `qualification_coverage_ratio` | capped / required; recalculate from counts for selections |
| `is_fragile` | 1 when holders = required and required > 0 |
| `is_single_holder_dependency` | 1 when holders = required = 1 |

Holder counts across different qualifications may count the same person several times. This is correct for qualification-slot coverage but does not give unique people or simultaneous assignment capacity. Projected fields are absent from this unchanged original CSV; Day 10 uses the separate scenario fact below.

## Expiration detail fields

Shared fields: `data_classification`, `as_of_date`, `unit_id`, `unit_name`, `person_id`, `qualification_id`, `qualification_name`.

| Field | Type / meaning |
| --- | --- |
| `is_available` | Whole Number 0/1, current snapshot availability; both values included |
| `valid_from` | Date, certificate activation; on/before D for every exported row |
| `expiration_date` | Date, exclusive validity end; after D for every exported row |
| `days_until_expiration` | Whole Number calendar days from D to expiration; positive |
| `expires_within_30_days`, `expires_within_60_days`, `expires_within_90_days` | Whole Number 0/1, expiration <= D + N; inclusive and cumulative |

Count rows for certificates and distinct `person_id` for affected people after selection. Never add the three window totals. Expired and future-start certificates stay in the source database but are absent from this current inventory.

## Manifest and next build

The manifest requires `status = passed`, `exit_code = 0`, `exports_ready = true`, the expected fixed date, and matching hashes for the three CSVs. It also records source-table reconciliation and the logical data digest. A failed rerun disables the manifest; old CSVs alone are not refresh authorization. A power interruption can leave replacement incomplete, so rerun after resolving the error.

Day 6/7 executive displayed reconciliation and prototype acceptance are verified from screenshots and user explanation; actual PBIX/installed definitions remain uninspected. Day 8 uses these existing detail exports through three new queries and shared unit/qualification filters in `docs/day08_windows_handoff.md`. Counts/grains/schemas are unchanged. Run `src/check_powerbi_input.py` before every import/refresh; M checks manifest/shape/date/types/grain/value consistency but does not hash. The qualification/expiration page is accepted from October 17 evidence. Its original CSV fields remain unchanged; process outputs use the separate bundle below, and no-renewal fields use the separate Day 10 bundle below.

## Day 9 separate process bundle

`src/export_process_metrics.py` writes only `data/processed/dashboard/process/` by default. Its `process_export_manifest.json` has bundle_kind process, passed/ready/exit 0, fixed as_of_date and period_start, source/database and SQL reconciliation, two CSV hashes/schemas/grains, and global case-level metrics. It does not replace the original three CSVs or export_manifest.json. `src/check_process_input.py` verifies both process files, semantic lifecycle/duration rules, unit summaries, and global components with zero writes. M independently gates the pinned reference shape/types/date/grain/values; it does not hash.

| CSV | Grain | Reference shape | Use |
| --- | --- | --- | --- |
| process_case_detail.csv | case_id, as_of_date | 600 rows / 16 columns | Power BI case fact; selected rates and medians recomputed from eligible rows |
| process_unit_summary.csv | unit_id, as_of_date | 6 rows / 14 columns | SQL reconciliation reference only; preserves zero-case units; do not import or aggregate its medians |

Case detail fields in exact order:

| Field | Type / rule |
| --- | --- |
| data_classification | Text, synthetic_only |
| as_of_date; period_start | Date, October 7 and July 10, 2026 |
| case_id; unit_id; unit_name; case_type | Nonempty Text; unique case grain and matching unit label |
| opened_date | Date, on/before D; older openings retained |
| closed_date | Nullable Date; actual completion on/before D, otherwise blank, including source completions after D |
| correction_required | Nullable Whole Number; known completed 0/1; open-at-D unknown stays blank |
| status_at_as_of | Text, Completed or Open at D; independent of whether completion lies in the reporting window |
| opened_in_period | Whole Number 0/1; opening in the inclusive 90-day period |
| completed_in_period | Whole Number 0/1; completion in the same inclusive period |
| open_at_as_of | Whole Number 0/1; no completion on/before D, regardless of opening-period membership |
| completed_cycle_days | Nullable Whole Number; closed-opened calendar days only for eligible period completions; same-day 0 |
| open_age_days | Nullable Whole Number; D-opened only for cases open at D; completed rows blank |

The summary starts data_classification, as_of_date, period_start, unit_id, unit_name, followed by known_case_count, opened_case_count, completed_case_count, correction_case_count, discrepancy_rate, median_completed_cycle_days, open_case_count, median_open_age_days, max_open_age_days. Counts sum over disjoint units; known_case_count counts all cases opened by D and is a reconciliation field rather than the opening-volume denominator. Rates and medians must be recomputed from the case population for selections. The median can be fractional even though every case duration is an integer. Zero denominators/no observations are blank; counts are zero.

Open outcomes are not no-correction outcomes. Older completed cases outside the completion period can retain known outcomes/status but have completed_in_period 0 and completed_cycle_days blank. Future source outcomes are masked at D. A single-date source snapshot plus administrative cases establishes process outcomes only; it does not reconstruct historical staffing/readiness.

## Day 10 separate no-renewal scenario bundle

Default output: data/processed/dashboard/scenario/. Its scenario_export_manifest.json requires passed/ready/exit 0, bundle_kind qualification_scenario, scenario no_renewal, fixed date, horizons 30/60/90, the declared fixed-cohort assumptions, source/database reconciliation, both file schemas/grains/hashes and per-horizon global components. A failed CLI rerun disables refresh authorization. Original and process bundles remain unchanged.

| CSV | Unique grain | Reference shape | Use |
| --- | --- | --- | --- |
| qualification_scenario.csv | unit_id, qualification_id, horizon_days, as_of_date | 144 rows / 25 columns | Report fact: 48 requirements at each of three alternative horizons |
| scenario_unit_summary.csv | unit_id, horizon_days, as_of_date | 18 rows / 24 columns | SQL reference only; do not import as a second fact |

Shared metadata in exact detail order: data_classification (Text, synthetic_only); scenario (Text, no_renewal); as_of_date (Date); horizon_days (Whole Number 30/60/90); horizon_date (Date, D+N); unit_id, unit_name, qualification_id, qualification_name (Text). Remaining fields in exact order:

| Field | Type / rule |
| --- | --- |
| required_holder_count | Whole Number; fixed pair requirement, repeated for each alternative horizon |
| current_eligible_holder_count | Whole Number; distinct available/currently-valid holders at D |
| projected_eligible_holder_count | Whole Number; only the current cohort's certificates with expiration_date > horizon_date |
| eligible_holders_lost | Whole Number; current eligible minus projected eligible, per pair |
| current_capped_holder_count | Whole Number; min(current eligible, required) |
| projected_capped_holder_count | Whole Number; min(projected eligible, required) |
| current_gap | Whole Number; max(required - current eligible, 0) |
| projected_gap | Whole Number; max(required - projected eligible, 0) |
| additional_gap | Whole Number; projected_gap - current_gap, never negative under these rules |
| current_coverage_ratio | Decimal Number; current capped / required; NULL/blank if undefined |
| projected_coverage_ratio | Decimal Number; projected capped / required; NULL/blank if undefined |
| current_is_gap | Whole Number 0/1; current_gap > 0 |
| projected_is_gap | Whole Number 0/1; projected_gap > 0 |
| is_new_gap | Whole Number 0/1; current_gap = 0 and projected_gap > 0; an existing gap worsening is not new |
| current_is_fragile | Whole Number 0/1; current holders = required > 0 |
| projected_is_fragile | Whole Number 0/1; projected holders = required > 0 |

A holder can contribute to several qualification pairs. Summed eligible losses are holder slots, not unique people, and need not equal missing required slots. Staffing, units, demand and availability are fixed; renewals and future-start activations are excluded. November 6/day 30 is invalid at that horizon and removed. No predicted renewal probability or actual future staffing outcome is present.

Summary metadata is data_classification, scenario, as_of_date, horizon_days, horizon_date, unit_id, unit_name, followed by qualification_pair_count, required_holder_slots, current_eligible_holder_slots, projected_eligible_holder_slots, eligible_holder_slots_lost, current_capped_holder_slots, projected_capped_holder_slots, current_gap, projected_gap, additional_gap, current_pairs_with_gap, projected_pairs_with_gap, new_gap_pairs, current_fragile_pairs, projected_fragile_pairs, current_coverage_ratio, projected_coverage_ratio. Counts sum over disjoint pairs within one selected horizon; divide summed capped/required slots for coverage. **Never sum alternative horizons**, which repeat demand/current components.

scenario_horizon is a derived three-row/two-column lookup (Whole Number horizon_days, Text horizon_label), not a new operational source. The seventeen ORI S measures require one horizon; absent/ambiguous horizons show blanks and a selection prompt. With one valid horizon and no matching pairs, counts are zero and undefined ratios/dates blank. M checks the current baseline against accepted qualification_detail; Python preflight verifies SHA-256 and scenario arithmetic/grids/monotonicity without writes. Exact runtime behavior remains pending Windows/Desktop evidence; see [handoff](day10_windows_handoff.md), [reconciliation](day10_reconciliation.md) and [audit](scenario_check.json).
