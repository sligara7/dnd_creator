from datetime import datetime
from typing import Awaitable, Callable, Dict, Optional
from uuid import UUID, uuid4

import structlog
from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp

from llm_service.core.exceptions import ErrorDetail, ErrorResponse, LLMServiceError
from llm_service.core.settings import Settings

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


class HeaderMiddleware(BaseHTTPMiddleware):
    """Middleware to add custom headers to responses."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        # Add custom headers if set in request state
        if hasattr(request.state, "response_headers"):
            for key, value in request.state.response_headers.items():
                response.headers[key] = value

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging of requests/responses."""

    def __init__(self, app: ASGIApp, settings: Settings) -> None:
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
                if isinstance(error, LLMServiceError):
                    log_data["error_code"] = error.error_code
                    log_data["error_details"] = error.error_details

            if self.settings.debug:
                log_data["headers"] = dict(request.headers)
                log_data["query_params"] = dict(request.query_params)

            if response and response.status_code >= 400:
                self.log.error("request_failed", **log_data)
            else:
                self.log.info("request_processed", **log_data)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting request/response metrics."""

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


def setup_middleware(app: FastAPI, settings: Settings) -> None:
    """Configure middleware for the application."""

    # Add header middleware first
    app.add_middleware(HeaderMiddleware)
    """Configure middleware for the application."""
    
    # Add CORS middleware first
    if settings.allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Request ID middleware
    app.add_middleware(RequestIdMiddleware)

    # Add metrics middleware if enabled
    if settings.metrics_enabled:
        app.add_middleware(MetricsMiddleware)

    # Logging middleware
    app.add_middleware(LoggingMiddleware, settings=settings)


async def error_handler(
    request: Request, exc: LLMServiceError
) -> ErrorResponse:
    """Global error handler for LLM service exceptions."""
    error_detail = ErrorDetail(
        request_id=str(request.state.request_id),
        timestamp=datetime.utcnow().isoformat(),
    )

    return ErrorResponse(
        error={
            "code": exc.error_code,
            "message": exc.detail["message"],
            "details": {
                **exc.error_details,
                **error_detail.dict(),
            },
        }
    )
