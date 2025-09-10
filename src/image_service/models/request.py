"""
Request models for the Image Service.
"""

from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class PortraitRequest(BaseModel):
    """Request model for character portrait generation."""
    character_id: UUID
    style: str = Field(..., description="Style of the portrait (e.g. realistic, anime, etc.)")
    description: str = Field(..., description="Basic description of the character")
    prompt_details: Dict[str, str | List[str]] = Field(
        default_factory=dict,
        description="Additional details for the image generation prompt"
    )
