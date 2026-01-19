"""Test script to debug schema issue."""
from database import DatabaseConnection, SchemaManager
from config.settings import settings

# Test database connection
db = DatabaseConnection(settings.database_path)

# Test schema manager
schema_manager = SchemaManager(db)

# Test getting tables
print("Getting all tables...")
tables = schema_manager.get_all_tables()
print(f"Tables: {tables}")

# Test getting table info
print("\nGetting table info for 'customers'...")
info = schema_manager.get_table_info('customers', include_samples=False)
print(f"Table: {info.name}")
print(f"Columns: {[col.name for col in info.columns]}")

# Test getting schema summary
print("\nGetting schema summary...")
summary = schema_manager.get_schema_summary()
print(summary)
