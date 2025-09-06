"""Redis caching service for image data."""
import json
import logging
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Union
from uuid import UUID

from redis.asyncio import Redis

from image.core.metrics import record_cache_operation
from image.models.storage import Image, ImageType
from image.core.config import get_settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching image data and metadata in Redis."""

    # Cache prefixes
    METADATA_PREFIX = "img:meta:"
    CONTENT_PREFIX = "img:content:"
    HASH_PREFIX = "img:hash:"
    TYPE_PREFIX = "img:type:"
    USAGE_PREFIX = "img:usage:"
    POPULAR_PREFIX = "img:popular:"
    WARMUP_PREFIX = "img:warmup:"
    TTL_PREFIX = "img:ttl:"

    # Cache TTLs (in seconds)
    DEFAULT_TTL = 3600  # 1 hour
    METADATA_TTL = 3600  # 1 hour
    CONTENT_TTL = 86400  # 24 hours
    HASH_TTL = 604800  # 1 week
    USAGE_TTL = 2592000  # 30 days

    def __init__(self, redis: Redis) -> None:
        """Initialize the cache service.

        Args:
            redis: Redis client instance
        """
        self.redis = redis
        self.settings = get_settings()

    def _get_metadata_key(self, image_id: UUID) -> str:
        """Get Redis key for image metadata.

        Args:
            image_id: Image UUID

        Returns:
            Redis key
        """
        return f"{self.METADATA_PREFIX}{image_id}"

    def _get_content_key(self, image_id: UUID) -> str:
        """Get Redis key for image content.

        Args:
            image_id: Image UUID

        Returns:
            Redis key
        """
        return f"{self.CONTENT_PREFIX}{image_id}"

    def _get_hash_key(self, content_hash: str) -> str:
        """Get Redis key for content hash mapping.

        Args:
            content_hash: Content hash

        Returns:
            Redis key
        """
        return f"{self.HASH_PREFIX}{content_hash}"

    def _get_type_key(self, image_type: ImageType) -> str:
        """Get Redis key for image type set.

        Args:
            image_type: Image type

        Returns:
            Redis key
        """
        return f"{self.TYPE_PREFIX}{image_type.value}"

    def _get_usage_key(self, image_id: UUID) -> str:
        """Get Redis key for image usage tracking.

        Args:
            image_id: Image UUID

        Returns:
            Redis key
        """
        return f"{self.USAGE_PREFIX}{image_id}"

    async def get_metadata(self, image_id: UUID) -> Optional[dict]:
        """Get cached image metadata.

        Args:
            image_id: Image UUID

        Returns:
            Metadata dict if found, otherwise None
        """
        try:
            key = self._get_metadata_key(image_id)
            data = await self.redis.get(key)
            if data:
                record_cache_operation("metadata_get", True)
                return json.loads(data)
            record_cache_operation("metadata_get", False)
            return None
        except Exception as e:
            logger.error(f"Cache error getting metadata: {str(e)}")
            record_cache_operation("metadata_get_error")
            return None

    async def set_metadata(
        self,
        image_id: UUID,
        metadata: dict,
        ttl: Optional[int] = None
    ) -> None:
        """Cache image metadata.

        Args:
            image_id: Image UUID
            metadata: Metadata dict
            ttl: Optional TTL in seconds
        """
        try:
            key = self._get_metadata_key(image_id)
            await self.redis.set(
                key,
                json.dumps(metadata),
                ex=ttl or self.METADATA_TTL
            )
            record_cache_operation("metadata_set")
        except Exception as e:
            logger.error(f"Cache error setting metadata: {str(e)}")
            record_cache_operation("metadata_set_error")

    async def get_content(self, image_id: UUID) -> Optional[bytes]:
        """Get cached image content.

        Args:
            image_id: Image UUID

        Returns:
            Image bytes if found, otherwise None
        """
        try:
            key = self._get_content_key(image_id)
            data = await self.redis.get(key)
            if data:
                # Track usage for cache warming
                await self.record_usage(image_id)
                record_cache_operation("content_get", True)
                return data
            record_cache_operation("content_get", False)
            return None
        except Exception as e:
            logger.error(f"Cache error getting content: {str(e)}")
            record_cache_operation("content_get_error")
            return None

    async def set_content(
        self,
        image_id: UUID,
        content: bytes,
        ttl: Optional[int] = None
    ) -> None:
        """Cache image content.

        Args:
            image_id: Image UUID
            content: Image bytes
            ttl: Optional TTL in seconds
        """
        try:
            key = self._get_content_key(image_id)
            await self.redis.set(
                key,
                content,
                ex=ttl or self.CONTENT_TTL
            )
            record_cache_operation("content_set")
        except Exception as e:
            logger.error(f"Cache error setting content: {str(e)}")
            record_cache_operation("content_set_error")

    async def record_usage(self, image_id: UUID) -> None:
        """Record image usage for cache warming.

        Args:
            image_id: Image UUID
        """
        try:
            # Increment usage counter
            key = self._get_usage_key(image_id)
            await self.redis.zincrby(
                self.POPULAR_PREFIX,
                1,
                str(image_id)
            )
            record_cache_operation("usage_record")
        except Exception as e:
            logger.error(f"Cache error recording usage: {str(e)}")
            record_cache_operation("usage_record_error")

    async def get_popular_images(
        self,
        limit: int = 1000
    ) -> List[Tuple[UUID, float]]:
        """Get most frequently accessed images.

        Args:
            limit: Maximum number of images

        Returns:
            List of (image_id, score) tuples
        """
        try:
            # Get top images by usage
            results = await self.redis.zrevrange(
                self.POPULAR_PREFIX,
                0,
                limit - 1,
                withscores=True
            )
            return [(UUID(id_bytes.decode()), score) for id_bytes, score in results]
        except Exception as e:
            logger.error(f"Cache error getting popular images: {str(e)}")
            return []

    async def warm_cache(
        self,
        images: List[Tuple[UUID, dict, bytes]]
    ) -> None:
        """Warm cache with frequently accessed images.

        Args:
            images: List of (image_id, metadata, content) tuples
        """
        try:
            # Track warmup start
            warmup_key = f"{self.WARMUP_PREFIX}{datetime.utcnow().isoformat()}"
            pipeline = self.redis.pipeline()

            # Cache all images
            for image_id, metadata, content in images:
                meta_key = self._get_metadata_key(image_id)
                content_key = self._get_content_key(image_id)
                pipeline.set(
                    meta_key,
                    json.dumps(metadata),
                    ex=self.METADATA_TTL
                )
                pipeline.set(
                    content_key,
                    content,
                    ex=self.CONTENT_TTL
                )
                pipeline.sadd(warmup_key, str(image_id))

            # Execute pipeline
            await pipeline.execute()
            record_cache_operation("warmup")
        except Exception as e:
            logger.error(f"Cache error during warmup: {str(e)}")
            record_cache_operation("warmup_error")

    async def get_image_by_hash(self, content_hash: str) -> Optional[UUID]:
        """Get image ID by content hash.

        Args:
            content_hash: Content hash to find

        Returns:
            Image UUID if found, otherwise None
        """
        try:
            key = self._get_hash_key(content_hash)
            data = await self.redis.get(key)
            if data:
                record_cache_operation("hash_get", True)
                return UUID(data.decode())
            record_cache_operation("hash_get", False)
            return None
        except Exception as e:
            logger.error(f"Cache error getting hash: {str(e)}")
            record_cache_operation("hash_get_error")
            return None

    async def set_image_hash(
        self,
        content_hash: str,
        image_id: UUID
    ) -> None:
        """Cache content hash to image mapping.

        Args:
            content_hash: Content hash
            image_id: Image UUID
        """
        try:
            key = self._get_hash_key(content_hash)
            await self.redis.set(
                key,
                str(image_id),
                ex=self.HASH_TTL
            )
            record_cache_operation("hash_set")
        except Exception as e:
            logger.error(f"Cache error setting hash: {str(e)}")
            record_cache_operation("hash_set_error")

    async def get_images_by_type(
        self,
        image_type: ImageType
    ) -> Set[UUID]:
        """Get cached image IDs by type.

        Args:
            image_type: Image type to find

        Returns:
            Set of image UUIDs
        """
        try:
            key = self._get_type_key(image_type)
            data = await self.redis.smembers(key)
            if data:
                record_cache_operation("type_get", True)
                return {UUID(id_bytes.decode()) for id_bytes in data}
            record_cache_operation("type_get", False)
            return set()
        except Exception as e:
            logger.error(f"Cache error getting type: {str(e)}")
            record_cache_operation("type_get_error")
            return set()

    async def add_image_to_type(
        self,
        image_type: ImageType,
        image_id: UUID
    ) -> None:
        """Add image to type set.

        Args:
            image_type: Image type
            image_id: Image UUID
        """
        try:
            key = self._get_type_key(image_type)
            await self.redis.sadd(key, str(image_id))
            record_cache_operation("type_add")
        except Exception as e:
            logger.error(f"Cache error adding to type: {str(e)}")
            record_cache_operation("type_add_error")

    async def remove_image_from_type(
        self,
        image_type: ImageType,
        image_id: UUID
    ) -> None:
        """Remove image from type set.

        Args:
            image_type: Image type
            image_id: Image UUID
        """
        try:
            key = self._get_type_key(image_type)
            await self.redis.srem(key, str(image_id))
            record_cache_operation("type_remove")
        except Exception as e:
            logger.error(f"Cache error removing from type: {str(e)}")
            record_cache_operation("type_remove_error")

    async def clear_image_cache(self, image_id: UUID) -> None:
        """Clear all cached data for an image.

        Args:
            image_id: Image UUID
        """
        try:
            # Get all keys for this image
            meta_key = self._get_metadata_key(image_id)
            content_key = self._get_content_key(image_id)
            usage_key = self._get_usage_key(image_id)

            # Delete all keys
            pipeline = self.redis.pipeline()
            pipeline.delete(meta_key)
            pipeline.delete(content_key)
            pipeline.delete(usage_key)
            pipeline.zrem(self.POPULAR_PREFIX, str(image_id))
            await pipeline.execute()
            record_cache_operation("clear")
        except Exception as e:
            logger.error(f"Cache error clearing image: {str(e)}")
            record_cache_operation("clear_error")

    async def get_cache_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dict containing cache stats
        """
        try:
            # Get counts
            meta_keys = await self.redis.keys(f"{self.METADATA_PREFIX}*")
            content_keys = await self.redis.keys(f"{self.CONTENT_PREFIX}*")
            hash_keys = await self.redis.keys(f"{self.HASH_PREFIX}*")
            type_keys = await self.redis.keys(f"{self.TYPE_PREFIX}*")

            # Calculate memory usage
            info = await self.redis.info("memory")
            used_memory = info.get("used_memory", 0)

            # Get popular image count
            popular_count = await self.redis.zcard(self.POPULAR_PREFIX)

            return {
                "metadata_count": len(meta_keys),
                "content_count": len(content_keys),
                "hash_count": len(hash_keys),
                "type_count": len(type_keys),
                "popular_count": popular_count,
                "memory_bytes": used_memory,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Cache error getting stats: {str(e)}")
            return {}
