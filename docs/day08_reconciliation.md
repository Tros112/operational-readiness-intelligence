# Day 8 — qualification and expiration reconciliation

All references describe the synthetic **2026-10-07** snapshot. Previous SQL evidence is in `docs/analytics_check.json` and `docs/verification_day05.md`. The October 14 unfiltered and October 15 D/Q04, C/Q06, and B/Q03 Desktop displays reconcile, including the inclusive day-30 endpoint and current-availability scope. The combined A+C/Q01+Q02 displays also reconcile; clear/empty/interactions and completion checks remain pending until inspected.

## Known reference values

| Selection | Required slots | Covered slots | Coverage | Missing slots | Qualification pairs with gaps | Fragile / single-holder |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| All units and qualifications | 95 | 88 | 92.63% | 7 | 7 | 6 / 1; derived from manifest-matching CSV on October 14 |
| Unit C, all qualifications | 16 | 15 | 93.75% | 1 | 1 | Get exact totals from the reference |
| Unit C / Q06 | 2 | 1 | 50.00% | 1 | 1 | 0 / 0 |
| Unit B / Q03 | 1 | 1 | 100.00% | 0 | 0 | 1 / 1 |
| Unit D / Q04 | 2 | 2 | 100.00% | 0 | 0 | 0 / 0; six eligible holders, capped at two |

The earlier source audit did not record the all-unit fragile total. The October 14 read-only CSV check now establishes six fragile pairs (A/Q01, A/Q08, B/Q03, B/Q07, D/Q07, F/Q07), one single-holder pair (B/Q03), and a matching global Desktop fragile card of 6. The live reference has no zero-holder pair; the prior SQL fixture separately verifies that requirements survive with zero holders.

| Inventory selection / cumulative cutoff | Certificate rows | Distinct people |
| --- | ---: | ---: |
| All current certificates | 193 | 145 |
| Within 30 days, through November 6, 2026 | 45 | 41 |
| Within 60 days, through December 6, 2026 | 68 | 62 |
| Within 90 days, through January 5, 2027 | 98 | 84 |
| Unit D / Q04: all current, and each 30/60/90 window | 6 | 6 |
| Unit C / Q06: all current, and each 30/60/90 window | 2 | 2 |
| Unit B / Q03: all current | 1 | 1 |
| Unit B / Q03: each 30/60/90 window | 0 | 0 |
| Units A+C / Q01+Q02: all current | 18 | 17 |
| Units A+C / Q01+Q02: 30 / 60 / 90 window | 4 / 6 / 9 | 4 / 6 / 9 |

The added selected inventory values were calculated October 14 from the existing detail CSVs after matching their SHA-256 values, 48/193 rows, fixed date, and synthetic classification to the passed manifest. No files were changed or pipeline/test suite rerun. They are reference expectations, not observed filtered Power BI results. The global page screenshot matches the global rows above.

The current inventory includes **21 certificate rows held by unavailable people**. Keep them in expiration counts. Unit D/Q04's six rows have offsets **7, 10, 14, 20, 25, 30**; the certificate expiring November 6 is included at day 30. Their current coverage is met with surplus, so they are not fragile today. No future gap is calculated here; the no-renewal scenario remains Day 10.

## Read-only reference for selected units and qualifications

Run this self-contained block from the existing project root. It calls the existing input checker before reading the saved CSVs. It does not export, load, refresh Power BI, or write files. The block is prepared, not executed by the assistant in this session.

