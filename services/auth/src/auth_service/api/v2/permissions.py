"""Permission management API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.database import get_db
from auth_service.core.exceptions import (
    StorageError,
    PermissionNotFoundError,
    ValidationError
)
from auth_service.models.api import PermissionCreate, PermissionResponse, PermissionUpdate
from auth_service.services.permission import PermissionService


router = APIRouter(prefix="/api/v2/permissions", tags=["Permissions"])


@router.get("", response_model=List[PermissionResponse])
async def list_permissions(
    name: Optional[str] = None,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    is_system_permission: Optional[bool] = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> List[PermissionResponse]:
    """
    List permissions with filtering and pagination.
    
    Args:
        name: Optional name filter
        resource: Optional resource filter
        action: Optional action filter
        is_system_permission: Optional system permission filter
        limit: Maximum number of records
        offset: Pagination offset
        db: Database session
        
    Returns:
        List of permissions
        
    Raises:
        HTTPException: If retrieval fails
    """
    permission_service = PermissionService(db)
    
    try:
        permissions = await permission_service.list_permissions(
            name=name,
            resource=resource,
            action=action,
            is_system_permission=is_system_permission,
            limit=limit,
            offset=offset
        )
        return permissions
        
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    request: PermissionCreate,
    db: AsyncSession = Depends(get_db)
) -> PermissionResponse:
    """
    Create new permission.
    
    Args:
        request: Permission creation model
        db: Database session
        
    Returns:
        Created permission
        
    Raises:
        HTTPException: If creation fails
    """
    permission_service = PermissionService(db)
    
    try:
        permission = await permission_service.create_permission(request)
        await db.commit()
        return permission
        
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


@router.get("/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> PermissionResponse:
    """
    Get permission details.
    
    Args:
        permission_id: Permission ID
        db: Database session
        
    Returns:
        Permission details
        
    Raises:
        HTTPException: If permission not found or retrieval fails
    """
    permission_service = PermissionService(db)
    
    try:
        permission = await permission_service.get_permission(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission {permission_id} not found"
            )
        return permission
        
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: UUID,
    request: PermissionUpdate,
    db: AsyncSession = Depends(get_db)
) -> PermissionResponse:
    """
    Update permission.
    
    Args:
        permission_id: Permission ID
        request: Permission update model
        db: Database session
        
    Returns:
        Updated permission
        
    Raises:
        HTTPException: If permission not found or update fails
    """
    permission_service = PermissionService(db)
    
    try:
        permission = await permission_service.update_permission(permission_id, request)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission {permission_id} not found"
            )
            
        await db.commit()
        return permission
        
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


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete permission (soft delete).
    
    Args:
        permission_id: Permission ID
        db: Database session
        
    Raises:
        HTTPException: If permission not found or deletion fails
    """
    permission_service = PermissionService(db)
    
    try:
        success = await permission_service.delete_permission(permission_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission {permission_id} not found"
            )
            
        await db.commit()
        
    except StorageError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/roles", status_code=status.HTTP_204_NO_CONTENT)
async def assign_permissions_to_roles(
    role_ids: List[UUID],
    permission_ids: List[UUID],
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Assign permissions to roles.
    
    Args:
        role_ids: List of role IDs
        permission_ids: List of permission IDs to assign
        db: Database session
        
    Raises:
        HTTPException: If assignment fails
    """
    permission_service = PermissionService(db)
    
    try:
        await permission_service.assign_to_roles(role_ids, permission_ids)
        await db.commit()
        
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


@router.delete("/roles", status_code=status.HTTP_204_NO_CONTENT)
async def remove_permissions_from_roles(
    role_ids: List[UUID],
    permission_ids: List[UUID],
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Remove permissions from roles.
    
    Args:
        role_ids: List of role IDs
        permission_ids: List of permission IDs to remove
        db: Database session
        
    Raises:
        HTTPException: If removal fails
    """
    permission_service = PermissionService(db)
    
    try:
        await permission_service.remove_from_roles(role_ids, permission_ids)
        await db.commit()
        
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