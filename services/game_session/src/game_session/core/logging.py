"""Game Session Service Logging Configuration.

This module configures structured logging for the service using structlog
and python-json-logger.
"""
import logging
import sys
from typing import Any, Dict

from pythonjsonlogger import jsonlogger
import structlog
from structlog import configure
from structlog.stdlib import ProcessorFormatter, add_log_level
from structlog.types import Processor

from game_session.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure service logging.

    Args:
        settings: Service configuration settings.
    """
    # Configure structlog processors
    processors: list[Processor] = [
        add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.LOG_FORMAT == "json":
        # Add JSON formatter for production
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Add console formatter for development
        processors.append(structlog.dev.ConsoleRenderer())

    configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    handler = logging.StreamHandler(sys.stdout)
    if settings.LOG_FORMAT == "json":
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
        handler.setFormatter(formatter)
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(settings.LOG_LEVEL)

    # Set levels for third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("websockets").setLevel(logging.INFO)


def get_request_id(request: Any) -> str:
    """Get request ID from FastAPI request object.

    Args:
        request: FastAPI request object.

    Returns:
        Request ID string.
    """
    if hasattr(request.state, "request_id"):
        return request.state.request_id
    return "unknown"


def get_correlation_context(request: Any = None) -> Dict[str, Any]:
    """Get correlation context for logging.

    Args:
        request: Optional FastAPI request object.

    Returns:
        Dictionary with correlation context.
    """
    context = {
        "service": "game-session",
    }

    if request:
        context.update({
            "request_id": get_request_id(request),
            "method": request.method,
            "path": request.url.path,
        })

    return context