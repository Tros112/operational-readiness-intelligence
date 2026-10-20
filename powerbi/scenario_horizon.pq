// New Blank Query named scenario_horizon, after qualification_scenario.
// Derived selector only. Single select one horizon; do not sum repeated requirements.
let
    Source = Table.Distinct(Table.SelectColumns(qualification_scenario, {"horizon_days"})),
    Sorted = Table.Sort(Source, {{"horizon_days", Order.Ascending}}),
    Checked = if Table.RowCount(Sorted) = 3 and Sorted[horizon_days] = {30, 60, 90} then Sorted
        else error Error.Record("ORI.ScenarioHorizons", "Expected the three contracted no-renewal horizons.", null),
    Labelled = Table.AddColumn(Checked, "horizon_label", each Text.From([horizon_days], "en-US") & " days", type text),
    Typed = Table.TransformColumnTypes(Labelled, {{"horizon_days", Int64.Type}, {"horizon_label", type text}})
in
    Typed
