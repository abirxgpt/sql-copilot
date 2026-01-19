"""Comprehensive logging setup for SQL Copilot with file and console handlers."""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import colorlog
from pythonjsonlogger import jsonlogger


class SQLCopilotLogger:
    """Custom logger with both console and file output."""
    
    def __init__(self, name: str = "sql_copilot", log_file: Optional[str] = None, log_level: str = "DEBUG"):
        self.name = name
        self.log_file = log_file
        self.log_level = getattr(logging, log_level.upper(), logging.DEBUG)
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logger with console and file handlers."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Console handler with colors
        console_handler = self._create_console_handler()
        logger.addHandler(console_handler)
        
        # File handler with JSON format
        if self.log_file:
            file_handler = self._create_file_handler()
            logger.addHandler(file_handler)
        
        return logger
    
    def _create_console_handler(self) -> logging.Handler:
        """Create colored console handler."""
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # Color formatter
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(formatter)
        return console_handler
    
    def _create_file_handler(self) -> logging.Handler:
        """Create JSON file handler for structured logging."""
        # Ensure log directory exists
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        
        # JSON formatter for structured logs
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s',
            timestamp=True
        )
        file_handler.setFormatter(formatter)
        return file_handler
    
    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger


# Convenience functions for different components
def get_logger(component_name: str) -> logging.Logger:
    """Get a logger for a specific component."""
    from config.settings import settings
    
    logger_instance = SQLCopilotLogger(
        name=f"sql_copilot.{component_name}",
        log_file=settings.log_file,
        log_level=settings.log_level
    )
    return logger_instance.get_logger()


# Create main logger
def setup_logging():
    """Initialize logging system."""
    from config.settings import settings
    
    main_logger = SQLCopilotLogger(
        name="sql_copilot",
        log_file=settings.log_file,
        log_level=settings.log_level
    )
    
    logger = main_logger.get_logger()
    logger.info("=" * 80)
    logger.info("SQL Copilot Starting")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info(f"Log File: {settings.log_file}")
    logger.info("=" * 80)
    
    return logger
