"""Query explainer that converts SQL to natural language using Ollama."""
from typing import Dict, Any
from langchain_community.llms import Ollama
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("core.explainer")


class QueryExplainer:
    """Explains SQL queries in natural language using local LLM."""
    
    def __init__(self):
        self.llm = None
        self._initialize_ollama()
        logger.info("Query Explainer initialized with Ollama")
    
    def _initialize_ollama(self):
        """Initialize Ollama LLM."""
        try:
            self.llm = Ollama(
                model=settings.llm_model,
                base_url=settings.ollama_base_url,
                temperature=0.3,
            )
            logger.info(f"Ollama initialized for explainer")
        
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            raise
    
    def explain(self, sql_query: str) -> Dict[str, Any]:
        """
        Explain a SQL query in natural language.
        
        Args:
            sql_query: SQL query to explain
        
        Returns:
            Dictionary with explanation details
        """
        logger.info("Explaining SQL query")
        logger.debug(f"Query: {sql_query[:200]}...")
        
        try:
            prompt = self._build_explanation_prompt(sql_query)
            
            logger.info("Calling Ollama for explanation...")
            response = self.llm.invoke(prompt)
            
            logger.info("Explanation generated successfully")
            
            return {
                "explanation": response.strip(),
                "query": sql_query
            }
        
        except Exception as e:
            logger.error(f"Failed to explain query: {e}")
            raise
    
    def _build_explanation_prompt(self, sql_query: str) -> str:
        """Build prompt for query explanation."""
        
        prompt = f"""You are an expert SQL teacher. Explain the following SQL query in simple, clear language.

SQL QUERY:
```sql
{sql_query}
```

Provide a step-by-step explanation that includes:
1. What data is being retrieved
2. From which tables
3. What conditions/filters are applied
4. How tables are joined (if applicable)
5. Any aggregations or grouping
6. How results are sorted/limited

Make it easy to understand for someone learning SQL.

EXPLANATION:"""

        return prompt
