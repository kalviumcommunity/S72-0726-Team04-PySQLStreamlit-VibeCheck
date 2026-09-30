"""KPI cards for the onboarding dashboard.

Building a card (formatted value, tone against target, delta vs a benchmark) is
plain Python and unit-tested; ``render_kpi_cards`` is a thin Streamlit layer.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class KpiSpec:
    key: str               # key in pipeline.kpis.compute_onboarding_kpis()
    label: str
    unit: str              # "%", " days" or "" for counts
    higher_is_better: bool
    target: float          # on target at or beyond this value
    floor: float           # off target beyond this value, on the wrong side
    help: str


# Programme targets live here, not in the page, so they are reviewed like code.
KPI_SPECS: tuple[KpiSpec, ...] = (
    KpiSpec("completion_rate_pct", "Onboarding completion rate", "%", True, 95.0, 85.0,
            "Share of hires whose onboarding status is Completed."),
    KpiSpec("avg_days_to_complete", "Avg days to complete", " days", False, 14.0, 21.0,
            "Mean onboarding days for completed hires. Target: two working weeks."),
    KpiSpec("delayed_count", "Delayed hires", "", False, 0, 10,
            "Hires whose onboarding is flagged Delayed - the intervention list."),
    KpiSpec("avg_training_pct", "Avg training completion", "%", True, 90.0, 75.0,
            "Mean share of mandatory training modules completed."),
    KpiSpec("buddy_coverage_pct", "Buddy coverage", "%", True, 98.0, 90.0,
            "Hires with an onboarding buddy assigned."),
    KpiSpec("first_week_checkin_pct", "First-week check-ins", "%", True, 98.0, 90.0,
            "Hires who had a manager check-in during week one."),
)


@dataclass(frozen=True)
class KpiCard:
    label: str
    value: str
    tone: str                   # good | warn | bad | neutral
    help: str
    delta: str | None = None
    delta_color: str = "normal"  # st.metric: "inverse" when a rise is bad news


TONE_BADGES = {
    "good": ":green[● On target]",
    "warn": ":orange[● Watch]",
    "bad": ":red[● Off target]",
    "neutral": ":gray[● No data]",
}


def tone_for(value: float | None, spec: KpiSpec) -> str:
    if value is None:
        return "neutral"
    if spec.higher_is_better:
        return "good" if value >= spec.target else "bad" if value < spec.floor else "warn"
    return "good" if value <= spec.target else "bad" if value > spec.floor else "warn"


def format_value(value: float | None, unit: str) -> str:
    if value is None:
        return "—"
    if unit == "%":
        return f"{value:.1f}%"
    if unit == " days":
        return f"{value:.1f} days"
    return f"{value:,.0f}"


def build_kpi_cards(kpis: Mapping[str, float | None], benchmark: Mapping[str, float | None] | None = None,
                    specs: Sequence[KpiSpec] = KPI_SPECS) -> list[KpiCard]:
    """One card per spec. With a benchmark (e.g. company-wide KPIs), rates show a delta."""
    cards = []
    for spec in specs:
        value = kpis.get(spec.key)
        reference = (benchmark or {}).get(spec.key)
        delta = None
        if spec.unit and value is not None and reference is not None:  # counts are not comparable across cohorts
            unit = " pts" if spec.unit == "%" else spec.unit
            delta = f"{value - reference:+.1f}{unit} vs company"
        cards.append(KpiCard(spec.label, format_value(value, spec.unit), tone_for(value, spec), spec.help,
                             delta, "normal" if spec.higher_is_better else "inverse"))
    return cards


def render_kpi_cards(cards: Sequence[KpiCard], per_row: int = 3) -> None:
    import streamlit as st

    for start in range(0, len(cards), per_row):
        for column, card in zip(st.columns(per_row), cards[start:start + per_row]):
            with column.container(border=True):
                st.metric(card.label, card.value, card.delta, delta_color=card.delta_color, help=card.help)
                st.caption(TONE_BADGES[card.tone])
