"""API endpoints for map generation."""
import logging
from typing import Optional
from uuid import UUID

from fastapi import (
    APIRouter, Depends, Header, HTTPException, Path, Query, Response,
    status
)

from image.api.models import (
    CampaignMapRequest,
    CampaignOverlayRequest,
    ImageResponse,
    TacticalMapRequest,
    TacticalOverlayRequest
)
from image.core.dependencies import (
    get_queue_service,
    get_storage_service
)
from image.core.errors import ImageNotFoundError, OverlayError
from image.core.validation import (
    validate_api_key,
    validate_grid_config,
    validate_image_dimensions,
    validate_overlay_coordinates
)
from image.models.generation import ImageType
from image.services.queue import QueueService
from image.services.storage import StorageService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/maps/tactical",
    response_model=ImageResponse,
    summary="Generate tactical map",
    response_description="The generated map",
    status_code=status.HTTP_201_CREATED
)
async def create_tactical_map(
    request: TacticalMapRequest,
    x_request_id: str = Header(None),
    x_api_key: str = Header(...),
    queue: QueueService = Depends(get_queue_service),
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Create a new tactical map.

    Args:
        request: Map request parameters
        x_request_id: Optional request ID
        x_api_key: API key for authentication
        queue: Queue service
        storage: Storage service

    Returns:
        Generated map details
    """
    # Validate API key
    validate_api_key(x_api_key, "maps:write")

    # Validate dimensions
    validate_image_dimensions(
        request.size.width,
        request.size.height,
        max_width=8192,  # Allow larger maps
        max_height=8192
    )

    # Validate grid if enabled
    if request.grid and request.grid.enabled:
        validate_grid_config(request.grid.size)

    try:
        # Create generation task
        task = await queue.enqueue_task(
            task_type=ImageType.MAP_TACTICAL,
            parameters={
                "size": request.size.dict(),
                "grid": request.grid.dict() if request.grid else None,
                "theme": request.theme,
                "features": request.features,
                "terrain": request.terrain.dict() if request.terrain else None
            },
            request_id=x_request_id
        )

        # Get generated image
        image = await storage.get_task_result(task.id)
        return {
            "id": image.id,
            "type": ImageType.MAP_TACTICAL,
            "url": image.url,
            "size": request.size.dict(),
            "theme": request.theme,
            "cdn_url": image.cdn_url,
            "metadata": image.metadata
        }

    except Exception as e:
        logger.exception("Error generating tactical map")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/maps/campaign",
    response_model=ImageResponse,
    summary="Generate campaign map",
    response_description="The generated map",
    status_code=status.HTTP_201_CREATED
)
async def create_campaign_map(
    request: CampaignMapRequest,
    x_request_id: str = Header(None),
    x_api_key: str = Header(...),
    queue: QueueService = Depends(get_queue_service),
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Create a new campaign map.

    Args:
        request: Map request parameters
        x_request_id: Optional request ID
        x_api_key: API key for authentication
        queue: Queue service
        storage: Storage service

    Returns:
        Generated map details
    """
    # Validate API key
    validate_api_key(x_api_key, "maps:write")

    # Validate dimensions
    validate_image_dimensions(
        request.size.width,
        request.size.height,
        max_width=16384,  # Allow very large campaign maps
        max_height=16384
    )

    try:
        # Create generation task
        task = await queue.enqueue_task(
            task_type=ImageType.MAP_CAMPAIGN,
            parameters={
                "size": request.size.dict(),
                "scale": request.scale.dict(),
                "theme": request.theme,
                "features": request.features,
                "points_of_interest": [
                    poi.dict() for poi in request.points_of_interest
                ]
            },
            request_id=x_request_id
        )

        # Get generated image
        image = await storage.get_task_result(task.id)
        return {
            "id": image.id,
            "type": ImageType.MAP_CAMPAIGN,
            "url": image.url,
            "size": request.size.dict(),
            "theme": request.theme,
            "cdn_url": image.cdn_url,
            "metadata": image.metadata
        }

    except Exception as e:
        logger.exception("Error generating campaign map")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/maps/{map_id}",
    response_model=ImageResponse,
    summary="Get map details",
    response_description="The map details"
)
async def get_map(
    map_id: UUID = Path(..., description="Map ID"),
    x_api_key: str = Header(...),
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Get details of a map.

    Args:
        map_id: Map ID
        x_api_key: API key for authentication
        storage: Storage service

    Returns:
        Map details

    Raises:
        ImageNotFoundError: If map not found
    """
    # Validate API key
    validate_api_key(x_api_key, "maps:read")

    try:
        # Get image
        image = await storage.get_image_metadata(map_id)
        if not image:
            raise ImageNotFoundError(map_id)

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
        logger.exception("Error getting map")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/maps/{map_id}/overlay/tactical",
    response_model=ImageResponse,
    summary="Add tactical overlay",
    response_description="The updated map"
)
async def add_tactical_overlay(
    request: TacticalOverlayRequest,
    map_id: UUID = Path(..., description="Map ID"),
    x_request_id: str = Header(None),
    x_api_key: str = Header(...),
    queue: QueueService = Depends(get_queue_service),
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Add tactical overlay to a map.

    Args:
        request: Overlay request
        map_id: Map ID
        x_request_id: Optional request ID
        x_api_key: API key for authentication
        queue: Queue service
        storage: Storage service

    Returns:
        Updated map details

    Raises:
        ImageNotFoundError: If map not found
        OverlayError: If overlay is invalid
    """
    # Validate API key
    validate_api_key(x_api_key, "maps:write")

    try:
        # Get map
        image = await storage.get_image_metadata(map_id)
        if not image:
            raise ImageNotFoundError(map_id)

        # Validate coordinates
        coordinates = []
        for element in request.elements:
            coordinates.append((element.position.x, element.position.y))

        validate_overlay_coordinates(
            coordinates,
            image.width,
            image.height
        )

        # Create overlay task
        task = await queue.enqueue_task(
            task_type=ImageType.OVERLAY,
            parameters={
                "map_id": str(map_id),
                "type": request.type,
                "elements": [e.dict() for e in request.elements]
            },
            request_id=x_request_id
        )

        # Get updated image
        updated = await storage.get_task_result(task.id)
        return {
            "id": updated.id,
            "type": updated.type,
            "url": updated.url,
            "size": {
                "width": updated.width,
                "height": updated.height
            },
            "theme": updated.theme,
            "cdn_url": updated.cdn_url,
            "metadata": updated.metadata
        }

    except (ImageNotFoundError, OverlayError):
        raise
    except Exception as e:
        logger.exception("Error adding tactical overlay")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/maps/{map_id}/overlay/campaign",
    response_model=ImageResponse,
    summary="Add campaign overlay",
    response_description="The updated map"
)
async def add_campaign_overlay(
    request: CampaignOverlayRequest,
    map_id: UUID = Path(..., description="Map ID"),
    x_request_id: str = Header(None),
    x_api_key: str = Header(...),
    queue: QueueService = Depends(get_queue_service),
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Add campaign overlay to a map.

    Args:
        request: Overlay request
        map_id: Map ID
        x_request_id: Optional request ID
        x_api_key: API key for authentication
        queue: Queue service
        storage: Storage service

    Returns:
        Updated map details

    Raises:
        ImageNotFoundError: If map not found
        OverlayError: If overlay is invalid
    """
    # Validate API key
    validate_api_key(x_api_key, "maps:write")

    try:
        # Get map
        image = await storage.get_image_metadata(map_id)
        if not image:
            raise ImageNotFoundError(map_id)

        # Validate coordinates
        for element in request.elements:
            coordinates = []
            for point in element.coordinates:
                coordinates.append((point.x, point.y))

            validate_overlay_coordinates(
                coordinates,
                image.width,
                image.height
            )

        # Create overlay task
        task = await queue.enqueue_task(
            task_type=ImageType.OVERLAY,
            parameters={
                "map_id": str(map_id),
                "type": request.type,
                "elements": [e.dict() for e in request.elements]
            },
            request_id=x_request_id
        )

        # Get updated image
        updated = await storage.get_task_result(task.id)
        return {
            "id": updated.id,
            "type": updated.type,
            "url": updated.url,
            "size": {
                "width": updated.width,
                "height": updated.height
            },
            "theme": updated.theme,
            "cdn_url": updated.cdn_url,
            "metadata": updated.metadata
        }

    except (ImageNotFoundError, OverlayError):
        raise
    except Exception as e:
        logger.exception("Error adding campaign overlay")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/maps/{map_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete map",
    response_description="Map deleted successfully"
)
async def delete_map(
    map_id: UUID = Path(..., description="Map ID"),
    x_api_key: str = Header(...),
    storage: StorageService = Depends(get_storage_service)
) -> Response:
    """Delete a map.

    Args:
        map_id: Map ID
        x_api_key: API key for authentication
        storage: Storage service

    Returns:
        Empty response

    Raises:
        ImageNotFoundError: If map not found
    """
    # Validate API key
    validate_api_key(x_api_key, "maps:delete")

    try:
        # Delete map
        success = await storage.delete_image(map_id)
        if not success:
            raise ImageNotFoundError(map_id)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ImageNotFoundError:
        raise
    except Exception as e:
        logger.exception("Error deleting map")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
