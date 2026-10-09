# Windows Power BI handoff

**Current status, October 9, Day 5:** user confirms Windows Power BI Desktop **2.158.1177.0, 64-bit (September 2026)**. Day 2 staffing review is complete, and at 04:38 PDT the user confirmed the existing learning report still opens/functions. SQL exports now exist and are verified on Linux; first finish `docs/day05_windows_handoff.md`. This document's prepared field mappings are aligned with those actual exports. The Day 6 build below remains unexecuted and requires the next milestone instruction. Desktop cannot run in the assistant's Linux environment; no PBIX has been created, opened, or verified by the assistant. Production SQL/Power BI reconciliation remains pending.

## Completed: Day 1 access check (user-reported)

The user completed this check on October 7. Retain these steps for reference; no repeat is needed unless access changes.

1. On your Windows computer, open Start and launch **Power BI Desktop**. If absent, use Microsoft's [installation guide](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop): open the Power BI Desktop Microsoft Store page and select Install, or use the linked 64-bit installer. Use the standard Desktop application.
2. Open a **blank report**. On the Help ribbon, select **About** and note the Version line.
3. Create a folder such as `C:\Users\<your-user>\Documents\Operational_Readiness_Intelligence\powerbi`. When using the project ZIP, extract it to Documents; the included project folder is `operational_readiness_intelligence`.
4. On the blank report, select **Insert → Text box** and enter `Operational Readiness Intelligence — simulated`. Add `Setup only: no operational data loaded` below it.
5. Select **File → Save as**, save as `Operational_Readiness_Intelligence.pbix` in that project's `powerbi` folder, close it, then reopen it.
6. Return this brief result to this workspace: `Desktop version: ...; blank report opens: yes/no; saved and reopened: yes/no; blocker: ...`.

This is an **access check**, not the October 13 prototype. A user-reported save does not mean the assistant has inspected the report. No cloud publishing or service setup is needed for today's task.

## Day 6 local build: run only after verified SQL exports arrive

**Day 2 learning preview — complete:** `powerbi/day02_staffing_review.md` documents the two-table clean-reference staffing view, four measures, expected totals, and six-source relationship map. October 8 evidence confirms global and Unit C slicer-selected values, relationship settings, the user's aggregate-versus-local explanation, and user-reported save/reopen. Day 3/4 are complete; Windows Day 5 SQL-export checks remain next. Release dates are unchanged. No PBIX is claimed as created or inspected by the assistant.

The following uses the **implemented Day 5 export contract**. The CSV is verified on Linux; verify it on Windows before any import. Report measures and visuals below are prepared instructions, not Power BI verification evidence.

File: `data/processed/dashboard/unit_summary.csv`. Grain: **one row per unit at the fixed analysis date** (six rows before filtering). Only use a passed `export_manifest.json` with exports_ready true, date October 7, and matching hashes. Exact fields/types are in `docs/export_dictionary.md`.

Fields used here: `as_of_date`, `unit_id`, `unit_name`, `available_personnel_count`, `required_personnel_count`, `capped_holder_slots`, `required_holder_slots`, `qualification_pairs_with_gap`, `unit_attention_flag`. The CSV also contains the synthetic classification, staffing gap, other count components, two row ratios, and cumulative expiration counts.

1. Continue in the existing Windows project with your existing `.venv` and local report. After Day 5 verification and the Day 6 instruction, open your PBIX. Rename the target page **Executive — simulated**. Keep the earlier learning page if needed for reference.
2. Select **Home → Get data → Text/CSV**. Choose the actual `unit_summary.csv`. Select **Transform Data**. The Text/CSV import procedure is documented by [Microsoft](https://learn.microsoft.com/en-us/power-query/connectors/text-csv).
3. Name the query `unit_summary`. Set `as_of_date` to Date, IDs/names/classification to Text, count/flag fields to Whole Number, and ratio fields to Decimal Number with blanks retained. Confirm six unique `unit_id` values and a single `as_of_date`. Use **Close & Apply**. Do not clean away validation errors in Power Query; return them to the pipeline.
4. This first page uses one summary table, so no relationships are required yet. Create each measure below with **New measure**. These definitions are prepared but have not been run in Power BI.

```dax
Available Personnel = SUM(unit_summary[available_personnel_count])

Required Personnel = SUM(unit_summary[required_personnel_count])

Staffing Coverage = DIVIDE([Available Personnel], [Required Personnel])

Qualification Coverage =
    DIVIDE(
        SUM(unit_summary[capped_holder_slots]),
        SUM(unit_summary[required_holder_slots])
    )

Flagged Units =
    COUNTROWS(FILTER(unit_summary, unit_summary[unit_attention_flag] = 1)) + 0

Analysis Date = MAX(unit_summary[as_of_date])
```

5. Format the two coverage measures as percentages; show staffing coverage uncapped. Keep counts as whole numbers and the date as a readable date.
6. Add cards for analysis date, available personnel, required personnel, staffing coverage, qualification coverage, and flagged units. Title the flag card **Units needing attention — fictional proxy**.
7. Add a **Table** visual with unit name, available/required personnel, staffing coverage, qualification coverage, and `qualification_pairs_with_gap`. Add a **Slicer** using unit name. Use the explicit measures for percentages, never an average of row percentages.
8. Retain a visible note: `Synthetic operational data. Qualification coverage does not establish simultaneous staffing assignments. No-renewal outlook is a scenario.`
9. Before styling, compare unfiltered and selected-unit cards with `docs/verification_day05.md` and the verified CSV. Global: 254/250 staffing, 88/95 qualification coverage, four units needing attention. Unit C: 40/50 staffing, 15/16 qualification coverage, one unit needing attention. Clear the slicer and confirm the original totals return. These are expected SQL values; they have not been verified in the production Power BI page. Inspect text, dates, counts, and screenshot readability.
10. Save the actual PBIX, capture the page in `powerbi/screenshots/executive.png`, and record the selected-unit/global check results in progress. Provide a screenshot and actual report evidence for review. Qualification/process pages remain later milestones.

If access is blocked, record the exact error. SQL/CSV work can proceed while access is repaired. A static analytical report would be interim evidence; the Power BI release criterion remains incomplete.

Sources checked October 7, 2026: Microsoft's installation guide and Text/CSV connector instructions linked above. They support the access/import steps; the report layout and metric choices are this project's design.
