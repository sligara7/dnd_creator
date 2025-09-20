"""Image operations router."""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile

from image_service.core.dependencies import get_storage
from image_service.core.exceptions import ImageServiceError
from image_service.domain.models import Image, ImageType, ImageSubtype
from image_service.integration.storage_service import StorageServiceClient

router = APIRouter(
    prefix="/api/v2/images",
    tags=["images"],
)


@router.post("/")
async def upload_image(
    image: UploadFile = File(...),
    type: ImageType = Form(...),
    subtype: ImageSubtype = Form(...),
    name: str = Form(...),
    theme: str = Form(...),
    storage: StorageServiceClient = Depends(get_storage),
) -> Image:
    """Upload a new image."""
    if not image.content_type or not image.content_type.startswith("image/"):
        raise ImageServiceError(
            message="Invalid file type",
            code="INVALID_FILE_TYPE",
            content_type=image.content_type,
        )

    content = await image.read()
    if not content:
        raise ImageServiceError(
            message="Empty file",
            code="EMPTY_FILE",
        )

    # Extract format from content type
    format = image.content_type.split("/")[-1]

    # TODO: Process image to get dimensions
    width = 512  # Example value
    height = 512  # Example value
    size = len(content)

    # Create image in storage service
    return await storage.create_image(
        type=type,
        subtype=subtype,
        name=name,
        url="",  # URL will be returned by storage service
        format=format,
        width=width,
        height=height,
        size=size,
        theme=theme,
    )


@router.get("/{image_id}")
async def get_image(
    image_id: uuid.UUID,
    storage: StorageServiceClient = Depends(get_storage),
) -> Image:
    """Get image by ID."""
    return await storage.get_image(image_id)


@router.get("/")
async def list_images(
    type: Optional[str] = None,
    theme: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    storage: StorageServiceClient = Depends(get_storage),
) -> List[Image]:
    """List images with optional filters."""
    return await storage.list_images(
        type=type,
        theme=theme,
        skip=skip,
        limit=limit,
    )


@router.delete("/{image_id}")
async def delete_image(
    image_id: uuid.UUID,
    storage: StorageServiceClient = Depends(get_storage),
) -> None:
    """Delete image."""
    await storage.delete_image(image_id)