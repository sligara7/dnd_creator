"""
Character Service Logging Configuration

This module provides centralized logging configuration for the character service,
with support for structured logging and standardized formatters.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional
import json
import structlog

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.environ.get("LOG_FORMAT", "json")  # "json" or "console"

def configure_logging() -> None:
    """Configure structured logging for the character service."""
    
    # Configure basic logging
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format="%(message)s"  # structlog will handle formatting
    )
    
    # Common processors
    shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]
    
    # Configure format-specific processors
    if LOG_FORMAT == "json":
        formatter = structlog.processors.JSONRenderer()
    else:
        formatter = structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.plain_traceback
        )
    
    structlog.configure(
        processors=shared_processors + [formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger for the given name."""
    return structlog.get_logger(name)

# Helper classes for structured logging

class ServiceEvent:
    """Base class for service-level events."""
    
    def __init__(self, event_type: str):
        self.event_type = event_type
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat()
        }

class CreationEvent(ServiceEvent):
    """Event class for object creation."""
    
    def __init__(self, 
                 creation_type: str,
                 object_id: str,
                 source_type: str = "custom",
                 **kwargs):
        super().__init__("creation")
        self.creation_type = creation_type
        self.object_id = object_id
        self.source_type = source_type
        self.extra = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "creation_type": self.creation_type,
            "object_id": self.object_id,
            "source_type": self.source_type
        })
        if self.extra:
            result["details"] = self.extra
        return result

class ValidationEvent(ServiceEvent):
    """Event class for validation operations."""
    
    def __init__(self,
                 validation_type: str,
                 success: bool,
                 object_id: Optional[str] = None,
                 errors: Optional[list] = None,
                 warnings: Optional[list] = None):
        super().__init__("validation")
        self.validation_type = validation_type
        self.success = success
        self.object_id = object_id
        self.errors = errors or []
        self.warnings = warnings or []
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "validation_type": self.validation_type,
            "success": self.success
        })
        if self.object_id:
            result["object_id"] = self.object_id
        if self.errors:
            result["errors"] = self.errors
        if self.warnings:
            result["warnings"] = self.warnings
        return result

class MigrationEvent(ServiceEvent):
    """Event class for migration operations."""
    
    def __init__(self,
                 migration_type: str,
                 items_migrated: int,
                 success: bool,
                 source_type: str = "official",
                 errors: Optional[list] = None):
        super().__init__("migration")
        self.migration_type = migration_type
        self.items_migrated = items_migrated
        self.success = success
        self.source_type = source_type
        self.errors = errors or []
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "migration_type": self.migration_type,
            "items_migrated": self.items_migrated,
            "success": self.success,
            "source_type": self.source_type
        })
        if self.errors:
            result["errors"] = self.errors
        return result

class DatabaseEvent(ServiceEvent):
    """Event class for database operations."""
    
    def __init__(self,
                 operation: str,
                 table: str,
                 success: bool,
                 record_count: Optional[int] = None,
                 error: Optional[str] = None):
        super().__init__("database")
        self.operation = operation
        self.table = table
        self.success = success
        self.record_count = record_count
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            "operation": self.operation,
            "table": self.table,
            "success": self.success
        })
        if self.record_count is not None:
            result["record_count"] = self.record_count
        if self.error:
            result["error"] = self.error
        return result

# Configure logging on module import
configure_logging()
