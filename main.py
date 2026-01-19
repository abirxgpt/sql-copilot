"""Main CLI application for SQL Copilot."""
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich import print as rprint

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from utils.logger import setup_logging, get_logger
from utils.formatters import (
    print_success, print_error, print_warning, print_info,
    print_sql_panel, print_explanation, print_validation_result,
    format_results_table, export_to_csv, export_to_json, console
)
from database import DatabaseConnection, SchemaManager
from core import NL2SQLConverter, QueryValidator, QueryExplainer, ErrorCorrector

# Initialize Typer app
app = typer.Typer(help="SQL Copilot - Natural Language to SQL Assistant")
console = Console()

# Global logger
logger = None


class SQLCopilot:
    """Main SQL Copilot application."""
    
    def __init__(self, use_rag: bool = None):
        global logger
        logger = setup_logging()
        logger.info("Initializing SQL Copilot")
        
        # Determine if RAG should be used
        if use_rag is None:
            use_rag = settings.rag_enabled
        
        # Initialize components
        try:
            self.db = DatabaseConnection(settings.database_path)
            self.schema_manager = SchemaManager(self.db)
            
            # Initialize RAG retriever if enabled
            self.rag_retriever = None
            if use_rag:
                try:
                    from rag.retriever import SchemaRetriever
                    self.rag_retriever = SchemaRetriever()
                    if self.rag_retriever.is_indexed():
                        logger.info("RAG retriever initialized and ready")
                    else:
                        logger.warning("RAG retriever initialized but schema not indexed")
                        logger.warning("Run 'python main.py index-schema' to create embeddings")
                        self.rag_retriever = None
                except Exception as e:
                    logger.warning(f"Failed to initialize RAG retriever: {e}")
                    logger.warning("Continuing without RAG")
                    self.rag_retriever = None
            
            self.nl2sql = NL2SQLConverter(self.schema_manager, self.rag_retriever)
            self.validator = QueryValidator(self.schema_manager)
            self.explainer = QueryExplainer()
            self.error_corrector = ErrorCorrector(self.schema_manager)
            
            logger.info("SQL Copilot initialized successfully")
            print_success("SQL Copilot initialized successfully!")
        
        except Exception as e:
            logger.error(f"Failed to initialize SQL Copilot: {e}")
            print_error(f"Initialization failed: {e}")
            raise
    
    def process_query(self, natural_language_query: str, explain: bool = False) -> Optional[list]:
        """Process a natural language query."""
        logger.info(f"Processing query: {natural_language_query}")
        
        try:
            # Convert NL to SQL
            console.print("\n🤖 [bold cyan]Converting to SQL...[/bold cyan]")
            result = self.nl2sql.convert(natural_language_query)
            
            sql_query = result['sql']
            explanation = result.get('explanation', '')
            confidence = result.get('confidence', 'medium')
            
            # Display generated SQL
            print_sql_panel(sql_query)
            
            if confidence:
                console.print(f"🎯 Confidence: [bold]{confidence.upper()}[/bold]\n")
            
            # Validate query
            console.print("🔍 [bold yellow]Validating query...[/bold yellow]")
            is_valid, warnings = self.validator.validate(sql_query)
            print_validation_result(is_valid, warnings)
            
            if not is_valid:
                logger.error("Query validation failed")
                return None
            
            # Show explanation if requested
            if explain and explanation:
                print_explanation(explanation)
            
            # Execute query
            console.print("\n⚡ [bold green]Executing query...[/bold green]")
            results = self.db.execute_query(sql_query)
            
            # Display results
            if results:
                table = format_results_table(results)
                console.print("\n")
                console.print(table)
                console.print(f"\n📊 [bold]Rows returned:[/bold] {len(results)}")
            else:
                print_info("No results returned")
            
            return results
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print_error(f"Query failed: {e}")
            
            # Try to correct the error only if we have a sql_query
            if 'sql_query' in locals() and hasattr(self, 'error_corrector'):
                console.print("\n🔧 [bold magenta]Attempting to fix error...[/bold magenta]")
                try:
                    correction = self.error_corrector.correct(sql_query, str(e))
                    if correction['success']:
                        console.print(f"\n💡 [bold green]Suggested fix:[/bold green]")
                        print_sql_panel(correction['sql'], title="Corrected SQL")
                        if correction['explanation']:
                            console.print(f"\n📝 {correction['explanation']}")
                        
                        # Ask if user wants to try the corrected query
                        retry = Prompt.ask("\nTry the corrected query?", choices=["y", "n"], default="y")
                        if retry.lower() == 'y':
                            return self.execute_sql(correction['sql'])
                except Exception as correction_error:
                    logger.error(f"Error correction failed: {correction_error}")
            
            return None
    
    def execute_sql(self, sql_query: str) -> Optional[list]:
        """Execute a SQL query directly."""
        logger.info(f"Executing SQL: {sql_query[:100]}...")
        
        try:
            # Validate
            is_valid, warnings = self.validator.validate(sql_query)
            print_validation_result(is_valid, warnings)
            
            if not is_valid:
                return None
            
            # Execute
            results = self.db.execute_query(sql_query)
            
            # Display results
            if results:
                table = format_results_table(results)
                console.print(table)
                console.print(f"\n📊 Rows returned: {len(results)}")
            else:
                print_info("No results returned")
            
            return results
        
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            print_error(f"Execution failed: {e}")
            return None
    
    def explain_query(self, sql_query: str):
        """Explain a SQL query."""
        logger.info("Explaining query")
        
        try:
            console.print("\n📖 [bold cyan]Generating explanation...[/bold cyan]")
            result = self.explainer.explain(sql_query)
            print_explanation(result['explanation'])
        
        except Exception as e:
            logger.error(f"Explanation failed: {e}")
            print_error(f"Failed to explain query: {e}")
    
    def show_schema(self):
        """Display database schema."""
        logger.info("Displaying schema")
        
        try:
            summary = self.schema_manager.get_schema_summary()
            panel = Panel(summary, title="📊 Database Schema", border_style="cyan")
            console.print(panel)
        
        except Exception as e:
            logger.error(f"Failed to show schema: {e}")
            print_error(f"Failed to display schema: {e}")
    
    def interactive_mode(self):
        """Start interactive CLI mode."""
        logger.info("Starting interactive mode")
        
        # Display welcome message
        console.print(Panel.fit(
            "[bold cyan]SQL Copilot[/bold cyan]\n"
            "Natural Language to SQL Assistant\n\n"
            "Commands:\n"
            "  • Type your question in natural language\n"
            "  • 'schema' - Show database schema\n"
            "  • 'explain <sql>' - Explain a SQL query\n"
            "  • 'exit' or 'quit' - Exit the program",
            border_style="green"
        ))
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]🤖 SQL Copilot[/bold green]")
                
                if not user_input.strip():
                    continue
                
                # Handle commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print_info("Goodbye! 👋")
                    break
                
                elif user_input.lower() == 'schema':
                    self.show_schema()
                
                elif user_input.lower().startswith('explain '):
                    sql = user_input[8:].strip()
                    self.explain_query(sql)
                
                else:
                    # Process as natural language query
                    self.process_query(user_input, explain=True)
            
            except KeyboardInterrupt:
                print_info("\nGoodbye! 👋")
                break
            
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print_error(f"Error: {e}")


@app.command()
def query(
    question: str = typer.Argument(..., help="Natural language question"),
    explain: bool = typer.Option(False, "--explain", "-e", help="Show query explanation"),
    export: Optional[str] = typer.Option(None, "--export", "-o", help="Export results to file (CSV or JSON)")
):
    """Convert a natural language question to SQL and execute it."""
    try:
        copilot = SQLCopilot()
        results = copilot.process_query(question, explain=explain)
        
        # Export if requested
        if results and export:
            if export.endswith('.csv'):
                export_to_csv(results, export)
            elif export.endswith('.json'):
                export_to_json(results, export)
            else:
                print_warning("Export file must be .csv or .json")
    
    except Exception as e:
        print_error(f"Error: {e}")
        raise typer.Exit(1)


@app.command()
def interactive():
    """Start interactive mode."""
    try:
        copilot = SQLCopilot()
        copilot.interactive_mode()
    
    except Exception as e:
        print_error(f"Error: {e}")
        raise typer.Exit(1)


@app.command()
def schema():
    """Display the database schema."""
    try:
        # Don't initialize full copilot, just database and schema manager
        db = DatabaseConnection(settings.database_path)
        schema_manager = SchemaManager(db)
        
        summary = schema_manager.get_schema_summary()
        panel = Panel(summary, title="📊 Database Schema", border_style="cyan")
        console.print(panel)
    
    except Exception as e:
        print_error(f"Error: {e}")
        raise typer.Exit(1)


@app.command()
def explain(sql_query: str = typer.Argument(..., help="SQL query to explain")):
    """Explain a SQL query in natural language."""
    try:
        copilot = SQLCopilot()
        copilot.explain_query(sql_query)
    
    except Exception as e:
        print_error(f"Error: {e}")
        raise typer.Exit(1)




@app.command()
def index_schema():
    """Index database schema for RAG (semantic search)."""
    try:
        print_info("Indexing database schema for RAG...")
        
        # Initialize components
        db = DatabaseConnection(settings.database_path)
        schema_manager = SchemaManager(db)
        
        # Import and initialize indexer
        from rag.schema_indexer import SchemaIndexer
        indexer = SchemaIndexer(schema_manager)
        
        # Index the schema
        console.print("\n🔍 [bold cyan]Analyzing database schema...[/bold cyan]")
        indexer.index_schema(force_reindex=True)
        
        # Get stats
        stats = indexer.get_collection_stats()
        
        console.print(f"\n✅ [bold green]Schema indexed successfully![/bold green]")
        console.print(f"📊 Total embeddings: {stats['total_embeddings']}")
        console.print(f"💾 Stored in: {settings.vector_db_path}")
        console.print("\n💡 RAG is now enabled for intelligent schema retrieval!")
    
    except Exception as e:
        print_error(f"Failed to index schema: {e}")
        logger.error(f"Schema indexing failed: {e}", exc_info=True)
        raise typer.Exit(1)


@app.command()
def init():
    """Initialize the database with sample data."""
    try:
        print_info("Creating sample database...")
        
        # Import and run the database creation script
        from scripts.create_sample_db import create_database
        create_database(settings.database_path)
        
        print_success(f"Database created successfully at: {settings.database_path}")
    
    except Exception as e:
        print_error(f"Failed to create database: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
