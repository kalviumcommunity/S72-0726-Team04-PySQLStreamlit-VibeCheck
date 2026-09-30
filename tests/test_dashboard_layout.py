from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from pipeline.standardize import STATUS_ORDER
from streamlit_app.components.kpi_cards import KPI_SPECS, build_kpi_cards
from streamlit_app.theme import STATUS_BADGES, STATUS_COLOURS, TABS, TONE_BADGES

PAGE = Path(__file__).resolve().parents[1] / "streamlit_app" / "onboarding_ops.py"


def test_tokens_cover_every_status_and_tone():
    assert list(STATUS_COLOURS) == list(STATUS_BADGES) == list(STATUS_ORDER)
    tones = {card.tone for card in build_kpi_cards({"completion_rate_pct": 99.0, "delayed_count": 5,
                                                    "avg_training_pct": 10.0})}
    assert tones | {"neutral"} <= set(TONE_BADGES)


@pytest.fixture(scope="module")
def app():
    return AppTest.from_file(str(PAGE), default_timeout=90).run()


def test_page_is_organised_in_tabs(app):
    assert not app.exception
    assert [tab.label for tab in app.tabs] == list(TABS)


def test_overview_tab_holds_cards_and_charts(app):
    overview = app.tabs[0]
    assert len(overview.metric) == len(KPI_SPECS)
    assert len(overview.get("plotly_chart")) == 2


def test_cohort_tab_shows_department_and_hire_tables(app):
    cohort = app.tabs[1]
    assert [s.value for s in cohort.subheader] == ["Departments", "Hires"]
    assert len(cohort.dataframe) == 2


def test_root_causes_tab_explains_delays(app):
    causes = app.tabs[2]
    findings = " ".join(m.value for m in causes.markdown)
    assert "No reporting manager assigned: 100% delayed" in findings
    assert len(causes.get("plotly_chart")) == 1


def test_alerts_tab_shows_the_live_feed(app):
    alerts = app.tabs[3]
    assert [m.label for m in alerts.metric] == ["High severity", "Medium severity", "Low severity"]
    assert len(alerts.dataframe) == 1
