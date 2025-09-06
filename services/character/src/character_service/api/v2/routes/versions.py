"""Version control API endpoints."""
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.services.version_control import VersionControlService
from character_service.domain.version import (
    CharacterVersion,
    VersionMetadata,
    ChangeSource,
)
from character_service.api.v2.dependencies import get_db
from character_service.api.v2.models.version import (
    VersionResponse,
    VersionListResponse,
    VersionCompareResponse,
    VersionRestoreRequest,
)

router = APIRouter(prefix="/api/v2/characters/{character_id}/versions")


@router.get(
    "",
    response_model=VersionListResponse,
    summary="Get version history",
    description="Get version history for a character",
    response_description="List of character versions",
)
async def get_versions(
    character_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> VersionListResponse:
    """Get version history for a character.

    Args:
        character_id: Character ID
        limit: Maximum number of versions to return
        offset: Offset for pagination
        db: Database session

    Returns:
        List of character versions
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
)
async def get_version(
    character_id: UUID,
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> VersionResponse:
    """Get version details.

    Args:
        character_id: Character ID
        version_id: Version ID
        db: Database session

    Returns:
        Version details

    Raises:
        HTTPException: If version not found
    """
    service = VersionControlService(db)
    version = await service.repository.get_version(
        version_id=version_id,
        character_id=character_id,
    )

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

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
)
async def get_version_state(
    character_id: UUID,
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get character state at a specific version.

    Args:
        character_id: Character ID
        version_id: Version ID
        db: Database session

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
        raise HTTPException(status_code=404, detail="Version not found")

    return version.state


@router.get(
    "/diff",
    response_model=VersionCompareResponse,
    summary="Compare versions",
    description="Compare two character versions",
    response_description="Version differences",
)
async def compare_versions(
    character_id: UUID,
    version_a: UUID = Query(..., description="First version ID"),
    version_b: UUID = Query(..., description="Second version ID"),
    db: AsyncSession = Depends(get_db),
) -> VersionCompareResponse:
    """Compare two versions.

    Args:
        character_id: Character ID
        version_a: First version ID
        version_b: Second version ID
        db: Database session

    Returns:
        Version differences

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
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/tree",
    response_model=List[Dict[str, Any]],
    summary="Get version tree",
    description="Get the version tree for a character",
    response_description="Version tree",
)
async def get_version_tree(
    character_id: UUID,
    root_version_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Get version tree.

    Args:
        character_id: Character ID
        root_version_id: Optional root version ID
        db: Database session

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
    response_model=List[Dict[str, Any]],
    summary="Get milestone versions",
    description="Get all milestone versions for a character",
    response_description="Milestone versions",
)
async def get_milestones(
    character_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Get milestone versions.

    Args:
        character_id: Character ID
        db: Database session

    Returns:
        List of milestone versions
    """
    service = VersionControlService(db)
    return await service.get_milestones(character_id)


@router.post(
    "/{version_id}/restore",
    response_model=VersionResponse,
    summary="Restore version",
    description="Restore a character to a specific version",
    response_description="New version created from restore",
)
async def restore_version(
    character_id: UUID,
    version_id: UUID,
    request: VersionRestoreRequest,
    db: AsyncSession = Depends(get_db),
) -> VersionResponse:
    """Restore a character to a specific version.

    Args:
        character_id: Character ID
        version_id: Version ID to restore
        request: Restore request details
        db: Database session

    Returns:
        Newly created version

    Raises:
        HTTPException: If version not found
    """
    service = VersionControlService(db)
    source_version = await service.repository.get_version(
        version_id=version_id,
        character_id=character_id,
    )

    if not source_version:
        raise HTTPException(status_code=404, detail="Version not found")

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
    response_model=Dict[str, Any],
    summary="Mark milestone",
    description="Mark a version as a milestone",
    response_description="Updated version metadata",
)
async def mark_milestone(
    character_id: UUID,
    version_id: UUID,
    milestone_metadata: Optional[Dict[str, Any]] = None,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Mark a version as a milestone.

    Args:
        character_id: Character ID
        version_id: Version ID
        milestone_metadata: Optional milestone metadata
        db: Database session

    Returns:
        Updated version metadata

    Raises:
        HTTPException: If version not found
    """
    service = VersionControlService(db)
    metadata = await service.mark_milestone(
        version_id=version_id,
        character_id=character_id,
        milestone_metadata=milestone_metadata,
    )

    if not metadata:
        raise HTTPException(status_code=404, detail="Version not found")

    return {
        "id": str(metadata.id),
        "version_id": str(metadata.version_id),
        "is_milestone": metadata.is_milestone,
        "metadata": metadata.metadata,
    }
