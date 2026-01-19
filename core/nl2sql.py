"""Natural Language to SQL converter using Ollama (local LLM)."""
from typing import Optional, Dict, Any
from langchain_community.llms import Ollama
from config.settings import settings
from utils.logger import get_logger
from database.schema_manager import SchemaManager

logger = get_logger("core.nl2sql")


class NL2SQLConverter:
    """Converts natural language queries to SQL using local LLM via Ollama."""
    
    def __init__(self, schema_manager: SchemaManager, rag_retriever=None):
        self.schema_manager = schema_manager
        self.rag_retriever = rag_retriever
        self.llm = None
        self._initialize_ollama()
        
        if rag_retriever:
            logger.info("NL2SQL Converter initialized with RAG retriever")
        else:
            logger.info("NL2SQL Converter initialized without RAG (using full schema)")
    
    def _initialize_ollama(self):
        """Initialize Ollama LLM."""
        try:
            self.llm = Ollama(
                model=settings.llm_model,
                base_url=settings.ollama_base_url,
                temperature=settings.llm_temperature,
            )
            logger.info(f"Ollama initialized with model: {settings.llm_model}")
            logger.info(f"Ollama URL: {settings.ollama_base_url}")
        
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            logger.error("Make sure Ollama is running: ollama serve")
            logger.error(f"And the model is installed: ollama pull {settings.llm_model}")
            raise
    
    def convert(self, natural_language_query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert natural language to SQL query.
        
        Args:
            natural_language_query: User's question in natural language
            context: Optional additional context
        
        Returns:
            Dictionary with 'sql', 'explanation', and 'confidence'
        """
        logger.info(f"Converting NL query: {natural_language_query}")
        
        try:
            # Get schema context
            schema_context = self._get_schema_context(natural_language_query)
            logger.debug(f"Schema context retrieved: {len(schema_context)} characters")
            
            # Build prompt
            prompt = self._build_prompt(natural_language_query, schema_context, context)
            logger.debug("Prompt built successfully")
            
            # Generate SQL using Ollama
            logger.info("Calling Ollama API...")
            response = self.llm.invoke(prompt)
            
            logger.info("Ollama API response received")
            logger.debug(f"Response text length: {len(response)} characters")
            
            # Parse response
            result = self._parse_response(response)
            logger.info(f"SQL generated successfully: {result['sql'][:100]}...")
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to convert NL to SQL: {e}")
            raise
    
    def _get_schema_context(self, query: str) -> str:
        """
        Get relevant schema context for the query.
        Uses RAG retriever if available, otherwise includes all tables.
        """
        logger.debug("Retrieving schema context")
        
        # Try to use RAG retriever if available and enabled
        if self.rag_retriever and settings.rag_enabled:
            try:
                logger.info("Using RAG to retrieve relevant tables")
                tables = self.rag_retriever.retrieve(query)
                
                if not tables:
                    logger.warning("RAG returned no tables, falling back to all tables")
                    tables = self.schema_manager.get_all_tables()
                else:
                    logger.info(f"RAG retrieved {len(tables)} relevant tables: {', '.join(tables)}")
            except Exception as e:
                logger.error(f"RAG retrieval failed: {e}, falling back to all tables")
                tables = self.schema_manager.get_all_tables()
        else:
            # Use all tables if RAG is not available
            logger.debug("RAG not available, using all tables")
            tables = self.schema_manager.get_all_tables()
        
        # Build context string
        context_parts = []
        
        for table_name in tables:
            table_info = self.schema_manager.get_table_info(table_name, include_samples=True)
            
            # Table header
            context_parts.append(f"\nTable: {table_name} ({table_info.row_count} rows)")
            
            # Columns
            context_parts.append("Columns:")
            for col in table_info.columns:
                pk = " [PRIMARY KEY]" if col.primary_key else ""
                null = " NULL" if col.nullable else " NOT NULL"
                context_parts.append(f"  - {col.name}: {col.type}{null}{pk}")
            
            # Foreign keys
            fks = self.schema_manager.get_foreign_keys(table_name)
            if fks:
                context_parts.append("Foreign Keys:")
                for fk in fks:
                    context_parts.append(
                        f"  - {fk['column']} -> {fk['referenced_table']}.{fk['referenced_column']}"
                    )
            
            # Sample data (only first 2 rows to save tokens)
            if table_info.sample_data:
                context_parts.append("Sample Data (first 2 rows):")
                for i, row in enumerate(table_info.sample_data[:2], 1):
                    context_parts.append(f"  Row {i}: {dict(row)}")
        
        context = "\n".join(context_parts)
        logger.debug(f"Schema context size: {len(context)} characters")
        return context
    
    def _build_prompt(self, query: str, schema_context: str, additional_context: Optional[str] = None) -> str:
        """Build the prompt for Ollama."""
        
        prompt = f"""You are an expert SQL query generator. Convert the natural language question into a valid SQLite query.

DATABASE SCHEMA:
{schema_context}

IMPORTANT RULES:
1. Generate ONLY valid SQLite syntax
2. Use proper table and column names from the schema
3. Include appropriate JOINs when querying multiple tables
4. Use aliases for better readability
5. Add LIMIT clause for queries that might return many rows
6. Return results in a logical order (use ORDER BY)
7. Use aggregate functions (COUNT, SUM, AVG, etc.) when appropriate

USER QUESTION:
{query}

RESPONSE FORMAT:
Provide your response in the following format:

SQL:
```sql
[Your SQL query here]
```

EXPLANATION:
[Brief explanation of what the query does and why you structured it this way]

CONFIDENCE:
[High/Medium/Low - your confidence in this query]

Now generate the SQL query:"""

        if additional_context:
            prompt += f"\n\nADDITIONAL CONTEXT:\n{additional_context}"
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Ollama's response to extract SQL, explanation, and confidence."""
        
        result = {
            "sql": "",
            "explanation": "",
            "confidence": "medium"
        }
        
        try:
            # Extract SQL
            if "```sql" in response_text:
                sql_start = response_text.find("```sql") + 6
                sql_end = response_text.find("```", sql_start)
                result["sql"] = response_text[sql_start:sql_end].strip()
            elif "SQL:" in response_text:
                # Fallback: look for SQL: marker
                lines = response_text.split("\n")
                sql_lines = []
                in_sql = False
                for line in lines:
                    if "SQL:" in line:
                        in_sql = True
                        continue
                    if in_sql:
                        if "EXPLANATION:" in line or "CONFIDENCE:" in line:
                            break
                        if line.strip() and not line.startswith("```"):
                            sql_lines.append(line)
                result["sql"] = "\n".join(sql_lines).strip()
            
            # Extract explanation
            if "EXPLANATION:" in response_text:
                expl_start = response_text.find("EXPLANATION:") + 12
                expl_end = response_text.find("CONFIDENCE:", expl_start)
                if expl_end == -1:
                    expl_end = len(response_text)
                result["explanation"] = response_text[expl_start:expl_end].strip()
            
            # Extract confidence
            if "CONFIDENCE:" in response_text:
                conf_start = response_text.find("CONFIDENCE:") + 11
                conf_text = response_text[conf_start:].strip().lower()
                if "high" in conf_text:
                    result["confidence"] = "high"
                elif "low" in conf_text:
                    result["confidence"] = "low"
                else:
                    result["confidence"] = "medium"
            
            # If SQL is still empty, try to extract any SELECT statement
            if not result["sql"] and "SELECT" in response_text.upper():
                # Find the first SELECT and try to extract the query
                select_start = response_text.upper().find("SELECT")
                # Find the end (look for semicolon or double newline)
                select_text = response_text[select_start:]
                if ";" in select_text:
                    result["sql"] = select_text[:select_text.find(";") + 1].strip()
                else:
                    # Take until double newline or end
                    lines = select_text.split("\n")
                    sql_lines = []
                    for line in lines:
                        if line.strip():
                            sql_lines.append(line)
                        elif sql_lines:  # Empty line after we've started collecting
                            break
                    result["sql"] = "\n".join(sql_lines).strip()
        
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            # Last resort: use the whole response as SQL
            result["sql"] = response_text.strip()
        
        return result
