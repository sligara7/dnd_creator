import pytest
from fastapi import HTTPException

from api_gateway.middleware.auth import JWTBearer, APIKeyAuth

pytestmark = pytest.mark.asyncio

async def test_jwt_bearer_valid_token(mock_auth_service):
    """Test JWT validation with valid token."""
    mock_auth_service.return_value.status_code = 200
    
    auth = JWTBearer("http://auth-service")
    request = type("Request", (), {"headers": {"Authorization": "Bearer valid_token"}})()
    
    result = await auth(request)
    assert result == "Bearer valid_token"

async def test_jwt_bearer_invalid_token(mock_auth_service):
    """Test JWT validation with invalid token."""
    mock_auth_service.return_value.status_code = 403
    
    auth = JWTBearer("http://auth-service")
    request = type("Request", (), {"headers": {"Authorization": "Bearer invalid_token"}})()
    
    with pytest.raises(HTTPException) as exc:
        await auth(request)
    assert exc.value.status_code == 403

async def test_api_key_auth_valid_key(mock_auth_service):
    """Test API key validation with valid key."""
    mock_auth_service.return_value.status_code = 200
    
    auth = APIKeyAuth("http://auth-service")
    request = type("Request", (), {"headers": {"X-API-Key": "valid_key"}})()
    
    result = await auth(request)
    assert result is True

async def test_api_key_auth_invalid_key(mock_auth_service):
    """Test API key validation with invalid key."""
    mock_auth_service.return_value.status_code = 403
    
    auth = APIKeyAuth("http://auth-service")
    request = type("Request", (), {"headers": {"X-API-Key": "invalid_key"}})()
    
    with pytest.raises(HTTPException) as exc:
        await auth(request)
    assert exc.value.status_code == 403

async def test_api_key_auth_missing_key():
    """Test API key validation with missing key."""
    auth = APIKeyAuth("http://auth-service")
    request = type("Request", (), {"headers": {}})()
    
    with pytest.raises(HTTPException) as exc:
        await auth(request)
    assert exc.value.status_code == 403
