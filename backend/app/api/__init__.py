from fastapi import APIRouter

# Import all router modules
from backend.app.api.character import router as character_router
from backend.app.api.dm import router as dm_router
from backend.app.api.ai_service import router as ai_router

# Create an aggregated router
router = APIRouter()

# Include all API routers
router.include_router(character_router)
router.include_router(dm_router)
router.include_router(ai_router)

# Export the routers individually as well for cases where they might be needed separately
__all__ = ["router", "character_router", "dm_router", "ai_router"]