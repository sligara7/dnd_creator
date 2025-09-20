"""Storage schema migration models."""

from typing import List

from pydantic import BaseModel, Field

class CollectionSchema(BaseModel):
    """Schema definition for a collection."""
    name: str = Field(..., description="Collection name")
    indexes: List[str] = Field(default_factory=list, description="List of fields to index")

class SchemaVersion(BaseModel):
    """Schema version information."""
    major: int = 1
    minor: int = 0
    patch: int = 0

class DatabaseSchema(BaseModel):
    """Complete database schema definition."""
    version: SchemaVersion = Field(default_factory=SchemaVersion)
    collections: List[CollectionSchema] = Field(...)