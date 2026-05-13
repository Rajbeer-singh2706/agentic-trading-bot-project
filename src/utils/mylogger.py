"""Logging configuration."""

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(
    name: str = __name__,
    log_level: str = None,
    log_file: str = None,
) -> logging.Logger:
    """Set up logger with file and console handlers.

    Args:
        name: Logger name
        log_level: Logging level (default: from LOG_LEVEL env var or INFO)
        log_file: Log file path (default: from LOG_FILE env var)

    Returns:
        Configured logger instance
    """
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO")
    log_file = log_file or os.getenv("LOG_FILE", "logs/app.log")

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))

    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(console_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
