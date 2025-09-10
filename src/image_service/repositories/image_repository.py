"""
Image repository for database operations.
"""

from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.image import Image

class ImageRepository:
    """Repository for Image model operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize with database session.
        
        Args:
            db: Async database session
        """
        self.db = db

    async def save(self, image: Image) -> Image:
        """Save an image to the database.
        
        Args:
            image: Image model to save
            
        Returns:
            Saved image model
        """
        self.db.add(image)
        await self.db.flush()
        return image

    async def get(self, image_id: UUID) -> Optional[Image]:
        """Retrieve an image by ID.
        
        Args:
            image_id: UUID of image to retrieve
            
        Returns:
            Image model if found, None otherwise
        """
        query = select(Image).where(Image.id == image_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
