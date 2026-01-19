"""Query validator with multi-layer validation."""
from typing import List, Dict, Tuple
import re
from utils.logger import get_logger
from database.schema_manager import SchemaManager
from config.settings import settings

logger = get_logger("core.validator")


class QueryValidator:
    """Validates SQL queries before execution."""
    
    # Dangerous SQL keywords that should be blocked
    DANGEROUS_KEYWORDS = [
        "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE"
    ]
    
    def __init__(self, schema_manager: SchemaManager):
        self.schema_manager = schema_manager
        logger.info("Query Validator initialized")
    
    def validate(self, sql_query: str) -> Tuple[bool, List[str]]:
        """
        Validate a SQL query through multiple layers.
        
        Args:
            sql_query: SQL query to validate
        
        Returns:
            Tuple of (is_valid, warnings)
        """
        logger.info("Validating SQL query")
        logger.debug(f"Query: {sql_query[:200]}...")
        
        warnings = []
        
        try:
            # Layer 1: Syntax validation
            if not self._validate_syntax(sql_query):
                logger.error("Syntax validation failed")
                return False, ["Invalid SQL syntax"]
            logger.debug("✓ Syntax validation passed")
            
            # Layer 2: Safety check
            safety_warnings = self._validate_safety(sql_query)
            if safety_warnings:
                if not settings.enable_dangerous_queries:
                    logger.error(f"Safety validation failed: {safety_warnings}")
                    return False, safety_warnings
                else:
                    warnings.extend(safety_warnings)
                    logger.warning(f"Safety warnings (allowed): {safety_warnings}")
            logger.debug("✓ Safety validation passed")
            
            # Layer 3: Schema validation
            schema_warnings = self._validate_schema(sql_query)
            if schema_warnings:
                warnings.extend(schema_warnings)
                logger.warning(f"Schema warnings: {schema_warnings}")
            logger.debug("✓ Schema validation passed")
            
            # Layer 4: Performance estimation
            perf_warnings = self._estimate_performance(sql_query)
            if perf_warnings:
                warnings.extend(perf_warnings)
                logger.info(f"Performance warnings: {perf_warnings}")
            logger.debug("✓ Performance estimation completed")
            
            logger.info(f"Validation successful with {len(warnings)} warnings")
            return True, warnings
        
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, [f"Validation error: {str(e)}"]
    
    def _validate_syntax(self, sql_query: str) -> bool:
        """Basic syntax validation."""
        # Check if query is empty
        if not sql_query or not sql_query.strip():
            logger.debug("Query is empty")
            return False
        
        # Check for balanced parentheses
        if sql_query.count("(") != sql_query.count(")"):
            logger.debug("Unbalanced parentheses")
            return False
        
        # Check if it starts with a valid SQL keyword
        first_word = sql_query.strip().split()[0].upper()
        valid_keywords = ["SELECT", "WITH", "EXPLAIN"]
        
        if not settings.enable_dangerous_queries:
            if first_word not in valid_keywords:
                logger.debug(f"Query starts with invalid keyword: {first_word}")
                return False
        
        return True
    
    def _validate_safety(self, sql_query: str) -> List[str]:
        """Check for dangerous operations."""
        warnings = []
        query_upper = sql_query.upper()
        
        for keyword in self.DANGEROUS_KEYWORDS:
            if re.search(rf'\b{keyword}\b', query_upper):
                warnings.append(f"Dangerous operation detected: {keyword}")
                logger.warning(f"Dangerous keyword found: {keyword}")
        
        return warnings
    
    def _validate_schema(self, sql_query: str) -> List[str]:
        """Validate table and column references."""
        warnings = []
        
        try:
            # Get all valid table names
            valid_tables = set(self.schema_manager.get_all_tables())
            
            # Extract table names from query (simple regex approach)
            # This is a simplified version; a full parser would be more robust
            table_pattern = r'\bFROM\s+(\w+)|\bJOIN\s+(\w+)'
            matches = re.findall(table_pattern, sql_query, re.IGNORECASE)
            
            referenced_tables = set()
            for match in matches:
                for table in match:
                    if table:
                        referenced_tables.add(table.lower())
            
            # Check if referenced tables exist
            for table in referenced_tables:
                if table not in [t.lower() for t in valid_tables]:
                    warnings.append(f"Table '{table}' not found in schema")
                    logger.warning(f"Unknown table referenced: {table}")
        
        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            warnings.append(f"Could not validate schema: {str(e)}")
        
        return warnings
    
    def _estimate_performance(self, sql_query: str) -> List[str]:
        """Estimate query performance and provide warnings."""
        warnings = []
        query_upper = sql_query.upper()
        
        # Check for SELECT * without LIMIT
        if "SELECT *" in query_upper and "LIMIT" not in query_upper:
            warnings.append("Query uses SELECT * without LIMIT - may return many rows")
            logger.info("Performance warning: SELECT * without LIMIT")
        
        # Check for multiple JOINs
        join_count = query_upper.count("JOIN")
        if join_count > 3:
            warnings.append(f"Query has {join_count} JOINs - may be slow")
            logger.info(f"Performance warning: {join_count} JOINs")
        
        # Check for subqueries
        if "SELECT" in query_upper[10:]:  # Skip first SELECT
            warnings.append("Query contains subqueries - verify performance")
            logger.info("Performance warning: Subqueries detected")
        
        return warnings
