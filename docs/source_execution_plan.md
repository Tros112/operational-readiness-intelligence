# SkillBridge portfolio execution plan

Version 1.0 · Prepared October 6, 2026 · Dates use America/Los_Angeles

## Purpose and working arrangement

Build one credible operational analytics flagship before the HoH interview window opens on October 20, then add complementary evidence only when it improves candidacy. Value means a project you can run, explain, defend, and connect to an employer's decisions. Repository count is not a success measure.

Use the existing brainstorming chat as the **project master/control record**: priorities, career alignment, approved scope, milestone changes, and new ideas. Use a separate execution workspace for implementation, troubleshooting, files, verification, and daily progress. “MDM” here is a practical project governance analogy; it is not a proposal to build a master data management platform.

The two chats do not automatically share updates. The execution workspace maintains its own files and produces a short report you bring back to the master chat. A scope decision becomes authoritative for execution after it is copied into `docs/decisions.md`.

This plan is based on the supplied conversation and HoH calendar. Employer names are the working bracket from that conversation, not a newly verified roster or a guarantee of particular openings. The schedule below is a planning estimate, contingent on available hours and tool access.

## Start here in the new workspace

1. Attach this Markdown file to the new workspace.
2. Paste the launch prompt at the end of this file.
3. Complete Day 1. Let the execution workspace create the project files; do not build the entire portfolio on the first day.
4. At the end of each session, update the progress log and save a resumable checkpoint.
5. Bring the checkpoint report back to the master chat on October 13, 19, and 30, November 20, and December 3, or whenever a material scope decision is needed.

If starting after October 7, preserve the October 19 release gate and reduce scope. Do not simply shift every date forward. If the interview window has already opened, ship the smallest demonstrable version first and rebaseline the remaining dates explicitly.

## Capacity and priority rules

Assume **two focused hours each weekday and three to four hours on weekend days**, approximately 16–18 hours per week before HoH events and interviews. These are proposed work blocks, not a claim about your actual availability. Record your real capacity on Day 1. About 30–34 focused hours are available from October 7–19 at this pace before event time; the MVP target is aggressive and depends on keeping scope small.

On an ordinary two-hour day: 10 minutes to resume/check priorities, 80 minutes to build, 20 minutes to validate and explain, and 10 minutes to log/save. On an interview day, replace most build time with employer research, practice, the interview, and notes. A 20-minute maintenance session is sufficient that day.

Priority order:

1. HoH requirements, employer conversations, and interview preparation.
2. A functioning, demonstrable flagship and truthful explanations of your own work.
3. Reproducibility, metric correctness, and documentation.
4. A complementary forecasting project.
5. Optional ML or a third case study justified by interview feedback.

Each day has one main output. Stop once it meets its completion check. Put extra ideas in the backlog. Treat dates as release goals, not reasons to claim incomplete work is finished.

## Release milestones

| Date | Required outcome | Evidence |
| --- | --- | --- |
| Tue Oct 13 | Visible flagship prototype for Meet & Greet | Real generated data, functioning SQL output, one Power BI page, accurate project description |
| Mon Oct 19 | Interview-ready flagship MVP | Repeatable pipeline, reconciled KPIs, three focused views or reduced equivalent, README, findings, demo |
| Tue Oct 20 | Interview window opens | A project you can show immediately; backups ready |
| Fri Oct 30 | Polished flagship | Reproduction instructions, dictionary, documented rules, corrected visuals, executive brief, practiced walkthrough |
| Fri Nov 20 | Complementary civilian forecasting project, if gates pass | Public-data pipeline, chronological evaluation, baseline comparison, decision brief |
| Thu Dec 3 | Interview-window portfolio freeze | Strongest evidence packaged; employer-driven extension optional |
| Mon Jan 11, 2027 | HoH cohort starts, as supplied | Host-relevant preparation after matching |

The earlier discussion incorrectly called October 19 a Sunday. It is **Monday**. Schedule the full rehearsal on Sunday, October 18, leaving Monday for final fixes and HoH activities.

## Flagship charter: Operational Readiness Intelligence

**Audience:** a fictional operations manager responsible for staffing, qualification coverage, and administrative workload.

**Decision:** which units need staffing attention, which qualifications need renewal or backup coverage, and which processes need review?

