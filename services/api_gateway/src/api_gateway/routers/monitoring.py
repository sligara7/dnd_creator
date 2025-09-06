from fastapi import APIRouter, Depends
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from api_gateway.monitoring.metrics import registry
from api_gateway.middleware.auth import APIKeyAuth

router = APIRouter(
    prefix="/monitoring",
    tags=["monitoring"],
    dependencies=[Depends(APIKeyAuth)]
)

@router.get("/metrics")
async def get_metrics():
    """Get Prometheus metrics."""
    return Response(
        generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )

@router.get("/health")
async def get_health():
    """Get service health status."""
    # This will be updated by the service discovery system
    # Just return a simple status for now
    return {
        "status": "healthy",
        "version": "0.1.0"
    }
