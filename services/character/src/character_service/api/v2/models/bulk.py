"""Bulk operations API models."""
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, constr

from character_service.api.v2.models.character import (
    CharacterCreate,
    CharacterResponse,
    ValidationError,
)


class BulkCharacterCreate(BaseModel):
    """Request model for bulk character creation."""

    characters: List[CharacterCreate] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="List of characters to create",
    )
    batch_label: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional label for the batch",
    )
    campaign_id: Optional[UUID] = Field(
        None,
        description="Optional campaign ID for all characters",
    )
    theme_id: Optional[UUID] = Field(
        None,
        description="Optional theme ID to apply to all characters",
    )
    created_by: constr(min_length=1, max_length=255) = Field(
        ...,
        description="Who/what is creating these characters",
    )


class BulkValidationError(BaseModel):
    """Model for bulk validation errors."""

    index: int
    character_id: Optional[UUID] = None
    errors: List[ValidationError]


class BulkOperationResult(BaseModel):
    """Response model for bulk operations."""

    total_count: int
    success_count: int
    error_count: int
    created: List[CharacterResponse]
    errors: List[BulkValidationError]
    batch_id: UUID


class BulkValidateRequest(BaseModel):
    """Request model for bulk validation."""

    characters: List[Dict[str, Any]] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="List of character data to validate",
    )
    campaign_id: Optional[UUID] = Field(
        None,
        description="Optional campaign ID for validation context",
    )
    theme_id: Optional[UUID] = Field(
        None,
        description="Optional theme ID for validation context",
    )
    validation_rules: Optional[List[str]] = Field(
        None,
        description="Optional list of specific rules to validate",
    )


class ValidationResult(BaseModel):
    """Model for individual validation result."""

    index: int
    character_id: Optional[UUID] = None
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]


class BulkValidationResponse(BaseModel):
    """Response model for bulk validation."""

    total_count: int
    valid_count: int
    invalid_count: int
    results: List[ValidationResult]


class BulkOperationStatus(BaseModel):
    """Model for bulk operation status."""

    batch_id: UUID
    status: str = Field(
        ...,
        description="Status of the bulk operation",
        examples=["pending", "processing", "completed", "failed"],
    )
    progress: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Progress of the operation (0.0 to 1.0)",
    )
    total_count: int
    processed_count: int
    success_count: int
    error_count: int
    created: List[CharacterResponse]
    errors: List[BulkValidationError]
    started_at: str
    completed_at: Optional[str] = None