**Minimum scope:** six fictional units, roughly 300 fictional personnel, eight qualification types, one current analysis date, 90 days of certification outlook, and 90 days of administrative cases. These are chosen portfolio parameters, not Navy standards. Use a fixed random seed and configuration file. Never use actual personnel identifiers or extracts from Navy systems.

**Core stack:** Python, pandas, SQL, PostgreSQL, Power BI, Git. Prefer PostgreSQL if it works on Day 1. If infrastructure setup consumes more than one session, use SQLite for the portable MVP and SQL-generated CSV exports for Power BI; document the change. PostgreSQL migration is a later improvement. Do not make database installation the project.

**Power BI access:** establish access to Power BI Desktop on your Windows computer immediately. The assistant's execution environment may not be able to create or open a `.pbix` file. In that case it prepares the data, SQL, measures, and build instructions; you build and inspect the Power BI report locally. Record the split of responsibility. A screenshot or HTML prototype is supporting evidence and must not be described as a finished Power BI report.

### Data model and grain

| Table | One row represents | Minimum fields/rules |
| --- | --- | --- |
| `units` | One fictional unit | Unique unit ID, name, required personnel count |
| `personnel` | One person at the current snapshot | Unique person ID, current unit ID, availability flag; exactly one unit per person |
| `qualification_types` | One qualification | Unique qualification ID and label |
| `personnel_qualifications` | One person's current certificate for one qualification | Person ID, qualification ID, valid-from date, expiration date; unique person/qualification pair |
| `unit_qualification_requirements` | One unit/qualification requirement | Unit ID, qualification ID, positive required holder count |
| `admin_cases` | One administrative case | Case ID, unit ID, case type, opened date, closed date if completed, correction-required flag if completed |

Do not add deployment histories, maintenance systems, assignment optimization, or a dozen more dimensions before the MVP. One snapshot avoids misleading historical staffing claims. Process history supports case-volume and cycle-time trends, not historical unit-readiness trends.

### Metric contract: write this before building visuals

All dashboard calculations use the same explicit `as_of_date`. Future cases are excluded. A person is currently available if their configured snapshot flag is true. A certificate is valid when `valid_from <= as_of_date < expiration_date`; it expires at the start of its expiration date. These are project conventions.

| Metric | Definition | Important interpretation |
| --- | --- | --- |
| Staffing coverage | Available personnel / required personnel, by unit | Show actual counts and uncapped ratio; aggregate by summing counts, not averaging unit percentages |
| Current qualification holders | Distinct available people in a unit with a currently valid certificate of the given type | Deduplicate person/qualification records; multiple certificates cannot inflate holder counts |
| Qualification coverage | For each unit/qualification pair, capped holders = min(valid available holders, required holders); coverage = sum(capped holders) / sum(required holders) | A coverage indicator. One person may hold several qualifications, so this does not prove simultaneous billet coverage |
| Current gap | Valid available holders below the requirement | Show missing holder count and affected unit/qualification pair |
| Fragile coverage | Requirement is currently met but there is no surplus holder | Separately flag a single-holder dependency when the required count and valid count are both one |
| 30/60/90-day expiration count | Currently valid certificates expiring on or before `as_of_date + N days` | Cumulative windows; also show distinct affected people. Do not count already-expired certificates as upcoming |
| Projected qualification gap | Remove certificates expiring by the horizon and recalculate coverage | A no-renewal scenario assuming unchanged staffing/availability; not an ML prediction |
| Completed-case discrepancy rate | Completed cases requiring correction / all completed cases in the selected period | Open cases have unknown outcomes and are excluded; zero denominator displays blank/not applicable |
| Completed-case cycle time | Median days from opened date to closed date for completed cases | Open cases appear separately as age/backlog; median is not an average |
| Unit attention flag | Staffing below requirement OR at least one qualification below requirement | A fictional business rule; label “readiness proxy,” not official readiness or deployability |

Always present staffing and qualification coverage separately. Do not create an unexplained composite readiness score. Keep totals comparable across SQL and Power BI. Explain that holder counts do not solve competing assignments or simultaneous coverage constraints.

### Synthetic-data discipline

