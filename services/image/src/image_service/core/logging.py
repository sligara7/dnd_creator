"""Logging configuration for the image service."""

import json
import logging
from functools import partial
from typing import Any

from image_service.core.config import get_settings

settings = get_settings()


class JSONFormatter(logging.Formatter):
    """JSON log formatter."""

    def __init__(self, **kwargs):
        super().__init__()
        self.default_fields = {
            "service": settings.SERVICE_NAME,
            "version": settings.VERSION,
            **kwargs,
        }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Base log data
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            **self.default_fields,
        }

        # Add extra fields from record
        if hasattr(record, "props"):
            log_data.update(record.props)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging() -> None:
    """Set up logging configuration."""
    # Create handlers
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)
    root_logger.addHandler(console_handler)

    # Create service logger
    service_logger = logging.getLogger("image_service")
    service_logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)
    

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    logger = logging.getLogger(f"image_service.{name}")
    
    # Add convenience methods for structured logging
    def log_with_props(level: int, msg: str, **kwargs: Any) -> None:
        """Log a message with additional properties."""
        if logger.isEnabledFor(level):
            record = logging.LogRecord(
                name=logger.name,
                level=level,
                pathname="",
                lineno=0,
                msg=msg,
                args=(),
                exc_info=None,
            )
            record.props = kwargs
            logger.handle(record)

    logger.debug_props = partial(log_with_props, logging.DEBUG)
    logger.info_props = partial(log_with_props, logging.INFO)
    logger.warning_props = partial(log_with_props, logging.WARNING)
    logger.error_props = partial(log_with_props, logging.ERROR)
    logger.critical_props = partial(log_with_props, logging.CRITICAL)

    return logger
