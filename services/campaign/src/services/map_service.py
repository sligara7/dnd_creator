"""Map generation service."""
from typing import Dict, List, Optional
from uuid import UUID

from src.core.logging import get_logger
from src.models.campaign import Campaign, Chapter

logger = get_logger(__name__)


class MapService:
    """Service for generating campaign and location maps."""

    def __init__(self, message_hub_client):
        """Initialize with required dependencies."""
        self.message_hub = message_hub_client

    async def generate_campaign_maps(
        self,
        campaign: Campaign
    ) -> Dict[str, str]:
        """Generate maps for a campaign."""
        try:
            maps = {}

            # Generate world map
            world_map = await self._generate_map(
                "world",
                campaign=campaign.dict(),
            )
            if world_map:
                maps["world"] = world_map["url"]

            # Generate region maps
            for region in campaign.regions:
                region_map = await self._generate_map(
                    "region",
                    region=region,
                    campaign=campaign.dict(),
                )
                if region_map:
                    maps[f"region_{region['name']}"] = region_map["url"]

            return maps

        except Exception as e:
            logger.error("Campaign map generation failed", error=str(e))
            return {}

    async def generate_chapter_maps(
        self,
        chapter: Chapter,
        campaign: Campaign
    ) -> Dict[str, str]:
        """Generate maps for a chapter."""
        try:
            maps = {}

            for location in chapter.locations:
                location_map = await self._generate_map(
                    location["type"],
                    location=location,
                    theme=chapter.theme,
                    campaign=campaign.dict(),
                )
                if location_map:
                    maps[f"location_{location['name']}"] = location_map["url"]

            return maps

        except Exception as e:
            logger.error("Chapter map generation failed", error=str(e))
            return {}

    async def generate_location_map(
        self,
        location_type: str,
        location_data: Dict,
        theme: Optional[Dict] = None,
        campaign_data: Optional[Dict] = None
    ) -> Optional[str]:
        """Generate a map for a specific location."""
        try:
            result = await self._generate_map(
                location_type,
                location=location_data,
                theme=theme,
                campaign=campaign_data,
            )
            return result["url"] if result else None

        except Exception as e:
            logger.error("Location map generation failed", error=str(e))
            return None

    async def _generate_map(
        self,
        map_type: str,
        **context
    ) -> Optional[Dict]:
        """Generate a map using the image service."""
        try:
            result = await self.message_hub.request(
                "image.generate_map",
                {
                    "type": map_type,
                    **context
                }
            )
            return result if result and "url" in result else None

        except Exception as e:
            logger.error(f"Map generation failed for type {map_type}", error=str(e))
            return None
