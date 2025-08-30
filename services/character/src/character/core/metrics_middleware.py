"""
Prometheus Metrics Middleware

This module provides Prometheus metrics collection for the character service.
"""

import time
from typing import Tuple

from fastapi import Request, Response
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from structlog import get_logger

# Metrics
REQUEST_COUNT = Counter(
    "character_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "character_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

CHARACTER_CREATION_COUNT = Counter(
    "character_creations_total",
    "Total number of characters created",
    ["type", "status"],
)

CUSTOM_CONTENT_COUNT = Counter(
    "character_custom_content_total",
    "Total number of custom content items created",
    ["type", "status"],
)

JOURNAL_ENTRY_COUNT = Counter(
    "character_journal_entries_total",
    "Total number of journal entries created",
)

ERROR_COUNT = Counter(
    "character_errors_total",
    "Total number of errors",
    ["type"],
)

logger = get_logger()

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting Prometheus metrics."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and record metrics."""
        start_time = time.time()
        method = request.method
        url_path = request.url.path
        
        try:
            response = await call_next(request)
            status = response.status_code
            self._record_metrics(method, url_path, status, start_time)
            return response
        except Exception as e:
            self._record_error(e)
            raise
    
    def _record_metrics(
        self, method: str, path: str, status: int, start_time: float
    ) -> None:
        """Record request metrics."""
        endpoint = self._get_endpoint_name(path)
        duration = time.time() - start_time
        
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
    
    def _record_error(self, error: Exception) -> None:
        """Record error metrics."""
        error_type = type(error).__name__
        ERROR_COUNT.labels(type=error_type).inc()
        logger.error(
            "Request error",
            error_type=error_type,
            error=str(error),
        )
    
    def _get_endpoint_name(self, path: str) -> str:
        """Get a generic endpoint name for grouping metrics."""
        parts = path.strip("/").split("/")
        if len(parts) < 2:
            return path
        
        # Group character-specific endpoints
        if parts[0] == "api" and parts[1] == "v2":
            if len(parts) < 3:
                return path
            if parts[2] == "characters" and len(parts) > 3:
                return f"/api/v2/characters/{{id}}/{'/'.join(parts[4:])}"
            return f"/api/v2/{parts[2]}"
        
        return path

def record_character_creation(char_type: str, status: str = "success") -> None:
    """Record a character creation event."""
    CHARACTER_CREATION_COUNT.labels(type=char_type, status=status).inc()

def record_custom_content_creation(content_type: str, status: str = "success") -> None:
    """Record a custom content creation event."""
    CUSTOM_CONTENT_COUNT.labels(type=content_type, status=status).inc()

def record_journal_entry() -> None:
    """Record a journal entry creation."""
    JOURNAL_ENTRY_COUNT.inc()
