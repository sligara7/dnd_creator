"""Campaign content generation API endpoints."""
from fastapi import APIRouter, Depends

from llm_service.core.exceptions import ContentGenerationError
from llm_service.schemas.campaign import (
    StoryRequest,
    StoryContent,
    NPCRequest,
    NPCContent,
    LocationRequest,
    LocationContent,
)
from llm_service.services.campaign import CampaignContentService

router = APIRouter(prefix="/campaign", tags=["campaign"])


@router.post("/story", response_model=StoryContent)
async def generate_story(
    request: StoryRequest,
    campaign_service: CampaignContentService = Depends(),
) -> StoryContent:
    """Generate campaign story content.

    Args:
        request: Story generation request
        campaign_service: Campaign content service

    Returns:
        Generated story content

    Raises:
        ContentGenerationError: If story generation fails
    """
    try:
        return await campaign_service.generate_story(request)
    except Exception as e:
        raise ContentGenerationError(
            message=f"Story generation failed: {str(e)}",
            details={"element_type": request.element_type},
        ) from e


@router.post("/npc", response_model=NPCContent)
async def generate_npc(
    request: NPCRequest,
    campaign_service: CampaignContentService = Depends(),
) -> NPCContent:
    """Generate campaign NPC content.

    Args:
        request: NPC generation request
        campaign_service: Campaign content service

    Returns:
        Generated NPC content

    Raises:
        ContentGenerationError: If NPC generation fails
    """
    try:
        return await campaign_service.generate_npc(request)
    except Exception as e:
        raise ContentGenerationError(
            message=f"NPC generation failed: {str(e)}",
            details={"role": request.role},
        ) from e


@router.post("/location", response_model=LocationContent)
async def generate_location(
    request: LocationRequest,
    campaign_service: CampaignContentService = Depends(),
) -> LocationContent:
    """Generate campaign location content.

    Args:
        request: Location generation request
        campaign_service: Campaign content service

    Returns:
        Generated location content

    Raises:
        ContentGenerationError: If location generation fails
    """
    try:
        return await campaign_service.generate_location(request)
    except Exception as e:
        raise ContentGenerationError(
            message=f"Location generation failed: {str(e)}",
            details={"location_type": request.location_type},
        ) from e
