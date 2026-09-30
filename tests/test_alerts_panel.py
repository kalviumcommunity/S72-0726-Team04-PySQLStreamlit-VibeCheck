from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from streamlit_app.components.alerts_panel import alert_counts, alerts_banner, filter_alerts

PAGE = Path(__file__).resolve().parents[1] / "streamlit_app" / "onboarding_ops.py"

ALERTS = pd.DataFrame({
    "employee_id": [7, 7, 8, 9],
    "severity": pd.Categorical(["high", "medium", "high", "low"], categories=["high", "medium", "low"], ordered=True),
    "code": ["DELAYED_STATUS", "NO_BUDDY_IN_FLIGHT", "NO_MANAGER", "LOW_TOOL_ACTIVITY"],
})


def test_counts_are_hires_per_severity():
    assert alert_counts(ALERTS) == {"high": 2, "medium": 1, "low": 1}
    assert alert_counts(ALERTS.head(0)) == {"high": 0, "medium": 0, "low": 0}


@pytest.mark.parametrize("severities, codes, expected", [
    ((), (), [7, 7, 8, 9]),                                   # empty selection = everything
    (("high",), (), [7, 8]),
    ((), ("NO_MANAGER", "LOW_TOOL_ACTIVITY"), [8, 9]),
    (("high",), ("LOW_TOOL_ACTIVITY",), []),
])
def test_filters(severities, codes, expected):
    assert filter_alerts(ALERTS, severities, codes)["employee_id"].tolist() == expected


def test_banner_wording():
    assert alerts_banner(ALERTS) == "2 hires in this cohort need attention now (high-severity alerts)."
    assert alerts_banner(ALERTS.iloc[[0]]) == "1 hire in this cohort needs attention now (high-severity alerts)."
    assert alerts_banner(ALERTS.iloc[[3]]) is None


@pytest.fixture
def app():
    return AppTest.from_file(str(PAGE), default_timeout=90).run()


def test_banner_and_feed_on_real_data(app):
    assert not app.exception
    assert app.warning[0].value.startswith("33 hires in this cohort need attention now")
    feed = app.tabs[3]
    assert {m.label: m.value for m in feed.metric}["High severity"] == "33"
    all_rows = len(feed.dataframe[0].value)
    feed.multiselect(key="alerts_severity").set_value(["high"]).run()
    assert 0 < len(app.tabs[3].dataframe[0].value) < all_rows


def test_calm_cohort_has_no_banner(app):
    app.multiselect(key="cohort_statuses").set_value(["Completed"]).run()
    assert not app.exception and len(app.warning) == 0
    assert "No open onboarding" in app.tabs[3].success[0].value
