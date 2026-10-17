-- One synthetic case opened on/before :as_of_date, including older backlog.
-- Opened/completed volume uses [:period_start, :as_of_date], inclusive.
-- Mask completions/outcomes after D; they are open at the snapshot.
SELECT
    'synthetic_only' AS data_classification,
    :as_of_date AS as_of_date,
    :period_start AS period_start,
    c.case_id,
    c.unit_id,
    u.unit_name,
    c.case_type,
    c.opened_date,
    CASE WHEN c.closed_date <= :as_of_date THEN c.closed_date END AS closed_date,
    CASE WHEN c.closed_date <= :as_of_date THEN c.correction_required END AS correction_required,
    CASE WHEN c.closed_date <= :as_of_date THEN 'Completed' ELSE 'Open' END AS status_at_as_of,
    CASE WHEN c.opened_date >= :period_start THEN 1 ELSE 0 END AS opened_in_period,
    CASE WHEN c.closed_date BETWEEN :period_start AND :as_of_date THEN 1 ELSE 0 END AS completed_in_period,
    CASE WHEN c.closed_date IS NULL OR c.closed_date > :as_of_date THEN 1 ELSE 0 END AS open_at_as_of,
    CASE WHEN c.closed_date BETWEEN :period_start AND :as_of_date
        THEN CAST(julianday(c.closed_date) - julianday(c.opened_date) AS INTEGER) END AS completed_cycle_days,
    CASE WHEN c.closed_date IS NULL OR c.closed_date > :as_of_date
        THEN CAST(julianday(:as_of_date) - julianday(c.opened_date) AS INTEGER) END AS open_age_days
FROM admin_cases AS c
JOIN units AS u ON u.unit_id = c.unit_id
WHERE c.opened_date <= :as_of_date
ORDER BY c.unit_id, c.case_type, c.case_id;
