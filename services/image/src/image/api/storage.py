"""API endpoints for storage management."""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter, Depends, File, Form, HTTPException, Query, Response,
    UploadFile, status
)
from pydantic import BaseModel

from image.core.cdn_config import CdnRegion
from image.core.dependencies import get_cdn_service, get_storage_service
from image.models.storage import ImageType
from image.services.cdn import CDNService
from image.services.storage import StorageService

logger = logging.getLogger(__name__)
router = APIRouter()


class ImageUploadResponse(BaseModel):
    """Response model for image upload."""

    id: UUID
    type: str
    format: str
    width: int
    height: int
    cdn_url: Optional[str]


class ImageMetadataResponse(BaseModel):
    """Response model for image metadata."""

    id: UUID
    type: str
    format: str
    width: int
    height: int
    cdn_url: Optional[str]
    theme: Optional[str]
    tags: List[str]
    metadata: dict
    version: int


class ImageUploadOptions(BaseModel):
    """Options for image upload."""

    type: ImageType
    theme: Optional[str] = None
    tags: List[str] = []
    metadata: dict = {}
    cdn_region: Optional[CdnRegion] = None
    push_to_cdn: bool = True


class ImageBatchResponse(BaseModel):
    """Response model for batch operations."""

    successful: List[UUID]
    failed: List[UUID]
    error_details: Optional[dict]


