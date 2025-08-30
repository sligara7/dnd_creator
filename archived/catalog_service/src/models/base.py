"""
Base models for the Catalog Service.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID, uuid4


class ContentType(str, Enum):
    ITEM = "item"
    SPELL = "spell"
    MONSTER = "monster"
    CUSTOM = "custom"


class ContentSource(str, Enum):
    OFFICIAL = "official"
    CUSTOM = "custom"


class ThemeData(BaseModel):
    """Theme-related data for content items."""
    themes: List[str] = Field(default_factory=list)
    adaptations: Dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    """Content validation result."""
    balance_score: float = 0.0
    consistency_check: bool = False
    last_validated: datetime = Field(default_factory=datetime.utcnow)
    issues: List[Dict[str, Any]] = Field(default_factory=list)


class ContentMetadata(BaseModel):
    """Metadata for content items."""
    version: str = "1.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None


class BaseContent(BaseModel):
    """Base model for all catalog content."""
    id: UUID = Field(default_factory=uuid4)
    type: ContentType
    name: str
    source: ContentSource
    description: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    metadata: ContentMetadata = Field(default_factory=ContentMetadata)
    theme_data: ThemeData = Field(default_factory=ThemeData)
    validation: ValidationResult = Field(default_factory=ValidationResult)
