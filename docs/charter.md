# Project charter

Version 0.3 · Day 2 completed early · October 7, 2026 · Schedule timezone: America/Los_Angeles

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

Day 2 completion: at the user's request, the October 8 milestone was executed on October 7. Metric contract v1.0, clean generator, six CSVs/manifest, field dictionary, and eight passing checks are complete. Repeated independent runs match byte for byte, and all four planted scenarios are traceable. Release dates are unchanged. Dirty validation, persistent loading, analytical marts, and the operational report remain later milestones.

MVP acceptance follows the source checklist: clean regeneration/load/export; visible critical-error handling and reconciliation; hand checks for duplicate certificates, expiration boundaries, and zero denominators; functional/filterable views; three to five evidenced simulated findings; honest README; demo backups; user explanation of grain, join, quality failure, and KPI.

If behind, cut styling and extra charts/dimensions first, defer PostgreSQL migration, reduce process detail, then combine complete pages. Preserve the three business questions, correct metrics, pipeline, evidence, and one reliable demo. If Power BI remains blocked, provide a clearly labeled static interim report and leave the Power BI acceptance item incomplete.

## Session responsibilities

The assistant implements and verifies code/SQL/documentation and prepares the report handoff. The user builds and inspects Power BI locally, practices and demonstrates explanations, provides actual availability/feedback, and carries checkpoint reports between chats. A generated explanation does not count as confirmed user understanding.

Read charter/progress/decisions at each session start. Work on one daily milestone. End with concrete paths, verification, blockers, and the next first action. Record coherent Git checkpoints locally; no remote has been supplied and no push is authorized. Use the source report template at the October 13, 19, and 30 release gates.
