"""Health check endpoints for storage service."""

import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from storage.core.config import settings
from storage.core.database import get_db
from storage.integrations.s3_client import storage_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness() -> Dict[str, Any]:
    """Liveness probe endpoint."""
    return {
        "status": "alive",
        "service": settings.service_name,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Readiness probe endpoint."""
    checks = {
        "database": False,
        "storage": False,
    }
    
    # Check database connection
    try:
        result = await db.execute(text("SELECT 1"))
        checks["database"] = result.scalar() == 1
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    # Check S3 connection
    try:
        # Try to list objects with a very small limit
        await storage_client.list_objects(max_keys=1)
        checks["storage"] = True
    except Exception as e:
        logger.error(f"S3 health check failed: {e}")
    
    # Overall status
    all_healthy = all(checks.values())
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "service": settings.service_name,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def health(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Combined health check endpoint."""
    # Get readiness data
    readiness_data = await readiness(db)
    
    return {
        "status": readiness_data["status"],
        "service": settings.service_name,
        "version": settings.service_version,
        "environment": settings.environment,
        "checks": readiness_data["checks"],
        "timestamp": datetime.utcnow().isoformat(),
    }
