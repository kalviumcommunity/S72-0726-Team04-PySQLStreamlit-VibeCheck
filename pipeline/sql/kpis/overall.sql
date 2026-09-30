-- Headline onboarding KPIs across every employee with an onboarding record.
-- "100.0 *" forces decimal division on both MySQL and SQLite; NULLIF guards an empty table.
SELECT
    COUNT(*)                                                                       AS total_hires,
    SUM(CASE WHEN onboarding_status = 'Completed'   THEN 1 ELSE 0 END)             AS completed_count,
    SUM(CASE WHEN onboarding_status = 'In Progress' THEN 1 ELSE 0 END)             AS in_progress_count,
    SUM(CASE WHEN onboarding_status = 'Delayed'     THEN 1 ELSE 0 END)             AS delayed_count,
    ROUND(100.0 * SUM(CASE WHEN onboarding_status = 'Completed' THEN 1 ELSE 0 END)
          / NULLIF(COUNT(*), 0), 2)                                                AS completion_rate_pct,
    ROUND(AVG(CASE WHEN onboarding_status = 'Completed' THEN onboarding_days END), 2) AS avg_days_to_complete,
    ROUND(AVG(training_completion_percent), 2)                                     AS avg_training_pct,
    ROUND(100.0 * SUM(CASE WHEN buddy_assigned = 'Yes' THEN 1 ELSE 0 END)
          / NULLIF(COUNT(*), 0), 2)                                                AS buddy_coverage_pct,
    ROUND(100.0 * SUM(CASE WHEN first_week_checkin = 'Yes' THEN 1 ELSE 0 END)
          / NULLIF(COUNT(*), 0), 2)                                                AS first_week_checkin_pct
FROM onboarding;
