-- Case-level totals for the same fixed window/snapshot as process_case_detail.
-- Run directly for all cases. Python replaces the SCOPE predicate with bound
-- unit/type placeholders for selections; user values are never SQL fragments.
-- Ranked middle observations give an actual median for odd/even populations.
WITH scoped AS (
    SELECT c.*,
        CASE WHEN opened_date >= :period_start THEN 1 ELSE 0 END AS opened_in_period,
        CASE WHEN closed_date BETWEEN :period_start AND :as_of_date THEN 1 ELSE 0 END AS completed_in_period,
        CASE WHEN closed_date IS NULL OR closed_date > :as_of_date THEN 1 ELSE 0 END AS open_at_as_of
    FROM admin_cases AS c
    WHERE opened_date <= :as_of_date AND /*SCOPE*/ 1 = 1
), completed AS (
    SELECT CAST(julianday(closed_date) - julianday(opened_date) AS INTEGER) AS days,
        ROW_NUMBER() OVER (ORDER BY julianday(closed_date) - julianday(opened_date), case_id) AS position,
        COUNT(*) OVER () AS n
    FROM scoped WHERE completed_in_period = 1
), backlog AS (
    SELECT CAST(julianday(:as_of_date) - julianday(opened_date) AS INTEGER) AS days,
        ROW_NUMBER() OVER (ORDER BY julianday(:as_of_date) - julianday(opened_date), case_id) AS position,
        COUNT(*) OVER () AS n
    FROM scoped WHERE open_at_as_of = 1
)
SELECT
    COUNT(*) AS known_case_count,
    COALESCE(SUM(opened_in_period), 0) AS opened_case_count,
    COALESCE(SUM(completed_in_period), 0) AS completed_case_count,
    COALESCE(SUM(CASE WHEN completed_in_period = 1 THEN correction_required ELSE 0 END), 0) AS correction_case_count,
    SUM(CASE WHEN completed_in_period = 1 THEN correction_required ELSE 0 END) * 1.0
        / NULLIF(SUM(completed_in_period), 0) AS discrepancy_rate,
    (SELECT AVG(days) FROM completed WHERE position IN ((n + 1) / 2, (n + 2) / 2)) AS median_completed_cycle_days,
    COALESCE(SUM(open_at_as_of), 0) AS open_case_count,
    (SELECT AVG(days) FROM backlog WHERE position IN ((n + 1) / 2, (n + 2) / 2)) AS median_open_age_days,
    (SELECT MAX(days) FROM backlog) AS max_open_age_days
FROM scoped;
