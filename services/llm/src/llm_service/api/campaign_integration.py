"""API routes for Campaign service integration."""
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from ..core.exceptions import EventHandlingError, IntegrationError
from ..models.theme import ThemeContext
from ..services.campaign_events import CampaignEventHandler
from ..services.campaign_integration import (
    CampaignContent,
    CampaignContentType,
    CampaignEvent,
    CampaignService
)
from ..services.generation import GenerationPipeline


router = APIRouter(prefix="/api/v2/campaign", tags=["campaign_integration"])


async def get_campaign_service() -> CampaignService:
    """Get Campaign service instance."""
    from ..core.dependencies import get_settings
    settings = get_settings()
    return CampaignService(settings)


async def get_generation_pipeline() -> GenerationPipeline:
    """Get generation pipeline instance."""
    from ..core.dependencies import get_settings, get_rate_limiter
    settings = get_settings()
    rate_limiter = get_rate_limiter()
    return GenerationPipeline(settings, rate_limiter)


@router.post(
    "/{campaign_id}/generate/{content_type}",
    description="Generate content for a campaign"
)
async def generate_campaign_content(
    campaign_id: UUID,
    content_type: CampaignContentType,
    theme_context: Optional[ThemeContext] = None,
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """Generate content for a campaign."""
    try:
        # Get existing campaign content
        campaign_content = await campaign_service.get_campaign_content(
            campaign_id,
            content_type
        )

        # Generate content
        result = await generation_pipeline.generate_content(
            content_type=content_type,
            theme_context=theme_context or campaign_content.theme_context,
            existing_content=campaign_content.existing_content
        )

        # Update campaign content
        await campaign_service.update_campaign_content(
            campaign_id=campaign_id,
            content_type=content_type,
            content=result.content,
            metadata={
                "model": result.metadata.model_name,
                "tokens": result.metadata.total_tokens,
                "theme": theme_context.name if theme_context else None
            }
        )

        # Notify about content generation asynchronously
        if background_tasks:
            background_tasks.add_task(
                campaign_service.notify_content_generation,
                campaign_id=campaign_id,
                content_type=content_type,
                theme_context=theme_context
            )

        return {"content": result.content}

    except (IntegrationError, EventHandlingError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{campaign_id}/theme/validate",
    description="Validate theme compatibility for a campaign"
)
async def validate_campaign_theme(
    campaign_id: UUID,
    theme_context: ThemeContext,
    campaign_service: CampaignService = Depends(get_campaign_service)
) -> Dict[str, bool]:
    """Validate theme compatibility for a campaign."""
    try:
        is_valid = await campaign_service.validate_theme(
            campaign_id,
            theme_context
        )
        return {"is_valid": is_valid}

    except IntegrationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{campaign_id}/plot",
    description="Create a plot element for a campaign"
)
async def create_campaign_plot(
    campaign_id: UUID,
    title: str,
    description: str,
    element_type: str,
    theme_context: Optional[ThemeContext] = None,
    campaign_service: CampaignService = Depends(get_campaign_service)
) -> Dict[str, Any]:
    """Create a plot element for a campaign."""
    try:
        result = await campaign_service.create_plot_element(
            campaign_id=campaign_id,
            title=title,
            description=description,
            element_type=element_type,
            theme_context=theme_context
        )
        return result

    except IntegrationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{campaign_id}/location",
    description="Create a location for a campaign"
)
async def create_campaign_location(
    campaign_id: UUID,
    name: str,
    description: str,
    location_type: str,
    theme_context: Optional[ThemeContext] = None,
    campaign_service: CampaignService = Depends(get_campaign_service)
) -> Dict[str, Any]:
    """Create a location for a campaign."""
    try:
        result = await campaign_service.create_location(
            campaign_id=campaign_id,
            name=name,
            description=description,
            location_type=location_type,
            theme_context=theme_context
        )
        return result

    except IntegrationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{campaign_id}/npc",
    description="Create an NPC for a campaign"
)
async def create_campaign_npc(
    campaign_id: UUID,
    name: str,
    description: str,
    role: str,
    theme_context: Optional[ThemeContext] = None,
    campaign_service: CampaignService = Depends(get_campaign_service)
) -> Dict[str, Any]:
    """Create an NPC for a campaign."""
    try:
        result = await campaign_service.create_npc(
            campaign_id=campaign_id,
            name=name,
            description=description,
            role=role,
            theme_context=theme_context
        )
        return result

    except IntegrationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{campaign_id}/events",
    description="Handle Campaign service events"
)
async def handle_campaign_events(
    campaign_id: UUID,
    event: CampaignEvent,
    campaign_service: CampaignService = Depends(get_campaign_service),
    generation_pipeline: GenerationPipeline = Depends(get_generation_pipeline),
    background_tasks: BackgroundTasks = None
) -> Dict[str, str]:
    """Handle events from Campaign service."""
    try:
        event_handler = CampaignEventHandler(
            campaign_service,
            generation_pipeline,
            background_tasks
        )

        await event_handler.handle_campaign_event(event)

        return {"status": "Event handled"}

    except (IntegrationError, EventHandlingError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
