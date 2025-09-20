"""FastAPI middleware for metrics collection."""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from metrics_service.core.metrics import registry, HTTP_REQUEST_DURATION, HTTP_REQUESTS_TOTAL, ACTIVE_REQUESTS

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics collection for the metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        path = request.url.path

        # Track active requests
        active_requests = registry.gauge(ACTIVE_REQUESTS)
        active_requests.labels(method=method, path=path).inc()

        # Time the request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status = str(response.status_code)
        except Exception as exc:
            status = "500"
            raise exc
        finally:
            # Record metrics
            duration = time.time() - start_time
            registry.histogram(HTTP_REQUEST_DURATION).labels(
                method=method, path=path, status=status
            ).observe(duration)
            
            registry.counter(HTTP_REQUESTS_TOTAL).labels(
                method=method, path=path, status=status
            ).inc()
            
            active_requests.labels(method=method, path=path).dec()

        return response