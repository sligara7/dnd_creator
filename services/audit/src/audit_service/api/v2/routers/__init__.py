"""
API router configuration for the Audit Service.
"""
from fastapi import APIRouter

from audit_service.api.v2.routers import event, analysis

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(event.router)
api_router.include_router(analysis.router)