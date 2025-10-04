"""Logging utilities for the PR Reviewer Agent."""
import logging
from pathlib import Path
from typing import Optional

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> None:
    """Setup logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file. If None, logs to console only
        format_string: Custom format string for logs
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(),
            *(
                [logging.FileHandler(log_file)]
                if log_file
                else []
            )
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.

    Args:
        name: Name for the logger

    Returns:
        Logger instance
    """
    return logging.getLogger(name)