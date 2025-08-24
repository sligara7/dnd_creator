"""
Service Clients

Shared service clients for external service communication.
"""

from typing import Optional
from shared.message_hub_client import MessageHubClient, ServiceType

_message_hub_client: Optional[MessageHubClient] = None

def get_message_hub_client() -> MessageHubClient:
    """Get or create the message hub client."""
    global _message_hub_client
    
    if _message_hub_client is None:
        _message_hub_client = MessageHubClient(
            service_type=ServiceType.CHARACTER,
            hub_url="http://message_hub:8200"
        )
        
        # Register message types this service can handle
        _message_hub_client.add_capability(MessageType.CREATE_CHARACTER)
        _message_hub_client.add_capability(MessageType.UPDATE_CHARACTER)
        _message_hub_client.add_capability(MessageType.GET_CHARACTER)
    
    return _message_hub_client

async def close_clients():
    """Close all service clients."""
    global _message_hub_client
    
    if _message_hub_client:
        await _message_hub_client.close()
        _message_hub_client = None
