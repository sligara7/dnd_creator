"""API endpoints for theme management."""
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Response, status

from image.api.models import ThemeListResponse, ThemeRequest, ThemeResponse
from image.core.dependencies import get_theme_service
from image.core.errors import ThemeNotFoundError
from image.core.validation import validate_api_key
from image.services.theme import ThemeService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/themes",
    response_model=ThemeListResponse,
    summary="List available themes",
    response_description="List of available themes"
)
async def list_themes(
    filter_type: Optional[str] = Query(None, description="Filter by theme type"),
    x_api_key: str = Header(...),
    theme_service: ThemeService = Depends(get_theme_service)
) -> dict:
    """List all available themes.

    Args:
        filter_type: Optional theme type filter
        x_api_key: API key for authentication
        theme_service: Theme service

    Returns:
        List of available themes
    """
    # Validate API key
    validate_api_key(x_api_key, "themes:read")

    try:
        # Get themes
        themes = await theme_service.list_themes(filter_type)
        return {
            "themes": [
                {
                    "id": theme.id,
                    "name": theme.name,
                    "description": theme.description,
                    "type": theme.type,
                    "style_options": theme.style_options,
                    "properties": theme.properties
                }
                for theme in themes
            ]
        }

    except Exception as e:
        logger.exception("Error listing themes")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/themes",
    response_model=ThemeResponse,
    summary="Create new theme",
    response_description="The created theme",
    status_code=status.HTTP_201_CREATED
)
async def create_theme(
    request: ThemeRequest,
    x_api_key: str = Header(...),
    theme_service: ThemeService = Depends(get_theme_service)
) -> dict:
    """Create a new theme.

    Args:
        request: Theme creation parameters
        x_api_key: API key for authentication
        theme_service: Theme service

    Returns:
        Created theme details
    """
    # Validate API key
    validate_api_key(x_api_key, "themes:write")

    try:
        # Create theme
        theme = await theme_service.create_theme(
            name=request.name,
            description=request.description,
            type=request.type,
            style_options=request.style_options,
            properties=request.properties
        )

        return {
            "id": theme.id,
            "name": theme.name,
            "description": theme.description,
            "type": theme.type,
            "style_options": theme.style_options,
            "properties": theme.properties,
            "created_at": theme.created_at,
            "updated_at": theme.updated_at
        }

    except Exception as e:
        logger.exception("Error creating theme")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/themes/{theme_id}",
    response_model=ThemeResponse,
    summary="Get theme details",
    response_description="The theme details"
)
async def get_theme(
    theme_id: UUID = Path(..., description="Theme ID"),
    x_api_key: str = Header(...),
    theme_service: ThemeService = Depends(get_theme_service)
) -> dict:
    """Get details of a theme.

    Args:
        theme_id: Theme ID
        x_api_key: API key for authentication
        theme_service: Theme service

    Returns:
        Theme details

    Raises:
        ThemeNotFoundError: If theme not found
    """
    # Validate API key
    validate_api_key(x_api_key, "themes:read")

    try:
        # Get theme
        theme = await theme_service.get_theme(theme_id)
        if not theme:
            raise ThemeNotFoundError(theme_id)

        return {
            "id": theme.id,
            "name": theme.name,
            "description": theme.description,
            "type": theme.type,
            "style_options": theme.style_options,
            "properties": theme.properties,
            "created_at": theme.created_at,
            "updated_at": theme.updated_at
        }

    except ThemeNotFoundError:
        raise
    except Exception as e:
        logger.exception("Error getting theme")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/themes/{theme_id}",
    response_model=ThemeResponse,
    summary="Update theme",
    response_description="The updated theme"
)
async def update_theme(
    request: ThemeRequest,
    theme_id: UUID = Path(..., description="Theme ID"),
    x_api_key: str = Header(...),
    theme_service: ThemeService = Depends(get_theme_service)
) -> dict:
    """Update an existing theme.

    Args:
        request: Updated theme parameters
        theme_id: Theme ID
        x_api_key: API key for authentication
        theme_service: Theme service

    Returns:
        Updated theme details

    Raises:
        ThemeNotFoundError: If theme not found
    """
    # Validate API key
    validate_api_key(x_api_key, "themes:write")

    try:
        # Verify theme exists
        theme = await theme_service.get_theme(theme_id)
        if not theme:
            raise ThemeNotFoundError(theme_id)

        # Update theme
        updated = await theme_service.update_theme(
            theme_id=theme_id,
            name=request.name,
            description=request.description,
            type=request.type,
            style_options=request.style_options,
            properties=request.properties
        )

        return {
            "id": updated.id,
            "name": updated.name,
            "description": updated.description,
            "type": updated.type,
            "style_options": updated.style_options,
            "properties": updated.properties,
            "created_at": updated.created_at,
            "updated_at": updated.updated_at
        }

    except ThemeNotFoundError:
        raise
    except Exception as e:
        logger.exception("Error updating theme")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/themes/{theme_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete theme",
    response_description="Theme deleted successfully"
)
async def delete_theme(
    theme_id: UUID = Path(..., description="Theme ID"),
    x_api_key: str = Header(...),
    theme_service: ThemeService = Depends(get_theme_service)
) -> Response:
    """Delete a theme.

    Args:
        theme_id: Theme ID
        x_api_key: API key for authentication
        theme_service: Theme service

    Returns:
        Empty response

    Raises:
        ThemeNotFoundError: If theme not found
    """
    # Validate API key
    validate_api_key(x_api_key, "themes:delete")

    try:
        # Verify theme exists
        theme = await theme_service.get_theme(theme_id)
        if not theme:
            raise ThemeNotFoundError(theme_id)

        # Delete theme
        success = await theme_service.delete_theme(theme_id)
        if not success:
            raise ThemeNotFoundError(theme_id)

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ThemeNotFoundError:
        raise
    except Exception as e:
        logger.exception("Error deleting theme")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/themes/{theme_id}/apply",
    response_model=ThemeResponse,
    summary="Apply theme to existing content",
    response_description="The applied theme result"
)
async def apply_theme(
    theme_id: UUID = Path(..., description="Theme ID"),
    content_ids: List[UUID] = Query(..., description="Content IDs to apply theme to"),
    x_request_id: str = Header(None),
    x_api_key: str = Header(...),
    theme_service: ThemeService = Depends(get_theme_service)
) -> dict:
    """Apply a theme to existing content.

    Args:
        theme_id: Theme ID to apply
        content_ids: List of content IDs to apply theme to
        x_request_id: Optional request ID
        x_api_key: API key for authentication
        theme_service: Theme service

    Returns:
        Theme application result

    Raises:
        ThemeNotFoundError: If theme not found
    """
    # Validate API key
    validate_api_key(x_api_key, "themes:apply")

    try:
        # Verify theme exists
        theme = await theme_service.get_theme(theme_id)
        if not theme:
            raise ThemeNotFoundError(theme_id)

        # Apply theme
        result = await theme_service.apply_theme(
            theme_id=theme_id,
            content_ids=content_ids,
            request_id=x_request_id
        )

        return {
            "id": result.id,
            "name": result.name,
            "description": result.description,
            "type": result.type,
            "style_options": result.style_options,
            "properties": result.properties,
            "created_at": result.created_at,
            "updated_at": result.updated_at,
            "application_status": result.status,
            "applied_content": result.content_ids
        }

    except ThemeNotFoundError:
        raise
    except Exception as e:
        logger.exception("Error applying theme")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
