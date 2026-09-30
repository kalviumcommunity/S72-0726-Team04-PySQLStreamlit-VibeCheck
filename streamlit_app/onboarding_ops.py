"""VibeCheck - Onboarding Ops: a Streamlit view over the onboarding data pipeline.

    streamlit run streamlit_app/onboarding_ops.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # `streamlit run` only puts this folder on sys.path
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from pipeline.features import build_feature_table  # noqa: E402
from pipeline.kpis import compute_onboarding_kpis  # noqa: E402
from streamlit_app.components.cohort_filters import apply_cohort_filter, render_cohort_sidebar  # noqa: E402
from streamlit_app.components.kpi_cards import build_kpi_cards, render_kpi_cards  # noqa: E402

COHORT_COLUMNS = ["employee_id", "Department", "JobRole", "onboarding_status", "onboarding_days",
                  "training_completion_percent", "onboarding_speed", "buddy_assigned"]

st.set_page_config(page_title="VibeCheck · Onboarding Ops", layout="wide")


@st.cache_data(show_spinner="Running the onboarding pipeline...")
def load_features():
    return build_feature_table()


features = load_features()
cohort = render_cohort_sidebar(features)
selected = apply_cohort_filter(features, cohort)

st.title("Onboarding Ops")
st.caption(f"Showing {len(selected):,} of {len(features):,} hires · {cohort.describe()}")
if selected.empty:
    st.info("No hires match this cohort. Widen the filters in the sidebar.")
    st.stop()

benchmark = compute_onboarding_kpis(features) if cohort.is_active else None
render_kpi_cards(build_kpi_cards(compute_onboarding_kpis(selected), benchmark=benchmark))

st.subheader("Hires in this cohort")
st.dataframe(
    selected.sort_values(["onboarding_status", "onboarding_days"], ascending=False)[COHORT_COLUMNS],
    hide_index=True,
)