Generate random background variation and documented fictional scenarios: one staffing shortfall, one fragile qualification, a renewal cluster, and one process discrepancy hotspot. Make those scenarios traceable to configuration, rather than concealing planted patterns as discoveries.

Produce a clean reference dataset and a separate dirty input version with a small, documented set of duplicate keys, missing required values, invalid dates, and broken foreign keys. The pipeline must detect, quarantine, or reject them. Never silently fill a missing critical identifier or manufacture a certificate date.

Findings describe the **simulation**. Write “In this fictional scenario, Unit C has…” rather than “Navy units have…” Synthetic data demonstrates system behavior; it does not establish real-world effects, official readiness, or predictive validity.

### MVP acceptance checklist

- [ ] From a clean checkout/folder, generate data, validate, load SQL, and export dashboard tables using documented steps.
- [ ] Critical validation errors stop the load or are explicitly quarantined; rejection counts are visible.
- [ ] SQL and dashboard totals match for staffing, qualification counts, expiration outlook, and discrepancy rate.
- [ ] At least three intentionally challenging cases are checked by hand: duplicate qualification, expiration boundary, and zero denominator.
- [ ] Executive, qualification, and process views work with clear labels and an analysis date. If time is short, combine them into one or two complete pages.
- [ ] Three to five findings have supporting counts, operational implications, proposed actions, and limits.
- [ ] README explains the fictional problem, methods, results, setup, and synthetic-data limitations.
- [ ] Screenshots and a PDF/static export back up the live demo.
- [ ] You can explain the grain, a SQL join, a data-quality failure, and one KPI in your own words.

## Workspace files and daily operating procedure

Have the execution workspace create this small structure. This is a proposed layout, not a claim that the repository already exists.

| Location | Purpose |
| --- | --- |
| `README.md` | Recruiter-facing problem, demo, findings, limitations, setup |
| `requirements.txt` | Actual Python dependencies used |
| `config/project.yml` | Seed, analysis date, size parameters, fictional scenario definitions |
| `src/generate_data.py` | Reproducible synthetic inputs |
| `src/validate_data.py` | Quality rules and reject/error report |
| `src/load_data.py` | Repeatable database load |
| `src/export_marts.py` | Dashboard-ready SQL outputs |
| `sql/schema.sql` | Keys, types, foreign keys, constraints |
| `sql/analytics.sql` | Business calculations and views |
| `tests/` | Small meaningful checks for data and metric boundaries |
| `data/raw/`, `data/processed/`, `data/rejected/` | Inputs, accepted data, rejected records; regeneration documented |
| `powerbi/` | Actual report when available, measure definitions, screenshots, static export |
| `docs/charter.md`, `docs/metric_contract.md`, `docs/data_dictionary.md` | Approved scope, definitions, field meanings |
| `docs/decisions.md`, `docs/progress.md`, `docs/interview_feedback.md` | Decisions, resumable daily status, employer feedback |
| `docs/executive_brief.md`, `docs/demo_script.md` | Decision narrative and walkthrough |

At the start of each session, read charter, latest progress, and decisions. Identify the next unmet acceptance criterion. At the end, record actual output paths, verification performed, remaining risk, and the first action for the next session. Commit a coherent local checkpoint if Git is initialized. Push only to the user's intended remote when that is part of the authorized workflow. Git history supports progress but does not by itself create a remote backup.

## Phase 1: daily flagship MVP sprint — October 7–19

