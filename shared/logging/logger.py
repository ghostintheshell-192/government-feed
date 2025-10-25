"""Centralized logging configuration for the application."""

import logging
import sys


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Create and configure a logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper()))

    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    # Format: [2025-01-25 10:30:45] [INFO] [module_name] Message
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance with default configuration.

    Args:
        name: Logger name (use __name__ for automatic module naming)

    Returns:
        Configured logger instance

    Example:
        >>> from shared.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
    """
    return setup_logger(name)
