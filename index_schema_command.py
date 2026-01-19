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


