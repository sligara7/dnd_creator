from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from llm_service.core.settings import Settings

# Type variable for service result
T = TypeVar("T")


class BaseService(ABC):
    """Base class for all services."""

    def __init__(
        self,
        settings: Settings,
        db: Optional[AsyncSession] = None,
        logger: Optional[structlog.BoundLogger] = None,
    ) -> None:
        self.settings = settings
        self.db = db
        self.logger = logger or structlog.get_logger()

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize service resources."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up service resources."""
        pass


class AsyncCacheService(BaseService):
    """Base class for services that use caching."""

    def __init__(self, settings: Settings, cache_client: Any, *args: Any, **kwargs: Any) -> None:
        super().__init__(settings, *args, **kwargs)
        self.cache = cache_client

    async def get_from_cache(self, key: str) -> Optional[str]:
        """Get value from cache."""
        try:
            return await self.cache.get(key)
        except Exception as e:
            self.logger.warning("cache_get_failed", error=str(e), key=key)
            return None

    async def set_in_cache(
        self, key: str, value: str, ttl_seconds: Optional[int] = None
    ) -> bool:
        """Set value in cache."""
        try:
            await self.cache.set(key, value, ttl_seconds)
            return True
        except Exception as e:
            self.logger.warning("cache_set_failed", error=str(e), key=key)
            return False


class AsyncQueueService(BaseService):
    """Base class for services that use queues."""

    def __init__(self, settings: Settings, queue_client: Any, *args: Any, **kwargs: Any) -> None:
        super().__init__(settings, *args, **kwargs)
        self.queue = queue_client

    @abstractmethod
    async def enqueue(self, job_type: str, payload: Dict[str, Any]) -> str:
        """Add job to queue."""
        pass

    @abstractmethod
    async def dequeue(self, job_type: str) -> Optional[Dict[str, Any]]:
        """Get next job from queue."""
        pass

    @abstractmethod
    async def complete_job(self, job_id: str, result: Optional[T] = None) -> None:
        """Mark job as completed."""
        pass

    @abstractmethod
    async def fail_job(self, job_id: str, error: str) -> None:
        """Mark job as failed."""
        pass
