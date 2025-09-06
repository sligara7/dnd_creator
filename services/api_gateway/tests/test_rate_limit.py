import time
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from api_gateway.middleware.rate_limit import RateLimitMiddleware

@pytest.fixture
def test_app():
    """Create test FastAPI app."""
    app = FastAPI()
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=2,
        burst_size=1
    )
    
    @app.get("/test")
    def test_endpoint():
        return {"message": "success"}
        
    return app

@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)

def test_rate_limit_allowed(client):
    """Test requests within rate limit."""
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-RateLimit-Remaining" in response.headers
    
    # Second request should also succeed
    response = client.get("/test")
    assert response.status_code == 200

def test_rate_limit_exceeded(client):
    """Test requests exceeding rate limit."""
    # First two requests succeed
    response = client.get("/test")
    assert response.status_code == 200
    
    response = client.get("/test")
    assert response.status_code == 200
    
    # Third request exceeds limit
    response = client.get("/test")
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]

def test_rate_limit_reset(client):
    """Test rate limit reset after window."""
    # Use up the rate limit
    response = client.get("/test")
    assert response.status_code == 200
    
    response = client.get("/test")
    assert response.status_code == 200
    
    # Wait for rate limit window to pass
    time.sleep(60)
    
    # Should be able to make requests again
    response = client.get("/test")
    assert response.status_code == 200

def test_rate_limit_headers(client):
    """Test rate limit headers."""
    response = client.get("/test")
    headers = response.headers
    
    assert "X-RateLimit-Limit" in headers
    assert "X-RateLimit-Remaining" in headers
    assert "X-RateLimit-Reset" in headers
    
    limit = int(headers["X-RateLimit-Limit"])
    remaining = int(headers["X-RateLimit-Remaining"])
    reset = float(headers["X-RateLimit-Reset"])
    
    assert limit == 2
    assert remaining == 1
    assert reset > time.time()
