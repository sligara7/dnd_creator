# OpenAI API Key should be stored in .env file
# Copy .env.example to .env and add your API key there



"""
External LLM API service for content generation.
Replaces the local Ollama service with cloud-based LLM providers.
"""
import json
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# Note: These imports will need to be installed
# pip install httpx openai anthropic

logger = logging.getLogger(__name__)


class LLMService(ABC):
    """Abstract base class for LLM services."""
    
    @abstractmethod
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using the LLM."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the LLM service is available."""
        pass


class OpenAILLMService(LLMService):
    """OpenAI API-based LLM service."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", timeout: int = 30):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        
        # Will need: pip install openai
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a D&D assistant. Respond ONLY with valid JSON. No explanations, no markdown, no extra text. Just JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1024),
                timeout=self.timeout
            )
            
            content = response.choices[0].message.content
            if not content or not content.strip():
                raise Exception("Empty response from OpenAI")
            
            return content
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise Exception(f"LLM generation failed: {e}")
    
    async def test_connection(self) -> bool:
        """Test OpenAI API connection."""
        try:
            await self.generate_content("Test", max_tokens=1)
            return True
        except Exception:
            return False


class AnthropicLLMService(LLMService):
    """Anthropic Claude API-based LLM service."""
    
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307", timeout: int = 30):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        
        # Will need: pip install anthropic
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using Anthropic API."""
        try:
            response = await self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 1024),
                temperature=kwargs.get("temperature", 0.7),
                timeout=self.timeout
            )
            
            content = response.content[0].text
            if not content or not content.strip():
                raise Exception("Empty response from Anthropic")
            
            return content
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise Exception(f"LLM generation failed: {e}")
    
    async def test_connection(self) -> bool:
        """Test Anthropic API connection."""
        try:
            await self.generate_content("Test", max_tokens=1)
            return True
        except Exception:
            return False


class HTTPLLMService(LLMService):
    """Generic HTTP-based LLM service for custom endpoints."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, 
                 model: str = "default", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        
        # Will need: pip install httpx
        try:
            import httpx
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            self.client = httpx.AsyncClient(headers=headers, timeout=timeout)
        except ImportError:
            raise ImportError("httpx package not installed. Run: pip install httpx")
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using custom HTTP endpoint."""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are a D&D assistant. Respond ONLY with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1024)
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            if not content or not content.strip():
                raise Exception("Empty response from HTTP LLM service")
            
            return content
            
        except Exception as e:
            logger.error(f"HTTP LLM service generation failed: {e}")
            raise Exception(f"LLM generation failed: {e}")
    
    async def test_connection(self) -> bool:
        """Test HTTP LLM service connection."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


def create_llm_service(provider: str, **kwargs) -> LLMService:
    """
    Factory function to create LLM service instances.
    
    Args:
        provider: LLM provider ("openai", "anthropic", "http")
        **kwargs: Provider-specific configuration
    
    Returns:
        Configured LLM service instance
    """
    if provider.lower() == "openai":
        return OpenAILLMService(**kwargs)
    elif provider.lower() == "anthropic":
        return AnthropicLLMService(**kwargs)
    elif provider.lower() == "http":
        return HTTPLLMService(**kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


# Example usage:
# llm_service = create_llm_service(
#     "openai", 
#     api_key="...", 
#     model="gpt-4"
# )
