"""
Backend Service Integration

Provides communication layer between campaign service and backend service.
Handles character/item creation, retrieval, and management via HTTP calls.
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

class BackendServiceConfig:
    """Configuration for backend service communication."""
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.timeout = 30.0
        self.max_retries = 3

class BackendContentRequest(BaseModel):
    """Request model for backend content creation."""
    creation_type: str  # character, monster, npc, weapon, armor, spell, other_item
    prompt: str
    user_preferences: Optional[Dict[str, Any]] = None
    extra_fields: Optional[Dict[str, Any]] = None
    save_to_database: bool = True

class BackendIntegrationService:
    """Service for communicating with the backend character/item creation service."""
    
    def __init__(self, config: BackendServiceConfig = None):
        self.config = config or BackendServiceConfig()
        self.client = httpx.AsyncClient(timeout=self.config.timeout)
    
    async def create_content(self, request: BackendContentRequest) -> Dict[str, Any]:
        """Create content using the backend factory endpoint with graceful fallback."""
        try:
            response = await self.client.post(
                f"{self.config.base_url}/api/v2/factory/create",
                json=request.dict()
            )
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "result": result,
                "source": "backend_service"
            }
            
        except httpx.RequestError as e:
            logger.warning(f"Backend service request failed, service likely unavailable: {e}")
            return {
                "success": False,
                "error": f"Backend service unavailable: {e}",
                "source": "error",
                "fallback_recommended": True
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"Backend service error {e.response.status_code}: {e.response.text}")
            return {
                "success": False,
                "error": f"Backend service error: {e.response.status_code}",
                "source": "error",
                "fallback_recommended": True
            }
    
    async def get_character(self, character_id: str) -> Dict[str, Any]:
        """Get character details from backend service with graceful fallback."""
        try:
            response = await self.client.get(
                f"{self.config.base_url}/api/v2/characters/{character_id}"
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            logger.warning(f"Backend character retrieval failed: {e}")
            return None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.warning(f"Backend service error {e.response.status_code}: {e.response.text}")
            return None
    
    async def list_characters(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List characters from backend service."""
        try:
            response = await self.client.get(
                f"{self.config.base_url}/api/v2/characters",
                params={"limit": limit, "offset": offset}
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Backend character listing failed: {e}")
            raise Exception(f"Backend service unavailable: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Backend service error {e.response.status_code}: {e.response.text}")
            raise Exception(f"Backend service error: {e.response.status_code}")
    
    async def update_character(self, character_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update character in backend service."""
        try:
            response = await self.client.put(
                f"{self.config.base_url}/api/v2/characters/{character_id}",
                json=updates
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Backend character update failed: {e}")
            raise Exception(f"Backend service unavailable: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Backend service error {e.response.status_code}: {e.response.text}")
            raise Exception(f"Backend service error: {e.response.status_code}")
    
    async def delete_character(self, character_id: str) -> bool:
        """Delete character from backend service."""
        try:
            response = await self.client.delete(
                f"{self.config.base_url}/api/v2/characters/{character_id}"
            )
            response.raise_for_status()
            return True
            
        except httpx.RequestError as e:
            logger.error(f"Backend character deletion failed: {e}")
            raise Exception(f"Backend service unavailable: {e}")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            logger.error(f"Backend service error {e.response.status_code}: {e.response.text}")
            raise Exception(f"Backend service error: {e.response.status_code}")
    
    # =========================
    # ITEM MANAGEMENT METHODS
    # =========================
    
    async def create_item(self, creation_prompt: str, item_type: str = "other_item", 
                         campaign_context: str = None, user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create an item using the backend factory endpoint."""
        # Enhance prompt with campaign context if provided
        enhanced_prompt = creation_prompt
        if campaign_context:
            enhanced_prompt = f"Campaign Context: {campaign_context}\n\nItem Request: {creation_prompt}"
        
        request = BackendContentRequest(
            creation_type=item_type,
            prompt=enhanced_prompt,
            user_preferences=user_preferences or {},
            save_to_database=True
        )
        
        return await self.create_content(request)
    
    async def get_item_by_id(self, item_id: str) -> Dict[str, Any]:
        """
        Get item details by ID. Since backend doesn't have item CRUD endpoints,
        this would need to be implemented or we track items differently.
        For now, returns None to indicate items are only created, not stored.
        """
        # TODO: Backend service needs item retrieval endpoints
        # For now, items are created via factory but not stored with IDs
        logger.warning(f"Item retrieval by ID not supported by backend service: {item_id}")
        return None
    
    async def list_items(self, item_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List items from backend service. Since backend doesn't have item endpoints,
        this returns empty list. Items are tracked by campaign service locally.
        """
        # TODO: Backend service needs item listing endpoints
        logger.warning("Item listing not supported by backend service")
        return []
    
    async def update_item(self, item_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update item in backend service. Since backend doesn't have item endpoints,
        this is not supported. Items are managed by campaign service.
        """
        # TODO: Backend service needs item CRUD endpoints
        logger.warning(f"Item updates not supported by backend service: {item_id}")
        raise Exception("Item updates not supported by backend service")
    
    async def delete_item(self, item_id: str) -> bool:
        """
        Delete item from backend service. Since backend doesn't have item endpoints,
        this is not supported. Items are managed by campaign service.
        """
        # TODO: Backend service needs item CRUD endpoints
        logger.warning(f"Item deletion not supported by backend service: {item_id}")
        return False

    async def health_check(self) -> bool:
        """Check if backend service is available."""
        try:
            response = await self.client.get(
                f"{self.config.base_url}/health",
                timeout=5.0  # Quick health check
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Backend service health check failed: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Factory functions for dependency injection
def create_backend_integration_service(base_url: str = None) -> BackendIntegrationService:
    """Create backend integration service with optional custom URL."""
    config = BackendServiceConfig(base_url) if base_url else BackendServiceConfig()
    return BackendIntegrationService(config)

async def get_backend_service() -> BackendIntegrationService:
    """Dependency injection function for FastAPI."""
    return create_backend_integration_service()
