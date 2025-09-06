"""CDN integration service for image delivery."""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin
from uuid import UUID

import aiohttp
from fastapi import HTTPException

from image.core.config import get_settings
from image.core.metrics import (
    record_cdn_bandwidth,
    record_cdn_error,
    record_cdn_hit,
    record_cdn_miss
)
from image.models.storage import Image
from image.services.cache import CacheService
from image.services.storage import StorageService

logger = logging.getLogger(__name__)


class CDNService:
    """Service for managing CDN integration."""

    def __init__(
        self,
        storage_service: StorageService,
        cache_service: CacheService,
        cdn_base_url: Optional[str] = None,
        cdn_token: Optional[str] = None
    ) -> None:
        """Initialize the CDN service.

        Args:
            storage_service: Storage service instance
            cache_service: Cache service instance
            cdn_base_url: Optional base URL for CDN (default from settings)
            cdn_token: Optional CDN auth token (default from settings)
        """
        self.storage = storage_service
        self.cache = cache_service
        self.settings = get_settings()
        self.base_url = cdn_base_url or self.settings.cdn_base_url
        self.token = cdn_token or self.settings.cdn_token
        self.http = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
        )

    async def __aenter__(self) -> "CDNService":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.http.close()

    def _get_cdn_path(
        self,
        image_id: UUID,
        region: Optional[str] = None
    ) -> str:
        """Generate CDN path for image.

        Args:
            image_id: Image UUID
            region: Optional CDN region

        Returns:
            CDN path
        """
        if region:
            return f"/images/{region}/{image_id}"
        return f"/images/{image_id}"

    async def _purge_cdn_path(self, path: str) -> None:
        """Purge path from CDN cache.

        Args:
            path: CDN path to purge

        Raises:
            HTTPException: If purge fails
        """
        try:
            url = urljoin(self.base_url, "/v1/purge")
            async with self.http.post(url, json={"paths": [path]}) as resp:
                if resp.status >= 400:
                    error = await resp.text()
                    raise HTTPException(
                        status_code=resp.status,
                        detail=f"CDN purge failed: {error}"
                    )
                record_cdn_operation("purge_success")

        except Exception as e:
            logger.exception(f"CDN purge failed: {str(e)}")
            record_cdn_error("purge_error")
            raise HTTPException(
                status_code=500,
                detail=f"CDN purge failed: {str(e)}"
            )

    async def push_to_cdn(
        self,
        image_id: UUID,
        region: Optional[str] = None
    ) -> str:
        """Push image to CDN.

        Args:
            image_id: Image UUID
            region: Optional CDN region

        Returns:
            CDN URL for the image

        Raises:
            HTTPException: If push fails
        """
        try:
            # Get image content
            content, image = await self.storage.download_image(image_id)

            # Record bandwidth
            content_size = len(content)
            record_cdn_bandwidth(content_size, "ingress")

            # Generate CDN path
            path = self._get_cdn_path(image_id, region)
            url = urljoin(self.base_url, f"/v1/upload{path}")

            # Upload to CDN
            async with self.http.put(
                url,
                data=content,
                headers={"Content-Type": f"image/{image.format.value}"}
            ) as resp:
                if resp.status >= 400:
                    error = await resp.text()
                    raise HTTPException(
                        status_code=resp.status,
                        detail=f"CDN upload failed: {error}"
                    )

                # Get CDN URL from response
                data = await resp.json()
                cdn_url = data.get("url")
                if not cdn_url:
                    raise HTTPException(
                        status_code=500,
                        detail="CDN upload missing URL"
                    )

                record_cdn_operation("push_success")
                return cdn_url

        except Exception as e:
            logger.exception(f"CDN push failed: {str(e)}")
            record_cdn_error("push_error")
            raise HTTPException(
                status_code=500,
                detail=f"CDN push failed: {str(e)}"
            )

    async def get_from_cdn(
        self,
        image_id: UUID,
        region: Optional[str] = None
    ) -> bytes:
        """Get image from CDN.

        Args:
            image_id: Image UUID
            region: Optional CDN region

        Returns:
            Image bytes

        Raises:
            HTTPException: If retrieval fails
        """
        try:
            # Try cache first
            cached = await self.cache.get_content(image_id)
            if cached:
                record_cdn_hit(region or "default")
                return cached

            # Get from CDN
            path = self._get_cdn_path(image_id, region)
            url = urljoin(self.base_url, f"/v1/fetch{path}")

            async with self.http.get(url) as resp:
                if resp.status >= 400:
                    # CDN miss, fall back to storage
                    record_cdn_miss(region or "default")
                    content, _ = await self.storage.download_image(image_id)

                    # Push to CDN for next time
                    asyncio.create_task(self.push_to_cdn(image_id, region))
                    return content

                # Record hit and bandwidth
                content = await resp.read()
                record_cdn_hit(region or "default")
                record_cdn_bandwidth(len(content), "egress")

                # Cache for next time
                await self.cache.set_content(image_id, content)
                return content

        except Exception as e:
            logger.exception(f"CDN fetch failed: {str(e)}")
            record_cdn_error("fetch_error")
            raise HTTPException(
                status_code=500,
                detail=f"CDN fetch failed: {str(e)}"
            )

    async def invalidate_cdn(
        self,
        image_id: UUID,
        regions: Optional[List[str]] = None
    ) -> None:
        """Invalidate image in CDN.

        Args:
            image_id: Image UUID
            regions: Optional list of regions to invalidate

        Raises:
            HTTPException: If invalidation fails
        """
        try:
            # Clear from cache
            await self.cache.clear_image_cache(image_id)

            # Build paths to purge
            paths = []
            if regions:
                for region in regions:
                    paths.append(self._get_cdn_path(image_id, region))
            else:
                paths.append(self._get_cdn_path(image_id))

            # Purge from CDN
            for path in paths:
                await self._purge_cdn_path(path)

            record_cdn_operation("invalidate_success")

        except Exception as e:
            logger.exception(f"CDN invalidation failed: {str(e)}")
            record_cdn_error("invalidate_error")
            raise HTTPException(
                status_code=500,
                detail=f"CDN invalidation failed: {str(e)}"
            )

    async def warm_cdn(
        self,
        image_ids: List[UUID],
        regions: Optional[List[str]] = None
    ) -> None:
        """Pre-warm images in CDN.

        Args:
            image_ids: List of image IDs to warm
            regions: Optional list of regions to warm

        Raises:
            HTTPException: If warming fails
        """
        try:
            for image_id in image_ids:
                if regions:
                    for region in regions:
                        await self.push_to_cdn(image_id, region)
                else:
                    await self.push_to_cdn(image_id)

            record_cdn_operation("warm_success")

        except Exception as e:
            logger.exception(f"CDN warming failed: {str(e)}")
            record_cdn_error("warm_error")
            raise HTTPException(
                status_code=500,
                detail=f"CDN warming failed: {str(e)}"
            )

    async def get_cdn_stats(self) -> dict:
        """Get CDN statistics.

        Returns:
            Dict containing CDN stats
        """
        try:
            url = urljoin(self.base_url, "/v1/stats")
            async with self.http.get(url) as resp:
                if resp.status >= 400:
                    error = await resp.text()
                    raise HTTPException(
                        status_code=resp.status,
                        detail=f"CDN stats failed: {error}"
                    )

                stats = await resp.json()
                record_cdn_operation("stats_success")
                return stats

        except Exception as e:
            logger.exception(f"CDN stats failed: {str(e)}")
            record_cdn_error("stats_error")
            return {}
