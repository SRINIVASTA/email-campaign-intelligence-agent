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
# Automatically pull credentials from .streamlit/secrets.toml and link to environment
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
else:
    st.error("❌ `GROQ_API_KEY` missing from Streamlit Secrets! Please populate your `.streamlit/secrets.toml` configuration file.")
    st.stop()

# ------------------------------------------------------------------
# 2. LOCAL FILE SYSTEM & STORAGE VALIDATIONS
# ------------------------------------------------------------------
DB_PATH = os.path.join("data", "mock_data.db")

if not os.path.exists(DB_PATH):
    st.error("🚨 Relational Data Storage Layer Offline. Run `python setup.py` to compile structural components.")
    st.stop()

# ------------------------------------------------------------------
# 3. LIVE SYSTEM TELEMETRY SIDEBAR HANDLER
# ------------------------------------------------------------------
conn = sqlite3.connect(DB_PATH)
with st.sidebar:
    st.markdown("### 📊 Enterprise DB Telemetry")
    for table in ["sales", "products", "marketing_campaign_metrics", "social_media", "support_cases"]:
        try:
            # Query table row configuration using position index [0] to match scalar extraction properties
            count_df = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {table}", conn)
            count = count_df.iloc[0]['cnt']
            st.caption(f"💾 **{table}**: {count} Verified Rows in production partition.")
        except Exception:
            st.caption(f"⚠️ **{table}**: Schema unreadable or parsing partition locked.")
conn.close()

# ------------------------------------------------------------------
# 4. INSTANTIATE CORE DECOUPLED ENGINE INTERFACE
# ------------------------------------------------------------------
engine = EnterpriseCoWorkEngine(db_path=DB_PATH)

st.markdown("Select an onboarded enterprise quick-prompt to launch analysis:")
user_query = st.chat_input("Query local decoupled workspace files...")

# Fast-execution control matrix mapping configuration array values safely
layout_cols = st.columns(3)
if layout_cols.button("📋 Q1: Trend Analysis"):
    user_query = STARTER_QUESTIONS[0]
if layout_cols.button("⚠️ Q2: Jacket Flaw Auditing"):
    user_query = STARTER_QUESTIONS[1]
if layout_cols.button("📈 Q3: Growth Correlation Run"):
    user_query = STARTER_QUESTIONS[2]

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
                
            # AUTO-VISUALIZATION ENGINE INTERCEPTOR
            if any(word in user_query.lower() for word in ["trend", "sales", "grow", "correlate"]):
                st.info("📊 Local Visualization Handler Triggered:")
                conn = sqlite3.connect(DB_PATH)
                viz_df = pd.read_sql_query("""
                    SELECT s.date, p.category, SUM(s.sales_amount) as revenue_total 
                    FROM sales s 
                    JOIN products p ON s.product_id = p.product_id 
                    GROUP BY s.date, p.category
                """, conn)
                conn.close()
                st.line_chart(data=viz_df, x="date", y="revenue_total", color="category")
                
        except Exception as runtime_fault:
            st.error(f"Engine Exception Met: {runtime_fault}")
