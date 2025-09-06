from typing import Optional

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
import httpx

class JWTBearer(HTTPBearer):
    def __init__(self, auth_service_url: str):
        super(JWTBearer, self).__init__(auto_error=True)
        self.auth_service_url = auth_service_url

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if not credentials:
            raise HTTPException(
                status_code=403,
                detail="Invalid authentication credentials"
            )

        if not credentials.credentials:
            raise HTTPException(
                status_code=403,
                detail="Invalid authentication token"
            )

        try:
            # Forward token validation to Auth Service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.auth_service_url}/validate",
                    json={"token": credentials.credentials}
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=403,
                        detail="Invalid token or insufficient permissions"
                    )
                
                return credentials.credentials

        except JWTError:
            raise HTTPException(
                status_code=403,
                detail="Invalid token or expired token"
            )
        except Exception as e:
            raise HTTPException(
                status_code=403,
                detail=str(e)
            )

class APIKeyAuth:
    def __init__(self, auth_service_url: str):
        self.auth_service_url = auth_service_url

    async def validate_api_key(self, api_key: str) -> bool:
        """Validate API key with Auth Service."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.auth_service_url}/validate-api-key",
                    json={"api_key": api_key}
                )
                return response.status_code == 200
        except Exception:
            return False

    async def __call__(self, request: Request) -> bool:
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            raise HTTPException(
                status_code=403,
                detail="API key required"
            )

        is_valid = await self.validate_api_key(api_key)
        
        if not is_valid:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key"
            )

        return True
