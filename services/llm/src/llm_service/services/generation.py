"""Theme-aware content generation pipeline."""
from datetime import datetime
from typing import AsyncGenerator, Dict, List, Optional, Tuple
import structlog

from ..core.cache import RateLimiter
from ..core.exceptions import TextGenerationError
from ..core.settings import Settings
from ..models.theme import (
    ContentType,
    GenerationConfig,
    GenerationMetadata,
    GenerationResult,
    ThemeContext
)
from .openai import OpenAIClient
from .prompts import PromptEngine, create_chat_prompt


class GenerationPipeline:
    """Pipeline for theme-aware content generation."""

    def __init__(
        self,
        settings: Settings,
        rate_limiter: RateLimiter,
        logger: Optional[structlog.BoundLogger] = None
    ):
        """Initialize the generation pipeline."""
        self.settings = settings
        self.rate_limiter = rate_limiter
        self.logger = logger or structlog.get_logger()
        self.openai_client = OpenAIClient(settings, rate_limiter, logger)
        self.default_config = GenerationConfig()

    async def validate_request(
        self,
        content_type: ContentType,
        theme_context: Optional[ThemeContext] = None,
        config: Optional[GenerationConfig] = None
    ) -> None:
        """Validate generation request parameters."""
        if not content_type:
            raise TextGenerationError("Content type must be specified")

        if config:
            if config.max_tokens <= 0:
                raise TextGenerationError("max_tokens must be greater than 0")
            if not (0 <= config.temperature <= 1):
                raise TextGenerationError("temperature must be between 0 and 1")

    def _create_generation_metadata(
        self,
        usage: Dict[str, int],
        generation_time_ms: int,
        model: str,
        cached: bool = False
    ) -> GenerationMetadata:
        """Create generation metadata from completion results."""
        return GenerationMetadata(
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            total_tokens=usage["total_tokens"],
            generation_time_ms=generation_time_ms,
            model_name=model,
            cached=cached
        )

    async def generate_content(
        self,
        content_type: ContentType,
        theme_context: Optional[ThemeContext] = None,
        config: Optional[GenerationConfig] = None,
    ) -> GenerationResult:
        """Generate content with theme awareness."""
        config = config or self.default_config
        start_time = datetime.now()

        # Validate request parameters
        await self.validate_request(content_type, theme_context, config)

        try:
            # Create theme-aware prompt
            prompt_engine = PromptEngine(theme_context) if theme_context else None
            if prompt_engine:
                prompt = prompt_engine.generate_prompt(content_type)
            else:
                # Fallback to basic prompt if no theme context
                prompt = f"Generate D&D 5e content for: {content_type.value}"

            # Create chat messages with theme context
            messages = create_chat_prompt(prompt, theme_context)

            # Generate content
            content, usage = await self.openai_client.generate_text(
                messages,
                model_config=config
            )

            # Calculate generation time
            generation_time = int((datetime.now() - start_time).total_seconds() * 1000)

            # Create metadata
            metadata = self._create_generation_metadata(
                usage=usage.dict(),
                generation_time_ms=generation_time,
                model=config.model,
                cached=usage.cached
            )

            # Create result
            result = GenerationResult(
                content=content,
                metadata=metadata,
                theme_context=theme_context,
                content_type=content_type
            )

            self.logger.info(
                "content_generated",
                content_type=content_type.value,
                theme=theme_context.name if theme_context else None,
                tokens=metadata.total_tokens,
                generation_time=metadata.generation_time_ms
            )

            return result

        except Exception as e:
            self.logger.error(
                "generation_failed",
                error=str(e),
                content_type=content_type.value,
                theme=theme_context.name if theme_context else None
            )
            raise TextGenerationError(f"Content generation failed: {str(e)}")

    async def generate_content_stream(
        self,
        content_type: ContentType,
        theme_context: Optional[ThemeContext] = None,
        config: Optional[GenerationConfig] = None,
    ) -> AsyncGenerator[Tuple[str, Optional[GenerationMetadata]], None]:
        """Generate content with theme awareness and streaming."""
        config = config or self.default_config
        start_time = datetime.now()

        # Validate request parameters
        await self.validate_request(content_type, theme_context, config)

        try:
            # Create theme-aware prompt
            prompt_engine = PromptEngine(theme_context) if theme_context else None
            if prompt_engine:
                prompt = prompt_engine.generate_prompt(content_type)
            else:
                prompt = f"Generate D&D 5e content for: {content_type.value}"

            # Create chat messages with theme context
            messages = create_chat_prompt(prompt, theme_context)

            # Stream content generation
            async for content, usage in self.openai_client.generate_text(
                messages,
                model_config=config,
                stream=True
            ):
                if usage:
                    # Final chunk with metadata
                    generation_time = int(
                        (datetime.now() - start_time).total_seconds() * 1000
                    )
                    metadata = self._create_generation_metadata(
                        usage=usage.dict(),
                        generation_time_ms=generation_time,
                        model=config.model,
                        cached=usage.cached
                    )
                    yield content, metadata
                else:
                    # Content chunks without metadata
                    yield content, None

        except Exception as e:
            self.logger.error(
                "streaming_generation_failed",
                error=str(e),
                content_type=content_type.value,
                theme=theme_context.name if theme_context else None
            )
            raise TextGenerationError(f"Content generation failed: {str(e)}")

    async def validate_theme_compatibility(
        self,
        content: str,
        theme_context: ThemeContext,
    ) -> bool:
        """Validate that generated content matches theme requirements."""
        try:
            # Create validation prompt
            prompt = f"""Validate if this content matches the following theme requirements:

Theme: {theme_context.name}
Genre: {theme_context.genre.value}
Tone: {theme_context.tone.value}

Content to validate:
{content}

Consider:
1. Genre consistency
2. Tone appropriateness
3. Theme element presence
4. Style guideline adherence

Respond with either 'valid' or 'invalid' followed by a brief explanation."""

            messages = create_chat_prompt(prompt)
            
            # Generate validation response
            response, _ = await self.openai_client.generate_text(
                messages,
                model_config=GenerationConfig(
                    temperature=0.1,  # Low temperature for consistent validation
                    max_tokens=100  # Short response needed
                )
            )

            # Check validation result
            is_valid = response.lower().startswith("valid")
            
            self.logger.info(
                "theme_validation_complete",
                theme=theme_context.name,
                is_valid=is_valid,
                validation_response=response
            )

            return is_valid

        except Exception as e:
            self.logger.error(
                "theme_validation_failed",
                error=str(e),
                theme=theme_context.name
            )
            return False  # Fail closed on validation errors
