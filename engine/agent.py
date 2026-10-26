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
            
        # Bind database utility instance
        self.db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        
        # Initialize open-weights inference runtime
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b", 
            temperature=0
        )
        
        # ⚡ PRODUCTION LCEL CHAIN CONSTRUCTION:
        # We completely bypass the tool-calling framework, using a pure text prompt instead.
        self.sql_generation_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""{SEMANTIC_MAPPING_LAYER}
You are an expert SQL generation engine. Given an operational instruction, write a clean, optimized SQLite query that will extract the required metrics.
Return ONLY valid, executable SQL code. Do not include markdown formatting, backticks (```sql), or conversational text.

Database Schema Information:
{self.db.get_table_info()}
"""),
            ("user", "User Operational Instruction: {client_query}")
        ])
        
        # Compile standard text pipeline execution path
        self.sql_generator_chain = self.sql_generation_prompt | self.llm | StrOutputParser()
        
    def _clean_sql(self, sql_text: str) -> str:
        """Removes potential LLM markdown wrappers like ```sql or trailing characters."""
        clean = sql_text.strip()
        clean = re.sub(r"^```sql\s*", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"^```\s*", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\s*```$", "", clean)
        return clean.strip()

    def execute_analytical_query(self, client_query: str) -> str:
        try:
            # Step 1: Generate clean text SQL query string from model
            raw_sql = self.sql_generator_chain.invoke({"client_query": client_query})
            executable_sql = self._clean_sql(raw_sql)
            
            # Step 2: Execute generated query directly against SQLite partition context
            query_results = self.db.run(executable_sql)
            
            # Step 3: Package raw data observations back into a legible narrative summary
            synthesis_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an Enterprise AI Marketing Analyst. Summarize the database findings layout for the user clearly. State the final numbers and facts."),
                ("user", f"Original Query: {client_query}\nExecuted SQL: {executable_sql}\nDatabase Output: {query_results}\n\nAnalytical Executive Summary:")
            ])
            
            synthesis_chain = synthesis_prompt | self.llm | StrOutputParser()
            return synthesis_chain.invoke({})
            
        except Exception as query_fault:
            return f"Operational Engine failure during execution pipeline logic: {query_fault}\nGenerated Expression String attempted: {executable_sql if 'executable_sql' in locals() else 'None'}"
