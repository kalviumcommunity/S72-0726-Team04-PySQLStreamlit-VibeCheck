import sqlite3
import math
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# Page Configuration & Modern Design System
# ---------------------------------------------------------
st.set_page_config(
    page_title="VibeCheck | Onboarding & Operational Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS for Premium Aesthetics
st.markdown("""
<style>
    /* Dark Glassmorphism Styling */
    .main {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    }

    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #58a6ff, #bc8cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    div[data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(48, 54, 61, 0.8);
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #58a6ff;
    }

    /* Header styling */
    .header-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38ef7d, #11998e, #38ef7d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .sub-title {
        color: #8b949e;
        font-size: 1.05rem;
        margin-bottom: 25px;
    }

    /* Table & Console aesthetics */
    .sql-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        color: #8b949e;
        font-weight: 600;
        border: 1px solid #30363d;
    }

    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        color: #58a6ff !important;
        border-bottom: 2px solid #58a6ff !important;
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
# Sidebar & Global Filters
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/isometric/96/lightning-bolt.png", width=64)
st.sidebar.title("VibeCheck Filters")

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
# Main App Header
# ---------------------------------------------------------
st.markdown('<div class="header-title">⚡ VibeCheck: Onboarding & Operational Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Identifying Operational Friction, IT Bottlenecks & Productivity Barriers for New Hires</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Dashboard Navigation Tabs
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Overview",
    "⚡ Onboarding Friction",
    "🎫 IT Support Bottlenecks",
    "💻 Tool Adoption & Activity",
    "🔍 PySQL Sandbox"
])

# =========================================================
# TAB 1: EXECUTIVE OVERVIEW
# =========================================================
with tab1:
    st.subheader("Key Performance Indicators (KPIs)")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_emp = len(filtered_emp)
    completed_onb = (filtered_onb["onboarding_status"] == "Completed").sum()
    onb_completion_rate = (completed_onb / max(total_emp, 1)) * 100
    
    avg_resolution = filtered_tck["resolution_hours"].dropna().mean()
    avg_resolution_str = f"{avg_resolution:.1f} hrs" if not math.isnan(avg_resolution) else "N/A"
    
    avg_training = filtered_onb["training_completion_percent"].mean()
    
    # Calculate Friction Score (% with delayed onboarding or >2 tickets)
    ticket_counts = filtered_tck.groupby("employee_id").size().to_dict()
    high_friction_count = 0
    for _, r in filtered_onb.iterrows():
        eid = r["employee_id"]
        tc = ticket_counts.get(eid, 0)
        if r["onboarding_status"] == "Delayed" or r["training_completion_percent"] < 60.0 or tc >= 3:
            high_friction_count += 1
            
    col1.metric("Filtered Employees", f"{total_emp:,}")
    col2.metric("Onboarding Completion", f"{onb_completion_rate:.1f}%")
    col3.metric("Avg Training Score", f"{avg_training:.1f}%")
    col4.metric("Avg Ticket Resolution", avg_resolution_str)
    col5.metric("High-Friction Hires", f"{high_friction_count:,}", delta=f"{(high_friction_count/max(total_emp,1))*100:.1f}% of total", delta_color="inverse")

    st.markdown("---")

    col_left, col_right = st.columns([1.2, 1])
    
    with col_left:
        st.markdown("### 📈 Onboarding Status Distribution by Department")
        dept_onb = filtered_emp.merge(filtered_onb, on="employee_id")
        dept_status_summary = dept_onb.groupby(["Department", "onboarding_status"]).size().reset_index(name="Count")
        
        fig_status = px.bar(
            dept_status_summary,
            x="Department",
            y="Count",
            color="onboarding_status",
            barmode="group",
            color_discrete_map={"Completed": "#38ef7d", "In Progress": "#58a6ff", "Delayed": "#ff4b4b"},
            template="plotly_dark"
        )
        fig_status.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_status, use_container_width=True)

    with col_right:
        st.markdown("### 🧭 Support Ticket Priority Breakdown")
        if not filtered_tck.empty:
            prio_summary = filtered_tck["priority"].value_counts().reset_index()
            prio_summary.columns = ["Priority", "Count"]
            fig_prio = px.pie(
                prio_summary,
                names="Priority",
                values="Count",
                color="Priority",
                color_discrete_map={"Low": "#58a6ff", "Medium": "#e3b341", "High": "#f0883e", "Critical": "#ff4b4b"},
                hole=0.45,
                template="plotly_dark"
            )
            fig_prio.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_prio, use_container_width=True)
        else:
            st.info("No tickets match current filters.")

# =========================================================
# TAB 2: ONBOARDING FRICTION ANALYTICS
# =========================================================
with tab2:
    st.subheader("⚡ New Hire Friction & Training Completion Impact")
    st.write("Examine how incomplete onboarding training directly correlates with support ticket spikes and operational delays.")

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
            color_discrete_map={"Completed": "#38ef7d", "In Progress": "#58a6ff", "Delayed": "#ff4b4b"},
            labels={"training_completion_percent": "Training Completion (%)", "ticket_count": "Support Ticket Count"},
            template="plotly_dark"
        )
        fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
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
            color_discrete_map={"Completed": "#38ef7d", "In Progress": "#58a6ff", "Delayed": "#ff4b4b"},
            template="plotly_dark"
        )
        fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("#### 🚨 High-Friction Employee Directory")
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
    st.subheader("🎫 IT & DevOps Support Bottleneck Analysis")
    st.write("Track resolution delays, team workload, and critical ticket distribution.")

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
                color_discrete_map={"Low": "#58a6ff", "Medium": "#e3b341", "High": "#f0883e", "Critical": "#ff4b4b"},
                labels={"resolution_hours": "Avg Resolution (Hours)"},
                template="plotly_dark"
            )
            fig_res.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_res, use_container_width=True)

        with col_d:
            st.markdown("#### Ticket Issue Type Volume by Team")
            team_issue = filtered_tck.groupby(["assigned_team", "issue_type"]).size().reset_index(name="count")
            fig_team = px.bar(
                team_issue,
                x="assigned_team",
                y="count",
                color="issue_type",
                barmode="stack",
                labels={"count": "Number of Tickets"},
                template="plotly_dark"
            )
            fig_team.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_team, use_container_width=True)
    else:
        st.info("No ticket data matching current filter selection.")

# =========================================================
# TAB 4: TOOL ADOPTION & ACTIVITY
# =========================================================
with tab4:
    st.subheader("💻 Internal Tool Adoption & Activity Metrics")
    st.write("Monitor session frequency, daily active minutes, and primary device usage.")

    if not filtered_tool.empty:
        col_e, col_f = st.columns(2)

        with col_e:
            st.markdown("#### Total Active Minutes per Software Tool")
            tool_mins = filtered_tool.groupby("tool_name")["active_minutes"].sum().reset_index()
            fig_tool_mins = px.pie(
                tool_mins,
                names="tool_name",
                values="active_minutes",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.4,
                template="plotly_dark"
            )
            fig_tool_mins.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_tool_mins, use_container_width=True)

        with col_f:
            st.markdown("#### Active Minutes vs Daily Logins by Tool")
            fig_tool_scatter = px.scatter(
                filtered_tool.sample(min(1000, len(filtered_tool)), random_state=42),
                x="login_count",
                y="active_minutes",
                color="tool_name",
                hover_data=["feature_used", "device_type"],
                labels={"login_count": "Daily Logins", "active_minutes": "Active Minutes"},
                template="plotly_dark"
            )
            fig_tool_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_tool_scatter, use_container_width=True)
    else:
        st.info("No tool usage data found for the current selection.")

# =========================================================
# TAB 5: PySQL QUERY SANDBOX
# =========================================================
with tab5:
    st.subheader("🔍 PySQL Live Query Console")
    st.write("Execute SQL queries against the in-memory database (`employees`, `onboarding`, `support_tickets`, `tool_usage`).")

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
    user_query = st.text_area("SQL Query Input", value=default_sql.strip(), height=160)

    if st.button("▶ Run SQL Query"):
        try:
            query_res = pd.read_sql_query(user_query, db_conn)
            st.success(f"Query returned {len(query_res)} rows successfully.")
            st.dataframe(query_res, use_container_width=True)
            
            # Download CSV option
            csv_data = query_res.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Query Results (CSV)",
                data=csv_data,
                file_name="vibecheck_query_results.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")
