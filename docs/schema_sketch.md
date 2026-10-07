# Six-table schema sketch

Day 1 · Single snapshot · All operational records are synthetic.

| Table | One row represents | Primary key | Relationships / rules |
| --- | --- | --- | --- |
| `units` | One fictional unit | `unit_id` | Positive staffing requirement |
| `personnel` | One person at D | `person_id` | `unit_id` → units; exactly one unit and one availability flag |
| `qualification_types` | One fictional qualification | `qualification_id` | Eight configured labels |
| `personnel_qualifications` | One person's current certificate record for one qualification | `(person_id, qualification_id)` | References personnel and qualification_types; record may be expired or not yet valid, but no history rows per pair |
| `unit_qualification_requirements` | One unit's requirement for one qualification | `(unit_id, qualification_id)` | References units and qualification_types; positive required holder count |
| `admin_cases` | One administrative case | `case_id` | `unit_id` → units; optional completion date and completion-only correction outcome |

Initial plan: 6 units; 300 personnel; 8 qualification types; all 6 × 8 = 48 unit/qualification requirements; variable certificate count; 600 cases. These are configured targets, not generated/loaded counts.

## Join choices

Staffing aggregates personnel by unit before any certificate join. Otherwise multiple qualifications per person would inflate staffing totals.

Qualification analysis starts from the required unit/qualification pairs, LEFT JOINs available valid holder counts, and treats absent counts as zero. An INNER JOIN would hide the pairs with no holders. Certificate rows reach their current unit through personnel, not through a separately stored unit field.

Administrative cases relate to their unit directly. Do not join case rows to personnel or certificates: those many-row tables would multiply cases. Use separate measures/marts connected by a unique unit dimension in Power BI.

`as_of_date` stays in configuration and is bound into analytical SQL as a parameter. It travels in every export; it is not a seventh operational source table. Dashboard marts are derived outputs, not additional source datasets.

## Constraint boundaries

`sql/schema.sql` is an executable SQLite scaffold using STRICT tables, unique keys, foreign keys, positive counts, availability values 0/1, date ordering, and case outcome consistency. Every connection must enable `PRAGMA foreign_keys = ON` before beginning a load transaction.

Dates remain ISO TEXT in SQLite. The schema checks length and ordering; **Python calendar-date parsing must reject invalid calendar dates before load**. SQLite's text length/order checks alone do not establish calendar validity. Critical nulls and broken relationships must fail or be explicitly quarantined; never invent IDs/dates to repair them.

Day 4 still needs the loader, transactions, idempotent reload behavior, and reconciliation to validated input. In-memory schema checks on Day 1 do not complete those tasks.
