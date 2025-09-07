"""Version management API endpoints."""

from fastapi import APIRouter

router = APIRouter()

# Placeholder - to be implemented
@router.get("/")
async def list_versions():
    """List versions."""
    return {"message": "Version endpoints to be implemented"}
