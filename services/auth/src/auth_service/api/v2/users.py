"""User management API endpoints."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.database import get_db
from auth_service.core.exceptions import (
    StorageError,
    UserNotFoundError,
    ValidationError
)
from auth_service.models.api import UserCreate, UserResponse, UserUpdate
from auth_service.services.user import UserService


router = APIRouter(prefix="/api/v2/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
async def list_users(
    username: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[str] = None,
    mfa_enabled: Optional[bool] = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> List[UserResponse]:
    """
    List users with filtering and pagination.
    
    Args:
        username: Optional username filter
        email: Optional email filter
        status: Optional status filter
        mfa_enabled: Optional MFA status filter
        limit: Maximum number of records
        offset: Pagination offset
        db: Database session
        
    Returns:
        List of users
        
    Raises:
        HTTPException: If retrieval fails
    """
    user_service = UserService(db)
    
    try:
        users = await user_service.list_users(
            username=username,
            email=email,
            status=status,
            mfa_enabled=mfa_enabled,
            limit=limit,
            offset=offset
        )
        return users
        
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreate,
    req: Request,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Create new user.
    
    Args:
        request: User creation model
        req: FastAPI request object
        db: Database session
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If creation fails
    """
    user_service = UserService(db)
    
    try:
        user = await user_service.create_user(request)
        await db.commit()
        return user
        
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


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Get user details.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User details
        
    Raises:
        HTTPException: If user not found or retrieval fails
    """
    user_service = UserService(db)
    
    try:
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
        return user
        
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UserUpdate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Update user.
    
    Args:
        user_id: User ID
        request: User update model
        db: Database session
        
    Returns:
        Updated user
        
    Raises:
        HTTPException: If user not found or update fails
    """
    user_service = UserService(db)
    
    try:
        user = await user_service.update_user(user_id, request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
            
        await db.commit()
        return user
        
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


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete user (soft delete).
    
    Args:
        user_id: User ID
        db: Database session
        
    Raises:
        HTTPException: If user not found or deletion fails
    """
    user_service = UserService(db)
    
    try:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found"
            )
            
        await db.commit()
        
    except StorageError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )