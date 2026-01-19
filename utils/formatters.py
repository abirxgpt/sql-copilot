"""Output formatting utilities for SQL Copilot."""
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
from rich.markdown import Markdown
import json


console = Console()


def format_sql(sql: str, theme: str = "monokai") -> Syntax:
    """Format SQL with syntax highlighting."""
    return Syntax(sql, "sql", theme=theme, line_numbers=False)


def format_results_table(results: List[Dict[str, Any]], title: str = "Query Results") -> Table:
    """Format query results as a rich table."""
    if not results:
        return Table(title=title, show_header=False)
    
    # Create table
    table = Table(title=title, show_header=True, header_style="bold magenta")
    
    # Add columns
    columns = list(results[0].keys())
    for col in columns:
        table.add_column(col, style="cyan")
    
    # Add rows
    for row in results:
        table.add_row(*[str(row.get(col, "")) for col in columns])
    
    return table


def print_success(message: str):
    """Print success message."""
    console.print(f"✅ [green]{message}[/green]")


def print_error(message: str):
    """Print error message."""
    console.print(f"❌ [red]{message}[/red]")


def print_warning(message: str):
    """Print warning message."""
    console.print(f"⚠️  [yellow]{message}[/yellow]")


def print_info(message: str):
    """Print info message."""
    console.print(f"ℹ️  [blue]{message}[/blue]")


def print_sql_panel(sql: str, title: str = "Generated SQL"):
    """Print SQL in a panel with syntax highlighting."""
    syntax = format_sql(sql)
    panel = Panel(syntax, title=title, border_style="green")
    console.print(panel)


def print_explanation(explanation: str):
    """Print query explanation."""
    md = Markdown(explanation)
    panel = Panel(md, title="📖 Query Explanation", border_style="blue")
    console.print(panel)


def print_validation_result(is_valid: bool, warnings: List[str] = None):
    """Print validation result."""
    if is_valid:
        print_success("Query validated successfully")
    else:
        print_error("Query validation failed")
    
    if warnings:
        for warning in warnings:
            print_warning(warning)


def export_to_csv(results: List[Dict[str, Any]], filename: str):
    """Export results to CSV file."""
    import csv
    
    if not results:
        print_warning("No results to export")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print_success(f"Results exported to {filename}")


def export_to_json(results: List[Dict[str, Any]], filename: str):
    """Export results to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print_success(f"Results exported to {filename}")
