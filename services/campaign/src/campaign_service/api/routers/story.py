"""Story management API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from campaign_service.core.exceptions import (
    CampaignNotFoundError,
    StoryManagementError,
    ValidationError,
)
from campaign_service.core.logging import get_logger
from campaign_service.models.story import PlotType, StoryArcType
from campaign_service.schemas.story import (
    NPCRelationshipCreate,
    NPCRelationshipList,
    NPCRelationshipRead,
    PlotChapterCreate,
    PlotChapterRead,
    PlotCreate,
    PlotList,
    PlotRead,
    PlotStateUpdate,
    StoryArcCreate,
    StoryArcList,
    StoryArcRead,
    StoryStructureRead,
)
from campaign_service.services.dependencies import get_story_management
from campaign_service.services.story_management import StoryManagementService

router = APIRouter(tags=["story-management"])
logger = get_logger(__name__)


@router.post(
    "/campaigns/{campaign_id}/arcs",
    response_model=StoryArcRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_story_arc(
    campaign_id: UUID,
    request: StoryArcCreate,
    story_management: StoryManagementService = Depends(get_story_management),
) -> StoryArcRead:
    """Create a new story arc.

    Args:
        campaign_id (UUID): Campaign ID
        request (StoryArcCreate): Arc creation request
        story_management (StoryManagementService): Story management service

    Returns:
        StoryArcRead: Created story arc

    Raises:
        HTTPException: If creation fails
    """
    try:
        arc = await story_management.create_story_arc(
            campaign_id=campaign_id,
            title=request.title,
            description=request.description,
            arc_type=request.arc_type,
            sequence_number=request.sequence_number,
            content=request.content,
            metadata=request.metadata,
        )
        return StoryArcRead.from_orm(arc)

    except ValidationError as e:
        logger.warning("Story arc validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except StoryManagementError as e:
        logger.error("Story arc creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Story arc creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create story arc",
        )


@router.get("/campaigns/{campaign_id}/arcs", response_model=StoryArcList)
async def list_story_arcs(
    campaign_id: UUID,
    story_management: StoryManagementService = Depends(get_story_management),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    arc_type: Optional[StoryArcType] = None,
) -> StoryArcList:
    """List story arcs.

    Args:
        campaign_id (UUID): Campaign ID
        story_management (StoryManagementService): Story management service
        skip (int): Number of records to skip
        limit (int): Maximum number of records
        arc_type (Optional[StoryArcType], optional): Filter by arc type. Defaults to None.

    Returns:
        StoryArcList: List of story arcs

    Raises:
        HTTPException: If listing fails
    """
    try:
        arcs = await story_management.arc_repo.get_by_campaign(
            campaign_id=campaign_id,
            skip=skip,
            limit=limit,
        )
        total = len(arcs)  # TODO: Improve with count query

        return StoryArcList(
            items=[StoryArcRead.from_orm(a) for a in arcs],
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.error("Failed to list story arcs", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list story arcs",
        )


@router.post(
    "/campaigns/{campaign_id}/plots",
    response_model=PlotRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_plot(
    campaign_id: UUID,
    request: PlotCreate,
    story_management: StoryManagementService = Depends(get_story_management),
) -> PlotRead:
    """Create a new plot.

    Args:
        campaign_id (UUID): Campaign ID
        request (PlotCreate): Plot creation request
        story_management (StoryManagementService): Story management service

    Returns:
        PlotRead: Created plot

    Raises:
        HTTPException: If creation fails
    """
    try:
        plot = await story_management.create_plot(
            campaign_id=campaign_id,
            title=request.title,
            description=request.description,
            plot_type=request.plot_type,
            arc_id=request.arc_id,
            parent_plot_id=request.parent_plot_id,
            content=request.content,
            metadata=request.metadata,
        )
        return PlotRead.from_orm(plot)

    except ValidationError as e:
        logger.warning("Plot validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except StoryManagementError as e:
        logger.error("Plot creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Plot creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create plot",
        )


@router.get("/campaigns/{campaign_id}/plots", response_model=PlotList)
async def list_plots(
    campaign_id: UUID,
    story_management: StoryManagementService = Depends(get_story_management),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    plot_type: Optional[PlotType] = None,
    arc_id: Optional[UUID] = None,
) -> PlotList:
    """List plots.

    Args:
        campaign_id (UUID): Campaign ID
        story_management (StoryManagementService): Story management service
        skip (int): Number of records to skip
        limit (int): Maximum number of records
        plot_type (Optional[PlotType], optional): Filter by plot type. Defaults to None.
        arc_id (Optional[UUID], optional): Filter by story arc. Defaults to None.

    Returns:
        PlotList: List of plots

    Raises:
        HTTPException: If listing fails
    """
    try:
        if arc_id:
            plots = await story_management.plot_repo.get_by_arc(
                arc_id=arc_id,
                skip=skip,
                limit=limit,
            )
        else:
            plots = await story_management.plot_repo.get_by_campaign(
                campaign_id=campaign_id,
                skip=skip,
                limit=limit,
            )
        total = len(plots)  # TODO: Improve with count query

        return PlotList(
            items=[PlotRead.from_orm(p) for p in plots],
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.error("Failed to list plots", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list plots",
        )


@router.post(
    "/campaigns/{campaign_id}/plots/{plot_id}/chapters/{chapter_id}",
    response_model=PlotChapterRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_plot_chapter(
    campaign_id: UUID,
    plot_id: UUID,
    chapter_id: UUID,
    request: PlotChapterCreate,
    story_management: StoryManagementService = Depends(get_story_management),
) -> PlotChapterRead:
    """Add a chapter to a plot.

    Args:
        campaign_id (UUID): Campaign ID
        plot_id (UUID): Plot ID
        chapter_id (UUID): Chapter ID
        request (PlotChapterCreate): Plot chapter creation request
        story_management (StoryManagementService): Story management service

    Returns:
        PlotChapterRead: Created plot chapter association

    Raises:
        HTTPException: If creation fails
    """
    try:
        plot_chapter = await story_management.add_plot_chapter(
            plot_id=plot_id,
            chapter_id=chapter_id,
            plot_content=request.plot_content,
            plot_order=request.plot_order,
        )
        return PlotChapterRead.from_orm(plot_chapter)

    except ValidationError as e:
        logger.warning("Plot chapter validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except StoryManagementError as e:
        logger.error("Plot chapter creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Plot chapter creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add plot chapter",
        )


@router.put(
    "/campaigns/{campaign_id}/plots/{plot_id}/state",
    response_model=PlotRead,
)
async def update_plot_state(
    campaign_id: UUID,
    plot_id: UUID,
    request: PlotStateUpdate,
    story_management: StoryManagementService = Depends(get_story_management),
) -> PlotRead:
    """Update plot state.

    Args:
        campaign_id (UUID): Campaign ID
        plot_id (UUID): Plot ID
        request (PlotStateUpdate): State update request
        story_management (StoryManagementService): Story management service

    Returns:
        PlotRead: Updated plot

    Raises:
        HTTPException: If update fails
    """
    try:
        updated_plot = await story_management.update_plot_state(
            plot_id=plot_id,
            new_state=request.new_state,
            reason=request.reason,
            metadata=request.metadata,
        )
        return PlotRead.from_orm(updated_plot)

    except StoryManagementError as e:
        logger.error("Plot state update failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Plot state update failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update plot state",
        )


@router.post(
    "/campaigns/{campaign_id}/relationships",
    response_model=NPCRelationshipRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_npc_relationship(
    campaign_id: UUID,
    request: NPCRelationshipCreate,
    story_management: StoryManagementService = Depends(get_story_management),
) -> NPCRelationshipRead:
    """Create NPC relationship.

    Args:
        campaign_id (UUID): Campaign ID
        request (NPCRelationshipCreate): Relationship creation request
        story_management (StoryManagementService): Story management service

    Returns:
        NPCRelationshipRead: Created NPC relationship

    Raises:
        HTTPException: If creation fails
    """
    try:
        relationship = await story_management.create_npc_relationship(
            campaign_id=campaign_id,
            npc_id=request.npc_id,
            relation_type=request.relation_type,
            description=request.description,
            plot_id=request.plot_id,
            arc_id=request.arc_id,
            metadata=request.metadata,
        )
        return NPCRelationshipRead.from_orm(relationship)

    except ValidationError as e:
        logger.warning("NPC relationship validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except StoryManagementError as e:
        logger.error("NPC relationship creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        logger.error("NPC relationship creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create NPC relationship",
        )


@router.get("/campaigns/{campaign_id}/relationships", response_model=NPCRelationshipList)
async def list_npc_relationships(
    campaign_id: UUID,
    story_management: StoryManagementService = Depends(get_story_management),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    plot_id: Optional[UUID] = None,
    arc_id: Optional[UUID] = None,
) -> NPCRelationshipList:
    """List NPC relationships.

    Args:
        campaign_id (UUID): Campaign ID
        story_management (StoryManagementService): Story management service
        skip (int): Number of records to skip
        limit (int): Maximum number of records
        plot_id (Optional[UUID], optional): Filter by plot. Defaults to None.
        arc_id (Optional[UUID], optional): Filter by arc. Defaults to None.

    Returns:
        NPCRelationshipList: List of NPC relationships

    Raises:
        HTTPException: If listing fails
    """
    try:
        if plot_id:
            relationships = await story_management.npc_repo.get_by_plot(
                plot_id=plot_id,
                skip=skip,
                limit=limit,
            )
        elif arc_id:
            relationships = await story_management.npc_repo.get_by_arc(
                arc_id=arc_id,
                skip=skip,
                limit=limit,
            )
        else:
            relationships = await story_management.npc_repo.get_by_campaign(
                campaign_id=campaign_id,
                skip=skip,
                limit=limit,
            )
        total = len(relationships)  # TODO: Improve with count query

        return NPCRelationshipList(
            items=[NPCRelationshipRead.from_orm(r) for r in relationships],
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.error("Failed to list NPC relationships", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list NPC relationships",
        )


@router.get("/campaigns/{campaign_id}/structure", response_model=StoryStructureRead)
async def get_campaign_story_structure(
    campaign_id: UUID,
    story_management: StoryManagementService = Depends(get_story_management),
) -> StoryStructureRead:
    """Get complete story structure for a campaign.

    Args:
        campaign_id (UUID): Campaign ID
        story_management (StoryManagementService): Story management service

    Returns:
        StoryStructureRead: Story structure

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        structure = await story_management.get_campaign_story_structure(campaign_id)
        return StoryStructureRead(**structure)

    except CampaignNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except StoryManagementError as e:
        logger.error("Failed to get story structure", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Failed to get story structure", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get campaign story structure",
        )
