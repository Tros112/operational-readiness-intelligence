-- Synthetic no-renewal scenario. One unit/qualification at one bound horizon.
-- Only today's available, valid cohort can survive. Expiration is exclusive.
WITH current_certificates AS (
    SELECT p.unit_id, pq.qualification_id, p.person_id, pq.expiration_date
    FROM personnel AS p
    JOIN personnel_qualifications AS pq ON pq.person_id = p.person_id
    WHERE p.is_available = 1
      AND pq.valid_from <= :as_of_date AND :as_of_date < pq.expiration_date
), holders AS (
    SELECT unit_id, qualification_id,
           COUNT(DISTINCT person_id) AS current_holders,
           COUNT(DISTINCT CASE
               WHEN expiration_date > date(:as_of_date, '+' || :horizon_days || ' days')
               THEN person_id END) AS projected_holders
    FROM current_certificates
    GROUP BY unit_id, qualification_id
), pairs AS (
    SELECT r.unit_id, r.qualification_id, r.required_holder_count,
           COALESCE(h.current_holders, 0) AS current_holders,
           COALESCE(h.projected_holders, 0) AS projected_holders
    FROM unit_qualification_requirements AS r
    LEFT JOIN holders AS h
      ON h.unit_id = r.unit_id AND h.qualification_id = r.qualification_id
)
SELECT 'synthetic_only' AS data_classification, 'no_renewal' AS scenario,
       :as_of_date AS as_of_date, :horizon_days AS horizon_days,
       date(:as_of_date, '+' || :horizon_days || ' days') AS horizon_date,
       p.unit_id, u.unit_name, p.qualification_id, q.qualification_name,
       required_holder_count,
       current_holders AS current_eligible_holder_count,
       projected_holders AS projected_eligible_holder_count,
       current_holders - projected_holders AS eligible_holders_lost,
       MIN(current_holders, required_holder_count) AS current_capped_holder_count,
       MIN(projected_holders, required_holder_count) AS projected_capped_holder_count,
       MAX(required_holder_count - current_holders, 0) AS current_gap,
       MAX(required_holder_count - projected_holders, 0) AS projected_gap,
       MAX(required_holder_count - projected_holders, 0)
           - MAX(required_holder_count - current_holders, 0) AS additional_gap,
       1.0 * MIN(current_holders, required_holder_count)
           / NULLIF(required_holder_count, 0) AS current_coverage_ratio,
       1.0 * MIN(projected_holders, required_holder_count)
           / NULLIF(required_holder_count, 0) AS projected_coverage_ratio,
       CASE WHEN current_holders < required_holder_count THEN 1 ELSE 0 END AS current_is_gap,
       CASE WHEN projected_holders < required_holder_count THEN 1 ELSE 0 END AS projected_is_gap,
       CASE WHEN current_holders >= required_holder_count
                  AND projected_holders < required_holder_count THEN 1 ELSE 0 END AS is_new_gap,
       CASE WHEN required_holder_count > 0 AND current_holders = required_holder_count
            THEN 1 ELSE 0 END AS current_is_fragile,
       CASE WHEN required_holder_count > 0 AND projected_holders = required_holder_count
            THEN 1 ELSE 0 END AS projected_is_fragile
FROM pairs AS p
JOIN units AS u ON u.unit_id = p.unit_id
JOIN qualification_types AS q ON q.qualification_id = p.qualification_id
ORDER BY p.unit_id, p.qualification_id;
