"""Dependency injection for FastAPI application."""

from typing import AsyncGenerator, Optional

import redis.asyncio as redis
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from image_service.core.config import get_settings
from image_service.core.logging import get_logger
from image_service.integration.getimg import GetImgClient
# TODO: Import message hub client once implemented

settings = get_settings()
logger = get_logger(__name__)

# Create database engine
engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=settings.DEBUG)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Create Redis client
redis_client = redis.from_url(str(settings.REDIS_URI))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Database error", error=str(e))
            raise
        finally:
            await session.close()


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """Get Redis client."""
    try:
        yield redis_client
    except Exception as e:
        logger.error("Redis error", error=str(e))
        raise


async def get_getimg_client() -> AsyncGenerator[GetImgClient, None]:
    """Get GetImg.AI client."""
    client = GetImgClient()
    try:
        yield client
    finally:
        await client.close()


async def get_request_id(request: Request) -> str:
    """Get unique request ID from request headers."""
    return request.headers.get("X-Request-ID", "")


# Dependency for requiring pagination parameters
async def get_pagination(
    page: Optional[int] = 1,
    per_page: Optional[int] = 20,
) -> tuple[int, int]:
    """Get pagination parameters."""
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20
    if per_page > 100:
        per_page = 100
    return page, per_page


# Shortcut for common dependencies
CommonDeps = Depends(lambda: (
    Depends(get_db),
    Depends(get_redis),
    Depends(get_request_id)
))
