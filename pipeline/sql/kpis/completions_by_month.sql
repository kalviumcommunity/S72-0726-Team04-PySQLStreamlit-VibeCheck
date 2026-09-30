-- Completed onboardings per completion month. SUBSTR on an ISO date behaves the
-- same in MySQL and SQLite, unlike DATE_FORMAT / strftime.
SELECT
    SUBSTR(onboarding_completion_date, 1, 7)                              AS completion_month,
    COUNT(*)                                                              AS completions,
    ROUND(AVG(onboarding_days), 2)                                        AS avg_days_to_complete
FROM onboarding
WHERE onboarding_status = 'Completed'
  AND onboarding_completion_date IS NOT NULL
GROUP BY SUBSTR(onboarding_completion_date, 1, 7)
ORDER BY completion_month;
