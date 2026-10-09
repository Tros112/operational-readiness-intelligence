# Day 5 SQL walkthrough

All examples are **simulated**, using October 7, 2026. These measures are fictional operational proxies. This walkthrough supports your explanation; it does not count as evidence that you independently own it.

## Follow three different grains

Staffing starts with `personnel`: one row per person. Qualification coverage starts with `unit_qualification_requirements`: one row per unit/qualification, matched to distinct available, valid holders. Expiration inventory starts with currently valid certificates: one row per person/qualification, including unavailable people. They answer different questions and should not be counted in one large joined row set.

In `sql/unit_summary.sql`, each common table expression (CTE, a named intermediate query) aggregates one subject before the final joins. `staff` counts people directly. `holders` counts distinct people within each unit/qualification. `qualifications` sums capped coverage and gaps from each requirement pair. `expirations` counts certificates and distinct people for each cumulative window. The final query joins these unit totals to `units`; it cannot turn a person's three certificates into three personnel rows.

In `sql/qualification_detail.sql`, the `holders` CTE filters eligibility **before** requirements are LEFT JOINed to it:

```sql
WHERE p.is_available = 1
  AND pq.valid_from <= :as_of_date
  AND :as_of_date < pq.expiration_date
```

Requirements define what must be covered, including when no eligible holder exists. A LEFT JOIN retains an unmatched requirement, and `COALESCE(h.holder_count, 0)` gives its holder count zero. An inner join would hide the missing coverage. Putting holder eligibility in a final WHERE clause can also discard unmatched rows. The denominator must survive even when the numerator is empty.

`COUNT(DISTINCT person_id)` is defensive counting. It is not authority to accept conflicting source certificates. Day 3 quarantines all duplicate versions; Day 4 constraints enforce the key; the exporter rechecks the passed source. The duplicate test intentionally bypasses constraints only in an isolated in-memory SQL fixture. It does not create a production deduplication policy.

## Hand-check Unit C

Use `qualification_detail.csv`, filter `unit_id = U03`, and compare with this simulated calculation:

| Qualification | Valid available holders | Required | Capped | Gap |
| --- | ---: | ---: | ---: | ---: |
| Q01 | 5 | 2 | 2 | 0 |
| Q02 | 4 | 2 | 2 | 0 |
| Q03 | 7 | 2 | 2 | 0 |
| Q04 | 4 | 2 | 2 | 0 |
| Q05 | 3 | 2 | 2 | 0 |
| Q06 | 1 | 2 | 1 | 1 |
| Q07 | 4 | 2 | 2 | 0 |
| Q08 | 3 | 2 | 2 | 0 |
| Total | Do not use as a unique-person count | **16** | **15** | **1** |

Qualification coverage is **15 / 16 = 93.75%**. Capping happens per pair, before summing. Q01's surplus cannot fill Q06's missing slot. Q06's only available, valid holder is fictional ID P0128. Its requirement is two, so it is unmet and is not fragile. Fragile means coverage is met with no surplus; Unit B/Q03, with P0096 as its sole eligible holder and a requirement of one, is both fragile and a single-holder dependency.

Unit C staffing is a separate calculation: **40 available / 50 required = 80%**, with **max(50 - 40, 0) = 10** missing personnel. Overall staffing is **254 / 250 = 101.6%**, while the sum of per-unit gaps is still **10**. This preserves the aggregate-versus-local distinction you already explained in Day 2. Sum counts before dividing; do not average the six unit percentages.

## Explain an expiration boundary

A certificate expiring on October 7 is already invalid on October 7. A certificate valid from October 7 is eligible that day if its expiration is later. Future-start certificates are excluded from today's inventory.

A currently valid certificate expiring November 6 is 30 days from October 7. It enters the inclusive 30-day window and therefore also the 60- and 90-day windows. November 7 enters the 60-day window but not the 30-day window. `expiration_detail.sql` uses the fixed parameter, SQLite date offsets, and calendar-day differences; it never uses the computer clock.

The Unit D/Q04 cluster has six certificates expiring after 7, 10, 14, 20, 25, and 30 days. Their current coverage is six holders for two required. Today's output reports the expiration inventory; recalculating a future no-renewal gap remains Day 10. Inventory includes unavailable people so their renewal need is visible. Current coverage counts available people only, because it answers today's availability question.

One person can have several expiring certificates. Accordingly, 45 certificates in the 30-day inventory affect 41 people, not 45. Count distinct person IDs over the selected records. The cumulative windows overlap and cannot be added together. Several qualification slots may also be held by one person; this project does not model simultaneous assignments.

## Run and read the export gate

`src/export_metrics.py` reuses the loader's passed-bundle checks, opens the database in read-only mode, and verifies every stored value against accepted input. A single read transaction keeps verification and all queries on the same database snapshot. The exporter never regenerates or reloads the database.

Three CSVs are staged before their fixed filenames are replaced. A successful `export_manifest.json` identifies the date, grains, counts, SQL hashes, CSV hashes, and logical database digest. Since replacing three files is not one filesystem transaction, the CLI invalidates the old manifest before starting. An error leaves `exports_ready = false`; rerun successfully before Power BI refresh. A missing database is an error, not a request to create an empty one.

SQL NULL denotes an undefined ratio. The CSV writer leaves it blank; a later Power BI import must retain that blank. Empty counts are zero. The clean reference has positive requirements, while an isolated zero-demand fixture verifies the defensive NULL behavior.

## Ownership check after Windows verification

Explain in your own words:

1. What would an inner join to holders hide, and why does a zero-holder requirement still belong in the coverage denominator?
2. Why does a person holding three certificates contribute one person to staffing? How do the separate CTE aggregates prevent inflated counts?

Then trace Unit C's Q06 row and explain why it has a gap without a fragile flag. These explanations remain unconfirmed until you supply them; SQL tests and a generated walkthrough cannot substitute for your understanding.

Primary technical references: [SQLite aggregate functions](https://www.sqlite.org/lang_aggfunc.html), [SQLite date functions](https://www.sqlite.org/lang_datefunc.html), and [SQLite read-only URI mode](https://www.sqlite.org/uri.html). The metric rules and dates are this project's contract, not SQLite policy.
