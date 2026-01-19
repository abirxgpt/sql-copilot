"""Configuration management for SQL Copilot."""
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration (optional for Gemini)
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    
    # Database Configuration
    database_path: str = Field(default="data/ecommerce.db", env="DATABASE_PATH")
    
    # Logging Configuration
    log_level: str = Field(default="DEBUG", env="LOG_LEVEL")
    log_file: str = Field(default="logs/sql_copilot.log", env="LOG_FILE")
    
    # RAG Configuration
    vector_db_path: str = Field(default="data/chroma_db", env="VECTOR_DB_PATH")
    embedding_model: str = Field(default="models/embedding-001", env="EMBEDDING_MODEL")
    
    # Query Configuration
    max_query_timeout: int = Field(default=30, env="MAX_QUERY_TIMEOUT")
    max_result_rows: int = Field(default=1000, env="MAX_RESULT_ROWS")
    enable_dangerous_queries: bool = Field(default=False, env="ENABLE_DANGEROUS_QUERIES")
    
    # LLM Configuration
    llm_provider: str = Field(default="ollama", env="LLM_PROVIDER")
    llm_model: str = Field(default="qwen2.5-coder:7b", env="LLM_MODEL")
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    llm_temperature: float = Field(default=0.1, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2048, env="LLM_MAX_TOKENS")
    
    # RAG Configuration
    rag_enabled: bool = Field(default=True, env="RAG_ENABLED")
    rag_top_k_tables: int = Field(default=5, env="RAG_TOP_K")
    rag_similarity_threshold: float = Field(default=0.3, env="RAG_SIMILARITY_THRESHOLD")
    embedding_model: str = Field(default="nomic-embed-text", env="EMBEDDING_MODEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self):
        """Create required directories if they don't exist."""
        dirs = [
            Path(self.database_path).parent,
            Path(self.log_file).parent,
            Path(self.vector_db_path),
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def validate_api_key(self) -> bool:
        """Check if Gemini API key is configured."""
        return bool(self.gemini_api_key and self.gemini_api_key != "your_gemini_api_key_here")


# Global settings instance
settings = Settings()
