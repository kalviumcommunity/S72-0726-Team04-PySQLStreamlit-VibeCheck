# Day 06 - Detect outliers in onboarding completion times (IQR and MAD)

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-06-completion-outliers` |
| **Base** | `main` - stacked on `gaurav/day-05-data-dictionary` (merge PR 05 first) |
| **Roadmap** | Day 6 (Sun 02 Aug 2026) - *Detect outliers in onboarding completion times.* |
| **Type** | `feat` |
| **Size** | 2 code files, +153 / -0 lines (docs excluded) |

## Summary

Adds `pipeline/outliers.py` with two robust methods - Tukey IQR fences and the modified z-score (MAD) - optionally computed per department, with small groups falling back to company-wide bounds.

## Why

- Mean +/- 3 SD is distorted by the long tail of delayed onboardings; IQR and MAD are not.
- Per-department bounds must not flag noise in tiny departments (Human Resources has 63 hires).

## What changed

- `iqr_bounds`, `mad_bounds` (with a MeanAD fallback when MAD collapses to 0).
- `detect_completion_outliers()` returns bounds, scope, direction and a flag per hire; `summarize_outliers()`.
- `tests/test_outliers.py`: 7 tests.

## How to test

```bash
pytest tests/test_outliers.py
```

## Result

IQR (upper fence 27.4 days) flags 20 hires (13 Delayed, 7 In Progress); per-department MAD flags 9, all Delayed. No Completed hire is ever flagged.

## Diff highlight

`pipeline/outliers.py` (excerpt)

```diff
+def detect_completion_outliers(
+    df: pd.DataFrame,
+    column: str = "onboarding_days",
+    method: str = "iqr",
+    group_by: str | None = None,
+    k: float = 1.5,
+    threshold: float = 3.5,
+    min_group_size: int = 20,
+    context_columns: Sequence[str] = ("onboarding_status",),
+) -> pd.DataFrame:
+    """Return one row per employee with the bounds applied and an outlier flag."""
+    if method not in METHODS:
+        raise ValueError(f"method must be one of {METHODS}, got {method!r}")
+    data = df.loc[df[column].notna()]
+    values = data[column].astype("float64")
+    overall_low, overall_high = _bounds(values, method, k, threshold)
+    lower = pd.Series(overall_low, index=data.index)
+    upper = pd.Series(overall_high, index=data.index)
+    scope = pd.Series("all", index=data.index, dtype="object")
+
+    if group_by:
+        for group, index in data.groupby(group_by, observed=True).groups.items():
+            if len(index) >= min_group_size:
+                lower.loc[index], upper.loc[index] = _bounds(values.loc[index], method, k, threshold)
+                scope.loc[index] = str(group)
+
+    direction = pd.Series(None, index=data.index, dtype="object")
+    direction = direction.mask(values > upper, "high").mask(values < lower, "low")
+    context = [c for c in (group_by, *context_columns) if c and c in data.columns]
+    result = data[["employee_id", *context]].assign(
+        **{column: values},
+        lower_bound=lower.round(2),
+        upper_bound=upper.round(2),
+        bounds_scope=scope,
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/outliers.py` | 91 | 0 |
| `tests/test_outliers.py` | 62 | 0 |
| `docs/prs/gaurav/day-06-completion-outliers.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
