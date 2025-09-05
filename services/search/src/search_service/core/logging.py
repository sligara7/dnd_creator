import logging
import sys
from datetime import datetime
from typing import Any, Dict

from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from search_service.core.config import settings


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: Dict[str, Any]) -> str:
    """
    Custom format for loguru loggers.
    Uses same format as default but adds extra fields for structured logging.
    """
    format_string = LOGURU_FORMAT
    
    if record["extra"].get("request_id"):
        format_string = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " \
                       "<level>{level: <8}</level> | " \
                       "<cyan>request_id={extra[request_id]}</cyan> | " \
                       "<level>{message}</level>\n"

    if record["extra"].get("timestamp"):
        format_string = format_string.replace(
            "{time:YYYY-MM-DD HH:mm:ss.SSS}",
            "{extra[timestamp]}"
        )
    
    # Add extra context fields
    extra_fields = [
        "index",
        "operation",
        "query",
        "duration_ms",
        "cache_hit",
        "result_count",
    ]
    for field in extra_fields:
        if field in record["extra"]:
            format_string = format_string.replace(
                "{message}",
                f"{{{field}}}={record['extra'][field]} | " + "{message}"
            )
    
    # Format exception if present
    if record["exception"]:
        format_string = format_string.replace(
            "{message}",
            "{message}\n{exception}"
        )

    return format_string


def setup_logging() -> None:
    """Configure logging"""
    
    # Remove all existing handlers
    logging.root.handlers = []
    
    # Stop propagation of logs to root logger
    logging.root.propagate = False
    
    # Clear loguru default handler
    logger.configure(handlers=[])
    
    # Configure log level based on settings
    log_level = settings.LOG_LEVEL.upper()
    
    # Add console handler
    logger.add(
        sys.stderr,
        level=log_level,
        format=format_record,
        colorize=True,
        backtrace=True,
        diagnose=True,
        catch=True,
        enqueue=True,
    )
    
    # Add JSON file handler for structured logging
    logger.add(
        "logs/search_service.json",
        level=log_level,
        format="{time} {level} {message}",
        serialize=True,  # Output as JSON
        rotation="100 MB",  # Rotate at 100MB
        retention="7 days",  # Keep logs for 7 days
        compression="gz",  # Compress rotated files
        backtrace=True,
        diagnose=True,
        catch=True,
        enqueue=True,
    )
    
    # Add plain text file handler for human-readable logs
    logger.add(
        "logs/search_service.log",
        level=log_level,
        format=format_record,
        rotation="100 MB",
        retention="7 days",
        compression="gz",
        backtrace=True,
        diagnose=True,
        catch=True,
        enqueue=True,
    )
    
    # Intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(log_level)
    
    # Remove other loggers' handlers
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    
    logger.configure(
        handlers=[{"sink": sys.stdout, "format": format_record}]
    )
    
    # Log configuration completion
    logger.info(
        "Logging configured",
        extra={
            "timestamp": datetime.utcnow().isoformat(),
            "level": log_level,
            "service": settings.SERVICE_NAME,
            "version": settings.VERSION,
        }
    )
