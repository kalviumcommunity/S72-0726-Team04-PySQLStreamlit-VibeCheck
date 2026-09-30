-- Onboarding KPIs per department (employees and onboarding are 1:1 on employee_id).
SELECT
    e.Department                                                                     AS department,
    COUNT(*)                                                                         AS hires,
    ROUND(100.0 * SUM(CASE WHEN o.onboarding_status = 'Completed' THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                                             AS completion_rate_pct,
    SUM(CASE WHEN o.onboarding_status = 'Delayed' THEN 1 ELSE 0 END)                 AS delayed_count,
    ROUND(AVG(CASE WHEN o.onboarding_status = 'Completed' THEN o.onboarding_days END), 2) AS avg_days_to_complete,
    ROUND(AVG(o.training_completion_percent), 2)                                     AS avg_training_pct
FROM onboarding o
JOIN employees e ON e.employee_id = o.employee_id
GROUP BY e.Department
ORDER BY e.Department;
