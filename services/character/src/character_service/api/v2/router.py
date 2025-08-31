"""API V1 Router Configuration"""

from fastapi import APIRouter

from character_service.api.v1.endpoints import (
    characters,
    journals,
    inventory,
    evolution,
    antitheticon,
    health,
)

router = APIRouter()

# Health check endpoint
router.include_router(
    health.router,
    prefix="/health",
    tags=["health"],
)

# Character management endpoints
router.include_router(
    characters.router,
    prefix="/characters",
    tags=["characters"],
)

# Journal system endpoints
router.include_router(
    journals.router,
    prefix="/journals",
    tags=["journals"],
)

# Inventory management endpoints
router.include_router(
    inventory.router,
    prefix="/inventory",
    tags=["inventory"],
)

# Character evolution endpoints
router.include_router(
    evolution.router,
    prefix="/evolution",
    tags=["evolution"],
)

# Antitheticon system endpoints
router.include_router(
    antitheticon.router,
    prefix="/antitheticon",
    tags=["antitheticon"],
)
