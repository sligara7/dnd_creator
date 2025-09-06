"""Character Service - FastAPI Application Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from character_service.api.v2.lifecycle import lifespan
from character_service.api.v2.router import router as api_v2_router
from character_service.config import get_settings
from character_service.core.openapi import configure_openapi


settings = get_settings()


def create_application() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="D&D Character Service",
        description="Character Creation and Management for D&D 5e 2024",
        version="2.0.0",
        lifespan=lifespan,
    )

    # CORS middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configure OpenAPI documentation
    configure_openapi(app)

    # Configure documentation UI
    app.docs_url = "/docs"               # Swagger UI
    app.redoc_url = "/redoc"           # ReDoc UI
    app.openapi_url = "/openapi.json"  # Raw OpenAPI Schema

    # Mount the v2 API router
    app.include_router(api_v2_router, prefix="/api/v2")

    return app

# Create the application instance
app = create_application()
