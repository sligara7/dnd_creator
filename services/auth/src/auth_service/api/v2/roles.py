"""Role management API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.database import get_db
from auth_service.core.exceptions import (
    StorageError,
    RoleNotFoundError,
    ValidationError
)
from auth_service.models.api import RoleCreate, RoleResponse, RoleUpdate
from auth_service.services.role import RoleService


router = APIRouter(prefix="/api/v2/roles", tags=["Roles"])


@router.get("", response_model=List[RoleResponse])
async def list_roles(
    name: Optional[str] = None,
    is_system_role: Optional[bool] = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> List[RoleResponse]:
    """
    List roles with filtering and pagination.
    
    Args:
        name: Optional name filter
        is_system_role: Optional system role filter
        limit: Maximum number of records
        offset: Pagination offset
        db: Database session
        
    Returns:
        List of roles
        
    Raises:
        HTTPException: If retrieval fails
    """
    role_service = RoleService(db)
    
    try:
        roles = await role_service.list_roles(
            name=name,
            is_system_role=is_system_role,
            limit=limit,
            offset=offset
        )
        return roles
        
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    request: RoleCreate,
    db: AsyncSession = Depends(get_db)
) -> RoleResponse:
    """
    Create new role.
    
    Args:
        request: Role creation model
        db: Database session
        
    Returns:
        Created role
        
    Raises:
        HTTPException: If creation fails
    """
    role_service = RoleService(db)
    
    try:
        role = await role_service.create_role(request)
        await db.commit()
        return role
        
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


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> RoleResponse:
    """
    Get role details.
    
    Args:
        role_id: Role ID
        db: Database session
        
    Returns:
        Role details
        
    Raises:
        HTTPException: If role not found or retrieval fails
    """
    role_service = RoleService(db)
    
    try:
        role = await role_service.get_role(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role {role_id} not found"
            )
        return role
        
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    request: RoleUpdate,
    db: AsyncSession = Depends(get_db)
) -> RoleResponse:
    """
    Update role.
    
    Args:
        role_id: Role ID
        request: Role update model
        db: Database session
        
    Returns:
        Updated role
        
    Raises:
        HTTPException: If role not found or update fails
    """
    role_service = RoleService(db)
    
    try:
        role = await role_service.update_role(role_id, request)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role {role_id} not found"
            )
            
        await db.commit()
        return role
        
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


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete role (soft delete).
    
    Args:
        role_id: Role ID
        db: Database session
        
    Raises:
        HTTPException: If role not found or deletion fails
    """
    role_service = RoleService(db)
    
    try:
        success = await role_service.delete_role(role_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role {role_id} not found"
            )
            
        await db.commit()
        
    except StorageError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{role_id}/users", status_code=status.HTTP_204_NO_CONTENT)
async def assign_users_to_role(
    role_id: UUID,
    user_ids: List[UUID],
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Assign users to role.
    
    Args:
        role_id: Role ID
        user_ids: List of user IDs to assign
        db: Database session
        
    Raises:
        HTTPException: If role not found or assignment fails
    """
    role_service = RoleService(db)
    
    try:
        await role_service.assign_users(role_id, user_ids)
        await db.commit()
        
    except RoleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role {role_id} not found"
        )
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


@router.delete("/{role_id}/users", status_code=status.HTTP_204_NO_CONTENT)
async def remove_users_from_role(
    role_id: UUID,
    user_ids: List[UUID],
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Remove users from role.
    
    Args:
        role_id: Role ID
        user_ids: List of user IDs to remove
        db: Database session
        
    Raises:
        HTTPException: If role not found or removal fails
    """
    role_service = RoleService(db)
    
    try:
        await role_service.remove_users(role_id, user_ids)
        await db.commit()
        
    except RoleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role {role_id} not found"
        )
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