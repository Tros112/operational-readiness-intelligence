-- Synthetic current coverage. Grain: one unit/qualification at :as_of_date.
-- Filter certificates before LEFT JOIN so requirements with no holders survive.
WITH holders AS (
    SELECT p.unit_id, pq.qualification_id, COUNT(DISTINCT p.person_id) AS holder_count
    FROM personnel AS p
    JOIN personnel_qualifications AS pq ON pq.person_id = p.person_id
    WHERE p.is_available = 1
      AND pq.valid_from <= :as_of_date AND :as_of_date < pq.expiration_date
    GROUP BY p.unit_id, pq.qualification_id
), pairs AS (
    SELECT r.unit_id, r.qualification_id, r.required_holder_count,
           COALESCE(h.holder_count, 0) AS valid_available_holder_count
    FROM unit_qualification_requirements AS r
    LEFT JOIN holders AS h
      ON h.unit_id = r.unit_id AND h.qualification_id = r.qualification_id
)
SELECT 'synthetic_only' AS data_classification, :as_of_date AS as_of_date,
       pairs.unit_id, u.unit_name, pairs.qualification_id, q.qualification_name,
       required_holder_count, valid_available_holder_count,
       MIN(valid_available_holder_count, required_holder_count) AS capped_holder_count,
       MAX(required_holder_count - valid_available_holder_count, 0) AS current_gap,
       1.0 * MIN(valid_available_holder_count, required_holder_count)
           / NULLIF(required_holder_count, 0) AS qualification_coverage_ratio,
       CASE WHEN valid_available_holder_count = required_holder_count
                  AND required_holder_count > 0 THEN 1 ELSE 0 END AS is_fragile,
       CASE WHEN valid_available_holder_count = 1 AND required_holder_count = 1
            THEN 1 ELSE 0 END AS is_single_holder_dependency
FROM pairs
JOIN units AS u ON u.unit_id = pairs.unit_id
JOIN qualification_types AS q ON q.qualification_id = pairs.qualification_id
ORDER BY pairs.unit_id, pairs.qualification_id;
