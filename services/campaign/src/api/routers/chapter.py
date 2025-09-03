"""Chapter API router."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ...core.db import get_db
from ...core.logging import get_logger
from ...services.chapter_service import ChapterService
from ...services.chapter_content import ChapterContent
from ...services.version_control import VersionControlService
from ..schemas.chapter import (
    ChapterType,
    ChapterStatus,
    CreateChapterRequest,
    UpdateChapterRequest,
    Chapter,
    ChapterSummary,
    ChapterDetail,
)
from ..dependencies import (
    get_chapter_service,
    get_chapter_content,
    get_version_control,
)

router = APIRouter(prefix="/chapters", tags=["chapters"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=ChapterDetail,
    status_code=status.HTTP_201_CREATED
)
async def create_chapter(
    request: CreateChapterRequest,
    db: Session = Depends(get_db),
    chapter_service: ChapterService = Depends(get_chapter_service),
) -> ChapterDetail:
    """Create a new chapter."""
    try:
        chapter_id, chapter = await chapter_service.create_chapter(
            request.campaign_id,
            request
        )
        return ChapterDetail.from_orm(chapter)
    except Exception as e:
        logger.error("Failed to create chapter", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[ChapterSummary])
async def list_chapters(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    status: Optional[List[ChapterStatus]] = None,
    chapter_type: Optional[ChapterType] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> List[ChapterSummary]:
    """List chapters with optional filters."""
    try:
        query = db.query(Chapter).filter(Chapter.campaign_id == campaign_id)
        if status:
            query = query.filter(Chapter.status.in_(status))
        if chapter_type:
            query = query.filter(Chapter.type == chapter_type)

        chapters = query.offset(offset).limit(limit).all()
        return [ChapterSummary.from_orm(c) for c in chapters]
    except Exception as e:
        logger.error("Failed to list chapters", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list chapters"
        )


@router.get("/{chapter_id}", response_model=ChapterDetail)
async def get_chapter(
    chapter_id: UUID,
    db: Session = Depends(get_db),
    version: Optional[str] = None,
) -> ChapterDetail:
    """Get chapter details."""
    try:
        chapter = db.query(Chapter).get(chapter_id)
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )

        # Get specific version if requested
        if version:
            version_control: VersionControlService = Depends(get_version_control)
            version_data = version_control.get_version(version)
            if not version_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Version not found"
                )
            return ChapterDetail(**version_data.content)

        return ChapterDetail.from_orm(chapter)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get chapter", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chapter"
        )


@router.patch("/{chapter_id}", response_model=ChapterDetail)
async def update_chapter(
    chapter_id: UUID,
    request: UpdateChapterRequest,
    db: Session = Depends(get_db),
    chapter_service: ChapterService = Depends(get_chapter_service),
) -> ChapterDetail:
    """Update chapter details."""
    try:
        chapter = await chapter_service.update_chapter(chapter_id, request)
        return ChapterDetail.from_orm(chapter)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update chapter", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chapter"
        )


@router.delete("/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(
    chapter_id: UUID,
    db: Session = Depends(get_db),
    chapter_service: ChapterService = Depends(get_chapter_service),
) -> Response:
    """Delete a chapter."""
    try:
        await chapter_service.delete_chapter(chapter_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete chapter", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chapter"
        )


@router.post("/{chapter_id}/npcs", status_code=status.HTTP_201_CREATED)
async def add_npc_to_chapter(
    chapter_id: UUID,
    npc_id: UUID,
    role: str,
    significance: str,
    db: Session = Depends(get_db),
    chapter_content: ChapterContent = Depends(get_chapter_content),
    location_id: Optional[UUID] = None,
    interaction_points: Optional[List[str]] = None,
) -> Dict:
    """Add an NPC to a chapter."""
    try:
        npc_assoc = await chapter_content.add_npc_to_chapter(
            chapter_id,
            npc_id,
            role,
            significance,
            location_id,
            interaction_points
        )
        return {
            "success": True,
            "npc_id": str(npc_id),
            "role": role
        }
    except Exception as e:
        logger.error("Failed to add NPC to chapter", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{chapter_id}/npcs/{npc_id}")
async def update_npc_in_chapter(
    chapter_id: UUID,
    npc_id: UUID,
    updates: Dict,
    db: Session = Depends(get_db),
    chapter_content: ChapterContent = Depends(get_chapter_content),
) -> Dict:
    """Update an NPC's role in a chapter."""
    try:
        updated_npc = await chapter_content.update_npc_in_chapter(
            chapter_id,
            npc_id,
            updates
        )
        return {
            "success": True,
            "npc_id": str(npc_id),
            "updates": updates
        }
    except Exception as e:
        logger.error("Failed to update NPC in chapter", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{chapter_id}/npcs/{npc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_npc_from_chapter(
    chapter_id: UUID,
    npc_id: UUID,
    db: Session = Depends(get_db),
    chapter_content: ChapterContent = Depends(get_chapter_content),
) -> Response:
    """Remove an NPC from a chapter."""
    try:
        await chapter_content.remove_npc_from_chapter(chapter_id, npc_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error("Failed to remove NPC from chapter", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{chapter_id}/locations", status_code=status.HTTP_201_CREATED)
async def add_location_to_chapter(
    chapter_id: UUID,
    location_id: UUID,
    role: str,
    significance: str,
    db: Session = Depends(get_db),
    chapter_content: ChapterContent = Depends(get_chapter_content),
    description_override: Optional[str] = None,
    state_changes: Optional[List[Dict]] = None,
) -> Dict:
    """Add a location to a chapter."""
    try:
        location_assoc = await chapter_content.add_location_to_chapter(
            chapter_id,
            location_id,
            role,
            significance,
            description_override,
            state_changes
        )
        return {
            "success": True,
            "location_id": str(location_id),
            "role": role
        }
    except Exception as e:
        logger.error("Failed to add location to chapter", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{chapter_id}/locations/{location_id}")
async def update_location_in_chapter(
    chapter_id: UUID,
    location_id: UUID,
    updates: Dict,
    db: Session = Depends(get_db),
    chapter_content: ChapterContent = Depends(get_chapter_content),
) -> Dict:
    """Update a location's role in a chapter."""
    try:
        updated_location = await chapter_content.update_location_in_chapter(
            chapter_id,
            location_id,
            updates
        )
        return {
            "success": True,
            "location_id": str(location_id),
            "updates": updates
        }
    except Exception as e:
        logger.error("Failed to update location in chapter", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{chapter_id}/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_location_from_chapter(
    chapter_id: UUID,
    location_id: UUID,
    db: Session = Depends(get_db),
    chapter_content: ChapterContent = Depends(get_chapter_content),
) -> Response:
    """Remove a location from a chapter."""
    try:
        await chapter_content.remove_location_from_chapter(chapter_id, location_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error("Failed to remove location from chapter", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{chapter_id}/encounters")
async def generate_encounters(
    chapter_id: UUID,
    requirements: Optional[Dict] = None,
    db: Session = Depends(get_db),
    chapter_content: ChapterContent = Depends(get_chapter_content),
) -> List[Dict]:
    """Generate encounters for a chapter."""
    try:
        encounters = await chapter_content.generate_chapter_encounters(
            chapter_id,
            requirements
        )
        return encounters
    except Exception as e:
        logger.error("Failed to generate encounters", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
