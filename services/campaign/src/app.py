"""Campaign service FastAPI application."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram
import time

from .api.routers import campaign, chapter, version, health
from .routers import story
from .core.config import settings
from .core.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Campaign Service",
    description="Service for managing D&D campaign generation and management",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics middleware
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"]
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to record request metrics."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        path=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        path=request.url.path
    ).observe(duration)

    return response


# Add routers
app.include_router(campaign.router)
app.include_router(chapter.router)
app.include_router(version.router)
app.include_router(health.router)
app.include_router(story.router)


@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    logger.info("Starting campaign service")


@app.on_event("shutdown")
async def shutdown_event():
    """Run shutdown tasks."""
    logger.info("Shutting down campaign service")
