import os
import re
import sqlite3
import pandas as pd
import smtplib
from datetime import datetime
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

    def send_email_tool(self, body_text: str, recipient_email: str = None, subject: str = "Local Engine Agent Operations Audit", attachment_path: str = None) -> str:
        """Dispatches text alerts with optional document attachments via secure SSL port 465."""
        import streamlit as st
        from email.mime.base import MIMEBase
        from email import encoders
        
        smtp_user = st.secrets.get("SMTP_USER")
        smtp_pass = st.secrets.get("SMTP_PASSWORD")
        smtp_server = st.secrets.get("SMTP_SERVER", "://gmail.com")
        
        if not recipient_email:
            recipient_email = st.secrets.get("REPORT_RECIPIENT", smtp_user)
            
        if not smtp_user or not smtp_pass:
            return "⚠️ Custom Tool Alert: SMTP credentials missing in Streamlit Secrets."

        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user          
            msg['To'] = recipient_email      
            msg['Subject'] = subject
            
            # Attach the main executive overview message
            msg.attach(MIMEText(body_text, 'plain'))
            
            # Handle document attachment processing loops securely
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(attachment_path)}",
                )
                msg.attach(part)
            
            server = smtplib.SMTP_SSL(smtp_server, 465)
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipient_email, msg.as_string())
            server.quit()
            
            return f"✅ Dispatch complete! Report successfully sent to {recipient_email}."
        except Exception as smtp_err:
            return f"❌ Custom tool connection failed with trace info: {str(smtp_err)}"
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

    def run_subscriber_health_audit(self) -> str:
        """New Agentic Workflow: Algorithmic parsing of subscriber matrices, computing open/bounce rates, and rendering structural responsive HTML emails."""
        event_query = "SELECT timestamp, campaign_name, event_type FROM email_event_logs;"
        df_events = self._execute_query_to_df(event_query)
        
        if df_events.empty:
            return "⚠️ Audit aborted: The `email_event_logs` target schema matrix contains no records."
            
        total_sent = len(df_events[df_events['event_type'] == 'SENT'])
        bounces = len(df_events[df_events['event_type'] == 'BOUNCE'])
        unsubscribes = len(df_events[df_events['event_type'] == 'UNSUBSCRIBE'])
        opens = len(df_events[df_events['event_type'] == 'OPEN'])
        
        bounce_rate = (bounces / total_sent) * 100 if total_sent > 0 else 0.0
        open_rate = (opens / total_sent) * 100 if total_sent > 0 else 0.0
        
        campaign_summary = df_events.groupby(['campaign_name', 'event_type']).size().unstack(fill_value=0).reset_index()
        campaign_summary.columns = [col.upper() for col in campaign_summary.columns]

        alert_section = ""
        if bounce_rate > 5.0:
            alert_section = f"""
            <div style="background: #fff7ed; border-left: 4px solid #ea580c; color: #c2410c; padding: 15px; border-radius: 0 6px 6px 0; margin-bottom: 25px; font-size: 14px;">
                <strong>⚠️ CRITICAL INFRASTRUCTURE ALARM:</strong> The detected email infrastructure transmission bounce rate is sitting at <strong>{bounce_rate:.2f}%</strong> (Threshold Limit: 5.0%). Deliverability reputation boundaries are highly threatened.
            </div>
            """

        synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an Enterprise Infrastructure & Data deliverability auditor. Review the metrics summary provided and provide a direct, concise 2-sentence executive advisory action statement."),
            ("user", "System Performance: Total Sent: {sent}, Bounces: {bounces}, Total Unsubscribes: {unsub}, Calculated System Open Ratio: {open_r:.2f}%. Strategy Output:")
        ])
        synthesis_chain = synthesis_prompt | self.llm | StrOutputParser()
        llm_analysis = synthesis_chain.invoke({"sent": total_sent, "bounces": bounces, "unsub": unsubscribes, "open_r": open_rate})

        table_rows_buffer = ""
        for _, row in campaign_summary.iterrows():
            bounce_color = '#dc2626' if row.get('BOUNCE', 0) > 0 else '#334155'
            table_rows_buffer += f"""
            <tr>
                <td style="padding: 12px; font-size: 14px; border-bottom: 1px solid #e2e8f0; color: #334155;"><strong>{row['CAMPAIGN_NAME']}</strong></td>
                <td style="padding: 12px; font-size: 14px; border-bottom: 1px solid #e2e8f0; color: #334155;">{row.get('SENT', 0)}</td>
                <td style="padding: 12px; font-size: 14px; border-bottom: 1px solid #e2e8f0; color: #334155;">{row.get('OPEN', 0)}</td>
                <td style="padding: 12px; font-size: 14px; border-bottom: 1px solid #e2e8f0; color: #334155;">{row.get('CLICK', 0)}</td>
                <td style="padding: 12px; font-size: 14px; border-bottom: 1px solid #e2e8f0; color: #334155; color: {bounce_color}">{row.get('BOUNCE', 0)}</td>
            </tr>
            """

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>Subscriber Deliverability Telemetry</title></head>
        <body style="font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #f4f6f9; color: #333333; margin: 0; padding: 20px;">
            <div style="max-width: 650px; background: #ffffff; margin: 0 auto; border-radius: 8px; border: 1px solid #e1e4e8; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <div style="background: linear-gradient(135deg, #1e293b, #0f172a); padding: 30px 25px; color: #ffffff;">
                    <h1 style="margin: 0; font-size: 22px; font-weight: 600; letter-spacing: -0.5px;">📋 SYSTEM DELIVERABILITY & HYGIENE AUDIT</h1>
                    <p style="margin: 5px 0 0 0; color: #94a3b8; font-size: 14px;">Microservice Diagnostics Pipeline Engine</p>
                </div>
                <div style="padding: 25px;">
                    <div style="display: flex; gap: 15px; margin-bottom: 25px;">
                        <div style="flex: 1; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; text-align: center;">
                            <div style="font-size: 24px; font-weight: bold; color: #0f172a;">{open_rate:.1f}%</div>
                            <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 600;">Avg Open Ratio</div>
                        </div>
                        <div style="flex: 1; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; text-align: center;">
                            <div style="font-size: 24px; font-weight: bold; color: #0f172a;">{bounce_rate:.2f}%</div>
                            <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 600;">Bounce Rate</div>
                        </div>
                        <div style="flex: 1; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; text-align: center;">
                            <div style="font-size: 24px; font-weight: bold; color: #0f172a;">{unsubscribes}</div>
                            <div style="font-size: 11px; color: #64748b; text-transform: uppercase; font-weight: 600;">Total Opt-Outs</div>
                        </div>
                    </div>
                    {alert_section}
                    <h3 style="color: #0f172a; margin-top: 0;">Executive Matrix Summary</h3>
                    <p style="font-size: 14px; line-height: 1.6; color: #334155;">{llm_analysis}</p>
                    <h3 style="color: #0f172a; margin-top: 25px;">Granular Data Footprint</h3>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                        <thead>
                            <tr style="background-color: #f1f5f9;">
                                <th style="text-align: left; padding: 10px 12px; font-size: 12px; text-transform: uppercase; color: #475569; border-bottom: 2px solid #cbd5e1;">Campaign</th>
                                <th style="text-align: left; padding: 10px 12px; font-size: 12px; text-transform: uppercase; color: #475569; border-bottom: 2px solid #cbd5e1;">Sent</th>
                                <th style="text-align: left; padding: 10px 12px; font-size: 12px; text-transform: uppercase; color: #475569; border-bottom: 2px solid #cbd5e1;">Open</th>
                                <th style="text-align: left; padding: 10px 12px; font-size: 12px; text-transform: uppercase; color: #475569; border-bottom: 2px solid #cbd5e1;">Click</th>
                                <th style="text-align: left; padding: 10px 12px; font-size: 12px; text-transform: uppercase; color: #475569; border-bottom: 2px solid #cbd5e1;">Bounce</th>
                            </tr>
                        </thead>
                        <tbody>{table_rows_buffer}</tbody>
                    </table>
                </div>
                <div style="background: #f8fafc; padding: 15px 25px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0;">
                    Confidential Internal Operations Log. Designed for microservice processing frameworks.
                </div>
            </div>
        </body>
        </html>
        """
        
        output_report_path = os.path.join("pages", "subscriber_health_report.html")
        os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
        with open(output_report_path, "w", encoding="utf-8") as f:
            f.write(html_template)
            
        return html_template
    def execute_analytical_query(self, client_query: str) -> str:
        """Programmatically parses prompts, writes native rich layout PDFs for ALL quarters, and transmits attachments."""
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        # 1. Standardize Logic Parsing Parameters Across Global Partition Boundaries
        is_q1 = "four quarters" in client_query.lower() or "q1" in client_query.lower()
        is_q2 = "jackets recently" in client_query.lower() or "q2" in client_query.lower()
        is_q3 = "fitness wear" in client_query.lower() or "q3" in client_query.lower()
        is_q4 = any(word in client_query.lower() for word in ["subscriber", "health", "bounce", "unsub", "q4"])
        prefer_pdf = "[mode: pdf]" in client_query.lower()

        anomalies = self.detect_critical_anomalies()
        correlation_results = self.calculate_growth_correlation()
        
        sales_sql = """
            SELECT p.category, 'Q' || ((cast(strftime('%m', s.date) as integer) - 1) / 3 + 1) as quarter,
                   SUM(s.sales_amount) as revenue, SUM(s.units_sold) as units
            FROM sales s JOIN products p ON s.product_id = p.product_id GROUP BY p.category, quarter
        """
        sales_df = self._execute_query_to_df(sales_sql)
        
        subscriber_metrics = ""
        if is_q4:
            self.run_subscriber_health_audit() 
            event_sql = "SELECT campaign_name, event_type, COUNT(*) as volume FROM email_event_logs GROUP BY campaign_name, event_type"
            subscriber_metrics = self._execute_query_to_df(event_sql).to_markdown(index=False)

        # 2. Prompt Synthesis Engine Layer
        synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an Enterprise Operations Auditor. Review the workspace data matrix parameters and build a concise executive summary report. Do NOT include markdown markdown tables in your text narrative; provide clear text data bullet frameworks instead."),
            ("user", "Query: {query}\nSales: {sales_data}\nAnomalies: {anomaly_data}\nSubscribers: {subscriber_data}\nStrategy Output:")
        ])
        synthesis_chain = synthesis_prompt | self.llm | StrOutputParser()
        report_output = synthesis_chain.invoke({
            "query": client_query, "sales_data": sales_df.to_markdown(index=False),
            "anomaly_data": "\n".join(anomalies) if anomalies else "None.",
            "subscriber_data": subscriber_metrics if subscriber_metrics else "N/A"
        })

        # -------------------------------------------------------------
        # 3. UNIVERSAL NATIVE RICH PDF LAYOUT GENERATOR FOR ALL QUARTERS
        # -------------------------------------------------------------
        pdf_path = None
        if prefer_pdf:
            pdf_dir = "pages"
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_path = os.path.join(pdf_dir, "executive_operations_report.pdf")
            
            doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor("#0f172a"), spaceAfter=15)
            body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#334155"), spaceAfter=12)
            
            # Universal Header Mapping Block
            report_title = "📋 ENTERPRISE EXECUTIVE OPERATIONS AUDIT REPORT"
            if is_q1: report_title = "📊 Q1 REPORT - 2025 REVENUE & SALES TRENDS"
            elif is_q2: report_title = "⚠️ Q2 REPORT - PRODUCT FRICTION & QUALITY RISK LOG"
            elif is_q3: report_title = "📈 Q3 REPORT - DIGITAL MARKETING CHANNEL CORRELATION RUN"
            elif is_q4: report_title = "🛡️ Q4 REPORT - SUBSCRIBER HEALTH & DELIVERABILITY MATRIX"

            story.append(Paragraph(report_title, title_style))
            story.append(Paragraph(f"<b>Generated Context:</b> Enterprise Analytics Pipeline • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
            story.append(Spacer(1, 10))
            
            story.append(Paragraph("<b>Executive Summary Strategy Analysis:</b>", ParagraphStyle('Sub', parent=styles['Heading3'], spaceAfter=5)))
            
            # Text Sanitize Pipeline Elements
            clean_text = report_output.replace("<br>", "<br/>").replace("&", "&amp;")
            clean_text = re.sub(r'\|.*\|', '', clean_text)
            
            for text_chunk in clean_text.split('\n'):
                if text_chunk.strip():
                    story.append(Paragraph(text_chunk.strip(), body_style))
            
            story.append(Spacer(1, 10))
            
            # Dynamic Table Injection Mapping Module based on Target Query Area
            table_df = pd.DataFrame()
            if is_q1 or is_q3:
                table_df = sales_df
            elif is_q2:
                table_df = self._execute_query_to_df("SELECT id, title, product, date FROM support_cases")
            elif is_q4:
                table_df = self._execute_query_to_df("SELECT campaign_name, event_type, COUNT(*) as volume FROM email_event_logs GROUP BY campaign_name, event_type")
                
            if not table_df.empty:
                table_data = [[Paragraph(f"<b>{str(col).upper()}</b>", body_style) for col in table_df.columns]]
                for _, row in table_df.iterrows():
                    table_data.append([Paragraph(str(val), body_style) for val in row.values])
                
                perf_table = Table(table_data)
                perf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
                    ('BOTTOMPADDING', (0,0), (-1,0), 6),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ]))
                story.append(Paragraph("<b>Granular Audit Performance Data:</b>", ParagraphStyle('Sub2', parent=styles['Heading3'], spaceAfter=5)))
                story.append(perf_table)
            
            doc.build(story)

        # -------------------------------------------------------------
        # 4. SECURE ROUTING LAYER WITH DYNAMIC ATTACHMENT SWITCHING
        # -------------------------------------------------------------
        subject_map = {
            "q1": ("📊 Q1 Executive Operations Audit - 2025 Sales Trends", "Sales"),
            "q2": ("⚠️ Q2 Executive Operations Audit - Product Quality Log", "Quality"),
            "q3": ("📈 Q3 Executive Operations Audit - Channel Correlation Run", "Marketing"),
            "q4": ("📋 Q4 Executive Operations Audit - Subscriber Health", "Hygiene")
        }
        
        current_key = "q1"
        if is_q2: current_key = "q2"
        elif is_q3: current_key = "q3"
        elif is_q4: current_key = "q4"
        
        base_subject, doc_name = subject_map[current_key]
        subject = f"{base_subject} (Rich PDF)" if prefer_pdf else f"{base_subject} (Text Sync)"
        attachment = pdf_path if prefer_pdf else None
        
        email_status = self.send_email_tool(body_text=report_output, subject=subject, attachment_path=attachment)
        report_output += f"\n\n⚙️ **Automated Pipeline Action:**\n{email_status}"
        
        if prefer_pdf:
            report_output += f"\n\n*(Note: Your visual report has been generated in your workspace path environment)*"
            
        return report_output
