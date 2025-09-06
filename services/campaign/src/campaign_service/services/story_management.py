"""Story management service implementation."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.core.exceptions import StoryManagementError
from campaign_service.core.logging import get_logger
from campaign_service.models.campaign import Campaign, Chapter
from campaign_service.models.story import (
    NPCRelationship,
    NPCRelationType,
    Plot,
    PlotChapter,
    PlotState,
    PlotType,
    StoryArc,
    StoryArcType,
)
from campaign_service.repositories.campaign import CampaignRepository
from campaign_service.repositories.story import (
    NPCRelationshipRepository,
    PlotChapterRepository,
    PlotRepository,
    StoryArcRepository,
)

logger = get_logger(__name__)


class StoryManagementService:
    """Service for managing campaign story elements."""

    def __init__(
        self,
        db: AsyncSession,
        campaign_repo: CampaignRepository,
        plot_repo: PlotRepository,
        arc_repo: StoryArcRepository,
        plot_chapter_repo: PlotChapterRepository,
        npc_repo: NPCRelationshipRepository,
        message_hub_client: Any,  # type: ignore
    ) -> None:
        """Initialize service.

        Args:
            db (AsyncSession): Database session
            campaign_repo (CampaignRepository): Campaign repository
            plot_repo (PlotRepository): Plot repository
            arc_repo (StoryArcRepository): Story arc repository
            plot_chapter_repo (PlotChapterRepository): Plot chapter repository
            npc_repo (NPCRelationshipRepository): NPC relationship repository
            message_hub_client (Any): Message hub client
        """
        self.db = db
        self.campaign_repo = campaign_repo
        self.plot_repo = plot_repo
        self.arc_repo = arc_repo
        self.plot_chapter_repo = plot_chapter_repo
        self.npc_repo = npc_repo
        self.message_hub = message_hub_client

    async def create_story_arc(
        self,
        campaign_id: UUID,
        title: str,
        description: str,
        arc_type: StoryArcType,
        sequence_number: Optional[int] = None,
        content: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ) -> StoryArc:
        """Create a new story arc.

        Args:
            campaign_id (UUID): Campaign ID
            title (str): Arc title
            description (str): Arc description
            arc_type (StoryArcType): Arc type
            sequence_number (Optional[int], optional): Arc sequence number. Defaults to None.
            content (Optional[Dict], optional): Additional arc content. Defaults to None.
            metadata (Optional[Dict], optional): Additional metadata. Defaults to None.

        Returns:
            StoryArc: Created story arc

        Raises:
            StoryManagementError: If arc creation fails
        """
        try:
            # Get max sequence number if not provided
            if sequence_number is None:
                existing_arcs = await self.arc_repo.get_by_campaign(campaign_id)
                sequence_number = max([arc.sequence_number for arc in existing_arcs], default=0) + 1

            # Create arc
            arc = await self.arc_repo.create({
                "campaign_id": campaign_id,
                "title": title,
                "description": description,
                "arc_type": arc_type,
                "sequence_number": sequence_number,
                "content": content or {},
                "metadata": metadata or {},
            })

            # Publish event
            await self.message_hub.publish(
                "campaign.story_arc_created",
                {
                    "campaign_id": str(campaign_id),
                    "arc_id": str(arc.id),
                    "type": arc_type.value,
                    "sequence_number": sequence_number,
                },
            )

            return arc

        except Exception as e:
            logger.error("Failed to create story arc", error=str(e))
            raise StoryManagementError(f"Failed to create story arc: {e}")

    async def create_plot(
        self,
        campaign_id: UUID,
        title: str,
        description: str,
        plot_type: PlotType,
        arc_id: Optional[UUID] = None,
        parent_plot_id: Optional[UUID] = None,
        content: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
    ) -> Plot:
        """Create a new plot.

        Args:
            campaign_id (UUID): Campaign ID
            title (str): Plot title
            description (str): Plot description
            plot_type (PlotType): Plot type
            arc_id (Optional[UUID], optional): Story arc ID. Defaults to None.
            parent_plot_id (Optional[UUID], optional): Parent plot ID. Defaults to None.
            content (Optional[Dict], optional): Additional plot content. Defaults to None.
            metadata (Optional[Dict], optional): Additional metadata. Defaults to None.

        Returns:
            Plot: Created plot

        Raises:
            StoryManagementError: If plot creation fails
        """
        try:
            # Verify parent plot if provided
            if parent_plot_id:
                parent_plot = await self.plot_repo.get(parent_plot_id)
                if not parent_plot:
                    raise StoryManagementError(f"Parent plot not found: {parent_plot_id}")

            # Create plot
            plot = await self.plot_repo.create({
                "campaign_id": campaign_id,
                "title": title,
                "description": description,
                "plot_type": plot_type,
                "state": PlotState.PLANNED,
                "arc_id": arc_id,
                "parent_plot_id": parent_plot_id,
                "content": content or {},
                "metadata": metadata or {},
            })

            # Publish event
            await self.message_hub.publish(
                "campaign.plot_created",
                {
                    "campaign_id": str(campaign_id),
                    "plot_id": str(plot.id),
                    "type": plot_type.value,
                    "arc_id": str(arc_id) if arc_id else None,
                    "parent_plot_id": str(parent_plot_id) if parent_plot_id else None,
                },
            )

            return plot

        except Exception as e:
            logger.error("Failed to create plot", error=str(e))
            raise StoryManagementError(f"Failed to create plot: {e}")

    async def add_plot_chapter(
        self,
        plot_id: UUID,
        chapter_id: UUID,
        plot_content: Dict,
        plot_order: Optional[int] = None,
    ) -> PlotChapter:
        """Add a chapter to a plot.

        Args:
            plot_id (UUID): Plot ID
            chapter_id (UUID): Chapter ID
            plot_content (Dict): Plot-specific chapter content
            plot_order (Optional[int], optional): Chapter order in plot. Defaults to None.

        Returns:
            PlotChapter: Created plot chapter association

        Raises:
            StoryManagementError: If chapter addition fails
        """
        try:
            # Get plot and verify it exists
            plot = await self.plot_repo.get(plot_id)
            if not plot:
                raise StoryManagementError(f"Plot not found: {plot_id}")

            # Get maximum plot order if not provided
            if plot_order is None:
                existing_chapters = await self.plot_chapter_repo.get_by_plot(plot_id)
                plot_order = max([ch.plot_order for ch in existing_chapters], default=0) + 1

            # Create plot chapter association
            plot_chapter = await self.plot_chapter_repo.create({
                "plot_id": plot_id,
                "chapter_id": chapter_id,
                "plot_content": plot_content,
                "plot_order": plot_order,
            })

            # Publish event
            await self.message_hub.publish(
                "campaign.plot_chapter_added",
                {
                    "campaign_id": str(plot.campaign_id),
                    "plot_id": str(plot_id),
                    "chapter_id": str(chapter_id),
                    "plot_order": plot_order,
                },
            )

            return plot_chapter

        except Exception as e:
            logger.error("Failed to add plot chapter", error=str(e))
            raise StoryManagementError(f"Failed to add plot chapter: {e}")

    async def update_plot_state(
        self,
        plot_id: UUID,
        new_state: PlotState,
        reason: str,
        metadata: Optional[Dict] = None,
    ) -> Plot:
        """Update plot state.

        Args:
            plot_id (UUID): Plot ID
            new_state (PlotState): New plot state
            reason (str): State change reason
            metadata (Optional[Dict], optional): Additional metadata. Defaults to None.

        Returns:
            Plot: Updated plot

        Raises:
            StoryManagementError: If state update fails
        """
        try:
            # Get plot and verify it exists
            plot = await self.plot_repo.get(plot_id)
            if not plot:
                raise StoryManagementError(f"Plot not found: {plot_id}")

            # Update plot state
            updated_plot = await self.plot_repo.update(
                plot_id,
                {
                    "state": new_state,
                    "metadata": {
                        **plot.metadata,
                        "state_history": [
                            *plot.metadata.get("state_history", []),
                            {
                                "from_state": plot.state,
                                "to_state": new_state,
                                "reason": reason,
                                "timestamp": datetime.utcnow().isoformat(),
                                **(metadata or {}),
                            },
                        ],
                    },
                },
            )
            if not updated_plot:
                raise StoryManagementError(f"Failed to update plot state: {plot_id}")

            # Publish event
            await self.message_hub.publish(
                "campaign.plot_state_changed",
                {
                    "campaign_id": str(plot.campaign_id),
                    "plot_id": str(plot_id),
                    "from_state": plot.state,
                    "to_state": new_state.value,
                    "reason": reason,
                },
            )

            return updated_plot

        except Exception as e:
            logger.error("Failed to update plot state", error=str(e))
            raise StoryManagementError(f"Failed to update plot state: {e}")

    async def create_npc_relationship(
        self,
        campaign_id: UUID,
        npc_id: UUID,
        relation_type: NPCRelationType,
        description: str,
        plot_id: Optional[UUID] = None,
        arc_id: Optional[UUID] = None,
        metadata: Optional[Dict] = None,
    ) -> NPCRelationship:
        """Create NPC relationship.

        Args:
            campaign_id (UUID): Campaign ID
            npc_id (UUID): NPC ID
            relation_type (NPCRelationType): Relationship type
            description (str): Relationship description
            plot_id (Optional[UUID], optional): Related plot ID. Defaults to None.
            arc_id (Optional[UUID], optional): Related arc ID. Defaults to None.
            metadata (Optional[Dict], optional): Additional metadata. Defaults to None.

        Returns:
            NPCRelationship: Created NPC relationship

        Raises:
            StoryManagementError: If relationship creation fails
        """
        try:
            # Create relationship
            relationship = await self.npc_repo.create({
                "campaign_id": campaign_id,
                "npc_id": npc_id,
                "relation_type": relation_type,
                "description": description,
                "plot_id": plot_id,
                "arc_id": arc_id,
                "metadata": metadata or {},
            })

            # Publish event
            await self.message_hub.publish(
                "campaign.npc_relationship_created",
                {
                    "campaign_id": str(campaign_id),
                    "npc_id": str(npc_id),
                    "relationship_id": str(relationship.id),
                    "type": relation_type.value,
                    "plot_id": str(plot_id) if plot_id else None,
                    "arc_id": str(arc_id) if arc_id else None,
                },
            )

            return relationship

        except Exception as e:
            logger.error("Failed to create NPC relationship", error=str(e))
            raise StoryManagementError(f"Failed to create NPC relationship: {e}")

    async def get_campaign_story_structure(
        self,
        campaign_id: UUID,
    ) -> Dict:
        """Get complete story structure for a campaign.

        Args:
            campaign_id (UUID): Campaign ID

        Returns:
            Dict: Story structure containing arcs, plots, and relationships

        Raises:
            StoryManagementError: If retrieval fails
        """
        try:
            # Get all story elements
            arcs = await self.arc_repo.get_by_campaign(campaign_id)
            plots = await self.plot_repo.get_by_campaign(campaign_id)
            relationships = await self.npc_repo.get_by_campaign(campaign_id)

            # Build story structure
            story_structure = {
                "campaign_id": str(campaign_id),
                "arcs": [
                    {
                        "id": str(arc.id),
                        "title": arc.title,
                        "type": arc.arc_type.value,
                        "sequence_number": arc.sequence_number,
                        "plots": [
                            {
                                "id": str(plot.id),
                                "title": plot.title,
                                "type": plot.plot_type.value,
                                "state": plot.state.value,
                                "subplots": [
                                    {
                                        "id": str(subplot.id),
                                        "title": subplot.title,
                                        "type": subplot.plot_type.value,
                                        "state": subplot.state.value,
                                    }
                                    for subplot in plots
                                    if subplot.parent_plot_id == plot.id
                                ],
                                "relationships": [
                                    {
                                        "npc_id": str(rel.npc_id),
                                        "type": rel.relation_type.value,
                                        "description": rel.description,
                                    }
                                    for rel in relationships
                                    if rel.plot_id == plot.id
                                ],
                            }
                            for plot in plots
                            if plot.arc_id == arc.id and not plot.parent_plot_id
                        ],
                        "relationships": [
                            {
                                "npc_id": str(rel.npc_id),
                                "type": rel.relation_type.value,
                                "description": rel.description,
                            }
                            for rel in relationships
                            if rel.arc_id == arc.id
                        ],
                    }
                    for arc in sorted(arcs, key=lambda x: x.sequence_number)
                ],
                # Include top-level plots (not part of any arc)
                "standalone_plots": [
                    {
                        "id": str(plot.id),
                        "title": plot.title,
                        "type": plot.plot_type.value,
                        "state": plot.state.value,
                        "subplots": [
                            {
                                "id": str(subplot.id),
                                "title": subplot.title,
                                "type": subplot.plot_type.value,
                                "state": subplot.state.value,
                            }
                            for subplot in plots
                            if subplot.parent_plot_id == plot.id
                        ],
                        "relationships": [
                            {
                                "npc_id": str(rel.npc_id),
                                "type": rel.relation_type.value,
                                "description": rel.description,
                            }
                            for rel in relationships
                            if rel.plot_id == plot.id
                        ],
                    }
                    for plot in plots
                    if not plot.arc_id and not plot.parent_plot_id
                ],
            }

            return story_structure

        except Exception as e:
            logger.error("Failed to get campaign story structure", error=str(e))
            raise StoryManagementError(f"Failed to get campaign story structure: {e}")