```powershell
& {
    $ErrorActionPreference = 'Stop'
    $oriDay8Output = '.\data\processed\dashboard'
    .\.venv\Scripts\python.exe src\check_powerbi_input.py
    if ($LASTEXITCODE -ne 0) { throw 'Input check failed; return its output before importing or refreshing.' }

    $oriDay8AllQ = @(Import-Csv -LiteralPath (Join-Path $oriDay8Output 'qualification_detail.csv') -Encoding UTF8)
    $oriDay8AllE = @(Import-Csv -LiteralPath (Join-Path $oriDay8Output 'expiration_detail.csv') -Encoding UTF8)
    if ($oriDay8AllQ.Count -ne 48 -or $oriDay8AllE.Count -ne 193) {
        throw 'Unexpected reference row counts.'
    }

    function Get-OriDay8Sum {
        param([object[]]$Rows, [string]$Name)
        return [int](($Rows | Measure-Object -Property $Name -Sum).Sum)
    }

    function Get-OriDay8People {
        param([object[]]$Rows)
        return @($Rows | Select-Object -ExpandProperty person_id | Sort-Object -Unique).Count
    }

    function Show-OriDay8Reference {
        param([string]$Label, [string[]]$UnitIds = @(), [string[]]$QualificationIds = @())
        $oriQRows = @($oriDay8AllQ | Where-Object {
            ($UnitIds.Count -eq 0 -or $_.unit_id -in $UnitIds) -and
            ($QualificationIds.Count -eq 0 -or $_.qualification_id -in $QualificationIds)
        })
        $oriERows = @($oriDay8AllE | Where-Object {
            ($UnitIds.Count -eq 0 -or $_.unit_id -in $UnitIds) -and
            ($QualificationIds.Count -eq 0 -or $_.qualification_id -in $QualificationIds)
        })
        $oriRequired = Get-OriDay8Sum -Rows $oriQRows -Name 'required_holder_count'
        $oriCovered = Get-OriDay8Sum -Rows $oriQRows -Name 'capped_holder_count'
        $oriCoverage = if ($oriRequired -gt 0) { '{0:P2}' -f ($oriCovered / $oriRequired) } else { $null }
        $oriE30 = @($oriERows | Where-Object { [int]$_.expires_within_30_days -eq 1 })
        $oriE60 = @($oriERows | Where-Object { [int]$_.expires_within_60_days -eq 1 })
        $oriE90 = @($oriERows | Where-Object { [int]$_.expires_within_90_days -eq 1 })
        [PSCustomObject]@{
            Selection = $Label
            Required = $oriRequired
            Covered = $oriCovered
            Coverage = $oriCoverage
            Gap = (Get-OriDay8Sum -Rows $oriQRows -Name 'current_gap')
            GapPairs = @($oriQRows | Where-Object { [int]$_.current_gap -gt 0 }).Count
            Fragile = (Get-OriDay8Sum -Rows $oriQRows -Name 'is_fragile')
            Single = (Get-OriDay8Sum -Rows $oriQRows -Name 'is_single_holder_dependency')
            Certificates = $oriERows.Count
            People = (Get-OriDay8People -Rows $oriERows)
            Unavailable = @($oriERows | Where-Object { [int]$_.is_available -eq 0 }).Count
            C30 = $oriE30.Count
            P30 = (Get-OriDay8People -Rows $oriE30)
            C60 = $oriE60.Count
            P60 = (Get-OriDay8People -Rows $oriE60)
            C90 = $oriE90.Count
            P90 = (Get-OriDay8People -Rows $oriE90)
        }
    }

    $oriDay8Results = @(
        Show-OriDay8Reference -Label 'All'
        Show-OriDay8Reference -Label 'C' -UnitIds @('U03')
        Show-OriDay8Reference -Label 'C/Q06' -UnitIds @('U03') -QualificationIds @('Q06')
        Show-OriDay8Reference -Label 'B/Q03' -UnitIds @('U02') -QualificationIds @('Q03')
        Show-OriDay8Reference -Label 'D/Q04' -UnitIds @('U04') -QualificationIds @('Q04')
        Show-OriDay8Reference -Label 'A+C/Q01+Q02' -UnitIds @('U01', 'U03') -QualificationIds @('Q01', 'Q02')
        Show-OriDay8Reference -Label 'Empty' -QualificationIds @('NO_SUCH_QUALIFICATION')
    )
    $oriDay8Results | Select-Object Selection, Required, Covered, Coverage, Gap, GapPairs, Fragile, Single | Format-Table -AutoSize
    $oriDay8Results | Select-Object Selection, Certificates, People, Unavailable, C30, P30, C60, P60, C90, P90 | Format-Table -AutoSize
}
```

