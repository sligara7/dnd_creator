"""Version control API endpoints."""
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Path,
    Body,
    Response,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.services.version_control import VersionControlService
from character_service.domain.version import ChangeSource
from character_service.api.v2.dependencies import (
    get_db,
    get_current_user,
    require_character_access,
)
from character_service.api.v2.models.version import (
    VersionResponse,
    VersionListResponse,
    VersionCompareResponse,
    VersionTreeNode,
    VersionRestoreRequest,
    MilestoneRequest,
    MilestoneResponse,
)


router = APIRouter(
    prefix="/api/v2/characters/{character_id}/versions",
    tags=["versions"],
)


@router.get(
    "",
    response_model=VersionListResponse,
    summary="Get version history",
    description="Get version history for a character",
    response_description="List of character versions",
    status_code=status.HTTP_200_OK,
)
async def get_versions(
    character_id: UUID = Path(..., description="Character ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of versions to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
    _: None = Depends(require_character_access),
) -> VersionListResponse:
    """Get version history for a character.

    Args:
        character_id: Character ID
        limit: Maximum number of versions to return
        offset: Offset for pagination
        db: Database session
        current_user: Current user ID
        _: Character access check

    Returns:
        Version list response
    """
    service = VersionControlService(db)
    versions, total = await service.get_version_history(
        character_id=character_id,
        limit=limit,
        offset=offset,
    )

    # Convert to response format
    version_data = []
    for version in versions:
        metadata = await service.repository.get_version_metadata(version.id)
        version_data.append(
            VersionResponse(
                id=version.id,
                character_id=version.character_id,
                parent_version_id=version.parent_version_id,
                label=version.label,
                description=version.description,
                is_active=version.is_active,
                created_at=version.created_at,
                created_by=version.created_by,
                metadata=metadata.metadata if metadata else None,
            )
        )

    return VersionListResponse(
        versions=version_data,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{version_id}",
    response_model=VersionResponse,
    summary="Get version details",
    description="Get details for a specific version",
    response_description="Version details",
    status_code=status.HTTP_200_OK,
)
async def get_version(
    character_id: UUID = Path(..., description="Character ID"),
    version_id: UUID = Path(..., description="Version ID"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
    _: None = Depends(require_character_access),
) -> VersionResponse:
    """Get version details.

    Args:
        character_id: Character ID
        version_id: Version ID
        db: Database session
        current_user: Current user ID
        _: Character access check

    Returns:
        Version details response

    Raises:
        HTTPException: If version not found
    """
    service = VersionControlService(db)
    version = await service.repository.get_version(
        version_id=version_id,
        character_id=character_id,
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    metadata = await service.repository.get_version_metadata(version.id)
    return VersionResponse(
        id=version.id,
        character_id=version.character_id,
        parent_version_id=version.parent_version_id,
        label=version.label,
        description=version.description,
        is_active=version.is_active,
        created_at=version.created_at,
        created_by=version.created_by,
        metadata=metadata.metadata if metadata else None,
    )


@router.get(
    "/{version_id}/state",
    response_model=Dict[str, Any],
    summary="Get version state",
    description="Get the complete character state at a specific version",
    response_description="Character state",
    status_code=status.HTTP_200_OK,
)
async def get_version_state(
    character_id: UUID = Path(..., description="Character ID"),
    version_id: UUID = Path(..., description="Version ID"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
    _: None = Depends(require_character_access),
) -> Dict[str, Any]:
    """Get character state at a specific version.

    Args:
        character_id: Character ID
        version_id: Version ID
        db: Database session
        current_user: Current user ID
        _: Character access check

    Returns:
        Complete character state

    Raises:
        HTTPException: If version not found
    """
    service = VersionControlService(db)
    version = await service.repository.get_version(
        version_id=version_id,
        character_id=character_id,
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    return version.state


@router.get(
    "/diff",
    response_model=VersionCompareResponse,
    summary="Compare versions",
    description="Compare two character versions",
    response_description="Version differences",
    status_code=status.HTTP_200_OK,
)
async def compare_versions(
    character_id: UUID = Path(..., description="Character ID"),
    version_a: UUID = Query(..., description="First version ID"),
    version_b: UUID = Query(..., description="Second version ID"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
    _: None = Depends(require_character_access),
) -> VersionCompareResponse:
    """Compare two versions.

    Args:
        character_id: Character ID
        version_a: First version ID
        version_b: Second version ID
        db: Database session
        current_user: Current user ID
        _: Character access check

    Returns:
        Version differences response

    Raises:
        HTTPException: If versions not found
    """
    service = VersionControlService(db)
    try:
        comparison = await service.compare_versions(
            version_a_id=version_a,
            version_b_id=version_b,
            character_id=character_id,
        )
        return VersionCompareResponse(
            version_a=version_a,
            version_b=version_b,
            diff=comparison["diff"],
            changes=comparison["changes"],
            metadata=comparison["metadata"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/tree",
    response_model=List[VersionTreeNode],
    summary="Get version tree",
    description="Get the version tree for a character",
    response_description="Version tree",
    status_code=status.HTTP_200_OK,
)
async def get_version_tree(
    character_id: UUID = Path(..., description="Character ID"),
    root_version_id: Optional[UUID] = Query(None, description="Optional root version ID"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
    _: None = Depends(require_character_access),
) -> List[VersionTreeNode]:
    """Get version tree.

    Args:
        character_id: Character ID
        root_version_id: Optional root version ID
        db: Database session
        current_user: Current user ID
        _: Character access check

    Returns:
        Version tree structure
    """
    service = VersionControlService(db)
    return await service.get_version_tree(
        character_id=character_id,
        root_version_id=root_version_id,
    )


@router.get(
    "/milestones",
    response_model=List[MilestoneResponse],
    summary="Get milestone versions",
    description="Get all milestone versions for a character",
    response_description="Milestone versions",
    status_code=status.HTTP_200_OK,
)
async def get_milestones(
    character_id: UUID = Path(..., description="Character ID"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
    _: None = Depends(require_character_access),
) -> List[MilestoneResponse]:
    """Get milestone versions.

    Args:
        character_id: Character ID
        db: Database session
        current_user: Current user ID
        _: Character access check

    Returns:
        List of milestone versions
    """
    service = VersionControlService(db)
    milestones = await service.get_milestones(character_id)

    return [
        MilestoneResponse(
            id=milestone["version"]["id"],
            version_id=milestone["version"]["id"],
            milestone_type=milestone["metadata"].get("milestone_type", "unknown"),
            label=milestone["version"]["label"] or "",
            description=milestone["version"]["description"],
            metadata=milestone["metadata"],
            created_at=milestone["version"]["created_at"],
        )
        for milestone in milestones
    ]


@router.post(
    "/{version_id}/restore",
    response_model=VersionResponse,
    summary="Restore version",
    description="Restore a character to a specific version",
    response_description="New version created from restore",
    status_code=status.HTTP_201_CREATED,
)
async def restore_version(
    character_id: UUID = Path(..., description="Character ID"),
    version_id: UUID = Path(..., description="Version ID to restore"),
    request: VersionRestoreRequest = Body(..., description="Restore request details"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
    _: None = Depends(require_character_access),
) -> VersionResponse:
    """Restore a character to a specific version.

    Args:
        character_id: Character ID
        version_id: Version ID to restore
        request: Restore request details
        db: Database session
        current_user: Current user ID
        _: Character access check

    Returns:
        Newly created version response

    Raises:
        HTTPException: If version not found
    """
    service = VersionControlService(db)
    source_version = await service.repository.get_version(
        version_id=version_id,
        character_id=character_id,
    )

    if not source_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    # Create new version from source state
    version = await service.create_version(
        character_id=character_id,
        current_state=source_version.state,
        parent_version_id=version_id,
        label=request.label or f"Restored from {version_id}",
        description=request.description,
        source=ChangeSource.USER,
        created_by=request.restored_by,
    )

    metadata = await service.repository.get_version_metadata(version.id)
    return VersionResponse(
        id=version.id,
        character_id=version.character_id,
        parent_version_id=version.parent_version_id,
        label=version.label,
        description=version.description,
        is_active=version.is_active,
        created_at=version.created_at,
        created_by=version.created_by,
        metadata=metadata.metadata if metadata else None,
    )


@router.post(
    "/{version_id}/milestone",
    response_model=MilestoneResponse,
    summary="Mark milestone",
    description="Mark a version as a milestone",
    response_description="Updated milestone metadata",
    status_code=status.HTTP_200_OK,
)
async def mark_milestone(
    character_id: UUID = Path(..., description="Character ID"),
    version_id: UUID = Path(..., description="Version ID"),
    request: MilestoneRequest = Body(..., description="Milestone request details"),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
    _: None = Depends(require_character_access),
) -> MilestoneResponse:
    """Mark a version as a milestone.

    Args:
        character_id: Character ID
        version_id: Version ID
        request: Milestone request details
        db: Database session
        current_user: Current user ID
        _: Character access check

    Returns:
        Updated milestone metadata response

    Raises:
        HTTPException: If version not found
    """
    service = VersionControlService(db)
    
    # Prepare milestone metadata
    metadata = {
        "milestone_type": request.milestone_type,
        "label": request.label,
        "description": request.description,
        **(request.metadata or {}),
    }

    version_metadata = await service.mark_milestone(
        version_id=version_id,
        character_id=character_id,
        milestone_metadata=metadata,
    )

    if not version_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    version = await service.repository.get_version(version_id, character_id)
    return MilestoneResponse(
        id=version_metadata.id,
        version_id=version_id,
        milestone_type=metadata["milestone_type"],
        label=metadata["label"],
        description=metadata.get("description"),
        metadata=version_metadata.metadata,
        created_at=version.created_at,
    )
