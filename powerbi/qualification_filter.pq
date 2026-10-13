// New Blank Query named qualification_filter, after qualification_detail.
// This derives eight filter rows from the approved detail; it adds no operational source.
let
    Source = Table.SelectColumns(qualification_detail, {"qualification_id", "qualification_name"}),
    Pairs = Table.Distinct(Source),
    BadKeys = Table.SelectRows(Pairs, each
        [qualification_id] = null or [qualification_id] = ""
        or [qualification_name] = null or [qualification_name] = ""),
    ShapeOK = Table.RowCount(Pairs) = 8 and Table.RowCount(BadKeys) = 0
        and Table.RowCount(Table.Distinct(Pairs, {"qualification_id"})) = 8,
    Checked = if ShapeOK then Pairs
        else error Error.Record("ORI.QualificationLookup", "Expected eight unique qualification IDs with consistent labels.", null),
    Typed = Table.TransformColumnTypes(Checked,
        {{"qualification_id", type text}, {"qualification_name", type text}}),
    Sorted = Table.Sort(Typed, {{"qualification_id", Order.Ascending}})
in
    Sorted
