# Day 2 Power BI staffing review

Prepared October 7, 2026, America/Los_Angeles. All operational records and expected results are **synthetic**. Staffing coverage is a fictional proxy, not an official Navy readiness rule.

Purpose: use the clean Day 2 reference to understand unit versus aggregate staffing and relationship filtering. Build one small staffing view. The production SQL exports, SQL/Power BI reconciliation, qualification/process views, and release gates remain on the existing schedule.

Status: instructions and DAX are prepared; expected arithmetic was independently recomputed from the assistant's clean CSVs. The assistant cannot run Power BI Desktop here and has not created, opened, or verified this PBIX. The user must build and check it locally. Matching Windows generation counts do not establish report correctness.

## 1. Import the two staffing tables

1. Open Power BI Desktop and create a new blank report.
2. Select **Home > Get data > Text/CSV**. In your OneDrive Day 2 project, choose `data/raw/clean/units.csv`, then **Transform Data**.
3. Name the query `units`. Verify the three headers below and their types. Select **Close & Apply**.
4. Repeat for `data/raw/clean/personnel.csv`, naming the query `personnel` and checking its three headers/types.

| Query | Column | Type |
| --- | --- | --- |
| units | unit_id | Text |
| units | unit_name | Text |
| units | required_personnel_count | Whole Number |
| personnel | person_id | Text |
| personnel | unit_id | Text |
| personnel | is_available | Whole Number |

Completion check: `units` contains six rows and six unique unit IDs; `personnel` contains 300 rows and 300 unique person IDs. Each person belongs to one unit. Retain the separate tables: staffing requirements belong to unit grain, while availability belongs to person grain.

## 2. Create or inspect one relationship

In **Model view**, inspect any auto-detected relationship. If needed, select **Modeling > Manage relationships > New** and configure:

| Property | Setting |
| --- | --- |
| One side | units[unit_id] |
| Many side | personnel[unit_id] |
| Cardinality | One to many (1:*) |
| Cross filter direction | Single, from units to personnel |
| Active | Yes |

If the dialog lists personnel first, it can display many-to-one (*:1); that is equivalent when units remains the unique side. In Model view the line should show `1` beside units, `*` beside personnel, and one filter arrow toward personnel. Use the shared unit ID, not the unit name, staffing requirement, or availability flag.

The relationship propagates a selected unit to that unit's personnel rows. It does not define what available means or calculate a percentage; those definitions belong in measures.

## 3. Create four measures, one at a time

Select the `units` table in the Data pane and choose **Modeling > New measure**. Paste each definition separately and confirm it before creating the next. A measure's home table organizes it; the formulas below explicitly identify their source tables.

```dax
Available Personnel =
    COALESCE(
        CALCULATE(
            DISTINCTCOUNT(personnel[person_id]),
            KEEPFILTERS(personnel[is_available] = 1)
        ),
        0
    )
```

```dax
Required Personnel = COALESCE(SUM(units[required_personnel_count]), 0)
```

```dax
Staffing Coverage = DIVIDE([Available Personnel], [Required Personnel])
```

```dax
Staffing Gap =
    COALESCE(
        SUMX(
            VALUES(units[unit_id]),
            MAX([Required Personnel] - [Available Personnel], 0)
        ),
        0
    )
```

Format Staffing Coverage as **Percentage, one decimal place**. Format the three count measures as whole numbers. Keep coverage uncapped; values over 100% remain visible.

Key choices:

- Available Personnel counts distinct person IDs subject to the available flag and selected units. COALESCE displays zero for an empty eligible count; KEEPFILTERS keeps the availability condition as an additional filter.
- Required Personnel sums the requirement once per selected unit, from `units`.
- Coverage divides selected totals. The total is not an average of unit percentages. DIVIDE leaves a zero-denominator rate blank.
- Staffing Gap iterates selected units and sums their nonnegative gaps. Measures evaluate for each iterated unit. This preserves a local shortage even when the aggregate has a surplus; a single `MAX(total required - total available, 0)` would hide it.
- Counts show zero for an empty scope; the zero-denominator coverage ratio remains blank.
- Staffing uses personnel grain. A person with several certificates remains one person; no certificate merge is needed for this view.

