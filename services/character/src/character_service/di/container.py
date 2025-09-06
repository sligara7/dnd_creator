"""Dependency injection container."""
from typing import AsyncGenerator

from rodi import Container, Services
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.config import get_settings
from character_service.infrastructure.database import create_engine, create_session_factory
from character_service.infrastructure.repositories.character import CharacterRepository
from character_service.infrastructure.repositories.event import CampaignEventRepository, EventImpactRepository
from character_service.infrastructure.repositories.inventory import InventoryRepository
from character_service.infrastructure.repositories.journal import (
    ExperienceEntryRepository,
    JournalEntryRepository,
    NPCRelationshipRepository,
    QuestRepository,
)
from character_service.domain.event import EventImpactService
from character_service.domain.event_publisher import EventPublicationManager
from character_service.domain.progress import ProgressTrackingService
from character_service.domain.state_publisher import StatePublisher
from character_service.domain.state_version import VersionManager
from character_service.domain.subscription import SubscriptionManager
from character_service.services.character import CharacterServiceImpl
from character_service.services.inventory import InventoryServiceImpl
from character_service.services.journal import JournalServiceImpl
from character_service.services.theme_service import ThemeService


def setup_di() -> Container:
    """Configure dependency injection container."""
    container = Container()

    # Configuration
    settings = get_settings()
    container.add_singleton(lambda: settings)

    # Database engine and session factory
    container.add_singleton(lambda c: create_engine(c.resolve(get_settings)))
    container.add_singleton(
        lambda c: create_session_factory(c.resolve(create_engine))
    )

    # Database session scoped to request
    async def get_db_session(c: Container) -> AsyncGenerator[AsyncSession, None]:
        """Get database session for request scope."""
        session_factory = c.resolve(create_session_factory)
        async with session_factory() as session:
            yield session

    container.add_scoped(get_db_session)

    # Repositories
    container.add_scoped(
        CharacterRepository,
        lambda c: CharacterRepository(c.resolve(get_db_session)),
    )
    container.add_scoped(
        InventoryRepository,
        lambda c: InventoryRepository(c.resolve(get_db_session)),
    )
    container.add_scoped(
        JournalEntryRepository,
        lambda c: JournalEntryRepository(c.resolve(get_db_session)),
    )
    container.add_scoped(
        ExperienceEntryRepository,
        lambda c: ExperienceEntryRepository(c.resolve(get_db_session)),
    )
    container.add_scoped(
        QuestRepository,
        lambda c: QuestRepository(c.resolve(get_db_session)),
    )
    container.add_scoped(
        NPCRelationshipRepository,
        lambda c: NPCRelationshipRepository(c.resolve(get_db_session)),
    )
    container.add_scoped(
        CampaignEventRepository,
        lambda c: CampaignEventRepository(c.resolve(get_db_session)),
    )
    container.add_scoped(
        EventImpactRepository,
        lambda c: EventImpactRepository(c.resolve(get_db_session)),
    )

    # Services
    container.add_scoped(
        ThemeService,
        lambda c: ThemeService(c.resolve(get_db_session))
    )
    container.add_scoped(
        CharacterServiceImpl,
        lambda c: CharacterServiceImpl(c.resolve(CharacterRepository))
    )
    container.add_scoped(
        InventoryServiceImpl,
        lambda c: InventoryServiceImpl(
            c.resolve(InventoryRepository),
            c.resolve(CharacterRepository),
        )
    )
    container.add_scoped(
        JournalServiceImpl,
        lambda c: JournalServiceImpl(
            c.resolve(JournalEntryRepository),
            c.resolve(CharacterRepository),
            c.resolve(ExperienceEntryRepository),
            c.resolve(QuestRepository),
            c.resolve(NPCRelationshipRepository),
        )
    )

    # State version management
    container.add_scoped(
        VersionManager,
        lambda c: VersionManager(
            char_repository=c.resolve(CharacterRepository),
        )
    )

    # Event-related services
    container.add_scoped(
        EventImpactService,
        lambda c: EventImpactService(
            c.resolve(CampaignEventRepository),
            c.resolve(EventImpactRepository),
            c.resolve(CharacterRepository),
            c.resolve(VersionManager),
        )
    )
    container.add_scoped(
        ProgressTrackingService,
        lambda c: ProgressTrackingService(
            c.resolve(CharacterRepository),
            c.resolve(CampaignEventRepository),
            c.resolve(EventImpactRepository),
            c.resolve(VersionManager),
        )
    )

    return container


def setup_test_di() -> Container:
    """Configure dependency injection container for testing."""
    container = setup_di()

    # Override settings for testing
    test_settings = get_settings()
    test_settings.TESTING = True
    container.add_singleton(lambda: test_settings)

    return container
