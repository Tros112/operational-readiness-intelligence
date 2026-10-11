// Paste this WHOLE query into a Blank Query > Advanced Editor.
// Replace only ProjectRoot with your existing Windows Git project path.
// Run src/check_powerbi_input.py before every import/refresh for SHA-256 checks.
// This M query checks manifest/shape/date/grain; it does NOT compute file hashes.
let
    ProjectRoot = "PASTE_EXISTING_PROJECT_ROOT_HERE",
    ExportFolder = ProjectRoot & "\data\processed\dashboard\",
    ExpectedDate = #date(2026, 10, 7),
    ExpectedColumns = {
        "data_classification", "as_of_date", "unit_id", "unit_name",
        "total_personnel_count", "available_personnel_count", "required_personnel_count",
        "staffing_gap", "staffing_coverage_ratio", "required_holder_slots", "capped_holder_slots",
        "qualification_coverage_ratio", "qualification_gap", "qualification_pair_count",
        "qualification_pairs_with_gap", "fragile_qualification_pairs", "single_holder_dependency_pairs",
        "unit_attention_flag", "certificates_expiring_30_days", "people_affected_30_days",
        "certificates_expiring_60_days", "people_affected_60_days",
        "certificates_expiring_90_days", "people_affected_90_days"
    },
    TextColumns = {"data_classification", "unit_id", "unit_name"},
    RatioColumns = {"staffing_coverage_ratio", "qualification_coverage_ratio"},
    CountColumns = List.Difference(ExpectedColumns, TextColumns & RatioColumns & {"as_of_date"}),
    Manifest = Json.Document(File.Contents(ExportFolder & "export_manifest.json")),
    ManifestOK = try (
        Manifest[status] = "passed" and Manifest[exports_ready] = true and Manifest[exit_code] = 0
        and Manifest[as_of_date] = "2026-10-07" and Manifest[data_classification] = "synthetic_only"
        and Manifest[database_matches_passed_source] = true
        and Manifest[cross_query_reconciliation] = "passed"
    ) otherwise false,
    Entry = if ManifestOK then Record.Field(Manifest[files], "unit_summary.csv")
        else error Error.Record("ORI.ExportBlocked", "Run the exporter successfully before refresh.", null),
    EntryOK = try (
        Entry[rows] = 6 and Entry[grain] = {"unit_id", "as_of_date"}
        and Entry[columns] = ExpectedColumns and Text.Length(Entry[sha256]) = 64
    ) otherwise false,
    CsvBytes = if EntryOK then Binary.Buffer(File.Contents(ExportFolder & "unit_summary.csv"))
        else error Error.Record("ORI.ManifestMismatch", "Unexpected unit-summary manifest/schema.", null),
    Parsed = Csv.Document(CsvBytes, [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Parsed, [PromoteAllScalars = true]),
    CheckedHeaders = if Table.ColumnNames(Headers) = ExpectedColumns then Headers
        else error Error.Record("ORI.HeaderMismatch", "CSV columns differ from the approved schema.", null),
    NullRatios = Table.ReplaceValue(CheckedHeaders, "", null, Replacer.ReplaceValue, RatioColumns),
    Numeric = Table.TransformColumnTypes(NullRatios,
        List.Transform(TextColumns, each {_, type text}) & {{"as_of_date", type date}}
        & List.Transform(CountColumns & RatioColumns, each {_, type number}), "en-US"),
    ErrorRows = Table.SelectRowsWithErrors(Numeric),
    NoTypeErrors = if Table.RowCount(ErrorRows) = 0 then Numeric
        else error Error.Record("ORI.TypeError", "Source values have invalid types; do not remove errors.", null),
    BadRows = Table.SelectRows(NoTypeErrors, (row) =>
        row[data_classification] <> "synthetic_only" or row[as_of_date] <> ExpectedDate
        or row[unit_id] = null or row[unit_id] = "" or row[unit_name] = null or row[unit_name] = ""
        or List.AnyTrue(List.Transform(CountColumns, (name) =>
            let value = Record.Field(row, name)
            in value = null or value < 0 or value <> Number.RoundDown(value)))
        or not List.Contains({0, 1}, row[unit_attention_flag])),
    ShapeOK = Table.RowCount(NoTypeErrors) = 6 and Table.RowCount(BadRows) = 0
        and Table.RowCount(Table.Distinct(NoTypeErrors, {"unit_id", "as_of_date"})) = 6,
    CheckedRows = if ShapeOK then NoTypeErrors
        else error Error.Record("ORI.GrainOrDateError", "Expected six unique synthetic unit rows at October 7.", null),
    Typed = Table.TransformColumnTypes(CheckedRows, List.Transform(CountColumns, each {_, Int64.Type})),
    Sorted = Table.Sort(Typed, {{"unit_id", Order.Ascending}})
in
    Sorted
