"""
Centralized logging configuration.

This module sets up structured logging for the application with
appropriate formatting and log levels.
"""

import logging
import sys
from typing import Any

from back.shared.core.config import settings


def setup_logging() -> None:
    """
    Configure application logging.

    Sets up structured logging with appropriate format and level
    based on environment (development vs production).
    """
    log_level = logging.DEBUG if settings.debug else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the module (usually __name__).

    Returns:
        Logger instance configured for the module.

    Usage:
        logger = get_logger(__name__)
        logger.info("Something happened")
    """
    return logging.getLogger(name)


# Initialize logging on module import
setup_logging()