| Day/date | Execution steps | Output and completion check |
| --- | --- | --- |
| 1 · Wed Oct 7 | Confirm available hours, Python/Git/database access, and local Power BI access. Write the charter and the six-table design. Create the project structure and progress log. Attend the supplied host-company preview if applicable; record role-relevant needs. | Charter, setup inventory, schema sketch. You can name the audience, decision, data grain, scope, and any tool blocker. Database fallback decision made within one session. |
| 2 · Thu Oct 8 | Write the metric contract. Generate the clean synthetic tables with a fixed seed and four documented scenarios. Check keys and relationships. Capture relevant preview notes. | Generator plus data dictionary draft. Running twice yields identical rows for the same configuration; no accidental broken relationships. |
| 3 · Fri Oct 9 | Generate a separate dirty input set. Implement key, missing-value, foreign-key, and date checks. Define reject/fail behavior. Attend the preview if applicable. | Validation report. Each injected error is detected; accepted/rejected input counts reconcile. |
| 4 · Sat Oct 10 | Implement schema and database load. Add constraints and an idempotent reload process. Load validated records and inspect table counts. | Working SQL database. A second run does not duplicate data; table counts agree with accepted inputs. |
| 5 · Sun Oct 11 | Write SQL for staffing coverage, qualification holders, current gaps, fragile coverage, and expiration windows. Hand-check a small unit. Export dashboard tables with explicit grain. | KPI SQL and CSV/view outputs. Counts are correct before Power BI enters the process; the duplicate-holder trap is checked. |
| 6 · Mon Oct 12 | Build one Power BI executive page from these outputs. Show analysis date, staffing count/requirement, qualification coverage, flagged units, and a unit comparison. Draft the README opening and a brief concept diagram. | A functioning page, saved screenshot, and honest prototype description. At least one filter works; its totals reconcile to SQL. |
| 7 · Tue Oct 13 | Spend the first block on fixing the prototype and rehearsing a 30–60 second explanation. Attend the Meet & Greet shown on the calendar. Record employer questions and needs immediately afterward. | **Prototype gate.** You can show real output. Record capabilities as built/in progress/planned; no claims that unbuilt ML exists. |
| 8 · Wed Oct 14 | Attend Prep & Resume Workshop. Build the qualification view: current gaps, fragile coverage, distinct affected people, and cumulative 30/60/90 expirations. | Qualification page plus accurate project résumé wording if justified. Boundary dates and duplicate holders give correct results. |
| 9 · Thu Oct 15 | Attend the elevator-pitch session. Build the process view with volume, completed-case discrepancy rate, median completed cycle time, and open-case age. Practice the pitch using your actual implementation. | Process page and concise explanation. Open cases are excluded from completed-case outcome metrics; no misleading denominator. |
| 10 · Fri Oct 16 | Add the no-renewal qualification scenario. Document assumptions. Reconcile all pages against SQL, including filtered units and empty selections. Write the first three scenario findings. | Reconciliation notes and first findings. Every visible KPI has a definition and traceable SQL result. |
| 11 · Sat Oct 17 | Write setup instructions, dictionary, limitations, and three to five recommendations. Add pipeline orchestration/documented run order. Create targeted checks for key metric boundaries. | Reproducible run instructions and executive brief. Each recommendation cites observed simulated evidence and states what remains unproven. |
| 12 · Sun Oct 18 | Rebuild from a fresh folder/environment. Run the entire workflow. Rehearse a two-minute demo and a five-minute technical explanation. Save screenshots/static export. Fix high-impact problems only. | Full rehearsal report and offline demo. You can explain one join, one validation rule, one KPI, and one limitation without reading generated prose. |
| 13 · Mon Oct 19 | Complete the acceptance checklist before evening. Attend HoH activities shown for the day if applicable. Freeze the MVP, save an identifiable release checkpoint, and prepare the interview package. | **MVP gate.** Working end-to-end pipeline, complete report, README, findings, and backup demo. If a criterion fails, label it explicitly and ship the reduced complete scope. |

### If the MVP falls behind

Use these cuts in order: optional styling, additional chart types, extra dimensions, PostgreSQL migration if using the fallback, extra historical process detail, then combine dashboard pages. Retain the pipeline, three core business questions, correct metrics, evidence, limitations, and one reliable demo. ML, dbt, cloud, and deployment remain outside the MVP.

If Power BI is blocked, ship validated SQL outputs and a clearly labeled static analytical report while repairing access. That is useful interim evidence, but the Power BI criterion remains incomplete. On October 13, report a partial prototype honestly rather than inventing a functioning page.

## Phase 2: daily flagship polish — October 20–30

Interview preparation and actual interviews supersede these build tasks. Move a displaced improvement into the next buffer session; do not miss an interview to preserve the table.

