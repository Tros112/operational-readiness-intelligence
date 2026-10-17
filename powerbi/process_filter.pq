// New Blank Query named process_filter, after process_case_detail.
// Derived lookup only; no new operational source. Do not join back in Power Query.
let
    Types = Table.Distinct(Table.SelectColumns(process_case_detail, {"case_type"})),
    Expected = {"evaluation", "onboarding", "records_update", "transfer"},
    Sorted = Table.Sort(Types, {{"case_type", Order.Ascending}}),
    Checked = if Table.RowCount(Sorted) = 4 and Sorted[case_type] = Expected then Sorted
        else error Error.Record("ORI.ProcessTypes", "Expected the four synthetic case types.", null)
in
    Checked
