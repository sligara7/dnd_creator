"""Router for story management endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db, get_story_service
from ..models.api.story import (ChapterCreate, ChapterResponse, ChapterUpdate,
                            NPCRelationshipCreate, NPCRelationshipResponse,
                            NPCRelationshipUpdate, PlotCreate, PlotResponse,
                            PlotUpdate, StoryArcCreate, StoryArcResponse,
                            StoryArcUpdate)
from ..services.story import StoryService

router = APIRouter(prefix="/api/v2/campaigns", tags=["story"])


@router.post("/{campaign_id}/plots", response_model=PlotResponse)
async def create_plot(
    campaign_id: UUID,
    plot: PlotCreate,
    story_service: StoryService = Depends(get_story_service),
) -> PlotResponse:
    """Create a new plot in the campaign."""
    if plot.campaign_id != campaign_id:
        raise HTTPException(
            status_code=400,
            detail="Campaign ID in path must match campaign ID in request body",
        )
    return await story_service.create_plot(plot)


@router.get("/{campaign_id}/plots", response_model=List[PlotResponse])
async def list_plots(
    campaign_id: UUID,
    story_service: StoryService = Depends(get_story_service),
) -> List[PlotResponse]:
    """List all plots in the campaign."""
    return await story_service.list_plots(campaign_id)


@router.get("/{campaign_id}/plots/{plot_id}", response_model=PlotResponse)
async def get_plot(
    campaign_id: UUID,
    plot_id: UUID,
    story_service: StoryService = Depends(get_story_service),
) -> PlotResponse:
    """Get a specific plot by ID."""
    plot = await story_service.get_plot(plot_id)
    if plot is None or plot.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Plot not found")
    return plot


@router.put("/{campaign_id}/plots/{plot_id}", response_model=PlotResponse)
async def update_plot(
    campaign_id: UUID,
    plot_id: UUID,
    plot_update: PlotUpdate,
    story_service: StoryService = Depends(get_story_service),
) -> PlotResponse:
    """Update a specific plot."""
    plot = await story_service.update_plot(plot_id, plot_update)
    if plot is None or plot.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Plot not found")
    return plot


@router.delete("/{campaign_id}/plots/{plot_id}", status_code=204)
async def delete_plot(
    campaign_id: UUID,
    plot_id: UUID,
    story_service: StoryService = Depends(get_story_service),
) -> None:
    """Delete a specific plot."""
    plot = await story_service.get_plot(plot_id)
    if plot is None or plot.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Plot not found")
    await story_service.delete_plot(plot_id)


@router.post("/{campaign_id}/arcs", response_model=StoryArcResponse)
async def create_story_arc(
    campaign_id: UUID,
    arc: StoryArcCreate,
    story_service: StoryService = Depends(get_story_service),
) -> StoryArcResponse:
    """Create a new story arc in the campaign."""
    if arc.campaign_id != campaign_id:
        raise HTTPException(
            status_code=400,
            detail="Campaign ID in path must match campaign ID in request body",
        )
    return await story_service.create_story_arc(arc)


@router.get("/{campaign_id}/arcs", response_model=List[StoryArcResponse])
async def list_story_arcs(
    campaign_id: UUID,
    story_service: StoryService = Depends(get_story_service),
) -> List[StoryArcResponse]:
    """List all story arcs in the campaign."""
    return await story_service.list_story_arcs(campaign_id)


@router.get("/{campaign_id}/arcs/{arc_id}", response_model=StoryArcResponse)
async def get_story_arc(
    campaign_id: UUID,
    arc_id: UUID,
    story_service: StoryService = Depends(get_story_service),
) -> StoryArcResponse:
    """Get a specific story arc by ID."""
    arc = await story_service.get_story_arc(arc_id)
    if arc is None or arc.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Story arc not found")
    return arc


@router.put("/{campaign_id}/arcs/{arc_id}", response_model=StoryArcResponse)
async def update_story_arc(
    campaign_id: UUID,
    arc_id: UUID,
    arc_update: StoryArcUpdate,
    story_service: StoryService = Depends(get_story_service),
) -> StoryArcResponse:
    """Update a specific story arc."""
    arc = await story_service.update_story_arc(arc_id, arc_update)
    if arc is None or arc.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Story arc not found")
    return arc


@router.delete("/{campaign_id}/arcs/{arc_id}", status_code=204)
async def delete_story_arc(
    campaign_id: UUID,
    arc_id: UUID,
    story_service: StoryService = Depends(get_story_service),
) -> None:
    """Delete a specific story arc."""
    arc = await story_service.get_story_arc(arc_id)
    if arc is None or arc.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Story arc not found")
    await story_service.delete_story_arc(arc_id)


@router.post("/{campaign_id}/relationships", response_model=NPCRelationshipResponse)
async def create_npc_relationship(
    campaign_id: UUID,
    relationship: NPCRelationshipCreate,
    story_service: StoryService = Depends(get_story_service),
) -> NPCRelationshipResponse:
    """Create a new NPC relationship in the campaign."""
    if relationship.campaign_id != campaign_id:
        raise HTTPException(
            status_code=400,
            detail="Campaign ID in path must match campaign ID in request body",
        )
    return await story_service.create_npc_relationship(relationship)


@router.get("/{campaign_id}/relationships", response_model=List[NPCRelationshipResponse])
async def list_npc_relationships(
    campaign_id: UUID,
    story_service: StoryService = Depends(get_story_service),
) -> List[NPCRelationshipResponse]:
    """List all NPC relationships in the campaign."""
    return await story_service.list_npc_relationships(campaign_id)


@router.get(
    "/{campaign_id}/relationships/{relationship_id}",
    response_model=NPCRelationshipResponse,
)
async def get_npc_relationship(
    campaign_id: UUID,
    relationship_id: UUID,
    story_service: StoryService = Depends(get_story_service),
) -> NPCRelationshipResponse:
    """Get a specific NPC relationship by ID."""
    relationship = await story_service.get_npc_relationship(relationship_id)
    if relationship is None or relationship.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="NPC relationship not found")
    return relationship


@router.put(
    "/{campaign_id}/relationships/{relationship_id}",
    response_model=NPCRelationshipResponse,
)
async def update_npc_relationship(
    campaign_id: UUID,
    relationship_id: UUID,
    relationship_update: NPCRelationshipUpdate,
    story_service: StoryService = Depends(get_story_service),
) -> NPCRelationshipResponse:
    """Update a specific NPC relationship."""
    relationship = await story_service.update_npc_relationship(
        relationship_id, relationship_update
    )
    if relationship is None or relationship.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="NPC relationship not found")
    return relationship


@router.delete("/{campaign_id}/relationships/{relationship_id}", status_code=204)
async def delete_npc_relationship(
    campaign_id: UUID,
    relationship_id: UUID,
    story_service: StoryService = Depends(get_story_service),
) -> None:
    """Delete a specific NPC relationship."""
    relationship = await story_service.get_npc_relationship(relationship_id)
    if relationship is None or relationship.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="NPC relationship not found")
    await story_service.delete_npc_relationship(relationship_id)


@router.post("/{campaign_id}/chapters", response_model=ChapterResponse)
async def create_chapter(
    campaign_id: UUID,
    chapter: ChapterCreate,
    story_service: StoryService = Depends(get_story_service),
) -> ChapterResponse:
    """Create a new chapter in the campaign."""
    if chapter.campaign_id != campaign_id:
        raise HTTPException(
            status_code=400,
            detail="Campaign ID in path must match campaign ID in request body",
        )
    return await story_service.create_chapter(chapter)


@router.get("/{campaign_id}/chapters", response_model=List[ChapterResponse])
async def list_chapters(
    campaign_id: UUID,
    story_service: StoryService = Depends(get_story_service),
) -> List[ChapterResponse]:
    """List all chapters in the campaign."""
    return await story_service.list_chapters(campaign_id)


@router.get("/{campaign_id}/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    campaign_id: UUID,
    chapter_id: UUID,
    story_service: StoryService = Depends(get_story_service),
) -> ChapterResponse:
    """Get a specific chapter by ID."""
    chapter = await story_service.get_chapter(chapter_id)
    if chapter is None or chapter.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.put("/{campaign_id}/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    campaign_id: UUID,
    chapter_id: UUID,
    chapter_update: ChapterUpdate,
    story_service: StoryService = Depends(get_story_service),
) -> ChapterResponse:
    """Update a specific chapter."""
    chapter = await story_service.update_chapter(chapter_id, chapter_update)
    if chapter is None or chapter.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.delete("/{campaign_id}/chapters/{chapter_id}", status_code=204)
async def delete_chapter(
    campaign_id: UUID,
    chapter_id: UUID,
    story_service: StoryService = Depends(get_story_service),
) -> None:
    """Delete a specific chapter."""
    chapter = await story_service.get_chapter(chapter_id)
    if chapter is None or chapter.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Chapter not found")
    await story_service.delete_chapter(chapter_id)