| Date | Execution steps | Completion check |
| --- | --- | --- |
| Tue Oct 20 | Interview window opens. Create a one-page project brief, two-minute demo, and tailored talking points for your next actual employer conversation. Inspect the packaged demo. | You can open the project in under one minute and state what you personally built. |
| Wed Oct 21 | Improve README navigation, setup instructions, architecture explanation, and field documentation. Remove unsupported claims. | Another reader can find the business problem, output, limitations, and run instructions quickly. |
| Thu Oct 22 | Protect time for the networking session shown on the calendar. Review one difficult SQL join and one denominator. Practice explaining how dirty inputs affect decisions. | Two technical explanations in your own words; event/feedback notes saved. |
| Fri Oct 23 | Act on the highest-value interview/preview feedback. Fix terminology, unclear measures, or confusing filters before adding features. | One evidenced improvement recorded, with a before/after explanation. |
| Sat Oct 24 | Improve repeatability, loader failure behavior, and visible data-quality reporting. Inspect whether configuration changes propagate consistently. | Failed input does not silently yield a misleading dashboard; configuration date is consistent across layers. |
| Sun Oct 25 | Refine report layout, labels, sort order, readable colors, and explanatory notes. Add one simple what-if renewal scenario only if core work is stable. | Each page leads to a decision; scenario outputs are labeled assumptions. |
| Mon Oct 26 | Prepare technical interview answers about grain, keys, joins, duplicates, missing values, tradeoffs, and limitations. Preserve calendar-listed HoH activity time. | Five-minute walkthrough practiced; one metric recomputed by hand. |
| Tue Oct 27 | Evaluate whether ML would add credible evidence now. Check for temporal observations, non-circular labels, leakage controls, and a meaningful decision. | A written go/no-go decision. Default: defer ML on a single synthetic snapshot. |
| Wed Oct 28 | If ML was deferred, improve horizon/scenario analysis and document it. If justified, scope a separate model experiment with honest simulation limits; do not displace release work. | A useful scenario or a defensible experiment charter. No claim of real-world predictive validation. |
| Thu Oct 29 | Run final reproduction and metric reconciliation. Finalize screenshots, executive brief, résumé bullet, and LinkedIn/GitHub presentation copy. | Artifacts reflect the final implementation and measured checks. Updating external profiles is a separate action. |
| Fri Oct 30 | Release the polished flagship checkpoint. Review capacity and employer feedback. Decide whether the complementary forecasting project should start. | **Flagship gate.** Core acceptance checks pass; master-chat report includes evidence and recommended next scope. |

### Why ML is conditional here

A 30-day risk label computed from today's expiration dates is often answered directly by SQL. Training a classifier to reproduce that same rule would add little evidence. A synthetic generator can also bake the answer into the inputs. Good performance then demonstrates the generator's assumptions, not useful operational prediction.

Build ML only when the task, target, chronology, feature availability, and evaluation justify it. A polished SQL/Power BI flagship without ML is a successful release. Your existing Student Performance project already provides foundational ML evidence.

## Phase 3: complementary civilian forecasting project — October 31–November 20

**Working title:** San Diego Service Demand Forecasting.

**Decision:** estimate next-week request volume for a small number of service categories to inform workload planning. Predicted request count is not automatically a staffing recommendation; handling time and staff productivity would be additional assumptions.

**Scope:** three to five service categories, weekly counts, one dependable public source, two report views, and a chronological evaluation. Prefer roughly two or more years of usable history if available. Dataset fields, access, license, update frequency, and suitable coverage must be checked at kickoff. Do not assume category labels, text descriptions, completion dates, or historical coverage exist merely because they appeared in an earlier idea.

**Methods:** last-week and, when history supports it, seasonal-naive baselines; then one simple alternative. Score on the same held-out dates using MAE and a documented aggregate measure such as WAPE where its denominator is nonzero. Avoid MAPE where counts can be zero. Compare categories and peak periods; do not promise a model will beat the baseline. A well-explained baseline win is a valid result.

Do not use random train/test splitting for this project. Reserve the newest block for final evaluation and use earlier rolling-origin folds for selection. Any imputation, scaling, lag construction, and tuning must respect time. A week with no observed rows may indicate an ingestion gap rather than zero demand. Demand records also reflect reporting behavior and access, not total community need.

