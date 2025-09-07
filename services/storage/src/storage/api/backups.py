"""Backup management API endpoints."""

from fastapi import APIRouter

router = APIRouter()

# Placeholder - to be implemented
@router.get("/")
async def list_backups():
    """List backups."""
    return {"message": "Backup endpoints to be implemented"}
