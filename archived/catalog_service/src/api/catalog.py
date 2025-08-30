"""
FastAPI routes for the Catalog Service.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field

from ..models.base import BaseContent, ContentType, ContentSource, ValidationResult
from ..services.catalog import CatalogService
from ..core.dependencies import get_catalog_service


router = APIRouter()


class CreateContentRequest(BaseModel):
    """Request model for content creation."""
    name: str
    description: str
    properties: Dict[str, Any]
    source: ContentSource = ContentSource.CUSTOM
    themes: List[str] = Field(default_factory=list)


class UpdateContentRequest(BaseModel):
    """Request model for content updates."""
    name: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    themes: Optional[List[str]] = None


class SearchResponse(BaseModel):
    """Response model for search results."""
    total: int
    page: int
    items: List[Dict[str, Any]]


class ValidationRequest(BaseModel):
    """Request model for content validation."""
    content: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class ThemeRequest(BaseModel):
    """Request model for theme application."""
    theme: str
    strength: float = 1.0
    preserve: List[str] = Field(default_factory=list)


@router.get("/api/v2/catalog/{type}/{id}", response_model=BaseContent)
async def get_content(
    content_id: UUID = Path(..., alias="id"),
    catalog: CatalogService = Depends(get_catalog_service)
):
    """Get content by ID."""
    content = await catalog.get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


@router.post("/api/v2/catalog/{type}", response_model=BaseContent)
async def create_content(
    content_type: ContentType = Path(..., alias="type"),
    request: CreateContentRequest,
    catalog: CatalogService = Depends(get_catalog_service)
):
    """Create new content."""
    try:
        content = await catalog.create_content(
            content_type=content_type,
            name=request.name,
            description=request.description,
            properties=request.properties,
            source=request.source,
            themes=request.themes
        )
        return content
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/api/v2/catalog/{type}/{id}", response_model=BaseContent)
async def update_content(
    content_id: UUID = Path(..., alias="id"),
    request: UpdateContentRequest,
    catalog: CatalogService = Depends(get_catalog_service)
):
    """Update existing content."""
    updates = request.dict(exclude_unset=True)
    content = await catalog.update_content(content_id, updates)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content


@router.delete("/api/v2/catalog/{type}/{id}")
async def delete_content(
    content_id: UUID = Path(..., alias="id"),
    catalog: CatalogService = Depends(get_catalog_service)
):
    """Delete content."""
    success = await catalog.delete_content(content_id)
    if not success:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"status": "deleted"}


@router.get("/api/v2/catalog/search", response_model=SearchResponse)
async def search_content(
    q: Optional[str] = None,
    type: Optional[ContentType] = None,
    themes: Optional[List[str]] = Query(None),
    page: int = Query(1, gt=0),
    size: int = Query(20, gt=0, le=100),
    catalog: CatalogService = Depends(get_catalog_service)
):
    """Search the catalog."""
    return await catalog.search_content(
        query=q,
        content_type=type,
        themes=themes,
        page=page,
        size=size
    )


@router.get("/api/v2/catalog/recommend")
async def get_recommendations(
    character_id: Optional[UUID] = None,
    campaign_id: Optional[UUID] = None,
    type: Optional[ContentType] = None,
    limit: int = Query(10, gt=0, le=100),
    catalog: CatalogService = Depends(get_catalog_service)
):
    """Get content recommendations."""
    return await catalog.get_recommendations(
        character_id=character_id,
        campaign_id=campaign_id,
        content_type=type,
        limit=limit
    )


@router.post("/api/v2/catalog/validate", response_model=ValidationResult)
async def validate_content(
    request: ValidationRequest,
    catalog: CatalogService = Depends(get_catalog_service)
):
    """Validate content."""
    try:
        # Create temporary content object for validation
        content_type = ContentType(request.content["type"])
        content = catalog._content_type_map[content_type](**request.content)
        return await catalog._validate_content(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/v2/catalog/theme/apply", response_model=BaseContent)
async def apply_theme(
    content_id: UUID,
    request: ThemeRequest,
    catalog: CatalogService = Depends(get_catalog_service)
):
    """Apply theme to content."""
    content = await catalog.apply_theme(
        content_id=content_id,
        theme=request.theme,
        strength=request.strength,
        preserve=request.preserve
    )
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content
