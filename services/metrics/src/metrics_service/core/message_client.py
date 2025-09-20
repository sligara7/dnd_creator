"""Message hub client implementation."""

import json
import uuid
from typing import Any, Dict, Optional
from datetime import datetime

import aio_pika
from aio_pika import Message as PikaMessage
from aio_pika.patterns import RPC

from metrics_service.config import ServiceConfig
from metrics_service.core.messages import Message, MessageHeader, MessageType

class MessageClient:
    """Client for interacting with the message hub."""

    def __init__(self, config: ServiceConfig):
        """Initialize message client."""
        self.config = config
        self._connection: Optional[aio_pika.Connection] = None
        self._channel: Optional[aio_pika.Channel] = None
        self._rpc: Optional[RPC] = None

    async def connect(self) -> None:
        """Establish connection to message hub."""
        self._connection = await aio_pika.connect_robust(self.config.message_hub_url)
        self._channel = await self._connection.channel()
        self._rpc = await RPC.create(self._channel)

    async def close(self) -> None:
        """Close message hub connection."""
        if self._connection:
            await self._connection.close()

    async def send_message(self, message_type: MessageType, payload: Dict[str, Any]) -> Message:
        """Send a message through the message hub."""
        if not self._rpc:
            raise RuntimeError("Message client not connected")

        message = Message(
            header=MessageHeader(
                message_id=str(uuid.uuid4()),
                message_type=message_type,
                correlation_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                source_service="metrics"
            ),
            payload=payload
        )

        # Convert to JSON for transport
        message_data = json.dumps(message.model_dump()).encode()

        # Send through RPC and await response
        response = await self._rpc.call(
            "metrics.storage",  # Route to storage service
            PikaMessage(message_data)
        )

        # Parse and return response
        response_data = json.loads(response.body.decode())
        return Message.model_validate(response_data)

    # Storage Service Operations
    async def create_alert_rule(self, alert_rule: Dict[str, Any]) -> Message:
        """Create alert rule in storage."""
        return await self.send_message(
            MessageType.STORAGE_CREATE,
            {"collection": "alert_rules", "document": alert_rule}
        )

    async def get_alert_rule(self, alert_id: str) -> Message:
        """Get alert rule from storage."""
        return await self.send_message(
            MessageType.STORAGE_READ,
            {"collection": "alert_rules", "id": alert_id}
        )

    async def update_alert_rule(self, alert_id: str, alert_rule: Dict[str, Any]) -> Message:
        """Update alert rule in storage."""
        return await self.send_message(
            MessageType.STORAGE_UPDATE,
            {
                "collection": "alert_rules",
                "id": alert_id,
                "document": alert_rule
            }
        )

    async def delete_alert_rule(self, alert_id: str) -> Message:
        """Delete alert rule from storage."""
        return await self.send_message(
            MessageType.STORAGE_DELETE,
            {"collection": "alert_rules", "id": alert_id}
        )

    async def create_dashboard(self, dashboard: Dict[str, Any]) -> Message:
        """Create dashboard in storage."""
        return await self.send_message(
            MessageType.STORAGE_CREATE,
            {"collection": "dashboards", "document": dashboard}
        )

    async def get_dashboard(self, dashboard_id: str) -> Message:
        """Get dashboard from storage."""
        return await self.send_message(
            MessageType.STORAGE_READ,
            {"collection": "dashboards", "id": dashboard_id}
        )

    async def update_dashboard(self, dashboard_id: str, dashboard: Dict[str, Any]) -> Message:
        """Update dashboard in storage."""
        return await self.send_message(
            MessageType.STORAGE_UPDATE,
            {
                "collection": "dashboards",
                "id": dashboard_id,
                "document": dashboard
            }
        )

    async def delete_dashboard(self, dashboard_id: str) -> Message:
        """Delete dashboard from storage."""
        return await self.send_message(
            MessageType.STORAGE_DELETE,
            {"collection": "dashboards", "id": dashboard_id}
        )