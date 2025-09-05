from typing import AsyncGenerator, Dict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from search_service.core.config import settings
from search_service.clients.elasticsearch import ElasticsearchClient
from search_service.clients.cache import CacheManager
from search_service.clients.message_hub import MessageHubClient


# SQLAlchemy async engine and session
engine = create_async_engine(
    settings.get_database_url,
    echo=settings.DEBUG,
    pool_size=settings.MAX_CONNECTIONS,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Dependency functions for FastAPI endpoints

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Elasticsearch client instance
es_client = ElasticsearchClient()

async def get_es() -> AsyncGenerator[ElasticsearchClient, None]:
    """Get Elasticsearch client"""
    try:
        yield es_client
    finally:
        pass  # Client closed on shutdown


# Redis cache manager instance
cache_manager = CacheManager()

async def get_cache() -> AsyncGenerator[CacheManager, None]:
    """Get cache manager"""
    try:
        yield cache_manager
    finally:
        pass  # Client closed on shutdown


# Message Hub client instance
message_hub = MessageHubClient()

async def get_message_hub() -> AsyncGenerator[MessageHubClient, None]:
    """Get Message Hub client"""
    try:
        yield message_hub
    finally:
        pass  # Client closed on shutdown


# Index mappings from config
def get_index_mappings() -> Dict:
    """Get index mappings configuration"""
    return settings.INDEX_MAPPINGS


# Startup and shutdown functions

async def start_clients() -> None:
    """Initialize service clients on startup"""
    await message_hub.start()


async def close_clients() -> None:
    """Close service clients on shutdown"""
    await es_client.close()
    await cache_manager.close()
    await message_hub.close()
    await engine.dispose()
