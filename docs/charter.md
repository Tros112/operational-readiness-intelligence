# Project charter

Version 0.11 · Day 4 complete; Linux/Windows verification and transaction ownership confirmed · October 9, 2026 · Schedule timezone: America/Los_Angeles

Authority: the supplied `SkillBridge_Project_Execution_Plan(1).md`, preserved unchanged as `docs/source_execution_plan.md`, plus the user's execution-workspace instructions. The brainstorming chat owns portfolio priorities, career alignment, and major scope decisions. Its updates are available here only when the user brings them; record those decisions before implementing them.

## Audience, decision, and value

Audience: a fictional operations manager responsible for staffing, qualification coverage, and administrative workload.

Decision: which units need staffing attention, which qualifications need renewal or backup coverage, and which administrative processes need review?

Value: a reproducible, correct, explainable operational analytics demonstration for analyst/BI and applied data-science interviews. California is required and San Diego preferred. Mathematics education, Navy operational/administrative experience, and coursework inform the framing; coursework does not establish professional implementation experience. No employer demand or outcome is inferred without recorded evidence.

## Boundaries

All operational records and findings are fictional/synthetic. Use invented IDs and generic unit/qualification labels. Readiness indicators are project proxies, not official Navy rules or deployability claims.

Minimum scope: six units, 300 people, eight qualification types, one staffing snapshot on **2026-10-07**, 90-day certificate outlook, and 90 days of administrative cases. Routine Day 1 sizing: 600 cases. Six source tables only; their grains are in `docs/schema_sketch.md`.

Python and SQL implement generation, validation, loading, and dashboard exports. SQLite with CSV is the documented fallback because PostgreSQL is unavailable in the execution environment. Power BI Desktop is built/inspected on the user's Windows computer. On October 7, the user confirmed Desktop 2.158.1177.0, 64-bit (September 2026), blank-report open/save/reopen, and no blocker. No PBIX has been supplied to this workspace or inspected by the assistant.

No ML, cloud, dbt, extra datasets/projects, deployment history, maintenance model, assignment optimization, or composite readiness score is in this MVP. Any predictive extension requires a written assessment of label validity, chronology, leakage, baseline value, and whether a SQL rule already solves it. Historical administrative cases support process trends only, not historical staffing/readiness claims.

## Dates, capacity, and completion

| Gate | Required evidence |
| --- | --- |
| October 13, Tuesday | Generated data, functioning SQL output, one inspected Power BI page, accurate prototype explanation |
| October 19, Monday | Repeatable pipeline; reconciled KPIs; executive, qualification, and process views or a reduced complete equivalent; findings, README, and demo backups |
| October 30, Friday | Reproduction instructions, dictionary, rules, corrected visuals, executive brief, and practiced walkthrough |

HoH interviews: October 20–December 3, supplied by the user. Other calendar events in the source plan remain supplied/provisional; no attendance or feedback is assumed.

Actual available hours are unknown. Plan provisionally for **two focused hours on weekdays and three to four on weekend days**, approximately 30–34 hours from October 7–19 before events. This is a capacity assumption, not hours performed. Record actual user hours when reported. Interview activity takes precedence over build work.

Day 1 setup completion: charter, metric outline, six-table schema sketch, access inventory, configuration/structure, and logs are present; the schema can be instantiated in memory; database fallback is recorded; Windows Power BI access is confirmed by the user. Independent explanations remain open as an ownership check. No release gate is passed by a blank report.

Day 2 completion: at the user's request, the October 8 milestone was executed on October 7. Metric contract v1.0, clean generator, six CSVs/manifest, field dictionary, and eight passing checks are complete. Repeated independent runs match byte for byte, and all four planted scenarios are traceable. Release dates are unchanged. Day 3 validation is recorded below; persistent loading, analytical marts, and the production operational report remain later milestones.

Day 2 learning follow-up completed October 8: screenshots show correct global staffing and Unit C slicer-selected results and the active 1:* Single units-to-personnel relationship. The user independently explained aggregate versus local staffing and reports the populated learning report saves/reopens. No actual PBIX or measure definitions have been inspected by the assistant. Broader filter/edge-case and SQL reconciliation remain later checks; this learning preview does not pass the prototype gate.

