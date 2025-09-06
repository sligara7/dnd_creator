"""API routes for Character service integration."""
from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from ..core.exceptions import EventHandlingError, IntegrationError
from ..models.theme import ContentType, ThemeContext
from ..services.character import CharacterEventType, CharacterService
from ..services.events import EventHandler
from ..services.generation import GenerationPipeline

router = APIRouter(prefix="/api/v2/character", tags=["character"])


async def get_character_service() -> CharacterService:
    """Get Character service instance."""
    from ..core.dependencies import get_settings
    settings = get_settings()
    return CharacterService(settings)


async def get_generation_pipeline() -> GenerationPipeline:
    """Get generation pipeline instance."""
    from ..core.dependencies import get_settings, get_rate_limiter
    settings = get_settings()
    rate_limiter = get_rate_limiter()
    return GenerationPipeline(settings, rate_limiter)


@router.post(
    "/{character_id}/generate/{content_type}",
    description="Generate content for a character"
)
async def generate_character_content(
    character_id: UUID,
    content_type: ContentType,
    theme_context: Optional[ThemeContext] = None,
    character_service: CharacterService = Depends(get_character_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """Generate content for a character."""
    try:
        # Get existing character content
        character_content = await character_service.get_character_content(
            character_id,
            content_type
        )

        # Generate content
        result = await generation_pipeline.generate_content(
            content_type=content_type,
            theme_context=theme_context or character_content.theme_context,
            existing_content=character_content.existing_content
        )

        # Update character content
        await character_service.update_character_content(
            character_id=character_id,
            content_type=content_type,
            content=result.content
        )

        # Notify about content generation asynchronously
        if background_tasks:
            background_tasks.add_task(
                character_service.notify_content_generation,
                character_id=character_id,
                content_type=content_type,
                theme_context=theme_context
            )

        return {"content": result.content}

    except (IntegrationError, EventHandlingError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{character_id}/theme/validate",
    description="Validate theme compatibility for a character"
)
async def validate_character_theme(
    character_id: UUID,
    theme_context: ThemeContext,
    character_service: CharacterService = Depends(get_character_service)
) -> Dict[str, bool]:
    """Validate theme compatibility for a character."""
    try:
        is_valid = await character_service.validate_theme(
            character_id,
            theme_context
        )
        return {"is_valid": is_valid}

    except IntegrationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{character_id}/theme/transition",
    description="Handle theme transition for a character"
)
async def handle_theme_transition(
    character_id: UUID,
    theme_context: ThemeContext,
    character_service: CharacterService = Depends(get_character_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """Handle theme transition for a character."""
    try:
        event_handler = EventHandler(
            character_service,
            generation_pipeline,
            background_tasks
        )

        await event_handler.handle_character_event(
            event_type=CharacterEventType.THEME_TRANSITIONED,
            character_id=character_id,
            data={},
            theme_context=theme_context
        )

        return {"status": "Theme transition queued"}

    except (IntegrationError, EventHandlingError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{character_id}/events/handle",
    description="Handle Character service events"
)
async def handle_character_events(
    character_id: UUID,
    event_type: CharacterEventType,
    data: Dict[str, str],
    theme_context: Optional[ThemeContext] = None,
    character_service: CharacterService = Depends(get_character_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """Handle events from Character service."""
    try:
        event_handler = EventHandler(
            character_service,
            generation_pipeline,
            background_tasks
        )

        await event_handler.handle_character_event(
            event_type=event_type,
            character_id=character_id,
            data=data,
            theme_context=theme_context
        )

        return {"status": "Event handled"}

    except (IntegrationError, EventHandlingError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
