"""Bulk operations API endpoints."""
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Body,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.services.bulk_operations import BulkOperationService
from character_service.api.v2.dependencies import (
    get_db,
    get_current_user,
)
from character_service.api.v2.models.bulk import (
    BulkCharacterCreate,
    BulkOperationStatus,
    BulkOperationResult,
    BulkValidateRequest,
    BulkValidationResponse,
)


router = APIRouter(prefix="/api/v2/characters/bulk", tags=["bulk"])


@router.post(
    "/create",
    response_model=BulkOperationResult,
    summary="Create characters in bulk",
    description="Create multiple characters in a single request",
    response_description="Batch creation result",
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_characters(
    request: BulkCharacterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> BulkOperationResult:
    """Create multiple characters in bulk.

    Args:
        request: Bulk creation request
        db: Database session
        current_user: Current user ID

    Returns:
        Operation result details
    """
    service = BulkOperationService(db)

    # Start bulk creation
    batch_id, initial_status = await service.create_characters(
        characters=[char.dict() for char in request.characters],
        batch_label=request.batch_label,
        campaign_id=request.campaign_id,
        theme_id=request.theme_id,
        created_by=request.created_by,
    )

    return BulkOperationResult(
        total_count=initial_status.total_count,
        success_count=initial_status.success_count,
        error_count=initial_status.error_count,
        created=initial_status.created,
        errors=initial_status.errors,
        batch_id=batch_id,
    )


@router.get(
    "/status/{batch_id}",
    response_model=BulkOperationStatus,
    summary="Get bulk operation status",
    description="Get the current status of a bulk operation",
    response_description="Operation status details",
    status_code=status.HTTP_200_OK,
)
async def get_operation_status(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> BulkOperationStatus:
    """Get bulk operation status.

    Args:
        batch_id: The batch ID to check
        db: Database session
        current_user: Current user ID

    Returns:
        Operation status details

    Raises:
        HTTPException: If batch not found
    """
    service = BulkOperationService(db)
    operation_status = await service.get_operation_status(batch_id)

    if not operation_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch {batch_id} not found",
        )

    return operation_status


@router.post(
    "/validate",
    response_model=BulkValidationResponse,
    summary="Validate characters in bulk",
    description="Validate multiple characters without creating them",
    response_description="Validation results",
    status_code=status.HTTP_200_OK,
)
async def validate_characters(
    request: BulkValidateRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> BulkValidationResponse:
    """Validate multiple characters.

    Args:
        request: Validation request
        db: Database session
        current_user: Current user ID

    Returns:
        Validation results
    """
    service = BulkOperationService(db)

    # Run validation
    results = await service.validate_characters(
        characters=request.characters,
        campaign_id=request.campaign_id,
        theme_id=request.theme_id,
        validation_rules=request.validation_rules,
    )

    # Calculate summary
    valid_count = sum(1 for r in results if r.is_valid)
    invalid_count = len(results) - valid_count

    return BulkValidationResponse(
        total_count=len(results),
        valid_count=valid_count,
        invalid_count=invalid_count,
        results=results,
    )
