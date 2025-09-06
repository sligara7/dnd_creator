"""API routes module."""
from fastapi import APIRouter

from character_service.api.v2.routes.version import router as version_router
from character_service.api.v2.routes.theme import router as theme_router


api_router = APIRouter(prefix="/api/v2")

# Add all route modules here
api_router.include_router(version_router)
api_router.include_router(theme_router)
