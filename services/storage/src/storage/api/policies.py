"""Lifecycle policy API endpoints."""

from fastapi import APIRouter

router = APIRouter()

# Placeholder - to be implemented
@router.get("/")
async def list_policies():
    """List policies."""
    return {"message": "Policy endpoints to be implemented"}
