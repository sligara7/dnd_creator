"""Audit logging API endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.database import get_db
from auth_service.core.exceptions import (
    StorageError,
    ValidationError
)
from auth_service.models.api import AuditLogResponse, AuditLogFilter
from auth_service.services.audit import AuditService


router = APIRouter(prefix="/api/v2/audit", tags=["Audit"])


@router.get("/logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    user_id: Optional[UUID] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    success_only: bool = False,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> List[AuditLogResponse]:
    """
    List audit logs with filtering and pagination.
    
    Args:
        user_id: Optional user ID filter
        action: Optional action filter
        resource_type: Optional resource type filter
        start_time: Optional start time filter
        end_time: Optional end time filter
        success_only: Only return successful operations
        limit: Maximum number of records
        offset: Pagination offset
        db: Database session
        
    Returns:
        List of audit logs
        
    Raises:
        HTTPException: If retrieval fails
    """
    audit_service = AuditService(db)
    
    try:
        audit_filter = AuditLogFilter(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            start_time=start_time,
            end_time=end_time,
            success_only=success_only
        )
        logs = await audit_service.list_logs(
            audit_filter,
            limit=limit,
            offset=offset
        )
        return logs
        
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/stats", response_model=dict)
async def get_audit_stats(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    interval: str = Query("1h", regex="^[0-9]+(h|d|w|m)$"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get audit statistics over time.
    
    Args:
        start_time: Optional start time
        end_time: Optional end time
        interval: Time interval for aggregation (e.g., 1h, 1d, 1w, 1m)
        db: Database session
        
    Returns:
        Audit statistics:
        - Total events
        - Events by type
        - Success/failure ratio
        - Top users
        - Top resources
        
    Raises:
        HTTPException: If retrieval fails
    """
    audit_service = AuditService(db)
    
    try:
        return await audit_service.get_statistics(
            start_time=start_time,
            end_time=end_time,
            interval=interval
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/cleanup", status_code=status.HTTP_202_ACCEPTED)
async def cleanup_audit_logs(
    before: datetime,
    archive: bool = True,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Clean up old audit logs.
    
    Args:
        before: Remove logs older than this time
        archive: Whether to archive logs before removal
        db: Database session
        
    Returns:
        Cleanup status:
        - Records removed
        - Records archived
        - Archive location
        
    Raises:
        HTTPException: If cleanup fails
    """
    audit_service = AuditService(db)
    
    try:
        result = await audit_service.cleanup_logs(
            before=before,
            archive=archive
        )
        await db.commit()
        return result
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except StorageError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/reports/security", response_model=dict)
async def get_security_report(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get security audit report.
    
    Args:
        start_time: Optional start time
        end_time: Optional end time
        db: Database session
        
    Returns:
        Security report:
        - Failed login attempts
        - Account lockouts
        - Permission changes
        - Role changes
        - Suspicious activity
        
    Raises:
        HTTPException: If report generation fails
    """
    audit_service = AuditService(db)
    
    try:
        return await audit_service.get_security_report(
            start_time=start_time,
            end_time=end_time
        )
        
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/reports/access", response_model=dict)
async def get_access_report(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get access pattern report.
    
    Args:
        start_time: Optional start time
        end_time: Optional end time
        db: Database session
        
    Returns:
        Access report:
        - Resource access patterns
        - User activity patterns
        - API usage statistics
        - Access anomalies
        
    Raises:
        HTTPException: If report generation fails
    """
    audit_service = AuditService(db)
    
    try:
        return await audit_service.get_access_report(
            start_time=start_time,
            end_time=end_time
        )
        
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )