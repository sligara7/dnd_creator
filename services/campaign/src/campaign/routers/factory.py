"""Router for campaign factory and content generation endpoints."""

from typing import Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db, get_campaign_factory
from ..docs.factory import (
    generate_campaign_docs,
    refine_campaign_docs,
    generate_npc_docs,
    generate_location_docs,
    generate_map_docs,
)
from ..models.api.factory import
                              CampaignGenerationResponse,
                              CampaignRefinementRequest,
                              CampaignRefinementResponse,
                              NPCGenerationRequest, NPCGenerationResponse,
                              LocationGenerationRequest,
                              LocationGenerationResponse,
                              MapGenerationRequest, MapGenerationResponse)
from ..services.factory import CampaignFactory


router = APIRouter(prefix="/api/v2", tags=["factory"])


@router.post(
    "/factory/create",
    response_model=CampaignGenerationResponse,
    **generate_campaign_docs
)
async def generate_campaign(
    request: CampaignGenerationRequest,
    factory: CampaignFactory = Depends(get_campaign_factory),
):
    """Generate a new campaign."""
    try:
        return await factory.generate_campaign(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/campaigns/{campaign_id}/refine",
    response_model=CampaignRefinementResponse,
    **refine_campaign_docs
)
async def refine_campaign(
    campaign_id: UUID,
    request: CampaignRefinementRequest,
    factory: CampaignFactory = Depends(get_campaign_factory),
):
    """Refine an existing campaign."""
    if request.campaign_id != campaign_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign ID in path must match campaign ID in request body",
        )

    try:
        return await factory.refine_campaign(request)
    except ValueError as e:
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
    "/campaigns/{campaign_id}/npcs",
    response_model=NPCGenerationResponse,
    **generate_npc_docs
)
async def generate_npc(
    campaign_id: UUID,
    request: NPCGenerationRequest,
    factory: CampaignFactory = Depends(get_campaign_factory),
):
    """Generate a new NPC for a campaign."""
    if request.campaign_id != campaign_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign ID in path must match campaign ID in request body",
        )

    try:
        return await factory.generate_npc(request)
    except ValueError as e:
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
    "/campaigns/{campaign_id}/locations",
    response_model=LocationGenerationResponse,
    **generate_location_docs
)
async def generate_location(
    campaign_id: UUID,
    request: LocationGenerationRequest,
    factory: CampaignFactory = Depends(get_campaign_factory),
):
    """Generate a new location for a campaign."""
    if request.campaign_id != campaign_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign ID in path must match campaign ID in request body",
        )

    try:
        return await factory.generate_location(request)
    except ValueError as e:
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
    "/campaigns/{campaign_id}/maps",
    response_model=MapGenerationResponse,
    **generate_map_docs
)
async def generate_map(
    campaign_id: UUID,
    request: MapGenerationRequest,
    factory: CampaignFactory = Depends(get_campaign_factory),
):
    """Generate a new map for a campaign."""
    if request.campaign_id != campaign_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign ID in path must match campaign ID in request body",
        )

    try:
        return await factory.generate_map(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
