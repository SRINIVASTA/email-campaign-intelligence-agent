import os
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from config.semantic_layer import SEMANTIC_MAPPING_LAYER

class EnterpriseCoWorkEngine:
    def __init__(self, db_path: str):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database target missing at path context: {db_path}")
            
        # Bind connection to local repository file footprint
        self.db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        
        # ⚡ OPENAI OPEN-WEIGHT PRODUCTION LAYER:
        # Initialized with 'openai/gpt-oss-120b' hosted natively on Groq.
        # This leverages 120B parameter reasoning depth for structured SQL extraction blocks.
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b", 
            temperature=0
        )
        
        # Compile agent logic architecture executor 
        self.agent_executor = create_sql_agent(
            self.llm, 
            db=self.db, 
            verbose=True, 
            handle_parsing_errors=True
        )
        
    def execute_analytical_query(self, client_query: str) -> str:
        # Build prompt injection framework wrapping context definitions
        structured_context_packet = f"{SEMANTIC_MAPPING_LAYER}\n\nUser Operational Instruction: {client_query}"
        return self.agent_executor.run(structured_context_packet)
