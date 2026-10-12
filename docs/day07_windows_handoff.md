# Day 7 — prepare and explain the prototype

**Completed October 12 from the 13:31 PDT submission.** Final captions and displayed outputs are screenshot-confirmed; the user’s accurate explanation, including Unit D and the assignment limitation, is reviewed. Duration 01:00:39 is user-reported and interpreted as about one minute; the exact timer format/delivery was not independently inspected. The prototype gate passes with these evidence limits. This remains a reference guide; completed checks need no repetition. See `docs/verification_day07.md` and the finalized `docs/checkpoints/2026-10-12_day07.md`. Stop before Day 8.

Started **October 12, 2026**, early at the user's request; the source schedule assigns Day 7 to **Tuesday, October 13**. The analysis date remains **2026-10-07**. Day 6 is complete. Today's output is a clear, demonstrable executive prototype and a practiced **30–60 second explanation**. Qualification/expiration visuals are Day 8, process metrics are Day 9, and the no-renewal scenario is Day 10.

## 1. Open the working report and tidy captions

Continue in the existing Git-connected Windows project folder. After this handoff's publication is verified, update documentation with `git pull --ff-only`. Open your working PBIX and select **Executive — simulated**. Clear the unit slicer and any table-row highlight so the presentation starts with all six units. Use the saved data; no refresh, data regeneration, database reload, or repeated Python tests are needed for captions or rehearsal. Before any later import/refresh, run the Day 6 input checker as documented.

Give caption polish at most **ten minutes**. For a card whose caption still shows an ORI measure name:

1. Select the card visual.
2. In **Visualizations → Build visual**, find its measure in the **Values** field well. Some layouts call this area Data.
3. Right-click that field entry, or open its menu, and choose **Rename for this visual**.
4. Enter the corresponding label below and press Enter. Change the label on the visual; keep the model measure definition/name intact.

| Existing measure | Caption on this page |
| --- | --- |
| ORI Available Personnel | Available personnel |
| ORI Required Personnel | Required personnel |
| ORI Staffing Coverage | Staffing coverage |
| ORI Staffing Gap | Local staffing gap |
| ORI Qualification Coverage | Qualification coverage |
| ORI Qualification Gap | Missing holder slots |
| ORI Units Needing Attention | Units with current gaps |
| ORI Analysis Date | Analysis date |

If the command is unavailable in your card layout, retain the existing readable caption and proceed to rehearsal. A cosmetic rename is not an additional release gate. Table headers can use the same captions; label the final table measure **Qualification pairs with gaps**. Retain the verified percentage formats, date, synthetic subtitle/footer, and interaction behavior. Save the working report after visual edits and keep your local screenshot as a demo fallback. PBIX/PBIT files and screenshots remain outside Git publication.

Microsoft's [report setup documentation](https://learn.microsoft.com/en-us/cloud-computing/finops/toolkit/power-bi/setup) documents Rename for this visual. Its [card documentation](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-card) describes the Values field well and differences between current and legacy card layouts. Reviewed October 12; these are UI references, not project metric rules.

## 2. Practice one short demonstration

Use this as a presentation sequence, not a request to repeat Day 6 verification. The prior global/single/multiple/clear/empty/table-row checks are already accepted.

| Moment | Action | Point to explain |
| --- | --- | --- |
| Start | Show the unfiltered executive page and analysis date | Six synthetic units at October 7. Staffing 254/250 = 101.6%; local gap 10. Qualification coverage 92.63%, missing slots 7, units with current gaps 4. |
| Local example | Select **Unit C in the unit slicer** | Available 40, required 50: 80.0% staffing coverage and a local gap of 10. Qualification slots 15/16 = 93.75%, missing one slot. |
| Finish | Clear the slicer | All-unit totals return. Aggregate staffing surplus does not cancel another unit's local gap. |

Use the unit slicer to filter the page. The comparison table's row highlight leaves the cards unchanged, as verified at Day 6 completion. Keep the walkthrough focused on the decision: **which unit needs staffing or qualification review?**

## 3. Rehearse the 30–60 second explanation

This sample was a drafting aid prepared before the user supplied their own version. The accepted explanation and reported timing are recorded in `docs/verification_day07.md`; this sample alone remains insufficient ownership evidence. Adapt it to your own words, speak it with a timer, and shorten it if you exceed 60 seconds.

> I'm building Operational Readiness Intelligence, a portfolio prototype that helps an operations manager identify local staffing and qualification gaps. It uses synthetic data for six units at an October 7 snapshot. Python validates the records, SQL calculates metrics in SQLite, and Power BI shows the comparisons. Overall staffing coverage is 101.6%, but Unit C is ten people short, showing why aggregate surplus can hide a local gap. Qualification coverage is 92.63%, with seven missing holder slots. I can filter the executive page and reconcile its results to SQL. Readiness rules are fictional, and the qualification and process detail pages are planned.

Your version should identify the audience/decision, describe the working pipeline, explain one displayed result, and state a material limitation. A limitation can be the synthetic single snapshot, fictional readiness rules, or the fact that holder-slot coverage does not establish simultaneous assignments. Preserve the distinction between built outputs and planned pages. An assistant-written script alone does not establish your understanding or rehearsal.

This evidence step is complete: the user supplied their own explanation and a reported duration of about one minute. No voice recording or repeat of prior successful report/test checks is required. For later practice, use “required qualification holder slots” when describing Unit D’s 87.5% to make the counted quantity explicit.

## 4. Keep these follow-up facts available

| If asked | Project-supported answer |
| --- | --- |
| Why is there a gap when global coverage exceeds 100%? | Global coverage divides total available by total required. The local gap adds each unit's positive shortage; surplus elsewhere does not erase Unit C's shortage. |
| What does qualification coverage count? | Eligible distinct people per unit/qualification, capped at that pair's demand before summing: 88 covered of 95 required holder slots. One person may contribute to multiple qualifications; these are slots, not 88 unique people or a proven staffing assignment. |
| What triggers a unit flag? | A current staffing shortage or at least one current qualification gap. Upcoming expirations and fragile-but-met coverage are separate questions. |
| How is input quality handled? | Key, relationship, type, date, and other checks produce traceable diagnostics. A failed batch is blocked from loading; critical values are not silently filled. |
| What is the summary grain? | One unit at the fixed October 7 snapshot. Staffing is aggregated from people before certificate summaries are joined. |
| What is finished and what is next? | Generation/validation/loading, current SQL exports, and the executive page are built and technically verified. Qualification/expiration visuals, process metrics, and the no-renewal scenario remain planned. ML is outside this MVP. |

The Day 5 LEFT JOIN/person-versus-certificate/fragility ownership review remains in `docs/sql_review_backlog.md`. These prepared answers do not mark it mastered. A complete SQL ownership check belongs before the interview-ready release; it does not require repeating successful implementation runs today.

## 5. Close the prototype gate and record actual feedback

The functioning-output criteria are supported by Day 6 evidence. The short explanation and user-reported rehearsal were reviewed October 12, and the **prototype gate passed**. The finalized source-template master-chat checkpoint records what is verified, what is user-reported, and what remains planned. Stop at Day 7; starting Day 8 requires the next instruction.

The source plan lists a Meet & Greet on October 13. Follow your actual event schedule; attendance, employer conversations, and outcomes have not been reported. After any conversation, capture the employer/role, actual question or need, evidence shown, weak explanation, and a specific follow-up in `docs/interview_feedback.md`. The technical prototype gate and event attendance are separate facts; neither implies the other.
