from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from search_service.security.security import SecurityService
from search_service.security.middleware import add_security

from search_service.api.routes import api_router
from search_service.api.dependencies import start_clients, close_clients
from search_service.core.config import settings
from search_service.core.exceptions import (
    SearchServiceError,
    handle_search_service_error,
    setup_exception_handlers,
)
from search_service.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Initialize service components
    setup_logging()
    await start_clients()
    
    # Start application
    yield
    
    # Cleanup on shutdown
    await close_clients()


def create_application() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="D&D Search Service",
        description="Search service for D&D character creation and campaign management system",
        version=settings.VERSION,
        lifespan=lifespan,
    )

    # Configure CORS
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Set up exception handlers
    setup_exception_handlers(app)
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Set up monitoring
    if settings.COLLECT_DETAILED_METRICS:
        Instrumentator().instrument(app).expose(app)
    
    return app


app = create_application()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )
