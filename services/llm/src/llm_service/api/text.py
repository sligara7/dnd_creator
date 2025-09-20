"""Text generation API routes."""
from typing import Dict, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from pydantic import UUID4

from ..core.exceptions import ContentGenerationError
from ..models.text import (
    TextGenerationType,
    TextGenerationRequest,
    TextGenerationResponse,
)
from ..services.character_content import CharacterContentService
from ..core.message_hub import MessageHubClient


router = APIRouter(prefix="/api/v2/text", tags=["text"])


async def get_character_content_service() -> CharacterContentService:
    """Get character content service instance."""
    from ..core.dependencies import get_settings, get_openai_provider
    settings = get_settings()
    openai_provider = get_openai_provider()
    return CharacterContentService(settings, openai_provider)


async def get_message_hub() -> MessageHubClient:
    """Get Message Hub client instance."""
    from ..core.dependencies import get_settings
    settings = get_settings()
    return MessageHubClient(settings)


@router.post(
    "/character",
    response_model=TextGenerationResponse,
    description="Generate character-related text content"
)
async def generate_character_text(
    request: TextGenerationRequest,
    background_tasks: BackgroundTasks,
    character_service: CharacterContentService = Depends(get_character_content_service),
    message_hub: MessageHubClient = Depends(get_message_hub),
) -> TextGenerationResponse:
    """Generate text content for characters."""
    try:
        # Generate unique request ID
        request_id = str(uuid4())

        # Extract character data
        character_data = {
            "race": request.parameters.character_race,
            "class": request.parameters.character_class,
            "level": request.parameters.character_level,
            "alignment": request.parameters.alignment,
            "background": request.parameters.background,
        }

        # Generate content based on type
        if request.type == TextGenerationType.PERSONALITY:
            traits = await character_service.generate_personality_traits(
                character_data=character_data,
                theme_context=request.theme.dict() if request.theme else None,
            )
            content = traits.json()
            
        elif request.type == TextGenerationType.BACKSTORY:
            narrative = await character_service.generate_background_narrative(
                character_data=character_data,
                theme_context=request.theme.dict() if request.theme else None,
            )
            content = narrative.json()
            
        else:
            raise ContentGenerationError(f"Unsupported content type: {request.type}")

        # Build response
        response = TextGenerationResponse(
            request_id=request_id,
            type=request.type,
            content=content,
            model_used=request.model.name if request.model else "gpt-4-turbo",
            metadata={
                "has_theme": str(bool(request.theme)).lower(),
                "character_class": request.parameters.character_class,
                "character_race": request.parameters.character_race,
                "character_level": str(request.parameters.character_level),
            }
        )

        # Publish event asynchronously
        background_tasks.add_task(
            message_hub.publish_event,
            event_type="text_generated",
            data={
                "request_id": request_id,
                "type": request.type,
                "status": "completed",
                "metadata": response.metadata,
            },
            routing_key=f"llm.text.character.{request.type}.completed",
        )

        return response

    except ContentGenerationError as e:
        # Publish error event asynchronously
        background_tasks.add_task(
            message_hub.publish_event,
            event_type="text_generation_failed",
            data={
                "error": str(e),
                "type": request.type,
                "metadata": {
                    "character_class": request.parameters.character_class,
                    "character_race": request.parameters.character_race,
                },
            },
            routing_key="llm.text.character.failed",
        )
        raise
