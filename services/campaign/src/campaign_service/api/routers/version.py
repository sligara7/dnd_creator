"""Version control API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from campaign_service.core.exceptions import StateError, ValidationError, VersionControlError
from campaign_service.core.logging import get_logger
from campaign_service.models.version import BranchType, VersionType
from campaign_service.schemas.version import (
    BranchCreate,
    BranchList,
    BranchMerge,
    BranchRead,
    VersionCreate,
    VersionList,
    VersionRead,
)
from campaign_service.services.dependencies import (
    get_state_tracking,
    get_version_control,
)

router = APIRouter(tags=["version-control"])
logger = get_logger(__name__)


@router.post(
    "/campaigns/{campaign_id}/versions",
    response_model=VersionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_version(
    campaign_id: UUID,
    branch_id: UUID,
    request: VersionCreate,
    version_control = Depends(get_version_control),  # type: ignore
) -> VersionRead:
    """Create a new version.

    Args:
        campaign_id (UUID): Campaign ID
        branch_id (UUID): Branch ID
        request (VersionCreate): Version creation request
        version_control (VersionControlService): Version control service

    Returns:
        VersionRead: Created version

    Raises:
        HTTPException: If creation fails
    """
    try:
        version = await version_control.create_version(
            campaign_id=campaign_id,
            branch_id=branch_id,
            content=request.content,
            title=request.title,
            message=request.message,
            author=request.author,
            version_type=request.version_type,
            metadata=request.metadata,
        )
        return VersionRead.from_orm(version)

    except ValidationError as e:
        logger.warning("Version validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except VersionControlError as e:
        logger.error("Version creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Version creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create version",
        )


@router.get("/campaigns/{campaign_id}/versions", response_model=VersionList)
async def list_versions(
    campaign_id: UUID,
    branch_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    version_control = Depends(get_version_control),  # type: ignore
) -> VersionList:
    """List versions.

    Args:
        campaign_id (UUID): Campaign ID
        branch_id (Optional[UUID], optional): Branch ID. Defaults to None.
        skip (int, optional): Number of records to skip. Defaults to 0.
        limit (int, optional): Maximum number of records. Defaults to 100.
        version_control (VersionControlService): Version control service

    Returns:
        VersionList: List of versions

    Raises:
        HTTPException: If listing fails
    """
    try:
        versions = await version_control.get_version_history(
            campaign_id=campaign_id,
            branch_id=branch_id,
            skip=skip,
            limit=limit,
        )
        total = len(versions)  # This should be improved with a count query

        return VersionList(
            items=[VersionRead.from_orm(v) for v in versions],
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.error("Failed to list versions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list versions",
        )


@router.post("/campaigns/{campaign_id}/branches", response_model=BranchRead)
async def create_branch(
    campaign_id: UUID,
    request: BranchCreate,
    version_control = Depends(get_version_control),  # type: ignore
) -> BranchRead:
    """Create a new branch.

    Args:
        campaign_id (UUID): Campaign ID
        request (BranchCreate): Branch creation request
        version_control (VersionControlService): Version control service

    Returns:
        BranchRead: Created branch

    Raises:
        HTTPException: If creation fails
    """
    try:
        branch = await version_control.create_branch(
            campaign_id=campaign_id,
            name=request.name,
            branch_type=request.branch_type,
            description=request.description,
            base_version_hash=request.base_version_hash,
            parent_branch_id=request.parent_branch_id,
            metadata=request.metadata,
        )
        return BranchRead.from_orm(branch)

    except ValidationError as e:
        logger.warning("Branch validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except VersionControlError as e:
        logger.error("Branch creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Branch creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create branch",
        )


@router.get("/campaigns/{campaign_id}/branches", response_model=BranchList)
async def list_branches(
    campaign_id: UUID,
    branch_type: Optional[BranchType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    version_control = Depends(get_version_control),  # type: ignore
) -> BranchList:
    """List branches.

    Args:
        campaign_id (UUID): Campaign ID
        branch_type (Optional[BranchType], optional): Branch type. Defaults to None.
        skip (int, optional): Number of records to skip. Defaults to 0.
        limit (int, optional): Maximum number of records. Defaults to 100.
        version_control (VersionControlService): Version control service

    Returns:
        BranchList: List of branches

    Raises:
        HTTPException: If listing fails
    """
    try:
        branches = await version_control.get_branches(
            campaign_id=campaign_id,
            branch_type=branch_type,
            skip=skip,
            limit=limit,
        )
        total = len(branches)  # This should be improved with a count query

        return BranchList(
            items=[BranchRead.from_orm(b) for b in branches],
            total=total,
            skip=skip,
            limit=limit,
        )

    except Exception as e:
        logger.error("Failed to list branches", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list branches",
        )


@router.post(
    "/campaigns/{campaign_id}/branches/merge",
    response_model=VersionRead,
)
async def merge_branches(
    campaign_id: UUID,
    request: BranchMerge,
    version_control = Depends(get_version_control),  # type: ignore
) -> VersionRead:
    """Merge two branches.

    Args:
        campaign_id (UUID): Campaign ID
        request (BranchMerge): Merge request
        version_control (VersionControlService): Version control service

    Returns:
        VersionRead: Merge version

    Raises:
        HTTPException: If merge fails
    """
    try:
        merge_version = await version_control.merge_branches(
            campaign_id=campaign_id,
            source_branch_id=request.source_branch_id,
            target_branch_id=request.target_branch_id,
            author=request.author,
            message=request.message,
            metadata=request.metadata,
        )
        return VersionRead.from_orm(merge_version)

    except ValidationError as e:
        logger.warning("Merge validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except VersionControlError as e:
        logger.error("Branch merge failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Branch merge failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to merge branches",
        )
