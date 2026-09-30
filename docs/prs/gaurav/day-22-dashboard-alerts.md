# Day 22 - Integrate alerts into the dashboard

| | |
| :--- | :--- |
| **Author** | Gaurav (`Gaurav-205`) |
| **Branch** | `gaurav/day-22-dashboard-alerts` |
| **Base** | `main` - stacked on `gaurav/day-21-dashboard-ux-mock` (merge PR 21 first) |
| **Roadmap** | Day 24 (Thu 20 Aug 2026) - *Integrate alerts into dashboard.* |
| **Type** | `feat` |
| **Size** | 6 code files, +141 / -8 lines (docs excluded) |

## Summary

Replaces the mock Alerts tab with the live feed: severity counters, severity / rule filters, the alert list, a CSV download, and a page-level warning banner when the cohort has high-severity alerts.

## Why

- The team should see who needs help *today* without leaving the dashboard.

## What changed

- `alert_counts()`, `filter_alerts()` (empty selection = all), `alerts_banner()` with correct pluralisation.
- Alerts are evaluated once with company thresholds, then narrowed to the cohort.
- `tests/test_alerts_panel.py`: 8 tests; layout and card tests updated for the new tab.

## How to test

```bash
streamlit run streamlit_app/onboarding_ops.py
pytest tests/test_alerts_panel.py
```

## Result

Banner: *33 hires in this cohort need attention now*. Counters show 33 high, 31 medium, 31 low. A completed-only cohort shows no banner.

## Diff highlight

`streamlit_app/components/alerts_panel.py` (excerpt)

```diff
+def alert_counts(alerts: pd.DataFrame) -> dict[str, int]:
+    """Hires with at least one alert at each severity."""
+    return {s: int(alerts.loc[alerts["severity"] == s, "employee_id"].nunique()) for s in SEVERITIES}
+
+
+def filter_alerts(alerts: pd.DataFrame, severities: Iterable[str] = (), codes: Iterable[str] = ()) -> pd.DataFrame:
+    """Empty selections mean "all", matching the "All ..." placeholders in the UI."""
+    severities, codes = list(severities), list(codes)
+    mask = pd.Series(True, index=alerts.index)
+    if severities:
+        mask &= alerts["severity"].isin(severities)
+    if codes:
+        mask &= alerts["code"].isin(codes)
+    return alerts[mask]
+
+
+def alerts_banner(alerts: pd.DataFrame) -> str | None:
+    high = alert_counts(alerts)["high"]
+    if not high:
+        return None
+    return f"{high} hire{'s' if high != 1 else ''} in this cohort need{'s' if high == 1 else ''} attention now (high-severity alerts)."
+
+
+def render_alerts_panel(alerts: pd.DataFrame, key: str = "alerts") -> None:
+    import streamlit as st
+
+    counts = alert_counts(alerts)
+    for column, severity in zip(st.columns(len(SEVERITIES)), SEVERITIES):
+        column.metric(f"{severity.title()} severity", counts[severity], help="Hires with at least one alert at this level")
+        column.caption(SEVERITY_BADGES[severity])
+    if alerts.empty:
+        st.success("No open onboarding in this cohort needs attention.")
+        return
```

## Files changed

| File | + | - |
| :--- | ---: | ---: |
| `streamlit_app/components/alerts_panel.py` | 59 | 0 |
| `streamlit_app/onboarding_ops.py` | 13 | 4 |
| `streamlit_app/theme.py` | 8 | 1 |
| `tests/test_alerts_panel.py` | 57 | 0 |
| `tests/test_dashboard_layout.py` | 3 | 2 |
| `tests/test_kpi_cards.py` | 1 | 1 |
| `docs/prs/gaurav/day-22-dashboard-alerts.md` | this file | |

## Checklist

- [x] Adds at least 10 lines of functional code, with tests
- [x] `pytest` passes locally on this branch
- [x] No secrets, credentials or `.env` files in the diff
- [x] PR doc added and `docs/prs/gaurav/README.md` updated
