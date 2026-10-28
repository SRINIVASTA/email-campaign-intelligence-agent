import streamlit as st
import pandas as pd
import sqlite3
import os
import time
from datetime import datetime
import streamlit.components.v1 as components
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
# 3. LIVE SYSTEM TELEMETRY SIDEBAR & EXPORT FORMAT SWITCH MATRIX
# ------------------------------------------------------------------
conn = sqlite3.connect(DB_PATH)
with st.sidebar:
    st.markdown("### 📊 Enterprise DB Telemetry")
    target_tables = [
        "sales", 
        "products", 
        "marketing_campaign_metrics", 
        "social_media", 
        "support_cases",
        "subscribers",
        "email_event_logs"
    ]
    for table in target_tables:
        try:
            count_df = pd.read_sql_query(f"SELECT COUNT(*) as cnt FROM {table}", conn)
            count = count_df.at[0, 'cnt']
            st.caption(f"💾 **{table}**: {count} Verified Rows in web partition.")
        except Exception as e:
            st.caption(f"⚠️ **{table}**: Schema partition locked or loading.")
            
    st.markdown("---")
    st.markdown("### ⚙️ Dispatch Export Format Settings")
    # 💡 NEW: Adds the delivery preference matrix toggles inside the side layout panel
    report_format = st.radio(
        "Choose Deliverability Export Output Mode:",
        options=["Standard Plain Text Sync", "Rich-Text Professional PDF Attachment"],
        index=1,
        help="Select standard inline text formatting or full multi-page document attachment packaging."
    )
conn.close()

# ------------------------------------------------------------------
# 4. INSTANTIATE CORE DECOUPLED ENGINE INTERFACE
# ------------------------------------------------------------------
engine = EnterpriseCoWorkEngine(db_path=DB_PATH)

st.markdown("Select an onboarded enterprise quick-prompt to launch analysis:")
selected_query = None

# ⚡ BALANCED DESIGN MATRIX: Splitting layout into 4 unified pathways
layout_cols = st.columns(4)

if layout_cols[0].button("📋 Q1: Trend Analysis", use_container_width=True):
    selected_query = STARTER_QUESTIONS[0]
if layout_cols[1].button("⚠️ Q2: Feedback Auditing", use_container_width=True):
    selected_query = STARTER_QUESTIONS[1]
if layout_cols[2].button("📈 Q3: Growth Correlation Run", use_container_width=True):
    selected_query = STARTER_QUESTIONS[2]
if layout_cols[3].button("🛡️ Q4: Subscriber Hygiene", use_container_width=True):
    # 🔄 CACHE BUSTER: Append a live timestamp so Streamlit can never freeze the execution loop
    selected_query = f"Run the high-visual Q4 Subscriber Health and bounce rate deliverability matrix analysis. ts_{int(time.time())}"

input_query = st.chat_input("Query web workspace files...")
user_query = input_query if input_query else selected_query

# ------------------------------------------------------------------
# 5. CORE EXECUTION AND LIVE VISUALIZATION INTERCEPTOR (ALL QUARTERS)
# ------------------------------------------------------------------
if user_query:
    # Append the selected formatting choice parameter onto the backend logic request pipeline
    format_suffix = " [MODE: PDF]" if "PDF" in report_format else " [MODE: TEXT]"
    processing_query = user_query + format_suffix
    
    st.chat_message("user").markdown(user_query)
    
    with st.chat_message("assistant"):
        try:
            with st.spinner("⚡ Decoupled Engine parsing request across partitions..."):
                response_text = engine.execute_analytical_query(processing_query)
                
            # Render out the standard LLM analysis summaries on your monitor interface
            st.markdown(response_text)
                
            # ✅ UNIVERSAL ATTACHMENT HANDLING: Injects a download button for any quarter if PDF mode is active
            if "PDF" in report_format:
                pdf_target_path = os.path.join("pages", "executive_operations_report.pdf")
                if os.path.exists(pdf_target_path):
                    with open(pdf_target_path, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Download Generated Rich-Text Executive PDF Report",
                            data=pdf_file,
                            file_name=f"Enterprise_Operations_Audit_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
            
            # Interactive visualization graph chart tracking engines
            if any(word in user_query.lower() for word in ["trend", "sales", "grow", "correlate", "quarter"]):
                st.info("📊 Local Visualization Handler Triggered:")
                conn = sqlite3.connect(DB_PATH)
                viz_df = pd.read_sql_query("""
                    SELECT s.date, p.category, SUM(s.sales_amount) as revenue_total 
                    FROM sales s JOIN products p ON s.product_id = p.product_id 
                    GROUP BY s.date, p.category ORDER BY s.date ASC
                """, conn)
                conn.close()
                
                if not viz_df.empty:
                    st.line_chart(data=viz_df, x="date", y="revenue_total", color="category")
                else:
                    st.caption("ℹ️ Telemetry partition read successfully, but row output array was empty.")
                
        except Exception as runtime_fault:
            st.error(f"Engine Exception Met: {runtime_fault}")
