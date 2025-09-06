"""Application lifecycle management."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from character_service.config import get_settings
from character_service.domain.event import EventImpactService
from character_service.domain.event_publisher import EventPublicationManager, PublicationConfig
from character_service.domain.progress import ProgressTrackingService
from character_service.domain.state_publisher import StatePublisher
from character_service.domain.subscription import SubscriptionManager
from character_service.domain.version_manager import VersionManager
from character_service.infrastructure.messaging.hub_client import MessageHubClient, MessageHubConfig


settings = get_settings()
event_publisher: EventPublicationManager | None = None
subscription_manager: SubscriptionManager | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Setup Message Hub client
    hub_client = MessageHubClient(
        config=MessageHubConfig(),
        settings=settings,
    )
    await hub_client.connect()

    # Get container
    from character_service.di.container import setup_di
    container = setup_di()

    # Initialize state publisher
    state_publisher = StatePublisher(
        message_hub=hub_client,
        event_service=container.resolve(EventImpactService),
    )

    # Initialize event publisher
    global event_publisher
    event_publisher = EventPublicationManager(
        state_publisher=state_publisher,
        event_service=container.resolve(EventImpactService),
        config=PublicationConfig(),
    )
    await event_publisher.start()

    # Initialize and start subscription manager
    global subscription_manager
    subscription_manager = SubscriptionManager(
        message_hub=hub_client,
        state_publisher=state_publisher,
        event_service=container.resolve(EventImpactService),
        progress_service=container.resolve(ProgressTrackingService),
        version_manager=container.resolve(VersionManager),
    )
    await subscription_manager.start()

    yield

    # Cleanup
    await event_publisher.stop()
    # No explicit stop needed for subscription manager currently
    await hub_client.disconnect()
