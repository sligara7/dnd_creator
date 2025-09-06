"""Story service dependencies."""
from typing import Any, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.core.database import get_db
from campaign_service.core.logging import get_logger
from campaign_service.repositories.campaign import CampaignRepository
from campaign_service.repositories.story import (
    NPCRelationshipRepository,
    PlotChapterRepository,
    PlotRepository,
    StoryArcRepository,
)
from campaign_service.services.dependencies import (
    get_campaign_repo,
    get_message_hub,
)
from campaign_service.services.story_management import StoryManagementService

logger = get_logger(__name__)


async def get_story_management_service(
    db: AsyncSession = Depends(get_db),
    campaign_repo: CampaignRepository = Depends(get_campaign_repo),
    message_hub_client: Any = Depends(get_message_hub),
) -> AsyncGenerator[StoryManagementService, None]:
    """Get story management service.

    Args:
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).
        campaign_repo (CampaignRepository, optional): Campaign repository. Defaults to Depends(get_campaign_repo).
        message_hub_client (Any, optional): Message hub client. Defaults to Depends(get_message_hub).

    Yields:
        AsyncGenerator[StoryManagementService, None]: Story management service
    """
    service = StoryManagementService(
        db=db,
        campaign_repo=campaign_repo,
        plot_repo=PlotRepository(db),
        arc_repo=StoryArcRepository(db),
        plot_chapter_repo=PlotChapterRepository(db),
        npc_repo=NPCRelationshipRepository(db),
        message_hub_client=message_hub_client,
    )
    try:
        yield service
    finally:
        pass
