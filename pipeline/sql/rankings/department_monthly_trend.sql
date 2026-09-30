-- Month-over-month completion speed per department: LAG gives the change against
-- the previous completion month, a 3-row window gives a rolling average.
WITH monthly AS (
    SELECT
        e.Department                                   AS department,
        SUBSTR(o.onboarding_completion_date, 1, 7)     AS completion_month,
        COUNT(*)                                       AS completions,
        AVG(o.onboarding_days)                         AS mean_days
    FROM onboarding o
    JOIN employees e ON e.employee_id = o.employee_id
    WHERE o.onboarding_status = 'Completed'
      AND o.onboarding_completion_date IS NOT NULL
    GROUP BY e.Department, SUBSTR(o.onboarding_completion_date, 1, 7)
)
SELECT
    department,
    completion_month,
    completions,
    ROUND(mean_days, 2)                                                            AS avg_days,
    ROUND(mean_days - LAG(mean_days) OVER (PARTITION BY department ORDER BY completion_month), 2)
                                                                                   AS change_vs_prev_month,
    ROUND(AVG(mean_days) OVER (PARTITION BY department ORDER BY completion_month
                               ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2)       AS rolling_3_month_avg_days
FROM monthly
ORDER BY department, completion_month;
