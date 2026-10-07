# Data dictionary draft

Day 1 schema draft; update alongside the Day 2 generator. Source dates use ISO `YYYY-MM-DD`; flags use integer 0/1; all identifiers and labels are invented. No data has been generated.

| Table | Fields and meanings |
| --- | --- |
| `units` | `unit_id` TEXT key; `unit_name` TEXT display label; `required_personnel_count` INTEGER positive fictional staffing requirement |
| `personnel` | `person_id` TEXT key; `unit_id` TEXT current unit FK; `is_available` INTEGER snapshot flag (1 available, 0 unavailable) |
| `qualification_types` | `qualification_id` TEXT key; `qualification_name` TEXT fictional label, not an official qualification |
| `personnel_qualifications` | `person_id` and `qualification_id` TEXT FKs/composite key; `valid_from` TEXT inclusive first valid date; `expiration_date` TEXT exclusive first invalid date; both required |
| `unit_qualification_requirements` | `unit_id` and `qualification_id` TEXT FKs/composite key; `required_holder_count` INTEGER positive configured requirement |
| `admin_cases` | `case_id` TEXT key; `unit_id` TEXT FK; `case_type` TEXT configured process category; `opened_date` TEXT required; `closed_date` nullable TEXT completion date; `correction_required` nullable INTEGER (1 correction required, 0 completed without correction) |

For an unclosed case, `closed_date` and `correction_required` are both NULL. For a closed case, the outcome flag is required. A completion after D is excluded from completed-case metrics at D; its future outcome must not leak into current rates.

The six configured unit allocations total 300. Case categories are onboarding, records_update, transfer, and evaluation; they describe fictional workflows. Planted scenarios are fully declared in `config/project.yml`. No realized rate, count, or simulated finding is claimed from these settings alone.

Clean reference inputs and dirty inputs will be separate. Accepted input, rejected input, and SQL exports will have documented lineage when the corresponding code is implemented. No real names, military IDs, or system extracts are permitted.
