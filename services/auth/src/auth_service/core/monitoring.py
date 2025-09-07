"""Monitoring and metrics for Auth Service."""

from typing import Dict, Any
import time
from functools import wraps
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
)
import structlog
from fastapi import Response

# Create custom registry
registry = CollectorRegistry()

# Metrics definitions
auth_requests_total = Counter(
    "auth_requests_total",
    "Total number of authentication requests",
    ["method", "endpoint", "status"],
    registry=registry,
)

auth_request_duration_seconds = Histogram(
    "auth_request_duration_seconds",
    "Authentication request duration in seconds",
    ["method", "endpoint"],
    registry=registry,
)

active_sessions = Gauge(
    "auth_active_sessions",
    "Number of active sessions",
    registry=registry,
)

active_users = Gauge(
    "auth_active_users",
    "Number of active users",
    registry=registry,
)

login_attempts = Counter(
    "auth_login_attempts_total",
    "Total number of login attempts",
    ["result"],  # success, failure, locked
    registry=registry,
)

token_operations = Counter(
    "auth_token_operations_total",
    "Token operations",
    ["operation", "token_type", "result"],
    registry=registry,
)

mfa_operations = Counter(
    "auth_mfa_operations_total",
    "MFA operations",
    ["operation", "result"],
    registry=registry,
)

api_key_operations = Counter(
    "auth_api_key_operations_total",
    "API key operations",
    ["operation", "result"],
    registry=registry,
)

permission_checks = Counter(
    "auth_permission_checks_total",
    "Permission check operations",
    ["resource", "action", "result"],
    registry=registry,
)

password_operations = Counter(
    "auth_password_operations_total",
    "Password operations",
    ["operation", "result"],
    registry=registry,
)

security_events = Counter(
    "auth_security_events_total",
    "Security events",
    ["event_type", "severity"],
    registry=registry,
)

# Logger setup
logger = structlog.get_logger()


def track_request_metrics(method: str, endpoint: str, status: int, duration: float):
    """Track request metrics."""
    auth_requests_total.labels(
        method=method,
        endpoint=endpoint,
        status=str(status),
    ).inc()
    
    auth_request_duration_seconds.labels(
        method=method,
        endpoint=endpoint,
    ).observe(duration)


def track_login_attempt(result: str):
    """Track login attempt."""
    login_attempts.labels(result=result).inc()


def track_token_operation(operation: str, token_type: str, result: str):
    """Track token operation."""
    token_operations.labels(
        operation=operation,
        token_type=token_type,
        result=result,
    ).inc()


def track_mfa_operation(operation: str, result: str):
    """Track MFA operation."""
    mfa_operations.labels(
        operation=operation,
        result=result,
    ).inc()


def track_api_key_operation(operation: str, result: str):
    """Track API key operation."""
    api_key_operations.labels(
        operation=operation,
        result=result,
    ).inc()


def track_permission_check(resource: str, action: str, result: str):
    """Track permission check."""
    permission_checks.labels(
        resource=resource,
        action=action,
        result=result,
    ).inc()


def track_password_operation(operation: str, result: str):
    """Track password operation."""
    password_operations.labels(
        operation=operation,
        result=result,
    ).inc()


def track_security_event(event_type: str, severity: str):
    """Track security event."""
    security_events.labels(
        event_type=event_type,
        severity=severity,
    ).inc()


def update_active_sessions(count: int):
    """Update active sessions gauge."""
    active_sessions.set(count)


def update_active_users(count: int):
    """Update active users gauge."""
    active_users.set(count)


def measure_time(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                f"Function executed",
                function=func.__name__,
                duration=duration,
                status="success",
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Function failed",
                function=func.__name__,
                duration=duration,
                status="error",
                error=str(e),
            )
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                f"Function executed",
                function=func.__name__,
                duration=duration,
                status="success",
            )
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Function failed",
                function=func.__name__,
                duration=duration,
                status="error",
                error=str(e),
            )
            raise
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


async def setup_monitoring():
    """Initialize monitoring systems."""
    logger.info("Setting up monitoring")
    
    # Initialize metrics
    update_active_sessions(0)
    update_active_users(0)
    
    logger.info("Monitoring setup complete")


async def get_metrics() -> Response:
    """Generate Prometheus metrics."""
    metrics = generate_latest(registry)
    return Response(
        content=metrics,
        media_type=CONTENT_TYPE_LATEST,
    )


def get_health_status() -> Dict[str, Any]:
    """Get service health status."""
    return {
        "status": "healthy",
        "metrics": {
            "active_sessions": active_sessions._value.get(),
            "active_users": active_users._value.get(),
        },
    }
