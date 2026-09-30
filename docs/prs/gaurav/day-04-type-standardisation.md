# Day 04 - Standardise onboarding dates, Yes/No flags and status categories

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-04-type-standardisation` |
| **Base** | `main` - stacked on `gaurav/day-03-onboarding-cleaning` (merge PR 03 first) |
| **Roadmap** | Day 4 (Fri 31 Jul 2026) - *Standardize data types (dates, booleans, categories) in onboarding dataset.* |
| **Type** | `feat` |
| **Size** | 2 code files, +188 / -0 lines (docs excluded) |

## Summary

Adds `pipeline/standardize.py`: Yes/No-style flags become nullable booleans, completion dates are parsed as strict ISO-8601, and statuses become an ordered categorical (`Completed < In Progress < Delayed`). `prepare_onboarding()` chains cleaning and standardisation.

## Why

- Treating an unknown token as `False` silently corrupts coverage KPIs, so unknown tokens become null and are counted.
- Ambiguous dates like `01/07/2026` are rejected rather than guessed.

## What changed

- `to_boolean`, `to_date`, `to_status` - each returns (series, problem_count).
- `StandardizationReport` also flags Completed hires without a completion date.
- `load_standardized_onboarding()` - the analysis-ready onboarding frame.
- `tests/test_standardize.py`: 6 tests.

## How to test

```bash
pytest tests/test_standardize.py
```

## Result

Real data: 1,433 Completed / 23 In Progress / 14 Delayed, 19 hires without a buddy, no standardisation issues.

## Diff highlight

`pipeline/standardize.py` (excerpt)

```diff
+def to_boolean(series: pd.Series) -> tuple[pd.Series, int]:
+    """Map Yes/No-style tokens to a nullable boolean. Returns (series, unknown_count)."""
+    tokens = series.map(_token)
+    mapped = tokens.map(lambda t: True if t in TRUE_TOKENS else False if t in FALSE_TOKENS else None)
+    unknown = int((tokens.notna() & mapped.isna()).sum())
+    return mapped.astype("boolean"), unknown
+
+
+def to_date(series: pd.Series) -> tuple[pd.Series, int]:
+    """Parse ISO-8601 dates only; ambiguous formats like 01/07/2026 are rejected, not guessed."""
+    parsed = pd.to_datetime(series, errors="coerce", format="ISO8601")
+    unparseable = int((series.notna() & parsed.isna()).sum())
+    return parsed.dt.normalize(), unparseable
+
+
+def to_status(series: pd.Series) -> tuple[pd.Series, int]:
+    """Canonicalise status spellings into an ordered categorical."""
+    keys = series.map(lambda v: re.sub(r"[\s_\-]+", " ", t) if (t := _token(v)) else None)
+    canonical = keys.map(lambda k: _STATUS_ALIASES.get(k) if k else None)
+    unknown = int((keys.notna() & canonical.isna()).sum())
+    status = pd.Categorical(canonical, categories=STATUS_ORDER, ordered=True)
+    return pd.Series(status, index=series.index, name=series.name), unknown
+
+
+def standardize_onboarding(clean: pd.DataFrame) -> tuple[pd.DataFrame, StandardizationReport]:
+    """Convert a cleaned onboarding frame to analysis-ready dtypes."""
+    out = clean.copy()
+    report = StandardizationReport()
+    for col in BOOLEAN_COLUMNS:
+        out[col], report.unknown_booleans[col] = to_boolean(out[col])
+    for col in DATE_COLUMNS:
+        out[col], report.unparseable_dates[col] = to_date(out[col])
+    out["onboarding_status"], report.unknown_statuses = to_status(out["onboarding_status"])
+    out["employee_id"] = out["employee_id"].astype("int64")
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/standardize.py` | 115 | 0 |
| `tests/test_standardize.py` | 73 | 0 |
| `docs/prs/gaurav/day-04-type-standardisation.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
