import os
import re
import sqlite3
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.semantic_layer import SEMANTIC_MAPPING_LAYER

class EnterpriseCoWorkEngine:
    def __init__(self, db_path: str):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database target missing at path context: {db_path}")
            
        self.db_path = db_path
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b", 
            temperature=0
        )
        
    def _execute_query_to_df(self, sql: str) -> pd.DataFrame:
        """Helper tool to cleanly pull query records into a Pandas DataFrame."""
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(sql, conn)
            return df
        finally:
            conn.close()

    def send_email_tool(self, body_text: str, recipient_email: str = None, subject: str = "Local Engine Agent Operations Audit") -> str:
        """Dispatches HTML alerts via standard SMTP layer client."""
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASSWORD")
        smtp_server = os.environ.get("SMTP_SERVER", "://gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        
        if not recipient_email:
            recipient_email = smtp_user
            
        if not smtp_user or not smtp_pass:
            return "⚠️ Custom Tool Alert: SMTP credentials missing in Environment Settings."

        try:
            html_body = body_text.replace("\n", "<br>").replace("**", "<b>").replace("*", "<i>")
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_body, 'html'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipient_email, msg.as_string())
            server.quit()
            
            return f"✅ Summary report dispatched to {recipient_email}."
        except Exception as smtp_err:
            return f"❌ Custom tool failed: {smtp_err}"

    def calculate_growth_correlation(self) -> dict:
        """Calculates mathematical Pearson correlation (R) on local table structures."""
        sql = """
            SELECT 
                strftime('%m', m.date) as month,
                SUM(m.clicks) as total_clicks,
                SUM(s.mentions) as total_mentions
            FROM marketing_campaign_metrics m
            JOIN social_media s ON strftime('%m', m.date) = strftime('%m', s.date)
                AND m.category = s.category
            WHERE m.category = 'Fitness Wear'
            GROUP BY month
        """
        df = self._execute_query_to_df(sql)
        if len(df) > 1:
            correlation = df['total_clicks'].corr(df['total_mentions'])
        else:
            correlation = 1.0 
            
        return {
            "data": df.to_dict(orient="records"),
            "r_value": round(correlation, 4)
        }

    def detect_critical_anomalies(self) -> list:
        """Scans support transcripts locally to catch manufacturing defects and system failures."""
        sql = "SELECT id, title, product, transcript, date FROM support_cases"
        df = self._execute_query_to_df(sql)
        
        anomalies = []
        for _, row in df.iterrows():
            text = row['transcript'].lower()
            if "tear" in text or "broken" in text or "defect" in text:
                anomalies.append(f"🚨 CRITICAL MANUFACTURING DEFECT found in {row['product']} ({row['id']}): '{row['transcript']}'")
            elif "error" in text or "fail" in text:
                anomalies.append(f"⚠️ LOCAL SERVER RUNTIME BOTTLENECK detected on {row['date']} ({row['id']}): '{row['transcript']}'")
                
        return anomalies

    def execute_analytical_query(self, client_query: str) -> str:
        """Intercepts prompts to run direct local calculations alongside the processing layer."""
        if any(word in client_query.lower() for word in ["email", "send a summary"]):
            data_context = self.execute_analytical_query("Show me the trend of sales by product category across all four quarters of 2025")
            email_status = self.send_email_tool(body_text=data_context, subject="Local Analytics System Report")
            return f"{data_context}\n\n⚙️ **Tool Execution Status:**\n{email_status}"

        anomalies = self.detect_critical_anomalies()
        correlation_results = self.calculate_growth_correlation()
        
        sales_sql = """
            SELECT 
                p.category,
                'Q' || ((cast(strftime('%m', s.date) as integer) - 1) / 3 + 1) as quarter,
                SUM(s.sales_amount) as revenue,
                SUM(s.units_sold) as units
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            GROUP BY p.category, quarter
        """
        sales_df = self._execute_query_to_df(sales_sql)
        
        synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Local Enterprise Marketing Analyst operating inside a Python microservice framework.
Your job is to read the raw local SQLite database matrix, calculated correlations, and detected operational anomalies, then build a scannable executive summary report.
Highlight calculated values accurately without changing them. Ensure clear bold text styling for entities."""),
            ("user", """
Query Request: {query}
Raw Sales Matrix Data:
{sales_data}

Calculated Marketing Correlation Matrix (Clicks vs Social Mentions):
{correlation_data}
Pearson Correlation Coefficient (R): {r_value}

Detected Workspace Operational Anomalies:
{anomaly_data}

Executive Summary Layout Structure:
""")
        ])
        
        synthesis_chain = synthesis_prompt | self.llm | StrOutputParser()
        
        return synthesis_chain.invoke({
            "query": client_query,
            "sales_data": sales_df.to_markdown(index=False),
            "correlation_data": str(correlation_results["data"]),
            "r_value": correlation_results["r_value"],
            "anomaly_data": "\n".join(anomalies) if anomalies else "None detected."
        })
