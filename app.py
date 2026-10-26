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
# 2. AUTOMATED WEB PROVISIONING (Replaces terminal setup.py run)
# ------------------------------------------------------------------
DB_PATH = os.path.join("data", "mock_data.db")

if not os.path.exists(DB_PATH):
    st.info("📦 First-time Web Server initialization detected. Compiling database partitions...")
    try:
        # Import the provisioning logic from your repository setup file dynamically
        from setup import provision_enterprise_workspace
        provision_enterprise_workspace()
        st.success("✨ Local data layout successfully provisioned on web instance!")
    except Exception as setup_err:
        st.error(f"Failed to auto-provision data storage layer: {setup_err}")
        st.stop()

# ------------------------------------------------------------------
# 3. LIVE SYSTEM TELEMETRY SIDEBAR HANDLER
# ------------------------------------------------------------------
conn = sqlite3.connect(DB_PATH)
with st.sidebar:
    st.markdown("### 📊 Enterprise DB Telemetry")
    for table in ["sales", "products", "marketing_campaign_metrics", "social_media", "support_cases"]:
        try:
            count_df = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {table}", conn)
            count = count_df.iloc[0]['cnt']
            st.caption(f"💾 **{table}**: {count} Verified Rows in web partition.")
        except Exception:
            st.caption(f"⚠️ **{table}**: Schema partition locked or loading.")
conn.close()

# ------------------------------------------------------------------
# 4. INSTANTIATE CORE DECOUPLED ENGINE INTERFACE
# ------------------------------------------------------------------
engine = EnterpriseCoWorkEngine(db_path=DB_PATH)

st.markdown("Select an onboarded enterprise quick-prompt to launch analysis:")
user_query = st.chat_input("Query web workspace files...")

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
