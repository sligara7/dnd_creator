"""Router for character progress and events."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.api.v2.schemas.progress import (
    AddAchievementRequest,
    AddExperienceRequest,
    AddExperienceResponse,
    AddMilestoneRequest,
    CharacterProgressResponse,
    CreateEventRequest,
    EventImpactResponse,
    EventResponse,
)
from character_service.core.exceptions import (
    CharacterNotFoundError,
    EventApplicationError,
    EventNotFoundError,
    ValidationError,
)
from character_service.domain.event import EventImpactService
from character_service.domain.progress import ProgressTrackingService
from character_service.infrastructure.repositories.character import CharacterRepository
from character_service.infrastructure.repositories.event import (
    CampaignEventRepository, EventImpactRepository)

router = APIRouter()


@router.post(
    "/{character_id}/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new campaign event",
    description="Create a new campaign event for a character and calculate its impacts.",
)
async def create_event(
    character_id: UUID,
    request: CreateEventRequest,
    event_service: EventImpactService = Depends(),
) -> EventResponse:
    """Create a new campaign event."""
    try:
        event = await event_service.create_event(
            character_id=character_id,
            event_type=request.event_type,
            event_data=request.event_data,
            impact_type=request.impact_type,
            impact_magnitude=request.impact_magnitude,
            journal_entry_id=request.journal_entry_id,
        )
        return EventResponse.from_orm(event)
    except CharacterNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.post(
    "/{character_id}/events/{event_id}/apply",
    response_model=List[EventImpactResponse],
    summary="Apply a campaign event",
    description="Apply a campaign event and its impacts to a character.",
)
async def apply_event(
    character_id: UUID,
    event_id: UUID,
    event_service: EventImpactService = Depends(),
) -> List[EventImpactResponse]:
    """Apply a campaign event."""
    try:
        impacts = await event_service.apply_event(event_id)
        return [EventImpactResponse.from_orm(impact) for impact in impacts]
    except EventNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except EventApplicationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.delete(
    "/{character_id}/events/{event_id}",
    response_model=List[EventImpactResponse],
    summary="Revert a campaign event",
    description="Revert all impacts of a campaign event on a character.",
)
async def revert_event(
    character_id: UUID,
    event_id: UUID,
    event_service: EventImpactService = Depends(),
) -> List[EventImpactResponse]:
    """Revert a campaign event."""
    try:
        impacts = await event_service.revert_event(event_id)
        return [EventImpactResponse.from_orm(impact) for impact in impacts]
    except EventNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{character_id}/history",
    response_model=List[EventResponse],
    summary="Get character event history",
    description="Get the history of campaign events for a character.",
)
async def get_character_events(
    character_id: UUID,
    include_deleted: bool = False,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    event_service: EventImpactService = Depends(),
) -> List[EventResponse]:
    """Get character event history."""
    try:
        events = await event_service.get_character_events(
            character_id,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
        )
        return [EventResponse.from_orm(event) for event in events]
    except CharacterNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/{character_id}/progress/experience",
    response_model=AddExperienceResponse,
    summary="Add experience points",
    description="Add experience points to a character, potentially triggering a level up.",
)
async def add_experience(
    character_id: UUID,
    request: AddExperienceRequest,
    progress_service: ProgressTrackingService = Depends(),
) -> AddExperienceResponse:
    """Add experience points."""
    try:
        xp, leveled_up, level_data = await progress_service.add_experience(
            character_id,
            request.amount,
            request.source,
            request.reason,
        )
        return AddExperienceResponse(
            total_experience=xp,
            leveled_up=leveled_up,
            level_data=level_data,
        )
    except CharacterNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.post(
    "/{character_id}/progress/milestones",
    response_model=CharacterProgressResponse,
    summary="Add milestone",
    description="Add a milestone to a character's progress.",
)
async def add_milestone(
    character_id: UUID,
    request: AddMilestoneRequest,
    progress_service: ProgressTrackingService = Depends(),
) -> CharacterProgressResponse:
    """Add a milestone."""
    try:
        progress = await progress_service.add_milestone(
            character_id,
            request.title,
            request.description,
            request.milestone_type,
            request.data,
        )
        return CharacterProgressResponse.from_orm(progress)
    except CharacterNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/{character_id}/progress/achievements",
    response_model=CharacterProgressResponse,
    summary="Add achievement",
    description="Add an achievement to a character's progress.",
)
async def add_achievement(
    character_id: UUID,
    request: AddAchievementRequest,
    progress_service: ProgressTrackingService = Depends(),
) -> CharacterProgressResponse:
    """Add an achievement."""
    try:
        progress = await progress_service.add_achievement(
            character_id,
            request.title,
            request.description,
            request.achievement_type,
            request.data,
        )
        return CharacterProgressResponse.from_orm(progress)
    except CharacterNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.get(
    "/{character_id}/progress",
    response_model=CharacterProgressResponse,
    summary="Get character progress",
    description="Get the progress tracking data for a character.",
)
async def get_character_progress(
    character_id: UUID,
    progress_service: ProgressTrackingService = Depends(),
) -> CharacterProgressResponse:
    """Get character progress."""
    try:
        progress = await progress_service.get_character_progress(character_id)
        return CharacterProgressResponse.from_orm(progress)
    except CharacterNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
