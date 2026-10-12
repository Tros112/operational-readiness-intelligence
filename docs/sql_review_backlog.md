# SQL ownership review — carried toward the interview-ready release

On October 11, the user acknowledged needing to review SQL basics and explicitly requested Day 6. Day 5 technical implementation/reproduction has passed. Independent ownership of the three concepts below remains **needs refinement**; this is a learning item, not an observed implementation defect or a reason to repeat successful technical checks.

| Concept | Rule in this project | Small review example |
| --- | --- | --- |
| Zero-holder requirements | Requirements LEFT JOIN eligible holder totals; COALESCE missing totals to zero | A requirement for two holders still has gap two if no holder matches. An inner join hides that requirement. LEFT JOIN does not enforce uniqueness. |
| Person versus certificate grain | Aggregate staffing directly from personnel before joining certificate summaries | One person with three different certificates has three valid person/qualification pairs and may appear in three joined rows, while staffing remains one person. Source keys can all be unique. |
| Unmet versus fragile | Unmet: fewer eligible holders than required. Fragile: positive demand met exactly with no surplus | 1/2 is unmet; 2/2 is fragile; 3/2 has surplus. The flag is unrelated to query success or an overall claim of unit viability. |

Reference `docs/sql_walkthrough.md`, `sql/qualification_detail.sql`, and the `staff` CTE in `sql/unit_summary.sql`. Before interview-ready release, explain an unseen example in your own words. A generated explanation or completed Python test does not satisfy this ownership item. Do not add a new SQL course or change the portfolio schedule silently; use the existing project examples when reviewing.


Day 7 follow-up, October 12: the user independently adds the correct Unit D example (117.5% staffing versus 87.5% qualification holder-slot coverage) and explains that multiple qualifications on one person do not establish simultaneous-assignment capacity. Confirm those specific metric/limitation explanations. The three SQL concepts above have not been independently revisited in an unseen example; keep their needs-refinement state rather than inferring mastery from the prototype gate. Day 7 technical prototype acceptance is complete and does not require successful implementation runs to be repeated.
