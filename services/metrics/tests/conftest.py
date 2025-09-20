"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from metrics_service.main import app

@pytest.fixture
def test_client():
    """Create FastAPI test client."""
    return TestClient(app)