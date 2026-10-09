# Day 2 verification

Executed October 7, 2026, ahead of the scheduled October 8 milestone at user request. Analysis date remains October 7; no release gate or scope changed. All operational counts below are **simulated**.

## Evidence and commands

```bash
python src/generate_data.py
python -m unittest discover -s tests -v
```

Both commands completed successfully. The second ran **8 checks, all passed**. `docs/generation_check.json` records realized source/scenario counts; `data/raw/clean/generation_manifest.json` records each CSV's SHA-256 hash, rows, columns, seed, configuration hash, generator hash, and versions.

| Check | Result / scope |
| --- | --- |
| Six table counts, keys, FKs, strict schema compatibility | Passed. Every source table loaded into an in-memory database; no FK violations |
| Calendar parsing, case chronology, nullable outcomes | Passed. No future case openings/completions; unknown open outcomes retained |
| Staffing scenario | Only Unit C is below staffing requirement: 40/50 |
| Fragile qualification | Unit B/Q03 has exactly one valid available holder and requirement one |
| Renewal cluster | Unit D/Q04 has six distinct available holders, expiration offsets 7/10/14/20/25/30; none survive day 30 without renewal |
| Process hotspot settings and usable completions | Passed. Explicit 30% versus 6% probabilities; outcomes not resampled |
| Two independent CLI processes | All six CSVs and the manifest are byte-identical in separate temporary folders |
| Seed sensitivity / invalid probabilities | A different seed changes random tables; status probabilities that do not sum to one are rejected |
| Canonical output hashes | All six file hashes match the manifest |

## Windows reproduction — October 7, 16:02 America/Los_Angeles

The user's terminal screenshots show Python **3.11.4**, the extracted OneDrive project folder, and a successful source-file path check. The screenshot supplied at 16:02 shows this command run with the project's virtual environment:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

All eight named tests report `ok`; the summary reads **Ran 8 tests in 2.230s** and **OK**. This confirms the clean-generator checks run successfully on the user's Windows computer as well as in the assistant's Linux environment. The assistant inspected the supplied screenshot, not the Windows machine itself. The repeatability test compares two runs within each environment; cross-platform byte identity was not tested. Reference counts and hashes below remain those of the assistant-generated canonical files.

## Actual reference counts

The user's 16:28 Windows screenshots also show a successful standalone `src/generate_data.py` run from VS Code using the project's `.venv` executable. The output reports `status: generated`, `data_classification: synthetic_only`, analysis date `2026-10-07`, and `data/raw/clean/` as the output folder. All six reported row counts match the following reference counts. The VS Code global-interpreter import failure seen at 16:18 is resolved by the selected project environment. Windows output hashes/bytes were not supplied; no cross-platform byte comparison is inferred from matching row counts.

| Source | Rows |
| --- | --- |
| units | 6 |
| personnel | 300 |
| qualification_types | 8 |
| personnel_qualifications | 265 |
| unit_qualification_requirements | 48 |
| admin_cases | 600 |

Certificate statuses reconcile: 193 currently valid + 49 expired + 23 future-start = 265. There are 172 valid certificates belonging to available people; those are certificate rows, not staffing headcount.

Cases reconcile: 442 completed + 158 open = 600. Corrections: 27/70 completed in Unit F (38.6%) and 18/372 elsewhere (4.8%). Those rates arise from the explicit planted probabilities, not real-world observations.

Staffing totals: 254 available / 250 required = 101.6%, while Unit C remains 40/50 with a local gap of 10. Qualification requirements total 95 slots; seven pairs are currently below their requirement. These are source audits, not exported/reconciled dashboard measures.

## Power BI staffing screenshot — October 8, America/Los_Angeles

Evidence: the user-supplied image, retained as `powerbi/screenshots/day02_staffing_review.png`. The assistant inspected the image, not the PBIX or live Desktop.

- All six visible unit rows match the expected staffing counts, percentages, and gaps in `powerbi/day02_staffing_review.md`. The matrix total is 254 available / 250 required = 101.6%, with total local gap 10.
- The Unit C matrix row is selected; the cards show 40 available, 50 required, 80.0% coverage, and gap 10. This is consistent with matrix selection filtering the cards. The unit slicer has no checked boxes; slicer behavior/reset is not demonstrated by this image.
- The report displays the fixed October 7 snapshot date and labels staffing synthetic and readiness a fictional proxy.
- The user independently explained that A/B/D/E surpluses of 1/4/7/2 push aggregate coverage over 100% while C's 10-person shortage remains. This specific ownership check is confirmed: 14 total surplus minus 10 local shortage leaves 4 net surplus.

### 21:30 follow-up — core staffing review complete

Three further attachments were successfully inspected and retained as evidence:

| Check | Result / evidence |
| --- | --- |
| All-unit view | `powerbi/screenshots/day02_staffing_all_units.png`: all expected matrix rows and cards 254 / 250 / 101.6% / 10; no checked unit slicer boxes |
| Unit C slicer | `powerbi/screenshots/day02_staffing_unit_c_slicer.png`: Unit C visibly selected; matrix and cards 40 / 50 / 80.0% / 10 |
| Relationship | `powerbi/screenshots/day02_staffing_relationship.png`: units[unit_id] unique side (1), personnel[unit_id] many side (*), active Yes, Single filtering toward personnel |
| Save/reopen | User reports that the populated report saves and reopens; no PBIX supplied or inspected by the assistant |

The properties pane lists personnel first, so its many-to-one (*:1) display is equivalent to the intended units-to-personnel 1:* relationship. The all-unit and selected-unit states are evidenced; the screenshots do not establish the chronology of a separate clear/reset action. Additional unit/multiselect and edge cases remain part of later production reconciliation. Actual measure definitions have not been inspected. The supplied evidence completes the core Day 2 learning review, not full SQL/dashboard reconciliation or a release gate.

## Deliberate limits and later checks

- In-memory population verifies source compatibility; there is no persistent loader, load transaction/idempotence check, or operational database release yet.
- This reference happens to have no zero-holder requirement pair. Day 5 must hand-check a small fixture to verify LEFT JOIN retains that pair. The metric contract already specifies the required behavior.
- No dirty copy, defect injection, quarantine, rejection reconciliation, or general `validate_data.py` exists yet. Day 3 owns those checks.
- No analytical marts, SQL/Power BI KPI reconciliation, production operational report, or PBIX inspection has been completed. Windows access is user-confirmed; the Day 2 learning report has the screenshot evidence recorded above.
- Dates/cases do not reconstruct historical staffing; no training/evaluation or empirical inference has been performed.
- Aggregate versus local staffing is independently explained. Other ownership topics and actual user-focused hours remain unreported.

Next exact action: on Day 3, October 9, create the separate dirty input copy and a defect catalog, implement validation, and prove each injected defect is detected with reconciled counts. Do not alter the clean reference to create defects or begin the Day 4 loader.
