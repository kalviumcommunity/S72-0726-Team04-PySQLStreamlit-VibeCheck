-- Rank completed hires by onboarding speed (fewer days = faster).
-- Ties on days are broken by higher training completion; NTILE also uses
-- employee_id so every engine assigns quartiles identically.
WITH completed AS (
    SELECT
        o.employee_id,
        e.Department                   AS department,
        e.JobRole                      AS job_role,
        o.onboarding_days,
        o.training_completion_percent
    FROM onboarding o
    JOIN employees e ON e.employee_id = o.employee_id
    WHERE o.onboarding_status = 'Completed'
)
SELECT
    employee_id,
    department,
    job_role,
    onboarding_days,
    training_completion_percent,
    RANK() OVER (PARTITION BY department
                 ORDER BY onboarding_days, training_completion_percent DESC)           AS dept_speed_rank,
    DENSE_RANK() OVER (ORDER BY onboarding_days)                                      AS company_speed_rank,
    NTILE(4) OVER (PARTITION BY department
                   ORDER BY onboarding_days, training_completion_percent DESC, employee_id) AS dept_speed_quartile,
    ROUND(PERCENT_RANK() OVER (ORDER BY onboarding_days), 4)                          AS company_percentile,
    ROUND(onboarding_days - AVG(onboarding_days) OVER (PARTITION BY department), 2)   AS days_vs_dept_avg,
    COUNT(*) OVER (PARTITION BY department)                                           AS dept_completed
FROM completed
ORDER BY department, dept_speed_rank, employee_id;
