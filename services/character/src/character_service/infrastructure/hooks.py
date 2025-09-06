"""Event hooks for automatic event publication."""
from typing import Optional

from character_service.domain.event import EventImpactService
from character_service.domain.event_publisher import EventPublicationManager
from character_service.domain.models import Character, CharacterProgress
from character_service.domain.progress import ProgressTrackingService


async def publish_event_impact(
    event_service: EventImpactService,
    event_publisher: EventPublicationManager,
    *args,
    **kwargs,
) -> None:
    """Hook to publish events when impact changes occur."""
    if kwargs.get("event") and kwargs.get("impacts"):
        await event_publisher.publish_event(kwargs["event"])


async def publish_character_update(
    event_publisher: EventPublicationManager,
    character: Character,
    previous_data: Optional[dict] = None,
    *args,
    **kwargs,
) -> None:
    """Hook to publish character state updates."""
    await event_publisher.publish_character_update(
        character,
        previous_data=previous_data,
    )


async def publish_progress_update(
    progress_service: ProgressTrackingService,
    event_publisher: EventPublicationManager,
    *args,
    **kwargs,
) -> None:
    """Hook to publish progress updates."""
    if kwargs.get("progress"):
        update_type = kwargs.get("update_type", "other")
        await event_publisher.publish_progress_update(
            kwargs["progress"],
            update_type,
        )
