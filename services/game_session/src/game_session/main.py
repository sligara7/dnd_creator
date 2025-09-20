"""
Game Session Service

Main application module that initializes and configures the FastAPI application
and WebSocket server.
"""
import logging
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import REGISTRY, Counter, Histogram
from structlog import get_logger

from game_session.core.config import Settings, get_settings
from game_session.core.events import create_start_app_handler, create_stop_app_handler
from game_session.core.logging import configure_logging
from game_session.routers import health, sessions, websocket

logger = get_logger(__name__)

# Metrics
REQUESTS = Counter(
    "game_session_http_requests_total",
    "Total count of HTTP requests by method and path",
    ["method", "path"],
)

WEBSOCKET_CONNECTIONS = Counter(
    "game_session_websocket_connections_total",
    "Total count of WebSocket connections",
)

WEBSOCKET_MESSAGES = Counter(
    "game_session_websocket_messages_total",
    "Total count of WebSocket messages by type",
    ["message_type"],
)

LATENCY = Histogram(
    "game_session_request_latency_seconds",
    "Request latency in seconds",
    ["method", "path"],
)

def create_app(settings: Settings = get_settings()) -> FastAPI:
    """Create and configure the FastAPI application."""
    configure_logging(settings)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add startup and shutdown handlers
    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))

    # Add routers
    app.include_router(health.router, tags=["health"])
    app.include_router(sessions.router, prefix="/api/v2/sessions", tags=["sessions"])
    app.include_router(websocket.router, prefix="/api/v2/sessions", tags=["websocket"])

    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}

    logger.info("Application initialized")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
