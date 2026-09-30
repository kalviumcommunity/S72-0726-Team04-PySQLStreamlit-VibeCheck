# Day 08 - Merge onboarding with tool usage and validate the join

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-08-merge-tool-usage` |
| **Base** | `main` - stacked on `gaurav/day-07-schema-contracts` (merge PR 07 first) |
| **Roadmap** | Day 8 (Tue 04 Aug 2026) - *Merge onboarding + tool usage datasets. Validate joins.* |
| **Type** | `feat` |
| **Size** | 2 code files, +132 / -0 lines (docs excluded) |

## Summary

Adds `pipeline/merge.py`: tool usage is aggregated to one row per employee (sessions, logins, minutes, distinct tools, active days, first/last activity) and left-joined onto onboarding with pandas' `validate="one_to_one"`. A `JoinReport` records matches and orphans.

## Why

- Joining 1:N logs directly would duplicate onboarding rows and inflate every KPI.
- A blanket `fillna(0)` previously turned missing categories into `0` (AUDIT R4); only count columns are zero-filled here.

## What changed

- `aggregate_tool_usage()`, `merge_onboarding_tool_usage()` and `JoinReport` (match rate, orphan IDs).
- Refuses onboarding input with duplicate employee IDs.
- `tests/test_merge.py`: 4 tests.

## How to test

```bash
pytest tests/test_merge.py
```

## Result

1,470 / 1,470 hires matched; all 7,810 tool sessions and every active minute are preserved after aggregation.

## Diff highlight

`pipeline/merge.py` (excerpt)

```diff
+def merge_onboarding_tool_usage(onboarding: pd.DataFrame,
+                                tool_usage: pd.DataFrame) -> tuple[pd.DataFrame, JoinReport]:
+    """Left-join per-employee tool activity onto onboarding (one row per hire)."""
+    duplicated = onboarding.loc[onboarding["employee_id"].duplicated(), "employee_id"]
+    if len(duplicated):
+        raise ValueError(f"onboarding has duplicate employee_id values: {sorted(duplicated.unique())[:5]}")
+
+    activity = aggregate_tool_usage(tool_usage)
+    left = onboarding.assign(employee_id=onboarding["employee_id"].astype("Int64"))
+    merged = left.merge(activity, on="employee_id", how="left", validate="one_to_one", indicator=True)
+
+    orphans = activity.loc[~activity["employee_id"].isin(left["employee_id"]), "employee_id"]
+    report = JoinReport(
+        onboarding_rows=len(left),
+        matched=int((merged["_merge"] == "both").sum()),
+        onboarding_only=int((merged["_merge"] == "left_only").sum()),
+        orphan_tool_employee_ids=tuple(int(i) for i in orphans),
+    )
+    merged["has_tool_activity"] = merged["_merge"].eq("both")
+    for col in TOOL_COUNT_COLUMNS:
+        merged[col] = merged[col].fillna(0).astype("int64")
+    merged = merged.drop(columns="_merge")
+    merged["employee_id"] = merged["employee_id"].astype("int64")
+
+    if report.orphan_tool_employee_ids:
+        log.warning("tool usage for employees without onboarding records: %s",
+                    list(report.orphan_tool_employee_ids)[:10])
+    log.info(report.summary())
+    return merged, report
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `pipeline/merge.py` | 84 | 0 |
| `tests/test_merge.py` | 48 | 0 |
| `docs/prs/gaurav/day-08-merge-tool-usage.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
