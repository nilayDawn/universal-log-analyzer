import streamlit as st
import os
import pandas as pd
import plotly.express as px
import requests
import json
from datetime import datetime

import warnings
warnings.filterwarnings("ignore")

# --- Configuration ---
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000").rstrip("/")

# --- Page Config & Theme ---
st.set_page_config(
    page_title="Security Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS Styling (Dark Theme Enhancements & Glassmorphism)
st.markdown("""
    <style>
    /* Global Background Adjustments */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #1f2937, #111827);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #374151;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .header-title {
        color: #f8fafc !important;
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        color: #9ca3af;
        margin-top: 0.5rem;
        font-size: 1.1rem;
    }
    
    /* Status Badge Styling */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .status-online {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid #10b981;
    }
    .status-offline {
        background-color: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid #ef4444;
    }
    
    /* Custom Card Containers */
    .custom-card {
        background: #161b22;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #30363d;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- Header Banner ---
st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🛡️ Security Command Center</h1>
        <p class="header-subtitle">Privacy-Preserving Automated Anomaly & Root Cause Analysis Engine</p>
    </div>
""", unsafe_allow_html=True)

# --- Helper: Check Ingestion API Status ---
def check_api_health():
    try:
        response = requests.get(f"{BACKEND_API_URL}/", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

# --- Helper: Fetch ML Results ---
@st.cache_data(ttl=5) # Real-time sync every 5 seconds
def fetch_analyzed_data():
    response = requests.get(f"{BACKEND_API_URL}/api/anomalies", timeout=10)
    response.raise_for_status()
    payload = response.json()
    return pd.DataFrame(payload.get("logs", [])), payload.get("summary", {})

# --- Sidebar Controls ---
with st.sidebar:
    st.image("https://img.icons8.com/nolan/128/shield.png", width=80)
    st.markdown("### System Diagnostics")
    
    api_online = check_api_health()
    if api_online:
        st.markdown('API Ingestion Server: <span class="status-badge status-online">Online</span>', unsafe_allow_html=True)
    else:
        st.markdown('API Ingestion Server: <span class="status-badge status-offline">Offline</span>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("### Dashboard Config")
    min_logs_input = st.number_input("Warmup Min Logs Threshold", min_value=10, max_value=500, value=25)
    
    st.markdown("---")
    st.markdown("### Pipeline Controls")
    if st.button("🔄 Force Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()

# --- Main Dashboard Logic ---
if not api_online:
    st.error(f"🚨 Connection Refused: Cannot reach Ingestion Server at {BACKEND_API_URL}. Please ensure your backend container is healthy and running.")
    st.stop()

try:
    df, summary = fetch_analyzed_data()
except Exception as exc:
    st.error(f"Failed to fetch data from Ingestion Server: {exc}")
    st.stop()

if df.empty:
    min_logs = summary.get("min_logs", min_logs_input)
    total_logs = summary.get("total_logs", 0)
    warmup_pct = min(100, int((total_logs / min_logs) * 100)) if min_logs > 0 else 0
    
    st.warning("⚠️ Baseline Warmup In Progress")
    st.progress(warmup_pct / 100.0)
    st.info(f"⏳ Waiting for enough logs to build ML baseline ({total_logs}/{min_logs} logs collected - {warmup_pct}%). Keep your log generator running!")
else:
    # 1. TOP KPI METRICS
    col1, col2, col3, col4 = st.columns(4)
    total_logs = len(df)
    high_risk = len(df[df['risk_level'] == 'High Risk'])
    medium_risk = len(df[df['risk_level'] == 'Medium Risk'])
    anomaly_rate = f"{( (high_risk + medium_risk) / total_logs * 100 ):.1f}%" if total_logs > 0 else "0.0%"
    
    with col1:
        st.metric("Total Logs Processed", total_logs)
    with col2:
        st.metric("High Risk Anomalies", high_risk, delta=f"{high_risk} alerts", delta_color="inverse")
    with col3:
        st.metric("Medium Risk Anomalies", medium_risk, delta=f"{medium_risk} alerts", delta_color="inverse")
    with col4:
        st.metric("Detection Rate", anomaly_rate)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. TABBED CORE PANELS
    tab1, tab2, tab3 = st.tabs(["🚨 Threat Feed & Diagnostics", "📊 Visual Analytics", "📝 Live Log Stream"])

    with tab1:
        st.subheader("Active Threat Feed")
        risks_df = df[df['risk_level'] != 'Normal'].copy()
        
        if risks_df.empty:
            st.success("🎉 System running normally. No behavioral or semantic anomalies detected.")
        else:
            # Sort by ID descending (most recent first)
            risks_df = risks_df.sort_values(by='id', ascending=False)
            
            # Formatted Columns for Interactive Table
            st.dataframe(
                risks_df[['id', 'timestamp', 'log_type', 'risk_level', 'velocity_10s', 'details']], 
                width="stretch",
                hide_index=True,
                column_config={
                    "id": "Log ID",
                    "timestamp": "Timestamp",
                    "log_type": "Log Type",
                    "risk_level": "Risk Category",
                    "velocity_10s": "Velocity (10s)",
                    "details": "Raw Details"
                }
            )
            
            st.markdown("---")
            
            # LLM ROOTS DETECTIVE
            st.markdown("### 🧠 AI Root Cause Detective")
            st.markdown("Request a secure LLM analysis of any flagged anomaly to trace its behavior.")
            
            # Selectbox includes both High and Medium risks
            flagged_logs = risks_df.to_dict('records')
            options = {f"ID {x['id']} [{x['risk_level']}] - {x['log_type']} - {x['timestamp']}": x for x in flagged_logs}
            
            selected_option = st.selectbox("Select flagged anomaly to inspect:", list(options.keys()))
            
            if selected_option:
                log_data = options[selected_option]
                
                # Show parsed details inside a clean JSON viewer
                with st.expander("🔍 Inspect Anomaly Metadata & Features", expanded=True):
                    inspect_col1, inspect_col2 = st.columns(2)
                    with inspect_col1:
                        st.markdown("**Core Properties**")
                        st.json({
                            "Log ID": log_data["id"],
                            "Timestamp": log_data["timestamp"],
                            "Log Type": log_data["log_type"],
                            "Status Code": log_data["status"],
                            "Risk Level": log_data["risk_level"]
                        })
                    with inspect_col2:
                        st.markdown("**ML Feature Space**")
                        st.json({
                            "Traffic Velocity (10s)": log_data.get("velocity_10s", 0),
                            "Semantic Isolation Pred": log_data.get("semantic_pred", 0),
                            "Behavioral Isolation Pred": log_data.get("behavioral_pred", 0),
                            "Raw Message": log_data["details"]
                        })
                
                # Button to generate root cause analysis
                if st.button("🚀 Analyze Anomaly with Llama 3", type="primary"):
                    with st.spinner(f"Querying local Llama 3 for diagnosis on Log ID {log_data['id']}..."):
                        try:
                            response = requests.post(
                                f"{BACKEND_API_URL}/api/anomalies/{log_data['id']}/analysis",
                                timeout=60,
                            )
                            response.raise_for_status()
                            st.success("Investigation Report Complete!")
                            
                            # Render report beautifully using Markdown
                            st.markdown("#### 📋 Diagnostic Report")
                            st.markdown(
                                f"<div class='custom-card'>{response.json().get('analysis', '')}</div>", 
                                unsafe_allow_html=True
                            )
                        except Exception as e:
                            st.error(f"Failed to generate root cause analysis: {e}")

    with tab2:
        st.subheader("Security Event Analytics")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("#### Anomaly Log Velocity Timeline")
            # Create a chronological scatter plot showing logs over time and highlighting velocities
            fig1 = px.scatter(
                df, 
                x="timestamp", 
                y="velocity_10s", 
                color="risk_level",
                size="velocity_10s", 
                hover_data=["log_type", "status", "details"],
                color_discrete_map={'Normal':'#2ecc71', 'Medium Risk':'#f39c12', 'High Risk':'#e74c3c'},
                template="plotly_dark"
            )
            fig1.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig1, use_container_width=True)
            
        with col_chart2:
            st.markdown("#### Overall Threat Profile Ratio")
            fig2 = px.pie(
                df, 
                names='risk_level', 
                color='risk_level', 
                color_discrete_map={'Normal':'#2ecc71', 'Medium Risk':'#f39c12', 'High Risk':'#e74c3c'},
                hole=0.4,
                template="plotly_dark"
            )
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.subheader("Live Log Stream")
        
        # Filtering controls
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            search_query = st.text_input("🔍 Search within Raw Details:")
        with filter_col2:
            type_options = ["ALL"] + df["log_type"].unique().tolist()
            selected_type = st.selectbox("Filter by Log Type:", type_options)
        with filter_col3:
            risk_options = ["ALL"] + df["risk_level"].unique().tolist()
            selected_risk = st.selectbox("Filter by Risk Category:", risk_options)
            
        # Apply filters
        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[filtered_df["details"].str.contains(search_query, case=False, na=False)]
        if selected_type != "ALL":
            filtered_df = filtered_df[filtered_df["log_type"] == selected_type]
        if selected_risk != "ALL":
            filtered_df = filtered_df[filtered_df["risk_level"] == selected_risk]
            
        # Sort most recent first
        filtered_df = filtered_df.sort_values(by="id", ascending=False)
        
        st.write(f"Showing {len(filtered_df)} of {len(df)} logs.")
        st.dataframe(
            filtered_df[['id', 'timestamp', 'log_type', 'status', 'risk_level', 'details']], 
            width="stretch",
            hide_index=True
        )

