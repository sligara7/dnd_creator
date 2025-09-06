"""Evolution router."""
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4, BaseModel, Field

from character_service.core.exceptions import (
    ValidationError,
    EvolutionError,
    StateError,
)
from character_service.domain.evolution import (
    EventType,
    MilestoneType,
    AchievementCategory,
    Difficulty,
)
from character_service.services.evolution import EvolutionService
from character_service.schemas.evolution import (
    CharacterEventCreate,
    CharacterEventResponse,
    MilestoneCreate,
    MilestoneResponse,
    AchievementCreate,
    AchievementResponse,
    ProgressResponse,
    SnapshotResponse,
)
from character_service.core.dependencies import (
    get_evolution_service,
)

router = APIRouter()


@router.get(
    "/characters/{character_id}/events",
    response_model=List[CharacterEventResponse],
    tags=["evolution"],
)
async def get_character_events(
    character_id: UUID4,
    event_type: Optional[EventType] = None,
    processed: Optional[bool] = None,
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    """Get character events."""
    try:
        events = await evolution_service.get_character_events(
            character_id=character_id,
            event_type=event_type,
            processed=processed,
        )
        return [CharacterEventResponse.from_orm(event) for event in events]
    except EvolutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/events",
    response_model=CharacterEventResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["evolution"],
)
async def create_event(
    character_id: UUID4,
    event: CharacterEventCreate,
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    """Create a character event."""
    try:
        created_event = await evolution_service.create_event(
            character_id=character_id,
            event_type=event.event_type,
            title=event.title,
            description=event.description,
            impact=event.impact,
            campaign_event_id=event.campaign_event_id,
            metadata=event.metadata,
        )
        return CharacterEventResponse.from_orm(created_event)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except EvolutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/characters/{character_id}/milestones",
    response_model=List[MilestoneResponse],
    tags=["evolution"],
)
async def get_milestones(
    character_id: UUID4,
    milestone_type: Optional[MilestoneType] = None,
    completed: Optional[bool] = None,
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    """Get character milestones."""
    try:
        milestones = await evolution_service.get_character_milestones(
            character_id=character_id,
            milestone_type=milestone_type,
            completed=completed,
        )
        return [MilestoneResponse.from_orm(milestone) for milestone in milestones]
    except EvolutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/milestones",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["evolution"],
)
async def create_milestone(
    character_id: UUID4,
    milestone: MilestoneCreate,
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    """Create a character milestone."""
    try:
        created_milestone = await evolution_service.create_milestone(
            character_id=character_id,
            milestone_type=milestone.milestone_type,
            title=milestone.title,
            description=milestone.description,
            requirements=milestone.requirements,
            rewards=milestone.rewards,
            campaign_milestone_id=milestone.campaign_milestone_id,
            metadata=milestone.metadata,
        )
        return MilestoneResponse.from_orm(created_milestone)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except EvolutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/milestones/{milestone_id}/complete",
    response_model=MilestoneResponse,
    tags=["evolution"],
)
async def complete_milestone(
    character_id: UUID4,
    milestone_id: UUID4,
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    """Complete a character milestone."""
    try:
        milestone = await evolution_service.complete_milestone(
            character_id=character_id,
            milestone_id=milestone_id,
        )
        return MilestoneResponse.from_orm(milestone)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except StateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except EvolutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/characters/{character_id}/progress",
    response_model=ProgressResponse,
    tags=["evolution"],
)
async def get_character_progress(
    character_id: UUID4,
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    """Get character progress."""
    try:
        progress = await evolution_service.get_character_progress(
            character_id=character_id,
        )
        return ProgressResponse.from_orm(progress)
    except EvolutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/xp",
    response_model=ProgressResponse,
    tags=["evolution"],
)
async def add_xp(
    character_id: UUID4,
    amount: int = Field(..., gt=0),
    source: str = Field(..., min_length=1),
    metadata: Optional[Dict] = None,
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    """Add XP to character."""
    try:
        progress = await evolution_service.add_xp(
            character_id=character_id,
            amount=amount,
            source=source,
            metadata=metadata,
        )
        return ProgressResponse.from_orm(progress)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except EvolutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/characters/{character_id}/snapshots",
    response_model=List[SnapshotResponse],
    tags=["evolution"],
)
async def get_snapshots(
    character_id: UUID4,
    event_id: Optional[UUID4] = None,
    snapshot_type: Optional[str] = None,
    limit: Optional[int] = 10,
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    """Get character progress snapshots."""
    try:
        snapshots = await evolution_service.get_character_snapshots(
            character_id=character_id,
            event_id=event_id,
            snapshot_type=snapshot_type,
            limit=limit,
        )
        return [SnapshotResponse.from_orm(snapshot) for snapshot in snapshots]
    except EvolutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/characters/{character_id}/achievements",
    response_model=List[AchievementResponse],
    tags=["evolution"],
)
async def get_achievements(
    character_id: UUID4,
    category: Optional[AchievementCategory] = None,
    completed: Optional[bool] = None,
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    """Get character achievements."""
    try:
        achievements = await evolution_service.get_character_achievements(
            character_id=character_id,
            category=category,
            completed=completed,
        )
        return [AchievementResponse.from_orm(achievement) for achievement in achievements]
    except EvolutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/achievements",
    response_model=AchievementResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["evolution"],
)
async def create_achievement(
    character_id: UUID4,
    achievement: AchievementCreate,
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    """Create a character achievement."""
    try:
        created_achievement = await evolution_service.create_achievement(
            character_id=character_id,
            title=achievement.title,
            description=achievement.description,
            category=achievement.category,
            difficulty=achievement.difficulty,
            requirements=achievement.requirements,
            rewards=achievement.rewards,
            points=achievement.points,
            campaign_achievement_id=achievement.campaign_achievement_id,
            metadata=achievement.metadata,
        )
        return AchievementResponse.from_orm(created_achievement)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except EvolutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/achievements/{achievement_id}/complete",
    response_model=AchievementResponse,
    tags=["evolution"],
)
async def complete_achievement(
    character_id: UUID4,
    achievement_id: UUID4,
    evolution_service: EvolutionService = Depends(get_evolution_service),
):
    """Complete a character achievement."""
    try:
        achievement = await evolution_service.complete_achievement(
            character_id=character_id,
            achievement_id=achievement_id,
        )
        return AchievementResponse.from_orm(achievement)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except StateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except EvolutionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
