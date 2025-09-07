"""Asset management API endpoints."""

from fastapi import APIRouter

router = APIRouter()

# Placeholder - to be implemented
@router.get("/")
async def list_assets():
    """List assets."""
    return {"message": "Asset endpoints to be implemented"}
