"""Database connection manager with connection pooling."""
import sqlite3
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
from pathlib import Path
from utils.logger import get_logger

logger = get_logger("database.connection")


class DatabaseConnection:
    """Manages database connections with proper error handling."""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        self.connection: Optional[sqlite3.Connection] = None
        logger.info(f"Database connection manager initialized for: {database_path}")
    
    def connect(self):
        """Establish database connection."""
        try:
            # Check if database file exists
            if not Path(self.database_path).exists():
                logger.warning(f"Database file not found: {self.database_path}")
                logger.info("Database will be created on first connection")
            
            self.connection = sqlite3.connect(self.database_path)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            logger.info(f"Successfully connected to database: {self.database_path}")
            return self.connection
        
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
            self.connection = None
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            logger.debug("Database connection acquired")
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
                logger.debug("Database connection released")
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None,
        fetch_all: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query to execute
            params: Query parameters (for parameterized queries)
            fetch_all: If True, fetch all results; if False, fetch one
        
        Returns:
            List of dictionaries representing rows
        """
        logger.debug(f"Executing query: {query[:100]}...")
        if params:
            logger.debug(f"Query parameters: {params}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Check if it's a query that returns results (SELECT or PRAGMA)
                query_upper = query.strip().upper()
                if query_upper.startswith("SELECT") or query_upper.startswith("PRAGMA"):
                    if fetch_all:
                        rows = cursor.fetchall()
                    else:
                        rows = [cursor.fetchone()] if cursor.fetchone() else []
                    
                    # Convert Row objects to dictionaries
                    results = [dict(row) for row in rows if row]
                    logger.info(f"Query executed successfully. Rows returned: {len(results)}")
                    return results
                else:
                    # For INSERT, UPDATE, DELETE
                    conn.commit()
                    logger.info(f"Query executed successfully. Rows affected: {cursor.rowcount}")
                    return [{"rows_affected": cursor.rowcount}]
            
            except sqlite3.Error as e:
                logger.error(f"Query execution failed: {e}")
                logger.error(f"Failed query: {query}")
                raise
    
    def execute_script(self, script: str):
        """Execute a SQL script (multiple statements)."""
        logger.info("Executing SQL script")
        logger.debug(f"Script length: {len(script)} characters")
        
        with self.get_connection() as conn:
            try:
                conn.executescript(script)
                conn.commit()
                logger.info("SQL script executed successfully")
            except sqlite3.Error as e:
                logger.error(f"Script execution failed: {e}")
                raise
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        results = self.execute_query(query, (table_name,))
        exists = len(results) > 0
        logger.debug(f"Table '{table_name}' exists: {exists}")
        return exists
