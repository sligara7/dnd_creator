"""Version control API router."""
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from ...core.db import get_db
from ...core.logging import get_logger
from ...services.version_control import VersionControlService
from ..schemas.version import (
    VersionType,
    BranchType,
    MergeStrategy,
    CreateBranchRequest,
    BranchInfo,
    MergeRequest,
    MergeRequestInfo,
    MergeResponse,
)
from ..dependencies import get_version_control

router = APIRouter(prefix="/versions", tags=["versions"])
logger = get_logger(__name__)


@router.get("")
async def list_versions(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    version_control: VersionControlService = Depends(get_version_control),
    branch: Optional[str] = None,
    max_count: Optional[int] = None,
) -> List[Dict]:
    """List versions with optional filters."""
    try:
        versions = version_control.get_version_history(
            campaign_id,
            branch,
            max_count
        )
        return [v.dict() for v in versions]
    except Exception as e:
        logger.error("Failed to list versions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list versions"
        )


@router.get("/{version_hash}")
async def get_version(
    version_hash: str,
    db: Session = Depends(get_db),
    version_control: VersionControlService = Depends(get_version_control),
    with_content: bool = True,
) -> Dict:
    """Get version details."""
    try:
        version = version_control.get_version(version_hash, with_content)
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found"
            )
        return version.dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get version", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get version"
        )


@router.post("/branches", response_model=BranchInfo)
async def create_branch(
    request: CreateBranchRequest,
    db: Session = Depends(get_db),
    version_control: VersionControlService = Depends(get_version_control),
) -> BranchInfo:
    """Create a new branch."""
    try:
        branch = await version_control.create_branch(
            request.campaign_id,
            request.name,
            request.start_point,
            request.type,
            request.description,
            request.metadata
        )
        return BranchInfo.from_orm(branch)
    except Exception as e:
        logger.error("Failed to create branch", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/branches")
async def list_branches(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    version_control: VersionControlService = Depends(get_version_control),
    branch_type: Optional[BranchType] = None,
    include_merged: bool = False,
) -> List[BranchInfo]:
    """List branches with optional filters."""
    try:
        query = db.query(Branch).filter_by(campaign_id=campaign_id)
        if branch_type:
            query = query.filter_by(type=branch_type)
        if not include_merged:
            query = query.filter_by(is_merged=False)
        branches = query.all()
        return [BranchInfo.from_orm(b) for b in branches]
    except Exception as e:
        logger.error("Failed to list branches", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list branches"
        )


@router.post("/merge-requests", response_model=MergeRequestInfo)
async def create_merge_request(
    request: MergeRequest,
    db: Session = Depends(get_db),
    version_control: VersionControlService = Depends(get_version_control),
) -> MergeRequestInfo:
    """Create a merge request."""
    try:
        merge_request = await version_control.create_merge_request(
            request.campaign_id,
            request.source_branch,
            request.target_branch,
            request.title,
            request.description,
            request.author,
            request.reviewers,
            request.metadata
        )
        return MergeRequestInfo.from_orm(merge_request)
    except Exception as e:
        logger.error("Failed to create merge request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/merge-requests/{merge_request_id}", response_model=MergeRequestInfo)
async def get_merge_request(
    merge_request_id: UUID,
    db: Session = Depends(get_db),
    version_control: VersionControlService = Depends(get_version_control),
) -> MergeRequestInfo:
    """Get merge request details."""
    try:
        mr = db.query(MergeRequest).get(merge_request_id)
        if not mr:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Merge request not found"
            )
        return MergeRequestInfo.from_orm(mr)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get merge request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get merge request"
        )


@router.post("/merge-requests/{merge_request_id}/merge", response_model=MergeResponse)
async def merge_branches(
    merge_request_id: UUID,
    strategy: MergeStrategy,
    message: str,
    author: str,
    db: Session = Depends(get_db),
    version_control: VersionControlService = Depends(get_version_control),
    resolution_data: Optional[Dict] = None,
) -> MergeResponse:
    """Merge branches via merge request."""
    try:
        merge_version = await version_control.merge_branches(
            merge_request_id,
            strategy,
            message,
            author,
            resolution_data
        )
        return MergeResponse(
            success=True,
            merge_version=merge_version.hash
        )
    except Exception as e:
        logger.error("Failed to merge branches", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/merge-requests/{merge_request_id}/resolve-conflicts")
async def resolve_conflicts(
    merge_request_id: UUID,
    resolutions: Dict[str, Dict],
    db: Session = Depends(get_db),
    version_control: VersionControlService = Depends(get_version_control),
) -> Dict:
    """Resolve merge conflicts."""
    try:
        conflicts = await version_control.resolve_conflicts(
            merge_request_id,
            resolutions
        )
        return {
            "success": True,
            "resolved_count": len(resolutions),
            "conflicts": [c.dict() for c in conflicts]
        }
    except Exception as e:
        logger.error("Failed to resolve conflicts", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
