// Paste the WHOLE query into a new Blank Query named expiration_detail.
// Replace only ProjectRoot with the existing Windows project root (not its powerbi folder).
// Requires unit_summary and the new qualification_filter query. Run check_powerbi_input.py before import/refresh.
// SHA-256 is checked by Python; this M query checks manifest/schema/types/date/grain and values.
let
    ProjectRoot = "PASTE_EXISTING_PROJECT_ROOT_HERE",
    ExportFolder = ProjectRoot & "\data\processed\dashboard\",
    ExpectedDate = #date(2026, 10, 7),
    ExpectedColumns = {"data_classification", "as_of_date", "unit_id", "unit_name", "person_id", "qualification_id", "qualification_name", "is_available", "valid_from", "expiration_date", "days_until_expiration", "expires_within_30_days", "expires_within_60_days", "expires_within_90_days"},
    TextColumns = {"data_classification", "unit_id", "unit_name", "person_id", "qualification_id", "qualification_name"},
    DateColumns = {"as_of_date", "valid_from", "expiration_date"},
    RatioColumns = {},
    CountColumns = {"is_available", "days_until_expiration", "expires_within_30_days", "expires_within_60_days", "expires_within_90_days"},
    Manifest = Json.Document(File.Contents(ExportFolder & "export_manifest.json")),
    ManifestOK = try (
        Manifest[status] = "passed" and Manifest[exports_ready] = true and Manifest[exit_code] = 0
        and Manifest[as_of_date] = "2026-10-07" and Manifest[data_classification] = "synthetic_only"
        and Manifest[database_matches_passed_source] = true
        and Manifest[cross_query_reconciliation] = "passed"
    ) otherwise false,
    Entry = if ManifestOK then Record.Field(Manifest[files], "expiration_detail.csv")
        else error Error.Record("ORI.ExportBlocked", "Run a successful export before import or refresh.", null),
    EntryOK = try (
        Entry[rows] = 193
        and Entry[grain] = {"person_id", "qualification_id", "as_of_date"}
        and Entry[columns] = ExpectedColumns and Text.Length(Entry[sha256]) = 64
    ) otherwise false,
    CsvBytes = if EntryOK then Binary.Buffer(File.Contents(ExportFolder & "expiration_detail.csv"))
        else error Error.Record("ORI.ManifestMismatch", "Unexpected expiration_detail manifest or schema.", null),
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
    QualificationNames = Record.FromList(qualification_filter[qualification_name],
        qualification_filter[qualification_id]),
    BadRows = Table.SelectRows(NoTypeErrors, (row) =>
        let
            KeysOK = List.AllTrue(List.Transform(TextColumns, (name) =>
                let value = Record.Field(row, name) in value <> null and value <> "")),
            CountsOK = List.AllTrue(List.Transform(CountColumns, (name) =>
                let value = Record.Field(row, name)
                in value <> null and value >= 0 and value = Number.RoundDown(value)))
        in
            if not KeysOK or not CountsOK or row[data_classification] <> "synthetic_only"
                or row[as_of_date] <> ExpectedDate or row[valid_from] = null
                or row[expiration_date] = null then true
            else if not Record.HasFields(UnitNames, row[unit_id])
                or not Record.HasFields(QualificationNames, row[qualification_id]) then true
            else
                let
                    Days = Duration.Days(row[expiration_date] - ExpectedDate),
                    Within30 = if Days <= 30 then 1 else 0,
                    Within60 = if Days <= 60 then 1 else 0,
                    Within90 = if Days <= 90 then 1 else 0
                in row[unit_name] <> Record.Field(UnitNames, row[unit_id])
                    or row[qualification_name] <> Record.Field(QualificationNames, row[qualification_id])
                    or not List.Contains({0, 1}, row[is_available])
                    or row[valid_from] > ExpectedDate or row[expiration_date] <= ExpectedDate
                    or row[days_until_expiration] <> Days
                    or row[expires_within_30_days] <> Within30
                    or row[expires_within_60_days] <> Within60
                    or row[expires_within_90_days] <> Within90),
    Assignments = Table.Distinct(Table.SelectColumns(NoTypeErrors,
        {"person_id", "unit_id", "is_available"})),
    People = Table.Distinct(Table.SelectColumns(NoTypeErrors, {"person_id"})),
    ShapeOK = Table.RowCount(NoTypeErrors) = 193 and Table.RowCount(BadRows) = 0
        and Table.RowCount(Table.Distinct(NoTypeErrors,
            {"person_id", "qualification_id", "as_of_date"})) = 193
        and Table.RowCount(Assignments) = Table.RowCount(People),
    CheckedRows = if ShapeOK then NoTypeErrors
        else error Error.Record("ORI.ExpirationInput", "Expected 193 unique current certificates, consistent person/unit availability, and inclusive cumulative flags.", null),
    Typed = Table.TransformColumnTypes(CheckedRows,
        List.Transform(CountColumns, each {_, Int64.Type})),
    Sorted = Table.Sort(Typed, {{"unit_id", Order.Ascending},
        {"person_id", Order.Ascending}, {"qualification_id", Order.Ascending}})
in
    Sorted
