"""Story management repositories."""
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from campaign_service.models.story import (
    NPCRelationship,
    Plot,
    PlotChapter,
    StoryArc,
)
from campaign_service.repositories.base import BaseRepository


class StoryArcRepository(BaseRepository[StoryArc]):
    """Story arc repository implementation."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db (AsyncSession): Database session
        """
        super().__init__(db, StoryArc)

    async def get_with_plots(self, arc_id: UUID) -> Optional[StoryArc]:
        """Get story arc with its plots.

        Args:
            arc_id (UUID): Story arc ID

        Returns:
            Optional[StoryArc]: Story arc with plots if found, None otherwise
        """
        query = (
            select(StoryArc)
            .options(selectinload(StoryArc.plots))
            .where(
                StoryArc.id == arc_id,
                StoryArc.is_deleted == False,  # noqa: E712
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_campaign(
        self,
        campaign_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[StoryArc]:
        """Get story arcs by campaign.

        Args:
            campaign_id (UUID): Campaign ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records

        Returns:
            List[StoryArc]: List of story arcs
        """
        return await self.get_multi(
            campaign_id=campaign_id,
            skip=skip,
            limit=limit,
        )


class PlotRepository(BaseRepository[Plot]):
    """Plot repository implementation."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db (AsyncSession): Database session
        """
        super().__init__(db, Plot)

    async def get_with_chapters(self, plot_id: UUID) -> Optional[Plot]:
        """Get plot with its chapters.

        Args:
            plot_id (UUID): Plot ID

        Returns:
            Optional[Plot]: Plot with chapters if found, None otherwise
        """
        query = (
            select(Plot)
            .options(selectinload(Plot.chapters).selectinload(PlotChapter.chapter))
            .where(
                Plot.id == plot_id,
                Plot.is_deleted == False,  # noqa: E712
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_campaign(
        self,
        campaign_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Plot]:
        """Get plots by campaign.

        Args:
            campaign_id (UUID): Campaign ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records

        Returns:
            List[Plot]: List of plots
        """
        return await self.get_multi(
            campaign_id=campaign_id,
            skip=skip,
            limit=limit,
        )

    async def get_by_arc(
        self,
        arc_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Plot]:
        """Get plots by story arc.

        Args:
            arc_id (UUID): Story arc ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records

        Returns:
            List[Plot]: List of plots
        """
        return await self.get_multi(
            arc_id=arc_id,
            skip=skip,
            limit=limit,
        )

    async def get_subplots(
        self,
        plot_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Plot]:
        """Get subplots of a plot.

        Args:
            plot_id (UUID): Parent plot ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records

        Returns:
            List[Plot]: List of subplots
        """
        return await self.get_multi(
            parent_plot_id=plot_id,
            skip=skip,
            limit=limit,
        )


class PlotChapterRepository(BaseRepository[PlotChapter]):
    """Plot chapter repository implementation."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db (AsyncSession): Database session
        """
        super().__init__(db, PlotChapter)

    async def get_by_plot(
        self,
        plot_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[PlotChapter]:
        """Get plot chapters by plot.

        Args:
            plot_id (UUID): Plot ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records

        Returns:
            List[PlotChapter]: List of plot chapters
        """
        return await self.get_multi(
            plot_id=plot_id,
            skip=skip,
            limit=limit,
        )

    async def get_plot_order(self, plot_id: UUID) -> List[Tuple[UUID, int]]:
        """Get chapter ordering for a plot.

        Args:
            plot_id (UUID): Plot ID

        Returns:
            List[Tuple[UUID, int]]: List of (chapter_id, order) tuples
        """
        query = (
            select(PlotChapter.chapter_id, PlotChapter.plot_order)
            .where(
                PlotChapter.plot_id == plot_id,
            )
            .order_by(PlotChapter.plot_order)
        )
        result = await self.db.execute(query)
        return list(result.all())


class NPCRelationshipRepository(BaseRepository[NPCRelationship]):
    """NPC relationship repository implementation."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository.

        Args:
            db (AsyncSession): Database session
        """
        super().__init__(db, NPCRelationship)

    async def get_by_campaign(
        self,
        campaign_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[NPCRelationship]:
        """Get NPC relationships by campaign.

        Args:
            campaign_id (UUID): Campaign ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records

        Returns:
            List[NPCRelationship]: List of NPC relationships
        """
        return await self.get_multi(
            campaign_id=campaign_id,
            skip=skip,
            limit=limit,
        )

    async def get_by_plot(
        self,
        plot_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[NPCRelationship]:
        """Get NPC relationships by plot.

        Args:
            plot_id (UUID): Plot ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records

        Returns:
            List[NPCRelationship]: List of NPC relationships
        """
        return await self.get_multi(
            plot_id=plot_id,
            skip=skip,
            limit=limit,
        )

    async def get_by_arc(
        self,
        arc_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[NPCRelationship]:
        """Get NPC relationships by story arc.

        Args:
            arc_id (UUID): Story arc ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records

        Returns:
            List[NPCRelationship]: List of NPC relationships
        """
        return await self.get_multi(
            arc_id=arc_id,
            skip=skip,
            limit=limit,
        )
