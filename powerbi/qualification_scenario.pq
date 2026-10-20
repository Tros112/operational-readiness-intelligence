// New Blank Query named qualification_scenario. Replace only ProjectRoot.
// Requires the accepted qualification_detail query. Run all three preflights before refresh.
// Python checks SHA-256; M checks manifest/schema/types/grain and baseline/scenario arithmetic.
let
    ProjectRoot = "PASTE_EXISTING_PROJECT_ROOT_HERE",
    Folder = ProjectRoot & "\data\processed\dashboard\scenario\",
    ExpectedDate = #date(2026, 10, 7),
    ExpectedColumns = {"data_classification", "scenario", "as_of_date", "horizon_days", "horizon_date", "unit_id", "unit_name", "qualification_id", "qualification_name", "required_holder_count", "current_eligible_holder_count", "projected_eligible_holder_count", "eligible_holders_lost", "current_capped_holder_count", "projected_capped_holder_count", "current_gap", "projected_gap", "additional_gap", "current_coverage_ratio", "projected_coverage_ratio", "current_is_gap", "projected_is_gap", "is_new_gap", "current_is_fragile", "projected_is_fragile"},
    TextColumns = {"data_classification", "scenario", "unit_id", "unit_name", "qualification_id", "qualification_name"},
    DateColumns = {"as_of_date", "horizon_date"},
    IntegerColumns = {"horizon_days", "required_holder_count", "current_eligible_holder_count", "projected_eligible_holder_count", "eligible_holders_lost", "current_capped_holder_count", "projected_capped_holder_count", "current_gap", "projected_gap", "additional_gap", "current_is_gap", "projected_is_gap", "is_new_gap", "current_is_fragile", "projected_is_fragile"},
    RatioColumns = {"current_coverage_ratio", "projected_coverage_ratio"},
    Manifest = Json.Document(File.Contents(Folder & "scenario_export_manifest.json")),
    ManifestOK = try (Manifest[status] = "passed" and Manifest[exports_ready] = true
        and Manifest[exit_code] = 0 and Manifest[bundle_kind] = "qualification_scenario"
        and Manifest[scenario] = "no_renewal" and Manifest[as_of_date] = "2026-10-07"
        and Manifest[data_classification] = "synthetic_only" and Manifest[horizons_days] = {30, 60, 90}
        and Manifest[database_matches_passed_source] = true and Manifest[cross_query_reconciliation] = "passed"
        and Manifest[assumptions][no_renewals] = true
        and Manifest[assumptions][staffing_unit_membership_and_availability] = "held_at_as_of_date"
        and Manifest[assumptions][eligible_cohort] = "available_and_currently_valid_at_as_of_date"
        and Manifest[assumptions][future_start_certificates] = "excluded"
        and Manifest[assumptions][expiration_rule] = "expiration_date_on_or_before_horizon_is_removed"
        and Manifest[assumptions][simultaneous_assignments] = "not_modeled") otherwise false,
    Entry = if ManifestOK then Record.Field(Manifest[files], "qualification_scenario.csv")
        else error Error.Record("ORI.ScenarioBlocked", "Run a successful no-renewal scenario export before refresh.", null),
    EntryOK = try (Entry[rows] = 144 and Entry[columns] = ExpectedColumns
        and Entry[grain] = {"unit_id", "qualification_id", "horizon_days", "as_of_date"}
        and Text.Length(Entry[sha256]) = 64) otherwise false,
    CsvBytes = if EntryOK then Binary.Buffer(File.Contents(Folder & "qualification_scenario.csv"))
        else error Error.Record("ORI.ScenarioManifest", "Unexpected scenario reference schema/count/grain.", null),
    Parsed = Csv.Document(CsvBytes, [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Parsed, [PromoteAllScalars = true]),
    CheckedHeaders = if Table.ColumnNames(Headers) = ExpectedColumns then Headers
        else error Error.Record("ORI.ScenarioHeader", "Scenario CSV schema differs.", null),
    NullRatios = Table.ReplaceValue(CheckedHeaders, "", null, Replacer.ReplaceValue, RatioColumns),
    Numeric = Table.TransformColumnTypes(NullRatios,
        List.Transform(TextColumns, each {_, type text}) & List.Transform(DateColumns, each {_, type date})
        & List.Transform(IntegerColumns & RatioColumns, each {_, type number}), "en-US"),
    NoErrors = if Table.RowCount(Table.SelectRowsWithErrors(Numeric)) = 0 then Numeric
        else error Error.Record("ORI.ScenarioTypes", "Scenario type errors; do not remove error rows.", null),
    Baseline = Table.SelectColumns(qualification_detail, {"as_of_date", "unit_id", "unit_name", "qualification_id",
        "qualification_name", "required_holder_count", "valid_available_holder_count"}),
    BaselineKeys = List.Transform(Table.ToRecords(Baseline), each [unit_id] & "|" & [qualification_id]),
    BaselineMap = if Table.RowCount(Baseline) = 48 and List.Count(List.Distinct(BaselineKeys)) = 48
        then Record.FromList(Table.ToRecords(Baseline), BaselineKeys)
        else error Error.Record("ORI.ScenarioBaseline", "Expected the accepted 48-pair current qualification baseline.", null),
    BadRows = Table.SelectRows(NoErrors, (row) =>
        let
            TextOK = List.AllTrue(List.Transform(TextColumns, (c) =>
                let v = Record.Field(row, c) in v <> null and Text.Trim(v) <> "")),
            IntsOK = List.AllTrue(List.Transform(IntegerColumns, (c) =>
                let v = Record.Field(row, c) in v <> null and v >= 0 and v = Number.RoundDown(v))),
            Key = if TextOK then row[unit_id] & "|" & row[qualification_id] else ""
        in
            if not TextOK or not IntsOK or row[data_classification] <> "synthetic_only"
                or row[scenario] <> "no_renewal" or row[as_of_date] <> ExpectedDate
                or not List.Contains({30, 60, 90}, row[horizon_days]) or row[required_holder_count] <= 0
                or row[horizon_date] = null then true
            else if not Record.HasFields(BaselineMap, Key) then true
            else
                let
                    Base = Record.Field(BaselineMap, Key),
                    Required = row[required_holder_count],
                    Current = row[current_eligible_holder_count],
                    Projected = row[projected_eligible_holder_count],
                    CurrentCap = List.Min({Current, Required}),
                    ProjectedCap = List.Min({Projected, Required}),
                    CurrentGap = List.Max({Required - Current, 0}),
                    ProjectedGap = List.Max({Required - Projected, 0}),
                    RatiosOK = row[current_coverage_ratio] <> null and row[projected_coverage_ratio] <> null
                        and Number.Abs(row[current_coverage_ratio] - CurrentCap / Required) <= 0.000000000001
                        and Number.Abs(row[projected_coverage_ratio] - ProjectedCap / Required) <= 0.000000000001
                in Base[as_of_date] <> ExpectedDate
                    or row[unit_name] <> Base[unit_name] or row[qualification_name] <> Base[qualification_name]
                    or Required <> Base[required_holder_count] or Current <> Base[valid_available_holder_count]
                    or Projected > Current or row[horizon_date] <> Date.AddDays(ExpectedDate, row[horizon_days])
                    or row[eligible_holders_lost] <> Current - Projected
                    or row[current_capped_holder_count] <> CurrentCap or row[projected_capped_holder_count] <> ProjectedCap
                    or row[current_gap] <> CurrentGap or row[projected_gap] <> ProjectedGap
                    or row[additional_gap] <> ProjectedGap - CurrentGap
                    or row[current_is_gap] <> (if CurrentGap > 0 then 1 else 0)
                    or row[projected_is_gap] <> (if ProjectedGap > 0 then 1 else 0)
                    or row[is_new_gap] <> (if CurrentGap = 0 and ProjectedGap > 0 then 1 else 0)
                    or row[current_is_fragile] <> (if Current = Required then 1 else 0)
                    or row[projected_is_fragile] <> (if Projected = Required then 1 else 0)
                    or not RatiosOK),
    Groups = Table.Group(NoErrors, {"unit_id", "qualification_id"},
        {{"Rows", each Table.Sort(_, {{"horizon_days", Order.Ascending}})}}),
    BadGroups = Table.SelectRows(Groups, each
        Table.RowCount([Rows]) <> 3
        or [Rows][projected_eligible_holder_count] <> List.Sort([Rows][projected_eligible_holder_count], Order.Descending)),
    ShapeOK = Table.RowCount(NoErrors) = 144 and Table.RowCount(BadRows) = 0 and Table.RowCount(BadGroups) = 0
        and Table.RowCount(Table.Distinct(NoErrors, {"unit_id", "qualification_id", "horizon_days", "as_of_date"})) = 144,
    CheckedRows = if ShapeOK then NoErrors
        else error Error.Record("ORI.ScenarioRows", "Expected all 48 baseline pairs at three unique, non-increasing no-renewal horizons.", null),
    Typed = Table.TransformColumnTypes(CheckedRows, List.Transform(IntegerColumns, each {_, Int64.Type})),
    Sorted = Table.Sort(Typed, {{"unit_id", Order.Ascending}, {"qualification_id", Order.Ascending}, {"horizon_days", Order.Ascending}})
in
    Sorted
