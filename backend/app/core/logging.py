"""
Logging setup for the Document Parser application.
Provides centralized structured logging using Loguru.
"""

import sys
from loguru import logger
from pathlib import Path

# Import settings from the configuration module
from app.core.config import get_settings

# Get global settings
settings = get_settings()


# Ensure the log directory exists
log_file_path = Path(settings.log_file)
log_file_path.parent.mkdir(parents=True, exist_ok=True)


# Configure Loguru logger
logger.remove()
logger.add(sys.stdout, level=settings.log_level.upper(), format="{time} - {level} - {message}")
logger.add(str(log_file_path), level=settings.log_level.upper(), rotation="10 MB", retention="3 months", enqueue=True)


# Aliases for common log levels
log_debug = logger.debug
log_info = logger.info
log_warning = logger.warning
log_error = logger.error
log_critical = logger.critical


# Utility function to log exceptions
def log_exception(exception: Exception, context: str = ""):
    """
    Log an exception with context information.

    Args:
        exception (Exception): The exception to log.
        context (str): Additional context information.
    """
    logger.exception(f"Exception occurred in {context}: {exception}")


# Set level functions
def set_log_level(level: str):
    """
    Dynamically set the log level.

    Args:
        level (str): The new log level (e.g., 'DEBUG', 'INFO').
    """
    log_level_int = logger.level(level.upper()).no
    logger.remove()
    logger.add(sys.stdout, level=log_level_int, format="{time} - {level} - {message}")
    logger.add(str(log_file_path), level=log_level_int, rotation="10 MB", retention="3 months", enqueue=True)


def setup_logging():
    """
    Setup logging configuration.
    """
    # Already configured above, just return
    logger.info("Logging initialized")


# Example usage: log_info("Application started")
