"""Content validation API endpoints."""
from fastapi import APIRouter, Depends

from llm_service.core.exceptions import ValidationError
from llm_service.schemas.validation import ValidationRequest, ValidationResponse
from llm_service.services.validation import ValidationService

router = APIRouter(prefix="/validation", tags=["validation"])


@router.post("/content", response_model=ValidationResponse)
async def validate_content(
    request: ValidationRequest,
    validation_service: ValidationService = Depends(),
) -> ValidationResponse:
    """Validate content against specified rules.

    Args:
        request: Content validation request
        validation_service: Content validation service

    Returns:
        Validation results with scores and issues

    Raises:
        ValidationError: If validation fails
    """
    try:
        return await validation_service.validate_content(request)
    except Exception as e:
        raise ValidationError(
            message=f"Content validation failed: {str(e)}",
            details={"content_type": request.content_type},
        ) from e
