import streamlit as st
import pandas as pd
import sqlite3
import os
from engine.agent import EnterpriseCoWorkEngine
from config.semantic_layer import STARTER_QUESTIONS

st.set_page_config(page_title="Enterprise CoWork Workspace", layout="wide")
st.title("⚡ Enterprise CoWork Agent (Production Architecture)")

# Path validations matching setup requirements
DB_PATH = os.path.join("data", "mock_data.db")

if not os.path.exists(DB_PATH):
    st.error("🚨 Relational Data Storage Layer Offline. Run `python setup.py` to compile structural components.")
    st.stop()

# Secret verification for api connections
if "GROQ_API_KEY" not in os.environ:
    user_token = st.sidebar.text_input("🔑 Provide your Groq Developer API Key:", type="password")
    if user_token:
        os.environ["GROQ_API_KEY"] = user_token
    else:
        st.info("💡 Input your Groq API key in the sidebar layout wrapper to initiate communication channels.")
        st.stop()

# ------------------------------------------------------------------
# SYSTEM TELEMETRY SIDEBAR HANDLER
# ------------------------------------------------------------------
conn = sqlite3.connect(DB_PATH)
with st.sidebar:
    st.markdown("### 📊 Enterprise DB Telemetry")
    for table in ["sales", "products", "marketing_campaign_metrics", "social_media", "support_cases"]:
        count = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {table}", conn).iloc[0]['cnt']
        st.caption(f"💾 **{table}**: {count} Verified Rows in production partition.")
conn.close()

# Instantiate core execution engine from decoupled application layer
engine = EnterpriseCoWorkEngine(db_path=DB_PATH)

st.markdown("Select an onboarded enterprise quick-prompt to launch analysis:")
user_query = st.chat_input("Query local decoupled workspace files...")

# Fast-execution control matrix mapping configuration array values
layout_cols = st.columns(3)
if layout_cols.button("📋 Q1: Trend Analysis"):
    user_query = STARTER_QUESTIONS[0]
if layout_cols.button("⚠️ Q2: Jacket Flaw Auditing"):
    user_query = STARTER_QUESTIONS[1]
if layout_cols.button("📈 Q3: Growth Correlation Run"):
    user_query = STARTER_QUESTIONS[2]

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
