"""Health check router."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    services: Dict[str, str]

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        services={
            "prometheus": "healthy",
            "storage": "unknown",
            "message_hub": "unknown",
        }
    )