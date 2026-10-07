import os
import sys
import time
import json
import pandas as pd
import streamlit as st
import plotly.express as px

# Root path add chesthunnam internal modules import kosam
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from ai_engine.anomaly_detector import TransactionAnomalyDetector
from ai_engine.llm_insights import SecurityInsightsGenerator

# Page Configuration
st.set_page_config(
    page_title="FinTech AI Real-Time Fraud Radar",
    page_icon="🛡️",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background-color: #1e222d;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Real-Time AI Fraud & Risk Analytics Platform")
st.caption("Live Transaction Stream • Isolation Forest Detection • LLM Incident Summarizer")

# Initialize Models
@st.cache_resource
def load_components():
    detector = TransactionAnomalyDetector()
    llm_generator = SecurityInsightsGenerator()
    return detector, llm_generator

detector, llm_generator = load_components()

STREAM_FILE = os.path.join(ROOT_DIR, "data_pipeline", "live_stream.jsonl")

# UI Placeholders for live continuous updates
kpi_placeholder = st.empty()
chart_placeholder = st.empty()
table_placeholder = st.empty()
briefing_placeholder = st.sidebar.empty()

# Sidebar Control
st.sidebar.header("Controls & AI Briefing")
poll_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 5, 2)
st.sidebar.divider()

def read_stream_records(limit=100):
    """Reads the most recent lines from the live stream buffer."""
    if not os.path.exists(STREAM_FILE):
        return []
    records = []
    try:
        with open(STREAM_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
            for line in lines:
                if line.strip():
                    records.append(json.loads(line.strip()))
    except Exception:
        pass
    return records

# Continuous Live Polling Loop
last_ai_briefing_time = 0
cached_briefing = "Initializing Live Monitoring... Waiting for events."

while True:
    raw_data = read_stream_records(limit=120)
    
    if not raw_data:
        st.warning("⚠️ No live transactions detected yet! Please start `python data_pipeline/producer.py` in a separate terminal.")
        time.sleep(2)
        continue

    # Process batch with ML Anomaly Detector
    processed_records = []
    flagged_records = []
    
    for item in raw_data:
        is_fraud, risk_score = detector.predict_anomaly(item["amount"], item["device"])
        rec = dict(item)
        rec["is_anomaly"] = is_fraud
        rec["risk_score"] = risk_score
        processed_records.append(rec)
        if is_fraud:
            flagged_records.append(rec)

    df = pd.DataFrame(processed_records)

    # 1. Update Top KPIs
    total_txns = len(df)
    anomalies_count = len(flagged_records)
    total_volume = df["amount"].sum() if "amount" in df else 0
    fraud_rate = (anomalies_count / total_txns * 100) if total_txns > 0 else 0

    with kpi_placeholder.container():
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Live Transactions Monitored", f"{total_txns}")
        col2.metric("Flagged Anomalies", f"{anomalies_count}", delta=f"{fraud_rate:.1f}% Risk", delta_color="inverse")
        col3.metric("Monitored Volume", f"₹{total_volume:,.2f}")
        col4.metric("Active Detection Engine", "Isolation Forest v1.0")

    # 2. Update Dynamic Visualizations
    with chart_placeholder.container():
        c1, c2 = st.columns([2, 1])
        
        # Real-time Amount Scatter with Anomaly highlight
        fig_scatter = px.scatter(
            df,
            x="timestamp",
            y="amount",
            color="is_anomaly",
            color_discrete_map={True: "#ff4b4b", False: "#00cc96"},
            title="Live Transaction Amount Trajectory (Red = Flagged Anomaly)",
            hover_data=["sender_id", "location", "device"]
        )
        fig_scatter.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        c1.plotly_chart(fig_scatter, use_container_width=True)

        # Device Distribution Chart
        fig_pie = px.pie(
            df,
            names="device",
            title="Traffic Distribution by Device",
            hole=0.4
        )
        fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        c2.plotly_chart(fig_pie, use_container_width=True)

    # 3. AI Security Briefing (Every 15-20 seconds or when triggered)
    current_time = time.time()
    if (current_time - last_ai_briefing_time > 20) and flagged_records:
        cached_briefing = llm_generator.generate_incident_summary(
            flagged_transactions=flagged_records[-5:],
            total_volume=total_txns,
            anomaly_count=anomalies_count
        )
        last_ai_briefing_time = current_time

    with briefing_placeholder.container():
        st.subheader("🤖 AI Incident Briefing")
        st.markdown(cached_briefing)

    # 4. Recent Transactions Data Feed Table
    with table_placeholder.container():
        st.subheader("🚨 Live Event Log (Latest 10 Events)")
        display_cols = ["timestamp", "transaction_id", "amount", "location", "device", "is_anomaly", "risk_score"]
        styled_df = df[display_cols].tail(10).iloc[::-1]
        st.dataframe(styled_df, use_container_width=True)

    time.sleep(poll_interval)