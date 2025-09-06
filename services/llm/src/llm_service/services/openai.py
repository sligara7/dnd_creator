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


class Nano5Config(BaseModel):
    """GPT-5-nano specific configuration."""
    context_window: int = Field(default=8000, description="Maximum context window size")
    token_buffer: int = Field(default=1000, description="Reserved tokens for system messages")
    stream_chunk_size: int = Field(default=100, description="Number of tokens per stream chunk")
    max_parallel_requests: int = Field(default=5, description="Maximum parallel requests")


class Usage(BaseModel):
    """Model token usage."""
    prompt_tokens: int = Field(description="Number of tokens in the prompt")
    completion_tokens: int = Field(description="Number of tokens in the completion")
    total_tokens: int = Field(description="Total tokens used")
    cached: bool = Field(default=False, description="Whether result was from cache")


class OpenAIClient:
    """OpenAI client optimized for GPT-5-nano with retries."""

    def __init__(
        self,
        settings: Settings,
        rate_limiter: RateLimiter,
        logger: Optional[structlog.BoundLogger] = None
    ) -> None:
        self.settings = settings
        self.rate_limiter = rate_limiter
        self.logger = logger or structlog.get_logger()

        # Configure GPT-5-nano specific settings
        self.nano_config = Nano5Config()
        
        # Create OpenAI client with nano-optimized configuration
        self.client = openai.AsyncOpenAI(
            api_key=self.settings.openai.api_key.get_secret_value(),
            timeout=self.settings.openai.request_timeout,
            max_retries=self.settings.openai.max_retries,
        )
        
        # Set GPT-5-nano as default model
        self.default_model = "gpt-5-nano"

    async def _create_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model_config: ModelConfig,
        stream: bool = False
    ) -> ChatCompletion:
        """Create a chat completion with the specified model."""
        try:
            # Check rate limit before making request
            await self.rate_limiter.check_model_limit(model_config.name)
            
            # Apply nano-specific optimizations
            nano_messages = self._optimize_messages_for_nano(messages)
            
            return await self.client.chat.completions.create(
                messages=nano_messages,
                model=model_config.name or self.default_model,
                temperature=model_config.temperature,
                max_tokens=min(model_config.max_tokens, self.nano_config.context_window - self.nano_config.token_buffer),
                stream=stream,
                presence_penalty=0.1,  # Nano-optimized presence penalty
                frequency_penalty=0.1,  # Nano-optimized frequency penalty
                response_format={"type": "text"}
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

    def _optimize_messages_for_nano(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Optimize messages for GPT-5-nano processing."""
        optimized = []
        for msg in messages:
            if msg["role"] == "system":
                # Add nano-specific markers to system messages
                msg["content"] = f"<|system|>{msg['content']}"
            elif msg["role"] == "user":
                # Add nano-specific markers to user messages
                msg["content"] = f"<|user|>{msg['content']}<|end|>"
            elif msg["role"] == "assistant":
                # Add nano-specific markers to assistant messages
                msg["content"] = f"<|assistant|>{msg['content']}<|end|>"
            optimized.append(msg)
        return optimized

    async def generate_text(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        model_config: Optional[ModelConfig] = None,
        stream: bool = False
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
