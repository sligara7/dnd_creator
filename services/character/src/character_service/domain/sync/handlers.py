"""Message handlers for state synchronization."""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from character_service.core.exceptions import CharacterNotFoundError
from character_service.domain.sync.exceptions import (
    SyncError,
    SyncMessageError,
    SyncStateError,
)
from character_service.domain.sync.models import (
    FieldSyncMode,
    StateChange,
    SyncDirection,
    SyncMessage,
    SyncState,
)
from character_service.domain.sync.service import SynchronizationService
from character_service.domain.sync.utils import with_retry
from character_service.infrastructure.messaging.handlers import MessageHandler
from character_service.infrastructure.messaging.hub_client import MessageHubClient

logger = logging.getLogger(__name__)


class CampaignStateHandler(MessageHandler):
    """Handler for campaign state update messages."""

    def __init__(
        self,
        sync_service: SynchronizationService,
        message_hub: MessageHubClient,
        topic: str = "campaign.state.update",
    ) -> None:
        """Initialize handler.

        Args:
            sync_service: Synchronization service
            message_hub: Message hub client
            topic: Message topic
        """
        super().__init__(topic)
        self._sync_service = sync_service
        self._message_hub = message_hub

    @with_retry()
    async def handle(self, message: Dict[str, Any]) -> None:
        """Handle campaign state update message.

        Args:
            message: Campaign state update message

        Format:
            {
                "message_id": str,
                "campaign_id": str,
                "character_ids": [str],
                "state_data": {
                    "field_path": str,
                    "value": Any,
                    "sync_mode": str,
                },
                "version": int,
                "timestamp": str,
                "metadata": Dict,
            }
        """
        try:
            # Convert message to sync format
            sync_message = SyncMessage(
                message_id=UUID(message["message_id"]),
                character_id=UUID(message["character_id"]),
                campaign_id=UUID(message["campaign_id"]),
                character_version=0,  # Will be set by sync service
                campaign_version=message["version"],
                changes=[
                    StateChange(
                        character_id=UUID(message["character_id"]),
                        campaign_id=UUID(message["campaign_id"]),
                        field_path=data["field_path"],
                        new_value=data["value"],
                        old_value=None,  # Campaign doesn't know our old value
                        timestamp=datetime.fromisoformat(message["timestamp"]),
                        source="campaign",
                        sync_mode=FieldSyncMode(data.get("sync_mode", "full")),
                    )
                    for data in message["state_data"]
                ],
                timestamp=datetime.fromisoformat(message["timestamp"]),
                metadata=message.get("metadata", {}),
            )

            # Process message
            await self._sync_service.handle_campaign_message(sync_message)

            # Acknowledge processing
            await self._message_hub.publish(
                "campaign.state.ack",
                {
                    "message_id": str(message["message_id"]),
                    "character_id": str(message["character_id"]),
                    "campaign_id": str(message["campaign_id"]),
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(
                "Error handling campaign state update: %s",
                str(e),
                exc_info=True,
            )
            # Send error notification
            await self._message_hub.publish(
                "campaign.state.error",
                {
                    "message_id": str(message["message_id"]),
                    "character_id": str(message["character_id"]),
                    "campaign_id": str(message["campaign_id"]),
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            raise


class CharacterStateHandler(MessageHandler):
    """Handler for character state change messages."""

    def __init__(
        self,
        sync_service: SynchronizationService,
        message_hub: MessageHubClient,
        topic: str = "character.state.change",
    ) -> None:
        """Initialize handler.

        Args:
            sync_service: Synchronization service
            message_hub: Message hub client
            topic: Message topic
        """
        super().__init__(topic)
        self._sync_service = sync_service
        self._message_hub = message_hub

    @with_retry()
    async def handle(self, message: Dict[str, Any]) -> None:
        """Handle character state change message.

        Args:
            message: Character state change message

        Format:
            {
                "message_id": str,
                "character_id": str,
                "changes": [
                    {
                        "field_path": str,
                        "old_value": Any,
                        "new_value": Any,
                        "sync_mode": str,
                    }
                ],
                "timestamp": str,
                "metadata": Dict,
            }
        """
        try:
            # Convert to state changes
            changes = [
                StateChange(
                    character_id=UUID(message["character_id"]),
                    campaign_id=None,  # Not yet known
                    field_path=data["field_path"],
                    old_value=data["old_value"],
                    new_value=data["new_value"],
                    timestamp=datetime.fromisoformat(message["timestamp"]),
                    source="character",
                    sync_mode=FieldSyncMode(data.get("sync_mode", "full")),
                )
                for data in message["changes"]
            ]

            # Push changes to sync service
            await self._sync_service.push_changes(
                UUID(message["character_id"]),
                changes,
            )

        except Exception as e:
            logger.error(
                "Error handling character state change: %s",
                str(e),
                exc_info=True,
            )
            raise


class SyncControlHandler(MessageHandler):
    """Handler for sync control messages."""

    def __init__(
        self,
        sync_service: SynchronizationService,
        message_hub: MessageHubClient,
        topic: str = "character.sync.control",
    ) -> None:
        """Initialize handler.

        Args:
            sync_service: Synchronization service
            message_hub: Message hub client
            topic: Message topic
        """
        super().__init__(topic)
        self._sync_service = sync_service
        self._message_hub = message_hub

    @with_retry()
    async def handle(self, message: Dict[str, Any]) -> None:
        """Handle sync control message.

        Args:
            message: Sync control message

        Format:
            {
                "message_id": str,
                "character_id": str,
                "campaign_id": str,
                "command": str,  # subscribe, unsubscribe
                "fields": [str],  # For subscribe
                "sync_mode": str,  # For subscribe
                "timestamp": str,
                "metadata": Dict,
            }
        """
        try:
            command = message["command"]
            character_id = UUID(message["character_id"])
            campaign_id = UUID(message["campaign_id"])

            if command == "subscribe":
                # Handle subscription
                await self._sync_service.subscribe_to_campaign(
                    character_id=character_id,
                    campaign_id=campaign_id,
                    fields=message.get("fields"),
                    sync_mode=SyncDirection(message.get("sync_mode", "bidirectional")),
                )
                status = "subscribed"

            elif command == "unsubscribe":
                # Handle unsubscription
                await self._sync_service.unsubscribe_from_campaign(
                    character_id=character_id,
                    campaign_id=campaign_id,
                )
                status = "unsubscribed"

            else:
                raise ValueError(f"Unknown command: {command}")

            # Send status update
            await self._message_hub.publish(
                "character.sync.status",
                {
                    "message_id": str(message["message_id"]),
                    "character_id": str(character_id),
                    "campaign_id": str(campaign_id),
                    "status": status,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(
                "Error handling sync control: %s",
                str(e),
                exc_info=True,
            )
            # Send error notification
            await self._message_hub.publish(
                "character.sync.error",
                {
                    "message_id": str(message["message_id"]),
                    "character_id": str(message["character_id"]),
                    "campaign_id": str(message["campaign_id"]),
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            raise


class VersionQueryHandler(MessageHandler):
    """Handler for version query messages."""

    def __init__(
        self,
        sync_service: SynchronizationService,
        message_hub: MessageHubClient,
        topic: str = "character.version.query",
    ) -> None:
        """Initialize handler.

        Args:
            sync_service: Synchronization service
            message_hub: Message hub client
            topic: Message topic
        """
        super().__init__(topic)
        self._sync_service = sync_service
        self._message_hub = message_hub

    @with_retry()
    async def handle(self, message: Dict[str, Any]) -> None:
        """Handle version query message.

        Args:
            message: Version query message

        Format:
            {
                "message_id": str,
                "character_id": str,
                "campaign_id": str,
                "timestamp": str,
            }
        """
        try:
            # Get version info from sync metadata
            metadata = await self._sync_service._metadata_repo.get(
                UUID(message["character_id"]),
                UUID(message["campaign_id"]),
            )

            # Send version info
            await self._message_hub.publish(
                "character.version.info",
                {
                    "message_id": str(message["message_id"]),
                    "character_id": str(message["character_id"]),
                    "campaign_id": str(message["campaign_id"]),
                    "character_version": metadata.character_version if metadata else 0,
                    "campaign_version": metadata.campaign_version if metadata else 0,
                    "last_sync": metadata.last_sync.isoformat() if metadata else None,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(
                "Error handling version query: %s",
                str(e),
                exc_info=True,
            )
            raise
