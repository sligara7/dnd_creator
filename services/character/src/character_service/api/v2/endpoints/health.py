"""Health Check Endpoint"""

from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "message": "D&D Character Service - Running"
    }
