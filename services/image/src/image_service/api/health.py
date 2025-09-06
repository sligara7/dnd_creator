"""Health check endpoints."""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from redis.asyncio import Redis

from image_service.core.config import get_settings
from image_service.core.deps import get_redis
from image_service.core.logging import get_logger
from image_service.core.constants import (
    DEPENDENCY_CACHE,
    DEPENDENCY_GETIMG_API,
    DEPENDENCY_MESSAGE_HUB,
    DEPENDENCY_STORAGE,
    STATUS_DEGRADED,
    STATUS_HEALTHY,
    STATUS_UNHEALTHY,
)
from image_service.core.metrics import metrics, CACHE_OPERATIONS, STORAGE_SIZE, STORAGE_OPERATIONS, API_REQUESTS_TOTAL

import httpx
from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from image_service.core.config import get_settings
from image_service.core.constants import (
    DEPENDENCY_CACHE,
    DEPENDENCY_GETIMG_API,
    DEPENDENCY_MESSAGE_HUB,
    DEPENDENCY_STORAGE,
    STATUS_DEGRADED,
    STATUS_HEALTHY,
    STATUS_UNHEALTHY,
)
from image_service.core.deps import get_redis
from image_service.core.logging import get_logger
from image_service.integration.message_hub import MessageHubClient

settings = get_settings()
logger = get_logger(__name__)

settings = get_settings()
logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/metrics")
async def metrics() -> Response:
    """Return current metrics."""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


async def check_redis(redis: Redis) -> str:
    """Check Redis connection."""
    try:
        await redis.ping()
        metrics.track_cache_operation("ping", hit=True)
        return STATUS_HEALTHY
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
        metrics.track_cache_operation("ping", hit=False)
        return STATUS_UNHEALTHY


async def check_message_hub(url: Optional[str] = None) -> str:
    """Check Message Hub connection."""
    url = url or str(settings.MESSAGE_HUB_URL)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{url}/health")
            if response.status_code == 200:
                return STATUS_HEALTHY
            return STATUS_DEGRADED
    except Exception as e:
        logger.error("Message Hub health check failed", error=str(e))
        return STATUS_UNHEALTHY


async def check_getimg_api() -> str:
    """Check GetImg.AI API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.GETIMG_API_URL}/health",
                headers={"Authorization": f"Bearer {settings.GETIMG_API_KEY}"}
            )
            if response.status_code == 200:
                return STATUS_HEALTHY
            return STATUS_DEGRADED
    except Exception as e:
        logger.error("GetImg.AI health check failed", error=str(e))
        return STATUS_UNHEALTHY


async def check_storage() -> str:
    """Check storage service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.STORAGE_SERVICE_URL}/health")
            if response.status_code == 200:
                return STATUS_HEALTHY
            return STATUS_DEGRADED
    except Exception as e:
        logger.error("Storage service health check failed", error=str(e))
        return STATUS_UNHEALTHY


@router.get("/health")
async def health_check(redis: Redis = Depends(get_redis)) -> Dict:
    """Health check endpoint."""
    # Check all dependencies
    dependency_status = {
        DEPENDENCY_CACHE: await check_redis(redis),
        DEPENDENCY_MESSAGE_HUB: await check_message_hub(),
        DEPENDENCY_GETIMG_API: await check_getimg_api(),
        DEPENDENCY_STORAGE: await check_storage(),
    }

    # Get overall status
    unhealthy = [
        dep for dep, status in dependency_status.items()
        if status == STATUS_UNHEALTHY
    ]
    degraded = [
        dep for dep, status in dependency_status.items()
        if status == STATUS_DEGRADED
    ]

    if unhealthy:
        status = STATUS_UNHEALTHY
    elif degraded:
        status = STATUS_DEGRADED
    else:
        status = STATUS_HEALTHY

    # Get metrics
    try:
        # Get queue stats - this will be implemented in the queue service
        queue_size = 0
        processing = 0
        completed = 0
        failed = 0

        # Calculate cache hit ratio
        total_ops = (
            CACHE_OPERATIONS.labels(operation="get", status="hit")._value.get() +
            CACHE_OPERATIONS.labels(operation="get", status="miss")._value.get()
        )
        hits = CACHE_OPERATIONS.labels(operation="get", status="hit")._value.get()
        cache_hit_rate = (hits / total_ops) if total_ops > 0 else 0.0

        metrics = {
            "tasks": {
                "pending": queue_size,
                "processing": processing,
                "completed": completed,
                "failed": failed,
            },
            "cache": {
                "hit_rate": cache_hit_rate,
                "operations": total_ops,
            },
            "storage": {
                "size_bytes": STORAGE_SIZE._value.get(),
                "operations": STORAGE_OPERATIONS._value.get(),
            },
            "api": {
                "requests": API_REQUESTS_TOTAL._value.get(),
                "errors": (
                    API_REQUESTS_TOTAL.labels(
                        method="*",
                        endpoint="*",
                        status="500",
                    )._value.get()
                ),
            },
        }
    except Exception as e:
        logger.error("Failed to get service stats", error=str(e))
        metrics = {}

    return {
        "status": status,
        "version": settings.VERSION,
        "dependencies": dependency_status,
        "metrics": metrics,
    }
