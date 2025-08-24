"""
Message Hub Client

Shared client for interacting with the message hub service.
"""

import uuid
import httpx
import structlog
from typing import Dict, Any, Optional
from enum import Enum

logger = structlog.get_logger()

class ServiceType(str, Enum):
    """Available service types."""
    CHARACTER = "character"
    CAMPAIGN = "campaign"
    IMAGE = "image"
    LLM = "llm"
    GATEWAY = "gateway"

class MessageType(str, Enum):
    """Types of messages that can be sent between services."""
    # Character Service Messages
    CREATE_CHARACTER = "create_character"
    UPDATE_CHARACTER = "update_character"
    GET_CHARACTER = "get_character"
    
    # Campaign Service Messages
    CREATE_CAMPAIGN = "create_campaign"
    UPDATE_CAMPAIGN = "update_campaign"
    ADD_CHARACTER = "add_character"
    
    # Image Service Messages
    GENERATE_PORTRAIT = "generate_portrait"
    GENERATE_MAP = "generate_map"
    
    # LLM Service Messages
    GENERATE_TEXT = "generate_text"
    GENERATE_IMAGE = "generate_image"

class MessageHubClient:
    """Client for interacting with the message hub."""
    
    def __init__(self,
                 service_type: ServiceType,
                 hub_url: str = "http://message_hub:8200",
                 timeout: int = 30):
        """Initialize the message hub client."""
        self.service_type = service_type
        self.hub_url = hub_url.rstrip("/")
        self.http_client = httpx.AsyncClient(timeout=timeout)
        
        # Service capabilities for registration
        self.capabilities = []
    
    async def register_service(self,
                             url: str,
                             health_check: str = "/health",
                             version: str = "1.0.0"):
        """Register this service with the message hub."""
        try:
            response = await self.http_client.post(
                f"{self.hub_url}/v1/services/register",
                json={
                    "name": self.service_type,
                    "url": url,
                    "health_check": health_check,
                    "version": version,
                    "capabilities": self.capabilities
                }
            )
            response.raise_for_status()
            logger.info("service_registered",
                       service=self.service_type,
                       url=url)
            return response.json()
            
        except Exception as e:
            logger.error("service_registration_failed",
                        service=self.service_type,
                        error=str(e))
            raise
    
    async def send_message(self,
                          destination: ServiceType,
                          message_type: MessageType,
                          payload: Dict[str, Any],
                          correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a message to another service through the hub."""
        try:
            message = {
                "source": self.service_type,
                "destination": destination,
                "message_type": message_type,
                "correlation_id": correlation_id or str(uuid.uuid4()),
                "payload": payload,
            }
            
            response = await self.http_client.post(
                f"{self.hub_url}/v1/messages/send",
                json=message
            )
            response.raise_for_status()
            
            result = response.json()
            if result["status"] == "error":
                raise ValueError(result["error"])
                
            return result["data"]
            
        except Exception as e:
            logger.error("message_send_failed",
                        destination=destination,
                        message_type=message_type,
                        error=str(e))
            raise
    
    async def generate_text(self,
                          prompt: str,
                          context: Dict[str, Any] = None,
                          model: str = None) -> str:
        """Generate text using the LLM service."""
        result = await self.send_message(
            destination=ServiceType.LLM,
            message_type=MessageType.GENERATE_TEXT,
            payload={
                "prompt": prompt,
                "context": context or {},
                "model": model
            }
        )
        return result["content"]
    
    async def generate_image(self,
                           prompt: str,
                           style: Dict[str, Any] = None) -> str:
        """Generate an image using the LLM service."""
        result = await self.send_message(
            destination=ServiceType.LLM,
            message_type=MessageType.GENERATE_IMAGE,
            payload={
                "prompt": prompt,
                "style": style or {}
            }
        )
        return result["content"]  # URL or base64 image
    
    def add_capability(self, message_type: MessageType):
        """Add a message type that this service can handle."""
        if message_type not in self.capabilities:
            self.capabilities.append(message_type)
    
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
