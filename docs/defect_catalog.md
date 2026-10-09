# Day 3 injected-defect catalog

All defects are deliberately injected into a separate **synthetic** copy. `src/inject_defects.py` reads `data/raw/clean/`, writes six CSVs to `data/raw/dirty/`, and records exact logical record numbers, before/after cells, and file hashes in `defect_manifest.json`. It does not copy the clean generation manifest into the dirty folder: that manifest's hashes describe the clean files.

| ID | Table | Deliberate change | Expected rejection code |
| --- | --- | --- | --- |
| D01 | personnel_qualifications | Append a duplicate certificate key; both original and appended records must fail | DUPLICATE_KEY |
| D02 | personnel | Clear an otherwise unused person's identifier | MISSING_REQUIRED |
| D03 | personnel_qualifications | Clear expiration_date | MISSING_REQUIRED |
| D04 | personnel_qualifications | Set valid_from to impossible 2026-02-30 | INVALID_DATE |
| D05 | personnel_qualifications | Set expiration equal to valid_from | CERTIFICATE_DATE_ORDER |
| D06 | personnel_qualifications | Reference nonexistent person PX9999 | FOREIGN_KEY |
| D07 | personnel | Reference nonexistent unit UX99; this person's one certificate must also fail | FOREIGN_KEY; child REJECTED_PARENT |
| D08 | personnel | Set is_available to 2 | INVALID_FLAG |
| D09 | admin_cases | Clear case_type | MISSING_REQUIRED |
| D10 | admin_cases | Set completion one day before opening | CASE_DATE_ORDER |
| D11 | admin_cases | Give an open case a correction outcome of 0 | CASE_OUTCOME_STATE |
| D12 | admin_cases | Clear a completed case's correction outcome | CASE_OUTCOME_STATE |
| D13 | unit_qualification_requirements | Set required_holder_count to 0 | NONPOSITIVE_COUNT |
| D14 | unit_qualification_requirements | Set required_holder_count to 2.5 | INVALID_INTEGER |
| D15 | unit_qualification_requirements | Reference nonexistent qualification Q99 | FOREIGN_KEY |
| D16 | personnel | Append a duplicate person key without certificates; reject both versions | DUPLICATE_KEY |

The injector chooses different targets for independent defects. Missing/invalid/duplicate personnel targets have no certificates; the deliberately broken-parent target has exactly one certificate outside the directly edited certificate records. This keeps causal attribution visible.

Verified reference result: 16 edits, two appended records, 18 directly rejected records and one rejected descendant. Dirty input 1,229 = accepted 1,210 + rejected 19. The three invalid requirement records also leave three missing accepted requirement pairs, a batch-level error without fabricated replacement rows. Evidence: `docs/verification_day03.md` and `docs/validation_check.json`.
