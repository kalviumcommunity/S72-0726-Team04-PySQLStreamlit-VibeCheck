-- KPIs for the new-hire cohort: at most one year of tenure, or onboarding still open.
-- Same definition as pipeline.features.is_new_hire, so SQL and Python agree on who counts.
WITH cohort AS (
    SELECT o.*
    FROM onboarding o
    JOIN employees e ON e.employee_id = o.employee_id
    WHERE e.YearsAtCompany <= 1
       OR o.onboarding_status IN ('In Progress', 'Delayed')
)
SELECT
    COUNT(*)                                                              AS new_hires,
    SUM(CASE WHEN onboarding_status = 'Delayed' THEN 1 ELSE 0 END)        AS delayed_count,
    ROUND(100.0 * SUM(CASE WHEN onboarding_status = 'Completed' THEN 1 ELSE 0 END)
          / NULLIF(COUNT(*), 0), 2)                                       AS completion_rate_pct,
    ROUND(AVG(onboarding_days), 2)                                        AS avg_onboarding_days,
    ROUND(AVG(training_completion_percent), 2)                            AS avg_training_pct,
    ROUND(100.0 * SUM(CASE WHEN manager_assigned = 'Yes' THEN 1 ELSE 0 END)
          / NULLIF(COUNT(*), 0), 2)                                       AS manager_coverage_pct,
    ROUND(100.0 * SUM(CASE WHEN buddy_assigned = 'Yes' THEN 1 ELSE 0 END)
          / NULLIF(COUNT(*), 0), 2)                                       AS buddy_coverage_pct
FROM cohort;
