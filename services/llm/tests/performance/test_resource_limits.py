"""Tests for service resource limits and quotas."""
import asyncio
import uuid
from collections import defaultdict
import time

import aiohttp
import pytest

from llm_service.core.config import Settings
from llm_service.schemas.image import (
    ImageModelConfig,
    ImageParameters,
    ImageSize,
    TextToImageRequest,
)


async def get_stats(base_url: str) -> dict:
    """Get service stats."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{base_url}/metrics/detailed") as response:
            return await response.json()


async def make_requests(
    base_url: str,
    endpoint: str,
    payload: dict,
    num_requests: int,
    delay: float = 0.1,
) -> list[tuple[float, int]]:
    """Make multiple requests and measure response times."""
    async with aiohttp.ClientSession() as session:
        results = []

        for _ in range(num_requests):
            # Add request ID
            request_data = {
                "request_id": str(uuid.uuid4()),
                **payload,
            }

            # Make request and measure time
            start = time.time()
            async with session.post(
                f"{base_url}{endpoint}",
                json=request_data,
            ) as response:
                duration = time.time() - start
                results.append((duration, response.status))

            # Add delay between requests
            await asyncio.sleep(delay)

        return results


@pytest.mark.asyncio
async def test_text_generation_limits(settings: Settings):
    """Test text generation rate limits."""
    # Create test request
    request_data = {
        "content_type": "backstory",
        "prompt": "Test prompt for rate limit testing",
        "parameters": {
            "character_class": "Wizard",
            "level": 5,
            "theme": "fantasy",
        },
    }

    # Make requests
    results = await make_requests(
        base_url=f"http://{settings.HOST}:{settings.PORT}",
        endpoint="/api/v2/text/character",
        payload=request_data,
        num_requests=120,  # Over the limit
        delay=0.1,  # 10 requests per second
    )

    # Analyze results
    response_times = defaultdict(list)
    status_codes = defaultdict(int)

    for duration, status in results:
        response_times[status].append(duration)
        status_codes[status] += 1

    # Verify rate limits
    assert status_codes[429] > 0, "No rate limit responses received"
    assert status_codes[200] <= settings.RATE_LIMIT_REQUESTS, (
        f"Received {status_codes[200]} successful responses, "
        f"expected <= {settings.RATE_LIMIT_REQUESTS}"
    )

    # Check response times
    success_times = response_times[200]
    if success_times:
        avg_time = sum(success_times) / len(success_times)
        assert avg_time < 5.0, f"Average response time {avg_time}s exceeds 5s limit"


@pytest.mark.asyncio
async def test_image_generation_limits(settings: Settings):
    """Test image generation rate limits."""
    # Create test request
    request_data = TextToImageRequest(
        prompt="Test image for rate limit testing",
        model=ImageModelConfig(
            name="stable-diffusion-v1-5",
            steps=30,
            cfg_scale=7.5,
        ),
        size=ImageSize(width=512, height=512),
        parameters=ImageParameters(
            style_preset="digital-art",
            negative_prompt="poor quality",
        ),
    ).dict()

    # Make requests
    results = await make_requests(
        base_url=f"http://{settings.HOST}:{settings.PORT}",
        endpoint="/api/v2/image/generate",
        payload=request_data,
        num_requests=15,  # Over the image limit
        delay=0.5,  # 2 requests per second
    )

    # Analyze results
    response_times = defaultdict(list)
    status_codes = defaultdict(int)

    for duration, status in results:
        response_times[status].append(duration)
        status_codes[status] += 1

    # Verify rate limits
    assert status_codes[429] > 0, "No rate limit responses received"
    assert status_codes[200] <= 10, (
        f"Received {status_codes[200]} successful responses, expected <= 10"
    )

    # Check response times
    success_times = response_times[200]
    if success_times:
        avg_time = sum(success_times) / len(success_times)
        assert avg_time < 30.0, f"Average response time {avg_time}s exceeds 30s limit"


@pytest.mark.asyncio
async def test_resource_quotas(settings: Settings):
    """Test resource quota tracking."""
    # Get initial stats
    stats = await get_stats(f"http://{settings.HOST}:{settings.PORT}")
    initial_text_tokens = stats["generation_metrics"]["text"]["token_usage"]["total_tokens"]
    initial_images = stats["generation_metrics"]["image"]["resource_usage"]["total_images"]

    # Make some requests
    text_request = {
        "content_type": "backstory",
        "prompt": "Test prompt for quota testing",
        "parameters": {
            "character_class": "Wizard",
            "level": 5,
            "theme": "fantasy",
        },
    }
    await make_requests(
        base_url=f"http://{settings.HOST}:{settings.PORT}",
        endpoint="/api/v2/text/character",
        payload=text_request,
        num_requests=5,
        delay=0.2,
    )

    image_request = TextToImageRequest(
        prompt="Test image for quota testing",
        model=ImageModelConfig(name="stable-diffusion-v1-5"),
        size=ImageSize(width=512, height=512),
        parameters=ImageParameters(),
    ).dict()
    await make_requests(
        base_url=f"http://{settings.HOST}:{settings.PORT}",
        endpoint="/api/v2/image/generate",
        payload=image_request,
        num_requests=3,
        delay=0.5,
    )

    # Get updated stats
    stats = await get_stats(f"http://{settings.HOST}:{settings.PORT}")
    final_text_tokens = stats["generation_metrics"]["text"]["token_usage"]["total_tokens"]
    final_images = stats["generation_metrics"]["image"]["resource_usage"]["total_images"]

    # Verify quota tracking
    assert final_text_tokens > initial_text_tokens, "Text token usage not tracked"
    assert final_images > initial_images, "Image generation not tracked"


@pytest.mark.asyncio
async def test_cache_effectiveness(settings: Settings):
    """Test cache hit rates and effectiveness."""
    # Make identical requests
    request_data = {
        "content_type": "backstory",
        "prompt": "Test prompt for cache testing",
        "parameters": {
            "character_class": "Wizard",
            "level": 5,
            "theme": "fantasy",
        },
    }

    # First request (cache miss)
    first_results = await make_requests(
        base_url=f"http://{settings.HOST}:{settings.PORT}",
        endpoint="/api/v2/text/character",
        payload=request_data,
        num_requests=1,
    )
    first_time = first_results[0][0]

    # Second request (should hit cache)
    second_results = await make_requests(
        base_url=f"http://{settings.HOST}:{settings.PORT}",
        endpoint="/api/v2/text/character",
        payload=request_data,
        num_requests=1,
    )
    second_time = second_results[0][0]

    # Verify cache hit
    assert second_time < first_time, "Cache hit not faster than cache miss"

    # Check cache metrics
    stats = await get_stats(f"http://{settings.HOST}:{settings.PORT}")
    cache_metrics = stats["cache_metrics"]
    assert cache_metrics["hit_rate"] > 0, "No cache hits recorded"
    assert cache_metrics["hit_rate"] + cache_metrics["miss_rate"] == 1.0, (
        "Invalid cache hit/miss rates"
    )
