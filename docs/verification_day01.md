# Day 1 verification

Performed October 7, 2026. These checks verify a foundation only; they do not establish a working pipeline or Power BI report.

| Check | Observed result |
| --- | --- |
| Environment/configuration checker | Passed, exit code 0 |
| Python syntax compilation | Passed |
| Empty in-memory SQLite schema | Exactly six source tables; foreign keys enabled; integrity_check = ok |
| Repeated schema DDL | Passed; this does not test loader idempotence |
| Configuration | Six units, 300 allocated personnel, eight qualifications, four scenarios; dates and references consistent |
| Constraint probe: duplicate person/qualification key | rejected as expected |
| Constraint probe: broken unit foreign key | rejected as expected |
| Constraint probe: invalid availability flag | rejected as expected |
| Constraint probe: zero qualification requirement | rejected as expected |
| Constraint probe: reversed certificate dates | rejected as expected |
| Constraint probe: open case with known correction outcome | rejected as expected |
| Constraint probe: completed case missing correction outcome | rejected as expected |
| Worked-example arithmetic | Staffing 26/40 = 65%; capped qualification coverage 3/4 = 75%; median [1,2,10] = 2 |
| 30-day boundary | D + 30 = 2026-11-06 confirmed by calendar arithmetic; analytical eligibility SQL not yet implemented |
| Required artifact paths | Present |
| Source schedule preservation | Byte-identical to attachment |
| No premature output claims | No operational CSVs, populated project database, or PBIX created |

## Known constraint limit

Confirmed: DDL length/order accepts 2026-02-30; Python calendar validation is required before load.
This is an intentionally demonstrated gap in the schema alone, not a passed data-validation criterion. Day 3 must reject invalid dates before Day 4 loading.

## Scope of the probes

Tiny fixture rows existed only in an in-memory connection that was closed. They are teaching/check fixtures, not the six-table operational dataset or simulated findings. No dirty-data pipeline has been written. Discrepancy/expiration analytical outputs and Power BI totals remain untested because those implementations do not exist.

## Remaining checks

- User Windows Power BI version and open/save/reopen confirmation.
- User explanation of grain, denominator, expiration boundary, and open-case treatment.
- Generator reproducibility and scenario realization (Day 2).
- Injected-error detection, accepted/rejected reconciliation (Day 3).
- Populated database and idempotent loader (Day 4).
- Analytical SQL and dashboard reconciliation (Day 5 onward).

Source schedule SHA-256: `0a4621f2a17e8d93285b3c2f46dc8313b050819ad509ea24303a68e776a0ffea`.
