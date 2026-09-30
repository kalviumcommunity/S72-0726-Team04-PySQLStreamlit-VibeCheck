# Day 05 - Add a code-backed data dictionary for onboarding fields

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-05-data-dictionary` |
| **Base** | `main` - stacked on `gaurav/day-04-type-standardisation` (merge PR 04 first) |
| **Roadmap** | Day 5 (Sat 01 Aug 2026) - *Create data dictionary mapping onboarding fields to business meaning.* |
| **Type** | `docs` |
| **Size** | 2 code files, +180 / -0 lines (docs excluded) |

## Summary

Adds `pipeline/data_dictionary.py`, which maps every onboarding field to its raw type, pipeline dtype, allowed values and business meaning, and generates `docs/data_dictionary/onboarding.md` from it.

## Why

- A dictionary kept only in a document goes stale; this one is checked against the dataset in CI (`--check`).
- Leadership asked what each field *means*, not just its type - e.g. the buddy comparison caveat (19 of 1,470).

## What changed

- `FieldSpec` entries for all 9 onboarding columns.
- `--write` regenerates the Markdown; `--check` fails on undocumented columns, missing columns or a stale doc.
- Generated `docs/data_dictionary/onboarding.md`.
- `tests/test_data_dictionary.py`: 6 tests, including dtype agreement with the standardised frame.

## How to test

```bash
python -m pipeline.data_dictionary --check
pytest tests/test_data_dictionary.py
```

## Result

All 9 columns documented; the documented dtypes match what `pipeline.standardize` actually produces.

## Diff highlight

`pipeline/data_dictionary.py` (excerpt)

```diff
+ONBOARDING_FIELDS: tuple[FieldSpec, ...] = (
+    FieldSpec("employee_id", "INTEGER", "int64", "Positive integer, unique", False,
+              "Employee identifier (IBM HR `EmployeeNumber`).",
+              "Join key to employees, tool usage and support tickets. Exactly one onboarding record per employee."),
+    FieldSpec("orientation_completed", "TEXT Yes/No", "boolean", "Yes / No", False,
+              "Whether the hire attended company orientation.",
+              "First onboarding milestone. A missed orientation means the hire was never formally walked "
+              "through processes and tooling."),
+    FieldSpec("training_completion_percent", "FLOAT", "float64", "0.0 - 100.0", False,
+              "Share of mandatory training modules completed.",
+              "Main readiness signal: `100 - value` is the outstanding training that drives the friction "
+              "score."),
+    FieldSpec("onboarding_days", "INTEGER", "Int64", "0 - 365", False,
+              "Days taken to finish onboarding (Completed) or elapsed so far (In Progress / Delayed).",
+              "Speed to productivity. Basis for time-to-value, completion-time outliers and speed rankings."),
+    FieldSpec("onboarding_status", "TEXT", "category", "Completed < In Progress < Delayed", False,
+              "Lifecycle state of the onboarding checklist, ordered by severity.",
+              "Delayed hires are the intervention list; In Progress hires are watched for overrun."),
+    FieldSpec("manager_assigned", "TEXT Yes/No", "boolean", "Yes / No", False,
+              "Whether a reporting manager was assigned at start.",
+              "Without a manager nobody is accountable for unblocking the hire; a root-cause candidate for delays."),
+    FieldSpec("buddy_assigned", "TEXT Yes/No", "boolean", "Yes / No", False,
+              "Whether a peer onboarding buddy was assigned.",
+              "Reach of the buddy programme. Only 19 of 1,470 hires have no buddy, so buddy vs no-buddy "
+              "comparisons are indicative, not conclusive."),
+    FieldSpec("first_week_checkin", "TEXT Yes/No", "boolean", "Yes / No", False,
+              "Whether a manager check-in happened in week one.",
+              "Early feedback loop; when it is missed, blockers surface weeks later as tickets or delays."),
+    FieldSpec("onboarding_completion_date", "TEXT YYYY-MM-DD", "datetime64", "ISO date; empty while in flight", True,
+              "Date the hire finished onboarding.",
+              "Anchors cohort trends by completion month. Must be present for every Completed hire."),
+)
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `docs/data_dictionary/onboarding.md` | 17 | 0 |
| `pipeline/data_dictionary.py` | 134 | 0 |
| `tests/test_data_dictionary.py` | 46 | 0 |
| `docs/prs/gaurav/day-05-data-dictionary.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
