#!/usr/bin/env python3
"""
Character Service - D&D Character Creator

This service provides character creation, management, and evolution functionality
for the D&D Character Creator platform.

Features:
- AI-powered character creation
- Custom content generation
- Character management and evolution
- Journal system
- Version control
- Campaign theme integration
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from structlog import get_logger

from character.api import router as api_router
from character.core.config import Settings
from character.core.logging_config import configure_logging
from character.core.metrics_middleware import PrometheusMiddleware
from character.core.startup import (
    initialize_database,
    initialize_message_hub,
    initialize_metrics,
    shutdown_database,
    shutdown_message_hub,
)

logger = get_logger()
settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting character service", version=settings.version)
    
    await initialize_database()
    await initialize_message_hub()
    initialize_metrics()
    
    yield
    
    # Shutdown
    logger.info("Shutting down character service")
    await shutdown_database()
    await shutdown_message_hub()

def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Character Service API",
        description="API for D&D Character Creator character management",
        version=settings.version,
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add Prometheus middleware
    app.add_middleware(PrometheusMiddleware)
    
    # Mount Prometheus metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    # Add API router
    app.include_router(api_router, prefix="/api/v2")
    
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.version,
            "dependencies": {
                "message_hub": "healthy",  # TODO: Add actual health check
                "database": "healthy",     # TODO: Add actual health check
                "llm_service": "healthy"   # TODO: Add actual health check
            }
        }
    
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Add unique request ID to each request."""
        request_id = request.headers.get("X-Request-ID", None)
        if not request_id:
            import uuid
            request_id = str(uuid.uuid4())
            request.headers.__dict__["_list"].append(
                (b"x-request-id", request_id.encode())
            )
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    
    return app

# Create application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    configure_logging()
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
