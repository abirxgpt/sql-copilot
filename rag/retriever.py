"""Schema retriever for finding relevant tables using semantic search."""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_community.embeddings import OllamaEmbeddings
from config.settings import settings
from utils.logger import get_logger
import json

logger = get_logger("rag.retriever")


class SchemaRetriever:
    """Retrieves relevant database tables using semantic search."""
    
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.embeddings = None
        self._initialize()
        logger.info("Schema Retriever initialized")
    
    def _initialize(self):
        """Initialize ChromaDB and embedding model."""
        try:
            # Initialize ChromaDB
            logger.debug(f"Connecting to ChromaDB at: {settings.vector_db_path}")
            self.chroma_client = chromadb.PersistentClient(
                path=settings.vector_db_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False
                )
            )
            
            # Get collection
            try:
                self.collection = self.chroma_client.get_collection(
                    name="schema_embeddings"
                )
                logger.info(f"Connected to schema embeddings collection. Count: {self.collection.count()}")
            except Exception as e:
                logger.warning(f"Schema embeddings collection not found: {e}")
                logger.warning("Run 'python main.py index-schema' to create embeddings")
                self.collection = None
            
            # Initialize Ollama embeddings
            logger.debug(f"Initializing embeddings with model: {settings.embedding_model}")
            self.embeddings = OllamaEmbeddings(
                model=settings.embedding_model,
                base_url=settings.ollama_base_url
            )
            
            logger.info("Schema retriever initialization complete")
        
        except Exception as e:
            logger.error(f"Failed to initialize schema retriever: {e}")
            raise
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = None,
        similarity_threshold: float = None
    ) -> List[str]:
        """
        Retrieve relevant table names based on natural language query.
        
        Args:
            query: Natural language query
            top_k: Number of tables to retrieve (default from settings)
            similarity_threshold: Minimum similarity score (default from settings)
        
        Returns:
            List of relevant table names, ordered by relevance
        """
        if not self.collection:
            logger.warning("No schema embeddings found. Returning empty list.")
            return []
        
        # Use defaults from settings if not provided
        if top_k is None:
            top_k = settings.rag_top_k_tables
        if similarity_threshold is None:
            similarity_threshold = settings.rag_similarity_threshold
        
        logger.info(f"Retrieving relevant tables for query: {query[:100]}...")
        logger.debug(f"Parameters: top_k={top_k}, threshold={similarity_threshold}")
        
        try:
            # Embed the query
            logger.debug("Generating query embedding")
            query_embedding = self.embeddings.embed_query(query)
            
            # Search ChromaDB
            logger.debug("Searching vector database")
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["metadatas", "distances", "documents"]
            )
            
            # Extract table names with scores
            table_names = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i, table_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    similarity = 1 - distance  # Convert distance to similarity
                    
                    # Apply threshold
                    if similarity >= similarity_threshold:
                        metadata = results['metadatas'][0][i]
                        table_name = metadata['table_name']
                        table_names.append(table_name)
                        
                        logger.debug(
                            f"Retrieved: {table_name} "
                            f"(similarity: {similarity:.3f}, "
                            f"columns: {metadata['column_count']}, "
                            f"rows: {metadata['row_count']})"
                        )
            
            logger.info(f"Retrieved {len(table_names)} relevant tables: {', '.join(table_names)}")
            return table_names
        
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            logger.warning("Falling back to empty list")
            return []
    
    def retrieve_with_details(
        self, 
        query: str, 
        top_k: int = None,
        similarity_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant tables with detailed metadata.
        
        Returns:
            List of dicts with table_name, similarity, metadata
        """
        if not self.collection:
            logger.warning("No schema embeddings found")
            return []
        
        # Use defaults from settings
        if top_k is None:
            top_k = settings.rag_top_k_tables
        if similarity_threshold is None:
            similarity_threshold = settings.rag_similarity_threshold
        
        logger.info(f"Retrieving detailed results for: {query[:100]}...")
        
        try:
            # Embed the query
            query_embedding = self.embeddings.embed_query(query)
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["metadatas", "distances", "documents"]
            )
            
            # Build detailed results
            detailed_results = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    distance = results['distances'][0][i]
                    similarity = 1 - distance
                    
                    if similarity >= similarity_threshold:
                        metadata = results['metadatas'][0][i]
                        
                        detailed_results.append({
                            "table_name": metadata['table_name'],
                            "similarity": similarity,
                            "column_count": metadata['column_count'],
                            "row_count": metadata['row_count'],
                            "has_foreign_keys": metadata['has_foreign_keys'],
                            "related_tables": json.loads(metadata['related_tables']),
                            "columns": json.loads(metadata['columns']),
                            "description": results['documents'][0][i]
                        })
            
            logger.info(f"Retrieved {len(detailed_results)} detailed results")
            return detailed_results
        
        except Exception as e:
            logger.error(f"Detailed retrieval failed: {e}")
            return []
    
    def is_indexed(self) -> bool:
        """Check if schema embeddings exist."""
        if not self.collection:
            return False
        return self.collection.count() > 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics."""
        if not self.collection:
            return {"indexed": False, "count": 0}
        
        return {
            "indexed": True,
            "count": self.collection.count(),
            "collection_name": self.collection.name
        }
