# Day 11 - Behavioural analysis of new hires: fast vs slow onboarders

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-11-fast-vs-slow-behaviour` |
| **Base** | `main` - stacked on `gaurav/day-10-completion-distribution` (merge PR 10 first) |
| **Roadmap** | Day 11 (Fri 07 Aug 2026) - *Behavioural analysis of new hires (fast vs slow onboarding).* |
| **Type** | `feat` |
| **Size** | 2 code files, +187 / -0 lines (docs excluded) |

## Summary

Adds `pipeline/analysis/behaviour.py`: compares fast and slow new hires on training, setup and tool engagement, reporting Cohen's d and group sizes next to the raw means.

## Why

- A raw gap on a small group looks dramatic; effect sizes and a `reliable` flag keep it honest.

## What changed

- `compare_fast_vs_slow()`, `cohens_d()`, `effect_label()`, `behaviour_findings()`.
- `tool_minutes_by_speed()` - minutes per hire per tool (non-users count as 0, so the averages are fair).
- CLI: `python -m pipeline.analysis.behaviour`. `tests/test_behaviour.py`: 9 tests.

## How to test

```bash
python -m pipeline.analysis.behaviour
pytest tests/test_behaviour.py
```

## Result

Among new hires (39 fast vs 77 slow), slow onboarders have less training (d = -0.57) and spend fewer minutes on every tool except Slack.

## Diff highlight

`pipeline/analysis/behaviour.py` (excerpt)

```diff
+def cohens_d(fast: pd.Series, slow: pd.Series) -> float:
+    """Standardised mean difference, slow minus fast (positive = slow hires score higher)."""
+    a, b = fast.dropna().astype("float64"), slow.dropna().astype("float64")
+    if len(a) < 2 or len(b) < 2:
+        return float("nan")
+    pooled = math.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2))
+    return float((b.mean() - a.mean()) / pooled) if pooled else float("nan")
+
+
+def effect_label(d: float) -> str:
+    if math.isnan(d):
+        return "n/a"
+    size = abs(d)
+    return "large" if size >= 0.8 else "medium" if size >= 0.5 else "small" if size >= 0.2 else "negligible"
+
+
+def _speed_groups(features: pd.DataFrame, new_hires_only: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
+    if new_hires_only:
+        if "is_new_hire" not in features.columns:
+            raise KeyError("is_new_hire missing: build features with the employees table joined")
+        features = features[features["is_new_hire"]]
+    speed = features["onboarding_speed"]
+    return features[speed.eq("fast")], features[speed.eq("slow")]
+
+
+def compare_fast_vs_slow(features: pd.DataFrame, metrics: Sequence[str] = BEHAVIOUR_METRICS,
+                         new_hires_only: bool = True, min_group_size: int = 10) -> pd.DataFrame:
+    fast, slow = _speed_groups(features, new_hires_only)
+    rows = []
+    for metric in metrics:
+        fast_mean, slow_mean = fast[metric].mean(), slow[metric].mean()
+        d = cohens_d(fast[metric], slow[metric])
+        rows.append({
+            "metric": metric,
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/analysis/behaviour.py` | 121 | 0 |
| `tests/test_behaviour.py` | 66 | 0 |
| `docs/prs/gaurav/day-11-fast-vs-slow-behaviour.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
