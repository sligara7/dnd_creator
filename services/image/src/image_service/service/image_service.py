from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from image_service.core.exceptions import (
    GenerationError,
    ImageNotFoundError,
    InvalidThemeError,
)
from image_service.core.messaging import MessageHub
from image_service.domain.models import (
    Image,
    ImageContent,
    ImageMetadata,
    ImageSubtype,
    ImageType,
    Overlay,
    OverlayRequest,
    ThemeRequest,
)
from image_service.integration.getimg import GetImgClient
from image_service.integration.storage import ImageStorage
from image_service.repository.repository import ImageRepository


class ImageService:
    """Core service for image operations"""

    def __init__(
        self,
        repository: ImageRepository,
        storage: ImageStorage,
        getimg: GetImgClient,
        message_hub: MessageHub,
    ):
        self.repository = repository
        self.storage = storage
        self.getimg = getimg
        self.message_hub = message_hub

    async def get_image(self, image_id: UUID) -> Image:
        """Get image by ID"""
        image = await self.repository.get_image(image_id)
        if not image:
            raise ImageNotFoundError(f"Image not found: {image_id}")
        return image

    async def create_tactical_map(
        self,
        size: Dict,
        grid: Dict,
        theme: str,
        features: List[str],
        terrain: Dict,
    ) -> Image:
        """Generate tactical map"""
        prompt, neg_prompt = self.getimg._build_map_prompt(
            theme, features, terrain, is_tactical=True
        )
        
        try:
            # Generate image
            image_url = await self.getimg.generate_image(
                prompt=prompt,
                negative_prompt=neg_prompt,
                size=(size["width"], size["height"]),
            )
            
            # Store image
            object_name = f"maps/tactical/{uuid4()}.png"
            stored_url = await self.storage.store_from_url(image_url, object_name)
            
            # Create image record
            image = Image(
                id=uuid4(),
                type=ImageType.MAP,
                subtype=ImageSubtype.TACTICAL,
                content=ImageContent(
                    url=stored_url,
                    format="png",
                    size=size,
                ),
                metadata=ImageMetadata(
                    theme=theme,
                    service="getimg",
                    generation_params={
                        "prompt": prompt,
                        "negative_prompt": neg_prompt,
                        "grid": grid,
                        "terrain": terrain,
                        "features": features,
                    },
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
            )
            
            await self.repository.create_image(image)
            
            # Publish event
            await self.message_hub.publish_event(
                "image_generated",
                {
                    "image_id": str(image.id),
                    "type": "map",
                    "subtype": "tactical",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            
            return image
            
        except Exception as e:
            raise GenerationError(f"Failed to generate tactical map: {str(e)}")

    async def create_campaign_map(
        self,
        size: Dict,
        scale: Dict,
        theme: str,
        features: List[str],
        points_of_interest: List[Dict],
    ) -> Image:
        """Generate campaign map"""
        prompt, neg_prompt = self.getimg._build_map_prompt(
            theme, features, {"type": "region"}, is_tactical=False
        )
        
        try:
            # Generate image
            image_url = await self.getimg.generate_image(
                prompt=prompt,
                negative_prompt=neg_prompt,
                size=(size["width"], size["height"]),
            )
            
            # Store image
            object_name = f"maps/campaign/{uuid4()}.png"
            stored_url = await self.storage.store_from_url(image_url, object_name)
            
            # Create image record
            image = Image(
                id=uuid4(),
                type=ImageType.MAP,
                subtype=ImageSubtype.CAMPAIGN,
                content=ImageContent(
                    url=stored_url,
                    format="png",
                    size=size,
                ),
                metadata=ImageMetadata(
                    theme=theme,
                    service="getimg",
                    generation_params={
                        "prompt": prompt,
                        "negative_prompt": neg_prompt,
                        "scale": scale,
                        "features": features,
                        "points_of_interest": points_of_interest,
                    },
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
            )
            
            await self.repository.create_image(image)
            
            # Publish event
            await self.message_hub.publish_event(
                "image_generated",
                {
                    "image_id": str(image.id),
                    "type": "map",
                    "subtype": "campaign",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            
            return image
            
        except Exception as e:
            raise GenerationError(f"Failed to generate campaign map: {str(e)}")

    async def create_portrait(
        self,
        character_id: UUID,
        theme: str,
        style: Dict,
        equipment: Dict,
    ) -> Image:
        """Generate character portrait"""
        # TODO: Get character details from character service
        character_details = {
            "id": character_id,
            "race": "human",  # Placeholder
            "class": "fighter",  # Placeholder
            "equipment": equipment.get("items", []),
        }
        
        prompt, neg_prompt = self.getimg._build_portrait_prompt(
            character_details, theme, style
        )
        
        try:
            # Generate image
            image_url = await self.getimg.generate_image(
                prompt=prompt,
                negative_prompt=neg_prompt,
            )
            
            # Enhance face
            enhanced_url = await self.getimg.enhance_face(image_url)
            
            # Store image
            object_name = f"portraits/{character_id}/{uuid4()}.png"
            stored_url = await self.storage.store_from_url(enhanced_url, object_name)
            
            # Create image record
            image = Image(
                id=uuid4(),
                type=ImageType.CHARACTER,
                subtype=ImageSubtype.PORTRAIT,
                content=ImageContent(
                    url=stored_url,
                    format="png",
                    size={"width": 1024, "height": 1024},
                ),
                metadata=ImageMetadata(
                    theme=theme,
                    source_id=character_id,
                    service="getimg",
                    generation_params={
                        "prompt": prompt,
                        "negative_prompt": neg_prompt,
                        "style": style,
                        "equipment": equipment,
                    },
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
            )
            
            await self.repository.create_image(image)
            
            # Publish event
            await self.message_hub.publish_event(
                "image_generated",
                {
                    "image_id": str(image.id),
                    "type": "character",
                    "source_id": str(character_id),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            
            return image
            
        except Exception as e:
            raise GenerationError(f"Failed to generate portrait: {str(e)}")

    async def create_item_image(
        self,
        item_id: UUID,
        item_type: str,
        theme: str,
        style: Dict,
        properties: Dict,
    ) -> Image:
        """Generate item image"""
        # TODO: Get item details from catalog service
        item_details = {
            "id": item_id,
            "type": item_type,
        }
        
        prompt, neg_prompt = self.getimg._build_item_prompt(
            item_details, theme, style, properties
        )
        
        try:
            # Generate image
            image_url = await self.getimg.generate_image(
                prompt=prompt,
                negative_prompt=neg_prompt,
            )
            
            # Store image
            object_name = f"items/{item_id}/{uuid4()}.png"
            stored_url = await self.storage.store_from_url(image_url, object_name)
            
            # Create image record
            image = Image(
                id=uuid4(),
                type=ImageType.ITEM,
                subtype=getattr(ImageSubtype, item_type.upper()),
                content=ImageContent(
                    url=stored_url,
                    format="png",
                    size={"width": 1024, "height": 1024},
                ),
                metadata=ImageMetadata(
                    theme=theme,
                    source_id=item_id,
                    service="getimg",
                    generation_params={
                        "prompt": prompt,
                        "negative_prompt": neg_prompt,
                        "style": style,
                        "properties": properties,
                    },
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                ),
            )
            
            await self.repository.create_image(image)
            
            # Publish event
            await self.message_hub.publish_event(
                "image_generated",
                {
                    "image_id": str(image.id),
                    "type": "item",
                    "source_id": str(item_id),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            
            return image
            
        except Exception as e:
            raise GenerationError(f"Failed to generate item image: {str(e)}")

    async def add_overlay(
        self,
        image_id: UUID,
        overlay: OverlayRequest,
    ) -> Overlay:
        """Add overlay to image"""
        image = await self.get_image(image_id)
        
        # Create overlay
        overlay_obj = Overlay(
            id=uuid4(),
            image_id=image_id,
            type=overlay.type,
            elements=overlay.elements,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        await self.repository.create_overlay(overlay_obj)
        
        # Publish event
        await self.message_hub.publish_event(
            "overlay_updated",
            {
                "map_id": str(image_id),
                "overlay_id": str(overlay_obj.id),
                "changes": [e.dict() for e in overlay.elements],
            },
        )
        
        return overlay_obj

    async def apply_theme(
        self,
        image_id: UUID,
        theme_request: ThemeRequest,
    ) -> Image:
        """Apply theme to image"""
        image = await self.get_image(image_id)
        
        try:
            # Apply style transfer
            new_url = await self.getimg.apply_style_transfer(
                image.content.url,
                theme_request.theme,
                theme_request.strength,
            )
            
            # Store new image
            object_name = f"{image.type.value}s/{image.id}/{uuid4()}.png"
            stored_url = await self.storage.store_from_url(new_url, object_name)
            
            # Update image
            image.content.url = stored_url
            image.metadata.theme = theme_request.theme
            image.metadata.updated_at = datetime.utcnow()
            
            await self.repository.update_image(image)
            
            # Publish event
            await self.message_hub.publish_event(
                "theme_applied",
                {
                    "image_id": str(image.id),
                    "theme": theme_request.theme,
                    "elements": theme_request.elements,
                },
            )
            
            return image
            
        except Exception as e:
            raise InvalidThemeError(f"Failed to apply theme: {str(e)}")

    async def delete_image(self, image_id: UUID):
        """Delete image and associated overlays"""
        image = await self.get_image(image_id)
        
        # Delete from storage
        object_name = self.storage.get_object_name(image.content.url)
        await self.storage.delete(object_name)
        
        # Delete from database
        await self.repository.delete_image(image_id)
