"""API endpoints for character portrait generation."""
import logging
from typing import Optional
from uuid import UUID

from fastapi import (
    APIRouter, Depends, Header, HTTPException, Path, Response, status
)

from image.api.models import ImageResponse, PortraitRequest
from image.core.dependencies import get_queue_service, get_storage_service
from image.core.errors import ImageNotFoundError
from image.core.validation import validate_api_key
from image.models.generation import ImageType
from image.services.queue import QueueService
from image.services.storage import StorageService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/portraits",
    response_model=ImageResponse,
    summary="Generate character portrait",
    response_description="The generated portrait",
    status_code=status.HTTP_201_CREATED
)
async def create_portrait(
    request: PortraitRequest,
    x_request_id: str = Header(None),
    x_api_key: str = Header(...),
    queue: QueueService = Depends(get_queue_service),
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Generate a character portrait.

    Args:
        request: Portrait request parameters
        x_request_id: Optional request ID
        x_api_key: API key for authentication
        queue: Queue service
        storage: Storage service

    Returns:
        Generated portrait details
    """
    # Validate API key
    validate_api_key(x_api_key, "portraits:write")

    try:
        # Create generation task
        task = await queue.enqueue_task(
            task_type=ImageType.CHARACTER_PORTRAIT,
            parameters={
                "character_id": str(request.character_id),
                "theme": request.theme,
                "style": request.style.dict(),
                "equipment": request.equipment.dict() if request.equipment else None
            },
            request_id=x_request_id
        )

        # Get generated image
        image = await storage.get_task_result(task.id)

        # Default portrait size
        size = {
            "width": 1024,
            "height": 1024
        }

        return {
            "id": image.id,
            "type": ImageType.CHARACTER_PORTRAIT,
            "url": image.url,
            "size": size,
            "theme": request.theme,
            "cdn_url": image.cdn_url,
            "metadata": {
                "character_id": str(request.character_id),
                "style": request.style.dict(),
                "equipment": request.equipment.dict() if request.equipment else None
            }
        }

    except Exception as e:
        logger.exception("Error generating portrait")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/portraits/{portrait_id}",
    response_model=ImageResponse,
    summary="Get portrait details",
    response_description="The portrait details"
)
async def get_portrait(
    portrait_id: UUID = Path(..., description="Portrait ID"),
    x_api_key: str = Header(...),
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Get details of a portrait.

    Args:
        portrait_id: Portrait ID
        x_api_key: API key for authentication
        storage: Storage service

    Returns:
        Portrait details

    Raises:
        ImageNotFoundError: If portrait not found
    """
    # Validate API key
    validate_api_key(x_api_key, "portraits:read")

    try:
        # Get image
        image = await storage.get_image_metadata(portrait_id)
        if not image:
            raise ImageNotFoundError(portrait_id)

        return {
            "id": image.id,
            "type": image.type,
            "url": image.url,
            "size": {
                "width": image.width,
                "height": image.height
            },
            "theme": image.theme,
            "cdn_url": image.cdn_url,
            "metadata": image.metadata
        }

    except ImageNotFoundError:
        raise
    except Exception as e:
        logger.exception("Error getting portrait")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/portraits/{portrait_id}",
    response_model=ImageResponse,
    summary="Update portrait",
    response_description="The updated portrait"
)
async def update_portrait(
    request: PortraitRequest,
    portrait_id: UUID = Path(..., description="Portrait ID"),
    x_request_id: str = Header(None),
    x_api_key: str = Header(...),
    queue: QueueService = Depends(get_queue_service),
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Update an existing portrait.

    This creates a new version of the portrait with updated parameters.

    Args:
        request: Portrait request parameters
        portrait_id: Portrait ID to update
        x_request_id: Optional request ID
        x_api_key: API key for authentication
        queue: Queue service
        storage: Storage service

    Returns:
        Updated portrait details

    Raises:
        ImageNotFoundError: If portrait not found
    """
    # Validate API key
    validate_api_key(x_api_key, "portraits:write")

    try:
        # Verify portrait exists
        image = await storage.get_image_metadata(portrait_id)
        if not image:
            raise ImageNotFoundError(portrait_id)

        # Create generation task
        task = await queue.enqueue_task(
            task_type=ImageType.CHARACTER_PORTRAIT,
            parameters={
                "character_id": str(request.character_id),
                "theme": request.theme,
                "style": request.style.dict(),
                "equipment": request.equipment.dict() if request.equipment else None,
                "previous_version": str(portrait_id)  # Link to previous
            },
            request_id=x_request_id
        )

        # Get generated image
        updated = await storage.get_task_result(task.id)

        return {
            "id": updated.id,
            "type": updated.type,
            "url": updated.url,
            "size": {
                "width": updated.width,
                "height": updated.height
            },
            "theme": request.theme,
            "cdn_url": updated.cdn_url,
            "metadata": {
                "character_id": str(request.character_id),
                "style": request.style.dict(),
                "equipment": request.equipment.dict() if request.equipment else None,
                "previous_version": str(portrait_id)
            }
        }

    except ImageNotFoundError:
        raise
    except Exception as e:
        logger.exception("Error updating portrait")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/portraits/{portrait_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete portrait",
    response_description="Portrait deleted successfully"
)
async def delete_portrait(
    portrait_id: UUID = Path(..., description="Portrait ID"),
    x_api_key: str = Header(...),
    storage: StorageService = Depends(get_storage_service)
) -> Response:
    """Delete a portrait.

    Args:
        portrait_id: Portrait ID
        x_api_key: API key for authentication
        storage: Storage service

    Returns:
        Empty response

    Raises:
        ImageNotFoundError: If portrait not found
    """
    # Validate API key
    validate_api_key(x_api_key, "portraits:delete")

    try:
        # Delete portrait
        success = await storage.delete_image(portrait_id)
        if not success:
            raise ImageNotFoundError(portrait_id)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ImageNotFoundError:
        raise
    except Exception as e:
        logger.exception("Error deleting portrait")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
