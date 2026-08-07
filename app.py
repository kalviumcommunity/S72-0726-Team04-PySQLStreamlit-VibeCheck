import sqlite3
import math
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# Page Configuration & Mastercard Design System
# ---------------------------------------------------------
st.set_page_config(
    page_title="VibeCheck | Operational Analytics Platform",
    page_icon="V",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS - Mastercard Editorial Magazine Design Language
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sofia+Sans:wght@400;450;500;600;700&display=swap');

    /* Master Canvas & Palette Variables */
    :root {
        --mc-canvas: #F3F0EE;
        --mc-lifted: #FCFBFA;
        --mc-ink: #141413;
        --mc-signal-orange: #CF4500;
        --mc-light-orange: #F37338;
        --mc-clay-brown: #9A3A0A;
        --mc-slate: #696969;
        --mc-link-blue: #3860BE;
        --mc-watermark: #E8E2DA;
    }

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Sofia Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: var(--mc-canvas) !important;
        color: var(--mc-ink) !important;
    }

    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Sidebar - Warm Lifted Surface */
    [data-testid="stSidebar"] {
        background-color: var(--mc-lifted) !important;
        border-right: 1px solid rgba(20, 20, 19, 0.08) !important;
        padding-top: 1.5rem;
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label {
        color: var(--mc-ink) !important;
        font-weight: 600 !important;
    }

    /* Streamlit Selectbox & Input Custom Styling */
    div[data-baseweb="select"] > div {
        border-radius: 16px !important;
        border: 1.5px solid rgba(20, 20, 19, 0.12) !important;
        background-color: #FFFFFF !important;
        color: var(--mc-ink) !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="select"] > div:hover {
        border-color: var(--mc-light-orange) !important;
    }

    /* Streamlit Slider Accent Color */
    div[data-baseweb="slider"] [role="slider"] {
        background-color: var(--mc-signal-orange) !important;
        border-color: var(--mc-signal-orange) !important;
    }

    div[aria-valuenow] {
        color: var(--mc-signal-orange) !important;
    }

    /* Streamlit Alert Banners */
    div[data-testid="stAlert"] {
        border-radius: 16px !important;
        border: 1px solid rgba(20, 20, 19, 0.1) !important;
        background-color: #FFFFFF !important;
        box-shadow: 0px 4px 16px rgba(0,0,0,0.02) !important;
    }

    /* Mastercard Floating Nav Bar */
    .mc-nav-floating {
        background: #FFFFFF;
        border-radius: 999px;
        padding: 14px 36px;
        margin-bottom: 28px;
        box-shadow: 0px 4px 24px rgba(0, 0, 0, 0.04);
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid rgba(20, 20, 19, 0.06);
    }

    .mc-brand-text {
        font-size: 1.45rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--mc-ink);
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .mc-brand-badge {
        font-size: 0.68rem;
        font-weight: 700;
        background: var(--mc-ink);
        color: var(--mc-canvas);
        padding: 3px 8px;
        border-radius: 999px;
        letter-spacing: 0.08em;
    }

    .mc-status-chip {
        background-color: var(--mc-canvas);
        color: var(--mc-ink);
        border-radius: 999px;
        padding: 6px 18px;
        font-size: 0.82rem;
        font-weight: 500;
        border: 1px solid rgba(20, 20, 19, 0.1);
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Mastercard Hero Stadium Frame (40px Radius) */
    .mc-hero-stadium {
        background-color: var(--mc-lifted);
        border-radius: 40px;
        padding: 52px 60px;
        margin-bottom: 36px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(20, 20, 19, 0.06);
        box-shadow: 0px 24px 48px rgba(0, 0, 0, 0.04);
    }

    .mc-ghost-watermark {
        position: absolute;
        right: -20px;
        bottom: -30px;
        font-size: 8.5rem;
        font-weight: 700;
        color: var(--mc-watermark);
        letter-spacing: -0.04em;
        user-select: none;
        pointer-events: none;
        opacity: 0.65;
        white-space: nowrap;
    }

    .mc-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--mc-slate);
        margin-bottom: 12px;
    }

    .mc-eyebrow-dot {
        width: 7px;
        height: 7px;
        background-color: var(--mc-signal-orange);
        border-radius: 50%;
    }

    .mc-hero-title {
        font-size: 3.2rem;
        font-weight: 500;
        line-height: 1.05;
        letter-spacing: -0.03em;
        color: var(--mc-ink);
        margin-bottom: 16px;
        max-width: 820px;
    }

    .mc-hero-body {
        font-size: 1.1rem;
        font-weight: 450;
        line-height: 1.45;
        color: var(--mc-ink);
        max-width: 680px;
        margin-bottom: 28px;
    }

    /* Mastercard Metric Cards (20px Radius) */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(20, 20, 19, 0.08) !important;
        border-radius: 20px !important;
        padding: 20px 24px !important;
        box-shadow: 0px 4px 16px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.25s ease !important;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        border-color: var(--mc-light-orange) !important;
        box-shadow: 0px 12px 28px rgba(243, 115, 56, 0.12) !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.03em !important;
        color: var(--mc-ink) !important;
        background: none !important;
        -webkit-text-fill-color: initial !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        color: var(--mc-slate) !important;
    }

    /* Mastercard Circular Portrait Cards & Constellation Orbits */
    .mc-constellation-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        gap: 24px;
        padding: 28px 0;
        position: relative;
        margin-bottom: 32px;
    }

    .mc-orbit-line {
        position: absolute;
        top: 98px;
        left: 10%;
        width: 80%;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, var(--mc-light-orange) 30%, var(--mc-signal-orange) 50%, var(--mc-light-orange) 70%, transparent 100%);
        z-index: 0;
        opacity: 0.45;
    }

    .mc-portrait-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        position: relative;
        z-index: 1;
    }

    .mc-circle-frame {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background-color: var(--mc-lifted);
        border: 2px solid #FFFFFF;
        box-shadow: 0px 16px 36px rgba(0,0,0,0.06);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        transition: transform 0.25s ease;
    }

    .mc-circle-frame:hover {
        transform: scale(1.05);
    }

    .mc-circle-svg-icon {
        width: 44px;
        height: 44px;
        stroke: var(--mc-ink);
        fill: none;
        stroke-width: 1.8;
        stroke-linecap: round;
        stroke-linejoin: round;
    }

    .mc-satellite-cta {
        position: absolute;
        bottom: 2px;
        right: 2px;
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #FFFFFF;
        border: 1px solid rgba(20, 20, 19, 0.12);
        box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--mc-ink);
    }

    .mc-satellite-svg {
        width: 16px;
        height: 16px;
        stroke: var(--mc-ink);
        fill: none;
        stroke-width: 2.2;
    }

    .mc-portrait-title {
        margin-top: 14px;
        font-size: 1.1rem;
        font-weight: 500;
        letter-spacing: -0.02em;
        color: var(--mc-ink);
    }

    .mc-portrait-sub {
        font-size: 0.85rem;
        color: var(--mc-slate);
        font-weight: 450;
    }

    /* Mastercard Buttons (20px & Pill Radius) */
    .stButton > button {
        background-color: var(--mc-ink) !important;
        color: var(--mc-canvas) !important;
        border-radius: 20px !important;
        padding: 8px 28px !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        letter-spacing: -0.02em !important;
        border: 1.5px solid var(--mc-ink) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background-color: var(--mc-signal-orange) !important;
        border-color: var(--mc-signal-orange) !important;
        color: #FFFFFF !important;
        transform: translateY(-1px) !important;
    }

    /* Streamlit Tabs - Mastercard Pill Style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        padding: 4px 0;
        margin-bottom: 24px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF !important;
        border-radius: 999px !important;
        padding: 10px 24px !important;
        color: var(--mc-slate) !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        letter-spacing: -0.02em !important;
        border: 1px solid rgba(20, 20, 19, 0.08) !important;
        transition: all 0.2s ease !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--mc-ink) !important;
        color: var(--mc-canvas) !important;
        border-color: var(--mc-ink) !important;
        box-shadow: 0px 4px 14px rgba(20, 20, 19, 0.15) !important;
    }

    /* Input & Text Area Styling */
    textarea, input {
        border-radius: 16px !important;
        border: 1.5px solid rgba(20, 20, 19, 0.15) !important;
        background-color: #FFFFFF !important;
        color: var(--mc-ink) !important;
        font-family: monospace !important;
    }

    /* Dataframe Container */
    div[data-testid="stDataFrame"] {
        border-radius: 20px !important;
        overflow: hidden !important;
        border: 1px solid rgba(20, 20, 19, 0.08) !important;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.03) !important;
        background-color: #FFFFFF !important;
    }

    /* Mastercard Footer (Ink Black #141413) */
    .mc-footer {
        background-color: var(--mc-ink);
        color: #FFFFFF;
        border-radius: 40px;
        padding: 56px 64px 40px 64px;
        margin-top: 64px;
        margin-bottom: 24px;
    }

    .mc-footer-headline {
        font-size: 2.2rem;
        font-weight: 500;
        letter-spacing: -0.03em;
        margin-bottom: 40px;
        color: #FFFFFF;
        max-width: 600px;
    }

    .mc-footer-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 32px;
        padding-bottom: 40px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    }

    .mc-footer-col-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: rgba(255, 255, 255, 0.5);
        margin-bottom: 16px;
    }

    .mc-footer-link {
        font-size: 0.92rem;
        font-weight: 450;
        color: rgba(255, 255, 255, 0.85);
        margin-bottom: 10px;
        cursor: pointer;
        display: block;
        text-decoration: none;
    }

    .mc-footer-bottom {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 24px;
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Loading & In-Memory SQLite Setup
# ---------------------------------------------------------
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

@st.cache_data
def load_datasets():
    emp_df = pd.read_csv(DATA_DIR / "employees.csv")
    onb_df = pd.read_csv(DATA_DIR / "onboarding.csv")
    tck_df = pd.read_csv(DATA_DIR / "support_tickets.csv")
    tool_df = pd.read_csv(DATA_DIR / "tool_usage.csv")
    return emp_df, onb_df, tck_df, tool_df

@st.cache_resource
def init_sqlite_db(emp_df, onb_df, tck_df, tool_df):
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    emp_df.to_sql("employees", conn, if_exists="replace", index=False)
    onb_df.to_sql("onboarding", conn, if_exists="replace", index=False)
    tck_df.to_sql("support_tickets", conn, if_exists="replace", index=False)
    tool_df.to_sql("tool_usage", conn, if_exists="replace", index=False)
    return conn

try:
    emp_df, onb_df, tck_df, tool_df = load_datasets()
    db_conn = init_sqlite_db(emp_df, onb_df, tck_df, tool_df)
except Exception as e:
    st.error(f"Error loading datasets: {e}")
    st.stop()

# ---------------------------------------------------------
# Sidebar & Clean Branding
# ---------------------------------------------------------
st.sidebar.markdown("""
<div style="margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid rgba(20, 20, 19, 0.08);">
    <div style="font-size: 1.5rem; font-weight: 700; letter-spacing: -0.04em; color: #141413; display: flex; align-items: center; gap: 8px;">
        VIBECHECK
        <span style="font-size: 0.65rem; font-weight: 700; background: #141413; color: #F3F0EE; padding: 2px 7px; border-radius: 999px; letter-spacing: 0.08em;">PRO</span>
    </div>
    <div style="font-size: 0.8rem; color: #696969; font-weight: 450; margin-top: 4px;">Operational Intelligence Engine</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="mc-eyebrow"><span class="mc-eyebrow-dot"></span>FILTERS</div>', unsafe_allow_html=True)

departments = ["All"] + list(emp_df["Department"].unique())
selected_dept = st.sidebar.selectbox("Filter Department", departments)

min_years = int(emp_df["YearsAtCompany"].min())
max_years = int(emp_df["YearsAtCompany"].max())
selected_tenure = st.sidebar.slider("Tenure (Years at Company)", min_years, max_years, (0, max_years))

onb_statuses = ["All"] + list(onb_df["onboarding_status"].unique())
selected_status = st.sidebar.selectbox("Onboarding Status", onb_statuses)

# Filter dataset based on sidebar choices
filtered_emp = emp_df.copy()
if selected_dept != "All":
    filtered_emp = filtered_emp[filtered_emp["Department"] == selected_dept]

filtered_emp = filtered_emp[
    (filtered_emp["YearsAtCompany"] >= selected_tenure[0]) &
    (filtered_emp["YearsAtCompany"] <= selected_tenure[1])
]

filtered_ids = set(filtered_emp["employee_id"])

filtered_onb = onb_df[onb_df["employee_id"].isin(filtered_ids)]
if selected_status != "All":
    filtered_onb = filtered_onb[filtered_onb["onboarding_status"] == selected_status]
    filtered_ids = set(filtered_onb["employee_id"])
    filtered_emp = filtered_emp[filtered_emp["employee_id"].isin(filtered_ids)]

filtered_tck = tck_df[tck_df["employee_id"].isin(filtered_ids)]
filtered_tool = tool_df[tool_df["employee_id"].isin(filtered_ids)]

# ---------------------------------------------------------
# Mastercard Clean Floating Header Bar
# ---------------------------------------------------------
st.markdown("""
<div class="mc-nav-floating">
    <div class="mc-brand-text">
        VIBECHECK
        <span class="mc-brand-badge">2026</span>
    </div>
    <div style="display: flex; gap: 12px; align-items: center;">
        <span class="mc-status-chip">
            <span class="mc-eyebrow-dot" style="margin: 0;"></span>
            OPERATIONAL INTEGRITY
        </span>
        <span class="mc-status-chip">PYSQL READY</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Mastercard Hero Stadium Container
# ---------------------------------------------------------
st.markdown("""
<div class="mc-hero-stadium">
    <div class="mc-ghost-watermark">VIBECHECK</div>
    <div class="mc-eyebrow"><span class="mc-eyebrow-dot"></span>OPERATIONAL INTELLIGENCE PLATFORM</div>
    <div class="mc-hero-title">Operational friction, solved with human-centered data.</div>
    <div class="mc-hero-body">
        Unifying employee onboarding benchmarks, IT support request histories, and software tool adoption metrics into a single editorial analytics experience.
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Mastercard Circular Department Constellation (SVG Vector Orbits)
# ---------------------------------------------------------
st.markdown('<div class="mc-eyebrow" style="margin-top: 10px;"><span class="mc-eyebrow-dot"></span>DEPARTMENT ORBITS</div>', unsafe_allow_html=True)

dept_counts = filtered_emp["Department"].value_counts().to_dict()

# SVG Icon Strings
rd_icon = '<svg class="mc-circle-svg-icon" viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>'
sales_icon = '<svg class="mc-circle-svg-icon" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>'
hr_icon = '<svg class="mc-circle-svg-icon" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>'
arrow_svg = '<svg class="mc-satellite-svg" viewBox="0 0 24 24"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>'

st.markdown(f"""
<div class="mc-constellation-container">
    <div class="mc-orbit-line"></div>
    <div class="mc-portrait-card">
        <div class="mc-circle-frame">
            {rd_icon}
            <div class="mc-satellite-cta">{arrow_svg}</div>
        </div>
        <div class="mc-portrait-title">Research & Dev</div>
        <div class="mc-portrait-sub">{dept_counts.get('Research & Development', 0):,} Hires</div>
    </div>
    <div class="mc-portrait-card">
        <div class="mc-circle-frame">
            {sales_icon}
            <div class="mc-satellite-cta">{arrow_svg}</div>
        </div>
        <div class="mc-portrait-title">Sales Operations</div>
        <div class="mc-portrait-sub">{dept_counts.get('Sales', 0):,} Hires</div>
    </div>
    <div class="mc-portrait-card">
        <div class="mc-circle-frame">
            {hr_icon}
            <div class="mc-satellite-cta">{arrow_svg}</div>
        </div>
        <div class="mc-portrait-title">Human Resources</div>
        <div class="mc-portrait-sub">{dept_counts.get('Human Resources', 0):,} Hires</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Dashboard Navigation Tabs (Clean No Emojis)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Overview",
    "Onboarding Friction",
    "IT Support Bottlenecks",
    "Tool Adoption & Activity",
    "PySQL Sandbox"
])

# Shared Mastercard Plotly Styling Function
def apply_mc_chart_style(fig):
    fig.update_layout(
        title=None,
        legend_title_text="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Sofia Sans, sans-serif", color="#141413", size=13),
        margin=dict(t=15, b=25, l=25, r=25),
        xaxis=dict(gridcolor="#F3F0EE", zerolinecolor="#F3F0EE"),
        yaxis=dict(gridcolor="#F3F0EE", zerolinecolor="#F3F0EE")
    )
    return fig

