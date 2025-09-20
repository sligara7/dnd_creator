"""
Storage Service client for the Audit Service.

This module handles communication with the Storage Service.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import json

import structlog
import httpx

from audit_service.core.config import settings
from audit_service.core.exceptions import StorageError
from audit_service.models.events import Event

logger = structlog.get_logger()

class StorageClient:
    """Client for interacting with the Storage Service."""
    
    def __init__(self) -> None:
        """Initialize the Storage client."""
        self.logger = logger.bind(component="storage_client")
        self._client = httpx.AsyncClient(
            base_url=settings.STORAGE_SERVICE_URL,
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "X-Service-Name": "audit_service"
            }
        )
        self._max_retries = settings.MAX_RETRIES
        self._retry_delay = settings.RETRY_DELAY
        self._db_name = "audit_events"
    
    async def setup(self) -> None:
        """Set up the storage client."""
        try:
            # Verify connection and create database if needed
            response = await self._client.post(
                "/db/create",
                json={
                    "name": self._db_name,
                    "options": {
                        "retention_days": settings.EVENT_RETENTION_DAYS,
                        "shards": 3,
                        "replicas": 1
                    }
                }
            )
            response.raise_for_status()
            
            self.logger.info(
                "Connected to Storage Service",
                database=self._db_name
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to connect to Storage Service",
                error=str(e)
            )
            raise StorageError(
                backend="storage_service",
                message="Failed to connect",
                operation="setup",
                details={"error": str(e)}
            )
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        await self._client.aclose()
    
    async def store_event(self, event: Event) -> str:
        """
        Store an event in the Storage Service.
        
        Args:
            event: Event to store
            
        Returns:
            Storage ID of the event
            
        Raises:
            StorageError: If storage fails
        """
        try:
            response = await self._client.post(
                f"/db/{self._db_name}/events",
                json=event.model_dump()
            )
            response.raise_for_status()
            result = response.json()
            return result["id"]
            
        except Exception as e:
            raise StorageError(
                backend="storage_service",
                message="Failed to store event",
                operation="store",
                details={"error": str(e)}
            )
    
    async def store_events(self, events: List[Event]) -> List[str]:
        """
        Store multiple events in the Storage Service.
        
        Args:
            events: List of events to store
            
        Returns:
            List of storage IDs for the events
            
        Raises:
            StorageError: If storage fails
        """
        try:
            response = await self._client.post(
                f"/db/{self._db_name}/events/batch",
                json=[event.model_dump() for event in events]
            )
            response.raise_for_status()
            result = response.json()
            return result["ids"]
            
        except Exception as e:
            raise StorageError(
                backend="storage_service",
                message="Failed to store events batch",
                operation="store_batch",
                details={"error": str(e)}
            )
    
    async def get_events(
        self,
        start_date: datetime,
        end_date: datetime,
        event_types: Optional[List[str]] = None,
        services: Optional[List[str]] = None,
        severity: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Event]:
        """
        Retrieve events from storage.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            event_types: Optional list of event types to filter by
            services: Optional list of services to filter by
            severity: Optional severity level to filter by
            limit: Maximum number of events to return
            offset: Number of events to skip
            
        Returns:
            List of matching events
            
        Raises:
            StorageError: If retrieval fails
        """
        try:
            query = {
                "time_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "filters": [
                    {
                        "field": "timestamp",
                        "operator": "gte",
                        "value": start_date.isoformat()
                    },
                    {
                        "field": "timestamp",
                        "operator": "lte",
                        "value": end_date.isoformat()
                    }
                ],
                "pagination": {
                    "limit": limit,
                    "offset": offset
                }
            }
            
            if event_types:
                query["filters"].append({
                    "field": "type",
                    "operator": "in",
                    "value": event_types
                })
            
            if services:
                query["filters"].append({
                    "field": "service",
                    "operator": "in",
                    "value": services
                })
            
            if severity:
                query["filters"].append({
                    "field": "severity",
                    "operator": "eq",
                    "value": severity
                })
            
            response = await self._client.post(
                f"/db/{self._db_name}/events/search",
                json=query
            )
            response.raise_for_status()
            result = response.json()
            return [Event(**event_data) for event_data in result["events"]]
            
        except Exception as e:
            raise StorageError(
                backend="storage_service",
                message="Failed to retrieve events",
                operation="retrieve",
                details={"error": str(e)}
            )
    
    async def archive_events(
        self,
        events: List[Event],
        archive_id: str
    ) -> None:
        """
        Archive events for long-term storage.
        
        Args:
            events: List of events to archive
            archive_id: ID of the archive batch
            
        Raises:
            StorageError: If archival fails
        """
        try:
            response = await self._client.post(
                f"/db/{self._db_name}/events/archive",
                json={
                    "events": [event.model_dump() for event in events],
                    "archive_id": archive_id,
                    "metadata": {
                        "created_at": datetime.utcnow().isoformat(),
                        "event_count": len(events)
                    }
                }
            )
            response.raise_for_status()
            
        except Exception as e:
            raise StorageError(
                backend="storage_service",
                message="Failed to archive events",
                operation="archive",
                details={"error": str(e)}
            )
    
    async def delete_events(
        self,
        event_ids: List[str]
    ) -> None:
        """
        Delete events from storage.
        
        Args:
            event_ids: List of event IDs to delete
            
        Raises:
            StorageError: If deletion fails
        """
        try:
            response = await self._client.post(
                f"/db/{self._db_name}/events/delete",
                json={"ids": event_ids}
            )
            response.raise_for_status()
            
        except Exception as e:
            raise StorageError(
                backend="storage_service",
                message="Failed to delete events",
                operation="delete",
                details={"error": str(e)}
            )
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Dictionary containing storage statistics
            
        Raises:
            StorageError: If retrieval fails
        """
        try:
            response = await self._client.get(
                f"/db/{self._db_name}/stats"
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            raise StorageError(
                backend="storage_service",
                message="Failed to get storage stats",
                operation="stats",
                details={"error": str(e)}
            )