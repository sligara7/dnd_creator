"""Tests for message client functionality."""

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from metrics_service.config import ServiceConfig
from metrics_service.core.message_client import MessageClient
from metrics_service.core.messages import MessageType, Message, MessageHeader

@pytest.fixture
def config():
    """Create test configuration."""
    return ServiceConfig(message_hub_url="amqp://guest:guest@localhost:5672/")

@pytest.fixture
async def message_client(config):
    """Create message client with mocked RPC."""
    client = MessageClient(config)
    
    # Mock RPC connection
    client._rpc = AsyncMock()
    client._rpc.call = AsyncMock()
    client._connection = AsyncMock()
    
    return client

async def test_send_message(message_client):
    """Test sending message through message hub."""
    # Prepare mocked response
    response_message = Message(
        header=MessageHeader(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.STORAGE_RESPONSE,
            correlation_id=str(uuid.uuid4()),
            source_service="storage"
        ),
        payload={"status": "success"}
    )
    
    mock_response = MagicMock()
    mock_response.body = response_message.model_dump_json().encode()
    message_client._rpc.call.return_value = mock_response
    
    # Test alert rule creation
    test_alert = {
        "name": "test_alert",
        "expression": "up == 1",
        "duration": "5m",
        "severity": "critical"
    }
    
    resp = await message_client.create_alert_rule(test_alert)
    assert resp.header.message_type == MessageType.STORAGE_RESPONSE
    
    # Verify RPC call
    message_client._rpc.call.assert_called_once()
    args = message_client._rpc.call.call_args
    assert args[0][0] == "metrics.storage"
    
    # Verify message format
    message_data = args[0][1].body.decode()
    assert "alert_rules" in message_data
    assert "test_alert" in message_data

async def test_connection_lifecycle(message_client):
    """Test connection management."""
    await message_client.close()
    message_client._connection.close.assert_called_once()