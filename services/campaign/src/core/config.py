"""Configuration wrapper for campaign service."""

import logging
from .settings import settings


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
