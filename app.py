import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv

# ---------------------------------------------------------
# Page Configuration & Styling Layout
# ---------------------------------------------------------
st.set_page_config(page_title="Onboarding Dashboard", layout="wide")

# Inject Custom CSS for Shadcn-like metrics cards and clean styling
st.markdown("""
<style>
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: #0f172a !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: #64748b !important;
    }
    /* Main Background */
    .stApp {
        background-color: #f8fafc;
    }
    /* Hide top padding */
    .block-container {
        padding-top: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Supabase Connection Logic
# ---------------------------------------------------------
# 1. To connect to your Supabase instance, uncomment the lines below
# 2. Make sure you have python-dotenv and supabase installed (already in requirements.txt)
# 3. Create a .env file with SUPABASE_URL and SUPABASE_ANON_KEY

# from supabase import create_client, Client
# load_dotenv()
# url: str = os.environ.get("SUPABASE_URL")
# key: str = os.environ.get("SUPABASE_ANON_KEY")
# supabase: Client = create_client(url, key)

# ---------------------------------------------------------
# Data Fetching (Cached to prevent glitching)
# ---------------------------------------------------------

@st.cache_data(ttl=3600)
def fetch_kpis():
    # Replace this mock logic with actual Supabase RPC/select call:
    # response = supabase.table("mv_dashboard_unified_kpis").select("*").execute()
    # return pd.DataFrame(response.data)
    
    return pd.DataFrame({
        "Total Employees": [1240],
        "Onboarding Completion %": [84.5],
        "Avg Support Tickets (New Hires)": [2.3],
        "Tool Adoption Rate %": [92.1]
    })

@st.cache_data(ttl=3600)
def fetch_friction_by_issue():
    # Replace this mock logic with actual Supabase RPC/select call:
    # response = supabase.table("vw_friction_by_issue").select("*").execute()
    # return pd.DataFrame(response.data)
    
    return pd.DataFrame({
        "Issue Type": ["Access Rights", "Software Install", "Hardware Setup", "General Q&A", "Payroll"],
        "Ticket Count": [320, 240, 150, 100, 50],
        "Avg Resolution (hrs)": [4.2, 5.1, 12.0, 1.5, 2.0]
    })

@st.cache_data(ttl=3600)
def fetch_tool_adoption():
    # Replace this mock logic with actual Supabase RPC/select call:
    # response = supabase.table("vw_tool_adoption_curves").select("*").execute()
    # return pd.DataFrame(response.data)
    
    return pd.DataFrame({
        "Day": list(range(1, 15)),
        "Slack": [95, 92, 90, 88, 87, 85, 84, 83, 82, 80, 80, 79, 78, 78],
        "Jira": [40, 45, 55, 60, 65, 70, 72, 75, 76, 78, 79, 80, 82, 83],
        "Notion": [70, 75, 78, 80, 82, 83, 84, 85, 85, 85, 86, 86, 87, 87]
    })

# Load data
df_kpis = fetch_kpis()
df_friction = fetch_friction_by_issue()
df_tools = fetch_tool_adoption()

# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## VibeCheck Dashboard")
    selected_page = option_menu(
        menu_title=None,  
        options=["Executive Summary", "IT Support & Roadblocks", "Tool Adoption"], 
        icons=["house", "wrench", "graph-up"], 
        menu_icon="cast", 
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#0f172a", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#e2e8f0"},
            "nav-link-selected": {"background-color": "#0f172a", "color": "white", "font-weight": "normal"},
        }
    )

# Helper function to clean up Plotly layout
def clean_plotly_layout(fig):
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig

# ---------------------------------------------------------
# Page 1: Executive Summary
# ---------------------------------------------------------
if selected_page == "Executive Summary":
    st.title("Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Employees", value=f"{df_kpis['Total Employees'][0]:,}")
    with col2:
        st.metric(label="Onboarding Completion", value=f"{df_kpis['Onboarding Completion %'][0]}%")
    with col3:
        st.metric(label="Avg Support Tickets", value=f"{df_kpis['Avg Support Tickets (New Hires)'][0]}")
    with col4:
        st.metric(label="Tool Adoption Rate", value=f"{df_kpis['Tool Adoption Rate %'][0]}%")
        
    st.markdown("### Top Bottlenecks")
    fig = px.bar(df_friction.sort_values(by="Ticket Count", ascending=True), 
                 x="Ticket Count", y="Issue Type", orientation='h', 
                 title="Most Common Friction Points")
    clean_plotly_layout(fig)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# Page 2: IT Support & Roadblocks
# ---------------------------------------------------------
elif selected_page == "IT Support & Roadblocks":
    st.title("IT Support & Roadblocks")
    
    tab1, tab2 = st.tabs(["Ticket Volumes", "Resolution Times"])
    
    with tab1:
        st.markdown("### Volume of Tickets by Category")
        fig1 = px.pie(df_friction, values='Ticket Count', names='Issue Type', hole=0.4)
        clean_plotly_layout(fig1)
        st.plotly_chart(fig1, use_container_width=True)
        
    with tab2:
        st.markdown("### Average Resolution Time (Hours)")
        fig2 = px.bar(df_friction, x="Issue Type", y="Avg Resolution (hrs)", 
                      color="Avg Resolution (hrs)", color_continuous_scale="Reds")
        clean_plotly_layout(fig2)
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------
# Page 3: Tool Adoption
# ---------------------------------------------------------
elif selected_page == "Tool Adoption":
    st.title("Tool Adoption")
    st.markdown("Monitoring the active usage of primary tools during the first 14 days of onboarding.")
    
    # Melt the dataframe for Plotly Express line chart
    df_melted = df_tools.melt(id_vars=["Day"], var_name="Tool", value_name="Adoption %")
    
    fig3 = px.line(df_melted, x="Day", y="Adoption %", color="Tool", markers=True,
                   title="14-Day Tool Adoption Curves")
    clean_plotly_layout(fig3)
    fig3.update_yaxes(range=[0, 100])
    st.plotly_chart(fig3, use_container_width=True)
