from typing import Dict, Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class ComponentStatus(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    message: str = "OK"


class HealthCheck(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    components: Dict[str, ComponentStatus]
    metrics: Dict[str, float]


@router.get("/health", response_model=HealthCheck)
async def health_check(request: Request) -> HealthCheck:
    """Check health status of all service components."""
    # TODO: Add actual health checks for each component
    return HealthCheck(
        status="healthy",
        components={
            "openai": ComponentStatus(),
            "getimg_ai": ComponentStatus(),
            "message_hub": ComponentStatus(),
            "queue": ComponentStatus(),
        },
        metrics={
            "text_generation_rate": 0.0,
            "image_generation_rate": 0.0,
            "error_rate": 0.0,
            "queue_length": 0,
        },
    )
