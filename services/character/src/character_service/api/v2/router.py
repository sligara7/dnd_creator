"""API V2 Router Configuration"""
from fastapi import APIRouter
from character_service.api.v2.endpoints import characters, health, inventory_new as inventory, journals_new as journals
from character_service.api.v2.routers import progress
from character_service.api.v2.routers import metrics

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

# Character progress and events endpoints
router.include_router(
    progress.router,
    prefix="/characters",
    tags=["progress", "events"],
)

# Metrics endpoint
router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["metrics"],
)

