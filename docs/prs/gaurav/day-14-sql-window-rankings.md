# Day 14 - Rank hires by onboarding speed with SQL window functions

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-14-sql-window-rankings` |
| **Base** | `main` - stacked on `gaurav/day-13-sql-onboarding-kpis` (merge PR 13 first) |
| **Roadmap** | Day 15 (Tue 11 Aug 2026) - *SQL window functions for ranking hires by onboarding speed.* |
| **Type** | `feat` |
| **Size** | 5 code files, +194 / -0 lines (docs excluded) |

## Summary

Adds three window-function queries and `pipeline/rankings.py`: department and company speed ranks, speed quartiles, percentiles, days vs the department average, the top N per department, and a month-over-month trend with a rolling average.

## Why

- Uses `RANK`, `DENSE_RANK`, `NTILE`, `PERCENT_RANK`, `AVG() OVER`, `LAG` and a `ROWS BETWEEN` frame, with deterministic tie-breakers so MySQL and SQLite return identical results.

## What changed

- `rankings/onboarding_speed.sql`, `rankings/fastest_per_department.sql` (bound `top_n`), `rankings/department_monthly_trend.sql`.
- `top_n` is validated (rejects 0, negatives, booleans and injection strings).
- Refactor: `cli_engine()` shares the local-only staging guard between CLIs.
- `tests/test_rankings.py`: 9 tests, including hand-checked RANK vs DENSE_RANK tie semantics.

## How to test

```bash
python -m pipeline.rankings --stage --top 3
pytest tests/test_rankings.py
```

## Result

All 1,433 completed hires ranked. Every department's rank 1 holds its minimum days, and every department fills all 4 quartiles.

## Diff highlight

`pipeline/sql/rankings/onboarding_speed.sql` (excerpt)

```diff
+-- Rank completed hires by onboarding speed (fewer days = faster).
+-- Ties on days are broken by higher training completion; NTILE also uses
+-- employee_id so every engine assigns quartiles identically.
+WITH completed AS (
+    SELECT
+        o.employee_id,
+        e.Department                   AS department,
+        e.JobRole                      AS job_role,
+        o.onboarding_days,
+        o.training_completion_percent
+    FROM onboarding o
+    JOIN employees e ON e.employee_id = o.employee_id
+    WHERE o.onboarding_status = 'Completed'
+)
+SELECT
+    employee_id,
+    department,
+    job_role,
+    onboarding_days,
+    training_completion_percent,
+    RANK() OVER (PARTITION BY department
+                 ORDER BY onboarding_days, training_completion_percent DESC)           AS dept_speed_rank,
+    DENSE_RANK() OVER (ORDER BY onboarding_days)                                      AS company_speed_rank,
+    NTILE(4) OVER (PARTITION BY department
+                   ORDER BY onboarding_days, training_completion_percent DESC, employee_id) AS dept_speed_quartile,
+    ROUND(PERCENT_RANK() OVER (ORDER BY onboarding_days), 4)                          AS company_percentile,
+    ROUND(onboarding_days - AVG(onboarding_days) OVER (PARTITION BY department), 2)   AS days_vs_dept_avg,
+    COUNT(*) OVER (PARTITION BY department)                                           AS dept_completed
+FROM completed
+ORDER BY department, dept_speed_rank, employee_id;
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/rankings.py` | 51 | 0 |
| `pipeline/sql/rankings/department_monthly_trend.sql` | 25 | 0 |
| `pipeline/sql/rankings/fastest_per_department.sql` | 19 | 0 |
| `pipeline/sql/rankings/onboarding_speed.sql` | 30 | 0 |
| `tests/test_rankings.py` | 69 | 0 |
| `docs/prs/gaurav/day-14-sql-window-rankings.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
