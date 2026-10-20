# Day 9 process reconciliation

These are **synthetic SQL/CSV reference results**. The October 19 screenshots reconcile the global, listed unit/type/multi, Open-only, and empty scopes at displayed precision; final restoration/interactions/reopening/own explanations remain pending. Fixed D is October 7, 2026. The opening/completion period is July 10–October 7 inclusive. Backlog age covers all known cases open at D, including older backlog if supplied; the generated reference happens to open every case inside the period.

## Reference selections

| Selection | Opened | Completed | Corrections | Rate | Median cycle days | Open | Median age days | Oldest age days |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| All | 600 | 442 | 45 | 10.18% | 7.0 | 158 | 27.0 | 88 |
| Unit F | 98 | 70 | 27 | 38.57% | 7.5 | 28 | 33.0 | 87 |
| Other five units | 502 | 372 | 18 | 4.84% | 7.0 | 130 | 26.0 | 88 |
| evaluation | 161 | 109 | 11 | 10.09% | 8.0 | 52 | 38.5 | 88 |
| onboarding | 148 | 111 | 11 | 9.91% | 7.0 | 37 | 35.0 | 87 |
| A+F | 194 | 141 | 28 | 19.86% | 8.0 | 53 | 35.0 | 87 |
| A+F / onboarding+transfer | 86 | 57 | 14 | 24.56% | 7.0 | 29 | 35.0 | 84 |
| Open only | 158 | 0 | 0 | blank | blank | 158 | 27.0 | 88 |
| Empty | 0 | 0 | 0 | blank | blank | 0 | blank | blank |

Analysis date is October 7 for all nonempty selections and blank for a fully empty case scope. The period-start measure follows the same rule. The current reference's 600 openings equal 442 completed plus 158 open because all openings fall inside the window; that identity is not a general definition when older cases exist.

## Unit comparison reference

| Selection | Opened | Completed | Corrections | Rate | Median cycle days | Open | Median age days | Oldest age days |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Unit A | 96 | 71 | 1 | 1.41% | 8.0 | 25 | 40.0 | 84 |
| Unit B | 95 | 76 | 3 | 3.95% | 7.0 | 19 | 16.0 | 86 |
| Unit C | 93 | 66 | 7 | 10.61% | 7.5 | 27 | 24.0 | 87 |
| Unit D | 111 | 83 | 4 | 4.82% | 8.0 | 28 | 41.0 | 84 |
| Unit E | 107 | 76 | 3 | 3.95% | 6.5 | 31 | 22.0 | 88 |
| Unit F | 98 | 70 | 27 | 38.57% | 7.5 | 28 | 33.0 | 87 |

The global median cycle time is **7.0**, even though the median of the six displayed unit medians is **7.5**. Recompute from the selected case durations. Similarly, the global rate is 45/442, not an unweighted average of unit rates. Unit F's 27/70 = 38.57% versus other units' 18/372 = 4.84% reflects the configured planted hotspot; it establishes no real-world cause or staff-performance finding.

## Desktop completion checks — October 19 review

1. **Passed — Global:** eight metric cards, date, and unit comparison match the references. Counts use no display-unit abbreviation; rates use two decimals, medians one decimal. Raw case table uses single dates and no totals.
2. **Selected results passed; final restoration pending — Shared slicers:** only Unit F gives the F row. Then clear Unit and select only evaluation to get its row. Select A+F and onboarding+transfer together for 86/57/14, 24.56%, cycle 7.0, open 29, median age 35.0, oldest 84. Clear both slicers and restore global.
3. **Passed — Zero eligible completions with data still present:** temporarily drag process_case_detail[status_at_as_of] into Filters on this page. Basic filtering: select only Open. Expect 158 opened, completed/corrections 0/0, rate/cycle blank, open 158, median age 27.0, oldest 88, date October 7. Open case outcomes in the case table are blank, not a known no-correction 0. Remove this filter.
4. **Empty result passed; removal/restoration pending:** the actual page filter is process_case_detail[status_at_as_of] Advanced filtering → is empty. Both valid statuses are nonempty, so this is an equivalent fully empty fact scope; no repeat with NO_SUCH_PROCESS is required. All count cards are zero; rate, cycle, median/oldest age, and analysis date are blank. Case table has no rows. Six unit lookup rows retain zero counts, as expected. Remove this temporary filter and restore global.
5. **Pending — Table interactions:** with slicers/temporary filters clear, select a row in each table separately. Cards/date and the other table stay global. Both slicers must continue filtering all new cards/tables.
6. **Pending — Reopening:** save with temporary filters removed; reopen and confirm the process, qualification, executive, and earlier learning pages function. User confirmation is acceptable; no filename or exact-definition screenshot gate is added.
7. **Pending — Own explanation:** why completed cases form the discrepancy denominator; why Open-only gives a blank rate; why selected-case medians cannot be replaced by unit medians. Add a verified process example to the existing short pitch without a new timing/recording requirement.

The first Windows checkpoint is now **passed** from the earlier October 17 files reviewed October 19: 60 tests/OK (44.115s), two-file process preflight 600/6 with zero writes, matching repeat/manifest results, and DB/prior bundle preserved. The imports are 600/16 and 4/1; seven active 1:* Single links and ten ORI P measures are visible. No setup/test/export/checker rerun is needed solely for evidence. An active visual border is not a selected-data-row test. Only the four final groups remain: post-filter restoration, both table row tests, reopening, and own process explanations.

## Independent SQL boundary checks already passed on Linux

The isolated fixture verifies completion on July 10 and October 7, exclusion of July 9 from the completion cohort, same-day cycle zero, older open backlog retained with a 128-day age, exclusion of October 8 openings, and masking of October 8 completion/outcome as open at D. A separate fixture has unit durations [0,1,2] and [100]: combined median 1.5, not mean 25.75 or median-of-unit-medians 50.5. Empty units remain in the SQL unit summary, empty counts are zero, and undefined rates/medians remain NULL. These fixtures are teaching/test data, not findings from the 600 generated cases.
