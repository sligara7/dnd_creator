"""Health check tests."""

from fastapi.testclient import TestClient

def test_health_check(test_client: TestClient):
    """Test health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "services" in data
    assert all(k in data["services"] for k in ["prometheus", "storage", "message_hub"])