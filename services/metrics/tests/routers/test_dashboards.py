"""Tests for dashboard management endpoints."""

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

def test_create_dashboard(test_client, mock_message_client):
    """Test dashboard creation endpoint."""
    mock_message_client.create_dashboard.return_value = Message(
        header=MessageHeader(
            message_id="test",
            message_type=MessageType.STORAGE_RESPONSE,
            correlation_id="test",
            source_service="storage"
        ),
        payload={"status": "success", "data": {"id": "test-dash"}}
    )
    
    response = test_client.post(
        "/api/v2/dashboards/",
        json={
            "title": "Test Dashboard",
            "panels": [
                {
                    "title": "Test Panel",
                    "type": "graph",
                    "targets": [{"expr": "up"}]
                }
            ]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["payload"]["status"] == "success"
    
    mock_message_client.create_dashboard.assert_called_once()

def test_get_dashboard(test_client, mock_message_client):
    """Test dashboard retrieval endpoint."""
    mock_message_client.get_dashboard.return_value = Message(
        header=MessageHeader(
            message_id="test",
            message_type=MessageType.STORAGE_RESPONSE,
            correlation_id="test",
            source_service="storage"
        ),
        payload={
            "status": "success",
            "data": {
                "id": "test-dash",
                "title": "Test Dashboard",
                "panels": []
            }
        }
    )
    
    response = test_client.get("/api/v2/dashboards/test-dash")
    assert response.status_code == 200
    data = response.json()
    assert data["payload"]["data"]["id"] == "test-dash"