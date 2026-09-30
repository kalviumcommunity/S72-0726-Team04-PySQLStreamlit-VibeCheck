# Day 12 - Root-cause investigation for delayed onboarding

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-12-delay-root-causes` |
| **Base** | `main` - stacked on `gaurav/day-11-fast-vs-slow-behaviour` (merge PR 11 first) |
| **Roadmap** | Day 12 (Sat 08 Aug 2026) - *Root cause investigation for delayed onboarding.* |
| **Type** | `feat` |
| **Size** | 2 code files, +192 / -0 lines (docs excluded) |

## Summary

Adds `pipeline/analysis/root_cause.py`: for each candidate factor, the delay rate *with* vs *without* it (lift, risk difference, coverage), with factors that are symptoms of delay ranked after real candidates.

## Why

- Leadership asked *why* hires are delayed, not just how many.

## What changed

- 8 candidate factors (no manager, no buddy, missed check-in, skipped orientation, low tool engagement, ...).
- `low_training` is marked as a symptom - delayed hires are undertrained *because* they are delayed.
- `delay_rate_by()` for department / job level; plain-English `root_cause_findings()`.
- `tests/test_root_cause.py`: 5 tests.

## How to test

```bash
python -m pipeline.analysis.root_cause
pytest tests/test_root_cause.py
```

## Result

All 7 new hires without a manager are Delayed (100% vs 3%, 29.7x). Bottom-quartile tool engagement is the widest signal (38.8x, covering 93% of delayed hires). Job level is not a driver (1.05x).

## Diff highlight

`pipeline/analysis/root_cause.py` (excerpt)

```diff
+def rank_root_causes(features: pd.DataFrame, factors: Sequence[Factor] = CANDIDATE_FACTORS,
+                     new_hires_only: bool = True, min_support: int = 5) -> pd.DataFrame:
+    pool, delayed = _population(features, new_hires_only)
+    total_delayed = int(delayed.sum())
+    rows = []
+    for factor in factors:
+        exposed = _mask(factor.predicate(pool))
+        n_with, n_without = int(exposed.sum()), int((~exposed).sum())
+        delayed_with, delayed_without = int((exposed & delayed).sum()), int((~exposed & delayed).sum())
+        rate_with = delayed_with / n_with if n_with else np.nan
+        rate_without = delayed_without / n_without if n_without else np.nan
+        if rate_without > 0:
+            lift = rate_with / rate_without
+        else:
+            lift = np.inf if rate_with > 0 else np.nan
+        rows.append({
+            "factor": factor.name,
+            "description": factor.description,
+            "hires_with_factor": n_with,
+            "delayed_with_factor": delayed_with,
+            "delay_rate_with_pct": rate_with * 100,
+            "delay_rate_without_pct": rate_without * 100,
+            "lift": lift,
+            "risk_difference_pts": (rate_with - rate_without) * 100,
+            "coverage_pct": delayed_with / total_delayed * 100 if total_delayed else np.nan,
+            "reliable": n_with >= min_support,
+            "symptom": factor.symptom,
+        })
+    table = pd.DataFrame(rows).sort_values(["reliable", "symptom", "lift"], ascending=[False, True, False],
+                                           na_position="last")
+    return table.round(2).reset_index(drop=True)
+
+
+def delay_rate_by(features: pd.DataFrame, column: str, new_hires_only: bool = True) -> pd.DataFrame:
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/analysis/root_cause.py` | 127 | 0 |
| `tests/test_root_cause.py` | 65 | 0 |
| `docs/prs/gaurav/day-12-delay-root-causes.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
