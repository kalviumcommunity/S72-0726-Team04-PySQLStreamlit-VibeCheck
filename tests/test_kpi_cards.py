from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from streamlit_app.components.kpi_cards import KPI_SPECS, build_kpi_cards, format_value, tone_for

PAGE = Path(__file__).resolve().parents[1] / "streamlit_app" / "onboarding_ops.py"
SPECS = {spec.key: spec for spec in KPI_SPECS}


@pytest.mark.parametrize("key, value, tone", [
    ("completion_rate_pct", 97.5, "good"),
    ("completion_rate_pct", 95.0, "good"),      # target is inclusive
    ("completion_rate_pct", 90.0, "warn"),
    ("completion_rate_pct", 80.0, "bad"),
    ("avg_days_to_complete", 12.0, "good"),     # lower is better
    ("avg_days_to_complete", 18.0, "warn"),
    ("avg_days_to_complete", 25.0, "bad"),
    ("delayed_count", 0, "good"),
    ("delayed_count", 14, "bad"),
    ("buddy_coverage_pct", None, "neutral"),
])
def test_tone_against_targets(key, value, tone):
    assert tone_for(value, SPECS[key]) == tone


def test_value_formatting():
    assert format_value(97.4829, "%") == "97.5%"
    assert format_value(11.68, " days") == "11.7 days"
    assert format_value(1470, "") == "1,470"
    assert format_value(None, "%") == "—"


def test_cards_show_deltas_for_rates_but_not_counts():
    cohort = {"completion_rate_pct": 90.0, "avg_days_to_complete": 15.0, "delayed_count": 3}
    company = {"completion_rate_pct": 97.5, "avg_days_to_complete": 11.7, "delayed_count": 14}
    cards = {card.label: card for card in build_kpi_cards(cohort, benchmark=company)}
    assert cards["Onboarding completion rate"].delta == "-7.5 pts vs company"
    assert cards["Avg days to complete"].delta == "+3.3 days vs company"
    assert cards["Avg days to complete"].delta_color == "inverse"
    assert cards["Delayed hires"].delta is None
    assert cards["Buddy coverage"].value == "—" and cards["Buddy coverage"].tone == "neutral"


def test_page_renders_all_cards_from_real_data():
    app = AppTest.from_file(str(PAGE), default_timeout=60).run()
    assert not app.exception
    metrics = {m.label: m.value for m in app.metric}
    assert len(metrics) == len(KPI_SPECS)
    assert metrics["Onboarding completion rate"] == "97.5%"
    assert metrics["Delayed hires"] == "14"
    assert any("Off target" in c.value for c in app.caption)
