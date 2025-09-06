import logging
import time
from typing import Callable, Dict

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = None
        status_code = 500  # Default to error status
        
        # Extract request details
        request_id = request.headers.get("X-Request-ID", "")
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
            
        except Exception as e:
            logger.error("Request failed",
                error=str(e),
                request_id=request_id,
                client_ip=client_ip,
                method=method,
                path=path
            )
            raise
            
        finally:
            # Calculate request duration
            duration = time.time() - start_time
            
            # Log request details
            log_data = {
                "request_id": request_id,
                "client_ip": client_ip,
                "method": method,
                "path": path,
                "query_params": query_params,
                "status_code": status_code,
                "duration": duration,
                "user_agent": request.headers.get("User-Agent", ""),
            }
            
            if 200 <= status_code < 400:
                logger.info("Request completed", **log_data)
            elif 400 <= status_code < 500:
                logger.warning("Client error", **log_data)
            else:
                logger.error("Server error", **log_data)


def get_request_logger(request_id: str) -> structlog.BoundLogger:
    """Get a logger instance bound with request context."""
    return logger.bind(request_id=request_id)


class ErrorLogger:
    """Error logging utility."""
    
    @staticmethod
    def log_error(
        error: Exception,
        request: Request = None,
        context: Dict = None
    ) -> None:
        """Log an error with request and context details."""
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        
        if request:
            error_data.update({
                "request_id": request.headers.get("X-Request-ID", ""),
                "client_ip": request.client.host if request.client else "unknown",
                "method": request.method,
                "path": request.url.path,
                "user_agent": request.headers.get("User-Agent", "")
            })
        
        logger.error("Application error", **error_data)
