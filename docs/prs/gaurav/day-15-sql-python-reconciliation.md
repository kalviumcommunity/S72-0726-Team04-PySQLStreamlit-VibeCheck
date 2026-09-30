# Day 15 - Validate SQL outputs against the Python pipeline

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-15-sql-python-reconciliation` |
| **Base** | `main` - stacked on `gaurav/day-14-sql-window-rankings` (merge PR 14 first) |
| **Roadmap** | Day 16 (Wed 12 Aug 2026) - *Validate SQL vs Python outputs.* |
| **Type** | `feat` |
| **Size** | 3 code files, +235 / -0 lines (docs excluded) |

## Summary

Adds `pipeline/kpis.py` (the pandas twin of the SQL KPIs) and `pipeline/reconcile.py`, which compares SQL-on-raw-tables with Python-on-cleaned-frames: headline KPIs, every department metric, per-employee speed ranks and the new-hire cohort.

## Why

- If SQL and Python agree, neither the SQL nor the cleaning logic has drifted - a strong guard for both.

## What changed

- `Check` (tolerance-aware; allows +/-0.01 because the engines round .xx5 differently).
- `python_speed_ranks()` reproduces SQL `RANK()` semantics in pandas.
- CLI `python -m pipeline reconcile` (stages SQLite; `--no-stage` for MySQL). `tests/test_reconcile.py`: 7 tests.
- A drift test injects a fake cleaning bug and asserts it is caught.

## How to test

```bash
python -m pipeline.reconcile
pytest tests/test_reconcile.py
```

## Result

26 / 26 checks agree between SQL and Python on the committed data.

## Diff highlight

`pipeline/reconcile.py` (excerpt)

```diff
+def python_speed_ranks(features: pd.DataFrame) -> pd.DataFrame:
+    """pandas equivalent of RANK() OVER (PARTITION BY department ORDER BY days, training DESC)."""
+    keys = ["Department", "onboarding_days", "training_completion_percent"]
+    completed = features.loc[features["onboarding_status"].eq("Completed"), ["employee_id", *keys]]
+    ordered = completed.sort_values(keys, ascending=[True, True, False])
+    ordered = ordered.assign(_position=ordered.groupby("Department", observed=True).cumcount() + 1)
+    rank = ordered.groupby(keys, observed=True)["_position"].transform("min")
+    return ordered.assign(dept_speed_rank=rank)[["employee_id", "dept_speed_rank"]]
+
+
+def reconcile(engine: Engine, features: pd.DataFrame, tolerance: float = 0.01) -> list[Check]:
+    checks: list[Check] = []
+
+    sql_kpis, py_kpis = onboarding_kpis(engine), compute_onboarding_kpis(features)
+    checks += [Check(f"overall.{key}", sql_kpis[key], py_kpis[key], tolerance) for key in KPI_KEYS]
+
+    sql_dept = run_query(engine, "kpis/by_department").set_index("department")
+    py_dept = compute_department_kpis(features).set_index("department")
+    for department in sorted(set(sql_dept.index) | set(py_dept.index)):
+        checks += [Check(f"department[{department}].{metric}", _value(sql_dept, department, metric),
+                         _value(py_dept, department, metric), tolerance) for metric in DEPARTMENT_METRICS]
+
+    sql_ranks = rank_hires_by_speed(engine)[["employee_id", "dept_speed_rank"]]
+    joined = sql_ranks.merge(python_speed_ranks(features), on="employee_id", how="outer", suffixes=("_sql", "_py"))
+    agreeing = int((joined["dept_speed_rank_sql"] == joined["dept_speed_rank_py"]).sum())
+    checks.append(Check("rankings.dept_speed_rank_agreement", float(len(joined)), float(agreeing), 0))
+
+    cohort = run_query(engine, "kpis/new_hire_cohort").iloc[0]
+    checks.append(Check("cohort.new_hires", float(cohort["new_hires"]), float(features["is_new_hire"].sum()), 0))
+    return checks
+
+
+def reconciliation_table(checks: list[Check]) -> pd.DataFrame:
+    columns = ["name", "sql_value", "python_value", "delta", "passed"]
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/kpis.py` | 62 | 0 |
| `pipeline/reconcile.py` | 111 | 0 |
| `tests/test_reconcile.py` | 62 | 0 |
| `docs/prs/gaurav/day-15-sql-python-reconciliation.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
