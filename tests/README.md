# Meaningful checks to add as implementation exists

Day 2 implements `test_generate_data.py`: eight passing clean-reference checks for keys/FKs/schema compatibility, calendars/lifecycle, the four documented scenarios, independent-run reproducibility, null serialization, seed sensitivity, and invalid configuration. Run `python -m unittest discover -s tests -v` from the root. No extra test runner is required.

Day 3 adds fourteen checks in `test_validate_data.py`, bringing the suite to **22 passing tests on Linux**. Every injected defect and dependent record is detected; counts, calendar/typed/lifecycle constraints, parent rejection, output hashes/raw values, malformed/missing files, source preservation, and failure replacing a prior success report are checked. Windows Day 3 reproduction remains pending. The accepted dirty subset's database check is memory-only; a persistent loader/reload, analytical marts, and SQL/Power BI reconciliation remain unimplemented. Later checks below still apply at their milestones.

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
