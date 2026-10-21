# Focused metric boundary checks

Day 11, October 20, 2026. **Twelve existing tests pass on Linux in 0.292 seconds, exit 0.** No new test code or metric definition is added. The full suite remains **72 tests**; prior full Linux/Windows passes are separate evidence. The focused command below makes the boundary checks directly reproducible and avoids treating a screenshot as execution of a SQL fixture.

## Run the focused set

From the project root with the project dependencies installed and reference data generated, use its interpreter. On Windows:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    .\.venv\Scripts\python.exe -m unittest discover -s tests -v -k duplicate_certificates -k zero_holder -k expiration_windows -k undefined_denominators -k ProcessSQLTests -k ScenarioSQLTests -k real_constraint_failure
    if ($LASTEXITCODE -ne 0) { throw 'Focused boundary checks failed.' }
}
```

On Linux, the executed invocation was:

```bash
python3 -m unittest discover -s tests -v -k duplicate_certificates -k zero_holder -k expiration_windows -k undefined_denominators -k ProcessSQLTests -k ScenarioSQLTests -k real_constraint_failure
```

Repeated `-k` selectors include matching tests. The tests' temporary fixtures isolate modifications from the accepted database/files. Some fixtures read the generated clean reference; the [fresh runbook](reproduce.md#dependency-order-and-expected-gates) creates sources/exports before running the full suite.

## Exact cases and the errors they prevent

| Module / class | Test method | Boundary or failure verified |
| --- | --- | --- |
| [test_export_metrics.py](../tests/test_export_metrics.py) / ExportTests | test_duplicate_certificates_do_not_inflate_staffing_holders_or_inventory | Certificate join multiplication does not inflate staffing/holders/inventory; distinct-holder semantics remain separate from source uniqueness. |
| same / ExportTests | test_zero_holder_pairs_survive_and_unavailable_inventory_is_separate | LEFT JOIN preserves a required pair with no eligible holder; unavailable valid inventory does not supply current coverage. |
| same / ExportTests | test_expiration_windows_are_inclusive_cumulative_and_count_distinct_people | D+N is included in its cumulative inventory window; people are distinct after selection. |
| same / ExportTests | test_undefined_denominators_remain_null_while_empty_counts_are_zero | Zero-demand SQL fixture returns NULL rate; empty counts remain zero. |
| [test_load_data.py](../tests/test_load_data.py) / LoaderTests | test_real_constraint_failure_after_deletion_rolls_back_the_whole_reload | A real constraint failure after deletion rolls back the full load, preserving the prior database records. |
| [test_process_metrics.py](../tests/test_process_metrics.py) / ProcessSQLTests | test_actual_even_and_odd_medians_recomputed_for_selected_cases | Odd/even medians use individual selected durations, including fractional medians. |
| same / ProcessSQLTests | test_period_boundaries_older_backlog_and_future_events | Inclusive process-period endpoints, retained older backlog and masking outcomes after D. |
| same / ProcessSQLTests | test_zero_completed_empty_units_and_bound_selection_values | No eligible completions gives undefined outcome metrics; empty/selected cases preserve count and bound-parameter behavior. |
| [test_qualification_scenario.py](../tests/test_qualification_scenario.py) / ScenarioSQLTests | test_duplicates_surplus_multiple_qualifications_and_zero_demand | Distinct holders, overlapping qualifications, surplus loss and zero demand remain separate. |
| same / ScenarioSQLTests | test_expiration_endpoints_current_cohort_and_unavailable_people | Exclusive expiration at D/D+N, following-day survival, unavailable people and excluded future-start certificates. |
| same / ScenarioSQLTests | test_new_gap_distinguished_from_worsening_existing_gap | A newly unmet pair differs from an already-unmet pair that loses more coverage. |
| same / ScenarioSQLTests | test_weighted_selected_totals_empty_bound_values_and_mixed_horizon_guard | Weighted selected components, empty scopes, bound values and rejection of mixed alternative horizons. |

Zero-demand, duplicate and zero-holder fixtures exercise defensive SQL behavior; they are not approved reference rows or additional simulated findings. The accepted source requires positive demand and unique keys.

The full suite additionally covers blocked/stale/changed validation, missing databases, repeat exports, protected paths, interrupted replacement, manifest/hash/grain/semantic tampering and read-only preflights. Use [tests/README.md](../tests/README.md) for scope. Fixtures do not verify Desktop execution, actual future outcomes or real operational impact. Day 11's hashes separately confirm preservation of all **51 current data files** after these checks and preflights.
