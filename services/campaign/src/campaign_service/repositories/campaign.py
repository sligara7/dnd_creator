"""Campaign repository implementation."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from campaign_service.models.campaign import Campaign, Chapter
from campaign_service.repositories.base import BaseRepository


class CampaignRepository(BaseRepository[Campaign]):
    """Campaign repository implementation."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db (AsyncSession): Database session
        """
        super().__init__(db, Campaign)

    async def get_with_chapters(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign with its chapters.

        Args:
            campaign_id (UUID): Campaign ID

        Returns:
            Optional[Campaign]: Campaign with chapters if found, None otherwise
        """
        query = (
            select(Campaign)
            .options(selectinload(Campaign.chapters))
            .where(
                Campaign.id == campaign_id,
                Campaign.is_deleted == False,  # noqa: E712
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_owner(
        self,
        owner_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Campaign]:
        """Get campaigns by owner.

        Args:
            owner_id (UUID): Owner ID
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records. Defaults to 100.

        Returns:
            List[Campaign]: List of campaigns
        """
        return await self.get_multi(
            owner_id=owner_id,
            skip=skip,
            limit=limit,
        )


class ChapterRepository(BaseRepository[Chapter]):
    """Chapter repository implementation."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db (AsyncSession): Database session
        """
        super().__init__(db, Chapter)

    async def get_by_campaign(
        self,
        campaign_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Chapter]:
        """Get chapters by campaign.

        Args:
            campaign_id (UUID): Campaign ID
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records. Defaults to 100.

        Returns:
            List[Chapter]: List of chapters
        """
        return await self.get_multi(
            campaign_id=campaign_id,
            skip=skip,
            limit=limit,
        )

    async def get_prerequisites(
        self,
        chapter_id: UUID,
    ) -> List[Chapter]:
        """Get chapter prerequisites.

        Args:
            chapter_id (UUID): Chapter ID

        Returns:
            List[Chapter]: List of prerequisite chapters
        """
        # First get the chapter to get its prerequisites
        chapter = await self.get(chapter_id)
        if not chapter:
            return []

        # Then get all the prerequisite chapters
        query = select(Chapter).where(
            Chapter.id.in_(chapter.prerequisites),
            Chapter.is_deleted == False,  # noqa: E712
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
