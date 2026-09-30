# Day 21 - Mock UX for dashboard improvements: tabs, shared design tokens, wireframe

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-21-dashboard-ux-mock` |
| **Base** | `main` - stacked on `gaurav/day-20-ci-pipeline-validation` (merge PR 20 first) |
| **Roadmap** | Day 23 (Wed 19 Aug 2026) - *Mock UX design for dashboard improvements.* |
| **Type** | `feat` |
| **Size** | 4 code files, +136 / -17 lines (docs excluded) |

## Summary

Reorganises the page into Overview / Cohort / Root causes / Alerts tabs, adds `streamlit_app/theme.py` design tokens, and documents the layout in `docs/ux/onboarding-ops-wireframe.md`. The Alerts tab is a mock until the next PR.

## Why

- KPI cards, the hire table and the analysis competed for one long scroll; the root-cause findings were never read.

## What changed

- Overview reuses `pipeline.export.build_charts` - charts and exports share one status palette.
- The Root causes tab uses company-wide lifts (a cohort is too small for stable ones) and says so.
- No custom CSS: coloured markdown keeps the page readable in light and dark themes.
- `tests/test_dashboard_layout.py`: 6 tests.

## How to test

```bash
streamlit run streamlit_app/onboarding_ops.py
pytest tests/test_dashboard_layout.py
```

## Result

Four tabs render headlessly: 6 KPI cards + 2 charts, department and hire tables, root-cause findings + lift chart.

## Diff highlight

`streamlit_app/onboarding_ops.py` (excerpt)

```diff
+charts = build_charts(selected, root_causes)
+overview, cohort_tab, causes_tab, alerts_tab = st.tabs(TABS)
+
+with overview:
+    benchmark = compute_onboarding_kpis(features) if cohort.is_active else None
+    render_kpi_cards(build_kpi_cards(compute_onboarding_kpis(selected), benchmark=benchmark))
+    left, right = st.columns(2)
+    left.plotly_chart(charts["completion_time_histogram"])
+    right.plotly_chart(charts["status_by_department"])
+
+with cohort_tab:
+    section("Departments", "KPIs per department for the selected cohort.")
+    st.dataframe(compute_department_kpis(selected), hide_index=True)
+    section("Hires", "Most urgent first: Delayed, then In Progress, longest onboarding at the top.")
+    st.dataframe(selected.sort_values(["onboarding_status", "onboarding_days"], ascending=False)[COHORT_COLUMNS],
+                 hide_index=True)
+
+with causes_tab:
+    section("Why onboardings get delayed",
+            "Computed on all new hires, so cohort filters do not apply. Association, not causation.")
+    st.markdown("\n".join(f"- {finding}" for finding in root_cause_findings(root_causes)))
+    st.plotly_chart(charts["delay_root_causes"])
 
-st.subheader("Hires in this cohort")
-st.dataframe(
-    selected.sort_values(["onboarding_status", "onboarding_days"], ascending=False)[COHORT_COLUMNS],
-    hide_index=True,
-)
+with alerts_tab:
+    open_count = int(selected["onboarding_status"].isin(["In Progress", "Delayed"]).sum())
+    section("Alerts", "Mock-up: the live alert feed replaces this panel in the next iteration.")
+    st.info(f"{open_count} hires in this cohort have an open onboarding and will be monitored here: "
+            "severity counters, a filterable alert list and a CSV export.")
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `docs/ux/onboarding-ops-wireframe.md` | 47 | 0 |
| `streamlit_app/components/kpi_cards.py` | 2 | 8 |
| `streamlit_app/onboarding_ops.py` | 41 | 9 |
| `streamlit_app/theme.py` | 42 | 0 |
| `tests/test_dashboard_layout.py` | 51 | 0 |
| `docs/prs/gaurav/day-21-dashboard-ux-mock.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
