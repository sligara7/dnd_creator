"""
Logging Configuration

This module configures structured logging for the character service using structlog.
"""

import logging
import sys
from typing import Any, Dict

import structlog

from .config import get_settings

settings = get_settings()

def configure_logging() -> None:
    """Configure structured logging for the service."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.log_level,
    )

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log_format == "json":
        shared_processors.append(structlog.processors.JSONRenderer())
    else:
        shared_processors.append(
            structlog.processors.ConsoleRenderer(
                colors=settings.debug,
                exception_formatter=structlog.processors.ExceptionRenderer(),
            )
        )

    structlog.configure(
        processors=shared_processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        cache_logger_on_first_use=True,
    )

def get_logger(**initial_values: Dict[str, Any]) -> structlog.BoundLogger:
    """Get a structured logger with initial values."""
    logger = structlog.get_logger()
    if initial_values:
        logger = logger.bind(**initial_values)
    return logger
