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
from streamlit_app.components.kpi_cards import build_kpi_cards, render_kpi_cards  # noqa: E402

st.set_page_config(page_title="VibeCheck · Onboarding Ops", layout="wide")


@st.cache_data(show_spinner="Running the onboarding pipeline...")
def load_features():
    return build_feature_table()


features = load_features()

st.title("Onboarding Ops")
st.caption(f"{len(features):,} hires · cleaned, merged and scored by the VibeCheck data pipeline")
render_kpi_cards(build_kpi_cards(compute_onboarding_kpis(features)))
