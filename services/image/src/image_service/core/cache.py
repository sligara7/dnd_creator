"""Style caching and optimization."""

import json
import zlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, TypeVar, Type, Union

from pydantic import BaseModel
from redis.asyncio import Redis

from image_service.api.schemas.style import Theme, StylePreset, StyleRequest
from image_service.core.config import get_settings
from image_service.core.logging import get_logger
from image_service.core.metrics import metrics

settings = get_settings()
logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class CacheManager:
    """Cache manager for style-related data."""

    def __init__(
        self,
        redis: Redis,
        prefix: str = "style:",
        ttl: int = settings.CACHE_TTL,
    ):
        """Initialize cache manager."""
        self.redis = redis
        self.prefix = prefix
        self.ttl = ttl

        # Default cache groups with specific TTLs
        self.cache_groups = {
            "theme": ttl * 2,  # Themes change less frequently
            "preset": ttl,
            "style": int(ttl * 0.5),  # Styles are more volatile
            "validation": int(ttl * 0.25),  # Very short TTL for validations
        }

    async def get_cached_model(
        self,
        key: str,
        model_class: Type[T],
        group: str = "default",
    ) -> Optional[T]:
        """Get cached model by key."""
        cache_key = f"{self.prefix}{group}:{key}"
        try:
            # Get from cache
            data = await self.redis.get(cache_key)
            if data:
                # Decompress if necessary
                if isinstance(data, bytes):
                    try:
                        data = zlib.decompress(data).decode()
                    except zlib.error:
                        data = data.decode()

                # Track cache hit
                metrics.track_cache_operation(f"get_{group}", hit=True)
                return model_class.parse_raw(data)

            # Track cache miss
            metrics.track_cache_operation(f"get_{group}", hit=False)
            return None

        except Exception as e:
            logger.error(
                "Cache read failed",
                key=cache_key,
                error=str(e),
            )
            return None

    async def set_cached_model(
        self,
        key: str,
        model: BaseModel,
        group: str = "default",
        compress: bool = True,
    ) -> None:
        """Cache model by key."""
        cache_key = f"{self.prefix}{group}:{key}"
        ttl = self.cache_groups.get(group, self.ttl)

        try:
            # Serialize model
            data = model.json()

            # Compress if needed
            if compress and len(data) > 1024:  # Only compress larger data
                data = zlib.compress(data.encode())

            # Store in cache
            await self.redis.set(
                cache_key,
                data,
                ex=ttl,
            )

        except Exception as e:
            logger.error(
                "Cache write failed",
                key=cache_key,
                error=str(e),
            )

    async def invalidate(
        self,
        key: str,
        group: str = "default",
    ) -> None:
        """Invalidate cached key."""
        cache_key = f"{self.prefix}{group}:{key}"
        try:
            await self.redis.delete(cache_key)
        except Exception as e:
            logger.error(
                "Cache invalidation failed",
                key=cache_key,
                error=str(e),
            )

    async def get_theme(self, theme_name: str) -> Optional[Theme]:
        """Get cached theme."""
        return await self.get_cached_model(
            key=theme_name,
            model_class=Theme,
            group="theme",
        )

    async def set_theme(self, theme: Theme) -> None:
        """Cache theme."""
        await self.set_cached_model(
            key=theme.name,
            model=theme,
            group="theme",
            compress=True,  # Themes can be large
        )

    async def get_preset(self, preset_name: str) -> Optional[StylePreset]:
        """Get cached preset."""
        return await self.get_cached_model(
            key=preset_name,
            model_class=StylePreset,
            group="preset",
        )

    async def set_preset(self, preset: StylePreset) -> None:
        """Cache preset."""
        await self.set_cached_model(
            key=preset.name,
            model=preset,
            group="preset",
        )

    async def get_style(
        self,
        style_hash: str,
    ) -> Optional[Dict[str, Any]]:
        """Get cached style parameters."""
        return await self.get_cached_model(
            key=style_hash,
            model_class=dict,
            group="style",
        )

    async def set_style(
        self,
        style_hash: str,
        params: Dict[str, Any],
    ) -> None:
        """Cache style parameters."""
        await self.set_cached_model(
            key=style_hash,
            model=params,
            group="style",
        )

    async def cache_validation_result(
        self,
        style: StyleRequest,
        issues: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Cache validation result."""
        # Create cache key from style and context
        key = (
            f"{style.json()}"
            f"{json.dumps(context or {}, sort_keys=True)}"
        )
        key_hash = str(hash(key))

        await self.set_cached_model(
            key=key_hash,
            model={"issues": issues},
            group="validation",
        )

    async def get_validation_result(
        self,
        style: StyleRequest,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[List[str]]:
        """Get cached validation result."""
        # Create cache key from style and context
        key = (
            f"{style.json()}"
            f"{json.dumps(context or {}, sort_keys=True)}"
        )
        key_hash = str(hash(key))

        result = await self.get_cached_model(
            key=key_hash,
            model_class=dict,
            group="validation",
        )
        return result.get("issues") if result else None

    async def warmup_cache(
        self,
        themes: Optional[List[Theme]] = None,
        presets: Optional[List[StylePreset]] = None,
    ) -> None:
        """Warm up cache with themes and presets."""
        if themes:
            for theme in themes:
                await self.set_theme(theme)

        if presets:
            for preset in presets:
                await self.set_preset(preset)

    async def cleanup_expired(self) -> None:
        """Clean up expired cache entries."""
        try:
            # Get all keys
            keys = []
            for group in self.cache_groups:
                pattern = f"{self.prefix}{group}:*"
                group_keys = await self.redis.keys(pattern)
                keys.extend(group_keys)

            # Check TTL for each key
            for key in keys:
                ttl = await self.redis.ttl(key)
                if ttl < 0:  # Key has no TTL or is expired
                    await self.redis.delete(key)

            logger.info(
                "Cache cleanup completed",
                expired_keys=len(keys),
            )

        except Exception as e:
            logger.error(
                "Cache cleanup failed",
                error=str(e),
            )
