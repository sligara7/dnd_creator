"""Storage service client using Message Hub."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import ValidationError

from image_service.core.config import get_settings
from image_service.core.exceptions import ImageServiceError, StorageError
from image_service.core.logging import get_logger
from image_service.domain.models import (
    Image,
    ImageType,
    ImageSubtype,
    ImageContent,
    ImageMetadata,
    Overlay,
    OverlayType,
    GridSettings,
)
from image_service.integration.message_hub import MessageHubClient

settings = get_settings()
logger = get_logger(__name__)


class StorageServiceClient:
    """Client for storage service via Message Hub."""

    def __init__(self):
        """Initialize client."""
        self.message_hub = MessageHubClient()

    async def connect(self):
        """Connect to Message Hub."""
        await self.message_hub.connect()
        # Subscribe to storage service responses
        self.message_hub.subscribe("storage.response", self._handle_storage_response)

    async def close(self):
        """Close Message Hub connection."""
        await self.message_hub.close()

    async def _handle_storage_response(self, data: Dict[str, Any]) -> None:
        """Handle storage service response events."""
        try:
            if data.get("status") == "error":
                raise StorageError(
                    message=data.get("message", "Storage operation failed"),
                    code=data.get("code", "STORAGE_ERROR"),
                    details=data.get("details", {}),
                )
        except ValidationError as e:
            raise StorageError(
                message=str(e),
                code="VALIDATION_ERROR",
            )

    # Image operations
    async def create_image(
        self,
        type: ImageType,
        subtype: ImageSubtype,
        name: str,
        url: str,
        format: str,
        width: int,
        height: int,
        size: int,
        theme: str,
        description: Optional[str] = None,
        style_data: Optional[Dict[str, Any]] = None,
        generation_params: Optional[Dict[str, Any]] = None,
        source_id: Optional[UUID] = None,
        source_type: Optional[str] = None,
    ) -> Image:
        """Create new image."""
        operation_id = str(uuid4())
        data = {
            "operation": "create_image",
            "operation_id": operation_id,
            "data": {
                "type": type,
                "subtype": subtype,
                "name": name,
                "description": description,
                "url": url,
                "format": format,
                "width": width,
                "height": height,
                "size": size,
                "theme": theme,
                "style_data": style_data,
                "generation_params": generation_params,
                "source_id": str(source_id) if source_id else None,
                "source_type": source_type,
            },
        }
        await self.message_hub.publish(
            event_type="storage.request",
            data=data,
            correlation_id=operation_id,
        )
        
        # Wait for response event
        # Note: In a real implementation, this would use an async queue or response channel
        # For now, we'll simulate the response
        response_data = {
            "id": str(uuid4()),
            "type": type,
            "subtype": subtype,
            "url": url,
            "format": format,
            "width": width,
            "height": height,
            "theme": theme,
            "source_id": str(source_id) if source_id else None,
            "source_type": source_type,
            "generation_params": generation_params or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        return Image(
            id=UUID(response_data["id"]),
            type=ImageType(response_data["type"]),
            subtype=ImageSubtype(response_data["subtype"]),
            content=ImageContent(
                url=response_data["url"],
                format=response_data["format"],
                size={"width": response_data["width"], "height": response_data["height"]},
            ),
            metadata=ImageMetadata(
                theme=response_data["theme"],
                source_id=UUID(response_data["source_id"]) if response_data["source_id"] else None,
                service=response_data.get("source_type", "image_service"),
                generation_params=response_data.get("generation_params", {}),
                created_at=datetime.fromisoformat(response_data["created_at"]),
                updated_at=datetime.fromisoformat(response_data["updated_at"]),
            ),
        )

    async def get_image(self, image_id: UUID) -> Image:
        """Get image by ID."""
        operation_id = str(uuid4())
        data = {
            "operation": "get_image",
            "operation_id": operation_id,
            "data": {"image_id": str(image_id)},
        }
        await self.message_hub.publish(
            event_type="storage.request",
            data=data,
            correlation_id=operation_id,
        )
        
        # Wait for response event
        # Note: In a real implementation, this would use an async queue or response channel
        # For now, we'll simulate the response
        response_data = {
            "id": str(image_id),
            "type": "portrait",  # Example type
            "subtype": "character",  # Example subtype
            "url": "https://example.com/image.png",  # Example URL
            "format": "png",
            "width": 512,
            "height": 512,
            "theme": "fantasy",
            "source_id": None,
            "source_type": "image_service",
            "generation_params": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        return Image(
            id=UUID(response_data["id"]),
            type=ImageType(response_data["type"]),
            subtype=ImageSubtype(response_data["subtype"]),
            content=ImageContent(
                url=response_data["url"],
                format=response_data["format"],
                size={"width": response_data["width"], "height": response_data["height"]},
            ),
            metadata=ImageMetadata(
                theme=response_data["theme"],
                source_id=UUID(response_data["source_id"]) if response_data["source_id"] else None,
                service=response_data.get("source_type", "image_service"),
                generation_params=response_data.get("generation_params", {}),
                created_at=datetime.fromisoformat(response_data["created_at"]),
                updated_at=datetime.fromisoformat(response_data["updated_at"]),
            ),
        )

    async def list_images(
        self,
        type: Optional[str] = None,
        theme: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Image]:
        """List images with optional filters."""
        operation_id = str(uuid4())
        data = {
            "operation": "list_images",
            "operation_id": operation_id,
            "data": {
                "type": type,
                "theme": theme,
                "skip": skip,
                "limit": limit,
            },
        }
        await self.message_hub.publish(
            event_type="storage.request",
            data=data,
            correlation_id=operation_id,
        )

        # Wait for response event
        # Note: In a real implementation, this would use an async queue or response channel
        # For now, we'll simulate the response
        response_data = [{
            "id": str(uuid4()),
            "type": "portrait",
            "subtype": "character",
            "url": "https://example.com/image.png",
            "format": "png",
            "width": 512,
            "height": 512,
            "theme": theme or "fantasy",
            "source_id": None,
            "source_type": "image_service",
            "generation_params": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }]

        return [
            Image(
                id=UUID(item["id"]),
                type=ImageType(item["type"]),
                subtype=ImageSubtype(item["subtype"]),
                content=ImageContent(
                    url=item["url"],
                    format=item["format"],
                    size={"width": item["width"], "height": item["height"]},
                ),
                metadata=ImageMetadata(
                    theme=item["theme"],
                    source_id=UUID(item["source_id"]) if item["source_id"] else None,
                    service=item.get("source_type", "image_service"),
                    generation_params=item.get("generation_params", {}),
                    created_at=datetime.fromisoformat(item["created_at"]),
                    updated_at=datetime.fromisoformat(item["updated_at"]),
                ),
            )
            for item in response_data
        ]

    async def update_image(
        self,
        image_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        style_data: Optional[Dict[str, Any]] = None,
        generation_params: Optional[Dict[str, Any]] = None,
    ) -> Image:
        """Update image."""
        operation_id = str(uuid4())
        data = {
            "operation": "update_image",
            "operation_id": operation_id,
            "data": {
                "image_id": str(image_id),
                "name": name,
                "description": description,
                "style_data": style_data,
                "generation_params": generation_params,
            },
        }
        await self.message_hub.publish(
            event_type="storage.request",
            data=data,
            correlation_id=operation_id,
        )

        # Wait for response event
        # Note: In a real implementation, this would use an async queue or response channel
        # For now, we'll simulate the response
        response_data = {
            "id": str(image_id),
            "type": "portrait",
            "subtype": "character",
            "url": "https://example.com/image.png",
            "format": "png",
            "width": 512,
            "height": 512,
            "theme": "fantasy",
            "source_id": None,
            "source_type": "image_service",
            "generation_params": generation_params or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        return Image(
            id=UUID(response_data["id"]),
            type=ImageType(response_data["type"]),
            subtype=ImageSubtype(response_data["subtype"]),
            content=ImageContent(
                url=response_data["url"],
                format=response_data["format"],
                size={"width": response_data["width"], "height": response_data["height"]},
            ),
            metadata=ImageMetadata(
                theme=response_data["theme"],
                source_id=UUID(response_data["source_id"]) if response_data["source_id"] else None,
                service=response_data.get("source_type", "image_service"),
                generation_params=response_data.get("generation_params", {}),
                created_at=datetime.fromisoformat(response_data["created_at"]),
                updated_at=datetime.fromisoformat(response_data["updated_at"]),
            ),
        )

    async def delete_image(self, image_id: UUID) -> None:
        """Delete image."""
        operation_id = str(uuid4())
        data = {
            "operation": "delete_image",
            "operation_id": operation_id,
            "data": {"image_id": str(image_id)},
        }
        await self.message_hub.publish(
            event_type="storage.request",
            data=data,
            correlation_id=operation_id,
        )

        # Note: In a real implementation, we would wait for confirmation
        # For now, we'll assume success if no error is raised

    # Overlay operations
    async def create_overlay(
        self,
        image_id: UUID,
        type: OverlayType,
        name: str,
        data: Dict[str, Any],
        style: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Overlay:
        """Create new overlay."""
        data = {
            "image_id": str(image_id),
            "type": type,
            "name": name,
            "description": description,
            "data": data,
            "style": style,
        }
        response = await self.client.post("/api/v2/image-storage/overlays", json=data)
        data = await self._handle_response(response)
        return Overlay(
            id=UUID(data["id"]),
            image_id=UUID(data["image_id"]),
            type=OverlayType(data["type"]),
            elements=data["data"].get("elements", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    async def get_overlay(self, overlay_id: UUID) -> Overlay:
        """Get overlay by ID."""
        response = await self.client.get(f"/api/v2/image-storage/overlays/{overlay_id}")
        data = await self._handle_response(response)
        return Overlay(
            id=UUID(data["id"]),
            image_id=UUID(data["image_id"]),
            type=OverlayType(data["type"]),
            elements=data["data"].get("elements", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    async def list_overlays(self, image_id: UUID) -> List[Overlay]:
        """List overlays for image."""
        response = await self.client.get(
            f"/api/v2/image-storage/images/{image_id}/overlays"
        )
        data = await self._handle_response(response)
        return [
            Overlay(
                id=UUID(item["id"]),
                image_id=UUID(item["image_id"]),
                type=OverlayType(item["type"]),
                elements=item["data"].get("elements", []),
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=datetime.fromisoformat(item["updated_at"]),
            )
            for item in data
        ]

    # Grid operations
    async def create_grid(
        self,
        image_id: UUID,
        settings: GridSettings,
    ) -> Dict[str, Any]:
        """Create map grid."""
        data = {
            "image_id": str(image_id),
            "enabled": settings.enabled,
            "size": settings.size,
            "color": settings.color,
            "opacity": 0.5,  # Default opacity
        }
        response = await self.client.post("/api/v2/image-storage/grids", json=data)
        return await self._handle_response(response)

    async def get_grid(self, grid_id: UUID) -> Dict[str, Any]:
        """Get grid by ID."""
        response = await self.client.get(f"/api/v2/image-storage/grids/{grid_id}")
        return await self._handle_response(response)

    async def get_image_grid(self, image_id: UUID) -> Optional[Dict[str, Any]]:
        """Get grid for image."""
        try:
            response = await self.client.get(
                f"/api/v2/image-storage/images/{image_id}/grid"
            )
            return await self._handle_response(response)
        except StorageError as e:
            if "Grid not found" in str(e):
                return None
            raise