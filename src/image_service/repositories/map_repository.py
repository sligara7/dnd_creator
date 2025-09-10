"""
Repository for map image operations.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.map_result import MapImage

class MapRepository:
    """Repository for map image operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize with database session.
        
        Args:
            db: Async database session
        """
        self.db = db

    async def save(self, map_image: MapImage) -> MapImage:
        """Save a map image.
        
        Args:
            map_image: Map image to save
            
        Returns:
            Saved map image
        """
        self.db.add(map_image)
        await self.db.flush()
        return map_image

    async def get_by_id(self, map_id: UUID) -> Optional[MapImage]:
        """Get a map image by ID.
        
        Args:
            map_id: UUID of map to retrieve
            
        Returns:
            MapImage if found, None otherwise
        """
        query = select(MapImage).where(MapImage.id == map_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_campaign(self, campaign_id: UUID) -> List[MapImage]:
        """Get all maps for a campaign.
        
        Args:
            campaign_id: Campaign UUID
            
        Returns:
            List of campaign maps
        """
        query = select(MapImage).where(MapImage.campaign_id == campaign_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_encounter(self, encounter_id: UUID) -> Optional[MapImage]:
        """Get tactical map for an encounter.
        
        Args:
            encounter_id: Encounter UUID
            
        Returns:
            MapImage if found, None otherwise
        """
        query = select(MapImage).where(MapImage.encounter_id == encounter_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
