"""Schema indexer for creating and maintaining vector embeddings of database schema."""
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.embeddings import OllamaEmbeddings
from database.schema_manager import SchemaManager
from config.settings import settings
from utils.logger import get_logger
import json

logger = get_logger("rag.schema_indexer")


class SchemaIndexer:
    """Creates and maintains vector embeddings for database schema."""
    
    def __init__(self, schema_manager: SchemaManager):
        self.schema_manager = schema_manager
        self.chroma_client = None
        self.collection = None
        self.embeddings = None
        self._initialize()
        logger.info("Schema Indexer initialized")
    
    def _initialize(self):
        """Initialize ChromaDB and embedding model."""
        try:
            # Initialize ChromaDB
            logger.info(f"Initializing ChromaDB at: {settings.vector_db_path}")
            self.chroma_client = chromadb.PersistentClient(
                path=settings.vector_db_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="schema_embeddings",
                metadata={"description": "Database schema embeddings for RAG"}
            )
            
            logger.info(f"ChromaDB collection ready. Current count: {self.collection.count()}")
            
            # Initialize Ollama embeddings
            logger.info(f"Initializing Ollama embeddings with model: {settings.embedding_model}")
            self.embeddings = OllamaEmbeddings(
                model=settings.embedding_model,
                base_url=settings.ollama_base_url
            )
            
            logger.info("Schema indexer initialization complete")
        
        except Exception as e:
            logger.error(f"Failed to initialize schema indexer: {e}")
            raise
    
    def index_schema(self, force_reindex: bool = False):
        """
        Index all tables in the database.
        
        Args:
            force_reindex: If True, clear existing embeddings and reindex
        """
        logger.info("Starting schema indexing")
        
        try:
            # Clear existing if force reindex
            if force_reindex and self.collection.count() > 0:
                logger.info("Force reindex: clearing existing embeddings")
                self.chroma_client.delete_collection("schema_embeddings")
                self.collection = self.chroma_client.create_collection(
                    name="schema_embeddings",
                    metadata={"description": "Database schema embeddings for RAG"}
                )
            
            # Get all tables
            tables = self.schema_manager.get_all_tables()
            logger.info(f"Indexing {len(tables)} tables")
            
            # Index each table
            for table_name in tables:
                self._index_table(table_name)
            
            logger.info(f"Schema indexing complete. Total embeddings: {self.collection.count()}")
        
        except Exception as e:
            logger.error(f"Schema indexing failed: {e}")
            raise
    
    def _index_table(self, table_name: str):
        """Index a single table."""
        logger.debug(f"Indexing table: {table_name}")
        
        try:
            # Get table info
            table_info = self.schema_manager.get_table_info(table_name, include_samples=True)
            
            # Create rich text description
            description = self._create_table_description(table_info)
            
            # Get foreign keys
            foreign_keys = self.schema_manager.get_foreign_keys(table_name)
            
            # Create metadata
            metadata = {
                "table_name": table_name,
                "column_count": len(table_info.columns),
                "row_count": table_info.row_count,
                "has_foreign_keys": len(foreign_keys) > 0,
                "related_tables": json.dumps([fk['referenced_table'] for fk in foreign_keys]),
                "columns": json.dumps([col.name for col in table_info.columns])
            }
            
            # Generate embedding
            logger.debug(f"Generating embedding for table: {table_name}")
            embedding = self.embeddings.embed_query(description)
            
            # Store in ChromaDB
            self.collection.upsert(
                ids=[f"table_{table_name}"],
                embeddings=[embedding],
                documents=[description],
                metadatas=[metadata]
            )
            
            logger.debug(f"Successfully indexed table: {table_name}")
        
        except Exception as e:
            logger.error(f"Failed to index table {table_name}: {e}")
            raise
    
    def _create_table_description(self, table_info) -> str:
        """Create a rich text description of a table for embedding."""
        
        description_parts = []
        
        # Table name and basic info
        description_parts.append(f"Table Name: {table_info.name}")
        description_parts.append(f"Row Count: {table_info.row_count} rows")
        
        # Columns with types
        description_parts.append("\nColumns:")
        for col in table_info.columns:
            col_desc = f"- {col.name} ({col.type})"
            if col.primary_key:
                col_desc += " [PRIMARY KEY]"
            if not col.nullable:
                col_desc += " [NOT NULL]"
            description_parts.append(col_desc)
        
        # Sample data (first 2 rows)
        if table_info.sample_data:
            description_parts.append("\nSample Data:")
            for i, row in enumerate(table_info.sample_data[:2], 1):
                # Convert row to readable format
                row_data = {k: v for k, v in dict(row).items()}
                description_parts.append(f"Row {i}: {json.dumps(row_data)}")
        
        # Foreign keys
        foreign_keys = self.schema_manager.get_foreign_keys(table_info.name)
        if foreign_keys:
            description_parts.append("\nRelationships:")
            for fk in foreign_keys:
                description_parts.append(
                    f"- {fk['column']} references {fk['referenced_table']}.{fk['referenced_column']}"
                )
        
        # Common use cases (inferred from table name and columns)
        use_cases = self._infer_use_cases(table_info)
        if use_cases:
            description_parts.append("\nCommon Use Cases:")
            for use_case in use_cases:
                description_parts.append(f"- {use_case}")
        
        description = "\n".join(description_parts)
        logger.debug(f"Created description for {table_info.name}: {len(description)} chars")
        
        return description
    
    def _infer_use_cases(self, table_info) -> List[str]:
        """Infer common use cases based on table name and columns."""
        use_cases = []
        table_name = table_info.name.lower()
        column_names = [col.name.lower() for col in table_info.columns]
        
        # Common patterns
        if 'customer' in table_name:
            use_cases.append("Customer information and demographics")
            use_cases.append("Customer contact details")
        
        if 'order' in table_name:
            use_cases.append("Order history and transactions")
            use_cases.append("Sales and revenue analysis")
        
        if 'product' in table_name:
            use_cases.append("Product catalog and inventory")
            use_cases.append("Product pricing and details")
        
        if 'review' in table_name or 'rating' in column_names:
            use_cases.append("Customer feedback and ratings")
            use_cases.append("Product quality analysis")
        
        if 'category' in table_name:
            use_cases.append("Product categorization")
            use_cases.append("Hierarchical organization")
        
        # Check for common columns
        if 'price' in column_names or 'amount' in column_names:
            use_cases.append("Financial and pricing data")
        
        if 'date' in str(column_names) or 'created_at' in column_names:
            use_cases.append("Time-based analysis and trends")
        
        return use_cases
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed schema."""
        return {
            "total_embeddings": self.collection.count(),
            "collection_name": self.collection.name,
            "metadata": self.collection.metadata
        }
    
    def clear_index(self):
        """Clear all embeddings."""
        logger.warning("Clearing all schema embeddings")
        self.chroma_client.delete_collection("schema_embeddings")
        self.collection = self.chroma_client.create_collection(
            name="schema_embeddings",
            metadata={"description": "Database schema embeddings for RAG"}
        )
        logger.info("Schema index cleared")
