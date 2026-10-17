# Day 8 qualification/expiration verification

Started **October 13, 2026**, under the user's explicit instruction, early relative to October 14. The October 7 synthetic snapshot, fictional readiness proxies, six operational sources, SQLite/CSV strategy, audience, and release dates are unchanged. The Day 7 prototype gate remains passed; MVP/polish remain open.

**Current status: global, D/Q04, C/Q06, B/Q03, combined A+C/Q01+Q02, and display-cleanup checks accepted; clear/empty/interactions, save/reopen, and remaining ownership pending.** The local execution environment was unavailable during preparation. At that stage no native command/file-system execution, current local dataset/hash check, Python/SQL/PowerShell run, M/DAX compilation, or actual PBIX operation was claimed. Read the immutable public baseline **9fdd5a39c7f4065c446303f20e5e1da74b37572f** through the connected GitHub interface. Root AGENTS is the only instruction file in that tree. Native execution returned for the follow-up below; this does not change the historical preparation boundary.

## Prepared files and model

| Asset | Purpose | Preparation boundary (historical; follow-ups below) |
| --- | --- | --- |
| powerbi/qualification_detail.pq | Approved 48-row/13-column pair import; counts/capping/gaps/ratio/fragility, date and unique grain gates | Not executed in M |
| powerbi/qualification_filter.pq | Eight unique qualification ID/name rows derived from approved pairs | Not loaded or linked in Desktop |
| powerbi/expiration_detail.pq | Approved 193-row/14-column current inventory; validity/days/inclusive flags, grain and identity checks | Not executed in M |
| powerbi/qualification_measures.dax | Sixteen scoped ORI Q measures, including distinct people per window and blank undefined values | Not executed in DAX |
| docs/day08_windows_handoff.md | Existing-folder import, four-relationship model, page, checks, and truthful project résumé wording | User build/evidence pending |
| docs/day08_reconciliation.md | Prior known references and a read-only selected-CSV PowerShell reference | PowerShell not executed |
| docs/qualification_check.json | Machine-readable static results, previous evidence, and pending runtime state | Preparation status, not page acceptance |

Reuse six-row unit_summary as the one-side unit lookup. The eight-row qualification_filter is another one side. Both filter qualification_detail and expiration_detail through four active 1:* Single relationships; no fact-to-fact link/merge or connection to the older learning tables is added. Source rows retain their grains. Original executive/learning measures stay intact; new qualification-specific formulas use pair detail, while inventory formulas use certificate detail.

The M gates validate integers before Int64 conversion, keep all 48 demands, check capped counts/gap/ratio/fragility, retain both inventory availability states, and verify exclusive current validity with inclusive cumulative flags. A distinct projection builds lookup rows; it does not silently deduplicate fact data. Python preflight still supplies SHA-256 immediately before import/refresh, with stable files between steps. M does not hash, and the filesystem procedure is not atomic.

## Static/reference verification performed

- Read governing files, source milestone, metric/export dictionaries, SQL, existing checker/import source, prior analytical audits/tests, and current report status at the pinned baseline.
- Confirmed exact 13/14-column schemas and grains, sixteen unique measure names, and valid DAX source-column references. Coverage divides summed capped slots by summed demand; window people use DISTINCTCOUNT with KEEPFILTERS, not summed category people totals.
- JSON parsing, whitespace, and relative file links pass. Git blob hashes for eighteen read source files match the pinned tree; prepared UTF-8 contents are hashed for publication checks. These checks use the orchestration JavaScript environment, not a native filesystem or M/DAX engine.
- Seven **JavaScript teaching-reference cases** pass: capped weighted coverage, unmet-versus-fragile, surplus, undefined demand, inclusive 30/60/90 boundaries, unavailable inventory, and distinct/empty selections. These are mathematical reference checks, not M/DAX/PowerShell tests, and are not findings in the live reference.
- Prior SQL evidence supplies global 88/95 = 92.63%, seven missing slots/seven gap pairs, inventory 193 certificates/145 people, and cumulative certificate/people values 45/41, 68/62, 98/84. B/Q03 and C/Q06 distinguish met fragility from an existing gap. Existing test code and its recorded prior passes establish exactly six D/Q04 inventory rows at days 7/10/14/20/25/30; each window includes all six people.
- The prior audit does not report global fragile-pair totals. The prepared Windows CSV reference derives those and new multi-selection results rather than inventing values.
- Reviewed primary Microsoft relationship, distinct-count/filter, and M-type documentation. This establishes documented semantics, not execution in the user's report.

