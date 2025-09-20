"""Storage operation message models for Message Hub communication."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

class StorageOperation(str, Enum):
    """Storage operation types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SCHEMA_INIT = "schema_init"  # For schema initialization
    QUERY = "query"  # For search operations

class CollectionIndex(BaseModel):
    """Collection index definition."""
    fields: List[str] = Field(..., description="Fields to index")
    unique: bool = Field(False, description="Whether the index is unique")
    sparse: bool = Field(False, description="Whether the index is sparse")

class CollectionSchema(BaseModel):
    """Collection schema definition."""
    indexes: Dict[str, CollectionIndex] = Field(
        default_factory=dict,
        description="Index definitions for the collection"
    )
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional collection options"
    )

class SchemaDefinition(BaseModel):
    """Database schema definition."""
    version: str = Field("1.0.0", description="Schema version")
    collections: Dict[str, CollectionSchema] = Field(
        ...,
        description="Collection definitions"
    )

class StorageRequest(BaseModel):
    """Storage operation request message."""
    operation: StorageOperation = Field(..., description="Operation type")
    database: str = Field(
        "catalog_db",
        description="Target database name"
    )
    collection: str = Field(..., description="Target collection name")
    request_id: UUID = Field(..., description="Request correlation ID")
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Operation data payload"
    )
    entity_id: Optional[UUID] = Field(
        None,
        description="Target entity ID"
    )
    schema: Optional[SchemaDefinition] = Field(
        None,
        description="Schema definition for initialization"
    )
    query: Optional[Dict[str, Any]] = Field(
        None,
        description="Query parameters for search"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "read",
                "database": "catalog_db",
                "collection": "items",
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "entity_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }

class StorageResponse(BaseModel):
    """Storage operation response message."""
    request_id: UUID = Field(..., description="Matching request correlation ID")
    success: bool = Field(..., description="Operation success status")
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Response data payload"
    )
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "success": True,
                "data": {
                    "id": "123e4567-e89b-12d3-a456-426614174001",
                    "name": "Sword"
                },
                "timestamp": "2025-09-20T21:32:11Z"
            }
        }
