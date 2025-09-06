"""Test configuration and fixtures."""
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import structlog
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from llm_service.core.app import app, create_app
from llm_service.core.cache import RateLimiter
from llm_service.core.events import MessageHubClient
from llm_service.core.settings import Settings, get_settings
from llm_service.services.openai import OpenAIClient
from llm_service.services.getimg_ai import GetImgAIClient


@pytest.fixture
def settings() -> Settings:
    """Get test settings."""
    return get_settings()


@pytest.fixture
def logger() -> structlog.BoundLogger:
    """Get test logger."""
    return structlog.get_logger()


@pytest.fixture
async def redis() -> AsyncGenerator[Redis, None]:
    """Get test Redis connection."""
    redis = Redis.from_url("redis://localhost:6379/1")
    yield redis
    await redis.flushdb()
    await redis.close()


@pytest.fixture
def rate_limiter(redis: Redis, settings: Settings) -> RateLimiter:
    """Get test rate limiter."""
    return RateLimiter(redis, settings)


@pytest.fixture
def message_hub() -> MessageHubClient:
    """Get mock message hub client."""
    client = AsyncMock(spec=MessageHubClient)
    client.publish_event = AsyncMock()
    return client


@pytest.fixture
def openai_client() -> OpenAIClient:
    """Get mock OpenAI client."""
    client = AsyncMock(spec=OpenAIClient)
    client.generate_text = AsyncMock(return_value=("Generated text", MagicMock()))
    return client


@pytest.fixture
def getimg_client() -> GetImgAIClient:
    """Get mock GetImg.AI client."""
    client = AsyncMock(spec=GetImgAIClient)
    client.generate_image = AsyncMock(return_value="base64_image_data")
    client.transform_image = AsyncMock(return_value="base64_image_data")
    return client


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Get test database session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///./test.db",
        echo=True,
    )
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture
def app_factory(
    settings: Settings,
    logger: structlog.BoundLogger,
    redis: Redis,
    rate_limiter: RateLimiter,
    message_hub: MessageHubClient,
    openai_client: OpenAIClient,
    getimg_client: GetImgAIClient,
    db: AsyncSession,
) -> Generator[None, None, None]:
    """Configure test application."""
    app.state.settings = settings
    app.state.logger = logger
    app.state.redis = redis
    app.state.rate_limiter = rate_limiter
    app.state.message_hub = message_hub
    app.state.openai = openai_client
    app.state.getimg_ai = getimg_client
    app.state.db = db
    yield


@pytest.fixture
async def client(app_factory) -> AsyncGenerator[AsyncClient, None]:
    """Get test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
