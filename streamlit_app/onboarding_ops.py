"""VibeCheck - Onboarding Ops: a Streamlit view over the onboarding data pipeline.

    streamlit run streamlit_app/onboarding_ops.py

Layout (see docs/ux/onboarding-ops-wireframe.md): cohort filters in the sidebar,
then four tabs - Overview, Cohort, Root causes, Alerts.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # `streamlit run` only puts this folder on sys.path
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from pipeline.analysis.root_cause import rank_root_causes, root_cause_findings  # noqa: E402
from pipeline.export import build_charts  # noqa: E402
from pipeline.features import build_feature_table  # noqa: E402
from pipeline.kpis import compute_department_kpis, compute_onboarding_kpis  # noqa: E402
from streamlit_app.components.cohort_filters import apply_cohort_filter, render_cohort_sidebar  # noqa: E402
from streamlit_app.components.kpi_cards import build_kpi_cards, render_kpi_cards  # noqa: E402
from streamlit_app.theme import TABS, configure_page, section  # noqa: E402

COHORT_COLUMNS = ["employee_id", "Department", "JobRole", "onboarding_status", "onboarding_days",
                  "training_completion_percent", "onboarding_speed", "buddy_assigned"]

configure_page()


@st.cache_data(show_spinner="Running the onboarding pipeline...")
def load_features():
    return build_feature_table()


@st.cache_data
def load_root_causes(features):
    return rank_root_causes(features)


features = load_features()
root_causes = load_root_causes(features)  # company-wide: cohorts are too small for stable lifts
cohort = render_cohort_sidebar(features)
selected = apply_cohort_filter(features, cohort)

st.title("Onboarding Ops")
st.caption(f"Showing {len(selected):,} of {len(features):,} hires · {cohort.describe()}")
if selected.empty:
    st.info("No hires match this cohort. Widen the filters in the sidebar.")
    st.stop()

charts = build_charts(selected, root_causes)
overview, cohort_tab, causes_tab, alerts_tab = st.tabs(TABS)

with overview:
    benchmark = compute_onboarding_kpis(features) if cohort.is_active else None
    render_kpi_cards(build_kpi_cards(compute_onboarding_kpis(selected), benchmark=benchmark))
    left, right = st.columns(2)
    left.plotly_chart(charts["completion_time_histogram"])
    right.plotly_chart(charts["status_by_department"])

with cohort_tab:
    section("Departments", "KPIs per department for the selected cohort.")
    st.dataframe(compute_department_kpis(selected), hide_index=True)
    section("Hires", "Most urgent first: Delayed, then In Progress, longest onboarding at the top.")
    st.dataframe(selected.sort_values(["onboarding_status", "onboarding_days"], ascending=False)[COHORT_COLUMNS],
                 hide_index=True)

with causes_tab:
    section("Why onboardings get delayed",
            "Computed on all new hires, so cohort filters do not apply. Association, not causation.")
    st.markdown("\n".join(f"- {finding}" for finding in root_cause_findings(root_causes)))
    st.plotly_chart(charts["delay_root_causes"])

with alerts_tab:
    open_count = int(selected["onboarding_status"].isin(["In Progress", "Delayed"]).sum())
    section("Alerts", "Mock-up: the live alert feed replaces this panel in the next iteration.")
    st.info(f"{open_count} hires in this cohort have an open onboarding and will be monitored here: "
            "severity counters, a filterable alert list and a CSV export.")
