"""Session management API endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.database import get_db
from auth_service.core.exceptions import (
    StorageError,
    SessionNotFoundError,
    ValidationError
)
from auth_service.models.api import SessionResponse
from auth_service.services.session import SessionService


router = APIRouter(prefix="/api/v2/sessions", tags=["Sessions"])


@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    user_id: Optional[UUID] = None,
    active_only: bool = True,
    before: Optional[datetime] = None,
    after: Optional[datetime] = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> List[SessionResponse]:
    """
    List active sessions with filtering.
    
    Args:
        user_id: Optional user ID filter
        active_only: Only return active sessions
        before: Optional max creation time
        after: Optional min creation time
        limit: Maximum number of records
        offset: Pagination offset
        db: Database session
        
    Returns:
        List of sessions
        
    Raises:
        HTTPException: If retrieval fails
    """
    session_service = SessionService(db)
    
    try:
        sessions = await session_service.list_sessions(
            user_id=user_id,
            active_only=active_only,
            before=before,
            after=after,
            limit=limit,
            offset=offset
        )
        return sessions
        
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> SessionResponse:
    """
    Get session details.
    
    Args:
        session_id: Session ID
        db: Database session
        
    Returns:
        Session details
        
    Raises:
        HTTPException: If session not found or retrieval fails
    """
    session_service = SessionService(db)
    
    try:
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        return session
        
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Revoke session.
    
    Args:
        session_id: Session ID
        db: Database session
        
    Raises:
        HTTPException: If session not found or revocation fails
    """
    session_service = SessionService(db)
    
    try:
        success = await session_service.revoke_session(session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
            
        await db.commit()
        
    except StorageError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/bulk/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def bulk_revoke_sessions(
    user_id: Optional[UUID] = None,
    before: Optional[datetime] = None,
    after: Optional[datetime] = None,
    session_ids: Optional[List[UUID]] = None,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Bulk session revocation.
    
    Args:
        user_id: Optional user ID to revoke all sessions for
        before: Optional max creation time
        after: Optional min creation time
        session_ids: Optional specific session IDs to revoke
        db: Database session
        
    Raises:
        HTTPException: If revocation fails
    """
    if not any([user_id, before, after, session_ids]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one filter criteria required"
        )
    
    session_service = SessionService(db)
    
    try:
        await session_service.bulk_revoke_sessions(
            user_id=user_id,
            before=before,
            after=after,
            session_ids=session_ids
        )
        await db.commit()
        
    except StorageError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )