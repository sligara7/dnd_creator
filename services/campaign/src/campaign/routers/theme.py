"""Router for theme management endpoints."""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import (get_db, get_llm_service, get_theme_service,
                        get_theme_integration_service, get_world_effect_service)
from ..models.api.theme import (FactionCreate, FactionResponse,
                            LocationCreate, LocationResponse,
                            ThemeApplicationRequest, ThemeApplicationResponse,
                            ThemeCombinationCreate, ThemeCombinationResponse,
                            ThemeCreate, ThemeResponse, ThemeUpdate,
                            ThemeValidationRequest, ThemeValidationResponse,
                            WorldEffectCreate, WorldEffectResponse)
from ..services.theme import ThemeService
from ..services.theme_integration import ThemeIntegrationService
from ..services.world_effect import WorldEffectService

router = APIRouter(prefix="/api/v2/themes", tags=["themes"])


# Theme Management Endpoints

@router.post("", response_model=ThemeResponse)
async def create_theme(
    theme: ThemeCreate,
    theme_service: ThemeService = Depends(get_theme_service),
):
    """Create a new theme."""
    return await theme_service.create_theme(theme)


@router.get("", response_model=List[ThemeResponse])
async def list_themes(
    type_filter: Optional[str] = None,
    tone_filter: Optional[str] = None,
    theme_service: ThemeService = Depends(get_theme_service),
):
    """List all themes, optionally filtered."""
    return await theme_service.list_themes(
        type_filter=type_filter,
        tone_filter=tone_filter,
    )


@router.get("/{theme_id}", response_model=ThemeResponse)
async def get_theme(
    theme_id: UUID,
    theme_service: ThemeService = Depends(get_theme_service),
):
    """Get a specific theme by ID."""
    theme = await theme_service.get_theme(theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found",
        )
    return theme


@router.put("/{theme_id}", response_model=ThemeResponse)
async def update_theme(
    theme_id: UUID,
    theme: ThemeUpdate,
    theme_service: ThemeService = Depends(get_theme_service),
):
    """Update a specific theme."""
    updated_theme = await theme_service.update_theme(theme_id, theme)
    if not updated_theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found",
        )
    return updated_theme


@router.delete("/{theme_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_theme(
    theme_id: UUID,
    theme_service: ThemeService = Depends(get_theme_service),
):
    """Delete a specific theme."""
    if not await theme_service.delete_theme(theme_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found",
        )


# Theme Combination Endpoints

@router.post("/combinations", response_model=ThemeCombinationResponse)
async def combine_themes(
    combination: ThemeCombinationCreate,
    theme_service: ThemeService = Depends(get_theme_service),
):
    """Create a new theme combination."""
    success = await theme_service.combine_themes(
        primary_theme_id=combination.primary_theme_id,
        secondary_theme_id=combination.secondary_theme_id,
        weight=combination.weight,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both themes not found",
        )
    return combination


@router.get("/{theme_id}/combinations", response_model=List[ThemeCombinationResponse])
async def list_theme_combinations(
    theme_id: UUID,
    theme_service: ThemeService = Depends(get_theme_service),
):
    """List all theme combinations for a specific theme."""
    return await theme_service.get_theme_combinations(theme_id)


# Theme Content Management Endpoints

