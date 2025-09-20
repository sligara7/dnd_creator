"""Storage service client."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
from pydantic import ValidationError

from image_service.core.config import get_settings
from image_service.core.exceptions import ImageServiceError, StorageError
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

settings = get_settings()


class StorageServiceClient:
    """Client for storage service API."""

    def __init__(self):
        """Initialize client."""
        self.base_url = settings.STORAGE_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response."""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error = response.json()
                raise StorageError(
                    message=error.get("message", str(e)),
                    code=error.get("code", "STORAGE_ERROR"),
                    details=error.get("details", {}),
                )
            except ValueError:
                raise StorageError(
                    message=str(e),
                    code="STORAGE_ERROR",
                )
        except (httpx.RequestError, ValidationError) as e:
            raise StorageError(
                message=str(e),
                code="STORAGE_ERROR",
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
        data = {
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
        }
        response = await self.client.post("/api/v2/image-storage/images", json=data)
        data = await self._handle_response(response)
        return Image(
            id=UUID(data["id"]),
            type=ImageType(data["type"]),
            subtype=ImageSubtype(data["subtype"]),
            content=ImageContent(
                url=data["url"],
                format=data["format"],
                size={"width": data["width"], "height": data["height"]},
            ),
            metadata=ImageMetadata(
                theme=data["theme"],
                source_id=UUID(data["source_id"]) if data["source_id"] else None,
                service=data.get("source_type", "image_service"),
                generation_params=data.get("generation_params", {}),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            ),
        )

    async def get_image(self, image_id: UUID) -> Image:
        """Get image by ID."""
        response = await self.client.get(f"/api/v2/image-storage/images/{image_id}")
        data = await self._handle_response(response)
        return Image(
            id=UUID(data["id"]),
            type=ImageType(data["type"]),
            subtype=ImageSubtype(data["subtype"]),
            content=ImageContent(
                url=data["url"],
                format=data["format"],
                size={"width": data["width"], "height": data["height"]},
            ),
            metadata=ImageMetadata(
                theme=data["theme"],
                source_id=UUID(data["source_id"]) if data["source_id"] else None,
                service=data.get("source_type", "image_service"),
                generation_params=data.get("generation_params", {}),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
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
        params = {"skip": skip, "limit": limit}
        if type:
            params["type"] = type
        if theme:
            params["theme"] = theme

        response = await self.client.get("/api/v2/image-storage/images", params=params)
        data = await self._handle_response(response)
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
            for item in data
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
        data = {
            "name": name,
            "description": description,
            "style_data": style_data,
            "generation_params": generation_params,
        }
        response = await self.client.put(
            f"/api/v2/image-storage/images/{image_id}",
            json={k: v for k, v in data.items() if v is not None},
        )
        data = await self._handle_response(response)
        return Image(
            id=UUID(data["id"]),
            type=ImageType(data["type"]),
            subtype=ImageSubtype(data["subtype"]),
            content=ImageContent(
                url=data["url"],
                format=data["format"],
                size={"width": data["width"], "height": data["height"]},
            ),
            metadata=ImageMetadata(
                theme=data["theme"],
                source_id=UUID(data["source_id"]) if data["source_id"] else None,
                service=data.get("source_type", "image_service"),
                generation_params=data.get("generation_params", {}),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
            ),
        )

    async def delete_image(self, image_id: UUID) -> None:
        """Delete image."""
        response = await self.client.delete(f"/api/v2/image-storage/images/{image_id}")
        await self._handle_response(response)

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