import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

import warnings
warnings.filterwarnings("ignore")


from src.llm.detective import get_log_by_id, analyze_anomaly
from src.ml.anomaly import load_data
from src.ml.behavioral_detector import run_behavioral_detector
from src.ml.semantic_detector import run_semantic_detector
from src.ml.aggregate_scores import aggregate_scores

# --- Page Configuration ---
st.set_page_config(page_title="Security Command Center", layout="wide")
st.title("🛡️ Privacy-Preserving Automated Root Cause Engine")

# --- Helper: Fetch ML Results ---
@st.cache_data(ttl=5) # Refreshes every 5 seconds
def fetch_analyzed_data():
    df = load_data()
    if len(df) < 25:
        return pd.DataFrame()
    
    # Run the ML pipeline
    df['semantic_pred'] = run_semantic_detector(df)
    df['behavioral_pred'] = run_behavioral_detector(df)
    df['risk_level'] = df.apply(aggregate_scores, axis=1)
    return df

# --- Main Dashboard Logic ---
df = fetch_analyzed_data()

if df.empty:
    st.warning("⏳ Waiting for enough logs to build a baseline. Keep your generator running!")
else:
    # 1. TOP KPI METRICS
    st.markdown("### System Metrics")
    col1, col2, col3, col4 = st.columns(4)
    total_logs = len(df)
    high_risk = len(df[df['risk_level'] == 'High Risk'])
    medium_risk = len(df[df['risk_level'] == 'Medium Risk'])
    
    col1.metric("Total Logs Processed", total_logs)
    col2.metric("High Risk Anomalies", high_risk, delta_color="inverse")
    col3.metric("Medium Risk Anomalies", medium_risk, delta_color="inverse")
    col4.metric("Active ML Models", 2)

    st.divider()

    # 2. VISUALIZATIONS
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Traffic Volume (Last 100 Logs)")
        recent_df = df.tail(100).copy()
        fig1 = px.histogram(recent_df, x="timestamp", color="log_type", title="Traffic by Log Type")
        st.plotly_chart(fig1, width="stretch")
        
    with col_chart2:
        st.subheader("Risk Distribution")
        fig2 = px.pie(df, names='risk_level', title="Anomaly Ratio", 
                      color='risk_level', color_discrete_map={'Normal':'#2ecc71', 'Medium Risk':'#f39c12', 'High Risk':'#e74c3c'})
        st.plotly_chart(fig2, width="stretch")

    st.divider()

    # 3. INTERACTIVE THREAT FEED
    st.subheader("🚨 Active Threat Feed")
    
    # Filter only risks for the table
    risks_df = df[df['risk_level'] != 'Normal'].sort_values(by='timestamp', ascending=False)
    
    if risks_df.empty:
        st.success("System normal. No anomalies detected.")
    else:
        # Display the anomalies in an interactive dataframe
        st.dataframe(
            risks_df[['id', 'timestamp', 'log_type', 'risk_level', 'details']], 
            width="stretch",
            hide_index=True
        )
        
        # 4. LLM INTEGRATION PANEL
        st.markdown("### 🧠 LLM Root Cause Detective")
        
        # Dropdown to select a specific High Risk ID
        high_risk_ids = risks_df[risks_df['risk_level'] == 'High Risk']['id'].tolist()
        
        if high_risk_ids:
            selected_id = st.selectbox("Select a High Risk Log ID to analyze:", high_risk_ids)
            
            if st.button("Generate Root Cause Analysis (Llama 3)", type="primary"):
                with st.spinner(f"Querying local Llama 3 model for ID {selected_id}..."):
                    import requests
                    
                    # Custom UI fetch for the LLM
                    log_data = get_log_by_id(selected_id)
                    prompt = f"""You are a Cybersecurity Analyst. Analyze this HIGH RISK event:
                    Type: {log_data[0]} | Time: {log_data[1]} | Msg: {log_data[2]}
                    Provide 1. Root Cause and 2. Mitigation."""
                    
                    try:
                        response = requests.post("http://localhost:11434/api/generate", json={"model": "llama3", "prompt": prompt, "stream": False})
                        st.success("Analysis Complete!")
                        st.info(response.json().get("response", ""))
                    except Exception as e:
                        st.error(f"Failed to connect to Ollama: {e}")
        else:
            st.write("No High Risk logs available for analysis.")
