"""API endpoints for item illustration generation."""
import logging
from typing import Optional
from uuid import UUID

from fastapi import (
    APIRouter, Depends, Header, HTTPException, Path, Response, status
)

from image.api.models import ImageResponse, ItemRequest
from image.core.dependencies import get_queue_service, get_storage_service
from image.core.errors import ImageNotFoundError
from image.core.validation import validate_api_key
from image.models.generation import ImageType
from image.services.queue import QueueService
from image.services.storage import StorageService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/items",
    response_model=ImageResponse,
    summary="Generate item illustration",
    response_description="The generated item image",
    status_code=status.HTTP_201_CREATED
)
async def create_item_image(
    request: ItemRequest,
    x_request_id: str = Header(None),
    x_api_key: str = Header(...),
    queue: QueueService = Depends(get_queue_service),
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Generate an item illustration.

    Args:
        request: Item request parameters
        x_request_id: Optional request ID
        x_api_key: API key for authentication
        queue: Queue service
        storage: Storage service

    Returns:
        Generated item image details
    """
    # Validate API key
    validate_api_key(x_api_key, "items:write")

    try:
        # Create generation task
        task = await queue.enqueue_task(
            task_type=ImageType.ITEM,
            parameters={
                "item_id": str(request.item_id),
                "type": request.type,
                "theme": request.theme,
                "style": request.style.dict(),
                "properties": request.properties.dict()
            },
            request_id=x_request_id
        )

        # Get generated image
        image = await storage.get_task_result(task.id)

        # Default size based on item type
        size = {
            "width": 512,
            "height": 512
        }
        if request.type in ("weapon", "armor"):
            size = {
                "width": 768,
                "height": 768
            }

        return {
            "id": image.id,
            "type": ImageType.ITEM,
            "url": image.url,
            "size": size,
            "theme": request.theme,
            "cdn_url": image.cdn_url,
            "metadata": {
                "item_id": str(request.item_id),
                "item_type": request.type,
                "style": request.style.dict(),
                "properties": request.properties.dict()
            }
        }

    except Exception as e:
        logger.exception("Error generating item image")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/items/{item_id}",
    response_model=ImageResponse,
    summary="Get item image details",
    response_description="The item image details"
)
async def get_item_image(
    item_id: UUID = Path(..., description="Item image ID"),
    x_api_key: str = Header(...),
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Get details of an item image.

    Args:
        item_id: Item image ID
        x_api_key: API key for authentication
        storage: Storage service

    Returns:
        Item image details

    Raises:
        ImageNotFoundError: If item image not found
    """
    # Validate API key
    validate_api_key(x_api_key, "items:read")

    try:
        # Get image
        image = await storage.get_image_metadata(item_id)
        if not image:
            raise ImageNotFoundError(item_id)

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
        logger.exception("Error getting item image")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/items/{item_id}",
    response_model=ImageResponse,
    summary="Update item image",
    response_description="The updated item image"
)
async def update_item_image(
    request: ItemRequest,
    item_id: UUID = Path(..., description="Item image ID"),
    x_request_id: str = Header(None),
    x_api_key: str = Header(...),
    queue: QueueService = Depends(get_queue_service),
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Update an existing item image.

    This creates a new version of the item image with updated parameters.

    Args:
        request: Item request parameters
        item_id: Item image ID to update
        x_request_id: Optional request ID
        x_api_key: API key for authentication
        queue: Queue service
        storage: Storage service

    Returns:
        Updated item image details

    Raises:
        ImageNotFoundError: If item image not found
    """
    # Validate API key
    validate_api_key(x_api_key, "items:write")

    try:
        # Verify image exists
        image = await storage.get_image_metadata(item_id)
        if not image:
            raise ImageNotFoundError(item_id)

        # Create generation task
        task = await queue.enqueue_task(
            task_type=ImageType.ITEM,
            parameters={
                "item_id": str(request.item_id),
                "type": request.type,
                "theme": request.theme,
                "style": request.style.dict(),
                "properties": request.properties.dict(),
                "previous_version": str(item_id)  # Link to previous
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
                "item_id": str(request.item_id),
                "item_type": request.type,
                "style": request.style.dict(),
                "properties": request.properties.dict(),
                "previous_version": str(item_id)
            }
        }

    except ImageNotFoundError:
        raise
    except Exception as e:
        logger.exception("Error updating item image")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete item image",
    response_description="Item image deleted successfully"
)
async def delete_item_image(
    item_id: UUID = Path(..., description="Item image ID"),
    x_api_key: str = Header(...),
    storage: StorageService = Depends(get_storage_service)
) -> Response:
    """Delete an item image.

    Args:
        item_id: Item image ID
        x_api_key: API key for authentication
        storage: Storage service

    Returns:
        Empty response

    Raises:
        ImageNotFoundError: If item image not found
    """
    # Validate API key
    validate_api_key(x_api_key, "items:delete")

    try:
        # Delete image
        success = await storage.delete_image(item_id)
        if not success:
            raise ImageNotFoundError(item_id)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ImageNotFoundError:
        raise
    except Exception as e:
        logger.exception("Error deleting item image")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
