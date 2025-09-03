from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from llm_service.core.cache import RedisCache
from llm_service.core.database import get_db
from llm_service.core.decorators import cached_response
from llm_service.core.settings import get_settings
from llm_service.schemas.image import (
    ImageEnhancementRequest,
    ImageGenerationResponse,
    ImageToImageRequest,
    TextToImageRequest,
)
from llm_service.services.getimg_ai import GetImgAIClient
from llm_service.services.image import ImageGenerationService


router = APIRouter(prefix="/image")


@router.post("/generate", response_model=ImageGenerationResponse)
@cached_response(prefix="text_to_image", ttl_seconds=3600)
async def generate_image(
    request: Request,
    req: TextToImageRequest,
    db: AsyncSession = Depends(get_db),
) -> ImageGenerationResponse:
    """Generate image from text prompt."""
    settings = get_settings()
    request_id = request.state.request_id

    # Set up services
    client = GetImgAIClient(settings)
    cache = request.app.state.redis
    message_hub = request.app.state.message_hub
    service = ImageGenerationService(settings, client, db, message_hub, cache_client=cache)

    # Generate image
    result = await service.generate_image(req, request_id)

    return ImageGenerationResponse(result=result)


@router.post("/transform", response_model=ImageGenerationResponse)
async def transform_image(
    request: Request,
    req: ImageToImageRequest,
    db: AsyncSession = Depends(get_db),
) -> ImageGenerationResponse:
    """Transform existing image."""
    settings = get_settings()
    request_id = request.state.request_id

    # Set up services
    client = GetImgAIClient(settings)
    cache = request.app.state.redis
    message_hub = request.app.state.message_hub
    service = ImageGenerationService(settings, client, db, message_hub, cache_client=cache)

    # Transform image
    result = await service.transform_image(req, request_id)

    return ImageGenerationResponse(result=result)


@router.post("/enhance", response_model=ImageGenerationResponse)
async def enhance_image(
    request: Request,
    req: ImageEnhancementRequest,
    db: AsyncSession = Depends(get_db),
) -> ImageGenerationResponse:
    """Apply enhancements to image."""
    settings = get_settings()
    request_id = request.state.request_id

    # Set up services
    client = GetImgAIClient(settings)
    cache = request.app.state.redis
    message_hub = request.app.state.message_hub
    service = ImageGenerationService(settings, client, db, message_hub, cache_client=cache)

    # Enhance image
    result = await service.enhance_image(req, request_id)

    return ImageGenerationResponse(result=result)
