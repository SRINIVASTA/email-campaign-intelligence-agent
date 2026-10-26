import streamlit as st
import sqlite3
import pandas as pd
import os

st.title("🗄️ Web Container Database Inspector")

DB_PATH = os.path.join("data", "mock_data.db")

if os.path.exists(DB_PATH):
    st.success(f"✅ Found `mock_data.db` inside the Streamlit cloud container!")
    
    conn = sqlite3.connect(DB_PATH)
    target_tables = ["email_campaigns", "campaign_metrics", "revenue_attribution", "recipient_feedback"]
    
    for table in target_tables:
        st.subheader(r"📋 Table: {table}")
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Could not read table: {e}")
    conn.close()
else:
    st.error("❌ Database file not found in web container path context yet.")
