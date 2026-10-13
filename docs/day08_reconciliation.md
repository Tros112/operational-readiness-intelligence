# Day 8 — qualification and expiration reconciliation

All references describe the synthetic **2026-10-07** snapshot. Previous SQL evidence is in `docs/analytics_check.json` and `docs/verification_day05.md`. The Desktop results are pending until inspected.

## Known reference values

| Selection | Required slots | Covered slots | Coverage | Missing slots | Qualification pairs with gaps | Fragile / single-holder |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| All units and qualifications | 95 | 88 | 92.63% | 7 | 7 | Get exact totals from the read-only reference below |
| Unit C, all qualifications | 16 | 15 | 93.75% | 1 | 1 | Get exact totals from the reference |
| Unit C / Q06 | 2 | 1 | 50.00% | 1 | 1 | 0 / 0 |
| Unit B / Q03 | 1 | 1 | 100.00% | 0 | 0 | 1 / 1 |
| Unit D / Q04 | 2 | 2 | 100.00% | 0 | 0 | 0 / 0; six eligible holders, capped at two |

The source audit does not record the all-unit fragile-pair total. Derive it from the approved CSV instead of inventing a number. The live reference has no zero-holder pair; the prior SQL fixture separately verifies that requirements survive with zero holders.

| Inventory selection / cumulative cutoff | Certificate rows | Distinct people |
| --- | ---: | ---: |
| All current certificates | 193 | 145 |
| Within 30 days, through November 6, 2026 | 45 | 41 |
| Within 60 days, through December 6, 2026 | 68 | 62 |
| Within 90 days, through January 5, 2027 | 98 | 84 |
| Unit D / Q04: all current, and each 30/60/90 window | 6 | 6 |

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

1. Compare the unfiltered coverage/gaps/fragility and inventory counts with the two reference tables.
2. Select C/Q06 and B/Q03 using the two dimension slicers. Verify the different gap/fragility states and compare their inventory windows with the reference.
3. Select D/Q04. The pair has six available holders against two required, 100% capped coverage, no current gap, and no fragility. Inventory and each cumulative window contain six certificates affecting six people. Confirm the November 6 / day-30 row remains included.
4. Select A+C and Q01+Q02 together. Compare all counts with the reference; distinct people must be recalculated for the union of selected qualifications.
5. Clear both slicers and restore global totals. Temporarily apply a page filter on `qualification_filter[qualification_id]` equal to `NO_SUCH_QUALIFICATION`. All new count measures should be zero; coverage and `ORI Q Analysis Date` should be blank. Both detail tables have no data rows. Remove the filter and restore the page.
6. Check that selecting a table row leaves cards unchanged when the slicers are clear, using the intended None interactions. Save the working report, reopen it, and confirm the new page and the prior executive/learning pages function.

Only repeat a completed check if a subsequent change or failure affects it. Empty-selection and selected-qualification behavior are new Day 8 checks, not reruns of the accepted executive-page arithmetic.

For ownership, explain why 45 expiring certificates affect 41 people, why a 1/2 pair is unmet while a 1/1 pair is fragile, and why the three cumulative windows cannot be added. The separate zero-holder join / person-versus-certificate row-grain review remains carried until independently explained.