@router.post(
    "/images",
    response_model=ImageUploadResponse,
    summary="Upload new image",
    response_description="The uploaded image"
)
async def upload_image(
    file: UploadFile = File(...),
    type: ImageType = Form(...),
    theme: Optional[str] = Form(None),
    tags: List[str] = Form([]),
    metadata: dict = Form({}),
    cdn_region: Optional[CdnRegion] = Form(None),
    push_to_cdn: bool = Form(True),
    storage: StorageService = Depends(get_storage_service),
    cdn: CDNService = Depends(get_cdn_service)
) -> dict:
    """Upload a new image.

    Args:
        file: Image file
        type: Image type
        theme: Optional theme
        tags: Optional tags
        metadata: Optional metadata
        cdn_region: Optional CDN region
        push_to_cdn: Whether to push to CDN
        storage: Storage service
        cdn: CDN service

    Returns:
        Uploaded image details
    """
    try:
        # Upload image to storage
        image = await storage.upload_image(file, type, metadata)

        # Push to CDN if requested
        cdn_url = None
        if push_to_cdn:
            cdn_url = await cdn.push_to_cdn(image.id, cdn_region)
            await storage.update_cdn_url(image.id, cdn_url)

        return {
            "id": image.id,
            "type": image.type.value,
            "format": image.format.value,
            "width": image.width,
            "height": image.height,
            "cdn_url": cdn_url
        }

    except Exception as e:
        logger.exception("Image upload failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/images/{image_id}",
    response_model=ImageMetadataResponse,
    summary="Get image metadata",
    response_description="The image metadata"
)
async def get_image_metadata(
    image_id: UUID,
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Get image metadata.

    Args:
        image_id: Image ID
        storage: Storage service

    Returns:
        Image metadata

    Raises:
        HTTPException: If image not found
    """
    try:
        image = await storage.get_image_metadata(image_id)
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )

        return {
            "id": image.id,
            "type": image.type.value,
            "format": image.format.value,
            "width": image.width,
            "height": image.height,
            "cdn_url": image.cdn_url,
            "theme": image.theme,
            "tags": image.tags,
            "metadata": image.metadata,
            "version": image.version
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting image metadata")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/images/{image_id}/content",
    response_class=Response,
    summary="Download image content",
    response_description="The image binary data"
)
async def download_image(
    image_id: UUID,
    cdn_region: Optional[CdnRegion] = None,
    storage: StorageService = Depends(get_storage_service),
    cdn: CDNService = Depends(get_cdn_service)
) -> Response:
    """Download image content.

    Args:
        image_id: Image ID
        cdn_region: Optional CDN region
        storage: Storage service
        cdn: CDN service

    Returns:
        Image content response
    """
    try:
        # Try CDN first
        try:
            content = await cdn.get_from_cdn(image_id, cdn_region)
            return Response(
                content=content,
                media_type="image/jpeg"  # TODO: Get from metadata
            )
        except Exception:
            # Fall back to storage
            content, image = await storage.download_image(image_id)
            return Response(
                content=content,
                media_type=f"image/{image.format.value}"
            )

    except Exception as e:
        logger.exception("Error downloading image")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete image",
    response_description="Image deleted successfully"
)
async def delete_image(
    image_id: UUID,
    storage: StorageService = Depends(get_storage_service),
    cdn: CDNService = Depends(get_cdn_service)
) -> Response:
    """Delete an image.

    Args:
        image_id: Image ID
        storage: Storage service
        cdn: CDN service

    Returns:
        Empty response
    """
    try:
        # Delete from storage
        await storage.delete_image(image_id)

        # Invalidate CDN
        try:
            await cdn.invalidate_cdn(image_id)
        except Exception:
            logger.warning("CDN invalidation failed", exc_info=True)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.exception("Error deleting image")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/images/{image_id}/version",
    response_model=ImageUploadResponse,
    summary="Create new image version",
    response_description="The new image version"
)
async def create_image_version(
    image_id: UUID,
    type: ImageType = Form(...),
    theme: Optional[str] = Form(None),
    tags: List[str] = Form([]),
    metadata: dict = Form({}),
    storage: StorageService = Depends(get_storage_service)
) -> dict:
    """Create new version of existing image.

    Args:
        image_id: Parent image ID
        type: Image type
        theme: Optional theme
        tags: Optional tags
        metadata: Optional metadata
        storage: Storage service

    Returns:
        New image version details

    Raises:
        HTTPException: If parent image not found
    """
    try:
        image = await storage.create_version(
            image_id,
            type,
            theme=theme,
            tags=tags,
            metadata=metadata
        )
        return {
            "id": image.id,
            "type": image.type.value,
            "format": image.format.value,
            "width": image.width,
            "height": image.height,
            "cdn_url": image.cdn_url
        }

    except Exception as e:
        logger.exception("Error creating image version")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/images/batch/delete",
    response_model=ImageBatchResponse,
    summary="Delete multiple images",
    response_description="Batch deletion results"
)
async def batch_delete_images(
    image_ids: List[UUID],
    storage: StorageService = Depends(get_storage_service),
    cdn: CDNService = Depends(get_cdn_service)
) -> dict:
    """Delete multiple images.

    Args:
        image_ids: List of image IDs to delete
        storage: Storage service
        cdn: CDN service

    Returns:
        Batch operation results
    """
    successful = []
    failed = []
    error_details = {}

    for image_id in image_ids:
        try:
            # Delete from storage
            await storage.delete_image(image_id)

            # Invalidate CDN
            try:
                await cdn.invalidate_cdn(image_id)
            except Exception:
                logger.warning("CDN invalidation failed", exc_info=True)

            successful.append(image_id)

        except Exception as e:
            failed.append(image_id)
            error_details[str(image_id)] = str(e)

    return {
        "successful": successful,
        "failed": failed,
        "error_details": error_details
    }


@router.get(
    "/images",
    response_model=List[ImageMetadataResponse],
    summary="List images",
    response_description="List of images"
)
async def list_images(
    type: Optional[ImageType] = None,
    theme: Optional[str] = None,
    limit: int = Query(100, gt=0, le=1000),
    offset: int = Query(0, ge=0),
    storage: StorageService = Depends(get_storage_service)
) -> List[dict]:
    """List images with optional filtering.

    Args:
        type: Optional image type filter
        theme: Optional theme filter
        limit: Maximum number of results
        offset: Pagination offset
        storage: Storage service

    Returns:
        List of images
    """
    try:
        images = await storage.list_images(
            type=type,
            theme=theme,
            limit=limit,
            offset=offset
        )
        return [
            {
                "id": image.id,
                "type": image.type.value,
                "format": image.format.value,
                "width": image.width,
                "height": image.height,
                "cdn_url": image.cdn_url,
                "theme": image.theme,
                "tags": image.tags,
                "metadata": image.metadata,
                "version": image.version
            }
            for image in images
        ]

    except Exception as e:
        logger.exception("Error listing images")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
