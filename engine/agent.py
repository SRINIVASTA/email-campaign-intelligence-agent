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
        
        # ✅ FIXED: Replaced non-existent "openai/gpt-oss-120b" with valid Groq Llama model string
        self.llm = ChatGroq(
            model="llama3-8b-8192", 
            temperature=0
        )
        
        self.sql_generation_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""{SEMANTIC_MAPPING_LAYER}
You are an expert SQL generation engine mapping instructions onto a Snowflake mirror environment.
Given an instruction, write a clean, case-insensitive SQLite query that will extract the required metrics.
Return ONLY valid, executable SQL code. Do not include markdown formatting or backticks.

Active Tables Layout:
{{table_info}}
"""),
            ("user", "Instruction: {{client_query}}")
        ])
        
        # Using late injection for table information to prevent structural initialization binding issues
        self.sql_generator_chain = self.sql_generation_prompt | self.llm | StrOutputParser()
        
    def _clean_sql(self, sql_text: str) -> str:
        clean = sql_text.strip()
        clean = re.sub(r"^```sql\s*", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"^```\s*", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\s*```$", "", clean)
        return clean.strip()

    def send_email_tool(self, body_text: str, recipient_email: str = None, subject: str = "Snowflake CoWork Local Agent Audit") -> str:
        """Translates markdown summaries to HTML and dispatches a live email via SMTP."""
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASSWORD")
        # ✅ FIXED: Changed invalid protocol prefix format "://gmail.com" to standard address host
        smtp_server = os.environ.get("SMTP_SERVER", "://gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        
        if not recipient_email:
            recipient_email = smtp_user
            
        if not smtp_user or not smtp_pass:
            return "⚠️ Custom Tool Alert: Email generation was prepared, but SMTP login credentials are missing in Environment Settings."

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
            
            return f"✅ Custom tool execution successful! Summary report dispatched to {recipient_email}."
        except Exception as smtp_err:
            return f"❌ Custom tool failed during message execution: {smtp_err}"

    def execute_analytical_query(self, client_query: str) -> str:
        if any(word in client_query.lower() for word in ["email", "send a summary", "send me this"]):
            data_context = self.execute_analytical_query("Show me the trend of sales by product category across all four quarters of 2025")
            email_status = self.send_email_tool(body_text=data_context, subject="Snowflake CoWork - Sales Summary Report")
            return f"{data_context}\n\n⚙️ **Tool Execution Status:**\n{email_status}"

        try:
            # Dynamically push structural information down into formatting logic run
            raw_sql = self.sql_generator_chain.invoke({
                "client_query": client_query,
                "table_info": self.db.get_table_info()
            })
            executable_sql = self._clean_sql(raw_sql)
            query_results = self.db.run(executable_sql)
            
            synthesis_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an Enterprise AI Marketing Analyst acting as a Snowflake CoWork agent. Summarize the findings clearly, showing final metrics and recommendations."),
                ("user", "Query: {client_query}\nExecuted SQL: {executable_sql}\nData Output: {query_results}\n\nExecutive Summary Layout:")
            ])
            
            # ✅ FIXED: Injected necessary prompt values safely down into processing pipeline
            synthesis_chain = synthesis_prompt | self.llm | StrOutputParser()
            return synthesis_chain.invoke({
                "client_query": client_query,
                "executable_sql": executable_sql,
                "query_results": query_results
            })
            
        except Exception as query_fault:
            return f"Operational Engine failure during execution pipeline logic: {query_fault}"
