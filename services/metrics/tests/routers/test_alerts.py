"""Tests for alert management endpoints."""

import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from metrics_service.main import app
from metrics_service.core.messages import Message, MessageHeader, MessageType

@pytest.fixture
def mock_message_client():
    """Create mock message client."""
    client = AsyncMock()
    return client

@pytest.fixture
def test_client(mock_message_client):
    """Create test client with mocked message client."""
    app.dependency_overrides = {
        "metrics_service.dependencies.get_message_client": lambda: mock_message_client
    }
    return TestClient(app)

def test_create_alert(test_client, mock_message_client):
    """Test alert creation endpoint."""
    # Setup mock response
    mock_message_client.create_alert_rule.return_value = Message(
        header=MessageHeader(
            message_id="test",
            message_type=MessageType.STORAGE_RESPONSE,
            correlation_id="test",
            source_service="storage"
        ),
        payload={"status": "success", "data": {"id": "test-alert"}}
    )
    
    # Test endpoint
    response = test_client.post(
        "/api/v2/alerts/",
        json={
            "name": "test_alert",
            "expression": "up == 1",
            "duration": "5m",
            "severity": "critical"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["payload"]["status"] == "success"
    
    # Verify client call
    mock_message_client.create_alert_rule.assert_called_once()

def test_get_alert(test_client, mock_message_client):
    """Test alert retrieval endpoint."""
    mock_message_client.get_alert_rule.return_value = Message(
        header=MessageHeader(
            message_id="test",
            message_type=MessageType.STORAGE_RESPONSE,
            correlation_id="test",
            source_service="storage"
        ),
        payload={
            "status": "success",
            "data": {
                "id": "test-alert",
                "name": "test_alert",
                "expression": "up == 1"
            }
        }
    )
    
    response = test_client.get("/api/v2/alerts/test-alert")
    assert response.status_code == 200
    data = response.json()
    assert data["payload"]["data"]["id"] == "test-alert"