"""
Metrics Middleware

FastAPI middleware for tracking request metrics and timings.
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from src.core.logging_config import get_logger
from src.services.metrics_service import get_metrics_service
from src.models.database_models import get_db

logger = get_logger(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting request metrics."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Get database session
        self.db = next(get_db())
        self.metrics_service = get_metrics_service(self.db)
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and record metrics."""
        path = request.url.path
        start_time = time.time()
        error = None
        
        try:
            response = await call_next(request)
            
            # Record error if response indicates one
            if response.status_code >= 400:
                error = f"HTTP {response.status_code}"
            
            return response
            
        except Exception as e:
            # Record unhandled errors
            error = type(e).__name__
            raise
            
        finally:
            # Calculate request duration
            duration = time.time() - start_time
            
            # Record metrics
            self.metrics_service.record_request(
                path=path,
                duration=duration,
                error=error
            )
            
            # Log request details
            log_data = {
                "path": path,
                "method": request.method,
                "duration": duration,
                "status": response.status_code if 'response' in locals() else 500
            }
            if error:
                log_data["error"] = error
                logger.warning("request_completed", **log_data)
            else:
                logger.info("request_completed", **log_data)

def setup_metrics(app):
    """Configure metrics collection for the application."""
    # Add metrics middleware
    app.add_middleware(MetricsMiddleware)
    
    # Start metrics collection on startup
    @app.on_event("startup")
    async def start_metrics():
        logger.info("starting_metrics_collection")
        db = next(get_db())
        metrics_service = get_metrics_service(db)
        await metrics_service.start_collection()
    
    # Stop metrics collection on shutdown
    @app.on_event("shutdown")
    async def stop_metrics():
        logger.info("stopping_metrics_collection")
        db = next(get_db())
        metrics_service = get_metrics_service(db)
        await metrics_service.stop_collection()
