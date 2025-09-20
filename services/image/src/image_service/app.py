"""FastAPI application setup."""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from image_service.core.config import Settings, get_settings
from image_service.core.exceptions import ImageServiceError
from image_service.integration.storage_service import StorageServiceClient

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan events."""
    # Connect to services
    from image_service.integration.message_hub import MessageHubClient
    from image_service.integration.getimg import GetImgClient
    from image_service.events.handlers import EVENT_HANDLERS
    from image_service.services.queue import AsyncQueueService
    from image_service.workers.generation import GenerationWorker

    # Initialize services
    message_hub = MessageHubClient()
    getimg_client = GetImgClient()
    storage_client = StorageServiceClient()
    queue_service = AsyncQueueService(
        redis=app.state.redis,
        storage=storage_client,
    )
    generation_worker = GenerationWorker(
        queue_service=queue_service,
        getimg_client=getimg_client,
        storage=storage_client,
    )

    try:
        # Register event handlers
        for event_type, handler in EVENT_HANDLERS.items():
            message_hub.subscribe(event_type, handler)

        # Connect services
        await message_hub.connect()
        app.state.message_hub = message_hub
        app.state.storage = storage_client
        app.state.queue = queue_service
        app.state.generation_worker = generation_worker

        # Start worker
        worker_task = asyncio.create_task(generation_worker.start())
        app.state.worker_task = worker_task

        yield

    finally:
        # Stop worker
        if hasattr(app.state, "generation_worker"):
            await app.state.generation_worker.stop()
            if hasattr(app.state, "worker_task"):
                app.state.worker_task.cancel()
                await app.state.worker_task

        # Close message hub
        if hasattr(app.state, "message_hub"):
            await app.state.message_hub.close()

        # Close storage client
        if hasattr(app.state, "storage"):
            await app.state.storage.close()


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V2_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Exception handlers
    @app.exception_handler(ImageServiceError)
    async def image_service_error_handler(request, exc):
        """Handle ImageServiceError exceptions."""
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": {
                        key: value
                        for key, value in exc.__dict__.items()
                        if key not in {"code", "message"}
                    }
                }
            },
        )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "dependencies": {
                "message_hub": "healthy",  # TODO: Add actual checks
                "getimg_api": "healthy",
                "storage": "healthy",
                "cache": "healthy"
            },
            "metrics": {
                "images_generated": 0,  # TODO: Add actual metrics
                "generation_queue": 0,
                "error_rate": 0.0,
                "cache_hit_rate": 0.0
            }
        }

    # API routers
    from image_service.api.health import router as health_router
    from image_service.api.routers.style import router as style_router

    app.include_router(health_router)
    app.include_router(style_router)

    return app