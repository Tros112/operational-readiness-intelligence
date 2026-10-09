# Windows Power BI handoff

**Current status, October 8:** user confirms Windows Power BI Desktop **2.158.1177.0, 64-bit (September 2026)**; blank report opens, saved/reopened, no blocker. Access evidence: `docs/powerbi_access.json`. The Day 2 staffing screenshot matches expected matrix totals and selected Unit C cards; evidence is `powerbi/screenshots/day02_staffing_review.png`. Model settings, slicer/reset checks, and save/reopen of that populated report remain unconfirmed. Desktop cannot run in the assistant's Linux environment; the assistant has not created, opened, or verified a PBIX. No SQL export exists yet.

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

**Day 2 learning preview:** at the user's October 7 request to inspect relationships in Power BI, `powerbi/day02_staffing_review.md` provides a two-table clean-reference staffing view, four prepared measures, expected per-unit/filtered totals, and the six-source relationship map. The October 8 screenshot and the user's explanation confirm the displayed staffing counts and aggregate-versus-local interpretation. Finish the remaining local relationship/slicer/save checks in that guide. The production SQL export/reconciliation sequence below and release dates are unchanged. No new PBIX is claimed as created or inspected by the assistant.

The following is the **planned executive export contract**, not a claim the file has been produced or its calculations checked. On Day 5, compare actual export fields with this contract before proceeding.

File: `data/processed/marts/unit_summary.csv`. Grain: **one row per unit at the fixed analysis date** (six rows before filtering).

Expected fields: `as_of_date`, `unit_id`, `unit_name`, `available_personnel_count`, `required_personnel_count`, `capped_holder_count`, `required_holder_count`, `qualification_gap_pair_count`, `unit_attention_flag`.

1. Copy the provided project/export folder to your Windows computer. Open your PBIX. Rename the first page **Executive — simulated**.
2. Select **Home → Get data → Text/CSV**. Choose the actual `unit_summary.csv`. Select **Transform Data**. The Text/CSV import procedure is documented by [Microsoft](https://learn.microsoft.com/en-us/power-query/connectors/text-csv).
3. Name the query `unit_summary`. Set `as_of_date` to Date, `unit_id`/`unit_name` to Text, and every count/flag field to Whole Number. Confirm six unique `unit_id` values and a single `as_of_date`. Use **Close & Apply**. Do not clean away validation errors in Power Query; return them to the pipeline.
4. This first page uses one summary table, so no relationships are required yet. Create each measure below with **New measure**. These definitions are prepared but have not been run in Power BI.

```dax
Available Personnel = SUM(unit_summary[available_personnel_count])

Required Personnel = SUM(unit_summary[required_personnel_count])

Staffing Coverage = DIVIDE([Available Personnel], [Required Personnel])

Qualification Coverage =
    DIVIDE(
        SUM(unit_summary[capped_holder_count]),
        SUM(unit_summary[required_holder_count])
    )

Flagged Units =
    COUNTROWS(FILTER(unit_summary, unit_summary[unit_attention_flag] = 1)) + 0

Analysis Date = MAX(unit_summary[as_of_date])
```

5. Format the two coverage measures as percentages; show staffing coverage uncapped. Keep counts as whole numbers and the date as a readable date.
6. Add cards for analysis date, available personnel, required personnel, staffing coverage, qualification coverage, and flagged units. Title the flag card **Units needing attention — fictional proxy**.
7. Add a **Table** visual with unit name, available/required personnel, staffing coverage, qualification coverage, and qualification gap pair count. Add a **Slicer** using unit name. Use the explicit measures for percentages, never an average of row percentages.
8. Retain a visible note: `Synthetic operational data. Qualification coverage does not establish simultaneous staffing assignments. No-renewal outlook is a scenario.`
9. Before styling, compare unfiltered and selected-unit cards with the SQL reconciliation sheet supplied with the export. Clear the slicer and confirm the original totals return. Inspect text, dates, counts, and screenshot readability.
10. Save the actual PBIX, capture the page in `powerbi/screenshots/executive.png`, and record the selected-unit/global check results in progress. Provide a screenshot and actual report evidence for review. Qualification/process pages remain later milestones.

If access is blocked, record the exact error. SQL/CSV work can proceed while access is repaired. A static analytical report would be interim evidence; the Power BI release criterion remains incomplete.

Sources checked October 7, 2026: Microsoft's installation guide and Text/CSV connector instructions linked above. They support the access/import steps; the report layout and metric choices are this project's design.
