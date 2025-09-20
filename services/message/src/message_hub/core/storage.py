"""Storage Service Client.

Handles all interactions with the Storage Service for persistent data.
"""

import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from datetime import datetime

from .exceptions import MessageHubError
from .config import Settings

logger = logging.getLogger(__name__)

class StorageServiceClient:
    """Client for interacting with Storage Service."""
    
    def __init__(self, settings: Settings):
        """Initialize storage service client.
        
        Args:
            settings: Service configuration
        """
        self.settings = settings
        self.client = httpx.AsyncClient(
            base_url=settings.storage_service_url,
            timeout=settings.storage_service_timeout,
            headers={
                "Authorization": f"Bearer {settings.storage_service_token}",
                "Content-Type": "application/json",
            }
        )
        self.message_events_path = "/api/v1/events/message/"
        self.service_events_path = "/api/v1/events/service/"
        self.metrics_path = "/api/v1/metrics/"
        
    async def store_message_event(
        self,
        event_type: str,
        message_id: str,
        source: str,
        destination: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Store a message event.
        
        Args:
            event_type: Type of message event
            message_id: Unique message identifier
            source: Source service
            destination: Destination service
            payload: Message payload
            correlation_id: Optional correlation ID
            
        Returns:
            Stored event data
        """
        data = {
            "event_type": event_type,
            "message_id": message_id,
            "source": source,
            "destination": destination,
            "payload": payload,
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            response = await self.client.post(
                self.message_events_path,
                json=data
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(
                "Failed to store message event",
                extra={
                    "message_id": message_id,
                    "error": str(e)
                }
            )
            raise MessageHubError(f"Storage service error: {str(e)}")
            
    async def store_service_event(
        self,
        event_type: str,
        service_name: str,
        status: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store a service event.
        
        Args:
            event_type: Type of service event
            service_name: Name of the service
            status: Service status
            details: Event details
            
        Returns:
            Stored event data
        """
        data = {
            "event_type": event_type,
            "service_name": service_name,
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            response = await self.client.post(
                self.service_events_path,
                json=data
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(
                "Failed to store service event",
                extra={
                    "service": service_name,
                    "error": str(e)
                }
            )
            raise MessageHubError(f"Storage service error: {str(e)}")
            
    async def get_message_events(
        self,
        correlation_id: Optional[str] = None,
        message_id: Optional[str] = None,
        source: Optional[str] = None,
        destination: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query message events.
        
        Args:
            correlation_id: Filter by correlation ID
            message_id: Filter by message ID
            source: Filter by source service
            destination: Filter by destination service
            event_type: Filter by event type
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        params = {
            "correlation_id": correlation_id,
            "message_id": message_id,
            "source": source,
            "destination": destination,
            "event_type": event_type,
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "limit": limit
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        try:
            response = await self.client.get(
                self.message_events_path,
                params=params
            )
            response.raise_for_status()
            return response.json()["events"]
            
        except Exception as e:
            logger.error(
                "Failed to get message events",
                extra={"error": str(e)}
            )
            raise MessageHubError(f"Storage service error: {str(e)}")
            
    async def get_service_events(
        self,
        service_name: Optional[str] = None,
        status: Optional[str] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query service events.
        
        Args:
            service_name: Filter by service name
            status: Filter by status
            event_type: Filter by event type
            start_time: Filter by start time
            end_time: Filter by end time
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        params = {
            "service_name": service_name,
            "status": status,
            "event_type": event_type,
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "limit": limit
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        try:
            response = await self.client.get(
                self.service_events_path,
                params=params
            )
            response.raise_for_status()
            return response.json()["events"]
            
        except Exception as e:
            logger.error(
                "Failed to get service events",
                extra={"error": str(e)}
            )
            raise MessageHubError(f"Storage service error: {str(e)}")
            
    async def store_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Store service metrics.
        
        Args:
            metrics: Metrics data to store
            
        Returns:
            Stored metrics data
        """
        try:
            response = await self.client.post(
                self.metrics_path,
                json=metrics
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(
                "Failed to store metrics",
                extra={"error": str(e)}
            )
            raise MessageHubError(f"Storage service error: {str(e)}")
            
    async def close(self):
        """Close storage service client."""
        await self.client.aclose()