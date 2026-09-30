# Day 10 - Distribution analysis of onboarding completion times

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-10-completion-distribution` |
| **Base** | `main` - stacked on `gaurav/day-09-feature-engineering` (merge PR 09 first) |
| **Roadmap** | Day 10 (Thu 06 Aug 2026) - *Distribution analysis of onboarding completion times.* |
| **Type** | `feat` |
| **Size** | 3 code files, +182 / -0 lines (docs excluded) |

## Summary

Adds `pipeline/analysis/` with a dependency-free Markdown table renderer and `distribution.py`: percentiles, spread and skew overall, by status and by department, plus a histogram and auto-generated key findings.

## Why

- We need to know what a *normal* onboarding looks like before calling one slow.

## What changed

- `describe_completion_times()`, `histogram()`, `key_findings()`, `distribution_report()`.
- CLI: `python -m pipeline.analysis.distribution [--output report.md]`.
- `tests/test_distribution.py`: 6 tests.

## How to test

```bash
python -m pipeline.analysis.distribution
pytest tests/test_distribution.py
```

## Result

Completed onboardings take a median of 12 days and 90% finish within 17. Delayed hires have already spent 3.0x the median (36 days).

## Diff highlight

`pipeline/analysis/distribution.py` (excerpt)

```diff
+def describe_completion_times(df: pd.DataFrame, column: str = "onboarding_days",
+                              by: str | None = None) -> pd.DataFrame:
+    """Count, centre, spread, percentiles and shape - overall or per group."""
+    values = df.loc[df[column].notna()].assign(**{column: lambda d: d[column].astype("float64")})
+    groups = [("All", values)] if by is None else [(str(k), g) for k, g in values.groupby(by, observed=True)]
+    rows = []
+    for name, group in groups:
+        v = group[column]
+        quantiles = v.quantile(PERCENTILES)
+        rows.append({
+            "group": name,
+            "count": len(v),
+            "mean": v.mean(),
+            "std": v.std(),
+            "min": v.min(),
+            **{f"p{round(p * 100)}": quantiles[p] for p in PERCENTILES},
+            "max": v.max(),
+            "skew": v.skew() if len(v) > 2 else float("nan"),
+            "cv": v.std() / v.mean() if v.mean() else float("nan"),
+        })
+    return pd.DataFrame(rows).round(2)
+
+
+def histogram(df: pd.DataFrame, column: str = "onboarding_days", bin_width: int = 2) -> pd.DataFrame:
+    """Fixed-width bins [start, end) with counts and shares."""
+    values = df[column].dropna().astype("float64")
+    start = math.floor(values.min() / bin_width) * bin_width
+    edges = np.arange(start, values.max() + bin_width + 1, bin_width)
+    counts, edges = np.histogram(values, bins=edges)
+    table = pd.DataFrame({"bin_start": edges[:-1].astype(int), "bin_end": edges[1:].astype(int), "count": counts})
+    table["share"] = (table["count"] / len(values)).round(4)
+    return table
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/analysis/__init__.py` | 17 | 0 |
| `pipeline/analysis/distribution.py` | 109 | 0 |
| `tests/test_distribution.py` | 56 | 0 |
| `docs/prs/gaurav/day-10-completion-distribution.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
