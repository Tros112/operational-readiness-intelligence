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

Core Windows **Day 3** validation/reproduction is complete as of October 9 with inspected report/rejection screenshots and a user-reported 22 tests, OK result. The duplicate-authority ownership check is confirmed; other validation explanations remain open. Evidence distinctions are recorded below. Actual focused hours and host-company preview attendance/feedback are unreported.

### Windows inspection evidence — October 8, 23:44 PDT

The assistant successfully inspected the user's action 4 screenshot despite the accompanying image-read error text. Evidence is retained locally as `docs/evidence/day03_windows_validation_inspection.png`, excluded from the public repository. It shows the rejection export, the D01 manifest entry for certificate source records 2 and 267 (P0003/Q04), and the dirty validation report. The report visibly contains a Windows OneDrive input directory, `exit_code: 1`, no file errors, and expected missing requirement pairs U01/Q01, U01/Q02, and U01/Q03. These are partial Windows dirty-validation and inspection results, not a new access blocker.

The displayed D01 certificates are identical, with dates February 8 through October 25, 2026; this fixture is not evidence of conflicting certificate dates. The rejection CSV uses source logical record numbers, not its own line positions. D07's expected trace is personnel record 8 (P0007, nonexistent unit UX99) followed by certificate record 9 (P0007/Q07), rejected because its parent was rejected.

The screenshot does not display the dirty totals or load_allowed, the clean run, all command exit codes, or the 22-test terminal summary. The selected Output panel contains package-updater messages, not test results. Do not mark full Windows reproduction or independent ownership complete from this image. The next action is to inspect the four target rejected records, return both report summaries and existing test evidence, and answer the duplicate-policy ownership prompt in `docs/day03_windows_handoff.md`.

### Windows core checks completed — October 9, 2026

The assistant successfully inspected both later attachments. Copies are retained locally as `docs/evidence/day03_windows_rejection_trace.png` and `docs/evidence/day03_windows_validation_totals.png`, excluded from the public repository. The rejection trace shows:

- Certificate source records 2 and 267, P0003/Q04: DUPLICATE_KEY on both.
- Personnel source record 8, P0007: FOREIGN_KEY.
- Certificate source record 9, P0007/Q07: REJECTED_PARENT.

The totals screenshot shows the clean report as passed, load_allowed True, report exit code 0, 1,227 input / 1,227 accepted / 0 rejected, counts_reconciled True, and an input path under the user's Windows Day 3 project ending in `data/raw/clean`. The dirty report is validation_failed, load_allowed False, report exit code 1, 1,229 input / 1,210 accepted / 19 rejected, and counts_reconciled True. Its Windows input-directory prefix is visible; the final path portion is truncated in this screenshot. These are inspected report fields, not direct observations of PowerShell's LASTEXITCODE.

At 00:40 PDT, the user reported **22 tests, OK** and explained that the terminal result had been accidentally cleared. Record the Windows suite as **user-reported passed**; its raw output, duration, interpreter, and process exit code were not retained or inspected. Do not request a repeat of successful tests solely for another screenshot. The independently executed Linux suite remains 22 passed.

The user's explanation identifies that no external source of truth was supplied to establish a conflicting record's authority. This demonstrates the core reason that selecting the first duplicate is unsupported. The assistant clarified that unresolved authority does not prove both rows false or manipulated; D01 itself is an identical duplicate. Other ownership topics remain pending, and the CSV/database enforcement explanation was provided rather than independently demonstrated.

**Completion check:** core Day 3 implementation, Windows report/rejection reproduction, and duplicate-authority ownership are complete. The Windows test evidence is explicitly user-reported. No access blocker is observed. The code, source reference, schema, metric definitions, and scope were unchanged in this documentation follow-up; a Git whitespace check passed. The frozen Day 3 ZIP remains the implementation checkpoint, and these notes/evidence are later supplements.

At the close of Day 3, no persistent loader, reload transaction/idempotence demonstration, analytical marts, or SQL/Power BI reconciliation existed. The diagnostic accepted subset's memory-only schema check did not complete Day 4. The later loader evidence is in `docs/verification_day04.md`. No PBIX was created/opened/verified by the assistant, and no release gate is passed by these checks.

The next milestone at Day 3 close was Day 4, scheduled Saturday October 10 or earlier if directed. It was subsequently implemented October 9; follow `docs/day04_windows_handoff.md` for local reproduction.

Public delivery note, October 9: automatic approval review rejected uploading the inspection screenshot because its contents were not explicitly authorized for public release. All three supplementary Day 3 screenshots remain local; the public repository contains these textual observations and reproducible validation evidence. Previously published Day 2 screenshots are unchanged. Screenshot exclusion does not change the implementation or the distinction between inspected reports and user-reported tests.
