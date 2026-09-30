-- Hires, share and averages per onboarding status. For open onboardings,
-- onboarding_days is the time elapsed so far rather than a completion time.
SELECT
    onboarding_status,
    COUNT(*)                                                              AS hires,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM onboarding), 2)        AS share_pct,
    ROUND(AVG(onboarding_days), 2)                                        AS avg_days,
    ROUND(AVG(training_completion_percent), 2)                            AS avg_training_pct
FROM onboarding
GROUP BY onboarding_status
ORDER BY hires DESC;
