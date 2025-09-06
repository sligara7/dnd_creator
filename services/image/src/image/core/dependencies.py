"""FastAPI dependency injection providers."""
from typing import AsyncGenerator

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from image.core.config import get_settings
from image.core.db import get_db_session
from image.core.redis import get_redis_client
from image.services.batch import BatchProcessor
from image.services.queue import QueueService


async def get_queue_service(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client)
) -> AsyncGenerator[QueueService, None]:
    """Get queue service instance.

    Args:
        session: Database session
        redis: Redis client

    Yields:
        Queue service instance
    """
    service = QueueService(redis=redis, session=session)
    try:
        yield service
    finally:
        await session.close()


async def get_batch_processor(
    queue: QueueService = Depends(get_queue_service)
) -> AsyncGenerator[BatchProcessor, None]:
    """Get batch processor instance.

    Args:
        queue: Queue service instance

    Yields:
        Batch processor instance
    """
    processor = BatchProcessor(queue_service=queue)
    yield processor