# =========================================================
# TAB 1: EXECUTIVE OVERVIEW
# =========================================================
with tab1:
    st.markdown('<div class="mc-eyebrow"><span class="mc-eyebrow-dot"></span>KEY PERFORMANCE INDICATORS</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_emp = len(filtered_emp)
    completed_onb = (filtered_onb["onboarding_status"] == "Completed").sum()
    onb_completion_rate = (completed_onb / max(total_emp, 1)) * 100
    
    avg_resolution = filtered_tck["resolution_hours"].dropna().mean()
    avg_resolution_str = f"{avg_resolution:.1f} hrs" if not math.isnan(avg_resolution) else "N/A"
    
    avg_training = filtered_onb["training_completion_percent"].mean()
    
    ticket_counts = filtered_tck.groupby("employee_id").size().to_dict()
    high_friction_count = 0
    for _, r in filtered_onb.iterrows():
        eid = r["employee_id"]
        tc = ticket_counts.get(eid, 0)
        if r["onboarding_status"] == "Delayed" or r["training_completion_percent"] < 60.0 or tc >= 3:
            high_friction_count += 1
            
    col1.metric("Total Workforce", f"{total_emp:,}")
    col2.metric("Onboarding Completion", f"{onb_completion_rate:.1f}%")
    col3.metric("Avg Training Benchmark", f"{avg_training:.1f}%")
    col4.metric("Avg Resolution Time", avg_resolution_str)
    col5.metric("High-Friction Hires", f"{high_friction_count:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1])
    
    with col_left:
        st.markdown('<div class="mc-eyebrow"><span class="mc-eyebrow-dot"></span>ONBOARDING STATUS BY DEPARTMENT</div>', unsafe_allow_html=True)
        dept_onb = filtered_emp.merge(filtered_onb, on="employee_id")
        dept_status_summary = dept_onb.groupby(["Department", "onboarding_status"]).size().reset_index(name="Count")
        
        fig_status = px.bar(
            dept_status_summary,
            x="Department",
            y="Count",
            color="onboarding_status",
            barmode="group",
            color_discrete_map={"Completed": "#141413", "In Progress": "#F37338", "Delayed": "#CF4500"}
        )
        apply_mc_chart_style(fig_status)
        st.plotly_chart(fig_status, use_container_width=True)

    with col_right:
        st.markdown('<div class="mc-eyebrow"><span class="mc-eyebrow-dot"></span>SUPPORT TICKET PRIORITY BREAKDOWN</div>', unsafe_allow_html=True)
        if not filtered_tck.empty:
            prio_summary = filtered_tck["priority"].value_counts().reset_index()
            prio_summary.columns = ["Priority", "Count"]
            fig_prio = px.pie(
                prio_summary,
                names="Priority",
                values="Count",
                color="Priority",
                color_discrete_map={"Low": "#3860BE", "Medium": "#F37338", "High": "#9A3A0A", "Critical": "#CF4500"},
                hole=0.55
            )
            apply_mc_chart_style(fig_prio)
            st.plotly_chart(fig_prio, use_container_width=True)
        else:
            st.info("No tickets match current filters.")

# =========================================================
# TAB 2: ONBOARDING FRICTION ANALYTICS
# =========================================================
with tab2:
    st.markdown('<div class="mc-eyebrow"><span class="mc-eyebrow-dot"></span>FRICTION MATRIX & TRAINING CORRELATION</div>', unsafe_allow_html=True)
    st.write("Evaluating how module completion rates directly influence IT support dependencies.")

    merged_onb = filtered_emp.merge(filtered_onb, on="employee_id")
    ticket_summary = filtered_tck.groupby("employee_id").size().reset_index(name="ticket_count")
    merged_full = merged_onb.merge(ticket_summary, on="employee_id", how="left")
    merged_full["ticket_count"] = merged_full["ticket_count"].fillna(0)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Training Completion % vs Support Tickets")
        fig_scatter = px.scatter(
            merged_full,
            x="training_completion_percent",
            y="ticket_count",
            color="onboarding_status",
            size="onboarding_days",
            hover_data=["employee_id", "Department", "JobRole"],
            color_discrete_map={"Completed": "#141413", "In Progress": "#F37338", "Delayed": "#CF4500"},
            labels={"training_completion_percent": "Training Completion (%)", "ticket_count": "Support Ticket Count"}
        )
        apply_mc_chart_style(fig_scatter)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_b:
        st.markdown("#### Average Onboarding Days by Department")
        avg_days = merged_full.groupby(["Department", "onboarding_status"])["onboarding_days"].mean().reset_index()
        fig_box = px.bar(
            avg_days,
            x="Department",
            y="onboarding_days",
            color="onboarding_status",
            barmode="group",
            labels={"onboarding_days": "Avg Onboarding Days"},
            color_discrete_map={"Completed": "#141413", "In Progress": "#F37338", "Delayed": "#CF4500"}
        )
        apply_mc_chart_style(fig_box)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown('<div class="mc-eyebrow" style="margin-top: 20px;"><span class="mc-eyebrow-dot"></span>HIGH-FRICTION WORKFORCE DIRECTORY</div>', unsafe_allow_html=True)
    high_friction_df = merged_full[
        (merged_full["onboarding_status"] == "Delayed") | 
        (merged_full["training_completion_percent"] < 60.0) |
        (merged_full["ticket_count"] >= 3)
    ][["employee_id", "Department", "JobRole", "YearsAtCompany", "training_completion_percent", "onboarding_days", "onboarding_status", "ticket_count"]]
    
    st.dataframe(high_friction_df, use_container_width=True)

# =========================================================
# TAB 3: IT SUPPORT BOTTLENECKS
# =========================================================
with tab3:
    st.markdown('<div class="mc-eyebrow"><span class="mc-eyebrow-dot"></span>DEVOPS & IT BOTTLENECK ANALYSIS</div>', unsafe_allow_html=True)

    if not filtered_tck.empty:
        col_c, col_d = st.columns(2)

        with col_c:
            st.markdown("#### Resolution Time (Hours) by Ticket Priority")
            avg_res_prio = filtered_tck.groupby("priority")["resolution_hours"].mean().reset_index()
            fig_res = px.bar(
                avg_res_prio,
                x="priority",
                y="resolution_hours",
                color="priority",
                color_discrete_map={"Low": "#3860BE", "Medium": "#F37338", "High": "#9A3A0A", "Critical": "#CF4500"},
                labels={"resolution_hours": "Avg Resolution (Hours)"}
            )
            apply_mc_chart_style(fig_res)
            st.plotly_chart(fig_res, use_container_width=True)

        with col_d:
            st.markdown("#### Ticket Volume by Assigned Team & Issue Type")
            team_issue = filtered_tck.groupby(["assigned_team", "issue_type"]).size().reset_index(name="count")
            fig_team = px.bar(
                team_issue,
                x="assigned_team",
                y="count",
                color="issue_type",
                barmode="stack",
                color_discrete_sequence=["#141413", "#F37338", "#CF4500", "#3860BE", "#9A3A0A"]
            )
            apply_mc_chart_style(fig_team)
            st.plotly_chart(fig_team, use_container_width=True)
    else:
        st.info("No ticket data matching current filter selection.")

# =========================================================
# TAB 4: TOOL ADOPTION & ACTIVITY
# =========================================================
with tab4:
    st.markdown('<div class="mc-eyebrow"><span class="mc-eyebrow-dot"></span>SOFTWARE TOOL ADOPTION METRICS</div>', unsafe_allow_html=True)

    if not filtered_tool.empty:
        col_e, col_f = st.columns(2)

        with col_e:
            st.markdown("#### Active Minutes Allocation per Tool")
            tool_mins = filtered_tool.groupby("tool_name")["active_minutes"].sum().reset_index()
            fig_tool_mins = px.pie(
                tool_mins,
                names="tool_name",
                values="active_minutes",
                color_discrete_sequence=["#141413", "#F37338", "#CF4500", "#3860BE", "#9A3A0A", "#696969"],
                hole=0.5
            )
            apply_mc_chart_style(fig_tool_mins)
            st.plotly_chart(fig_tool_mins, use_container_width=True)

        with col_f:
            st.markdown("#### Logins vs Daily Active Minutes")
            fig_tool_scatter = px.scatter(
                filtered_tool.sample(min(1000, len(filtered_tool)), random_state=42),
                x="login_count",
                y="active_minutes",
                color="tool_name",
                color_discrete_sequence=["#141413", "#F37338", "#CF4500", "#3860BE", "#9A3A0A"],
                labels={"login_count": "Daily Logins", "active_minutes": "Active Minutes"}
            )
            apply_mc_chart_style(fig_tool_scatter)
            st.plotly_chart(fig_tool_scatter, use_container_width=True)
    else:
        st.info("No tool usage data found for current selection.")

# =========================================================
# TAB 5: PySQL QUERY SANDBOX
# =========================================================
with tab5:
    st.markdown('<div class="mc-eyebrow"><span class="mc-eyebrow-dot"></span>PYSQL IN-MEMORY CONSOLE</div>', unsafe_allow_html=True)
    st.write("Execute ANSI SQL queries against in-memory tables (`employees`, `onboarding`, `support_tickets`, `tool_usage`).")

    query_presets = {
        "High Friction New Hires": """
SELECT 
    e.employee_id, 
    e.Department, 
    e.JobRole, 
    o.training_completion_percent, 
    o.onboarding_status, 
    COUNT(s.ticket_id) AS total_tickets
FROM employees e
JOIN onboarding o ON e.employee_id = o.employee_id
LEFT JOIN support_tickets s ON e.employee_id = s.employee_id
WHERE o.onboarding_status != 'Completed' OR o.training_completion_percent < 60.0
GROUP BY e.employee_id, e.Department, e.JobRole, o.training_completion_percent, o.onboarding_status
ORDER BY total_tickets DESC;
""",
        "IT Support Resolution Bottlenecks": """
SELECT 
    assigned_team, 
    issue_type, 
    priority, 
    COUNT(*) AS total_tickets, 
    ROUND(AVG(resolution_hours), 2) AS avg_resolution_hours
FROM support_tickets
GROUP BY assigned_team, issue_type, priority
ORDER BY avg_resolution_hours DESC;
""",
        "Tool Usage by Department": """
SELECT 
    e.Department, 
    t.tool_name, 
    COUNT(DISTINCT e.employee_id) AS active_users, 
    ROUND(AVG(t.active_minutes), 1) AS avg_active_mins
FROM employees e
JOIN tool_usage t ON e.employee_id = t.employee_id
GROUP BY e.Department, t.tool_name
ORDER BY e.Department, active_users DESC;
"""
    }

    selected_preset = st.selectbox("Load Preset Query", ["Custom Query"] + list(query_presets.keys()))
    
    default_sql = query_presets.get(selected_preset, "SELECT * FROM employees LIMIT 10;")
    user_query = st.text_area("SQL Input Console", value=default_sql.strip(), height=150)

    if st.button("Execute Query"):
        try:
            query_res = pd.read_sql_query(user_query, db_conn)
            st.success(f"Query returned {len(query_res)} records.")
            st.dataframe(query_res, use_container_width=True)
            
            csv_data = query_res.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV Results",
                data=csv_data,
                file_name="vibecheck_query_results.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"SQL Error: {e}")

# ---------------------------------------------------------
# Mastercard Dark Warm-Black Footer (#141413)
# ---------------------------------------------------------
st.markdown("""
<div class="mc-footer">
    <div class="mc-footer-headline">We're always here when you need operational insights.</div>
    <div class="mc-footer-grid">
        <div>
            <div class="mc-footer-col-title">VIBECHECK PLATFORM</div>
            <a class="mc-footer-link">Executive Overview</a>
            <a class="mc-footer-link">Onboarding Benchmarks</a>
            <a class="mc-footer-link">PySQL Console Engine</a>
        </div>
        <div>
            <div class="mc-footer-col-title">SOLUTIONS</div>
            <a class="mc-footer-link">DevOps Support Queues</a>
            <a class="mc-footer-link">IT Bottleneck Prevention</a>
            <a class="mc-footer-link">Software Tool Adoption</a>
        </div>
        <div>
            <div class="mc-footer-col-title">DATA PIPELINE</div>
            <a class="mc-footer-link">Supabase REST Integration</a>
            <a class="mc-footer-link">PostgreSQL Schema DDL</a>
            <a class="mc-footer-link">Synthetic ETL Pipeline</a>
        </div>
        <div>
            <div class="mc-footer-col-title">NEED HELP?</div>
            <a class="mc-footer-link">Support Desk</a>
            <a class="mc-footer-link">Documentation</a>
            <a class="mc-footer-link">Privacy & Consent</a>
        </div>
    </div>
    <div class="mc-footer-bottom">
        <div>© 2026 VibeCheck Analytics Network. All rights reserved.</div>
        <div>Global English (US)</div>
    </div>
</div>
""", unsafe_allow_html=True)
