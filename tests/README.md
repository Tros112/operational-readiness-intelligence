# Meaningful checks to add as implementation exists

Day 1 has an environment/configuration/schema check and one-time in-memory constraint probes. The generator, validator, loader, analytical metrics, and Power BI report are not yet implemented.

Later checks must address actual failure risks:

- Same configuration/seed yields identical six-table CSV data.
- Each injected defect is detected and accepted/rejected counts reconcile.
- Duplicate person/qualification rows cannot inflate holder counts or staffing.
- Certificate expiration on D is excluded; expiration on D + 30 is included in the 30-day outlook and removed from projected coverage.
- Requirements with zero holders remain visible after joins.
- Cases open at D do not enter discrepancy/cycle metrics; zero completed cases produce an undefined rate.
- Repeating the loader does not duplicate accepted records and a failed load does not leave partial results.
- SQL and Power BI agree on global and selected-unit counts/ratios.

Do not add tests that merely repeat implementation statements or imply unbuilt features passed.
