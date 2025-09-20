"""FastAPI dependencies."""

from fastapi import Request

from image_service.integration.storage_service import StorageServiceClient


def get_storage(request: Request) -> StorageServiceClient:
    """Get storage service client."""
    return request.app.state.storage