# Day 09 - Engineer onboarding features (days to complete, speed bucket, new-hire flag)

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-09-feature-engineering` |
| **Base** | `main` - stacked on `gaurav/day-08-merge-tool-usage` (merge PR 08 first) |
| **Roadmap** | Day 9 (Wed 05 Aug 2026) - *Engineer features (e.g., "days to complete onboarding").* |
| **Type** | `feat` |
| **Size** | 2 code files, +153 / -0 lines (docs excluded) |

## Summary

Adds `pipeline/features.py` and `build_feature_table()` - the single table every analysis, export and dashboard view starts from.

## Why

- Analyses kept re-deriving the same columns in slightly different ways.

## What changed

- `days_to_complete`, `onboarding_start_date`, `training_gap_pct`, `setup_completeness`, `logins_per_active_day`, `minutes_per_session` (NaN, never inf, when dividing by 0).
- `onboarding_speed`: fast / typical / slow against the quartiles of *completed* hires; Delayed = slow.
- `is_new_hire`: tenure <= 1 year or onboarding still open (same cohort definition as the API audit).
- `tests/test_features.py`: 5 tests.

## How to test

```bash
pytest tests/test_features.py
```

## Result

Feature table: 1,470 rows, one per hire; 215 new hires; speed thresholds 8 and 15 days.

## Diff highlight

`pipeline/features.py` (excerpt)

```diff
+def engineer_features(merged: pd.DataFrame, employees: pd.DataFrame | None = None,
+                      thresholds: tuple[float, float] | None = None) -> pd.DataFrame:
+    out = merged.copy()
+    status = out["onboarding_status"]
+    days = out["onboarding_days"]
+
+    out["days_to_complete"] = days.where(status.eq("Completed"))
+    out["onboarding_start_date"] = (out["onboarding_completion_date"]
+                                    - pd.to_timedelta(days.astype("float64"), unit="D"))
+    out["training_gap_pct"] = (100 - out["training_completion_percent"]).round(1)
+    out["setup_completeness"] = out[list(SETUP_MILESTONES)].astype("float64").mean(axis=1).round(3)
+    out["logins_per_active_day"] = _ratio(out["total_logins"], out["active_days"]).round(2)
+    out["minutes_per_session"] = _ratio(out["total_active_minutes"], out["tool_sessions"]).round(1)
+
+    fast_max, slow_min = thresholds or speed_thresholds(out)
+    speed = np.select(
+        [_mask(status.eq("Delayed")), _mask(status.eq("In Progress")),
+         _mask(days <= fast_max), _mask(days >= slow_min)],
+        ["slow", "in_progress", "fast", "slow"],
+        default="typical",
+    )
+    out["onboarding_speed"] = pd.Categorical(speed, categories=SPEED_LABELS)
+
+    if employees is not None:
+        out = out.merge(employees[["employee_id", *EMPLOYEE_COLUMNS]], on="employee_id",
+                        how="left", validate="one_to_one")
+        tenure = pd.to_numeric(out["YearsAtCompany"], errors="coerce")
+        out["is_new_hire"] = _mask(tenure <= NEW_HIRE_MAX_TENURE_YEARS) | _mask(out["onboarding_status"].isin(OPEN_STATUSES))
+    return out
+
+
+def build_feature_table(settings: Settings | None = None) -> pd.DataFrame:
+    """Load, clean, merge and engineer: the one table every analysis starts from."""
+    onboarding = load_standardized_onboarding(settings)
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/features.py` | 85 | 0 |
| `tests/test_features.py` | 68 | 0 |
| `docs/prs/gaurav/day-09-feature-engineering.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
