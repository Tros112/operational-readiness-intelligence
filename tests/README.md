# Meaningful checks to add as implementation exists

Day 2 implements `test_generate_data.py`: eight passing clean-reference checks for keys/FKs/schema compatibility, calendars/lifecycle, the four documented scenarios, independent-run reproducibility, null serialization, seed sensitivity, and invalid configuration. Run `python -m unittest discover -s tests -v` from the root. No extra test runner is required.

Day 3 adds fourteen checks in `test_validate_data.py`. Every injected defect and dependent record is detected; counts, calendar/typed/lifecycle constraints, parent rejection, output hashes/raw values, malformed/missing files, source preservation, and failure replacing a prior success report are checked. Windows Day 3 report evidence was inspected; its 22-test pass was user-reported after terminal output was cleared.

Day 4 adds ten checks in `test_load_data.py`. Its **32-test suite passes on Linux and inspected Windows output**. Persistent counts/values/nulls, repeat identity, blocked dirty/stale/changed input, actual constraint-failure rollback, database constraints, and preservation of unrelated databases and protected local assets are checked. Failed CLI runs invalidate old success audits.

Day 5 adds ten checks in `test_export_metrics.py`, bringing the suite to **42 passing tests on Linux** (10.731 seconds, exit 0). Windows Day 5 is pending. Tests cover:

- Every current SQL metric versus independent Python calculations from source CSVs, with fixed Unit C/fragility/renewal-cluster hand checks.
- Multiple certificates and intentional identical duplicates cannot inflate staffing, distinct holders, or certificate inventory; surplus remains capped per requirement pair.
- Zero-holder requirements survive, and unavailable valid certificates appear in inventory but not current available-holder coverage.
- Expiration on D is excluded; D + 30/60/90 endpoints are included; following days fall outside the matching window; distinct people and cumulative overlaps remain correct.
- Zero denominators give NULL while empty counts give zero.
- Repeated CLI exports produce identical unique-grain/classified/dated CSVs without changing database or source bytes.
- Dirty, stale-date, changed-source/accepted, mismatched-database and missing-database attempts cannot authorize an export; prior passed manifests are invalidated.
- Protected folders/report-file fixtures remain untouched, and a simulated interrupted CSV replacement disables the manifest.

The duplicate and zero-demand fixtures are isolated unconstrained in-memory databases used only to exercise defensive SQL. Production validation and schema constraints still reject those inputs. The generated reference currently has no zero-holder pair. Do not call a fixture result an observed reference finding.

Run `python -m unittest discover -s tests -v` from the root. Run generation first on a fresh checkout because reference tests require the clean CSVs; an existing working folder reuses them. Power BI reconciliation and later process/no-renewal metrics are not claimed by this suite.

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
