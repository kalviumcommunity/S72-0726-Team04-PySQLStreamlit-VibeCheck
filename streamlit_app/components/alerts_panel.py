"""Alert feed for the dashboard: severity counters, filters, the alert list and a CSV export.

``alert_counts``, ``filter_alerts`` and ``alerts_banner`` are pure; ``render_alerts_panel``
only lays them out. Alerts are evaluated once with company-wide thresholds
(pipeline.alerts) and then narrowed to the hires in the selected cohort.
"""
from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from pipeline.alerts import SEVERITIES
from streamlit_app.theme import SEVERITY_BADGES

TABLE_COLUMNS = ["severity", "employee_id", "Department", "JobRole", "title", "message", "onboarding_days"]


def alert_counts(alerts: pd.DataFrame) -> dict[str, int]:
    """Hires with at least one alert at each severity."""
    return {s: int(alerts.loc[alerts["severity"] == s, "employee_id"].nunique()) for s in SEVERITIES}


def filter_alerts(alerts: pd.DataFrame, severities: Iterable[str] = (), codes: Iterable[str] = ()) -> pd.DataFrame:
    """Empty selections mean "all", matching the "All ..." placeholders in the UI."""
    severities, codes = list(severities), list(codes)
    mask = pd.Series(True, index=alerts.index)
    if severities:
        mask &= alerts["severity"].isin(severities)
    if codes:
        mask &= alerts["code"].isin(codes)
    return alerts[mask]


def alerts_banner(alerts: pd.DataFrame) -> str | None:
    high = alert_counts(alerts)["high"]
    if not high:
        return None
    return f"{high} hire{'s' if high != 1 else ''} in this cohort need{'s' if high == 1 else ''} attention now (high-severity alerts)."


def render_alerts_panel(alerts: pd.DataFrame, key: str = "alerts") -> None:
    import streamlit as st

    counts = alert_counts(alerts)
    for column, severity in zip(st.columns(len(SEVERITIES)), SEVERITIES):
        column.metric(f"{severity.title()} severity", counts[severity], help="Hires with at least one alert at this level")
        column.caption(SEVERITY_BADGES[severity])
    if alerts.empty:
        st.success("No open onboarding in this cohort needs attention.")
        return

    left, right = st.columns(2)
    severities = left.multiselect("Severity", SEVERITIES, key=f"{key}_severity", placeholder="All severities")
    codes = right.multiselect("Rule", sorted(alerts["code"].unique()), key=f"{key}_codes", placeholder="All rules")
    shown = filter_alerts(alerts, severities, codes)
    st.dataframe(shown[TABLE_COLUMNS].astype({"severity": str}), hide_index=True)
    st.download_button("Download alerts (CSV)", shown.to_csv(index=False).encode("utf-8"),
                       file_name="onboarding_alerts.csv", mime="text/csv", key=f"{key}_download")
