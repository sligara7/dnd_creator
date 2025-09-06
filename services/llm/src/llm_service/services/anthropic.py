"""Anthropic Claude 3 client implementation."""
from typing import Dict, List, Optional, Any, Union, Tuple

import anthropic
import structlog
from pydantic import BaseModel

from llm_service.core.exceptions import TextGenerationError
from llm_service.core.settings import Settings
from llm_service.schemas.text import ModelConfig, ModelType, Usage


class AnthropicClient:
    """Anthropic client for Claude 3 models."""

    def __init__(self, settings: Settings, logger: Optional[structlog.BoundLogger] = None) -> None:
        self.settings = settings
        self.logger = logger or structlog.get_logger()

        # Create Anthropic client
        self.client = anthropic.AsyncAnthropic(
            api_key=self.settings.anthropic.api_key.get_secret_value(),
            max_retries=self.settings.anthropic.max_retries,
            timeout=self.settings.anthropic.request_timeout,
        )

    async def _create_message(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        model_config: ModelConfig,
    ) -> Tuple[str, Usage]:
        """Create a message with Claude model.

        Args:
            prompt: Either a string prompt or a list of messages
            model_config: Model configuration

        Returns:
            Tuple of (generated text, token usage)
        """
        try:
            # Convert messages to system/user format if needed
            messages: list[Dict[str, str]] = []
            if isinstance(prompt, str):
                messages = [{"role": "user", "content": prompt}]
            else:
                # Map OpenAI message format to Anthropic format
                for msg in prompt:
                    # Skip system messages as Claude handles them differently
                    if msg["role"] != "system":
                        messages.append({
                            "role": "user" if msg["role"] == "user" else "assistant",
                            "content": msg["content"]
                        })

            # Create message
            response = await self.client.messages.create(
                model=model_config.name.value,
                messages=messages,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                top_p=model_config.top_p,
            )

            # Get response content
            text = response.content[0].text

            # Build usage stats
            usage = Usage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens
            )

            return text, usage

        except anthropic.RateLimitError as e:
            self.logger.error(
                "anthropic_rate_limit_error",
                error=str(e),
                model=model_config.name.value,
            )
            raise TextGenerationError(
                message="Anthropic rate limit exceeded",
                details={
                    "retry_after": e.response.headers.get("Retry-After", "60"),
                    "model": model_config.name.value,
                }
            ) from e
        except anthropic.APIError as e:
            self.logger.error(
                "anthropic_api_error",
                error=str(e),
                model=model_config.name.value,
            )
            raise TextGenerationError(
                message=f"Anthropic API error: {str(e)}",
                details={"model": model_config.name.value}
            ) from e

    async def generate_text(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        model_config: Optional[ModelConfig] = None,
    ) -> Tuple[str, Usage]:
        """Generate text using Claude 3 model.

        Args:
            prompt: Either a string prompt or a list of messages
            model_config: Optional model configuration. Uses default if not provided.

        Returns:
            Tuple of (generated text, token usage)
        """
        if model_config is None:
            model_config = ModelConfig(
                name=ModelType.CLAUDE_3_OPUS,
                provider="anthropic"
            )

        try:
            return await self._create_message(prompt, model_config)

        except TextGenerationError as e:
            # Try fallback models if specified
            if model_config.fallback_models:
                for fallback_model in model_config.fallback_models:
                    if fallback_model.value.startswith("claude"):
                        self.logger.warning(
                            "primary_model_failed_using_fallback",
                            error=str(e),
                            primary_model=model_config.name.value,
                            fallback_model=fallback_model.value,
                        )
                        fallback_config = model_config.model_copy(
                            update={"name": fallback_model}
                        )
                        return await self.generate_text(prompt, fallback_config)

            # If no fallback or fallbacks also failed, reraise
            raise
