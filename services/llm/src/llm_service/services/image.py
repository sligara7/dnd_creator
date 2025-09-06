import uuid
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from llm_service.core.cache import AsyncCacheService
from llm_service.core.events import MessageHubClient, ImageGeneratedEvent
from llm_service.core.settings import Settings
from llm_service.models.content import ImageContent
from llm_service.schemas.image import
    GeneratedImage,
    ImageEnhancementRequest,
    ImageGenerationResponse,
    ImageToImageRequest,
    TextToImageRequest,
    ContentMetadata,
)
from llm_service.services.getimg_ai import GetImgAIClient


class ImageGenerationService(AsyncCacheService):
    """Service for generating and processing images."""

def __init__(
        self, settings: Settings, client: GetImgAIClient, db: AsyncSession, message_hub: MessageHubClient, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(settings, *args, **kwargs)
        self.client = client
        self.db = db
        self.message_hub = message_hub

    async def initialize(self) -> None:
        """Initialize service resources."""
        pass

    async def cleanup(self) -> None:
        """Clean up service resources."""
        await self.client.close()

    async def _check_cache(self, cache_key: str) -> Optional[GeneratedImage]:
        """Check cache for existing content."""
        if cached := await self.get_json(cache_key):
            return GeneratedImage.model_validate(cached)
        return None

    async def _save_image(
        self,
        image_data: str,
        image_type: str,
        metadata: ContentMetadata,
        parent_image_id: Optional[uuid.UUID] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> uuid.UUID:
        """Save image to database."""
        # Create thumbnail
        thumbnail = self.client.create_thumbnail(image_data)

        # Create database record
        content = ImageContent(
            image_data=image_data,
            image_type=image_type,
            parent_image_id=parent_image_id,
            metadata=metadata.model_dump(),
            thumbnail=thumbnail,
            width=width or 512,
            height=height or 512,
        )
        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)

        return content.id

    async def generate_character_image(
        self, request: TextToImageRequest, character_id: uuid.UUID, request_id: uuid.UUID
    ) -> GeneratedImage:
        """Generate character image."""
        # Create prompt from template
        from .prompts.image import get_character_portrait_prompt, get_character_action_prompt
        
        prompt = get_character_portrait_prompt(
            character_class=request.parameters.character_class,
            character_race=request.parameters.character_race,
            character_level=request.parameters.character_level,
            equipment=request.parameters.equipment,
            theme=request.parameters.theme,
        )
        
        # Generate image
        try:
            image_data = await self.client.generate_image(request)
        except Exception as e:
            self.logger.error(
                "character_image_generation_failed",
                error=str(e),
                character_id=str(character_id),
                request_id=str(request_id),
            )
            raise

        # Create metadata
        metadata = ContentMetadata(
            request_id=request_id,
            source_service=request.model.name,
            model_used=request.model.name,
            prompt_used=prompt,
            settings_used={
                "character_id": str(character_id),
                "negative_prompt": request.parameters.negative_prompt,
                "style_preset": request.parameters.style_preset,
                "size": request.size.model_dump(),
                **request.model.model_dump(),
            },
        )

        # Save character image
        from ..models.image import CharacterImage
        character_image = CharacterImage(
            character_id=character_id,
            content_type="character",
            image_type="portrait",
            generated_by=request.model.name,
            prompt=prompt,
            result_image=image_data,
            thumbnail=self.client.create_thumbnail(image_data),
            parameters=request.parameters.dict(),
            metadata=metadata.dict(),
        )
        self.db.add(character_image)
        await self.db.commit()
        await self.db.refresh(character_image)

        # Create response
        result = GeneratedImage(
            image_data=image_data,
            image_id=character_image.id,
            metadata=metadata,
            parameters_used=metadata.settings_used,
        )

        # Publish event
        await self.message_hub.publish_event({
            "type": "character_image_generated",
            "image_id": str(character_image.id),
            "character_id": str(character_id),
            "image_type": "portrait",
        })

        return result

    async def generate_location_image(
        self, request: TextToImageRequest, location_id: uuid.UUID, request_id: uuid.UUID
    ) -> Dict[str, GeneratedImage]:
        """Generate location imagery."""
        results = {}

        # Create location visualization
        from .prompts.image import get_location_prompt
        location_prompt = get_location_prompt(
            location_type=request.parameters.location_type,
            size=request.parameters.size,
            purpose=request.parameters.purpose,
            features=request.parameters.features,
            theme=request.parameters.theme,
        )

        # Generate visualization
        try:
            vis_data = await self.client.generate_image(request)
        except Exception as e:
            self.logger.error(
                "location_image_generation_failed",
                error=str(e),
                location_id=str(location_id),
                request_id=str(request_id),
            )
            raise

        # Save location visualization
        from ..models.image import LocationImage
        location_image = LocationImage(
            location_id=location_id,
            content_type="location",
            location_type=request.parameters.location_type,
            generated_by=request.model.name,
            prompt=location_prompt,
            result_image=vis_data,
            thumbnail=self.client.create_thumbnail(vis_data),
            parameters=request.parameters.dict(),
            metadata={
                "request_id": str(request_id),
                "location_type": request.parameters.location_type,
                "size": request.parameters.size,
                "purpose": request.parameters.purpose,
            },
        )
        self.db.add(location_image)
        await self.db.commit()
        await self.db.refresh(location_image)

        results["visualization"] = GeneratedImage(
            image_data=vis_data,
            image_id=location_image.id,
            metadata=ContentMetadata(
                request_id=request_id,
                source_service=request.model.name,
                model_used=request.model.name,
                prompt_used=location_prompt,
                settings_used=request.parameters.dict(),
            ),
            parameters_used=request.parameters.dict(),
        )

        # Generate map if requested
        if request.parameters.generate_map:
            from .prompts.image import get_map_prompt
            map_prompt = get_map_prompt(
                location_type=request.parameters.location_type,
                size=request.parameters.size,
                important_areas=request.parameters.features,
                details=request.parameters.details,
            )

            map_request = request.model_copy()
            map_request.prompt = map_prompt

            try:
                map_data = await self.client.generate_image(map_request)
            except Exception as e:
                self.logger.error(
                    "map_generation_failed",
                    error=str(e),
                    location_id=str(location_id),
                    request_id=str(request_id),
                )
                raise

            # Save map
            map_image = LocationImage(
                location_id=location_id,
                content_type="map",
                location_type=request.parameters.location_type,
                generated_by=request.model.name,
                prompt=map_prompt,
                result_image=map_data,
                thumbnail=self.client.create_thumbnail(map_data),
                parameters=request.parameters.dict(),
                metadata={
                    "request_id": str(request_id),
                    "location_type": request.parameters.location_type,
                    "map_style": "fantasy",
                },
            )
            self.db.add(map_image)
            await self.db.commit()
            await self.db.refresh(map_image)

            results["map"] = GeneratedImage(
                image_data=map_data,
                image_id=map_image.id,
                metadata=ContentMetadata(
                    request_id=request_id,
                    source_service=request.model.name,
                    model_used=request.model.name,
                    prompt_used=map_prompt,
                    settings_used=request.parameters.dict(),
                ),
                parameters_used=request.parameters.dict(),
            )

        # Publish event
        await self.message_hub.publish_event({
            "type": "location_images_generated",
            "location_id": str(location_id),
            "image_types": list(results.keys()),
        })

        return results

    async def generate_item_image(
        self, request: TextToImageRequest, item_id: uuid.UUID, request_id: uuid.UUID
    ) -> GeneratedImage:
        """Generate item illustration."""
        # Create prompt from template
        from .prompts.image import get_item_prompt
        prompt = get_item_prompt(
            item_type=request.parameters.item_type,
            rarity=request.parameters.rarity,
            magical=request.parameters.is_magical,
            properties=request.parameters.properties,
            theme=request.parameters.theme,
        )

        # Update request with template prompt
        request.prompt = prompt

        # Generate image
        try:
            image_data = await self.client.generate_image(request)
        except Exception as e:
            self.logger.error(
                "item_image_generation_failed",
                error=str(e),
                item_id=str(item_id),
                request_id=str(request_id),
            )
            raise

        # Save item image
        from ..models.image import ItemImage
        item_image = ItemImage(
            item_id=item_id,
            content_type="item",
            item_type=request.parameters.item_type,
            rarity=request.parameters.rarity,
            generated_by=request.model.name,
            prompt=prompt,
            result_image=image_data,
            thumbnail=self.client.create_thumbnail(image_data),
            parameters=request.parameters.dict(),
            metadata={
                "request_id": str(request_id),
                "item_type": request.parameters.item_type,
                "rarity": request.parameters.rarity,
                "is_magical": request.parameters.is_magical,
            },
        )
        self.db.add(item_image)
        await self.db.commit()
        await self.db.refresh(item_image)

        # Create response
        result = GeneratedImage(
            image_data=image_data,
            image_id=item_image.id,
            metadata=ContentMetadata(
                request_id=request_id,
                source_service=request.model.name,
                model_used=request.model.name,
                prompt_used=prompt,
                settings_used=request.parameters.dict(),
            ),
            parameters_used=request.parameters.dict(),
        )

        # Publish event
        await self.message_hub.publish_event({
            "type": "item_image_generated",
            "image_id": str(item_image.id),
            "item_id": str(item_id),
            "item_type": request.parameters.item_type,
        })

        return result

    async def generate_image(
        self, request: TextToImageRequest, request_id: uuid.UUID
    ) -> GeneratedImage:
        """Generate image from text prompt."""
        # Check cache first
        cache_key = f"image_generation:{hash(request.model_dump_json())}"
        if cached := await self._check_cache(cache_key):
            self.logger.info(
                "using_cached_image",
                request_id=str(request_id),
                image_id=str(cached.image_id),
            )
            return cached

        # Generate image
        try:
            image_data = await self.client.generate_image(request)
        except Exception as e:
            self.logger.error(
                "image_generation_failed",
                error=str(e),
                request_id=str(request_id),
            )
            raise

        # Create metadata
        metadata = ContentMetadata(
            request_id=request_id,
            source_service=request.model.name,
            model_used=request.model.name,
            prompt_used=request.prompt,
            settings_used={
                "negative_prompt": request.parameters.negative_prompt,
                "style_preset": request.parameters.style_preset,
                "size": request.size.model_dump(),
                **request.model.model_dump(),
            },
        )

        # Save image
        image_id = await self._save_image(
            image_data,
            str(request.type),
            metadata,
            width=request.size.width,
            height=request.size.height,
        )

        # Create response
        result = GeneratedImage(
            image_data=image_data,
            image_id=image_id,
            metadata=metadata,
            parameters_used=metadata.settings_used,
        )

        # Cache result
        await self.set_in_cache(
            cache_key,
            result.model_dump(),
            ttl_seconds=self.settings.cache.image_ttl_seconds,
        )

        # Publish event
        event = ImageGeneratedEvent(
            request_id=request_id,
            image_type=request.type,
            image_id=image_id,
            status="completed",
            model_used=request.model.name,
            prompt=request.prompt,
            parameters=result.parameters_used,
        )
        await self.message_hub.publish_event(event)

        self.logger.info(
            "image_generated",
            request_id=str(request_id),
            image_id=str(image_id),
            image_type=request.type,
        )

        return result

    async def transform_image(
        self, request: ImageToImageRequest, request_id: uuid.UUID
    ) -> GeneratedImage:
        """Transform existing image."""
        # Transform image
        try:
            image_data = await self.client.transform_image(request)
        except Exception as e:
            self.logger.error(
                "image_transformation_failed",
                error=str(e),
                request_id=str(request_id),
            )
            raise

        # Create metadata
        metadata = ContentMetadata(
            request_id=request_id,
            source_service=request.model.name,
            model_used=request.model.name,
            prompt_used=request.prompt,
            settings_used={
                "negative_prompt": request.parameters.negative_prompt,
                "style_preset": request.parameters.style_preset,
                "strength": request.strength,
                **request.model.model_dump(),
            },
        )

        # Save image
        image_id = await self._save_image(
            image_data, str(request.type), metadata
        )

        # Create response
        result = GeneratedImage(
            image_data=image_data,
            image_id=image_id,
            metadata=metadata,
            parameters_used=metadata.settings_used,
        )

        self.logger.info(
            "image_transformed",
            request_id=str(request_id),
            image_id=str(image_id),
            image_type=request.type,
        )

        return result

    async def enhance_image(
        self, request: ImageEnhancementRequest, request_id: uuid.UUID
    ) -> GeneratedImage:
        """Apply enhancements to image."""
        try:
            image_data = await self.client.enhance_image(request)
        except Exception as e:
            self.logger.error(
                "image_enhancement_failed",
                error=str(e),
                request_id=str(request_id),
            )
            raise

        # Create metadata
        metadata = ContentMetadata(
            request_id=request_id,
            source_service="getimg_ai",
            model_used="enhancement",
            prompt_used=str(request.enhancements),
            settings_used=request.parameters.model_dump(),
        )

        # Save image
        image_id = await self._save_image(
            image_data, "enhanced", metadata
        )

        # Create response
        result = GeneratedImage(
            image_data=image_data,
            image_id=image_id,
            metadata=metadata,
            parameters_used=metadata.settings_used,
        )

        self.logger.info(
            "image_enhanced",
            request_id=str(request_id),
            image_id=str(image_id),
            enhancements=request.enhancements,
        )

        return result
