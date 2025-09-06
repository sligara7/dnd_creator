"""Message registry for sync handlers."""
import logging
from typing import Dict, List

from character_service.domain.sync.handlers import (
    CampaignStateHandler,
    CharacterStateHandler,
    SyncControlHandler,
    VersionQueryHandler,
)
from character_service.domain.sync.service import SynchronizationService
from character_service.infrastructure.messaging.handlers import MessageHandler
from character_service.infrastructure.messaging.hub_client import MessageHubClient
from character_service.infrastructure.messaging.registry import HandlerRegistry

logger = logging.getLogger(__name__)


def register_sync_handlers(
    sync_service: SynchronizationService,
    message_hub: MessageHubClient,
    registry: HandlerRegistry,
) -> None:
    """Register state sync message handlers.

    Args:
        sync_service: Synchronization service
        message_hub: Message hub client
        registry: Handler registry
    """
    # Create handlers
    handlers = [
        CampaignStateHandler(sync_service, message_hub),
        CharacterStateHandler(sync_service, message_hub),
        SyncControlHandler(sync_service, message_hub),
        VersionQueryHandler(sync_service, message_hub),
    ]

    # Register handlers
    for handler in handlers:
        registry.register(handler)
