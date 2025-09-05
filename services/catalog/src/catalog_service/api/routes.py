from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from catalog_service.api.dependencies import get_catalog_service
from catalog_service.domain.models import (
    BaseContent,
    ContentType,
    Item,
    Monster,
    Spell,
    ValidationResult,
)
from catalog_service.service.catalog_service import CatalogService

api_router = APIRouter()

class ContentCreate(BaseModel):
    """Request model for content creation"""
    name: str
    source: str
    description: str
    properties: Dict
    theme_data: Optional[Dict] = None


class ContentUpdate(BaseModel):
    """Request model for content updates"""
    name: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[Dict] = None
    theme_data: Optional[Dict] = None


class ThemeApplication(BaseModel):
    """Request model for theme application"""
    theme: str
    strength: float = 1.0
    preserve: Optional[List[str]] = None


class SearchQuery(BaseModel):
    """Request model for advanced search"""
    query: str
    filters: Optional[Dict] = None
    sort: Optional[Dict] = None
    page: int = 1
    size: int = 20


@api_router.get("/catalog/{type}/{id}", response_model=BaseContent)
async def get_content(
    type: ContentType,
    id: UUID,
    service: CatalogService = Depends(get_catalog_service),
) -> BaseContent:
    """Get content item by ID"""
    return await service.get_content(type, id)


@api_router.post("/catalog/{type}", response_model=BaseContent)
async def create_content(
    type: ContentType,
    content: ContentCreate,
    service: CatalogService = Depends(get_catalog_service),
) -> BaseContent:
    """Create new content item"""
    return await service.create_content(type, content.dict())


@api_router.put("/catalog/{type}/{id}", response_model=BaseContent)
async def update_content(
    type: ContentType,
    id: UUID,
    content: ContentUpdate,
    service: CatalogService = Depends(get_catalog_service),
) -> BaseContent:
    """Update existing content item"""
    update_data = {k: v for k, v in content.dict().items() if v is not None}
    return await service.update_content(type, id, update_data)


@api_router.delete("/catalog/{type}/{id}")
async def delete_content(
    type: ContentType,
    id: UUID,
    service: CatalogService = Depends(get_catalog_service),
) -> Dict:
    """Delete content item"""
    success = await service.delete_content(type, id)
    return {"success": success}


@api_router.get("/catalog/search")
async def search_content(
    q: str = Query(..., description="Search query"),
    type: Optional[ContentType] = None,
    theme: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    service: CatalogService = Depends(get_catalog_service),
) -> Dict:
    """Search content items"""
    return await service.search_content(q, type, theme, page, size)


@api_router.post("/catalog/search/advanced")
async def advanced_search(
    query: SearchQuery,
    service: CatalogService = Depends(get_catalog_service),
) -> Dict:
    """Advanced content search"""
    return await service.search_content(
        query.query,
        filters=query.filters,
        sort=query.sort,
        page=query.page,
        size=query.size,
    )


@api_router.get("/catalog/recommend")
async def get_recommendations(
    character_id: Optional[UUID] = None,
    campaign_id: Optional[UUID] = None,
    service: CatalogService = Depends(get_catalog_service),
) -> Dict:
    """Get content recommendations"""
    # TODO: Implement recommendations
    return {"recommendations": []}


@api_router.post("/catalog/theme/apply")
async def apply_theme(
    content_id: UUID,
    theme_data: ThemeApplication,
    service: CatalogService = Depends(get_catalog_service),
) -> BaseContent:
    """Apply theme to content"""
    return await service.apply_theme(
        content_id,
        theme_data.theme,
        theme_data.strength,
        theme_data.preserve,
    )


@api_router.get("/catalog/theme/list")
async def list_themes(
    service: CatalogService = Depends(get_catalog_service),
) -> Dict:
    """List available themes"""
    # TODO: Implement theme listing
    return {
        "themes": [
            {
                "id": "fantasy",
                "name": "High Fantasy",
                "description": "Classic D&D high fantasy setting",
                "compatible_types": ["item", "spell", "monster"],
                "modifiers": {},
            }
        ]
    }
