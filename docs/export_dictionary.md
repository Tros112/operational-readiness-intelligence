# Day 5 dashboard export dictionary

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

Holder counts across different qualifications may count the same person several times. This is correct for qualification-slot coverage but does not give unique people or simultaneous assignment capacity. Projected horizon holder/gap fields are not present; they remain Day 10.

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

Day 6 starts with the unit summary for the executive page. Relationships to qualification/expiration detail should be built only when those views are requested; joining every source/detail table is unnecessary for the first summary page. No Power BI file or SQL/Power BI reconciliation has been verified by the assistant.
