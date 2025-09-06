from datetime import datetime
from uuid import UUID
from typing import Dict, Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from llm_service.core.cache import AsyncCacheService, RateLimiter
from llm_service.core.events import MessageHubClient, TextGeneratedEvent
from llm_service.core.settings import Settings
from llm_service.models.content import TextContent
from llm_service.schemas.text import (
    TextGenerationRequest,
    TextType,
    GeneratedText,
    ContentMetadata,
    ModelProvider,
)
from llm_service.services.openai import OpenAIClient
from llm_service.services.anthropic import AnthropicClient
from llm_service.services.prompts import (
    PROMPT_TEMPLATES,
    create_chat_prompt,
    format_campaign_prompt,
    format_character_prompt,
)


class ProviderFactory:
    """Factory for creating appropriate model provider clients."""

    def __init__(self, settings: Settings, logger: Optional[structlog.BoundLogger] = None):
        self.settings = settings
        self.logger = logger or structlog.get_logger()
        self._clients = {}

    def get_client(self, provider: ModelProvider):
        """Get or create appropriate client for the given provider."""
        if provider not in self._clients:
            if provider == ModelProvider.OPENAI:
                self._clients[provider] = OpenAIClient(self.settings, self.logger)
            elif provider == ModelProvider.ANTHROPIC:
                self._clients[provider] = AnthropicClient(self.settings, self.logger)
            else:
                raise ValueError(f"Unsupported provider: {provider}")

        return self._clients[provider]


class TextGenerationService(AsyncCacheService):
    """Service for generating text content."""

def __init__(
        self,
        settings: Settings,
        openai: OpenAIClient,
        db: AsyncSession,
        message_hub: MessageHubClient,
        rate_limiter: RateLimiter,
        *args: Any,
        **kwargs: Any
    ) -> None:
        super().__init__(settings, *args, **kwargs)
        self.openai = openai
        self.db = db
        self.message_hub = message_hub
        self.rate_limiter = rate_limiter

    async def initialize(self) -> None:
        """Initialize service resources."""
        pass

    async def cleanup(self) -> None:
        """Clean up service resources."""
        pass

    async def generate_text(
        self, request: TextGenerationRequest, request_id: uuid.UUID
    ) -> GeneratedText:
        """Generate text content based on request."""
        # Check cache first
        if cached := await self._check_cache(request):
            self.logger.info(
                "using_cached_text",
                request_id=str(request_id),
                content_id=str(cached.content_id),
            )
            return cached

        # Get prompt template
        template = PROMPT_TEMPLATES.get(request.type)
        if not template:
            raise ValueError(f"No template found for content type {request.type}")

        # Format prompt based on request type
        if request.type.value.startswith("character_"):
            if not request.character_context:
                raise ValueError("Character context required for character content")
            prompt = format_character_prompt(
                template,
                request.character_context,
                request.theme.model_dump(),
                additional_context=request.additional_context,
            )
        else:
            if not request.campaign_context:
                raise ValueError("Campaign context required for campaign content")
            prompt = format_campaign_prompt(
                template,
                request.campaign_context.model_dump(),
                request.theme.model_dump(),
                additional_context=request.additional_context,
            )

        # Convert to chat format for better responses
        messages = create_chat_prompt(prompt)

        # Generate text
        try:
            client = self.provider_factory.get_client(request.model.provider)
            text, usage = await client.generate_text(messages, request.model)
        except Exception as e:
            self.logger.error(
                "text_generation_failed",
                error=str(e),
                request_id=str(request_id),
                provider=request.model.provider,
                model=request.model.name,
            )
            raise

        # Create content metadata
        metadata = ContentMetadata(
            request_id=request_id,
            source_service=request.model.name,
            model_used=request.model.name,
            prompt_used=prompt,
            settings_used={
                "temperature": request.model.temperature,
                "max_tokens": request.model.max_tokens,
                "theme": request.theme.model_dump(),
                **request.additional_context or {},
            },
        )

        # Create database record
        content = TextContent(
            content=text,
            content_type=request.type,
            parent_content_id=request.parent_content_id,
            metadata=metadata.model_dump(),
        )
        self.db.add(content)
        await self.db.commit()
        await self.db.refresh(content)

        # Create response
        result = GeneratedText(
            content=text,
            content_id=content.id,
            metadata=metadata,
            parent_content_id=request.parent_content_id,
        )

        # Cache result
        await self._cache_result(request, result)

        # Publish event
        event = TextGeneratedEvent(
            request_id=request_id,
            content_type=request.type,
            content_id=result.content_id,
            status="completed",
            model_used=request.model.name,
            token_usage=usage.model_dump(),
        )
        await self.message_hub.publish_event(event)

        self.logger.info(
            "text_generated",
            request_id=str(request_id),
            content_id=str(result.content_id),
            content_type=request.type,
            token_usage=usage.model_dump(),
        )

        return result

    async def _check_cache(
        self, request: TextGenerationRequest
    ) -> Optional[GeneratedText]:
        """Check cache for existing content."""
        cache_key = self._make_cache_key(request)
        if cached := await self.get_json(cache_key):
            return GeneratedText.model_validate(cached)
        return None

    async def _cache_result(
        self, request: TextGenerationRequest, result: GeneratedText
    ) -> None:
        """Cache generated content."""
        cache_key = self._make_cache_key(request)
        ttl = self.settings.cache.text_ttl_seconds
        await self.set_in_cache(cache_key, result.model_dump(), ttl)

    def _make_cache_key(self, request: TextGenerationRequest) -> str:
        """Create cache key from request."""
        # Hash unique request attributes
        key_parts = [
            request.type,
            str(hash(frozenset(request.theme.model_dump().items()))),
        ]

        if request.character_context:
            key_parts.append(
                str(hash(frozenset(request.character_context.model_dump().items())))
            )

        if request.campaign_context:
            key_parts.append(
                str(hash(frozenset(request.campaign_context.model_dump().items())))
            )

        if request.additional_context:
            key_parts.append(str(hash(frozenset(request.additional_context.items()))))

        return f"text_generation:{'_'.join(key_parts)}"
