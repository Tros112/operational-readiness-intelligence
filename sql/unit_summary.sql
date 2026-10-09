-- Synthetic executive inputs. Grain: one unit at :as_of_date.
-- Aggregate people, qualification slots, and expirations separately before joining.
WITH staff AS (
    SELECT unit_id, COUNT(*) AS total_personnel_count,
           SUM(CASE WHEN is_available = 1 THEN 1 ELSE 0 END) AS available_personnel_count
    FROM personnel GROUP BY unit_id
), valid_certificates AS (
    SELECT DISTINCT p.unit_id, p.person_id, p.is_available,
           pq.qualification_id, pq.expiration_date
    FROM personnel AS p
    JOIN personnel_qualifications AS pq ON pq.person_id = p.person_id
    WHERE pq.valid_from <= :as_of_date AND :as_of_date < pq.expiration_date
), holders AS (
    SELECT unit_id, qualification_id, COUNT(DISTINCT person_id) AS holder_count
    FROM valid_certificates WHERE is_available = 1
    GROUP BY unit_id, qualification_id
), pair_counts AS (
    SELECT r.unit_id, r.required_holder_count, COALESCE(h.holder_count, 0) AS holder_count
    FROM unit_qualification_requirements AS r
    LEFT JOIN holders AS h
      ON r.unit_id = h.unit_id AND r.qualification_id = h.qualification_id
), qualifications AS (
    SELECT unit_id, COUNT(*) AS qualification_pair_count,
           SUM(required_holder_count) AS required_holder_slots,
           SUM(MIN(holder_count, required_holder_count)) AS capped_holder_slots,
           SUM(MAX(required_holder_count - holder_count, 0)) AS qualification_gap,
           SUM(CASE WHEN holder_count < required_holder_count THEN 1 ELSE 0 END)
               AS qualification_pairs_with_gap,
           SUM(CASE WHEN holder_count = required_holder_count AND required_holder_count > 0
                    THEN 1 ELSE 0 END) AS fragile_qualification_pairs,
           SUM(CASE WHEN holder_count = 1 AND required_holder_count = 1
                    THEN 1 ELSE 0 END) AS single_holder_dependency_pairs
    FROM pair_counts GROUP BY unit_id
), expirations AS (
    SELECT unit_id,
           SUM(CASE WHEN expiration_date <= date(:as_of_date, '+30 days') THEN 1 ELSE 0 END)
               AS certificates_expiring_30_days,
           COUNT(DISTINCT CASE WHEN expiration_date <= date(:as_of_date, '+30 days')
                               THEN person_id END) AS people_affected_30_days,
           SUM(CASE WHEN expiration_date <= date(:as_of_date, '+60 days') THEN 1 ELSE 0 END)
               AS certificates_expiring_60_days,
           COUNT(DISTINCT CASE WHEN expiration_date <= date(:as_of_date, '+60 days')
                               THEN person_id END) AS people_affected_60_days,
           SUM(CASE WHEN expiration_date <= date(:as_of_date, '+90 days') THEN 1 ELSE 0 END)
               AS certificates_expiring_90_days,
           COUNT(DISTINCT CASE WHEN expiration_date <= date(:as_of_date, '+90 days')
                               THEN person_id END) AS people_affected_90_days
    FROM valid_certificates GROUP BY unit_id
)
SELECT 'synthetic_only' AS data_classification, :as_of_date AS as_of_date,
       u.unit_id, u.unit_name, COALESCE(s.total_personnel_count, 0) AS total_personnel_count,
       COALESCE(s.available_personnel_count, 0) AS available_personnel_count,
       u.required_personnel_count,
       MAX(u.required_personnel_count - COALESCE(s.available_personnel_count, 0), 0) AS staffing_gap,
       1.0 * COALESCE(s.available_personnel_count, 0)
           / NULLIF(u.required_personnel_count, 0) AS staffing_coverage_ratio,
       COALESCE(q.required_holder_slots, 0) AS required_holder_slots,
       COALESCE(q.capped_holder_slots, 0) AS capped_holder_slots,
       1.0 * COALESCE(q.capped_holder_slots, 0)
           / NULLIF(q.required_holder_slots, 0) AS qualification_coverage_ratio,
       COALESCE(q.qualification_gap, 0) AS qualification_gap,
       COALESCE(q.qualification_pair_count, 0) AS qualification_pair_count,
       COALESCE(q.qualification_pairs_with_gap, 0) AS qualification_pairs_with_gap,
       COALESCE(q.fragile_qualification_pairs, 0) AS fragile_qualification_pairs,
       COALESCE(q.single_holder_dependency_pairs, 0) AS single_holder_dependency_pairs,
       CASE WHEN COALESCE(s.available_personnel_count, 0) < u.required_personnel_count
                  OR COALESCE(q.qualification_pairs_with_gap, 0) > 0
            THEN 1 ELSE 0 END AS unit_attention_flag,
       COALESCE(e.certificates_expiring_30_days, 0) AS certificates_expiring_30_days,
       COALESCE(e.people_affected_30_days, 0) AS people_affected_30_days,
       COALESCE(e.certificates_expiring_60_days, 0) AS certificates_expiring_60_days,
       COALESCE(e.people_affected_60_days, 0) AS people_affected_60_days,
       COALESCE(e.certificates_expiring_90_days, 0) AS certificates_expiring_90_days,
       COALESCE(e.people_affected_90_days, 0) AS people_affected_90_days
FROM units AS u
LEFT JOIN staff AS s ON s.unit_id = u.unit_id
LEFT JOIN qualifications AS q ON q.unit_id = u.unit_id
LEFT JOIN expirations AS e ON e.unit_id = u.unit_id
ORDER BY u.unit_id;
