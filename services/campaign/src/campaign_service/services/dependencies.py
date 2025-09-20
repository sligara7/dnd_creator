"""Service dependencies for FastAPI."""
from typing import AsyncGenerator, Any
from fastapi import Depends
from campaign_service.core.logging import get_logger
from campaign_service.core.messaging.client import MessageHubClient
from campaign_service.models.storage_campaign import Campaign, Chapter
from campaign_service.storage.storage_port import StoragePort
from campaign_service.services.campaign_factory import CampaignFactoryService
from campaign_service.services.chapter import ChapterService
from campaign_service.services.story_management import StoryManagementService
from campaign_service.services.theme import ThemeService
from campaign_service.services.campaign_factory import CampaignFactoryService
from campaign_service.services.chapter import ChapterService
from campaign_service.services.story_management import StoryManagementService
from campaign_service.services.theme import ThemeService

logger = get_logger(__name__)


# Storage ports
async def get_campaign_storage(
    message_hub_client: Any = Depends(get_message_hub),  # type: ignore
) -> AsyncGenerator[StoragePort[Campaign], None]:
    """Get campaign repository.

    Args:
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).

    Yields:
        AsyncGenerator[CampaignRepository, None]: Campaign repository
    """
    storage = StoragePort[Campaign](
        message_hub=message_hub_client,
        model_class=Campaign,
        database="campaign_db",
    )
    try:
        yield storage
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


async def get_chapter_storage(
    message_hub_client: Any = Depends(get_message_hub),  # type: ignore
) -> AsyncGenerator[StoragePort[Chapter], None]:
    """Get chapter repository.

    Args:
        db (AsyncSession, optional): Database session. Defaults to Depends(get_db).

    Yields:
        AsyncGenerator[ChapterRepository, None]: Chapter repository
    """
    storage = StoragePort[Chapter](
        message_hub=message_hub_client,
        model_class=Chapter,
        database="campaign_db",
    )
    try:
        yield storage
    finally:
        pass


async def get_theme_service(
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
        message_hub_client=message_hub_client,
    )
    try:
        yield service
    finally:
        pass


async def get_chapter_service(
    chapter_storage: StoragePort[Chapter] = Depends(get_chapter_storage),
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
        chapter_storage=chapter_storage,
        theme_service=theme_service,
        message_hub_client=message_hub_client,
    )
    try:
        yield service
    finally:
        pass


async def get_campaign_factory(
    campaign_storage: StoragePort[Campaign] = Depends(get_campaign_storage),
    chapter_storage: StoragePort[Chapter] = Depends(get_chapter_storage),
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
        campaign_storage=campaign_storage,
        chapter_storage=chapter_storage,
        theme_service=theme_service,
        message_hub_client=message_hub_client,
    )
    try:
        yield service
    finally:
        pass
