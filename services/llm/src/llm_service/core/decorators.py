from functools import wraps
from typing import Any, Callable, Optional

import structlog
from fastapi import Request
from pydantic import BaseModel

from llm_service.core.cache import RedisCache

logger = structlog.get_logger()


def cached_response(
    prefix: str, ttl_seconds: Optional[int] = None, skip_cache_keys: Optional[set[str]] = None
) -> Callable:
    """Cache endpoint response using Redis.

    Args:
        prefix: Cache key prefix
        ttl_seconds: Time to live in seconds
        skip_cache_keys: Set of request param/body keys to exclude from cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get request object from args or kwargs
            request = next(
                (arg for arg in args if isinstance(arg, Request)),
                kwargs.get("request", None),
            )
            if not request:
                logger.warning("cached_response_no_request")
                return await func(*args, **kwargs)

            cache: RedisCache = request.app.state.redis

            # Build cache key from request params and body
            key_parts = [prefix]

            # Add query params
            params = dict(request.query_params)
            if skip_cache_keys:
                params = {k: v for k, v in params.items() if k not in skip_cache_keys}
            if params:
                key_parts.append(f"params:{hash(frozenset(params.items()))}")

            # Add request body for POST/PUT
            if request.method in {"POST", "PUT"}:
                body = await request.json()
                if isinstance(body, dict):
                    if skip_cache_keys:
                        body = {k: v for k, v in body.items() if k not in skip_cache_keys}
                    if body:
                        key_parts.append(f"body:{hash(frozenset(body.items()))}")

            cache_key = ":".join(key_parts)

            # Check cache
            if cached := await cache.get_json(cache_key):
                logger.debug("cache_hit", key=cache_key)
                return BaseModel.model_validate(cached)

            # Get fresh response
            response = await func(*args, **kwargs)

            # Cache response
            if response:
                if isinstance(response, BaseModel):
                    response_dict = response.model_dump()
                else:
                    response_dict = response
                await cache.set(cache_key, response_dict, ttl_seconds)
                logger.debug("cache_set", key=cache_key)

            return response

        return wrapper
    return decorator


def clear_cache(prefix: str) -> Callable:
    """Clear all cached responses with given prefix.

    Use as a class decorator to clear cache when mutating data:
    @clear_cache("text_generation")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get request object from args or kwargs
            request = next(
                (arg for arg in args if isinstance(arg, Request)),
                kwargs.get("request", None),
            )
            if not request:
                logger.warning("clear_cache_no_request")
                return await func(*args, **kwargs)

            cache: RedisCache = request.app.state.redis
            pattern = f"{cache.prefix}:{prefix}*"

            # Execute original function
            result = await func(*args, **kwargs)

            # Clear matching cache keys
            await cache._client.delete(*await cache._client.keys(pattern))
            logger.debug("cache_cleared", pattern=pattern)

            return result

        return wrapper
    return decorator
