"""API dependency configuration."""
from fastapi import Depends
from rodi import Container
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.services.interfaces import CharacterService, InventoryService, JournalService
from character_service.services.character import CharacterServiceImpl
from character_service.services.inventory import InventoryServiceImpl
from character_service.services.journal import JournalServiceImpl
from character_service.services.theme_service import ThemeService
from character_service.domain.event import EventImpactService
from character_service.domain.event_publisher import EventPublicationManager
from character_service.domain.progress import ProgressTrackingService
from character_service.domain.state_publisher import StatePublisher
from character_service.infrastructure.messaging.hub_client import MessageHubClient
from character_service.api.v2.lifecycle import event_publisher


def get_container() -> Container:
    """Get dependency injection container."""
    # This would typically be initialized on app startup and stored in state
    from character_service.di.container import setup_di
    return setup_di()


async def get_db_session(container: Container = Depends(get_container)) -> AsyncSession:
    """Get database session."""
    session = container.resolve_provider("get_db_session")
    async for s in session():
        yield s


async def get_character_service(
    container: Container = Depends(get_container),
) -> CharacterService:
    """Get character service."""
    return container.resolve(CharacterServiceImpl)


async def get_inventory_service(
    container: Container = Depends(get_container),
) -> InventoryService:
    """Get inventory service."""
    return container.resolve(InventoryServiceImpl)


async def get_journal_service(
    container: Container = Depends(get_container),
) -> JournalService:
    """Get journal service."""
    return container.resolve(JournalServiceImpl)


async def get_theme_service(
    container: Container = Depends(get_container),
) -> ThemeService:
    """Get theme service."""
    return container.resolve(ThemeService)


async def get_event_publisher() -> EventPublicationManager:
    """Get event publication manager instance."""
    if event_publisher is None:
        raise RuntimeError("Event publisher not initialized")
    return event_publisher


async def get_event_service(
    container: Container = Depends(get_container),
) -> EventImpactService:
    """Get event impact service."""
    return container.resolve(EventImpactService)


async def get_progress_service(
    container: Container = Depends(get_container),
) -> ProgressTrackingService:
    """Get progress tracking service."""
    return container.resolve(ProgressTrackingService)
