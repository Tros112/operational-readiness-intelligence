-- Synthetic inventory. Grain: one currently valid person/qualification at D.
-- Include unavailable people. The three flags are overlapping cumulative windows.
SELECT DISTINCT 'synthetic_only' AS data_classification, :as_of_date AS as_of_date,
       p.unit_id, u.unit_name, p.person_id, pq.qualification_id, q.qualification_name,
       p.is_available, pq.valid_from, pq.expiration_date,
       CAST(julianday(pq.expiration_date) - julianday(:as_of_date) AS INTEGER)
           AS days_until_expiration,
       CASE WHEN pq.expiration_date <= date(:as_of_date, '+30 days')
            THEN 1 ELSE 0 END AS expires_within_30_days,
       CASE WHEN pq.expiration_date <= date(:as_of_date, '+60 days')
            THEN 1 ELSE 0 END AS expires_within_60_days,
       CASE WHEN pq.expiration_date <= date(:as_of_date, '+90 days')
            THEN 1 ELSE 0 END AS expires_within_90_days
FROM personnel_qualifications AS pq
JOIN personnel AS p ON p.person_id = pq.person_id
JOIN units AS u ON u.unit_id = p.unit_id
JOIN qualification_types AS q ON q.qualification_id = pq.qualification_id
WHERE pq.valid_from <= :as_of_date AND :as_of_date < pq.expiration_date
ORDER BY p.unit_id, p.person_id, pq.qualification_id;
