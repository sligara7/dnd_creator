"""Dependency injection container."""
from typing import AsyncGenerator

from rodi import Container

from character_service.config import get_settings
from character_service.domain.messages import MessagePublisher, RabbitMQPublisher
from character_service.storage.storage_adapter import (
    StorageAdapter,
    MessageBasedStorageAdapter
)
from character_service.repositories.character_storage_repository import CharacterStorageRepository
from character_service.repositories.experience_repository import ExperienceEntryRepository
from character_service.repositories.inventory_repository import InventoryRepository
from character_service.repositories.journal_repository import (
    JournalEntryRepository,
    NPCRelationshipRepository,
    QuestRepository,
)
from character_service.repositories.version_repository import VersionRepository
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

    # Message publisher
    container.add_singleton(
        MessagePublisher,
        lambda: RabbitMQPublisher()
    )

    # Storage adapter
    container.add_singleton(
        StorageAdapter,
        lambda c: MessageBasedStorageAdapter(c.resolve(MessagePublisher))
    )

    # Repositories
    container.add_scoped(
        CharacterStorageRepository,
        lambda c: CharacterStorageRepository(c.resolve(StorageAdapter))
    )
    container.add_scoped(
        InventoryRepository,
        lambda c: InventoryRepository(c.resolve(StorageAdapter))
    )
    container.add_scoped(
        JournalEntryRepository,
        lambda c: JournalEntryRepository(c.resolve(StorageAdapter))
    )
    container.add_scoped(
        ExperienceEntryRepository,
        lambda c: ExperienceEntryRepository(c.resolve(StorageAdapter))
    )
    container.add_scoped(
        QuestRepository,
        lambda c: QuestRepository(c.resolve(StorageAdapter))
    )
    container.add_scoped(
        NPCRelationshipRepository,
        lambda c: NPCRelationshipRepository(c.resolve(StorageAdapter))
    )
    container.add_scoped(
        VersionRepository,
        lambda c: VersionRepository(c.resolve(StorageAdapter))
    )

    # Services
    container.add_scoped(
        ThemeService,
        lambda c: ThemeService(c.resolve(StorageAdapter))
    )
    container.add_scoped(
        CharacterServiceImpl,
        lambda c: CharacterServiceImpl(c.resolve(CharacterStorageRepository))
    )
    container.add_scoped(
        InventoryServiceImpl,
        lambda c: InventoryServiceImpl(
            c.resolve(InventoryRepository),
            c.resolve(CharacterStorageRepository),
        )
    )
    container.add_scoped(
        JournalServiceImpl,
        lambda c: JournalServiceImpl(
            c.resolve(JournalEntryRepository),
            c.resolve(CharacterStorageRepository),
            c.resolve(ExperienceEntryRepository),
            c.resolve(QuestRepository),
            c.resolve(NPCRelationshipRepository),
        )
    )

    # State version management
    container.add_scoped(
        VersionManager,
        lambda c: VersionManager(
            char_repository=c.resolve(CharacterStorageRepository),
            version_repository=c.resolve(VersionRepository)
        )
    )

    # Event-related services
    container.add_scoped(
        EventImpactService,
        lambda c: EventImpactService(
            storage=c.resolve(StorageAdapter),
            version_manager=c.resolve(VersionManager)
        )
    )
    container.add_scoped(
        ProgressTrackingService,
        lambda c: ProgressTrackingService(
            storage=c.resolve(StorageAdapter),
            version_manager=c.resolve(VersionManager)
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
