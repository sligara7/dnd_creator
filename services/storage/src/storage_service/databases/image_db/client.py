"""Image database client."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from .models import Image, Overlay


class ImageDBClient:
    """Client for image database operations."""

    def __init__(self, storage_client):
        """Initialize the client.

        Args:
            storage_client: The storage service client
        """
        self.storage = storage_client

    async def get_image(self, id: UUID) -> Optional[Dict]:
        """Get an image by ID.

        Args:
            id: Image UUID

        Returns:
            Image data or None if not found
        """
        return await self.storage.read(
            "image_db",
            "images",
            {"id": id, "is_deleted": False}
        )

    async def list_images(self, type: str = None, subtype: str = None, limit: int = 100) -> List[Dict]:
        """List images with optional filtering.

        Args:
            type: Optional image type filter
            subtype: Optional image subtype filter
            limit: Maximum number of images to return

        Returns:
            List of image data
        """
        filters = {"is_deleted": False}
        if type:
            filters["type"] = type
        if subtype:
            filters["subtype"] = subtype

        return await self.storage.read(
            "image_db",
            "images",
            filters,
            limit=limit,
            order_by=["-created_at"]
        )

    async def create_image(self, image: Dict) -> Dict:
        """Create a new image.

        Args:
            image: Image data

        Returns:
            Created image data
        """
        return await self.storage.write(
            "image_db",
            "images",
            image
        )

    async def update_image(self, id: UUID, data: Dict) -> Optional[Dict]:
        """Update an image.

        Args:
            id: Image UUID
            data: Updated image data

        Returns:
            Updated image data or None if not found
        """
        data["updated_at"] = datetime.utcnow()
        return await self.storage.update(
            "image_db",
            "images",
            {"id": id, "is_deleted": False},
            data
        )

    async def delete_image(self, id: UUID) -> bool:
        """Soft delete an image.

        Args:
            id: Image UUID

        Returns:
            True if image was deleted
        """
        result = await self.storage.update(
            "image_db",
            "images",
            {"id": id, "is_deleted": False},
            {
                "is_deleted": True,
                "deleted_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        return result is not None

    async def get_overlay(self, id: UUID) -> Optional[Dict]:
        """Get an overlay by ID.

        Args:
            id: Overlay UUID

        Returns:
            Overlay data or None if not found
        """
        return await self.storage.read(
            "image_db",
            "overlays",
            {"id": id, "is_deleted": False}
        )

    async def list_overlays(self, image_id: UUID, type: str = None) -> List[Dict]:
        """List overlays for an image.

        Args:
            image_id: Image UUID
            type: Optional overlay type filter

        Returns:
            List of overlay data
        """
        filters = {
            "image_id": image_id,
            "is_deleted": False
        }
        if type:
            filters["type"] = type

        return await self.storage.read(
            "image_db",
            "overlays",
            filters,
            order_by=["created_at"]
        )

    async def create_overlay(self, overlay: Dict) -> Dict:
        """Create a new overlay.

        Args:
            overlay: Overlay data

        Returns:
            Created overlay data
        """
        return await self.storage.write(
            "image_db",
            "overlays",
            overlay
        )

    async def update_overlay(self, id: UUID, data: Dict) -> Optional[Dict]:
        """Update an overlay.

        Args:
            id: Overlay UUID
            data: Updated overlay data

        Returns:
            Updated overlay data or None if not found
        """
        data["updated_at"] = datetime.utcnow()
        return await self.storage.update(
            "image_db",
            "overlays",
            {"id": id, "is_deleted": False},
            data
        )

    async def delete_overlay(self, id: UUID) -> bool:
        """Soft delete an overlay.

        Args:
            id: Overlay UUID

        Returns:
            True if overlay was deleted
        """
        result = await self.storage.update(
            "image_db",
            "overlays",
            {"id": id, "is_deleted": False},
            {
                "is_deleted": True,
                "deleted_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        )
        return result is not None

    async def delete_image_overlays(self, image_id: UUID) -> int:
        """Soft delete all overlays for an image.

        Args:
            image_id: Image UUID

        Returns:
            Number of overlays deleted
        """
        overlays = await self.list_overlays(image_id)
        count = 0
        for overlay in overlays:
            if await self.delete_overlay(overlay["id"]):
                count += 1
        return count