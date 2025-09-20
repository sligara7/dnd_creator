"""
API routes for the Audit Service.
"""
from fastapi import APIRouter

from audit_service.api.v2.routers.event import router as event_router
from audit_service.api.v2.routers.analysis import router as analysis_router

api_router = APIRouter()
api_router.include_router(event_router)
api_router.include_router(analysis_router)