## 4. Build and check the view

1. Rename the page **Staffing review — simulated**. Add a text box: `Synthetic staffing snapshot as of October 7, 2026. Fictional readiness proxy.`
2. Add a **Matrix**. Set Rows to `units[unit_name]`; Values to Available Personnel, Required Personnel, Staffing Coverage, and Staffing Gap. Keep the row grand total visible.
3. Add a **Slicer** using `units[unit_name]`. Use the unit dimension for both matrix rows and the slicer so it filters both sides of the calculation.
4. Optionally add cards for the same four measures. Styling is unnecessary for this review.

Expected results independently counted from the clean reference CSVs:

| Unit | Available | Required | Coverage | Gap |
| --- | ---: | ---: | ---: | ---: |
| Unit A | 41 | 40 | 102.5% | 0 |
| Unit B | 44 | 40 | 110.0% | 0 |
| Unit C | 40 | 50 | 80.0% | 10 |
| Unit D | 47 | 40 | 117.5% | 0 |
| Unit E | 42 | 40 | 105.0% | 0 |
| Unit F | 40 | 40 | 100.0% | 0 |
| All units | 254 | 250 | 101.6% | 10 |

Completion checks:

- With the slicer cleared: 254 available, 250 required, 101.6% coverage, total local gap 10.
- Select Unit C: 40 available, 50 required, 80.0% coverage, gap 10.
- Select Unit A: 41 available, 40 required, 102.5% coverage, gap zero.
- Clear the slicer: the original totals return.
- Optional C + F selection: 80 available, 90 required, 88.9% coverage, gap 10. This checks aggregation of counts rather than averaging percentages.

If results differ, inspect query names/types, the relationship's active status and filter direction, and the exact measures. Record the mismatch before changing source records or metric definitions.

Save the actual report in your local project's `powerbi/Day02_Staffing_Review.pbix`. Provide a screenshot of Model view and the unfiltered matrix, plus the Unit C selected values. State whether you saved and reopened it. The assistant will record only evidence actually supplied; this learning preview alone does not pass the October 13 prototype gate.

Ownership check: explain why the overall 101.6% can coexist with Unit C's 80%, why the summed gap remains 10, and what the relationship does when the Unit C slicer is selected. Your own explanation remains required even when the expected numbers appear.

## Reference: relationships for all six clean source tables

If you later inspect all six source tables in this learning report, the following is the source relationship map. Today's staffing completion check requires only the first relationship. All listed relationships are active, one-to-many, and Single from left to right.

| Unique side (1) | Repeated side (*) | Key |
| --- | --- | --- |
| units | personnel | unit_id |
| personnel | personnel_qualifications | person_id |
| qualification_types | personnel_qualifications | qualification_id |
| units | unit_qualification_requirements | unit_id |
| qualification_types | unit_qualification_requirements | qualification_id |
| units | admin_cases | unit_id |

Personnel qualifications reach a unit through personnel. Requirements and certificate observations retain separate grains; current-valid/available eligibility and capped coverage still require the metric-contract calculations. Administrative case measures operate at case grain. Keep the relationship map as a reference rather than merging the many-row tables into one staffing table.

The production report is still planned to use validated SQL-derived outputs as described in `powerbi/build_instructions.md`; final mart relationships will follow their exported grains. No SQL output or full six-table analytical model is claimed as implemented here.

## Sources and verification limits

Microsoft documentation checked October 7, 2026:

- [Text/CSV connector](https://learn.microsoft.com/en-us/power-query/connectors/text-csv): file import and transformation entry points.
- [Create and manage relationships](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-create-and-manage-relationships) and [model relationships](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-relationships-understand): cardinality, active status, and filter propagation.
- [Create measures](https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures), [CALCULATE](https://learn.microsoft.com/en-us/dax/calculate-function-dax), and [SUMX](https://learn.microsoft.com/en-us/dax/sumx-function-dax): measure creation, filter evaluation, and iteration.

The specific measures, relationship choices, and expected results are this project's design, governed by `docs/metric_contract.md`. Expected arithmetic was checked against CSVs; the DAX and report remain unexecuted in this assistant environment.