| Date | Execution steps | Completion check |
| --- | --- | --- |
| Sat Oct 31 | Review flagship acceptance, employer interest, and actual weekly capacity. Draft the forecasting charter and narrow decision. | Start only if flagship is stable. Otherwise this day begins repair; later project dates become provisional. |
| Sun Nov 1 | Locate and inspect the current public source and documentation. Review access/license, fields, category stability, history, and date meanings. | Source feasibility recorded with provenance. If inadequate, choose a smaller supported question or defer; do not manufacture missing data. |
| Mon Nov 2 | Write ingestion for a small sample. Record source location, retrieval date, coverage, and file/schema checks. | Sample loads repeatably; timestamps and row grain are understood. |
| Tue Nov 3 | Fetch the chosen historical slice. Check duplicates, IDs, timestamp parsing, category missingness, and schema drift. | Accepted/rejected counts and coverage summary saved. |
| Wed Nov 4 | Build canonical request and weekly category-count tables. Document timezone, week boundaries, and zero-versus-missing rules. | SQL/Python aggregations reconcile on a small date range. |
| Thu Nov 5 | Explore volumes, seasonality, reporting changes, outliers, and category comparability. Reduce to three to five supported categories. | EDA identifies source limitations and locks the forecast scope. |
| Fri Nov 6 | Define prediction timing, horizon, available features, training period, validation folds, final holdout, and metrics. | Evaluation plan exists before fitting alternatives; holdout is untouched. |
| Sat Nov 7 | Implement last-week baseline and seasonal-naive baseline if sufficient history exists. Save predictions and error by category. | Baselines evaluated on identical dates with no future inputs. |
| Sun Nov 8 | Implement rolling-origin validation and inspect simple diagnostic plots. Check lag construction by hand. | Earliest/latest training and prediction dates prove the chronology; no random split. |
| Mon Nov 9 | Fit one simple alternative, such as a regularized lag/calendar regression. Learn preprocessing only from each training fold. | One model evaluated under the same protocol as baselines. |
| Tue Nov 10 | Compare validation results. Inspect categories, peaks, bias, and failures. Choose the simplest defensible option. | Selection rationale written; a baseline may be the selected model. |
| Wed Nov 11 | Buffer/light day for work, family, or Veterans Day commitments. Repair data issues or practice interviews. | Status and next action remain current; no forced feature expansion. |
| Thu Nov 12 | Create reproducible training/prediction steps and a model limitations note. Freeze selection before final holdout evaluation. | Outputs regenerate; tuning has not used the holdout. |
| Fri Nov 13 | Evaluate once on the final holdout. Report baseline comparison and failure patterns honestly. | Final metrics saved for identical category/date sets, with scope and denominators. |
| Sat Nov 14 | Build a small Power BI report or precise static analytical report: demand trends and forecast/error view. | Views reconcile to saved prediction outputs; training and evaluation periods are clearly marked. |
| Sun Nov 15 | Translate results into a workload-planning brief. State error consequences and what staffing assumptions would still be needed. | Three supported findings, a decision, and limits; no unsupported allocation claim. |
| Mon Nov 16 | Write README, source provenance, methodology, evaluation protocol, and reproducible steps. | Reader can see both the result and how it was tested. |
| Tue Nov 17 | Practice explaining seasonality, time splits, baselines, leakage, and why the selected method is sufficient. | Two-minute demo plus five-minute technical walkthrough in your words. |
| Wed Nov 18 | Reproduce from a clean folder. Check data coverage, model outputs, metrics, and report totals. | Reproduction passes or remaining blocker is explicit. |
| Thu Nov 19 | Fix high-impact issues, export backups, and prepare employer-specific explanations grounded in actual feedback. | Forecast portfolio package ready; no new model added for appearances. |
| Fri Nov 20 | Release the second project if checks pass. Assess the next employer-relevant gap. Send a checkpoint report to the master chat. | **Complementary-project gate.** If unfinished, report the true state and prioritize completion over a third project. |

## Phase 4: daily feedback-led closeout — November 21–December 3

Select **one** branch on November 21. These are talking-point adaptations based on the working employer bracket, not assertions about current vacancies.

