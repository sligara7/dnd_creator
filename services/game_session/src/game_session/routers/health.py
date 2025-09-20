"""Game Session Service - Health Check Router.

This module implements the health check endpoints.
"""
from typing import Dict, List

from fastapi import APIRouter, Depends, Request
from prometheus_client import Histogram
from structlog import get_logger

from game_session.api.dependencies import SettingsDep
from game_session.core.config import Settings

router = APIRouter()
logger = get_logger(__name__)

# Metrics
HEALTH_CHECK_LATENCY = Histogram(
    "game_session_health_check_latency_seconds",
    "Health check latency in seconds",
    ["check_type"],
)


@router.get("/health")
async def health_check(
    request: Request,
    settings: SettingsDep,
) -> Dict:
    """Health check endpoint.

    Returns:
        Health status information.
    """
    overall_status = "healthy"
    checks: List[Dict] = []

    # Check Redis
    redis_client = request.app.state.redis
    try:
        with HEALTH_CHECK_LATENCY.labels("redis").time():
            redis_healthy = await redis_client.check_health()
            checks.append({
                "component": "redis",
                "status": "healthy" if redis_healthy else "unhealthy",
            })
            if not redis_healthy:
                overall_status = "unhealthy"
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        checks.append({
            "component": "redis",
            "status": "unhealthy",
            "error": str(e),
        })
        overall_status = "unhealthy"

    # Check Message Hub
    message_hub = request.app.state.message_hub
    try:
        with HEALTH_CHECK_LATENCY.labels("message_hub").time():
            # Just verify we have an active connection
            if message_hub.connection and message_hub.connection.is_closed:
                checks.append({
                    "component": "message_hub",
                    "status": "unhealthy",
                    "error": "Connection closed",
                })
                overall_status = "unhealthy"
            else:
                checks.append({
                    "component": "message_hub",
                    "status": "healthy",
                })
    except Exception as e:
        logger.error("Message Hub health check failed", error=str(e))
        checks.append({
            "component": "message_hub",
            "status": "unhealthy",
            "error": str(e),
        })
        overall_status = "unhealthy"

    # Check WebSocket connections
    websocket_manager = request.app.state.websocket_manager
    with HEALTH_CHECK_LATENCY.labels("websocket").time():
        total_connections = sum(
            len(connections) 
            for connections in websocket_manager.active_connections.values()
        )
        checks.append({
            "component": "websocket",
            "status": "healthy",
            "details": {
                "active_sessions": len(websocket_manager.active_connections),
                "total_connections": total_connections,
            },
        })

    # Service state
    session_count = len(request.app.state.sessions)
    checks.append({
        "component": "service_state",
        "status": "healthy",
        "details": {
            "active_sessions": session_count,
        },
    })

    return {
        "status": overall_status,
        "checks": checks,
    }


@router.get("/health/liveness")
async def liveness_check() -> Dict:
    """Liveness probe endpoint.

    A basic check that returns success if the service is running and able to accept requests.

    Returns:
        Basic health status.
    """
    return {"status": "healthy"}