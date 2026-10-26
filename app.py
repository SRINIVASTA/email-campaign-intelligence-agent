import streamlit as st
import pandas as pd
import sqlite3
import os
from engine.agent import EnterpriseCoWorkEngine
from config.semantic_layer import STARTER_QUESTIONS

st.set_page_config(page_title="Email Campaign Agent Workspace", layout="wide")
st.title("✉️ Email Campaign Automation Hub (Production Architecture)")

# ------------------------------------------------------------------
# 1. STREAMLIT SECRETS INGESTION LAYER
# ------------------------------------------------------------------
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
else:
    st.error("❌ `GROQ_API_KEY` missing from Streamlit Secrets! Please populate your web app configuration settings.")
    st.stop()

# ------------------------------------------------------------------
# 2. AUTOMATED WEB PROVISIONING
# ------------------------------------------------------------------
DB_PATH = os.path.join("data", "mock_data.db")

if not os.path.exists(DB_PATH):
    st.info("📦 First-time Web Server initialization detected. Compiling database partitions...")
    try:
        from setup import provision_enterprise_workspace
        provision_enterprise_workspace()
        st.success("✨ Local data layout successfully provisioned on web instance!")
    except Exception as setup_err:
        st.error(f"Failed to auto-provision data storage layer: {setup_err}")
        st.stop()

# ------------------------------------------------------------------
# 3. LIVE SYSTEM TELEMETRY SIDEBAR HANDLER (Aligned to correct Schemas)
# ------------------------------------------------------------------
conn = sqlite3.connect(DB_PATH)
with st.sidebar:
    st.markdown("### 📊 Enterprise DB Telemetry")
    target_tables = ["email_campaigns", "campaign_metrics", "revenue_attribution", "recipient_feedback"]
    for table in target_tables:
        try:
            count_df = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {table}", conn)
            count = count_df.iloc[0]['cnt']
            st.caption(f"💾 **{table}**: {count} Verified Rows in web partition.")
        except Exception as e:
            st.caption(f"⚠️ **{table}**: Schema partition locked or missing.")
conn.close()

# ------------------------------------------------------------------
# 4. INSTANTIATE CORE DECOUPLED ENGINE INTERFACE
# ------------------------------------------------------------------
engine = EnterpriseCoWorkEngine(db_path=DB_PATH)

st.markdown("Select an onboarded enterprise quick-prompt to launch analysis:")

# Fix: Correctly break down columns layout assignment and extraction
layout_cols = st.columns(3)
selected_query = None

if layout_cols[0].button("📋 Q1: Trend Analysis", use_container_width=True):
    selected_query = STARTER_QUESTIONS[0]
if layout_cols[1].button("⚠️ Q2: Feedback Auditing", use_container_width=True):
    selected_query = STARTER_QUESTIONS[1]
if layout_cols[2].button("📈 Q3: Growth Correlation Run", use_container_width=True):
    selected_query = STARTER_QUESTIONS[2]

# Ingest free-form input or fall back to quick buttons
input_query = st.chat_input("Query web workspace files...")
user_query = input_query if input_query else selected_query

# ------------------------------------------------------------------
# 5. CORE EXECUTION AND LIVE VISUALIZATION INTERCEPTOR
# ------------------------------------------------------------------
if user_query:
    st.chat_message("user").markdown(user_query)
    
    with st.chat_message("assistant"):
        try:
            with st.spinner("⚡ Decoupled Engine parsing request across partitions..."):
                response_text = engine.execute_analytical_query(user_query)
                st.markdown(response_text)
                
            if any(word in user_query.lower() for word in ["trend", "sales", "grow", "correlate"]):
                st.info("📊 Local Visualization Handler Triggered:")
                conn = sqlite3.connect(DB_PATH)
                
                # Fix: Aligned fallback visualization query directly to the real schema
                viz_df = pd.read_sql_query("""
                    SELECT conversion_date AS date, product_category AS category, SUM(attributed_sales) as revenue_total 
                    FROM revenue_attribution 
                    GROUP BY conversion_date, product_category
                """, conn)
                conn.close()
                
                if not viz_df.empty:
                    st.line_chart(data=viz_df, x="date", y="revenue_total", color="category")
                else:
                    st.warning("No data returned for historical visualization layer mapping.")
                
        except Exception as runtime_fault:
            st.error(f"Engine Exception Met: {runtime_fault}")
