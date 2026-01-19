"""Error corrector for SQL queries using Ollama."""
from typing import Dict, Any
from langchain_community.llms import Ollama
from config.settings import settings
from utils.logger import get_logger
from database.schema_manager import SchemaManager

logger = get_logger("core.error_corrector")


class ErrorCorrector:
    """Automatically corrects common SQL errors using local LLM."""
    
    def __init__(self, schema_manager: SchemaManager):
        self.schema_manager = schema_manager
        self.llm = None
        self._initialize_ollama()
        logger.info("Error Corrector initialized with Ollama")
    
    def _initialize_ollama(self):
        """Initialize Ollama LLM."""
        try:
            self.llm = Ollama(
                model=settings.llm_model,
                base_url=settings.ollama_base_url,
                temperature=0.2,
            )
            logger.info("Ollama initialized for error correction")
        
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            raise
    
    def correct(self, sql_query: str, error_message: str) -> Dict[str, Any]:
        """
        Attempt to correct a SQL query that produced an error.
        
        Args:
            sql_query: The SQL query that failed
            error_message: The error message from the database
        
        Returns:
            Dictionary with corrected query and explanation
        """
        logger.info("Attempting to correct SQL error")
        logger.debug(f"Original query: {sql_query[:200]}...")
        logger.debug(f"Error: {error_message}")
        
        try:
            # Get schema context
            schema_context = self._get_schema_summary()
            
            # Build correction prompt
            prompt = self._build_correction_prompt(sql_query, error_message, schema_context)
            
            logger.info("Calling Ollama for error correction...")
            response = self.llm.invoke(prompt)
            
            logger.info("Correction suggestion received")
            
            # Parse response
            corrected = self._parse_correction_response(response)
            
            logger.info(f"Corrected query: {corrected['sql'][:100]}...")
            
            return corrected
        
        except Exception as e:
            logger.error(f"Failed to correct error: {e}")
            raise
    
    def _get_schema_summary(self) -> str:
        """Get a summary of the database schema."""
        tables = self.schema_manager.get_all_tables()
        summary_parts = ["Available tables and columns:\n"]
        
        for table_name in tables:
            table_info = self.schema_manager.get_table_info(table_name, include_samples=False)
            columns = [col.name for col in table_info.columns]
            summary_parts.append(f"- {table_name}: {', '.join(columns)}")
        
        return "\n".join(summary_parts)
    
    def _build_correction_prompt(self, sql_query: str, error: str, schema: str) -> str:
        """Build prompt for error correction."""
        
        prompt = f"""You are an expert SQL debugger. A SQL query has failed with an error. Your job is to fix it.

DATABASE SCHEMA:
{schema}

FAILED QUERY:
```sql
{sql_query}
```

ERROR MESSAGE:
{error}

Analyze the error and provide a corrected version of the query.

RESPONSE FORMAT:
CORRECTED SQL:
```sql
[Your corrected SQL query here]
```

EXPLANATION:
[Explain what was wrong and how you fixed it]

Now provide the correction:"""

        return prompt
    
    def _parse_correction_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the correction response."""
        
        result = {
            "sql": "",
            "explanation": "",
            "success": False
        }
        
        try:
            # Extract corrected SQL
            if "```sql" in response_text:
                sql_start = response_text.find("```sql") + 6
                sql_end = response_text.find("```", sql_start)
                result["sql"] = response_text[sql_start:sql_end].strip()
                result["success"] = True
            
            # Extract explanation
            if "EXPLANATION:" in response_text:
                expl_start = response_text.find("EXPLANATION:") + 12
                result["explanation"] = response_text[expl_start:].strip()
            elif result["sql"]:
                # If we found SQL but no explicit explanation, use the rest
                result["explanation"] = "Query has been corrected based on the error message."
        
        except Exception as e:
            logger.error(f"Error parsing correction response: {e}")
        
        return result
