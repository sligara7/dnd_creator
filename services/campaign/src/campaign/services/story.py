"""Service layer for story management."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.api.story import (
    ChapterCreate, ChapterResponse, ChapterUpdate,
    NPCRelationshipCreate, NPCRelationshipResponse, NPCRelationshipUpdate,
    PlotCreate, PlotResponse, PlotUpdate,
    StoryArcCreate, StoryArcResponse, StoryArcUpdate
)
from campaign_service.models.story import Plot, StoryArc, NPCRelationship, PlotChapter


class StoryService:
    """Service for managing campaign stories, plots, and relationships."""

    def __init__(self, db: AsyncSession):
        """Initialize the story service.

        Args:
            db: Database session
        """
        self.db = db

    # Plot Management
    async def create_plot(self, plot_data: PlotCreate) -> PlotResponse:
        """Create a new plot.

        Args:
            plot_data: Plot creation data

        Returns:
            The created plot
        """
        plot = Plot(**plot_data.dict())
        self.db.add(plot)
        await self.db.flush()
        await self.db.refresh(plot)
        return PlotResponse.from_orm(plot)

    async def get_plot(self, plot_id: UUID) -> Optional[PlotResponse]:
        """Get a plot by ID.

        Args:
            plot_id: Plot ID

        Returns:
            The plot if found, None otherwise
        """
        query = select(Plot).where(
            and_(Plot.id == plot_id, Plot.is_deleted == False)
        ).options(selectinload(Plot.chapters))
        
        result = await self.db.execute(query)
        plot = result.scalar_one_or_none()
        
        if plot:
            return PlotResponse.from_orm(plot)
        return None

    async def list_plots(self, campaign_id: UUID) -> List[PlotResponse]:
        """List all plots for a campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            List of plots
        """
        query = select(Plot).where(
            and_(Plot.campaign_id == campaign_id, Plot.is_deleted == False)
        ).options(selectinload(Plot.chapters))
        
        result = await self.db.execute(query)
        plots = result.scalars().all()
        
        return [PlotResponse.from_orm(plot) for plot in plots]

    async def update_plot(
        self, plot_id: UUID, plot_data: PlotUpdate
    ) -> Optional[PlotResponse]:
        """Update a plot.

        Args:
            plot_id: Plot ID
            plot_data: Plot update data

        Returns:
            The updated plot if found, None otherwise
        """
        query = select(Plot).where(
            and_(Plot.id == plot_id, Plot.is_deleted == False)
        )
        result = await self.db.execute(query)
        plot = result.scalar_one_or_none()
        
        if not plot:
            return None

        for key, value in plot_data.dict(exclude_unset=True).items():
            setattr(plot, key, value)
        plot.updated_at = datetime.utcnow()
        
        await self.db.flush()
        await self.db.refresh(plot)
        return PlotResponse.from_orm(plot)

    async def delete_plot(self, plot_id: UUID) -> bool:
        """Soft delete a plot.

        Args:
            plot_id: Plot ID

        Returns:
            True if plot was deleted, False if not found
        """
        query = select(Plot).where(
            and_(Plot.id == plot_id, Plot.is_deleted == False)
        )
        result = await self.db.execute(query)
        plot = result.scalar_one_or_none()
        
        if not plot:
            return False

        plot.is_deleted = True
        plot.deleted_at = datetime.utcnow()
        plot.updated_at = datetime.utcnow()
        
        await self.db.flush()
        return True

    # Story Arc Management
    async def create_story_arc(self, arc_data: StoryArcCreate) -> StoryArcResponse:
        """Create a new story arc.

        Args:
            arc_data: Story arc creation data

        Returns:
            The created story arc
        """
        arc = StoryArc(**arc_data.dict())
        self.db.add(arc)
        await self.db.flush()
        await self.db.refresh(arc)
        return StoryArcResponse.from_orm(arc)

    async def get_story_arc(self, arc_id: UUID) -> Optional[StoryArcResponse]:
        """Get a story arc by ID.

        Args:
            arc_id: Story arc ID

        Returns:
            The story arc if found, None otherwise
        """
        query = select(StoryArc).where(
            and_(StoryArc.id == arc_id, StoryArc.is_deleted == False)
        )
        result = await self.db.execute(query)
        arc = result.scalar_one_or_none()
        
        if arc:
            return StoryArcResponse.from_orm(arc)
        return None

    async def list_story_arcs(self, campaign_id: UUID) -> List[StoryArcResponse]:
        """List all story arcs for a campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            List of story arcs
        """
        query = select(StoryArc).where(
            and_(StoryArc.campaign_id == campaign_id, StoryArc.is_deleted == False)
        ).order_by(StoryArc.arc_number)
        
        result = await self.db.execute(query)
        arcs = result.scalars().all()
        
        return [StoryArcResponse.from_orm(arc) for arc in arcs]

    async def update_story_arc(
        self, arc_id: UUID, arc_data: StoryArcUpdate
    ) -> Optional[StoryArcResponse]:
        """Update a story arc.

        Args:
            arc_id: Story arc ID
            arc_data: Story arc update data

        Returns:
            The updated story arc if found, None otherwise
        """
        query = select(StoryArc).where(
            and_(StoryArc.id == arc_id, StoryArc.is_deleted == False)
        )
        result = await self.db.execute(query)
        arc = result.scalar_one_or_none()
        
        if not arc:
            return None

        for key, value in arc_data.dict(exclude_unset=True).items():
            setattr(arc, key, value)
        arc.updated_at = datetime.utcnow()
        
        await self.db.flush()
        await self.db.refresh(arc)
        return StoryArcResponse.from_orm(arc)

    async def delete_story_arc(self, arc_id: UUID) -> bool:
        """Soft delete a story arc.

        Args:
            arc_id: Story arc ID

        Returns:
            True if arc was deleted, False if not found
        """
        query = select(StoryArc).where(
            and_(StoryArc.id == arc_id, StoryArc.is_deleted == False)
        )
        result = await self.db.execute(query)
        arc = result.scalar_one_or_none()
        
        if not arc:
            return False

        arc.is_deleted = True
        arc.deleted_at = datetime.utcnow()
        arc.updated_at = datetime.utcnow()
        
        await self.db.flush()
        return True

    # NPC Relationship Management
    async def create_npc_relationship(
        self, relationship_data: NPCRelationshipCreate
    ) -> NPCRelationshipResponse:
        """Create a new NPC relationship.

        Args:
            relationship_data: NPC relationship creation data

        Returns:
            The created NPC relationship
        """
        relationship = NPCRelationship(**relationship_data.dict())
        self.db.add(relationship)
        await self.db.flush()
        await self.db.refresh(relationship)
        return NPCRelationshipResponse.from_orm(relationship)

    async def get_npc_relationship(
        self, relationship_id: UUID
    ) -> Optional[NPCRelationshipResponse]:
        """Get an NPC relationship by ID.

        Args:
            relationship_id: NPC relationship ID

        Returns:
            The NPC relationship if found, None otherwise
        """
        query = select(NPCRelationship).where(
            and_(
                NPCRelationship.id == relationship_id,
                NPCRelationship.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        relationship = result.scalar_one_or_none()
        
        if relationship:
            return NPCRelationshipResponse.from_orm(relationship)
        return None

    async def list_npc_relationships(
        self, campaign_id: UUID
    ) -> List[NPCRelationshipResponse]:
        """List all NPC relationships for a campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            List of NPC relationships
        """
        query = select(NPCRelationship).where(
            and_(
                NPCRelationship.campaign_id == campaign_id,
                NPCRelationship.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        relationships = result.scalars().all()
        
        return [
            NPCRelationshipResponse.from_orm(rel) for rel in relationships
        ]

    async def update_npc_relationship(
        self, relationship_id: UUID, relationship_data: NPCRelationshipUpdate
    ) -> Optional[NPCRelationshipResponse]:
        """Update an NPC relationship.

        Args:
            relationship_id: NPC relationship ID
            relationship_data: NPC relationship update data

        Returns:
            The updated NPC relationship if found, None otherwise
        """
        query = select(NPCRelationship).where(
            and_(
                NPCRelationship.id == relationship_id,
                NPCRelationship.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        relationship = result.scalar_one_or_none()
        
        if not relationship:
            return None

        for key, value in relationship_data.dict(exclude_unset=True).items():
            setattr(relationship, key, value)
        relationship.updated_at = datetime.utcnow()
        
        await self.db.flush()
        await self.db.refresh(relationship)
        return NPCRelationshipResponse.from_orm(relationship)

    async def delete_npc_relationship(self, relationship_id: UUID) -> bool:
        """Soft delete an NPC relationship.

        Args:
            relationship_id: NPC relationship ID

        Returns:
            True if relationship was deleted, False if not found
        """
        query = select(NPCRelationship).where(
            and_(
                NPCRelationship.id == relationship_id,
                NPCRelationship.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        relationship = result.scalar_one_or_none()
        
        if not relationship:
            return False

        relationship.is_deleted = True
        relationship.deleted_at = datetime.utcnow()
        relationship.updated_at = datetime.utcnow()
        
        await self.db.flush()
        return True
