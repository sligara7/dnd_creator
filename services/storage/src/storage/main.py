"""Storage Service Main Application."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from prometheus_client import make_asgi_app

from storage.core.exceptions import (
    StorageException, AssetNotFoundException, AssetAlreadyExistsException,
    ValidationError, S3StorageException
)
from storage.api.openapi.examples import MODELS, ERROR_EXAMPLES

from storage.core.config import settings
from storage.core.database import db_manager
from storage.integrations.s3_client import storage_client
from storage.api import assets, versions, policies, backups, health, image_storage
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
    description="""Binary asset storage and management service for D&D Character Creator.

    This service provides a centralized storage solution for all binary assets in the system, including:
    * Character portraits and images
    * Campaign maps and location images
    * Audio files for ambiance and effects
    * Document storage for game content
    * Video content for cinematics and tutorials

    Features:
    * Deduplication by SHA256 checksum
    * Version control with rollback capabilities
    * Lifecycle policies for asset management
    * Backup and restore capabilities
    * Direct access via presigned URLs
    * Bulk operations support
    * Content-type validation
    * Quota management per service
    * Comprehensive asset metadata
    """,
    version=settings.service_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    terms_of_service="https://dndcreator.com/terms",
    contact={
        "name": "D&D Character Creator Support",
        "url": "https://dndcreator.com/support",
        "email": "support@dndcreator.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
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


def custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=[
            {
                "name": "Assets",
                "description": "Operations for managing binary assets",
                "externalDocs": {
                    "description": "Asset Management Guide",
                    "url": "https://dndcreator.com/docs/storage/assets"
                }
            },
            {
                "name": "Health",
                "description": "Health check endpoints"
            }
        ]
    )

    # Add examples to schema components
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "examples" not in openapi_schema["components"]:
        openapi_schema["components"]["examples"] = {}

    # Add model examples
    for model_name, model_info in MODELS.items():
        if model_name in openapi_schema["components"]["schemas"]:
            openapi_schema["components"]["schemas"][model_name]["description"] = model_info["description"]
            openapi_schema["components"]["schemas"][model_name]["example"] = model_info["example"]

    # Add error examples
    openapi_schema["components"]["examples"].update(ERROR_EXAMPLES)

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        },
        "JWTAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Exception handlers
@app.exception_handler(StorageException)
async def storage_exception_handler(request: Request, exc: StorageException):
    """Handle storage service specific exceptions."""
    logger.error(f"Storage error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.exception_handler(AssetNotFoundException)
async def not_found_handler(request: Request, exc: AssetNotFoundException):
    """Handle asset not found errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.exception_handler(AssetAlreadyExistsException)
async def conflict_handler(request: Request, exc: AssetAlreadyExistsException):
    """Handle duplicate asset errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.exception_handler(S3StorageException)
async def s3_error_handler(request: Request, exc: S3StorageException):
    """Handle S3 storage errors."""
    logger.error(f"S3 error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    """Handle any unhandled exceptions."""
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "details": {"error": str(exc)}
        }
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
app.include_router(
    image_storage.router,
    tags=["Image Storage"],
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
