"""Campaign API router."""
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ...core.db import get_db
from ...core.logging import get_logger
from ...services.campaign_factory import CampaignFactory
from ...services.version_control import VersionControlService
from ..schemas.campaign import (
    Campaign,
    CampaignDetail,
    CampaignSummary,
    CreateCampaignRequest,
    CreateCampaignResponse,
    UpdateCampaignRequest,
    CampaignProgress,
    GenerateCampaignRequest,
    GenerationResult,
)
from ..dependencies import (
    get_campaign_factory,
    get_version_control,
    get_message_hub,
)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=CreateCampaignResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_campaign(
    request: CreateCampaignRequest,
    db: Session = Depends(get_db),
    campaign_factory: CampaignFactory = Depends(get_campaign_factory),
) -> CreateCampaignResponse:
    """Create a new campaign."""
    try:
        campaign_id, campaign = await campaign_factory.create_campaign(request)
        return CreateCampaignResponse(
            id=campaign_id,
            name=campaign.name,
            status="draft",
            config=request.config,
            theme=request.theme.dict(),
        )
    except Exception as e:
        logger.error("Failed to create campaign", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[CampaignSummary])
async def list_campaigns(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    theme: Optional[str] = None,
    owner: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> List[CampaignSummary]:
    """List campaigns with optional filters."""
    try:
        query = db.query(Campaign)
        if status:
            query = query.filter(Campaign.status == status)
        if theme:
            query = query.filter(Campaign.theme["primary"].astext == theme)
        if owner:
            query = query.filter(Campaign.owner_id == owner)

        total = query.count()
        campaigns = query.offset(offset).limit(limit).all()

        return [
            CampaignSummary(
                id=c.id,
                name=c.name,
                concept=c.concept,
                status=c.status,
                created_at=c.created_at,
                updated_at=c.updated_at,
                type=c.type,
                theme=c.theme.get("primary"),
                metrics=c.get_metrics(),
                current_chapter=c.current_chapter.dict() if c.current_chapter else None
            )
            for c in campaigns
        ]
    except Exception as e:
        logger.error("Failed to list campaigns", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list campaigns"
        )


@router.get("/{campaign_id}", response_model=CampaignDetail)
async def get_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    version: Optional[str] = None,
) -> CampaignDetail:
    """Get campaign details."""
    try:
        campaign = db.query(Campaign).get(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )

        # Get specific version if requested
        if version:
            version_control: VersionControlService = Depends(get_version_control)
            version_data = version_control.get_version(version)
            if not version_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Version not found"
                )
            return CampaignDetail(**version_data.content)

        return CampaignDetail(
            id=campaign.id,
            name=campaign.name,
            concept=campaign.concept,
            status=campaign.status,
            config=campaign.config,
            metrics=campaign.get_metrics(),
            theme=campaign.theme,
            current_chapter=campaign.current_chapter.dict() if campaign.current_chapter else None,
            chapters=[c.dict() for c in campaign.chapters],
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            metadata=campaign.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get campaign", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get campaign"
        )


@router.patch("/{campaign_id}", response_model=CampaignDetail)
async def update_campaign(
    campaign_id: UUID,
    request: UpdateCampaignRequest,
    db: Session = Depends(get_db),
    campaign_factory: CampaignFactory = Depends(get_campaign_factory),
    version_control: VersionControlService = Depends(get_version_control),
) -> CampaignDetail:
    """Update campaign details."""
    try:
        campaign = db.query(Campaign).get(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )

        # Create new version with updates
        updates = request.dict(exclude_unset=True)
        content = campaign.dict()
        content.update(updates)

        version = version_control.create_version(
            campaign_id=campaign_id,
            content=content,
            title=f"Update campaign {campaign.name}",
            message=request.commit_message,
            author=request.author,
            version_type="update"
        )

        # Apply updates
        for key, value in updates.items():
            setattr(campaign, key, value)
        db.commit()

        return CampaignDetail(
            id=campaign.id,
            name=campaign.name,
            concept=campaign.concept,
            status=campaign.status,
            config=campaign.config,
            metrics=campaign.get_metrics(),
            theme=campaign.theme,
            current_chapter=campaign.current_chapter.dict() if campaign.current_chapter else None,
            chapters=[c.dict() for c in campaign.chapters],
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            metadata=campaign.metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update campaign", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update campaign"
        )


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    hard_delete: bool = False,
) -> Response:
    """Delete a campaign."""
    try:
        campaign = db.query(Campaign).get(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )

        if hard_delete:
            db.delete(campaign)
        else:
            campaign.is_deleted = True
            campaign.deleted_at = datetime.utcnow()

        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete campaign", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete campaign"
        )


@router.post("/generate", response_model=GenerationResult)
async def generate_campaign(
    request: GenerateCampaignRequest,
    db: Session = Depends(get_db),
    campaign_factory: CampaignFactory = Depends(get_campaign_factory),
) -> GenerationResult:
    """Generate a campaign using AI."""
    try:
        campaign_id, campaign = await campaign_factory.create_campaign(
            CreateCampaignRequest(
                name=f"Generated Campaign - {datetime.utcnow().isoformat()}",
                concept=request.prompt.concept,
                config=request.config,
                theme=request.theme_id,
                generation_flags=request.metadata.get("generation_flags", {})
            )
        )
        return GenerationResult(
            campaign=CampaignDetail(
                id=campaign_id,
                name=campaign.name,
                concept=campaign.concept,
                status=campaign.status,
                config=campaign.config,
                metrics=campaign.get_metrics(),
                theme=campaign.theme,
                current_chapter=campaign.current_chapter.dict() if campaign.current_chapter else None,
                chapters=[c.dict() for c in campaign.chapters],
                created_at=campaign.created_at,
                updated_at=campaign.updated_at,
                metadata=campaign.metadata
            ),
            generation_notes=request.prompt.concept,
            suggested_themes=request.prompt.themes,
            metadata=request.metadata
        )
    except Exception as e:
        logger.error("Failed to generate campaign", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{campaign_id}/progress", response_model=CampaignProgress)
async def get_campaign_progress(
    campaign_id: UUID,
    db: Session = Depends(get_db),
) -> CampaignProgress:
    """Get campaign progress information."""
    try:
        campaign = db.query(Campaign).get(campaign_id)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )

        metrics = campaign.get_metrics()
        return CampaignProgress(
            campaign_id=campaign_id,
            metrics=metrics,
            current_chapter=campaign.current_chapter.summary() if campaign.current_chapter else None,
            next_milestone=campaign.get_next_milestone(),
            completion_status=campaign.get_completion_status(),
            recent_events=campaign.get_recent_events(),
            achievements=campaign.get_achievements()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get campaign progress", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get campaign progress"
        )
