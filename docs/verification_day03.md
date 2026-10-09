# Day 3 verification

Executed October 8, 2026, America/Los_Angeles, ahead of the scheduled October 9 milestone at the user's explicit request. Metric date remains October 7. All data and injected defects are synthetic; readiness remains a fictional proxy.

## Verified results

| Source | Clean input / accepted / rejected | Dirty input | Dirty accepted | Dirty rejected |
| --- | --- | ---: | ---: | ---: |
| units | 6 / 6 / 0 | 6 | 6 | 0 |
| personnel | 300 / 300 / 0 | 301 | 296 | 5 |
| qualification_types | 8 / 8 / 0 | 8 | 8 | 0 |
| personnel_qualifications | 265 / 265 / 0 | 266 | 259 | 7 |
| unit_qualification_requirements | 48 / 48 / 0 | 48 | 45 | 3 |
| admin_cases | 600 / 600 / 0 | 600 | 596 | 4 |
| Total | **1,227 / 1,227 / 0** | **1,229** | **1,210** | **19** |

The clean CLI exits **0**, `status: passed`, `load_allowed: true`. The dirty CLI exits **1**, `status: validation_failed`, `load_allowed: false`. Every table reconciles input = accepted + rejected. Reconciling counts does not mean the dirty data passes quality.

All **16** cataloged edits were independently matched to their expected table, logical record number, and rejection code in the actual report. Both versions of the duplicate certificate and person keys were rejected. The deliberately orphaned person's certificate (fictional P0007, certificate logical record 9) was rejected with `REJECTED_PARENT`. There are **18 direct rejections + 1 descendant = 19**. The three invalid requirement records also leave missing U01/Q01, U01/Q02, and U01/Q03 pairs; the batch is blocked without manufacturing requirements. Machine-readable coverage: `docs/validation_check.json`.

**22 tests passed** in the assistant's Linux environment: the existing eight generator checks and fourteen validator checks. Coverage includes every cataloged defect/cascade, unchanged clean values, database key/FK compatibility of the diagnostic accepted subset in memory only, conflicting parent versions, expired/future-start certificates, same-day completions, exact ISO/leap calendars, integer/storage limits, padded IDs, missing requirement pairs, multiple issues counted once per rejected row, missing/malformed/unparseable/extra sources, exported counts/hashes/raw values, deterministic dirty creation, source protection, and CLI failure replacing a prior success report.

All six original clean CSV hashes **and the clean generation manifest hash are unchanged** from the pre-session snapshot. Dirty regeneration produces identical six CSVs and defect manifest. All emitted-file hashes match their reports. No Python dependency, clean generator, source schema, or scenario configuration changed.

## Reproduce

From the project root, using its Python environment:

```bash
python src/inject_defects.py
python src/validate_data.py
python src/validate_data.py --input-dir data/raw/dirty --output-dir data/rejected/day03_dirty
python -m unittest discover -s tests -v
```

Expected exits are **0 / 0 / 1 / 0**. The dirty validator's exit 1 is intentional; inspect the blocked report and reasons. Windows commands and extraction path: `docs/day03_windows_handoff.md`.

## Artifacts and limits

- Clean bundle: `data/processed/validation_clean/validation_report.json`, six `accepted/*.csv`, empty `rejected_rows.csv`, and empty `validation_issues.csv`.
- Dirty inputs: six `data/raw/dirty/*.csv` and `defect_manifest.json`.
- Dirty diagnostics: `data/rejected/day03_dirty/validation_report.json`, six `accepted/*.csv`, 19 rows in `rejected_rows.csv`, and 19 issues in `validation_issues.csv`. These accepted rows are **diagnostics only** because the batch is blocked.
- Rules: `docs/validation_rules.md`; catalog: `docs/defect_catalog.md`; explanation: `docs/validator_walkthrough.md`.
- Source implementation: `src/validate_data.py`, `src/inject_defects.py`, `tests/test_validate_data.py`.

Windows **Day 3** reproduction and the user's independent explanation of the rejection policy remain pending. Prior Day 2 Windows tests and staffing-review evidence remain valid; they do not verify this new validator. Actual focused hours and host-company preview attendance/feedback are unreported.

No persistent loader, reload transaction/idempotence demonstration, analytical marts, or SQL/Power BI reconciliation exists yet. The diagnostic accepted subset's memory-only schema check does not complete Day 4. No PBIX was created/opened/verified by the assistant, and no release gate is passed today.

Next implementation milestone: Day 4, scheduled Saturday October 10 or earlier if directed. Inspect the clean validation report and accepted-file hashes before implementing an atomic SQLite load with foreign keys enabled, exact counts, blocked dirty input, rollback on failure, and unchanged counts after a second run.
