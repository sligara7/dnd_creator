from datetime import datetime
from typing import Optional

from fastapi import Request
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from llm_service.core.cache import RedisCache
from llm_service.core.settings import Settings

# Metrics
TOKEN_USAGE = Counter(
    "openai_token_usage_total",
    "Total number of OpenAI tokens used",
    ["model", "type"],  # type is either "prompt" or "completion"
)

TOKEN_COST = Counter(
    "openai_token_cost_total",
    "Total cost of OpenAI API usage in USD",
    ["model"],
)

TOKEN_LATENCY = Histogram(
    "openai_request_duration_seconds",
    "OpenAI API request latency",
    ["model", "endpoint"],
)


class TokenTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking OpenAI token usage."""

    def __init__(self, app, settings: Settings, cache: RedisCache) -> None:
        super().__init__(app)
        self.settings = settings
        self.cache = cache

        # Token costs per 1K tokens (approximate, may need updating)
        self.token_costs = {
            "gpt-4-turbo": {
                "prompt": 0.01,
                "completion": 0.03,
            },
            "gpt-3.5-turbo": {
                "prompt": 0.0005,
                "completion": 0.0015,
            },
        }

    async def _get_daily_usage(self, date_key: str) -> dict:
        """Get token usage for a specific date."""
        usage = await self.cache.get_json(f"token_usage:{date_key}")
        if not usage:
            usage = {
                "total_tokens": 0,
                "models": {},
            }
        return usage

    async def _update_usage(
        self,
        date_key: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        """Update token usage statistics."""
        # Update Redis tracking
        usage = await self._get_daily_usage(date_key)
        
        if model not in usage["models"]:
            usage["models"][model] = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cost": 0.0,
            }

        model_usage = usage["models"][model]
        model_usage["prompt_tokens"] += prompt_tokens
        model_usage["completion_tokens"] += completion_tokens
        model_usage["total_tokens"] += prompt_tokens + completion_tokens
        
        # Calculate cost
        if model in self.token_costs:
            prompt_cost = (prompt_tokens / 1000) * self.token_costs[model]["prompt"]
            completion_cost = (completion_tokens / 1000) * self.token_costs[model]["completion"]
            model_usage["cost"] += prompt_cost + completion_cost

        usage["total_tokens"] += prompt_tokens + completion_tokens

        # Store updated usage
        await self.cache.set(
            f"token_usage:{date_key}",
            usage,
            ttl_seconds=86400 * 7,  # Keep for 7 days
        )

        # Update Prometheus metrics
        TOKEN_USAGE.labels(model=model, type="prompt").inc(prompt_tokens)
        TOKEN_USAGE.labels(model=model, type="completion").inc(completion_tokens)
        if model in self.token_costs:
            TOKEN_COST.labels(model=model).inc(prompt_cost + completion_cost)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Optional[dict]:
        """Process request and track token usage."""
        # Skip non-OpenAI endpoints
        if not request.url.path.startswith("/api/v2/text"):
            return await call_next(request)

        response = await call_next(request)

        # Extract token usage from response
        if hasattr(response, "headers"):
            model = response.headers.get("X-Model-Used")
            prompt_tokens = int(response.headers.get("X-Prompt-Tokens", 0))
            completion_tokens = int(response.headers.get("X-Completion-Tokens", 0))

            if model and (prompt_tokens or completion_tokens):
                date_key = datetime.utcnow().strftime("%Y-%m-%d")
                await self._update_usage(
                    date_key=date_key,
                    model=model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                )

        return response
