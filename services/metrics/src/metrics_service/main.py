"""Main FastAPI application module."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from prometheus_client import make_asgi_app
from metrics_service.config import ServiceConfig
from metrics_service.routers import metrics, alerts, dashboards, health
from metrics_service.core.middleware import MetricsMiddleware
from metrics_service.core.message_client import MessageClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Initialize services
    config = ServiceConfig.from_env(**os.environ)
    app.state.service_config = config

    # Initialize Message Hub client (all external comms via hub per ARCHITECTURE.json)
    message_client = MessageClient(config)
    await message_client.connect()
    app.state.message_client = message_client

    try:
        yield
    finally:
        # Cleanup services
        client = getattr(app.state, "message_client", None)
        if client:
            await client.close()

async def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Create FastAPI app
    app = FastAPI(
        title="Metrics Service",
        description="Metrics collection and monitoring for D&D Character Creator",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Load configuration
    config = ServiceConfig.from_env(**os.environ)

    # Mount Prometheus metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    # Add middleware
    app.add_middleware(MetricsMiddleware)

    # Include routers
    app.include_router(metrics.router, prefix="/api/v2/metrics", tags=["metrics"])
    app.include_router(alerts.router, prefix="/api/v2/alerts", tags=["alerts"])
    app.include_router(dashboards.router, prefix="/api/v2/dashboards", tags=["dashboards"])
    app.include_router(health.router, tags=["health"])

    return app

app = create_app()