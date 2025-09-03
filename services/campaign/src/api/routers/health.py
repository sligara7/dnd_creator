"""Health check API router."""
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from prometheus_client import Counter, Gauge, Histogram
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...core.db import get_db
from ...core.logging import get_logger
from ..dependencies import get_message_hub

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger(__name__)

# Prometheus metrics
REQUESTS = Counter(
    "campaign_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"]
)
RESPONSE_TIME = Histogram(
    "campaign_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"]
)
DB_POOL = Gauge(
    "campaign_db_pool_size",
    "Database connection pool size",
    ["status"]
)
MESSAGE_QUEUE = Gauge(
    "campaign_message_queue_size",
    "Message queue size",
    ["queue"]
)


@router.get("", status_code=status.HTTP_200_OK)
async def health_check() -> Dict:
    """Basic health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "campaign"
    }


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness() -> Dict:
    """Kubernetes liveness probe."""
    return {"status": "alive"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness(
    db: Session = Depends(get_db),
    message_hub = Depends(get_message_hub)
) -> Dict:
    """Kubernetes readiness probe."""
    try:
        # Check database
        db.execute(text("SELECT 1"))
        db_status = "ready"
    except Exception as e:
        logger.error("Database not ready", error=str(e))
        db_status = "not ready"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not ready"
        )

    try:
        # Check message hub
        await message_hub.health_check()
        mh_status = "ready"
    except Exception as e:
        logger.error("Message hub not ready", error=str(e))
        mh_status = "not ready"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Message hub not ready"
        )

    return {
        "status": "ready",
        "database": db_status,
        "message_hub": mh_status
    }


@router.get("/metrics")
def metrics() -> Response:
    """Prometheus metrics."""
    from prometheus_client import generate_latest
    return Response(
        generate_latest(),
        media_type="text/plain"
    )
