"""Message handlers for subscription management."""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from character_service.domain.sync.exceptions import SyncSubscriptionError
from character_service.domain.sync.models import SyncDirection
from character_service.domain.sync.subscription import SubscriptionService
from character_service.domain.sync.utils import with_retry
from character_service.infrastructure.messaging.handlers import MessageHandler
from character_service.infrastructure.messaging.hub_client import MessageHubClient

logger = logging.getLogger(__name__)


class SubscriptionRequestHandler(MessageHandler):
    """Handler for subscription request messages."""

    def __init__(
        self,
        subscription_service: SubscriptionService,
        message_hub: MessageHubClient,
        topic: str = "campaign.subscription.request",
    ) -> None:
        """Initialize handler.

        Args:
            subscription_service: Subscription service
            message_hub: Message hub client
            topic: Message topic
        """
        super().__init__(topic)
        self._subscription_service = subscription_service
        self._message_hub = message_hub

    @with_retry()
    async def handle(self, message: Dict[str, Any]) -> None:
        """Handle subscription request message.

        Args:
            message: Subscription request message

        Format:
            {
                "message_id": str,
                "character_id": str,
                "campaign_id": str,
                "fields": [str],
                "sync_mode": str,
                "timestamp": str,
            }
        """
        try:
            # Create subscription
            subscription = await self._subscription_service.create_subscription(
                character_id=UUID(message["character_id"]),
                campaign_id=UUID(message["campaign_id"]),
                fields=message.get("fields"),
                sync_mode=SyncDirection(message.get("sync_mode", "bidirectional")),
            )

            # Send response
            await self._message_hub.publish(
                "campaign.subscription.response",
                {
                    "message_id": str(message["message_id"]),
                    "character_id": str(subscription.character_id),
                    "campaign_id": str(subscription.campaign_id),
                    "status": "accepted",
                    "fields": subscription.fields,
                    "sync_mode": subscription.sync_mode.value,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            # Send error response
            await self._message_hub.publish(
                "campaign.subscription.response",
                {
                    "message_id": str(message["message_id"]),
                    "character_id": str(message["character_id"]),
                    "campaign_id": str(message["campaign_id"]),
                    "status": "rejected",
                    "reason": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            logger.error(
                "Error handling subscription request: %s",
                str(e),
                exc_info=True,
            )
            raise


class SubscriptionResponseHandler(MessageHandler):
    """Handler for subscription response messages."""

    def __init__(
        self,
        subscription_service: SubscriptionService,
        message_hub: MessageHubClient,
        topic: str = "campaign.subscription.response",
    ) -> None:
        """Initialize handler.

        Args:
            subscription_service: Subscription service
            message_hub: Message hub client
            topic: Message topic
        """
        super().__init__(topic)
        self._subscription_service = subscription_service
        self._message_hub = message_hub

    @with_retry()
    async def handle(self, message: Dict[str, Any]) -> None:
        """Handle subscription response message.

        Args:
            message: Subscription response message

        Format:
            {
                "message_id": str,
                "character_id": str,
                "campaign_id": str,
                "status": str,  # accepted/rejected
                "reason": str,  # Optional rejection reason
                "timestamp": str,
            }
        """
        await self._subscription_service.handle_subscription_response(message)


class SubscriptionHeartbeatHandler(MessageHandler):
    """Handler for subscription heartbeat messages."""

    def __init__(
        self,
        subscription_service: SubscriptionService,
        message_hub: MessageHubClient,
        topic: str = "campaign.subscription.heartbeat",
    ) -> None:
        """Initialize handler.

        Args:
            subscription_service: Subscription service
            message_hub: Message hub client
            topic: Message topic
        """
        super().__init__(topic)
        self._subscription_service = subscription_service
        self._message_hub = message_hub

    @with_retry()
    async def handle(self, message: Dict[str, Any]) -> None:
        """Handle subscription heartbeat message.

        Args:
            message: Subscription heartbeat message

        Format:
            {
                "message_id": str,
                "character_id": str,
                "campaign_id": str,
                "timestamp": str,
            }
        """
        try:
            # Update subscription state
            await self._subscription_service.update_subscription(
                character_id=UUID(message["character_id"]),
                campaign_id=UUID(message["campaign_id"]),
                active=True,  # Keep subscription active
            )

        except Exception as e:
            logger.error(
                "Error handling subscription heartbeat: %s",
                str(e),
                exc_info=True,
            )
            raise


class SubscriptionErrorHandler(MessageHandler):
    """Handler for subscription error messages."""

    def __init__(
        self,
        subscription_service: SubscriptionService,
        message_hub: MessageHubClient,
        topic: str = "campaign.subscription.error",
    ) -> None:
        """Initialize handler.

        Args:
            subscription_service: Subscription service
            message_hub: Message hub client
            topic: Message topic
        """
        super().__init__(topic)
        self._subscription_service = subscription_service
        self._message_hub = message_hub

    @with_retry()
    async def handle(self, message: Dict[str, Any]) -> None:
        """Handle subscription error message.

        Args:
            message: Subscription error message

        Format:
            {
                "message_id": str,
                "character_id": str,
                "campaign_id": str,
                "error": str,
                "timestamp": str,
            }
        """
        await self._subscription_service.handle_subscription_error(message)
