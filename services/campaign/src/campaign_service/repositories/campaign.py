"""Campaign repository implementation."""
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from campaign_service.models.campaign import Campaign, Chapter, CampaignType, CampaignState
from campaign_service.models.pagination import PaginationResult
from campaign_service.repositories.base import BaseRepository


class CampaignRepository(BaseRepository[Campaign]):
    """Campaign repository implementation."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db (AsyncSession): Database session
        """
        super().__init__(db, Campaign)
        self.func = func

    async def batch_create(self, campaigns: List[Campaign]) -> List[Campaign]:
        """Create multiple campaigns in a single batch operation."""
        self.db.add_all(campaigns)
        await self.db.flush()
        return campaigns

    async def batch_update(self, campaigns: List[Campaign]) -> List[Campaign]:
        """Update multiple campaigns in a single batch operation."""
        for campaign in campaigns:
            campaign.updated_at = datetime.now(UTC)
        self.db.add_all(campaigns)
        await self.db.flush()
        return campaigns

    async def batch_soft_delete(self, campaign_ids: List[UUID]) -> bool:
        """Soft delete multiple campaigns in a single batch operation."""
        stmt = (
            update(Campaign)
            .where(
                and_(
                    Campaign.id.in_(campaign_ids),
                    Campaign.is_deleted == False  # noqa: E712
                )
            )
            .values(
                is_deleted=True,
                deleted_at=datetime.now(UTC),
                updated_at=datetime.now(UTC)
            )
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def get_all(self, *, include_deleted: bool = False) -> List[Campaign]:
        """Get all campaigns with option to include soft-deleted records."""
        query = select(Campaign)
        if not include_deleted:
            query = query.where(Campaign.is_deleted == False)  # noqa: E712
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> PaginationResult[Campaign]:
        """Get campaigns with pagination and optional filtering."""
        # Build base query with soft delete filter
        query = select(Campaign).where(Campaign.is_deleted == False)  # noqa: E712

        # Apply additional filters if provided
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(Campaign, key):
                    conditions.append(getattr(Campaign, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        # Get total count for pagination
        count_query = select(Campaign).where(Campaign.is_deleted == False)  # noqa: E712
        if filters:
            count_query = count_query.where(and_(*conditions))
        total = await self.db.scalar(
            select(self.func.count()).select_from(count_query.subquery())
        )

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Execute query
        result = await self.db.execute(query)
        items = result.scalars().all()

        # Calculate pagination metadata
        total_items = total or 0
        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1

        return PaginationResult[
            Campaign
        ](
            items=list(items),
            total_items=total_items,
            total_pages=total_pages,
            page_number=page,
            page_size=page_size,
            has_next=has_next,
            has_previous=has_previous
        )

    async def filter_by(
        self,
        states: Optional[List[CampaignState]] = None,
        campaign_types: Optional[List[CampaignType]] = None,
        owner_id: Optional[UUID] = None
    ) -> List[Campaign]:
        """Filter campaigns by multiple criteria."""
        conditions = [Campaign.is_deleted == False]  # noqa: E712

        if states:
            conditions.append(Campaign.state.in_(states))
        if campaign_types:
            conditions.append(Campaign.campaign_type.in_(campaign_types))
        if owner_id:
            conditions.append(Campaign.owner_id == owner_id)

        query = select(Campaign).where(and_(*conditions))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def filter_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Campaign]:
        """Filter campaigns by creation date range."""
        query = (
            select(Campaign)
            .where(
                and_(
                    Campaign.is_deleted == False,  # noqa: E712
                    Campaign.created_at >= start_date,
                    Campaign.created_at <= end_date
                )
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

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
