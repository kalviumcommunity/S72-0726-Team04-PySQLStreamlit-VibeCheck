# Day 13 - SQL layer: MySQL-ready engine and onboarding KPI queries

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-13-sql-onboarding-kpis` |
| **Base** | `main` - stacked on `gaurav/day-12-delay-root-causes` (merge PR 12 first) |
| **Roadmap** | Day 13 (Sun 09 Aug 2026) - *Write SQL queries for onboarding KPIs.* |
| **Type** | `feat` |
| **Size** | 10 code files, +318 / -0 lines (docs excluded) |

## Summary

Adds the SQL layer. `pipeline/db.py` builds a SQLAlchemy engine from `VIBECHECK_DB_URL` (`mysql+pymysql://...` for the team MySQL, local SQLite by default). Five portable KPI queries live in `pipeline/sql/kpis/`.

## Why

- The project brief is Python + SQL; KPIs must be reproducible straight from the database.
- The same `.sql` file has to run on MySQL 8 and SQLite: no `DATE_FORMAT`/`strftime`, and no reserved aliases such as `delayed`.

## What changed

- Queries: overall, by_department, status_breakdown, new_hire_cohort, completions_by_month.
- `sql_queries.py`: query catalogue, path-traversal-safe loader, MySQL `DECIMAL` -> float, CLI.
- `--stage` loads the CSVs into *local SQLite only*; it refuses to overwrite a shared MySQL database.
- Passwords are masked in all logs and errors. `tests/test_sql_queries.py`: 12 tests.

## How to test

```bash
python -m pipeline.sql_queries kpis/overall --stage
pytest tests/test_sql_queries.py
```

## Result

Completion rate 97.48%, buddy coverage 98.71%, 11.68 average days to complete, new-hire cohort 215.

## Diff highlight

`pipeline/sql/kpis/overall.sql` (excerpt)

```diff
+-- Headline onboarding KPIs across every employee with an onboarding record.
+-- "100.0 *" forces decimal division on both MySQL and SQLite; NULLIF guards an empty table.
+SELECT
+    COUNT(*)                                                                       AS total_hires,
+    SUM(CASE WHEN onboarding_status = 'Completed'   THEN 1 ELSE 0 END)             AS completed_count,
+    SUM(CASE WHEN onboarding_status = 'In Progress' THEN 1 ELSE 0 END)             AS in_progress_count,
+    SUM(CASE WHEN onboarding_status = 'Delayed'     THEN 1 ELSE 0 END)             AS delayed_count,
+    ROUND(100.0 * SUM(CASE WHEN onboarding_status = 'Completed' THEN 1 ELSE 0 END)
+          / NULLIF(COUNT(*), 0), 2)                                                AS completion_rate_pct,
+    ROUND(AVG(CASE WHEN onboarding_status = 'Completed' THEN onboarding_days END), 2) AS avg_days_to_complete,
+    ROUND(AVG(training_completion_percent), 2)                                     AS avg_training_pct,
+    ROUND(100.0 * SUM(CASE WHEN buddy_assigned = 'Yes' THEN 1 ELSE 0 END)
+          / NULLIF(COUNT(*), 0), 2)                                                AS buddy_coverage_pct,
+    ROUND(100.0 * SUM(CASE WHEN first_week_checkin = 'Yes' THEN 1 ELSE 0 END)
+          / NULLIF(COUNT(*), 0), 2)                                                AS first_week_checkin_pct
+FROM onboarding;
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/db.py` | 52 | 0 |
| `pipeline/sql/kpis/by_department.sql` | 13 | 0 |
| `pipeline/sql/kpis/completions_by_month.sql` | 11 | 0 |
| `pipeline/sql/kpis/new_hire_cohort.sql` | 21 | 0 |
| `pipeline/sql/kpis/overall.sql` | 16 | 0 |
| `pipeline/sql/kpis/status_breakdown.sql` | 11 | 0 |
| `pipeline/sql_queries.py` | 96 | 0 |
| `requirements-pipeline.txt` | 2 | 0 |
| `tests/conftest.py` | 13 | 0 |
| `tests/test_sql_queries.py` | 83 | 0 |
| `docs/prs/gaurav/day-13-sql-onboarding-kpis.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
