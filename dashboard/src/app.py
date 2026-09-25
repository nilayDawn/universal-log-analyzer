import streamlit as st
import sqlite3
import pandas as pd
import json
import os
import sys
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from LogAnalyzer.config import Config

st.set_page_config(page_title="AIOps Incident Command", layout="wide", page_icon="🛡️")

def fetch_incidents():
    db_path = os.path.abspath(Config.SQLITE_DB_PATH)
    if not os.path.exists(db_path):
        return pd.DataFrame()
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM incidents ORDER BY detected_at DESC", conn)
    conn.close()
    
    if not df.empty:
        df['detected_at'] = pd.to_datetime(df['detected_at'])
        
        # Categorize confidence for visuals
        def categorize_confidence(score):
            if score >= 0.9: return "High"
            elif score >= 0.7: return "Medium"
            else: return "Low"
            
        df['confidence_tier'] = df['confidence_level'].apply(categorize_confidence)
    return df

st.title("🛡️ AIOps Incident Command Center")
st.markdown("Real-time generative AI root cause analysis for streaming log anomalies.")
st.divider()

df = fetch_incidents()

if df.empty:
    st.success("No critical incidents detected. System is healthy.")
else:
    # --- KPI METRICS ---
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(label="Total Critical Incidents", value=len(df))
    kpi2.metric(label="High Confidence Diagnoses", value=len(df[df['confidence_tier'] == 'High']))
    kpi3.metric(label="Unique Entities Affected", value=df['block_id'].nunique())
    
    st.write(" ")
    
    # --- VISUALIZATIONS ---
    chart_col1, chart_col2 = st.columns([2, 1])
    
    with chart_col1:
        st.subheader("Incident Detection Timeline")
        # Group by hour/minute for trend line
        timeline_df = df.set_index('detected_at').resample('h').size().reset_index(name='count')
        fig_timeline = px.line(timeline_df, x='detected_at', y='count', markers=True, 
                               labels={'detected_at': 'Time', 'count': 'Incidents'},
                               line_shape='spline')
        fig_timeline.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=300)
        st.plotly_chart(fig_timeline, use_container_width=True)
        
    with chart_col2:
        st.subheader("AI Confidence Distribution")
        color_map = {"High": "#00CC96", "Medium": "#FFA15A", "Low": "#EF553B"}
        fig_pie = px.pie(df, names='confidence_tier', color='confidence_tier',
                         color_discrete_map=color_map, hole=0.4)
        fig_pie.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()
    st.subheader("Recent Incident Reports")
    
    # --- INCIDENT CARDS ---
    for _, row in df.iterrows():
        with st.expander(f"🚨 {row['block_id']} | Detected: {row['detected_at'].strftime('%Y-%m-%d %H:%M:%S')}"):
            col_text, col_score = st.columns([3, 1])
            
            with col_text:
                st.markdown("**Root Cause Analysis**")
                st.write(row['root_cause_summary'])
                
                st.markdown("**Recommended Remediation**")
                steps = json.loads(row['remediation_steps'])
                for step in steps:
                    st.markdown(f"- `{step}`")
                    
            with col_score:
                st.metric(label="AI Confidence Level", value=f"{row['confidence_level'] * 100:.1f}%")
                if row['confidence_tier'] == "High":
                    st.success("High Confidence")
                elif row['confidence_tier'] == "Medium":
                    st.warning("Medium Confidence")
                else:
                    st.error("Low Confidence - Manual Review Advised")