Existing **49 Python tests** previously passed on Linux and screenshot-verified Windows. Python/SQL/test definitions are unchanged; those tests do not compile the new M/DAX. No new runtime pass, live export reconciliation, or local hash-preservation claim is added for this unavailable session.

## Publication and remaining checks

Prepared code/text publication is within the user's standing scope. Build a normal commit from fresh public main and verify the parent, complete tree, changed path set, and blob contents through GitHub before reporting delivery. Preserve every other remote path and excluded image/generated/binary/private-history asset. No native fetch or branch alignment is possible/claimed here; existing native private archives are not accessed or pushed.

First user review: passed input checker, imported 48/13 and 193/14 facts plus 8/2 lookup, correct types/date/classification, and four active Single relationships. Then inspect page measures and shared slicer scopes against the read-only reference, selected B/C/D cases, multiple qualifications/units, boundary counts, clear/empty behavior, and report save/reopen including earlier pages. Exact Desktop definitions and actual PBIX internals remain uninspected until evidence establishes them.

Keep distinct-person/overlapping-window and unmet/fragile ownership explanations specific. Carried zero-holder join/person-certificate grain review is not marked mastered by generated code or reference checks. Workshop/event attendance, employer feedback, and actual hours remain unreported. Stop at Day 8 acceptance; process metrics/view are Day 9 and the no-renewal gap is Day 10.

## October 13, 20:54 PDT screenshot follow-up

Successfully read all three supplied scratch images without copying or publishing them:

- image(20261014-034237).png: Manage relationships, eight relationships with cardinality/direction/status visible.
- image(20261014-034351).png: Model view with the same new tables and active/inactive paths.
- image(20261014-034917).png: checker output ending status passed, files_checked 3, unique grains true, rows 6/48/193, file_writes 0, and powerbi_execution_verified false. It returns to the existing Windows project prompt. Individual hashes and explicit exit code are outside the crop.

Both qualification_filter-to-detail links are active 1:* Single and match the intended model. Both unit_summary-to-detail links exist as inactive 1:* Single. Unintended active links connect each detail to old units; an extra inactive link joins expiration_detail[person_id] to personnel[person_id]. Keep the original active units-to-personnel relationship. The model checkpoint therefore **does not pass yet**: the intended unit_summary slicer has no active path to the two new facts.

The three new tables are visible; their imported row/column counts, types, actual M source, and new DAX measures are not shown. Accept the passed checker without treating source CSV counts as imported counts. No new page, filter reconciliation, ownership explanation, or save/reopen result is established.

Native fetch and fast-forward aligned clean local main with prepared public commit 45397ca736b3e83a2091b7b0dc44750148cc17f7 (parent 9fdd5a39c7f4065c446303f20e5e1da74b37572f, tree 5c55fd84cf3847211e99c217303d8889a25f3d9a). This follow-up reads project text and images only; no current operational data read, regeneration, pipeline/test execution, M/DAX/PowerShell execution, or PBIX operation is claimed. Prior successful tests remain prior evidence.

The handoff now names the three connections to delete and two to activate. Next obtain the corrected Manage relationships view and a one-line import count/type confirmation; do not repeat the input checker for relationship-only edits. Then proceed to measures/page/reconciliation. Day 8 and the MVP/polish gates remain open; the accepted prototype gate and specific SQL ownership backlog are unchanged.

## October 13, 21:13 PDT relationship follow-up

Read image(20261014-041036).png and image(20261014-041325).png directly from the supplied scratch paths; neither image was copied or published. Manage relationships lists six active 1:* Single relationships. Both unit_summary links and both qualification_filter links match the required four-link model. The original units-to-personnel link remains. The prior expiration-to-units and expiration-to-personnel links are absent. One unintended active qualification_detail[unit_id]-to-units[unit_id] link remains; delete only that fifth listed row. No cause for the configuration is inferred, and an extra relationship alone is not evidence of duplicated source rows or inflated displayed counts.

The model checkpoint stays open pending that last removal and imported count/type confirmation. Neither image establishes import counts/types, exact M/DAX definitions, page metrics, save/reopen, or new ownership. The prior passed input check is accepted without a rerun. No pipeline/tests or operational data reads/writes are needed for these documentation and relationship instructions. Existing metric definitions, prototype acceptance, carried SQL review, and later release gates are unchanged.

## October 13, 21:29 PDT relationships and import counts accepted

Inspected four new images directly from scratch without copying or publishing them:

- image(20261014-042424).png shows exactly five active 1:* Single relationships: both unit_summary-to-detail links, both qualification_filter-to-detail links, and the original units-to-personnel link. The last unintended link is gone. The model relationship check passes.
- image(20261014-042636).png shows qualification_detail with 48 rows.
- image(20261014-042700).png shows qualification_filter with eight entries Q01-Q08 and its two expected ID/name columns.
- image(20261014-042731).png shows expiration_detail with 193 rows and visible synthetic_only, October 7 date, text IDs/names, dates, numeric availability/day-offset/window entries. This is visible data/formatting, not selected-column type metadata or verification of every row.

The user explicitly states “All import counts are accurate.” In the context of the requested 48/13, 8/2, and 193/14 checks, accept those imported row/column counts as user-confirmed, with the visible row/lookup evidence above. Do not convert a count-only confirmation into an independent type inspection or exact M-source verification. Continue with the existing type check during measure creation; no additional relationship-only screenshot or repeated checker is needed.

The prior checker pass remains accepted. No new DAX/page results, filter/boundary/empty check, save/reopen, independent ownership explanation, focused hours, or event feedback is supplied. Next create the sixteen ORI Q measures and the Qualification — simulated page, then review unfiltered current coverage/inventory/date/windows against the prior SQL references before selected cases. Global fragile-pair totals still come from the approved CSV reference, not an invented expected number. No code/data/metric change or pipeline/test rerun; Day 8 and later release gates remain open.

## October 14, 20:48 PDT global report display accepted

Read image(20261015-034810).png directly from its supplied scratch path without copying or publishing it. The page title is Qualification coverage and expirations — synthetic. Both Unit and Qualification slicers have no checked entries visible. Cards show coverage 92.63%, pairs with current gaps 7, missing holder slots 7, fragile pairs 6, current certificates 193, current inventory people 145, and October 7, 2026. The one-row cumulative table shows 30d 45/41, 60d 68/62, and 90d 98/84 certificates/people. These displayed global values reconcile at their shown precision. No hidden-filter state or exact formula is independently inspected.

The visible lower visual is the eight-column qualification requirements table, including per-pair demand/current holders/coverage/gap/fragile/single-holder fields. Its title combines requirements and certificate inventory, but no separate certificate-level table is visible in this image. The vertical scrollbar hides later rows and any final totals; neither all table rows nor disabled totals are newly established. The synthetic footer correctly distinguishes available current holders, broader expiration inventory, overlapping windows, and simultaneous-assignment limits. These captions are not a new independent user explanation.

Read-only reference work: read the passed/ready October 7 synthetic export manifest and the existing qualification_detail.csv and expiration_detail.csv. Both SHA-256 values match manifest entries, both row counts match 48/193, and every row has the fixed date/classification. Recalculate positive-demand exactly-met fragility independently of the saved flags and compare every flag: six fragile pairs, A/Q01, A/Q08, B/Q03, B/Q07, D/Q07, F/Q07; one single-holder pair, B/Q03. Recalculate global and selected scoped sums/counts/distinct people/windows; existing known references match. Newly recorded selected inventory expectations are C/Q06 2/2 current and in each window, B/Q03 1/1 current and 0/0 in each window, and A+C/Q01+Q02 18/17 current with 4/4, 6/6, 9/9 windows. D/Q04 is 6/6 current and in every window, all six available, days 7/10/14/20/25/30 and dates October 14/17/21/27, November 1/6. These are file-derived references, not observed filtered report results.

No file writes, CSV/database regeneration, DB access, input-checker/exporter/pipeline/test-suite rerun, PowerShell execution, or assistant-operated M/DAX/PBIX is performed. The screenshot establishes functional displayed global calculations; exact installed definitions and full type metadata remain uninspected. Historical preparation-only/no-data-access statements above apply to their earlier stages and are superseded for this read-only reference follow-up.

Next add a separately titled Current certificate inventory table with expiration_detail unit_name, qualification_id, person_id, expiration_date, days_until_expiration, is_available; retain both availability states. Rename the current table for qualification requirements and keep its totals off. Select only Unit D and Q04, verify capped coverage 100% from 2 required/6 current holders, zero gaps/fragility, 6 certificates/people in all cumulative windows, and the inclusive November 6/day-30 row. Then continue the existing C/Q06, B/Q03, multiple-selection, clear, empty, interactions, save/reopen, and ownership checks. Day 8 and later release gates remain open; the prototype remains passed.

## October 15, 20:42 PDT Unit D/Q04 selected-detail/boundary result accepted

Read image(20261016-034226).png directly from scratch without copying or publishing it. Unit D and Q04 are visibly the sole selected entries. Cards show 100.00% coverage, gap pairs 0, missing slots 0, fragile pairs 0, current certificates 6, current people 6, and October 7, 2026. All six cumulative window entries equal 6. The requirements table has one D/Q04 row: required 2, eligible 6, capped coverage 100%, gap/fragile/single-holder 0/0/0; no requirements total is visible in this view. Accept the displayed capping and shared-selection scope across both fact outputs.

