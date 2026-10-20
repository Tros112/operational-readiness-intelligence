-- Embed the reviewed detail query; selection values are bound parameters.
-- Sum components within ONE horizon; never combine repeated requirements.
WITH detail AS (
    /*SCENARIO_DETAIL*/
), selected AS (
    SELECT * FROM detail AS d WHERE /*SCOPE*/ 1 = 1
)
SELECT COUNT(*) AS qualification_pair_count,
       COALESCE(SUM(required_holder_count), 0) AS required_holder_slots,
       COALESCE(SUM(current_eligible_holder_count), 0) AS current_eligible_holder_slots,
       COALESCE(SUM(projected_eligible_holder_count), 0) AS projected_eligible_holder_slots,
       COALESCE(SUM(eligible_holders_lost), 0) AS eligible_holder_slots_lost,
       COALESCE(SUM(current_capped_holder_count), 0) AS current_capped_holder_slots,
       COALESCE(SUM(projected_capped_holder_count), 0) AS projected_capped_holder_slots,
       COALESCE(SUM(current_gap), 0) AS current_gap,
       COALESCE(SUM(projected_gap), 0) AS projected_gap,
       COALESCE(SUM(additional_gap), 0) AS additional_gap,
       COALESCE(SUM(current_is_gap), 0) AS current_pairs_with_gap,
       COALESCE(SUM(projected_is_gap), 0) AS projected_pairs_with_gap,
       COALESCE(SUM(is_new_gap), 0) AS new_gap_pairs,
       COALESCE(SUM(current_is_fragile), 0) AS current_fragile_pairs,
       COALESCE(SUM(projected_is_fragile), 0) AS projected_fragile_pairs,
       1.0 * COALESCE(SUM(current_capped_holder_count), 0)
           / NULLIF(SUM(required_holder_count), 0) AS current_coverage_ratio,
       1.0 * COALESCE(SUM(projected_capped_holder_count), 0)
           / NULLIF(SUM(required_holder_count), 0) AS projected_coverage_ratio
FROM selected;
