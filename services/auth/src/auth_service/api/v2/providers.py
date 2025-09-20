"""External identity provider integration endpoints."""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.core.database import get_db
from auth_service.core.exceptions import (
    StorageError,
    ValidationError
)
from auth_service.models.api import ProviderLoginResponse, OAuthConfig
from auth_service.services.provider import ProviderService


router = APIRouter(prefix="/api/v2/auth/providers", tags=["External Identity"])


@router.get("/config", response_model=Dict[str, OAuthConfig])
async def get_provider_configs(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, OAuthConfig]:
    """
    Get configuration for enabled identity providers.
    
    Args:
        db: Database session
        
    Returns:
        Provider configurations keyed by provider ID
        
    Raises:
        HTTPException: If retrieval fails
    """
    provider_service = ProviderService(db)
    
    try:
        return await provider_service.get_configurations()
        
    except StorageError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/login/{provider_id}")
async def initiate_provider_login(
    provider_id: str,
    redirect_uri: str,
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> RedirectResponse:
    """
    Initiate OAuth2 login flow with provider.
    
    Args:
        provider_id: Identity provider ID
        redirect_uri: OAuth2 redirect URI
        state: Optional state parameter
        db: Database session
        
    Returns:
        Redirect to provider's authorization endpoint
        
    Raises:
        HTTPException: If provider not found or flow initiation fails
    """
    provider_service = ProviderService(db)
    
    try:
        auth_url = await provider_service.get_authorization_url(
            provider_id,
            redirect_uri,
            state
        )
        return RedirectResponse(url=auth_url)
        
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


@router.get("/callback/{provider_id}", response_model=ProviderLoginResponse)
async def handle_provider_callback(
    provider_id: str,
    code: str,
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> ProviderLoginResponse:
    """
    Handle OAuth2 callback from provider.
    
    Args:
        provider_id: Identity provider ID
        code: Authorization code
        state: Optional state parameter
        db: Database session
        
    Returns:
        Login response with tokens
        
    Raises:
        HTTPException: If provider not found or callback processing fails
    """
    provider_service = ProviderService(db)
    
    try:
        return await provider_service.handle_callback(
            provider_id,
            code,
            state
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


@router.post("/link/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def link_provider_account(
    provider_id: str,
    user_id: UUID,
    provider_token: str,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Link external provider account to existing user.
    
    Args:
        provider_id: Identity provider ID
        user_id: User ID to link
        provider_token: Provider's access token
        db: Database session
        
    Raises:
        HTTPException: If provider not found or linking fails
    """
    provider_service = ProviderService(db)
    
    try:
        await provider_service.link_account(
            provider_id,
            user_id,
            provider_token
        )
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


@router.delete("/link/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_provider_account(
    provider_id: str,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Unlink external provider account from user.
    
    Args:
        provider_id: Identity provider ID
        user_id: User ID to unlink
        db: Database session
        
    Raises:
        HTTPException: If provider not found or unlinking fails
    """
    provider_service = ProviderService(db)
    
    try:
        await provider_service.unlink_account(provider_id, user_id)
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