The separate Current certificate inventory table is now visible with six distinct person IDs and availability 1 for each row. Dates are displayed as Year=2026, Quarter=4, Month and Day; reconstruct October 14/17/21/27 and November 1/6. Day offsets are 7/10/14/20/25/30. The November 6/day-30 certificate is included in the visible six-row current inventory and all three six-certificate windows. This matches the approved-CSV expectation and accepts the focused inclusive endpoint check. The day-30 record is not independently removed/recomputed inside the PBIX; exact installed formulas/interactions remain uninspected. No such extra internal-definition gate is imposed.

Display cleanup: switch this visual's expiration_date field from Date Hierarchy to its plain date column, and disable totals for the certificate table. Its current total 106 is the sum of day offsets, not a defined expiry metric; availability total 6 is also unnecessary in the record list. Keep the accepted values and the existing requirements table. Microsoft primary documentation confirms the visual-field menu can switch between date hierarchy and date column; guidance only, no assistant Desktop operation.

Next review C/Q06: required/eligible 2/1, coverage 50%, missing/pairs 1/1, fragile/single 0/0, current and each-window certificates/people 2/2. Review B/Q03 separately: required/eligible 1/1, coverage 100%, gaps/pairs 0/0, fragile/single 1/1, current certificates/people 1/1 and every window 0/0. These are existing reference expectations, not newly observed results. Clear previous selections between cases, retain both availability states, and obtain the user's own short explanation of why certificate inventory can exceed eligible holders. Then continue multiple selections, cleared restoration, empty scope, table interactions, save/reopen, and remaining ownership checks.

Reuse prior manifest-matching CSV calculations; no operational data or database read/write, checker/exporter/pipeline/test rerun, or M/DAX/PowerShell/PBIX execution by the assistant in this follow-up. No new independent ownership, full-page completion, event feedback, actual hours, or release gate is established. Day 8 stays open and Days 9/10 are not started.

## October 15, 21:06 PDT C/Q06 and B/Q03 accepted; availability interpretation refined

Read three supplied images directly from scratch without copying or publishing them:

- image(20261016-035325).png: D/Q04 still matches its accepted cards/requirements/windows/date. Its certificate table now uses one full expiration-date column, lists all six records, and has no visible total row. The two requested display edits pass.
- image(20261016-035658).png: only C/Q06 is visibly selected. Cards/table show required/eligible 2/1, coverage 50%, missing slots/pairs 1/1, fragile/single 0/0, current certificates/people 2/2, all three cumulative windows 2/2, and October 7 date. Two certificate records show availability 0 with October 17/day 10 and availability 1 with October 25/day 18. Inventory retains both; eligible current coverage counts only one. Plain dates, readable pair-field captions, and no totals are visible.
- image(20261016-035752).png: only B/Q03 is visibly selected. Cards/table show required/eligible 1/1, coverage 100%, missing/pairs 0/0, fragile/single 1/1, current certificates/people 1/1, all three windows 0/0, and October 7 date. The single available certificate expires April 5, 2027/day 180, outside every window. No table total is visible.

These observed single-case outputs match the existing approved-CSV references and pass. They do not establish multiple selections, a full empty scope, cleared restoration, source/target table interaction settings, or save/reopen. B's zero window counts are not the full-page empty-scope test.

User reasoning: correctly identifies two currently valid Q06 holders and differing availability, but interprets the unavailable flag as inability to renew after the day-10 expiry. Consulted docs/export_dictionary.md and the current-holder metric contract: the flag is availability at the snapshot D, used for current staffing/qualification coverage. The unavailable holder is excluded already on October 7; both certificates remain in current inventory, and neither flag describes future renewal ability or intent. C's current shortage exists at D. Explain this correction, retain the supported observation, and await a corrected own account before claiming independent current-eligibility understanding. No renewal-prediction or no-renewal feature is introduced.

Next select A+C and Q01+Q02 together: required/covered 8/8, coverage 100%, gaps/pairs 0/0, fragile pairs 1, inventory 18 certificates/17 distinct people, and cumulative windows 4/4, 6/6, 9/9. Then clear both slicers to restore global, test an empty filter on the shared qualification lookup, verify table/slicer interactions, save/reopen old and new pages, and complete remaining distinct-person/fragility/window explanations. These remaining expectations are prepared, not observed outcomes.

No current operational data/DB reread or writes, pipeline/checker/exporter/test rerun, assistant M/DAX/PowerShell/PBIX operation, new actual hours, event/employer feedback, full Day 8 completion, or later release pass is claimed. Existing 49-test and prior accepted output evidence remain unchanged.

