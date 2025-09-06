import logging.config
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from prometheus_client import make_asgi_app
import structlog

from llm_service.api import health, text, image, theme
from llm_service.core.cache import RedisCache, RateLimiter
from llm_service.core.events import MessageHubClient
from llm_service.core.exceptions import LLMServiceError
from llm_service.core.middleware import error_handler, setup_middleware
from llm_service.core.rate_limit import RateLimitMiddleware
from llm_service.core.token_tracking import TokenTrackingMiddleware
from llm_service.core.settings import Settings, get_settings
from llm_service.services.openai import OpenAIClient
from llm_service.services.getimg_ai import GetImgAIClient
from llm_service.services.text import TextGenerationService
from llm_service.services.image import ImageGenerationService
from llm_service.services.theme import ThemeAnalysisService

# Configure structured logging
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        }
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        }
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True,
        }
    },
})

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI application lifespan setup and cleanup."""
    # Setup
    settings = get_settings()
    app.state.settings = settings
    app.state.logger = structlog.get_logger()

    app.state.logger.info(
        "application_starting",
        service=settings.service_name,
        environment=settings.environment,
    )

    # Initialize Redis cache
    app.state.logger.info("initializing_redis_cache")
    app.state.redis = RedisCache(settings)
    await app.state.redis.initialize()
    app.state.rate_limiter = RateLimiter(app.state.redis)
    
    # Initialize service clients
    app.state.openai = OpenAIClient(settings, app.state.rate_limiter, app.state.logger)
    app.state.getimg_ai = GetImgAIClient(settings, app.state.rate_limiter, app.state.logger)
    app.state.message_hub = MessageHubClient(settings)

    # Initialize business logic services
    app.state.text_service = TextGenerationService(
        settings=settings,
        openai=app.state.openai,
        rate_limiter=app.state.rate_limiter,
        message_hub=app.state.message_hub,
        logger=app.state.logger,
    )
    app.state.image_service = ImageGenerationService(
        settings=settings,
        getimg_ai=app.state.getimg_ai,
        rate_limiter=app.state.rate_limiter,
        message_hub=app.state.message_hub,
        logger=app.state.logger,
    )
    app.state.theme_service = ThemeAnalysisService(
        openai=app.state.openai,
        rate_limiter=app.state.rate_limiter,
        db=app.state.db,
        logger=app.state.logger,
    )

    # Initialize services
    await app.state.text_service.initialize()
    await app.state.image_service.initialize()

    yield

    # Cleanup
    app.state.logger.info(
        "application_shutting_down",
        service=settings.service_name,
        environment=settings.environment,
    )

    # Close Redis connection
    app.state.logger.info("closing_redis_connection")
    await app.state.redis.close()

    # Close services
    app.state.logger.info("closing_services")
    await app.state.text_service.cleanup()
    await app.state.image_service.cleanup()

    # Close Message Hub client
    app.state.logger.info("closing_message_hub_client")
    await app.state.message_hub.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="LLM Service",
        description="AI-powered text and image generation for D&D Character Creator",
        version="1.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # Add middleware
    setup_middleware(app, settings)

    # Add rate limiting middleware
    redis_cache = RedisCache(settings)
    app.add_middleware(
        RateLimitMiddleware,
        settings=settings,
        rate_limiter=RateLimiter(redis_cache)
    )

    # Add token tracking middleware
    if settings.openai.token_tracking_enabled:
        app.add_middleware(
            TokenTrackingMiddleware,
            settings=settings,
            cache=redis_cache
        )

    # Set up exception handlers
    app.add_exception_handler(LLMServiceError, error_handler)

    # Add Prometheus metrics endpoint
    if settings.metrics_enabled:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)

    # Mount API routers
    app.include_router(health.router)
    
    # API v2 routers will be mounted under /api/v2
    api_v2_app = FastAPI(openapi_prefix=settings.api_prefix)
    api_v2_app.include_router(text.router)
    api_v2_app.include_router(image.router)
    api_v2_app.include_router(theme.router)
    app.mount(settings.api_prefix, api_v2_app)

    return app


app = create_app()
