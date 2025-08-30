"""
Startup and Shutdown Utilities

This module manages service startup and shutdown, including database connections,
message hub integration, and metrics initialization.
"""

import aioredis
from prometheus_client import REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from structlog import get_logger

from .config import get_settings

settings = get_settings()
logger = get_logger()

# Global connection pools
db_engine = None
db_session = None
redis_pool = None

async def initialize_database() -> None:
    """Initialize database connection pool."""
    global db_engine, db_session
    
    logger.info("Initializing database connection")
    
    db_engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        pool_recycle=settings.database_pool_recycle,
    )
    
    db_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Verify connection
    async with db_engine.begin() as conn:
        await conn.execute("SELECT 1")
    
    logger.info("Database connection initialized")

async def initialize_message_hub() -> None:
    """Initialize message hub connection."""
    logger.info("Initializing message hub connection")
    # TODO: Implement message hub client initialization
    logger.info("Message hub connection initialized")

async def initialize_redis() -> None:
    """Initialize Redis connection pool."""
    global redis_pool
    
    if not settings.redis_url:
        logger.info("Redis not configured, skipping initialization")
        return
    
    logger.info("Initializing Redis connection")
    
    redis_pool = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    
    # Verify connection
    await redis_pool.ping()
    
    logger.info("Redis connection initialized")

def initialize_metrics() -> None:
    """Initialize Prometheus metrics collectors."""
    logger.info("Initializing metrics collectors")
    
    # Unregister default collectors
    REGISTRY.unregister(PROCESS_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    
    # Register custom collectors
    # TODO: Add custom collectors if needed
    
    logger.info("Metrics collectors initialized")

async def shutdown_database() -> None:
    """Shutdown database connection pool."""
    global db_engine
    
    if db_engine is not None:
        logger.info("Closing database connections")
        await db_engine.dispose()
        db_engine = None
        logger.info("Database connections closed")

async def shutdown_message_hub() -> None:
    """Shutdown message hub connection."""
    logger.info("Closing message hub connection")
    # TODO: Implement message hub client shutdown
    logger.info("Message hub connection closed")

async def shutdown_redis() -> None:
    """Shutdown Redis connection pool."""
    global redis_pool
    
    if redis_pool is not None:
        logger.info("Closing Redis connections")
        await redis_pool.close()
        await redis_pool.wait_closed()
        redis_pool = None
        logger.info("Redis connections closed")

async def get_db() -> AsyncSession:
    """Get database session."""
    if db_session is None:
        raise RuntimeError("Database not initialized")
    
    async with db_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_redis():
    """Get Redis connection."""
    if redis_pool is None:
        raise RuntimeError("Redis not initialized")
    return redis_pool
