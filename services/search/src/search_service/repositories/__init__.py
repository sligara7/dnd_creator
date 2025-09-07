"""Search Service Repository Layer

This module provides data access layer for search operations,
following the repository pattern for clean architecture.
"""

from search_service.repositories.base import BaseRepository
from search_service.repositories.search import SearchRepository
from search_service.repositories.index import IndexRepository
from search_service.repositories.analytics import AnalyticsRepository

__all__ = [
    "BaseRepository",
    "SearchRepository", 
    "IndexRepository",
    "AnalyticsRepository",
]
