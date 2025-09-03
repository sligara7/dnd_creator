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
