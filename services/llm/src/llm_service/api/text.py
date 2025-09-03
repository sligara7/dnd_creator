from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from llm_service.core.cache import AsyncCacheService, RedisCache
from llm_service.core.database import get_db
from llm_service.core.decorators import cached_response
from llm_service.core.settings import get_settings
from llm_service.schemas.text import (
    TextGenerationRequest,
    TextGenerationResponse,
)
from llm_service.services.openai import OpenAIClient
from llm_service.services.text import TextGenerationService


router = APIRouter(prefix="/text")


@router.post("/character", response_model=TextGenerationResponse)
@cached_response(prefix="character_content", ttl_seconds=3600)
async def generate_character_content(
    request: Request,
    req: TextGenerationRequest,
    db: AsyncSession = Depends(get_db),
) -> TextGenerationResponse:
    """Generate character-related content."""
    settings = get_settings()
    request_id = request.state.request_id

    # Set up services
    openai = OpenAIClient(settings)
    cache = request.app.state.redis
    message_hub = request.app.state.message_hub
    service = TextGenerationService(settings, openai, db, message_hub, cache_client=cache)

    # Generate text
    result = await service.generate_text(req, request_id)

    # Set response headers for token tracking
    request.state.response_headers = {
        "X-Model-Used": result.metadata.model_used,
        "X-Prompt-Tokens": str(result.metadata.settings_used.get("prompt_tokens", 0)),
        "X-Completion-Tokens": str(result.metadata.settings_used.get("completion_tokens", 0)),
    }

    return TextGenerationResponse(result=result)
