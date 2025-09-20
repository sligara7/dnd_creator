"""Content management API endpoints."""

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, Path, status
from prometheus_client import Counter, Histogram

from catalog_service.models import (
    BaseContent,
    ContentType,
    Item,
    Monster,
    Spell,
)
from catalog_service.core.exceptions import ContentNotFoundError
from catalog_service.services.content import ContentService, get_content_service

# Metrics
CONTENT_REQUEST_COUNT = Counter(
    "catalog_content_requests_total",
    "Total content requests",
    ["method", "type"]
)

CONTENT_LATENCY = Histogram(
    "catalog_content_request_duration_seconds",
    "Content request duration in seconds",
    ["method", "type"]
)

router = APIRouter(prefix="/catalog", tags=["content"])

@router.get(
    "/{type}/{id}",
    response_model=BaseContent,
    summary="Get content by ID",
    response_description="The requested content item"
)
async def get_content(
    type: ContentType,
    id: UUID = Path(..., description="Content ID"),
    service: ContentService = Depends(get_content_service),
) -> BaseContent:
    """
    Retrieve content from the catalog by ID.

    Args:
        type: Content type (item, spell, monster)
        id: Content UUID
        service: Content service instance

    Returns:
        Content item matching the ID and type

    Raises:
        ContentNotFoundError: If content is not found
    """
    CONTENT_REQUEST_COUNT.labels(method="get", type=type).inc()
    with CONTENT_LATENCY.labels(method="get", type=type).time():
        content = await service.get_content(type, id)
        if not content:
            raise ContentNotFoundError(str(id), type)
        return content

@router.post(
    "/{type}",
    response_model=BaseContent,
    status_code=status.HTTP_201_CREATED,
    summary="Create new content",
    response_description="The created content item"
)
async def create_content(
    type: ContentType,
    content: BaseContent,
    service: ContentService = Depends(get_content_service),
) -> BaseContent:
    """
    Create new content in the catalog.

    Args:
        type: Content type (item, spell, monster)
        content: Content data
        service: Content service instance

    Returns:
        Created content item
    """
    CONTENT_REQUEST_COUNT.labels(method="post", type=type).inc()
    with CONTENT_LATENCY.labels(method="post", type=type).time():
        return await service.create_content(type, content)

@router.put(
    "/{type}/{id}",
    response_model=BaseContent,
    summary="Update content",
    response_description="The updated content item"
)
async def update_content(
    type: ContentType,
    id: UUID = Path(..., description="Content ID"),
    content: BaseContent = None,
    service: ContentService = Depends(get_content_service),
) -> BaseContent:
    """
    Update existing content in the catalog.

    Args:
        type: Content type (item, spell, monster)
        id: Content UUID
        content: Updated content data
        service: Content service instance

    Returns:
        Updated content item

    Raises:
        ContentNotFoundError: If content is not found
    """
    CONTENT_REQUEST_COUNT.labels(method="put", type=type).inc()
    with CONTENT_LATENCY.labels(method="put", type=type).time():
        updated = await service.update_content(type, id, content)
        if not updated:
            raise ContentNotFoundError(str(id), type)
        return updated

@router.delete(
    "/{type}/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete content",
    response_description="Content successfully deleted"
)
async def delete_content(
    type: ContentType,
    id: UUID = Path(..., description="Content ID"),
    service: ContentService = Depends(get_content_service),
) -> None:
    """
    Delete content from the catalog.

    Args:
        type: Content type (item, spell, monster)
        id: Content UUID
        service: Content service instance

    Raises:
        ContentNotFoundError: If content is not found
    """
    CONTENT_REQUEST_COUNT.labels(method="delete", type=type).inc()
    with CONTENT_LATENCY.labels(method="delete", type=type).time():
        success = await service.delete_content(type, id)
        if not success:
            raise ContentNotFoundError(str(id), type)