Day 3 completion: the October 9 validation milestone was executed early on October 8 at the user's explicit request. Separate dirty input contains sixteen cataloged edits. Clean input passes with 1,227 accepted/0 rejected; dirty input reconciles 1,229 = 1,210 accepted + 19 rejected and is blocked from loading. Every intended defect/cascade is detected; all duplicate versions and invalid descendants are quarantined without filling critical values. Twenty-two tests pass on Linux; the clean reference is unchanged. October 9 Windows screenshots confirm both report totals, pass/block states, report exit codes, and D01/D07 rejection traces. The user reports 22 tests, OK, after clearing the terminal output; this is user-reported rather than screenshot-verified test evidence. The user independently identified the absence of authority for choosing a duplicate version; the assistant clarified that unresolved authority does not prove both records false. Core Day 3 implementation/reproduction and this specific ownership check are complete. Other validation explanations remain open. Day 4 storage is recorded below.

Day 4 completion: October 9, ahead of the October 10 schedule, under the user's instruction to continue in the existing Git-connected project. The loader verifies the passed report, date, source/export hashes, source/export value agreement, and source integrity before opening SQLite. It loads all six tables in one transaction with foreign keys enabled, checks exact records/counts and database integrity before commit, and rolls back a failed reload. Two Linux loads retain identical 1,227 records; dirty input exits 1 before changing the database. All 32 tests pass on Linux. October 9 Windows screenshots confirm the Git update, existing interpreter path, clean validation, two successful loads with matching accepted/database counts, passing FK/integrity checks, a True repeat-digest comparison, blocked dirty input/process exit 1, unchanged database bytes, and all 32 tests OK/process exit 0. At 04:38 PDT the user confirmed the existing Power BI learning report opens and functions and independently explained the risk of mixing old/new table contents after a partial commit, using a hypothetical personnel transfer and distorted staffing measures. Day 4 implementation, Windows reproduction, report-preservation confirmation, and this transaction ownership check are complete. Actual PBIX inspection and later SQL/Power BI reconciliation are not established. Analytical SQL/CSV exports are Day 5; no release gate is passed by storage alone.

MVP acceptance follows the source checklist: clean regeneration/load/export; visible critical-error handling and reconciliation; hand checks for duplicate certificates, expiration boundaries, and zero denominators; functional/filterable views; three to five evidenced simulated findings; honest README; demo backups; user explanation of grain, join, quality failure, and KPI.

If behind, cut styling and extra charts/dimensions first, defer PostgreSQL migration, reduce process detail, then combine complete pages. Preserve the three business questions, correct metrics, pipeline, evidence, and one reliable demo. If Power BI remains blocked, provide a clearly labeled static interim report and leave the Power BI acceptance item incomplete.

## Session responsibilities

The assistant implements and verifies code/SQL/documentation and prepares the report handoff. The user builds and inspects Power BI locally, practices and demonstrates explanations, provides actual availability/feedback, and carries checkpoint reports between chats. A generated explanation does not count as confirmed user understanding.

The existing Git-connected Windows folder is the continuing project root. Deliver updates through that checkout; retain .git history, reuse .venv, and preserve the user's local Power BI report. Use the existing-folder handoff rather than a new daily folder or full archive overlay. Local generated data/database/audits and PBIX/PBIT files are excluded from Git. No assistant Windows-file or PBIX inspection is inferred from these protections.

Read charter/progress/decisions at each session start. Work on one daily milestone. End with concrete paths, verification, blockers, and the next first action. Record coherent Git checkpoints locally. The intended repository is https://github.com/Tros112/operational-readiness-intelligence.git, supplied October 9. Before Day 4 publication, the GitHub plugin and native fetch verified public main at 828975fa65e66adb0c5d336fb4bca1a7493e4402. This execution copy has origin configured and main tracking origin/main. The user's remote .gitignore change was merged locally; original local history is preserved.

After the interrupted delivery, the user explicitly authorized publishing Day 4 code, tests, and text documentation only. Exclude screenshots and other images, generated datasets/databases, .venv, and Power BI binaries from the update. Do not retry the denied screenshot upload. Supplementary Day 3 image files and their earlier commits remain local; do not publish private history through an all-branches or history push. Deliver a normal commit based on current remote main and verify its SHA, parent history, and exact file changes. Windows instructions become actionable only after that verification. Use the source report template at the October 13, 19, and 30 release gates.

Day 4 implementation publication is verified at `11697ebd20b3a03dd8b388334ec28a094ccd166c`, directly following the prior remote main, with delivery notes at `7c5dfe8f58b4685d123e27d809248b4688acd56e`. Nineteen text-file changes matched the local checkpoint; no image/generated/local asset changed remotely. The original execution history is retained on local branch `execution/day04-local-history`, including the private image history. Keep that local branch private. Subsequent text documentation records the completed Windows checks and the user-confirmed transaction explanation; the same Windows project folder, .venv, and report remain in use.
