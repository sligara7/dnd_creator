"""Tests for metrics middleware."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from metrics_service.core.middleware import MetricsMiddleware
from metrics_service.core.metrics import registry

@pytest.fixture
def app():
    """Create test FastAPI application."""
    app = FastAPI()
    app.add_middleware(MetricsMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")

    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)

def test_successful_request_metrics(client):
    """Test metrics collection for successful requests."""
    response = client.get("/test")
    assert response.status_code == 200

    # Get metrics
    metrics_response = client.get("/metrics")
    metrics_text = metrics_response.text

    # Check counter metrics
    assert 'http_requests_total{method="GET",path="/test",status="200"} 1.0' in metrics_text

    # Check histogram metrics
    assert 'http_request_duration_seconds_bucket{method="GET",path="/test",status="200"' in metrics_text

    # Active requests should be 0 after request completion
    assert 'active_requests{method="GET",path="/test"} 0.0' in metrics_text

def test_error_request_metrics(client):
    """Test metrics collection for failed requests."""
    with pytest.raises(ValueError):
        client.get("/error")

    # Get metrics
    metrics_response = client.get("/metrics")
    metrics_text = metrics_response.text

    # Check error metrics
    assert 'http_requests_total{method="GET",path="/error",status="500"} 1.0' in metrics_text

def test_metrics_endpoint_excluded(client):
    """Test that /metrics endpoint itself is not measured."""
    client.get("/metrics")
    
    # Get metrics again
    metrics_response = client.get("/metrics")
    metrics_text = metrics_response.text

    # Verify /metrics endpoint is not measured
    assert 'path="/metrics"' not in metrics_text