import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.semantic_layer import SEMANTIC_MAPPING_LAYER

class EnterpriseCoWorkEngine:
    def __init__(self, db_path: str):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database target missing at path context: {db_path}")
            
        self.db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b", 
            temperature=0
        )
        
        # ✅ FIXED: Hardcoded exact SQLite schemas so the model maps them correctly instead of returning "SELECT 1;"
        self.sql_generation_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""{SEMANTIC_MAPPING_LAYER}
You are an expert SQL generation engine mapping instructions onto a local SQLite database environment.
Return ONLY valid, executable, raw SQLite code. Do not include markdown blocks, backticks, conversational filler, or explanations. 

CRITICAL SCHEMA MATCHING INSTRUCTIONS:
- Do NOT use Snowflake functions like DATE_TRUNC, DATE_PART, or YEAR.
- To filter by year 2025, use: strftime('%Y', date) = '2025' or date LIKE '2025-%'
- To extract a quarter, use: 'Q' || ((strftime('%m', date) - 1) / 3 + 1)

Use ONLY these verified tables and columns:
1. Table `products`: columns: [product_id INTEGER, product_name TEXT, category TEXT]
2. Table `sales`: columns: [date TEXT, region TEXT, product_id INTEGER, units_sold INTEGER, sales_amount REAL]
3. Table `marketing_campaign_metrics`: columns: [date TEXT, category TEXT, campaign_name TEXT, impressions INTEGER, clicks INTEGER]
4. Table `social_media`: columns: [date TEXT, category TEXT, platform TEXT, influencer TEXT, mentions INTEGER]
5. Table `support_cases`: columns: [id TEXT, title TEXT, product TEXT, transcript TEXT, date TEXT]

If you fail to understand the prompt, output: SELECT s.date, p.category, s.sales_amount FROM sales s JOIN products p ON s.product_id = p.product_id;
"""),
            ("user", "Instruction: {client_query}")
        ])
        
        self.sql_generator_chain = self.sql_generation_prompt | self.llm | StrOutputParser()
        
    def _clean_sql(self, sql_text: str) -> str:
        clean = sql_text.strip()
        clean = re.sub(r"^```sql\s*", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"^```\s*", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\s*```$", "", clean)
        return clean.strip()

    def send_email_tool(self, body_text: str, recipient_email: str = None, subject: str = "Snowflake CoWork Local Agent Audit") -> str:
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASSWORD")
        smtp_server = os.environ.get("SMTP_SERVER", "://gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        
        if not recipient_email:
            recipient_email = smtp_user
            
        if not smtp_user or not smtp_pass:
            return "⚠️ Custom Tool Alert: SMTP credentials missing."

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
            
            return f"✅ Report sent to {recipient_email}."
        except Exception as smtp_err:
            return f"❌ Custom tool failed: {smtp_err}"

    def execute_analytical_query(self, client_query: str) -> str:
        if any(word in client_query.lower() for word in ["email", "send a summary"]):
            data_context = self.execute_analytical_query("Show me the trend of sales by product category across all four quarters of 2025")
            email_status = self.send_email_tool(body_text=data_context, subject="Snowflake CoWork - Sales Summary Report")
            return f"{data_context}\n\n⚙️ **Tool Execution Status:**\n{email_status}"

        try:
            raw_sql = self.sql_generator_chain.invoke({"client_query": client_query})
            executable_sql = self._clean_sql(raw_sql)
            query_results = self.db.run(executable_sql)
            
            synthesis_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an Enterprise AI Marketing Analyst acting as a Snowflake CoWork agent. Summarize the findings clearly, showing final metrics and recommendations based on provided query results."),
                ("user", f"Query: {client_query}\nExecuted SQL: {executable_sql}\nData Output: {query_results}\n\nExecutive Summary Layout:")
            ])
            
            synthesis_chain = synthesis_prompt | self.llm | StrOutputParser()
            return synthesis_chain.invoke({})
            
        except Exception as query_fault:
            return f"Operational Engine failure during execution pipeline logic: {query_fault}"