## October 15, 21:17 PDT combined selection accepted

Read image(20261016-041753).png directly from scratch without copying or publishing it. Unit A and Unit C, plus Q01 and Q02, are visibly selected. Cards show coverage 100.00%, missing slots/pairs 0/0, fragile pairs 1, current certificates/people 18/17, and October 7, 2026. The cumulative table shows 4/4, 6/6, 9/9 certificates/people for 30/60/90 days. Four requirement rows show demand 2 each and eligible holders A/Q01=2, A/Q02=3, C/Q01=5, C/Q02=4; capping each at 2 yields 8/8 coverage. Only A/Q01 is fragile; all single-holder flags are zero. These displayed results match the prior approved-CSV reference and pass the combined-selection check.

The certificate table shows a subset of the 18 records with a scrollbar and both availability states visible. The 17-person card matches the reference; the full ID union is not recounted from this clipped table, and exact formulas/interactions remain uninspected. Prior cleanup remains accepted. No own explanation or corrected availability interpretation was submitted with this image.

Next perform only the remaining checks: clear both slicers and restore global; click a row in each table separately with slicers clear and confirm cards/other table stay unchanged; filter qualification_filter[qualification_id] to NO_SUCH_QUALIFICATION and confirm count zeros, blank coverage/date, and empty detail tables; remove the temporary filter, restore global, save/reopen and confirm new/old pages work. Obtain three short own explanations: 18 certificates versus 17 people; C undercoverage versus B fragility including current availability at D; overlapping cumulative windows. These are pending, not inferred from this screenshot. No extra filename, exact-definition, new recording, or repeated passed-case gate is added.

No operational data/DB reread/write, new pipeline/checker/exporter/test run, assistant M/DAX/PowerShell/PBIX operation, focused hours, employer feedback, Day 8 completion, or later release pass is claimed. Definitions, scope, dates, prior 49-test evidence, and prototype acceptance are unchanged.

## October 17, 10:52 PDT cleared global and ownership pass; interaction repair pending

Three images were read directly from scratch without copying or publishing them:

- image(20261017-172426).png: slicers are clear, but the A/Q03 requirement row is selected. Coverage becomes 100%, gap pairs/missing slots/fragile pairs become 0/0/0, while inventory stays at 193/145 and windows stay global. The requirement table still filters qualification cards.
- image(20261017-172440).png: a certificate row outside 90 days is selected. Inventory becomes 1 certificate/1 person and each cumulative window becomes 0/0, while coverage/gaps/pairs/fragility remain global. The certificate table still filters inventory cards. Its zero windows are not a full empty-result test.
- image(20261017-172513).png: no slicer entries or detail rows are visibly selected. Global cards/windows/date restore to 92.63%, missing/pairs 7/7, fragile 6, inventory 193/145, windows 45/41, 68/62, 98/84, October 7. Accept displayed cleared global restoration.

The user confirms the table-selection behavior and asks for help with the empty test. Both table interactions are observed as needing repair, rather than pending without evidence. Configure each detail table as the source in top Format → Edit interactions; select None over other data visuals/slicers. Preserve each slicer's Filter effect on cards/tables, exit edit mode, and retest both sources separately. No relationship or DAX change is indicated by the observed default cross-filtering.

All three own answers are correct: one person may hold multiple certificates; C/Q06 has a one-holder shortage while B/Q03 meets one-holder demand exactly and is fragile; 30-day expirations also belong to the 90-day cumulative count, so windows cannot be summed. Accept these specific explanations and the project fragility concept in the SQL backlog. The remaining LEFT JOIN and SQL staffing-row multiplication concepts were not independently explained. The prior current-availability/renewal correction remains recorded, without adding another Day 8 quiz.

The full empty case is still unobserved. Handoff now gives exact UI steps: shared qualification_filter[qualification_id] → Filters on this page → Advanced filtering → is → NO_SUCH_QUALIFICATION → Apply filter. Expected count cards and six window counts are zero, coverage/date blank, and both detail tables have no data rows. The measure-only window table may retain one zero row. Removing the temporary filter/restoring global and saving/reopening old/new pages remain unverified. Primary Microsoft interaction/page-filter/show-hide-filter documentation was consulted for UI guidance, not as evidence of project outputs.

Only documentation/audit status changes. No current operational data/DB reread/write, pipeline/checker/exporter/test rerun, assistant M/DAX/PowerShell/PBIX execution, metric/model/scope change, actual focused hours, event/employer feedback, Day 8 closure, or later release-gate pass is claimed.