@router.post("/apply", response_model=ThemeApplicationResponse)
async def apply_theme_to_content(
    request: ThemeApplicationRequest,
    theme_integration: ThemeIntegrationService = Depends(get_theme_integration_service),
):
    """Apply a theme to content."""
    try:
        return await theme_integration.apply_theme_to_content(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/validate", response_model=ThemeValidationResponse)
async def validate_theme_content(
    request: ThemeValidationRequest,
    theme_integration: ThemeIntegrationService = Depends(get_theme_integration_service),
):
    """Validate if content is consistent with a theme."""
    try:
        return await theme_integration.validate_theme_consistency(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{theme_id}/content/{content_type}", response_model=Dict)
async def generate_themed_content(
    theme_id: UUID,
    content_type: str,
    parameters: Optional[Dict] = None,
    theme_integration: ThemeIntegrationService = Depends(get_theme_integration_service),
):
    """Generate new content based on a theme."""
    try:
        return await theme_integration.generate_themed_content(
            theme_id=theme_id,
            content_type=content_type,
            parameters=parameters,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/adapt", response_model=Dict)
async def adapt_content_between_themes(
    content: Dict,
    source_theme_id: UUID,
    target_theme_id: UUID,
    theme_integration: ThemeIntegrationService = Depends(get_theme_integration_service),
):
    """Adapt content from one theme to another."""
    try:
        return await theme_integration.adapt_content_to_theme(
            content=content,
            source_theme_id=source_theme_id,
            target_theme_id=target_theme_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# World Effect Endpoints

@router.post("/effects", response_model=WorldEffectResponse)
async def create_world_effect(
    effect: WorldEffectCreate,
    world_effect_service: WorldEffectService = Depends(get_world_effect_service),
):
    """Create a new world effect."""
    return await world_effect_service.create_world_effect(effect)


@router.get("/effects", response_model=List[WorldEffectResponse])
async def list_world_effects(
    theme_id: Optional[UUID] = None,
    effect_type: Optional[str] = None,
    world_effect_service: WorldEffectService = Depends(get_world_effect_service),
):
    """List world effects, optionally filtered."""
    return await world_effect_service.list_world_effects(
        theme_id=theme_id,
        effect_type=effect_type,
    )


@router.get("/effects/{effect_id}", response_model=WorldEffectResponse)
async def get_world_effect(
    effect_id: UUID,
    world_effect_service: WorldEffectService = Depends(get_world_effect_service),
):
    """Get a specific world effect."""
    effect = await world_effect_service.get_world_effect(effect_id)
    if not effect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="World effect not found",
        )
    return effect


@router.delete("/effects/{effect_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_world_effect(
    effect_id: UUID,
    world_effect_service: WorldEffectService = Depends(get_world_effect_service),
):
    """Delete a specific world effect."""
    if not await world_effect_service.delete_world_effect(effect_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="World effect not found",
        )


@router.post("/effects/{effect_id}/apply/location/{location_id}")
async def apply_effect_to_location(
    effect_id: UUID,
    location_id: UUID,
    world_effect_service: WorldEffectService = Depends(get_world_effect_service),
):
    """Apply a world effect to a location."""
    success = await world_effect_service.apply_effect_to_location(
        effect_id=effect_id,
        location_id=location_id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Effect or location not found, or effect not applicable",
        )
    return {"status": "success"}


@router.post("/effects/{effect_id}/apply/faction/{faction_id}")
async def apply_effect_to_faction(
    effect_id: UUID,
    faction_id: UUID,
    world_effect_service: WorldEffectService = Depends(get_world_effect_service),
):
    """Apply a world effect to a faction."""
    success = await world_effect_service.apply_effect_to_faction(
        effect_id=effect_id,
        faction_id=faction_id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Effect or faction not found, or effect not applicable",
        )
    return {"status": "success"}


@router.get("/effects/active")
async def list_active_effects(
    location_id: Optional[UUID] = None,
    faction_id: Optional[UUID] = None,
    world_effect_service: WorldEffectService = Depends(get_world_effect_service),
):
    """List active world effects for a location or faction."""
    return await world_effect_service.get_active_effects(
        location_id=location_id,
        faction_id=faction_id,
    )


@router.post("/effects/process")
async def process_theme_effects(
    theme_id: UUID,
    campaign_id: UUID,
    world_effect_service: WorldEffectService = Depends(get_world_effect_service),
):
    """Process and generate world effects for a theme in a campaign."""
    effects = await world_effect_service.process_theme_world_effects(
        theme_id=theme_id,
        campaign_id=campaign_id,
    )
    return {
        "status": "success",
        "effects_created": len(effects),
        "effects": effects,
    }
