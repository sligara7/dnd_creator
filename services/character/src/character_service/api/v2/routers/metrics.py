"""Metrics endpoint for Prometheus."""
from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

router = APIRouter()


@router.get(
    "",
    response_class=Response,
    summary="Get service metrics",
    description="Get Prometheus metrics for service monitoring.",
)
async def get_metrics():
    """Get Prometheus metrics."""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
