"""Background worker for cache warming."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from image.core.config import get_settings
from image.core.metrics import record_cache_operation
from image.services.cache import CacheService
from image.services.storage import StorageService
from image.repositories.image import ImageRepository

logger = logging.getLogger(__name__)


class CacheWarmer:
    """Worker for managing cache warming."""

    def __init__(
        self,
        cache_service: CacheService,
        storage_service: StorageService,
        warm_interval: int = 300,  # 5 minutes
        target_hit_rate: float = 0.9,  # 90%
        max_cache_size: int = 10 * 1024 * 1024 * 1024  # 10GB
    ) -> None:
        """Initialize the cache warmer.

        Args:
            cache_service: Redis cache service
            storage_service: S3 storage service
            warm_interval: Seconds between warm cycles
            target_hit_rate: Target cache hit rate
            max_cache_size: Maximum cache size in bytes
        """
        self.cache = cache_service
        self.storage = storage_service
        self.warm_interval = warm_interval
        self.target_hit_rate = target_hit_rate
        self.max_cache_size = max_cache_size
        self.running = False

    async def start(self) -> None:
        """Start the cache warming loop."""
        if self.running:
            return

        self.running = True
        asyncio.create_task(self._warm_loop())

    async def stop(self) -> None:
        """Stop the cache warming loop."""
        self.running = False

    async def _get_cache_hit_rate(self) -> float:
        """Calculate current cache hit rate.

        Returns:
            Hit rate as float between 0 and 1
        """
        # Get operation counts from metrics
        hit_count = record_cache_operation.labels(
            operation="content_get",
            status="True"
        )._value.get()
        miss_count = record_cache_operation.labels(
            operation="content_get",
            status="False"
        )._value.get()
        total = hit_count + miss_count

        if total == 0:
            return 1.0  # No requests yet

        return hit_count / total

    async def _warm_loop(self) -> None:
        """Main cache warming loop."""
        while self.running:
            try:
                # Check current hit rate
                hit_rate = await self._get_cache_hit_rate()
                logger.info(f"Current cache hit rate: {hit_rate:.2%}")

                # Only warm if below target
                if hit_rate < self.target_hit_rate:
                    await self._warm_cache()

                # Wait for next cycle
                await asyncio.sleep(self.warm_interval)

            except Exception as e:
                logger.exception("Error in cache warm loop")
                await asyncio.sleep(self.warm_interval)

    async def _warm_cache(self) -> None:
        """Perform cache warming."""
        try:
            # Get cache stats
            stats = await self.cache.get_cache_stats()
            current_size = stats.get("memory_bytes", 0)

            # Check if we have room
            if current_size >= self.max_cache_size:
                logger.warning("Cache at maximum size, skipping warm")
                return

            # Get popular images
            popular = await self.cache.get_popular_images()
            if not popular:
                logger.info("No popular images to warm")
                return

            # Calculate space available
            space_available = self.max_cache_size - current_size

            # Process popular images until full
            warm_count = 0
            space_used = 0

            for image_id, score in popular:
                # Skip if already cached
                if await self.cache.get_content(image_id):
                    continue

                # Get image data
                try:
                    content, image = await self.storage.download_image(image_id)
                    metadata = {
                        "type": image.type.value,
                        "format": image.format.value,
                        "width": image.width,
                        "height": image.height,
                        "theme": image.theme,
                        "tags": image.tags
                    }

                    # Check if we have room
                    content_size = len(content)
                    if space_used + content_size > space_available:
                        break

                    # Cache image
                    await self.cache.set_metadata(image_id, metadata)
                    await self.cache.set_content(image_id, content)
                    space_used += content_size
                    warm_count += 1

                except Exception as e:
                    logger.error(f"Error warming image {image_id}: {str(e)}")
                    continue

            logger.info(
                f"Warmed {warm_count} images using "
                f"{space_used / 1024 / 1024:.1f}MB"
            )

        except Exception as e:
            logger.exception("Error warming cache")


async def run_cache_warmer() -> None:
    """Run the cache warmer as a standalone process."""
    # Get settings
    settings = get_settings()

    # Create Redis client
    redis = await create_redis_pool(
        f"redis://{settings.redis_host}:{settings.redis_port}"
    )

    # Create database engine
    engine = create_async_engine(settings.database_url)
    AsyncSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Create services
    async with AsyncSessionLocal() as session:
        cache_service = CacheService(redis)
        storage_service = StorageService(session)
        warmer = CacheWarmer(cache_service, storage_service)

        try:
            # Run warmer
            await warmer.start()

            # Keep running
            while True:
                await asyncio.sleep(3600)

        except KeyboardInterrupt:
            # Shutdown
            await warmer.stop()
            await redis.close()
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_cache_warmer())
