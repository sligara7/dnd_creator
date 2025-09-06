from typing import Any, Dict, List, Optional, Union

import openai
import structlog
from openai.types.completion import Completion
from openai.types.chat import ChatCompletion
from pydantic import BaseModel, Field

from llm_service.core.exceptions import TextGenerationError
from llm_service.core.settings import Settings
from llm_service.core.cache import RateLimiter
from llm_service.schemas.text import ModelConfig, ModelType


class Usage(BaseModel):
    """Model token usage."""
    prompt_tokens: int = Field(description="Number of tokens in the prompt")
    completion_tokens: int = Field(description="Number of tokens in the completion")
    total_tokens: int = Field(description="Total number of tokens used")


class OpenAIClient:
    """OpenAI client with retries and fallback."""

    def __init__(
        self,
        settings: Settings,
        rate_limiter: RateLimiter,
        logger: Optional[structlog.BoundLogger] = None
    ) -> None:
        self.settings = settings
        self.rate_limiter = rate_limiter
        self.logger = logger or structlog.get_logger()

        # Create OpenAI client
        self.client = openai.AsyncOpenAI(
            api_key=self.settings.openai.api_key.get_secret_value(),
            timeout=self.settings.openai.request_timeout,
            max_retries=self.settings.openai.max_retries,
        )

    async def _create_chat_completion(
        self, messages: List[Dict[str, str]], model_config: ModelConfig
    ) -> ChatCompletion:
        """Create a chat completion with the specified model."""
        try:
            # Check rate limit before making request
            await self.rate_limiter.check_model_limit(model_config.name)
            
            return await self.client.chat.completions.create(
                messages=messages,
                model=model_config.name,
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens,
            )
        except openai.RateLimitError as e:
            raise TextGenerationError(
                message="OpenAI rate limit exceeded",
                details={"retry_after": e.response.headers.get("Retry-After", "60")},
            ) from e
        except openai.APIError as e:
            self.logger.error(
                "openai_api_error",
                error=str(e),
                model=model_config.name,
            )
            raise TextGenerationError(
                message=f"OpenAI API error: {str(e)}",
                details={"model": model_config.name},
            ) from e

    async def _create_completion(
        self, prompt: str, model_config: ModelConfig
    ) -> Completion:
        """Create a text completion with the specified model."""
        try:
            # Check rate limit before making request
            await self.rate_limiter.check_model_limit(model_config.name)
            
            return await self.client.completions.create(
                prompt=prompt,
                model=model_config.name,
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens,
            )
        except openai.RateLimitError as e:
            raise TextGenerationError(
                message="OpenAI rate limit exceeded",
                details={"retry_after": e.response.headers.get("Retry-After", "60")},
            ) from e
        except openai.APIError as e:
            self.logger.error(
                "openai_api_error",
                error=str(e),
                model=model_config.name,
            )
            raise TextGenerationError(
                message=f"OpenAI API error: {str(e)}",
                details={"model": model_config.name},
            ) from e

    async def generate_text(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        model_config: Optional[ModelConfig] = None,
    ) -> tuple[str, Usage]:
        """Generate text using either chat or completion API.
        
        Args:
            prompt: Either a string prompt or a list of chat messages
            model_config: Optional model configuration. Uses default if not provided.

        Returns:
            Tuple of (generated text, token usage)
        """
        if model_config is None:
            model_config = ModelConfig()

        try:
            if isinstance(prompt, list):
                # Use chat completion API
                response = await self._create_chat_completion(prompt, model_config)
                text = response.choices[0].message.content or ""
                usage = Usage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                )
            else:
                # Use completion API
                response = await self._create_completion(prompt, model_config)
                text = response.choices[0].text.strip()
                usage = Usage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                )

            return text, usage

        except TextGenerationError as e:
            # If using primary model, try fallback
            if model_config.name == self.settings.openai.primary_model:
                self.logger.warning(
                    "primary_model_failed_using_fallback",
                    error=str(e),
                    primary_model=model_config.name,
                    fallback_model=self.settings.openai.fallback_model,
                )
                fallback_config = model_config.model_copy(
                    update={"name": self.settings.openai.fallback_model}
                )
                return await self.generate_text(prompt, fallback_config)
            raise
