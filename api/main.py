"""FastAPI backend for SQL Copilot web interface."""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from database import DatabaseConnection, SchemaManager
from core import NL2SQLConverter, QueryValidator, QueryExplainer, ErrorCorrector
from utils.logger import get_logger

logger = get_logger("api.main")

# Initialize FastAPI app
app = FastAPI(
    title="SQL Copilot API",
    description="Natural Language to SQL API with RAG",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = None
schema_manager = None
nl2sql = None
validator = None
explainer = None
error_corrector = None
rag_retriever = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global db, schema_manager, nl2sql, validator, explainer, error_corrector, rag_retriever
    
    logger.info("Initializing SQL Copilot API...")
    
    try:
        # Initialize database components
        db = DatabaseConnection(settings.database_path)
        schema_manager = SchemaManager(db)
        
        # Initialize RAG if enabled
        if settings.rag_enabled:
            try:
                from rag.retriever import SchemaRetriever
                rag_retriever = SchemaRetriever()
                if rag_retriever.is_indexed():
                    logger.info("RAG retriever initialized")
                else:
                    logger.warning("RAG not indexed, run index-schema command")
                    rag_retriever = None
            except Exception as e:
                logger.warning(f"RAG initialization failed: {e}")
                rag_retriever = None
        
        # Initialize core components
        nl2sql = NL2SQLConverter(schema_manager, rag_retriever)
        validator = QueryValidator(schema_manager)
        explainer = QueryExplainer()
        error_corrector = ErrorCorrector(schema_manager)
        
        logger.info("SQL Copilot API initialized successfully")
    
    except Exception as e:
        logger.error(f"Failed to initialize API: {e}")
        raise


# Request/Response Models
class NL2SQLRequest(BaseModel):
    question: str
    context: Optional[str] = None


class NL2SQLResponse(BaseModel):
    sql: str
    explanation: str
    confidence: str
    tables_used: Optional[List[str]] = None


class ExecuteQueryRequest(BaseModel):
    sql: str


class ExecuteQueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    row_count: int
    execution_time: float


class ValidateQueryRequest(BaseModel):
    sql: str


class ValidateQueryResponse(BaseModel):
    is_valid: bool
    warnings: List[str]


class ExplainQueryRequest(BaseModel):
    sql: str


class ExplainQueryResponse(BaseModel):
    explanation: str
    query: str


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "SQL Copilot API",
        "version": "1.0.0",
        "status": "running",
        "rag_enabled": settings.rag_enabled,
        "rag_indexed": rag_retriever.is_indexed() if rag_retriever else False
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected" if db else "disconnected",
        "rag": "enabled" if rag_retriever else "disabled"
    }


@app.post("/api/v1/query/nl2sql", response_model=NL2SQLResponse)
async def convert_nl_to_sql(request: NL2SQLRequest):
    """Convert natural language to SQL."""
    try:
        logger.info(f"NL2SQL request: {request.question}")
        
        # Convert to SQL
        result = nl2sql.convert(request.question, request.context)
        
        # Get tables used (if RAG was used)
        tables_used = None
        if rag_retriever and settings.rag_enabled:
            tables_used = rag_retriever.retrieve(request.question)
        
        return NL2SQLResponse(
            sql=result['sql'],
            explanation=result.get('explanation', ''),
            confidence=result.get('confidence', 'medium'),
            tables_used=tables_used
        )
    
    except Exception as e:
        logger.error(f"NL2SQL conversion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/query/execute", response_model=ExecuteQueryResponse)
async def execute_query(request: ExecuteQueryRequest):
    """Execute SQL query."""
    try:
        logger.info(f"Executing query: {request.sql[:100]}...")
        
        # Validate first
        is_valid, warnings = validator.validate(request.sql)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid query: {warnings}")
        
        # Execute
        import time
        start_time = time.time()
        results = db.execute_query(request.sql)
        execution_time = time.time() - start_time
        
        return ExecuteQueryResponse(
            results=results,
            row_count=len(results),
            execution_time=execution_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/query/validate", response_model=ValidateQueryResponse)
async def validate_query(request: ValidateQueryRequest):
    """Validate SQL query."""
    try:
        is_valid, warnings = validator.validate(request.sql)
        
        return ValidateQueryResponse(
            is_valid=is_valid,
            warnings=warnings
        )
    
    except Exception as e:
        logger.error(f"Query validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/query/explain", response_model=ExplainQueryResponse)
async def explain_query(request: ExplainQueryRequest):
    """Explain SQL query."""
    try:
        result = explainer.explain(request.sql)
        
        return ExplainQueryResponse(
            explanation=result['explanation'],
            query=result['query']
        )
    
    except Exception as e:
        logger.error(f"Query explanation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/schema")
async def get_schema():
    """Get database schema."""
    try:
        tables = schema_manager.get_all_tables()
        schema_info = {}
        
        for table_name in tables:
            table_info = schema_manager.get_table_info(table_name, include_samples=False)
            schema_info[table_name] = {
                "row_count": table_info.row_count,
                "columns": [
                    {
                        "name": col.name,
                        "type": col.type,
                        "nullable": col.nullable,
                        "primary_key": col.primary_key
                    }
                    for col in table_info.columns
                ],
                "foreign_keys": schema_manager.get_foreign_keys(table_name)
            }
        
        return schema_info
    
    except Exception as e:
        logger.error(f"Failed to get schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/schema/{table_name}")
async def get_table_schema(table_name: str):
    """Get schema for specific table."""
    try:
        table_info = schema_manager.get_table_info(table_name, include_samples=True)
        
        return {
            "name": table_name,
            "row_count": table_info.row_count,
            "columns": [
                {
                    "name": col.name,
                    "type": col.type,
                    "nullable": col.nullable,
                    "primary_key": col.primary_key,
                    "default_value": col.default_value
                }
                for col in table_info.columns
            ],
            "foreign_keys": schema_manager.get_foreign_keys(table_name),
            "sample_data": table_info.sample_data[:5]  # First 5 rows
        }
    
    except Exception as e:
        logger.error(f"Failed to get table schema: {e}")
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")


# WebSocket for real-time query execution
@app.websocket("/ws/query")
async def websocket_query(websocket: WebSocket):
    """WebSocket endpoint for real-time query execution."""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            action = data.get("action")
            
            if action == "nl2sql":
                # Convert NL to SQL
                question = data.get("question")
                result = nl2sql.convert(question)
                await websocket.send_json({
                    "type": "nl2sql_result",
                    "data": result
                })
            
            elif action == "execute":
                # Execute SQL
                sql = data.get("sql")
                is_valid, warnings = validator.validate(sql)
                
                if not is_valid:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Invalid query: {warnings}"
                    })
                else:
                    results = db.execute_query(sql)
                    await websocket.send_json({
                        "type": "execute_result",
                        "data": {
                            "results": results,
                            "row_count": len(results)
                        }
                    })
            
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
