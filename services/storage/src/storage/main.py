"""Storage Service Main Application."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from storage.core.config import settings
from storage.core.database import db_manager
from storage.integrations.s3_client import storage_client
from storage.api import assets, versions, policies, backups, health
from storage.utils.logging import setup_logging


# Set up logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Storage Service...")
    
    # Initialize database
    await db_manager.init()
    logger.info("Database initialized")
    
    # Ensure S3 bucket exists
    await storage_client.ensure_bucket_exists()
    logger.info("S3 storage initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Storage Service...")
    await db_manager.close()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="Storage Service",
    description="Binary asset storage and management service for D&D Character Creator",
    version=settings.service_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Add Prometheus metrics endpoint
if settings.metrics_enabled:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(
    assets.router,
    prefix=f"{settings.api_prefix}/assets",
    tags=["Assets"],
)
app.include_router(
    versions.router,
    prefix=f"{settings.api_prefix}/versions",
    tags=["Versions"],
)
app.include_router(
    policies.router,
    prefix=f"{settings.api_prefix}/policies",
    tags=["Policies"],
)
app.include_router(
    backups.router,
    prefix=f"{settings.api_prefix}/backups",
    tags=["Backups"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "storage.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
    )