The last case should have zero counts and a blank coverage value. If console width clips a field, replace either final table line with `$oriDay8Results | Format-List`. Reference values come from CSV rows after the hash/grain prerequisite; they are not observed Power BI results. Keep the input files stable until import/refresh.

## Desktop completion checks

1. **Passed:** unfiltered coverage/gaps/fragility and inventory counts match the two reference tables.
2. **Passed:** C/Q06 and B/Q03 dimension-slicer selections match their different gap/fragility states and inventory/window references.
3. **Passed:** D/Q04 selection. The pair has six available holders against two required, 100% capped coverage, no current gap, and no fragility. Inventory and each cumulative window contain six certificates affecting six people. Confirm the November 6 / day-30 row remains included.
4. **Passed:** A+C and Q01+Q02 together match the reference, including 18 certificates/17 people and 4/4, 6/6, 9/9 windows for the selected union.
5. **Passed October 17:** the shared-lookup advanced page filter equals `NO_SUCH_QUALIFICATION`; every new count card and all six window counts show zero, coverage/date display blank as dashes, and both detail tables have no data rows. The next image shows the page-filter area empty and the global values restored. The window-measures table correctly retains its zero row in the empty scope.
6. **Passed October 17:** selecting A/Q02 in requirements and a certificate outside 90 days in inventory separately leaves global cards, windows, date, and the other table unchanged. This supersedes the earlier interaction failure. The user confirms "PBIX reopens and functions correctly," accepted for the requested new/prior-page regression check. Exact interaction settings and the reopened PBIX were not operated by the assistant.

Only repeat a completed check if a subsequent change or failure affects it. Empty-selection and selected-qualification behavior are new Day 8 checks, not reruns of the accepted executive-page arithmetic.

**Ownership passed October 17:** the user correctly explains multiple certificates per person, C/Q06 unmet versus B/Q03 met exactly and fragile, and overlapping cumulative windows that must not be added. Do not repeat these questions. The separate zero-holder LEFT JOIN and SQL join-multiplication review remains carried; recognizing multiple certificates does not alone establish how to prevent inflated staffing after a join.

October 15 D/Q04 screenshot acceptance: both slicers select only D/Q04; required/eligible 2/6, coverage 100%, zero gaps/fragility, current and all-window certificates/people 6/6, fixed October 7 date, and all six certificate rows at days 7/10/14/20/25/30 are visible. November 6/day 30 is included. Date hierarchy and certificate-table totals need display cleanup; they do not change this numeric reconciliation. C/Q06, B/Q03, multiple/clear/empty/interactions, save/reopen, and ownership remain pending.

Later October 15 C/Q06 and B/Q03 screenshots match their reference rows, current inventory, and all windows; date/table-total cleanup is visible. C shows two valid certificates but only one currently available eligible holder, so coverage is already 50% at D. B is met exactly and fragile, with its lone current certificate outside 90 days. is_available refers to current snapshot coverage, not future renewal prospects. Multiple/clear/empty/interactions, save/reopen, and remaining ownership checks stay open.

October 15, 21:17 PDT combined selection passes: A+C/Q01+Q02 visible, required/capped 8/8, coverage 100%, gaps/pairs 0/0, fragile one, certificates/people 18/17, windows 4/4, 6/6, 9/9, fixed October 7 date. Remaining clear/empty/interactions, save/reopen, and own explanations are not established by that screenshot.

October 17, 11:28 PDT completion: all six Desktop checks above pass, including the full empty page, filter removal/global restoration, and both separate table-selection tests. Reopening/function is user-confirmed. The three own explanations were accepted earlier today. Day 8 is complete; prior pending/failure entries are historical. No further arithmetic/test rerun, screenshot, or quiz is required for this milestone.
