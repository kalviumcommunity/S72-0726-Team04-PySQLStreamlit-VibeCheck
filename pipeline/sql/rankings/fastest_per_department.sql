-- The N fastest completed hires in each department. Ties share a rank, so a
-- department can return more than N rows. N is bound as the top_n parameter.
WITH ranked AS (
    SELECT
        o.employee_id,
        e.Department                   AS department,
        e.JobRole                      AS job_role,
        o.onboarding_days,
        o.training_completion_percent,
        RANK() OVER (PARTITION BY e.Department
                     ORDER BY o.onboarding_days, o.training_completion_percent DESC) AS dept_speed_rank
    FROM onboarding o
    JOIN employees e ON e.employee_id = o.employee_id
    WHERE o.onboarding_status = 'Completed'
)
SELECT *
FROM ranked
WHERE dept_speed_rank <= :top_n
ORDER BY department, dept_speed_rank, employee_id;
