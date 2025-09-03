"""Middleware components for Campaign Service."""
from datetime import datetime
from typing import Any, Callable, Dict, Optional
from uuid import UUID, uuid4

import structlog
from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware

from src.core.settings import Settings

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total count of HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

CAMPAIGN_OPERATIONS = Counter(
    "campaign_operations_total",
    "Total count of campaign operations",
    ["operation_type"],
)

CHAPTER_OPERATIONS = Counter(
    "chapter_operations_total",
    "Total count of chapter operations",
    ["operation_type"],
)

VERSION_OPERATIONS = Counter(
    "version_operations_total",
    "Total count of version control operations",
    ["operation_type"],
)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure each request has a unique ID."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = UUID(request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = str(request_id)
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging."""

    def __init__(self, app: FastAPI, settings: Settings) -> None:
        super().__init__(app)
        self.log = structlog.get_logger()
        self.settings = settings

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = datetime.utcnow()
        response = None
        error = None

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            error = e
            raise
        finally:
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            log_data = {
                "request_id": str(request.state.request_id),
                "method": request.method,
                "url": str(request.url),
                "duration": duration,
                "status_code": response.status_code if response else 500,
            }

            if error:
                log_data["error"] = str(error)
                if hasattr(error, "code"):
                    log_data["error_code"] = error.code

            if self.settings.debug:
                log_data["headers"] = dict(request.headers)
                log_data["query_params"] = dict(request.query_params)

            if response and response.status_code >= 400:
                self.log.error("request_failed", **log_data)
            else:
                self.log.info("request_processed", **log_data)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting request metrics."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        method = request.method
        endpoint = request.url.path

        with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
            response = await call_next(request)

            REQUEST_COUNT.labels(
                method=method, endpoint=endpoint, status=response.status_code
            ).inc()

            return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""

    def __init__(
        self, app: FastAPI, settings: Settings, storage: Optional[Dict] = None
    ) -> None:
        super().__init__(app)
        self.settings = settings
        self.storage = storage or {}
        self.log = structlog.get_logger()

    async def _get_rate_limit_key(self, request: Request) -> str:
        """Get key for rate limiting."""
        # Use API token or IP address as key
        if "Authorization" in request.headers:
            return request.headers["Authorization"]
        return request.client.host if request.client else "unknown"

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        key = await self._get_rate_limit_key(request)
        now = datetime.utcnow()

        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        # Initialize or cleanup old window
        if key not in self.storage:
            self.storage[key] = {"count": 0, "window": now}
        elif (now - self.storage[key]["window"]).total_seconds() > 60:
            self.storage[key] = {"count": 0, "window": now}

        # Check rate limit
        if self.storage[key]["count"] >= self.settings.rate_limit_rpm:
            self.log.warning("rate_limit_exceeded", key=key)
            return Response(
                status_code=429,
                content={"error": "Rate limit exceeded"},
            )

        # Increment counter
        self.storage[key]["count"] += 1
        return await call_next(request)


def setup_middleware(app: FastAPI, settings: Settings) -> None:
    """Configure all middleware for the application."""
    
    # Add CORS middleware first
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Request ID middleware
    app.add_middleware(RequestIdMiddleware)

    # Rate limiting
    app.add_middleware(RateLimitMiddleware, settings=settings)

    # Add metrics middleware if enabled
    if settings.metrics_enabled:
        app.add_middleware(MetricsMiddleware)

    # Logging middleware last to capture everything
    app.add_middleware(LoggingMiddleware, settings=settings)
