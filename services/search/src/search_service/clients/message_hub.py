import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from httpx import AsyncClient, HTTPError
from loguru import logger

from search_service.core.config import settings


class MessageHubClient:
    """Client for interacting with the Message Hub service"""

    def __init__(self) -> None:
        """Initialize Message Hub client"""
        self.client = AsyncClient(
            base_url=settings.MESSAGE_HUB_URL,
            timeout=30.0,
        )
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._health_task: Optional[asyncio.Task] = None

    async def close(self) -> None:
        """Close client connections"""
        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass
        await self.client.aclose()

    async def start(self) -> None:
        """Start client and health check"""
        await self._register_service()
        self._health_task = asyncio.create_task(self._health_check())

    async def _register_service(self) -> None:
        """Register service with Message Hub"""
        try:
            await self.client.post(
                "/register",
                json={
                    "service_name": settings.SERVICE_NAME,
                    "version": settings.VERSION,
                    "ttl": settings.SERVICE_TTL,
                    "endpoints": [
                        {
                            "name": "health",
                            "url": f"http://{settings.HOST}:{settings.PORT}/health",
                            "method": "GET",
                        },
                        {
                            "name": "metrics",
                            "url": f"http://{settings.HOST}:{settings.METRICS_PORT}/metrics",
                            "method": "GET",
                        },
                    ],
                },
            )
            logger.info("Service registered with Message Hub")
        except HTTPError as e:
            logger.error(f"Failed to register service: {e}")
            raise

    async def _health_check(self) -> None:
        """Periodic health check ping"""
        while True:
            try:
                await self.client.post(
                    "/health",
                    json={
                        "service_name": settings.SERVICE_NAME,
                        "status": "healthy",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                await asyncio.sleep(5)  # Shorter retry interval on failure

    async def publish(
        self,
        topic: str,
        message: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish message to topic"""
        try:
            await self.client.post(
                "/publish",
                json={
                    "topic": topic,
                    "message": message,
                    "metadata": metadata or {},
                    "publisher": settings.SERVICE_NAME,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            logger.debug(f"Published message to {topic}", extra={"metadata": metadata})
        except HTTPError as e:
            logger.error(f"Failed to publish message: {e}")
            raise

    async def subscribe(
        self,
        topic: str,
        callback: Callable[[Dict[str, Any]], None],
    ) -> None:
        """Subscribe to topic with callback"""
        if topic not in self._subscriptions:
            self._subscriptions[topic] = []
            try:
                await self.client.post(
                    "/subscribe",
                    json={
                        "topic": topic,
                        "subscriber": settings.SERVICE_NAME,
                        "callback_url": f"http://{settings.HOST}:{settings.PORT}/events",
                    },
                )
                logger.info(f"Subscribed to topic: {topic}")
            except HTTPError as e:
                logger.error(f"Failed to subscribe to topic: {e}")
                raise
        self._subscriptions[topic].append(callback)

    async def unsubscribe(self, topic: str) -> None:
        """Unsubscribe from topic"""
        if topic in self._subscriptions:
            try:
                await self.client.post(
                    "/unsubscribe",
                    json={
                        "topic": topic,
                        "subscriber": settings.SERVICE_NAME,
                    },
                )
                del self._subscriptions[topic]
                logger.info(f"Unsubscribed from topic: {topic}")
            except HTTPError as e:
                logger.error(f"Failed to unsubscribe from topic: {e}")
                raise

    def get_callbacks(self, topic: str) -> List[Callable]:
        """Get registered callbacks for topic"""
        return self._subscriptions.get(topic, [])

    # Search-specific events

    async def publish_index_update(
        self,
        index: str,
        operation: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish index update event"""
        await self.publish(
            topic="search.index.update",
            message={
                "index": index,
                "operation": operation,
                "document_id": document_id,
            },
            metadata=metadata,
        )

    async def publish_search_stats(
        self,
        index: str,
        query: str,
        results: int,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish search statistics event"""
        await self.publish(
            topic="search.stats",
            message={
                "index": index,
                "query": query,
                "results": results,
                "duration_ms": duration_ms,
            },
            metadata=metadata,
        )

    async def publish_cache_stats(
        self,
        operation: str,
        key: str,
        hit: bool,
        duration_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish cache statistics event"""
        await self.publish(
            topic="search.cache.stats",
            message={
                "operation": operation,
                "key": key,
                "hit": hit,
                "duration_ms": duration_ms,
            },
            metadata=metadata,
        )
