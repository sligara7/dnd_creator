"""API V2 Router Configuration"""

from fastapi import APIRouter

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from character_service.api.v2.dependencies import get_container
from character_service.api.v2.endpoints import (
    characters,
    health,
    inventory_new as inventory,
    journals_new as journals,
)
from character_service.api.v2.routers import progress
from character_service.api.v2.models import ErrorResponse

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
from character_service.api.v2.routers import metrics as metrics_router
router.include_router(
    metrics_router.router,
    prefix="/metrics",
    tags=["metrics"],
)

