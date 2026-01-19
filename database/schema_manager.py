"""Schema manager for extracting and caching database metadata."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from utils.logger import get_logger

logger = get_logger("database.schema_manager")


@dataclass
class ColumnInfo:
    """Information about a database column."""
    name: str
    type: str
    nullable: bool
    default_value: Optional[str]
    primary_key: bool


@dataclass
class TableInfo:
    """Information about a database table."""
    name: str
    columns: List[ColumnInfo]
    row_count: int
    sample_data: List[Dict[str, Any]]


class SchemaManager:
    """Manages database schema metadata extraction and caching."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self._schema_cache: Dict[str, TableInfo] = {}
        logger.info("Schema manager initialized")
    
    def get_all_tables(self) -> List[str]:
        """Get list of all tables in the database."""
        logger.debug("Fetching all table names")
        
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        
        results = self.db.execute_query(query)
        tables = [row['name'] for row in results]
        
        logger.info(f"Found {len(tables)} tables: {', '.join(tables)}")
        return tables
    
    def get_table_info(self, table_name: str, include_samples: bool = True) -> TableInfo:
        """
        Get detailed information about a table.
        
        Args:
            table_name: Name of the table
            include_samples: Whether to include sample data
        
        Returns:
            TableInfo object with table metadata
        """
        logger.debug(f"Fetching info for table: {table_name}")
        
        # Check cache
        if table_name in self._schema_cache and not include_samples:
            logger.debug(f"Returning cached info for table: {table_name}")
            return self._schema_cache[table_name]
        
        # Get column information
        columns = self._get_columns(table_name)
        
        # Get row count
        row_count = self._get_row_count(table_name)
        
        # Get sample data
        sample_data = []
        if include_samples:
            sample_data = self._get_sample_data(table_name, limit=5)
        
        table_info = TableInfo(
            name=table_name,
            columns=columns,
            row_count=row_count,
            sample_data=sample_data
        )
        
        # Cache the result
        self._schema_cache[table_name] = table_info
        
        logger.info(f"Table '{table_name}': {len(columns)} columns, {row_count} rows")
        return table_info
    
    def _get_columns(self, table_name: str) -> List[ColumnInfo]:
        """Get column information for a table."""
        query = f"PRAGMA table_info({table_name})"
        results = self.db.execute_query(query)
        
        columns = []
        for row in results:
            col = ColumnInfo(
                name=row['name'],
                type=row['type'],
                nullable=not bool(row['notnull']),
                default_value=row['dflt_value'],
                primary_key=bool(row['pk'])
            )
            columns.append(col)
        
        logger.debug(f"Table '{table_name}' has {len(columns)} columns")
        return columns
    
    def _get_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table."""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.db.execute_query(query)
        count = result[0]['count'] if result else 0
        return count
    
    def _get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample rows from a table."""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        results = self.db.execute_query(query)
        logger.debug(f"Retrieved {len(results)} sample rows from '{table_name}'")
        return results
    
    def get_foreign_keys(self, table_name: str) -> List[Dict[str, str]]:
        """Get foreign key relationships for a table."""
        query = f"PRAGMA foreign_key_list({table_name})"
        results = self.db.execute_query(query)
        
        foreign_keys = []
        for row in results:
            # Use bracket notation since 'from' and 'to' are Python keywords
            fk = {
                'column': row.get('from', ''),
                'referenced_table': row.get('table', ''),
                'referenced_column': row.get('to', '')
            }
            foreign_keys.append(fk)
        
        logger.debug(f"Table '{table_name}' has {len(foreign_keys)} foreign keys")
        return foreign_keys
    
    def get_full_schema(self) -> Dict[str, TableInfo]:
        """Get complete schema information for all tables."""
        logger.info("Fetching full database schema")
        
        tables = self.get_all_tables()
        schema = {}
        
        for table_name in tables:
            schema[table_name] = self.get_table_info(table_name, include_samples=True)
        
        logger.info(f"Full schema retrieved for {len(schema)} tables")
        return schema
    
    def get_schema_summary(self) -> str:
        """Get a human-readable summary of the database schema."""
        logger.debug("Generating schema summary")
        
        tables = self.get_all_tables()
        summary_lines = ["Database Schema Summary", "=" * 50, ""]
        
        for table_name in tables:
            info = self.get_table_info(table_name, include_samples=False)
            summary_lines.append(f"Table: {table_name} ({info.row_count} rows)")
            
            for col in info.columns:
                pk_marker = " [PK]" if col.primary_key else ""
                null_marker = " NULL" if col.nullable else " NOT NULL"
                summary_lines.append(f"  - {col.name}: {col.type}{null_marker}{pk_marker}")
            
            # Add foreign keys
            fks = self.get_foreign_keys(table_name)
            if fks:
                summary_lines.append("  Foreign Keys:")
                for fk in fks:
                    summary_lines.append(
                        f"    - {fk['column']} -> {fk['referenced_table']}.{fk['referenced_column']}"
                    )
            
            summary_lines.append("")
        
        summary = "\n".join(summary_lines)
        logger.debug("Schema summary generated")
        return summary
    
    def clear_cache(self):
        """Clear the schema cache."""
        self._schema_cache.clear()
        logger.info("Schema cache cleared")
