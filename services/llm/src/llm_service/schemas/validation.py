"""Schemas for content validation."""
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from llm_service.schemas.common import ContentMetadata


class ValidationCategory(str, Enum):
    """Content validation categories."""
    THEME = "theme"
    QUALITY = "quality"
    CONSISTENCY = "consistency"
    RULES = "rules"
    CUSTOM = "custom"


class ValidationRule(BaseModel):
    """Individual validation rule."""
    id: UUID = Field(description="Unique identifier for the rule")
    category: ValidationCategory
    name: str = Field(description="Rule name")
    description: str = Field(description="Rule description")
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        description="Rule-specific parameters"
    )
    is_required: bool = Field(
        default=True,
        description="Whether this rule must pass"
    )


class ValidationRequest(BaseModel):
    """Request for content validation."""
    content: str = Field(description="Content to validate")
    content_type: str = Field(description="Type of content being validated")
    rules: List[ValidationRule] = Field(description="Rules to apply")
    theme: Optional[Dict[str, str]] = Field(
        None,
        description="Theme parameters if validating theme consistency"
    )
    context: Optional[Dict[str, str]] = Field(
        None,
        description="Additional context for validation"
    )


class ValidationIssue(BaseModel):
    """Individual validation issue."""
    rule_id: UUID = Field(description="ID of the failed rule")
    severity: str = Field(description="Issue severity (error, warning, info)")
    message: str = Field(description="Issue description")
    location: Optional[str] = Field(
        None,
        description="Location of the issue in content"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions for fixing the issue"
    )


class ValidationResult(BaseModel):
    """Individual rule validation result."""
    rule_id: UUID = Field(description="Rule ID")
    passed: bool = Field(description="Whether the rule passed")
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Rule satisfaction score"
    )
    issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="Issues found by this rule"
    )


class ValidationResponse(BaseModel):
    """Response containing validation results."""
    content_id: UUID = Field(description="Content identifier")
    metadata: ContentMetadata = Field(description="Validation metadata")
    overall_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall validation score"
    )
    passed: bool = Field(description="Whether all required rules passed")
    results: List[ValidationResult] = Field(
        description="Individual rule results"
    )
    summary: str = Field(description="Validation summary")
