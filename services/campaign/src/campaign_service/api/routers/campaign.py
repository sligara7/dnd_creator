"""Campaign router implementation."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from campaign_service.core.exceptions import (
    CampaignNotFoundError,
    GenerationError,
    ThemeValidationError,
)
from campaign_service.core.logging import get_logger
from campaign_service.models.storage_campaign import Campaign, CampaignState
from campaign_service.schemas.campaign import (
    CampaignCreate,
    CampaignList,
    CampaignRead,
    CampaignUpdate,
)
from campaign_service.services.campaign_factory import CampaignFactoryService
from campaign_service.services.dependencies import get_campaign_factory

router = APIRouter(prefix="/api/v2/campaigns", tags=["campaigns"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=CampaignRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_campaign(
    request: CampaignCreate,
    factory: CampaignFactoryService = Depends(get_campaign_factory),
) -> CampaignRead:
    """Create a new campaign.

    Args:
        request (CampaignCreate): Campaign creation request
        factory (CampaignFactoryService): Campaign factory service

    Returns:
        CampaignRead: Created campaign

    Raises:
        HTTPException: If creation fails
    """
    try:
        campaign = await factory.create_campaign(
            name=request.name,
            description=request.description,
            campaign_type=request.campaign_type,
            creator_id=request.creator_id,
            owner_id=request.owner_id,
            theme_id=request.theme_id,
            metadata=request.metadata,
        )
        return CampaignRead.from_orm(campaign)

    except ThemeValidationError as e:
        logger.warning("Theme validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except GenerationError as e:
        logger.error("Campaign generation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Campaign creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create campaign",
        )


@router.get("", response_model=CampaignList)
async def list_campaigns(
    factory: CampaignFactoryService = Depends(get_campaign_factory),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    owner_id: Optional[UUID] = None,
    campaign_type: Optional[str] = None,
    state: Optional[CampaignState] = None,
    theme_id: Optional[UUID] = None,
) -> CampaignList:
    """List campaigns with optional filters.

    Args:
        factory (CampaignFactoryService): Campaign factory service
        skip (int): Number of records to skip
        limit (int): Maximum number of records
        owner_id (Optional[UUID], optional): Filter by owner. Defaults to None.
        campaign_type (Optional[str], optional): Filter by type. Defaults to None.
        state (Optional[CampaignState], optional): Filter by state. Defaults to None.
        theme_id (Optional[UUID], optional): Filter by theme. Defaults to None.

    Returns:
        CampaignList: List of campaigns

    Raises:
        HTTPException: If listing fails
    """
    try:
        filters = {}
        if owner_id:
            filters["owner_id"] = owner_id
        if campaign_type:
            filters["campaign_type"] = campaign_type
        if state:
            filters["state"] = state
        if theme_id:
            filters["theme_id"] = theme_id

        campaigns = await factory.campaign_storage.get_all(
            skip=skip,
            limit=limit,
            **filters,
        )
        total = await factory.campaign_storage.count(**filters)

        return CampaignList(
            items=[CampaignRead.from_orm(c) for c in campaigns],
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.error("Failed to list campaigns", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list campaigns",
        )


@router.get("/{campaign_id}", response_model=CampaignRead)
async def get_campaign(
    campaign_id: UUID,
    factory: CampaignFactoryService = Depends(get_campaign_factory),
) -> CampaignRead:
    """Get campaign by ID.

    Args:
        campaign_id (UUID): Campaign ID
        factory (CampaignFactoryService): Campaign factory service

    Returns:
        CampaignRead: Campaign details

    Raises:
        HTTPException: If campaign not found or retrieval fails
    """
    try:
        campaign = await factory.campaign_storage.get(campaign_id)
        if not campaign:
            raise CampaignNotFoundError(f"Campaign not found: {campaign_id}")

        return CampaignRead.model_validate(campaign.model_dump())

    except CampaignNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Failed to get campaign", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get campaign",
        )


@router.put("/{campaign_id}", response_model=CampaignRead)
async def update_campaign(
    campaign_id: UUID,
    request: CampaignUpdate,
    factory: CampaignFactoryService = Depends(get_campaign_factory),
) -> CampaignRead:
    """Update campaign.

    Args:
        campaign_id (UUID): Campaign ID
        request (CampaignUpdate): Update data
        factory (CampaignFactoryService): Campaign factory service

    Returns:
        CampaignRead: Updated campaign

    Raises:
        HTTPException: If campaign not found or update fails
    """
    try:
        # Verify campaign exists
        campaign = await factory.campaign_storage.get(campaign_id)
        if not campaign:
            raise CampaignNotFoundError(f"Campaign not found: {campaign_id}")

        # Prepare update data
        update_data = request.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        # Update campaign
        updated_campaign = await factory.campaign_storage.update(campaign_id, update_data)
        if not updated_campaign:
            raise CampaignNotFoundError(f"Campaign not found: {campaign_id}")

        return CampaignRead.model_validate(updated_campaign.model_dump())

    except CampaignNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Failed to update campaign", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update campaign",
        )


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: UUID,
    factory: CampaignFactoryService = Depends(get_campaign_factory),
) -> Response:
    """Delete campaign.

    Args:
        campaign_id (UUID): Campaign ID
        factory (CampaignFactoryService): Campaign factory service

    Returns:
        Response: Empty response

    Raises:
        HTTPException: If campaign not found or deletion fails
    """
    try:
        # Verify campaign exists
        campaign = await factory.campaign_storage.get(campaign_id)
        if not campaign:
            raise CampaignNotFoundError(f"Campaign not found: {campaign_id}")

        # Delete campaign
        result = await factory.campaign_storage.delete(campaign_id)
        if not result:
            raise CampaignNotFoundError(f"Campaign not found: {campaign_id}")

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except CampaignNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Failed to delete campaign", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete campaign",
        )
