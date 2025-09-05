from typing import Any, Dict, Generic, List, Optional, TypeVar
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# Type variable for generic response models
T = TypeVar("T")


class SearchQuery(BaseModel):
    """Base search query model"""
    query: str = Field(..., description="Search query string")
    index_type: str = Field(..., description="Index type to search in")
    size: Optional[int] = Field(default=20, description="Number of results to return")
    offset: Optional[int] = Field(default=0, description="Offset for pagination")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Search filters")
    facets: Optional[List[str]] = Field(default=None, description="Facets to return")
    sort: Optional[Dict[str, str]] = Field(default=None, description="Sort order")
    highlight: Optional[bool] = Field(default=True, description="Enable highlighting")
    fuzzy: Optional[bool] = Field(default=True, description="Enable fuzzy matching")
    semantic: Optional[bool] = Field(default=False, description="Enable semantic search")
    explain: Optional[bool] = Field(default=False, description="Return explanation of results")


class SearchHit(BaseModel):
    """Individual search result hit"""
    id: UUID = Field(..., description="Document ID")
    index: str = Field(..., description="Index name")
    score: float = Field(..., description="Search relevance score")
    source: Dict[str, Any] = Field(..., description="Document source")
    highlight: Optional[Dict[str, List[str]]] = Field(default=None, description="Highlighted snippets")
    explanation: Optional[Dict[str, Any]] = Field(default=None, description="Score explanation")


class SearchResponse(BaseModel, Generic[T]):
    """Generic search response model"""
    total: int = Field(..., description="Total number of matching documents")
    took: int = Field(..., description="Search time in milliseconds")
    max_score: float = Field(..., description="Maximum score of results")
    hits: List[T] = Field(..., description="Search results")
    facets: Optional[Dict[str, Dict[str, int]]] = Field(default=None, description="Facet counts")
    suggest: Optional[Dict[str, List[str]]] = Field(default=None, description="Search suggestions")
    

class SuggestQuery(BaseModel):
    """Suggestion query model"""
    text: str = Field(..., description="Text to get suggestions for")
    index_type: str = Field(..., description="Index type to get suggestions from")
    size: Optional[int] = Field(default=5, description="Number of suggestions to return")
    fuzzy: Optional[bool] = Field(default=True, description="Enable fuzzy matching")


class SuggestResponse(BaseModel):
    """Suggestion response model"""
    suggestions: List[str] = Field(..., description="List of suggestions")
    took: int = Field(..., description="Time taken in milliseconds")


class IndexOperation(BaseModel):
    """Index operation model"""
    index_type: str = Field(..., description="Index type")
    operation: str = Field(..., description="Operation type (create/update/delete)")
    document_id: UUID = Field(..., description="Document ID")
    document: Optional[Dict[str, Any]] = Field(default=None, description="Document data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Operation timestamp")


class IndexResponse(BaseModel):
    """Index operation response model"""
    success: bool = Field(..., description="Operation success status")
    index: str = Field(..., description="Index name")
    document_id: UUID = Field(..., description="Document ID")
    result: str = Field(..., description="Operation result")
    version: Optional[int] = Field(default=None, description="Document version")
    took: int = Field(..., description="Operation time in milliseconds")


class BulkOperation(BaseModel):
    """Bulk operation model"""
    operations: List[IndexOperation] = Field(..., description="List of operations")


class BulkResponse(BaseModel):
    """Bulk operation response model"""
    took: int = Field(..., description="Total time taken in milliseconds")
    errors: bool = Field(..., description="Whether there were any errors")
    items: List[Dict[str, Any]] = Field(..., description="Operation results")


class ErrorResponse(BaseModel):
    """API error response model"""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    components: Dict[str, Dict[str, Any]] = Field(..., description="Component health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
