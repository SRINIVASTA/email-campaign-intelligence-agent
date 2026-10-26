import os
import re
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
        
        # Deploy high-throughput open-weights processing layer mapping
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b", 
            temperature=0
        )
        
        self.sql_generation_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""{SEMANTIC_MAPPING_LAYER}
You are an expert SQL generation engine mapping instructions onto a Snowflake mirror environment.
Given an instruction, write a clean, case-insensitive SQLite query that will extract the required metrics.
Return ONLY valid, executable SQL code. Do not include markdown formatting or backticks.

Active Tables Layout:
{self.db.get_table_info()}
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

    def execute_analytical_query(self, client_query: str) -> str:
        try:
            raw_sql = self.sql_generator_chain.invoke({"client_query": client_query})
            executable_sql = self._clean_sql(raw_sql)
            query_results = self.db.run(executable_sql)
            
            synthesis_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an Enterprise AI Marketing Analyst acting as a Snowflake CoWork agent. Summarize the findings clearly, showing final metrics and recommendations."),
                ("user", f"Query: {client_query}\nExecuted SQL: {executable_sql}\nData Output: {query_results}\n\nExecutive Summary Layout:")
            ])
            
            synthesis_chain = synthesis_prompt | self.llm | StrOutputParser()
            return synthesis_chain.invoke({})
            
        except Exception as query_fault:
            return f"Operational Engine failure during execution pipeline logic: {query_fault}"
