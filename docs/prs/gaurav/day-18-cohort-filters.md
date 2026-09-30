# Day 18 - Cohort filters for the onboarding dashboard

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-18-cohort-filters` |
| **Base** | `main` - stacked on `gaurav/day-17-export-datasets-charts` (merge PR 17 first) |
| **Roadmap** | Day 19 (Sat 15 Aug 2026) - *Add filters for onboarding cohorts.* |
| **Type** | `feat` |
| **Size** | 3 code files, +180 / -2 lines (docs excluded) |

## Summary

Adds a sidebar with filters for new hires, department, status, tenure band and buddy. KPI cards recompute for the cohort and show deltas vs the company, and a hire table lists the cohort most-urgent first.

## Why

- The same KPI means different things for a new-hire cohort and for 10-year veterans.

## What changed

- `CohortFilter` (validated value object, `describe()`), pure `apply_cohort_filter()`, `render_cohort_sidebar()`.
- An unknown buddy flag matches neither *With* nor *Without* buddy.
- Empty cohorts show a clear message instead of crashing. `tests/test_cohort_filters.py`: 11 tests.

## How to test

```bash
streamlit run streamlit_app/onboarding_ops.py
pytest tests/test_cohort_filters.py
```

## Result

New hires only: 215 of 1,470 hires, completion rate 82.8% (-14.7 pts vs company).

## Diff highlight

`streamlit_app/components/cohort_filters.py` (excerpt)

```diff
+def apply_cohort_filter(df: pd.DataFrame, cohort: CohortFilter) -> pd.DataFrame:
+    mask = np.ones(len(df), dtype=bool)
+    if cohort.departments:
+        mask &= _as_mask(df["Department"].isin(cohort.departments))
+    if cohort.statuses:
+        mask &= _as_mask(df["onboarding_status"].isin(cohort.statuses))
+    if cohort.tenure_bands:
+        mask &= _tenure_mask(pd.to_numeric(df["YearsAtCompany"], errors="coerce"), cohort.tenure_bands)
+    if cohort.buddy != "Any":
+        mask &= _as_mask(df["buddy_assigned"].eq(cohort.buddy == "With buddy"))
+    if cohort.new_hires_only:
+        mask &= _as_mask(df["is_new_hire"])
+    return df[mask]
+
+
+def render_cohort_sidebar(df: pd.DataFrame, key: str = "cohort") -> CohortFilter:
+    import streamlit as st
+
+    present = set(df["onboarding_status"].dropna())
+    with st.sidebar:
+        st.header("Cohort")
+        new_hires = st.toggle("New hires only", key=f"{key}_new_hires",
+                              help="Tenure of at most one year, or onboarding still open.")
+        departments = st.multiselect("Department", sorted(df["Department"].dropna().unique()), key=f"{key}_departments")
+        statuses = st.multiselect("Onboarding status", [s for s in STATUS_ORDER if s in present], key=f"{key}_statuses")
+        tenure = st.multiselect("Tenure", list(TENURE_BANDS), key=f"{key}_tenure")
+        buddy = st.radio("Onboarding buddy", BUDDY_OPTIONS, horizontal=True, key=f"{key}_buddy")
+    return CohortFilter(tuple(departments), tuple(statuses), tuple(tenure), buddy, new_hires)
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `streamlit_app/components/cohort_filters.py` | 91 | 0 |
| `streamlit_app/onboarding_ops.py` | 19 | 2 |
| `tests/test_cohort_filters.py` | 70 | 0 |
| `docs/prs/gaurav/day-18-cohort-filters.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
