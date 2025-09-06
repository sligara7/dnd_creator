"""Health check endpoints."""

from typing import Dict, List, Optional

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

router = APIRouter(tags=["Health"])


async def check_redis(redis: Redis) -> str:
    """Check Redis connection."""
    try:
        await redis.ping()
        return STATUS_HEALTHY
    except Exception as e:
        logger.error("Redis health check failed", error=str(e))
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

    # Get metrics (TODO: implement actual metrics)
    metrics = {
        "images_generated": 0,
        "generation_queue": 0,
        "error_rate": 0.0,
        "cache_hit_rate": 0.0
    }

    return {
        "status": status,
        "version": settings.VERSION,
        "dependencies": dependency_status,
        "metrics": metrics,
    }
