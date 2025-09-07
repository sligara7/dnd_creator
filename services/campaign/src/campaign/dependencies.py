"""Dependencies for campaign routers."""

from typing import AsyncGenerator, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.db import get_db
from .services.story import StoryService
from .services.theme import ThemeService
from .services.theme_integration import ThemeIntegrationService
from .services.world_effect import WorldEffectService
from ..services.campaign_factory import CampaignFactory
from ..services.llm_service import LLMService


async def get_story_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[StoryService, None]:
    """Get story service instance."""
    service = StoryService(db)
    yield service


async def get_theme_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ThemeService, None]:
    """Get theme service instance."""
    service = ThemeService(db)
    yield service


async def get_llm_service() -> AsyncGenerator[LLMService, None]:
    """Get LLM service instance."""
    # TODO: Add actual LLM service configuration
    service = LLMService()
    yield service


async def get_theme_integration_service(
    db: AsyncSession = Depends(get_db),
    theme_service: ThemeService = Depends(get_theme_service),
    llm_service: LLMService = Depends(get_llm_service),
) -> AsyncGenerator[ThemeIntegrationService, None]:
    """Get theme integration service instance."""
    service = ThemeIntegrationService(db, theme_service, llm_service)
    yield service


async def get_world_effect_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[WorldEffectService, None]:
    """Get world effect service instance."""
    service = WorldEffectService(db)
    yield service


async def get_campaign_factory(
    db: AsyncSession = Depends(get_db),
    theme_service: ThemeService = Depends(get_theme_service),
    llm_service: LLMService = Depends(get_llm_service),
) -> AsyncGenerator[CampaignFactory, None]:
    """Get campaign factory instance."""
    # TODO: Add additional dependencies as needed
    factory = CampaignFactory(
        db=db,
        ai_client=llm_service,
        message_hub_client=None,  # TODO: Add message hub client
        theme_service=theme_service,
        version_service=None,  # TODO: Add version service
        map_service=None,  # TODO: Add map service
    )
    yield factory
