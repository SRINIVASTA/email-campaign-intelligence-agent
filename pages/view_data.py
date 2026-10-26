import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Database Inspector", layout="wide")
st.title("🗄️ Web Container Database Inspector")
st.markdown("This view prints the raw records currently seated in the temporary cloud database partition.")

# Target the production workspace database footprint
DB_PATH = os.path.join("data", "mock_data.db")

if os.path.exists(DB_PATH):
    st.success("✅ Connected to `mock_data.db` inside the execution container.")
    
    conn = sqlite3.connect(DB_PATH)
    
    # ⚡ PRODUCTION SNOWFLAKE TABLES ALIGNMENT
    target_tables = [
        "products", 
        "marketing_campaign_metrics", 
        "sales", 
        "social_media", 
        "support_cases"
    ]
    
    # Loop through each table partition and render a separate UI card layout
    for table in target_tables:
        st.write("---")
        st.subheader(f"📋 Table: {table.upper()}")
        try:
            # Extract all raw rows into a tabular pandas framework
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            
            # Display rows as an interactive clean data grid container
            st.dataframe(df, use_container_width=True)
            
            # Print a quick metric tracking summary badge
            st.caption(f"📊 Total record volume inside `{table}`: **{len(df)}** rows loaded.")
            
        except Exception as table_err:
            st.error(f"Failed to scan data from partition partition `{table}`: {table_err}")
            
    conn.close()
else:
    st.error("❌ Database footprint missing. Please navigate back to the main homepage to initialize the workspace layout.")
