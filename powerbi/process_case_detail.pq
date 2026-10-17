// Paste the whole query into a new Blank Query named process_case_detail.
// Replace only ProjectRoot with the existing Windows project root (not powerbi).
// Requires the existing unit_summary query. Run check_process_input.py before refresh.
// Python checks SHA-256. M checks the approved reference schema/types/grain and lifecycle.
let
    ProjectRoot = "PASTE_EXISTING_PROJECT_ROOT_HERE",
    Folder = ProjectRoot & "\data\processed\dashboard\process\",
    ExpectedDate = #date(2026, 10, 7),
    PeriodStart = #date(2026, 7, 10),
    ExpectedColumns = {"data_classification", "as_of_date", "period_start", "case_id", "unit_id", "unit_name", "case_type", "opened_date", "closed_date", "correction_required", "status_at_as_of", "opened_in_period", "completed_in_period", "open_at_as_of", "completed_cycle_days", "open_age_days"},
    TextColumns = {"data_classification", "case_id", "unit_id", "unit_name", "case_type", "status_at_as_of"},
    DateColumns = {"as_of_date", "period_start", "opened_date", "closed_date"},
    IntegerColumns = {"correction_required", "opened_in_period", "completed_in_period", "open_at_as_of", "completed_cycle_days", "open_age_days"},
    FlagColumns = {"opened_in_period", "completed_in_period", "open_at_as_of"},
    NullableColumns = {"closed_date", "correction_required", "completed_cycle_days", "open_age_days"},
    AllowedTypes = {"onboarding", "records_update", "transfer", "evaluation"},
    Manifest = Json.Document(File.Contents(Folder & "process_export_manifest.json")),
    ManifestOK = try (Manifest[status] = "passed" and Manifest[exports_ready] = true
        and Manifest[exit_code] = 0 and Manifest[bundle_kind] = "process"
        and Manifest[as_of_date] = "2026-10-07" and Manifest[period_start] = "2026-07-10"
        and Manifest[data_classification] = "synthetic_only"
        and Manifest[database_matches_passed_source] = true
        and Manifest[cross_query_reconciliation] = "passed") otherwise false,
    Entry = if ManifestOK then Record.Field(Manifest[files], "process_case_detail.csv")
        else error Error.Record("ORI.ProcessBlocked", "Run a successful process export before refresh.", null),
    EntryOK = try (Entry[rows] = 600 and Entry[columns] = ExpectedColumns
        and Entry[grain] = {"case_id", "as_of_date"} and Text.Length(Entry[sha256]) = 64) otherwise false,
    CsvBytes = if EntryOK then Binary.Buffer(File.Contents(Folder & "process_case_detail.csv"))
        else error Error.Record("ORI.ProcessManifest", "Unexpected process reference schema/count/grain.", null),
    Parsed = Csv.Document(CsvBytes, [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Parsed, [PromoteAllScalars = true]),
    CheckedHeaders = if Table.ColumnNames(Headers) = ExpectedColumns then Headers
        else error Error.Record("ORI.ProcessHeader", "Process CSV schema differs.", null),
    Nulls = Table.ReplaceValue(CheckedHeaders, "", null, Replacer.ReplaceValue, NullableColumns),
    Numeric = Table.TransformColumnTypes(Nulls,
        List.Transform(TextColumns, each {_, type text})
        & List.Transform(DateColumns, each {_, type date})
        & List.Transform(IntegerColumns, each {_, type number}), "en-US"),
    NoErrors = if Table.RowCount(Table.SelectRowsWithErrors(Numeric)) = 0 then Numeric
        else error Error.Record("ORI.ProcessType", "Process type errors; do not remove error rows.", null),
    Units = Table.SelectColumns(unit_summary, {"unit_id", "unit_name", "as_of_date"}),
    UnitsOK = Table.RowCount(Units) = 6 and Table.RowCount(Table.Distinct(Units, {"unit_id"})) = 6
        and Table.RowCount(Table.SelectRows(Units, each [as_of_date] <> ExpectedDate)) = 0,
    UnitNames = if UnitsOK then Record.FromList(Units[unit_name], Units[unit_id])
        else error Error.Record("ORI.ProcessUnits", "Expected six unique units at the same snapshot.", null),
    BadRows = Table.SelectRows(NoErrors, (row) =>
        let
            TextOK = List.AllTrue(List.Transform(TextColumns, (c) =>
                let v = Record.Field(row, c) in v <> null and Text.Trim(v) <> "")),
            IntegersOK = List.AllTrue(List.Transform(IntegerColumns, (c) =>
                let v = Record.Field(row, c)
                in if v = null then List.Contains(NullableColumns, c)
                else v >= 0 and v = Number.RoundDown(v))),
            FlagsOK = List.AllTrue(List.Transform(FlagColumns, (c) => List.Contains({0, 1}, Record.Field(row, c))))
        in
            if not TextOK or not IntegersOK or not FlagsOK or row[data_classification] <> "synthetic_only"
                or row[as_of_date] <> ExpectedDate or row[period_start] <> PeriodStart
                or row[opened_date] = null then true
            else if not Record.HasFields(UnitNames, row[unit_id])
                or not List.Contains(AllowedTypes, row[case_type]) then true
            else if row[opened_date] > ExpectedDate or (row[closed_date] <> null
                and (row[closed_date] < row[opened_date] or row[closed_date] > ExpectedDate)) then true
            else
                let
                    IsOpen = row[closed_date] = null,
                    Opened = if row[opened_date] >= PeriodStart then 1 else 0,
                    Completed = if IsOpen then 0 else if row[closed_date] >= PeriodStart then 1 else 0,
                    Cycle = if Completed = 1 then Duration.Days(row[closed_date] - row[opened_date]) else null,
                    Age = if IsOpen then Duration.Days(ExpectedDate - row[opened_date]) else null,
                    OutcomeOK = if IsOpen then row[correction_required] = null
                        else List.Contains({0, 1}, row[correction_required])
                in row[unit_name] <> Record.Field(UnitNames, row[unit_id]) or not OutcomeOK
                    or row[status_at_as_of] <> (if IsOpen then "Open" else "Completed")
                    or row[opened_in_period] <> Opened or row[completed_in_period] <> Completed
                    or row[open_at_as_of] <> (if IsOpen then 1 else 0)
                    or row[completed_cycle_days] <> Cycle or row[open_age_days] <> Age),
    ShapeOK = Table.RowCount(NoErrors) = 600 and Table.RowCount(BadRows) = 0
        and Table.RowCount(Table.Distinct(NoErrors, {"case_id", "as_of_date"})) = 600,
    CheckedRows = if ShapeOK then NoErrors
        else error Error.Record("ORI.ProcessRows", "Expected 600 unique as-of cases with correct unknown outcomes, dates, flags, and durations.", null),
    Typed = Table.TransformColumnTypes(CheckedRows, List.Transform(IntegerColumns, each {_, Int64.Type})),
    Sorted = Table.Sort(Typed, {{"unit_id", Order.Ascending}, {"case_type", Order.Ascending}, {"case_id", Order.Ascending}})
in
    Sorted
