"""Base models for catalog content."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

class ContentType(str, Enum):
    """Valid content types for catalog entries."""
    ITEM = "item"
    SPELL = "spell"
    MONSTER = "monster"

class ContentSource(str, Enum):
    """Source of the content."""
    OFFICIAL = "official"
    CUSTOM = "custom"

class ThemeData(BaseModel):
    """Theme-related data for content."""
    themes: List[str] = Field(default_factory=list, description="List of theme names")
    adaptations: Dict[str, Any] = Field(default_factory=dict, description="Theme-specific adaptations")

class ValidationData(BaseModel):
    """Validation data for content."""
    balance_score: float = Field(0.0, description="Content balance score")
    consistency_check: bool = False
    last_validated: Optional[datetime] = None
    validation_notes: Dict[str, Any] = Field(default_factory=dict)

class Metadata(BaseModel):
    """Metadata for catalog content."""
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None

class BaseContent(BaseModel):
    """Base model for all catalog content."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    type: ContentType
    name: str = Field(..., min_length=1, max_length=100)
    source: ContentSource
    description: str = Field(..., min_length=1)
    properties: Dict[str, Any] = Field(default_factory=dict)
    metadata: Metadata = Field(default_factory=Metadata)
    theme_data: ThemeData = Field(default_factory=ThemeData)
    validation: ValidationData = Field(default_factory=ValidationData)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "item",
                "name": "Example Item",
                "source": "official",
                "description": "An example catalog item",
                "properties": {},
                "metadata": {
                    "version": "1.0.0",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                    "created_by": "system"
                },
                "theme_data": {
                    "themes": [],
                    "adaptations": {}
                },
                "validation": {
                    "balance_score": 0.0,
                    "consistency_check": False,
                    "last_validated": None,
                    "validation_notes": {}
                }
            }
        }