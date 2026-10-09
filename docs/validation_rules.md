# Day 3 validation contract

Prepared October 8, 2026; scheduled milestone October 9, executed early at the user's request. All source data and defects are synthetic. Metric date remains October 7.

## Loading decision

Quarantine invalid records, preserve their original values and reasons, and **block the entire batch from loading when any row, file, or batch check fails**. Accepted rows in a failed run are diagnostic subsets, not approved dashboard inputs. Day 4 must require `load_allowed: true` and verify the accepted-file hashes; no persistent loader is implemented on Day 3.

Duplicate keys reject **every** record with that key, including the original. Keeping the first or last would make an unsupported choice when versions disagree. Child records may reference only accepted parent records. A child pointing to a rejected parent is rejected with `REJECTED_PARENT`; a key never present in the parent source gets `FOREIGN_KEY`.

## Checks

| Check | Rule |
| --- | --- |
| Source structure | Six expected UTF-8 CSV files; exact ordered headers; valid CSV quoting and row width. Extra CSV files block the batch. Missing/unreadable/unparseable files do not get invented zero input counts. |
| Required values | Every field is required except admin_cases.closed_date and correction_required. Empty/whitespace-only required values are rejected. Critical identifiers with surrounding whitespace are rejected, not trimmed. |
| Keys | Unique declared keys, including person/qualification and unit/qualification composite keys. Every colliding record is quarantined. |
| Counts/flags | Counts are positive integer strings within SQLite's signed 64-bit range. Availability and known correction flags are exactly 0 or 1. |
| Foreign keys | Unit, person, and qualification references must resolve to accepted parents. Rejection propagates in dependency order. |
| Calendar dates | Exact YYYY-MM-DD and a real Python calendar date. 2026-02-30 fails even if SQLite's text constraints accept it. |
| Certificate order | expiration_date must be strictly after valid_from. Expired and future-start records can pass validation; eligibility at D is a later SQL rule. |
| Case lifecycle | closed_date cannot precede opened_date. A blank closed_date requires a blank correction flag; a populated closed_date requires a 0/1 flag. Same-day completion is valid. |
| Requirement completeness | Every accepted unit/qualification combination must have an accepted requirement. Missing pairs block the batch; no requirement is invented. Units and qualification_types must be nonempty. |

Valid future case dates are retained under the metric contract; SQL must exclude future openings and treat after-D completions as open at D. Validation checks record integrity, not current eligibility. There is no case-type whitelist beyond a required nonblank label and no forced source row counts; the generator's scope checks remain separate.

## Outputs and counts

Each output bundle contains six `accepted/*.csv` files, `rejected_rows.csv` (one record per quarantined source row), `validation_issues.csv` (one issue per rule/field), and `validation_report.json`. A row with several issues counts **once** as rejected. Rejected payloads retain the original CSV cell list as JSON; no identifier, date, or outcome is repaired.

For each completely read source: **input rows = accepted rows + rejected rows**. `record_number` counts logical CSV records including the header as record 1, not physical text lines. Missing/unparseable sources have unknown input counts and `counts_reconciled: false`. Extra-file errors refer to files outside the six-table count scope.

Exit codes: **0** passed; **1** row/batch validation failure; **2** file/structure/configuration/output error. A dirty-run exit 1 demonstrates intentional defect detection. Counts can reconcile while quality fails.

The report records source hashes and emitted-file hashes. It is written with `load_allowed: false` before exports, then replaced with the final result after all exports succeed. A failed rerun therefore cannot leave an earlier success report authorizing stale outputs. Outputs must not overlap the input directory or the canonical clean-reference directory.
