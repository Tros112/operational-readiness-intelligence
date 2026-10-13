// Paste the WHOLE query into a new Blank Query named qualification_detail.
// Replace only ProjectRoot with the existing Windows project root (not its powerbi folder).
// Requires the existing unit_summary query. Run check_powerbi_input.py before import/refresh.
// SHA-256 is checked by Python; this M query checks manifest/schema/types/date/grain and values.
let
    ProjectRoot = "PASTE_EXISTING_PROJECT_ROOT_HERE",
    ExportFolder = ProjectRoot & "\data\processed\dashboard\",
    ExpectedDate = #date(2026, 10, 7),
    ExpectedColumns = {"data_classification", "as_of_date", "unit_id", "unit_name", "qualification_id", "qualification_name", "required_holder_count", "valid_available_holder_count", "capped_holder_count", "current_gap", "qualification_coverage_ratio", "is_fragile", "is_single_holder_dependency"},
    TextColumns = {"data_classification", "unit_id", "unit_name", "qualification_id", "qualification_name"},
    DateColumns = {"as_of_date"},
    RatioColumns = {"qualification_coverage_ratio"},
    CountColumns = {"required_holder_count", "valid_available_holder_count", "capped_holder_count", "current_gap", "is_fragile", "is_single_holder_dependency"},
    Manifest = Json.Document(File.Contents(ExportFolder & "export_manifest.json")),
    ManifestOK = try (
        Manifest[status] = "passed" and Manifest[exports_ready] = true and Manifest[exit_code] = 0
        and Manifest[as_of_date] = "2026-10-07" and Manifest[data_classification] = "synthetic_only"
        and Manifest[database_matches_passed_source] = true
        and Manifest[cross_query_reconciliation] = "passed"
    ) otherwise false,
    Entry = if ManifestOK then Record.Field(Manifest[files], "qualification_detail.csv")
        else error Error.Record("ORI.ExportBlocked", "Run a successful export before import or refresh.", null),
    EntryOK = try (
        Entry[rows] = 48
        and Entry[grain] = {"unit_id", "qualification_id", "as_of_date"}
        and Entry[columns] = ExpectedColumns and Text.Length(Entry[sha256]) = 64
    ) otherwise false,
    CsvBytes = if EntryOK then Binary.Buffer(File.Contents(ExportFolder & "qualification_detail.csv"))
        else error Error.Record("ORI.ManifestMismatch", "Unexpected qualification_detail manifest or schema.", null),
    Parsed = Csv.Document(CsvBytes, [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Parsed, [PromoteAllScalars = true]),
    CheckedHeaders = if Table.ColumnNames(Headers) = ExpectedColumns then Headers
        else error Error.Record("ORI.HeaderMismatch", "CSV columns differ from the approved schema.", null),
    NullRatios = if List.IsEmpty(RatioColumns) then CheckedHeaders
        else Table.ReplaceValue(CheckedHeaders, "", null, Replacer.ReplaceValue, RatioColumns),
    Numeric = Table.TransformColumnTypes(NullRatios,
        List.Transform(TextColumns, each {_, type text})
        & List.Transform(DateColumns, each {_, type date})
        & List.Transform(CountColumns & RatioColumns, each {_, type number}), "en-US"),
    NoTypeErrors = if Table.RowCount(Table.SelectRowsWithErrors(Numeric)) = 0 then Numeric
        else error Error.Record("ORI.TypeError", "Source values have invalid types; do not remove errors.", null),
    Units = Table.SelectColumns(unit_summary, {"unit_id", "unit_name", "as_of_date"}),
    UnitsOK = Table.RowCount(Units) = 6
        and Table.RowCount(Table.Distinct(Units, {"unit_id"})) = 6
        and Table.RowCount(Table.SelectRows(Units, each [as_of_date] <> ExpectedDate)) = 0,
    UnitNames = if UnitsOK then Record.FromList(Units[unit_name], Units[unit_id])
        else error Error.Record("ORI.UnitLookup", "Expected the six-unit summary at the same analysis date.", null),
    BadRows = Table.SelectRows(NoTypeErrors, (row) =>
        let
            KeysOK = List.AllTrue(List.Transform(TextColumns, (name) =>
                let value = Record.Field(row, name) in value <> null and value <> "")),
            CountsOK = List.AllTrue(List.Transform(CountColumns, (name) =>
                let value = Record.Field(row, name)
                in value <> null and value >= 0 and value = Number.RoundDown(value)))
        in
            if not KeysOK or not CountsOK or row[data_classification] <> "synthetic_only"
                or row[as_of_date] <> ExpectedDate then true
            else if not Record.HasFields(UnitNames, row[unit_id]) then true
            else
                let
                    Required = row[required_holder_count],
                    Holders = row[valid_available_holder_count],
                    Capped = List.Min({Required, Holders}),
                    Gap = List.Max({Required - Holders, 0}),
                    RatioOK = if Required = 0 then row[qualification_coverage_ratio] = null
                        else row[qualification_coverage_ratio] <> null
                            and Number.Abs(row[qualification_coverage_ratio] - Capped / Required) <= 0.000000000001,
                    Fragile = if Required > 0 and Holders = Required then 1 else 0,
                    SingleHolder = if Required = 1 and Holders = 1 then 1 else 0
                in row[unit_name] <> Record.Field(UnitNames, row[unit_id])
                    or row[capped_holder_count] <> Capped or row[current_gap] <> Gap
                    or row[is_fragile] <> Fragile or row[is_single_holder_dependency] <> SingleHolder
                    or not RatioOK),
    QualificationNames = Table.Distinct(Table.SelectColumns(NoTypeErrors,
        {"qualification_id", "qualification_name"})),
    ShapeOK = Table.RowCount(NoTypeErrors) = 48 and Table.RowCount(BadRows) = 0
        and Table.RowCount(Table.Distinct(NoTypeErrors,
            {"unit_id", "qualification_id", "as_of_date"})) = 48
        and Table.RowCount(QualificationNames) = 8
        and Table.RowCount(Table.Distinct(QualificationNames, {"qualification_id"})) = 8,
    CheckedRows = if ShapeOK then NoTypeErrors
        else error Error.Record("ORI.QualificationInput", "Expected 48 valid, unique unit/qualification pairs and eight consistent qualifications.", null),
    Typed = Table.TransformColumnTypes(CheckedRows,
        List.Transform(CountColumns, each {_, Int64.Type})),
    Sorted = Table.Sort(Typed, {{"unit_id", Order.Ascending}, {"qualification_id", Order.Ascending}})
in
    Sorted
