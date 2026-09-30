# Day 03 - Add reusable cleaning functions for onboarding data

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-03-onboarding-cleaning` |
| **Base** | `main` - stacked on `gaurav/day-02-csv-json-ingestion` (merge PR 02 first) |
| **Roadmap** | Day 3 (Thu 30 Jul 2026) - *Build reusable functions for reading and cleaning onboarding data.* |
| **Type** | `feat` |
| **Size** | 2 code files, +206 / -0 lines (docs excluded) |

## Summary

Adds `pipeline/cleaning.py`: small, reusable functions (snake_case column names, whitespace trimming, range checks, key de-duplication) composed into `clean_onboarding()`, which returns the cleaned frame and a `CleaningReport` of everything it changed.

## Why

- Every later step (types, merge, SQL) assumes one clean row per employee.
- Silent fixes hide data problems, so every change is counted in the report.

## What changed

- Out-of-range values (e.g. 120% training, -3 days) are nulled, never clipped, so a typo cannot look like a fully trained hire.
- Duplicate `employee_id`s keep the most complete row; later rows win ties.
- Invalid IDs (`abc`, negatives) are dropped and counted.
- `tests/test_cleaning.py`: 11 tests, including a deliberately messy fixture.

## How to test

```bash
pytest tests/test_cleaning.py
```

## Result

The messy fixture is repaired exactly as expected; the committed dataset passes with zero changes (1,470 -> 1,470 rows).

## Diff highlight

`pipeline/cleaning.py` (excerpt)

```diff
+def clean_onboarding(raw: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
+    """Run every cleaning step on a raw onboarding frame and report what changed."""
+    report = CleaningReport(rows_in=len(raw))
+    df = snake_case_columns(raw)
+    require_columns(df, ONBOARDING_COLUMNS)
+    df, report.blank_strings = strip_strings(df)
+
+    ids = pd.to_numeric(df["employee_id"], errors="coerce")
+    valid_id = ids.notna() & (ids > 0) & (ids == ids.round())
+    report.invalid_ids = int((~valid_id).sum())
+    df = df.loc[valid_id].assign(employee_id=ids[valid_id].astype("int64"))
+
+    df, report.invalid_values = null_invalid_numbers(df, VALID_RANGES)
+    df, report.exact_duplicates, report.duplicate_ids = deduplicate_by_key(df, "employee_id")
+    report.rows_out = len(df)
+    return df, report
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/cleaning.py` | 125 | 0 |
| `tests/test_cleaning.py` | 81 | 0 |
| `docs/prs/gaurav/day-03-onboarding-cleaning.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
