"""Pagination models for use across the campaign service."""
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict


T = TypeVar("T")


class PaginationResult(BaseModel, Generic[T]):
    """Represents a paginated set of results."""

    items: List[T]
    total_items: int
    total_pages: int
    page_number: int
    page_size: int
    has_next: bool
    has_previous: bool

    model_config = ConfigDict(arbitrary_types_allowed=True)
