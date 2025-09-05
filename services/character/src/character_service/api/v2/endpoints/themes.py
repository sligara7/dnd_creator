"""Theme management endpoints."""
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.services.theme_state import ThemeStateManager
from character_service.services.theme_transition import ThemeTransitionService
from character_service.services.character import CharacterService
from character_service.core.database import get_db
from character_service.core.exceptions import (
    CharacterNotFoundError,
    ThemeNotFoundError,
    ThemeValidationError,
)

# Import API schemas
from character_service.api.v2.schemas.theme import (
    ThemeTransitionRequest,
    ThemeListResponse,
    ThemeListQuery,
    ThemeHistoryResponse,
    ThemeValidationRequest,
    ThemeValidationResponse,
    ThemeSuggestionRequest,
    ThemeSuggestionResponse,
)

router = APIRouter(prefix="/themes", tags=["themes"])

@router.post(
    "/transition/{character_id}",
    response_model=ThemeHistoryResponse,
    responses={
        404: {"description": "Character or theme not found"},
        400: {"description": "Invalid transition request"},
        422: {"description": "Validation error"},
    },
)
async def transition_theme(
    character_id: UUID,
    request: ThemeTransitionRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Transition a character's theme."""
    # Initialize services
    theme_state_manager = ThemeStateManager(db)
    character_service = CharacterService(db)
    theme_transition_service = ThemeTransitionService(
        db,
        theme_state_manager,
        character_service,
    )

    try:
        # Apply transition
        result = await theme_transition_service.apply_transition(
            character_id=character_id,
            from_theme_id=request.from_theme_id,
            to_theme_id=request.to_theme_id,
            transition_type=request.transition_type,
            triggered_by=request.triggered_by,
            campaign_event_id=request.campaign_event_id,
        )

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Theme transition failed",
                    "errors": [e.dict() for e in result.validation_result.errors],
                    "details": result.error_details,
                },
            )

        # Get updated history
        transitions = await theme_state_manager.get_theme_history(character_id)
        current_state = await theme_state_manager.get_active_theme_state(character_id)
        current_theme = result.new_state.theme if result.new_state else None

        return ThemeHistoryResponse(
            transitions=transitions,
            current_theme=current_theme,
            current_state=current_state,
        )

    except (CharacterNotFoundError, ThemeNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ThemeValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/history/{character_id}",
    response_model=ThemeHistoryResponse,
    responses={
        404: {"description": "Character not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_theme_history(
    character_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ThemeHistoryResponse:
    """Get a character's theme history."""
    try:
        # Initialize services
        theme_state_manager = ThemeStateManager(db)

        # Get history
        transitions = await theme_state_manager.get_theme_history(character_id)
        current_state = await theme_state_manager.get_active_theme_state(character_id)
        current_theme = None  # TODO: Get current theme

        return ThemeHistoryResponse(
            transitions=transitions,
            current_theme=current_theme,
            current_state=current_state,
        )

    except CharacterNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/validate",
    response_model=ThemeValidationResponse,
    responses={
        404: {"description": "Character or theme not found"},
        500: {"description": "Internal server error"},
    },
)
async def validate_theme(
    request: ThemeValidationRequest,
    db: AsyncSession = Depends(get_db)
) -> ThemeValidationResponse:
    """Validate a theme for a character."""
    try:
        # Initialize services
        theme_state_manager = ThemeStateManager(db)
        character_service = CharacterService(db)
        theme_transition_service = ThemeTransitionService(
            db,
            theme_state_manager,
            character_service,
        )

        # Get current theme state
        current_state = await theme_state_manager.get_active_theme_state(
            request.character_id
        )
        from_theme_id = current_state.theme_id if current_state else None

        # Validate transition
        validation_result = await theme_transition_service.validate_transition(
            character_id=request.character_id,
            from_theme_id=from_theme_id,
            to_theme_id=request.theme_id,
            transition_type=request.transition_type,
            campaign_event_id=request.campaign_event_id,
        )

        return ThemeValidationResponse(
            is_valid=validation_result.is_valid,
            errors=validation_result.errors,
            warnings=validation_result.warnings,
            suggestions=validation_result.suggestions,
        )

    except (CharacterNotFoundError, ThemeNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/suggest",
    response_model=ThemeSuggestionResponse,
    responses={
        404: {"description": "Character not found"},
        500: {"description": "Internal server error"},
    },
)
async def suggest_themes(
    request: ThemeSuggestionRequest,
    db: AsyncSession = Depends(get_db)
) -> ThemeSuggestionResponse:
    """Get theme suggestions for a character."""
    try:
        # Initialize services
        theme_state_manager = ThemeStateManager(db)
        character_service = CharacterService(db)
        theme_transition_service = ThemeTransitionService(
            db,
            theme_state_manager,
            character_service,
        )

        # Get suggestions
        suggestions = await theme_transition_service.get_transition_suggestions(
            character_id=request.character_id,
            event_context=request.event_context,
        )

        return ThemeSuggestionResponse(
            suggestions=suggestions,
            reason=None,  # TODO: Add reason from LLM service
        )

    except CharacterNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
