"""Session notes API router."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ...core.db import get_db
from ...core.logging import get_logger
from ...services.session_service import SessionService
from ..schemas.session_notes import (
    CreateSessionNoteRequest,
    UpdateSessionNoteRequest,
    ProcessNoteFeedbackRequest,
    SessionNoteSummary,
    SessionNoteDetail,
    FeedbackResult,
)
from ..dependencies import get_session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])
logger = get_logger(__name__)


@router.post(
    "/notes",
    response_model=SessionNoteDetail,
    status_code=status.HTTP_201_CREATED
)
async def create_session_note(
    request: CreateSessionNoteRequest,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
) -> SessionNoteDetail:
    """Create a new session note."""
    try:
        note = await session_service.create_note(request)
        return SessionNoteDetail.from_orm(note)
    except Exception as e:
        logger.error("Failed to create session note", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/notes",
    response_model=List[SessionNoteSummary]
)
async def list_session_notes(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
    chapter_id: Optional[UUID] = None,
    status: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> List[SessionNoteSummary]:
    """List session notes with optional filters."""
    try:
        notes = await session_service.list_notes(
            campaign_id,
            chapter_id,
            status,
            limit,
            offset
        )
        return [SessionNoteSummary.from_orm(n) for n in notes]
    except Exception as e:
        logger.error("Failed to list session notes", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list session notes"
        )


@router.get(
    "/notes/{note_id}",
    response_model=SessionNoteDetail
)
async def get_session_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
) -> SessionNoteDetail:
    """Get session note details."""
    try:
        note = await session_service.get_note(note_id)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session note not found"
            )
        return SessionNoteDetail.from_orm(note)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get session note", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session note"
        )


@router.patch(
    "/notes/{note_id}",
    response_model=SessionNoteDetail
)
async def update_session_note(
    note_id: UUID,
    request: UpdateSessionNoteRequest,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
) -> SessionNoteDetail:
    """Update session note."""
    try:
        note = await session_service.update_note(note_id, request)
        return SessionNoteDetail.from_orm(note)
    except Exception as e:
        logger.error("Failed to update session note", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_session_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
) -> Response:
    """Delete a session note."""
    try:
        await session_service.delete_note(note_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error("Failed to delete session note", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/notes/{note_id}/process",
    response_model=FeedbackResult
)
async def process_note_feedback(
    note_id: UUID,
    request: ProcessNoteFeedbackRequest,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
) -> FeedbackResult:
    """Process feedback from session note."""
    try:
        result = await session_service.process_feedback(note_id, request)
        return FeedbackResult(
            campaign_updates=result.get("campaign"),
            character_updates=result.get("characters", []),
            npc_updates=result.get("npcs", []),
            processing_notes=result.get("notes", [])
        )
    except Exception as e:
        logger.error("Failed to process feedback", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/scene-setter",
    response_model=SceneSetterResponse,
    summary="Generate narrative scene description for DMs",
    description="Generate rich narrative descriptions and DM notes for a campaign, chapter or encounter"
)
async def generate_scene_setter(
    request: SceneSetterRequest,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
) -> SceneSetterResponse:
    """Generate a narrative scene setter for DMs.

    This endpoint provides DMs with rich narrative descriptions and important details
    about the campaign, chapter, or specific encounter, including:
    - Current state of the campaign world
    - Chapter-specific context and plot points
    - Encounter details (enemies, NPCs, environment)
    - Puzzles, clues, and other interactive elements
    - Key information needed to run the session effectively
    """
    try:
        result = await session_service.generate_scene_setter(
            campaign_id=request.campaign_id,
            chapter_id=request.chapter_id,
            encounter_id=request.encounter_id,
            custom_rules=request.custom_rules
        )
        return SceneSetterResponse(**result)
    except Exception as e:
        logger.error("Failed to generate scene setter", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/notes/{note_id}/update",
    response_model=CampaignUpdateResponse,
    summary="Update campaign/chapter from session notes",
    description="Process session notes using LLM to update campaign and chapter state"
)
async def update_campaign_from_note(
    note_id: UUID,
    request: CampaignUpdateRequest,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
) -> CampaignUpdateResponse:
    """Update campaign and chapter based on session notes.

    This endpoint processes the session notes using LLM analysis to update:
    - Campaign progress and state
    - Chapter developments
    - World state changes
    - Quest and objective updates
    """
    try:
        result = await session_service.update_campaign_from_notes(
            note_id=note_id,
            update_type=request.update_type,
            custom_rules=request.custom_rules
        )
        return CampaignUpdateResponse(**result)
    except Exception as e:
        logger.error("Failed to update from notes", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/notes/{note_id}/character/{character_id}/history",
    response_model=List[Dict]
)
async def get_character_session_history(
    note_id: UUID,
    character_id: str,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends(get_session_service),
    limit: int = Query(default=10, ge=1, le=50),
) -> List[Dict]:
    """Get character's session history."""
    try:
        history = await session_service.get_character_history(
            note_id,
            character_id,
            limit
        )
        return history
    except Exception as e:
        logger.error("Failed to get character history", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
