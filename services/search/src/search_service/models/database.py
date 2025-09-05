from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel:
    """Base model with common fields"""
    id = Column(PGUUID, primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)


class SearchQuery(Base, BaseModel):
    """Model to track search queries and their performance"""
    __tablename__ = "search_queries"

    query = Column(Text, nullable=False)
    index = Column(String(50), nullable=False)
    filters = Column(JSONB, nullable=True)
    result_count = Column(JSONB, nullable=False)  # Results per page and total
    duration_ms = Column(JSONB, nullable=False)  # Timing breakdowns
    cache_hit = Column(Boolean, default=False)
    error = Column(JSONB, nullable=True)


class SearchSuggestion(Base, BaseModel):
    """Model to track search suggestions and their usage"""
    __tablename__ = "search_suggestions"

    original_query = Column(Text, nullable=False)
    suggested_query = Column(Text, nullable=False)
    index = Column(String(50), nullable=False)
    used = Column(Boolean, default=False)
    result_improvement = Column(JSONB, nullable=True)


class SearchAnalytics(Base, BaseModel):
    """Model to track search analytics"""
    __tablename__ = "search_analytics"

    event_type = Column(String(50), nullable=False)
    index = Column(String(50), nullable=False)
    data = Column(JSONB, nullable=False)
    session_id = Column(PGUUID, nullable=True)
    user_id = Column(PGUUID, nullable=True)


class IndexMetadata(Base, BaseModel):
    """Model to track index metadata and stats"""
    __tablename__ = "index_metadata"

    index = Column(String(50), unique=True, nullable=False)
    document_count = Column(JSONB, nullable=False)
    last_refresh = Column(DateTime, nullable=False)
    settings = Column(JSONB, nullable=False)
    mappings = Column(JSONB, nullable=False)
    stats = Column(JSONB, nullable=False)


class CacheMetrics(Base, BaseModel):
    """Model to track cache performance metrics"""
    __tablename__ = "cache_metrics"

    cache_key = Column(String(255), nullable=False)
    hits = Column(JSONB, nullable=False)
    misses = Column(JSONB, nullable=False)
    latency_ms = Column(JSONB, nullable=False)
    size_bytes = Column(JSONB, nullable=False)


class SearchFailure(Base, BaseModel):
    """Model to track search failures and errors"""
    __tablename__ = "search_failures"

    query = Column(Text, nullable=False)
    index = Column(String(50), nullable=False)
    error_type = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    context = Column(JSONB, nullable=True)