| Evidence from actual conversations | Preferred branch | Bounded extension |
| --- | --- | --- |
| Readiness, data integration, or operational decision interest — e.g., GDIT, Booz Allen, PMAT, Accenture Federal | Deepen the flagship | One renewal/staffing scenario, clearer data-quality reporting, or one defensible analytical extension |
| Modeling/resource-allocation interest — e.g., SPA | Decision analysis | One small scenario comparison with assumptions; optimization only if you can define assignment constraints accurately |
| Aviation/predictive-maintenance interest — e.g., GA or Northrop | Maintenance feasibility study | Inspect a current public dataset; start a bounded engine-level baseline only if access and chronology are sound |
| Forecasting/process analytics interest — e.g., Indeed or Travelers | Deepen civilian evidence | Improve baseline comparison, error analysis, or a documented decision threshold |
| No clear demand, limited capacity, or unfinished work | Portfolio/interview polish | Complete existing work, practice SQL and demos, fix explanations; no third project |

An aviation branch is an optional **case study**, not a promise of a complete third flagship in this period. For engine sensor data, split by engine rather than randomly by rows, calculate remaining-life labels correctly, and keep evaluation engines isolated. Inspect the current dataset and documentation before selecting it. Do not infer production aircraft safety from a benchmark dataset.

| Date | Execution steps | Completion check |
| --- | --- | --- |
| Sat Nov 21 | Choose one branch from recorded interview feedback. Write a one-page extension charter with a five-session implementation cap. | Decision states employer relevance, evidence, completion criterion, and cut line. |
| Sun Nov 22 | Inspect needed data/assumptions and establish a simplest baseline or scenario. If data access fails, switch to polish. | Feasibility demonstrated without creating another broad project. |
| Mon Nov 23 | Implement the branch's smallest analytical output. Reserve time for interview preparation. | One working output you can explain. |
| Tue Nov 24 | Validate that output against known values, a baseline, or documented assumptions. | Correctness/evaluation evidence saved. |
| Wed Nov 25 | Check remaining interviews and decide whether the extension deserves release. Drop low-value unfinished extras. | Existing demo remains stable; no speculative feature drives the schedule. |
| Thu Nov 26 | Thanksgiving/family buffer. Optional brief status update only. | No required new artifact. |
| Fri Nov 27 | Light buffer or interview catch-up. Record current employer needs and next conversations. | Updated feedback log; core package remains ready. |
| Sat Nov 28 | Finish the selected extension or use the session to repair/polish the two main projects. | One completed, defensible addition or a stronger existing release. |
| Sun Nov 29 | Run clean reproduction and final reconciliations. Archive stable demos and static backups. | Neither project depends on undocumented local steps. |
| Mon Nov 30 | Rehearse tailored interview stories and technical questions. Review résumé/Featured wording against built evidence. | Claims are accurate and demonstrations open quickly. |
| Tue Dec 1 | Fix only issues that impair comprehension, correctness, or demo reliability. | No new scope; priority defects resolved. |
| Wed Dec 2 | Prepare final interview materials and a project handoff summary. Practice the hardest explanation once. | Offline backup and final links/files ready. |
| Thu Dec 3 | Interview window closes as supplied. Freeze portfolio, report outcomes and unresolved gaps, and choose post-window priorities. | **Window closeout.** Evidence and actual interview results recorded; no need to manufacture a third project. |

## After December 3

Do not pre-commit to another daily 90-day build sprint before employer feedback arrives. Use these weekly objectives, then generate a fresh daily plan in the execution workspace.

| Period | Objective |
| --- | --- |
| Dec 4–10 | Record matching/interview outcomes and align the next learning task with the likely host and role. Repair any remaining reproduction issues. |
| Dec 11–17 | Deepen the most relevant tool or analytical method using an existing project. Keep evidence of what changed and why. |
| Dec 18–24 | Prepare a bounded maintenance case study only if useful; otherwise practice SQL, explanation, and host-relevant workflow. |
| Dec 25–31 | Holiday buffer and light review. If capacity allows, begin the education/economic-growth question, literature map, and source feasibility only. |
| Jan 1–4 | Final portfolio and résumé consistency review. No large new feature required for the earlier Day 90 checkpoint. |
| Jan 5–10 | Complete host-specific onboarding preparation and questions. Prioritize information provided by HoH/host over this provisional schedule. |

Education/economic-growth remains a longer-term research project. Scope the causal versus predictive question, data availability, panel construction, and limitations before committing to a completion deadline.

## Progress, feedback, and control templates

### Daily log — append to `docs/progress.md`

