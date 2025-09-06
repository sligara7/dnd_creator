import os
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from api_gateway.main import app

@pytest.fixture
def test_client():
    """Get test client."""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Get async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_auth_service(mocker):
    """Mock auth service for testing."""
    return mocker.patch("api_gateway.middleware.auth.httpx.AsyncClient.post")

@pytest.fixture
def mock_message_hub(mocker):
    """Mock message hub for testing."""
    return mocker.patch("api_gateway.services.discovery.httpx.AsyncClient.post")
