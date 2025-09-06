"""Service dependencies for FastAPI."""
from typing import AsyncGenerator, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.core.database import get_db
from campaign_service.core.logging import get_logger
from campaign_service.repositories.campaign import CampaignRepository, ChapterRepository
from campaign_service.repositories.story import (
    NPCRelationshipRepository,
    PlotChapterRepository,
    PlotRepository,
    StoryArcRepository,
)
from campaign_service.services.campaign_factory import CampaignFactoryService
from campaign_service.services.chapter import ChapterService
from campaign_service.services.story_management import StoryManagementService
from campaign_service.services.theme import ThemeService
    PlotRepository,
    StoryArcRepository,
)
from campaign_service.services.campaign_factory import CampaignFactoryService
from campaign_service.services.chapter import ChapterService
from campaign_service.services.story_management import StoryManagementService
from campaign_service.services.theme import ThemeService

logger = get_logger(__name__)


async def get_campaign_repo(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[CampaignRepository, None]:
    """Get campaign repository.

    Args:
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).

    Yields:
        AsyncGenerator[CampaignRepository, None]: Campaign repository
    """
    repo = CampaignRepository(db)
    try:
        yield repo
    finally:
        pass


async def get_story_management(
    db: AsyncSession = Depends(get_db),
    campaign_repo: CampaignRepository = Depends(get_campaign_repo),
    message_hub_client: Any = Depends(get_message_hub),  # type: ignore
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


async def get_chapter_repo(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ChapterRepository, None]:
    """Get chapter repository.

    Args:
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).

    Yields:
        AsyncGenerator[ChapterRepository, None]: Chapter repository
    """
    repo = ChapterRepository(db)
    try:
        yield repo
    finally:
        pass


async def get_theme_service(
    db: AsyncSession = Depends(get_db),
    message_hub_client: Any = Depends(get_message_hub),  # type: ignore
) -> AsyncGenerator[ThemeService, None]:
    """Get theme service.

    Args:
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).
        message_hub_client (Any, optional): Message hub client. Defaults to Depends(get_message_hub).
        llm_client (Any, optional): LLM client. Defaults to Depends(get_llm).

    Yields:
        AsyncGenerator[ThemeService, None]: Theme service
    """
    service = ThemeService(
        db=db,
        message_hub_client=message_hub_client,
    )
    try:
        yield service
    finally:
        pass


async def get_chapter_service(
    db: AsyncSession = Depends(get_db),
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    theme_service: ThemeService = Depends(get_theme_service),
    message_hub_client: Any = Depends(get_message_hub),  # type: ignore
) -> AsyncGenerator[ChapterService, None]:
    """Get chapter service.

    Args:
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).
        chapter_repo (ChapterRepository, optional): Chapter repository. Defaults to Depends(get_chapter_repo).
        theme_service (ThemeService, optional): Theme service. Defaults to Depends(get_theme_service).
        message_hub_client (Any, optional): Message hub client. Defaults to Depends(get_message_hub).
        llm_client (Any, optional): LLM client. Defaults to Depends(get_llm).

    Yields:
        AsyncGenerator[ChapterService, None]: Chapter service
    """
    service = ChapterService(
        db=db,
        chapter_repo=chapter_repo,
        theme_service=theme_service,
        message_hub_client=message_hub_client,
    )
    try:
        yield service
    finally:
        pass


async def get_campaign_factory(
    db: AsyncSession = Depends(get_db),
    campaign_repo: CampaignRepository = Depends(get_campaign_repo),
    chapter_repo: ChapterRepository = Depends(get_chapter_repo),
    chapter_service: ChapterService = Depends(get_chapter_service),
    theme_service: ThemeService = Depends(get_theme_service),
    message_hub_client: Any = Depends(get_message_hub),  # type: ignore
) -> AsyncGenerator[CampaignFactoryService, None]:
    """Get campaign factory service.

    Args:
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).
        campaign_repo (CampaignRepository, optional): Campaign repository. Defaults to Depends(get_campaign_repo).
        chapter_repo (ChapterRepository, optional): Chapter repository. Defaults to Depends(get_chapter_repo).
        chapter_service (ChapterService, optional): Chapter service. Defaults to Depends(get_chapter_service).
        theme_service (ThemeService, optional): Theme service. Defaults to Depends(get_theme_service).
        message_hub_client (Any, optional): Message hub client. Defaults to Depends(get_message_hub).
        llm_client (Any, optional): LLM client. Defaults to Depends(get_llm).

    Yields:
        AsyncGenerator[CampaignFactoryService, None]: Campaign factory service
    """
    service = CampaignFactoryService(
        db=db,
        campaign_repo=campaign_repo,
        chapter_repo=chapter_repo,
        theme_service=theme_service,
        message_hub_client=message_hub_client,
    )
    try:
        yield service
    finally:
        pass