```text
Date / actual focused hours:
Today's objective:
Completed artifacts and paths:
Verification and result:
What I can now explain independently:
Blocked / incomplete:
Scope decisions or new assumptions:
Next session's first action:
Current gate: prototype / MVP / polish / forecasting / closeout
```

### Employer feedback — append to `docs/interview_feedback.md`

```text
Company / role / conversation date:
Question or need they actually expressed:
Evidence I showed:
Where my explanation or evidence was weak:
Potential improvement:
Estimated effort / interview value:
Follow-up deadline, if any:
Decision: improve now / backlog / no action
```

### Checkpoint report — paste into the master chat

```text
PROJECT CHECKPOINT — [date]
Project / release state:
Original gate / actual outcome:
Built and verified:
Evidence locations:
Hours used / remaining capacity:
What I can demonstrate and explain:
Known limitations or failed checks:
Employer feedback that changes priorities:
Recommended next step:
Scope decision needed, if any:
Next checkpoint:
```

Routine implementation decisions stay in the execution workspace. Bring back changes to project priority, target audience, completion deadline, database/tool strategy with major effort implications, new model scope, or a new project. Keep useful ideas in a backlog with a reason and estimated effort instead of slipping them into today's build.

## Copy/paste launch prompt for the new execution workspace

```text
This is the execution workspace for my SkillBridge portfolio. Use the attached
SkillBridge_Project_Execution_Plan.md as the initial project charter and schedule.
My existing brainstorming chat remains the master record for portfolio priorities,
career alignment, and major scope changes. Do not assume you can read updates from
that chat; I will bring checkpoint reports and decisions between the workspaces.

My immediate objective is to build Operational Readiness Intelligence using
fictional/synthetic operational data, Python, SQL, and Power BI. The milestones
are a visible prototype by October 13, 2026, an interview-ready MVP by Monday,
October 19, and a polished flagship by October 30. The HoH interview window is
October 20–December 3. Project value, correctness, explainability, and interview
readiness take precedence over project count or algorithm count.

My background: B.S. Mathematics; active-duty Navy operational and administrative
data experience; Python, SQL, pandas, NumPy, Excel/Power Query, Power BI, Git,
and ML coursework including regression, trees/ensembles, and neural networks.
I am transitioning toward analyst/BI roles and applied data science, with
California required and San Diego preferred. Do not equate coursework with
professional implementation experience. I need to understand and own the work
well enough to explain it in an interview.

Start by reading the attached plan and inspecting the existing workspace for
project instructions and files. State the current date, determine the applicable
phase, and resume existing work if present. If this is a new project, complete
Day 1: charter, metric contract outline, six-table schema sketch, environment
inventory, project structure, and progress/decision logs. Proceed with routine
choices autonomously; ask only for missing facts that materially block work.
If available hours are unknown, use the plan's provisional two-hour weekday
and three-to-four-hour weekend assumption while making that assumption explicit.

Check database and Power BI access immediately. Power BI Desktop may need to run
on my Windows computer; tell me the exact local build steps and have me perform
them when your environment cannot. Never claim to have created or verified a
PBIX file unless you actually did. Use SQLite/CSV as the documented fallback if
PostgreSQL setup consumes more than one session. Do not let infrastructure or
styling displace the MVP.

Work one daily milestone at a time. Give each session a concrete output and
completion check. Help implement the code, SQL, validation, documentation, and
report build instructions, while explaining the key choices and checking that
I can understand the important calculations. Do not silently expand to cloud,
dbt, ML, extra datasets, or additional projects. All findings must be identified
as simulated; readiness measures are fictional proxies, not official Navy rules.
Before any predictive extension, assess label validity, chronology, leakage,
baseline value, and whether the proposed task is already solved by a SQL rule.

Maintain docs/charter.md, docs/metric_contract.md, docs/decisions.md,
docs/progress.md, and docs/interview_feedback.md. End each session with completed
artifact paths, verification results, blockers, and the next exact action.
At release gates, produce the checkpoint report from the plan for me to paste
back into the master chat. If starting late or falling behind, propose the
smallest complete scope that protects interview readiness and record the change.

Begin the current day's work now. This request is to execute the next milestone,
not simply to repeat or redesign the entire plan.
```

