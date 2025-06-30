# REFACTORED: Now defaults to Ollama with Llama3 for local testing
# REFACTORED: No API keys needed for local development
# ADDRESSED: OpenAI API Key support via .env file for production use
# ADDRESSED: Proper rate limiting implemented per OpenAI cookbook recommendations

"""
LLM API service for content generation - defaults to local Ollama for testing.
Supports both local Ollama service and cloud-based LLM providers.
Includes comprehensive rate limiting for cloud providers.
"""
import json
import logging
import os
import asyncio
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections import deque

# Note: These imports will need to be installed
# pip install httpx openai anthropic python-dotenv

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not installed. Run: pip install python-dotenv")

logger = logging.getLogger(__name__)


# ============================================================================
# RATE LIMITING IMPLEMENTATION
# ============================================================================

@dataclass
class RateLimitConfig:
    """Configuration for API rate limiting."""
    requests_per_minute: int = 3      # Tier 1 OpenAI free limit
    requests_per_day: int = 200       # Tier 1 OpenAI free limit
    tokens_per_minute: int = 40000    # Tier 1 OpenAI free limit
    max_retries: int = 3
    base_delay: float = 1.0           # Base exponential backoff delay
    max_delay: float = 60.0           # Maximum delay between retries


class RateLimiter:
    """
    Rate limiter implementing OpenAI cookbook recommendations.
    Tracks requests per minute, requests per day, and tokens per minute.
    """
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        
        # Track requests per minute
        self.rpm_requests = deque()
        
        # Track requests per day  
        self.rpd_requests = deque()
        
        # Track tokens per minute
        self.tpm_tokens = deque()
        self.current_tokens = 0
        
        # Lock for thread safety
        self._lock = asyncio.Lock()
    
    async def acquire(self, estimated_tokens: int = 1000) -> bool:
        """
        Acquire permission to make a request.
        
        Args:
            estimated_tokens: Estimated tokens for the request
            
        Returns:
            True if request can proceed, False if rate limited
        """
        async with self._lock:
            now = time.time()
            
            # Clean old entries
            self._cleanup_old_entries(now)
            
            # Check if we can make the request
            if not self._can_make_request(now, estimated_tokens):
                return False
            
            # Record the request
            self.rpm_requests.append(now)
            self.rpd_requests.append(now)
            self.tpm_tokens.append((now, estimated_tokens))
            self.current_tokens += estimated_tokens
            
            return True
    
    def _cleanup_old_entries(self, now: float):
        """Remove old entries outside the rate limit windows."""
        # Clean requests older than 1 minute
        minute_ago = now - 60
        while self.rpm_requests and self.rpm_requests[0] < minute_ago:
            self.rpm_requests.popleft()
        
        # Clean requests older than 1 day
        day_ago = now - 86400  # 24 * 60 * 60
        while self.rpd_requests and self.rpd_requests[0] < day_ago:
            self.rpd_requests.popleft()
        
        # Clean token entries older than 1 minute
        while self.tpm_tokens and self.tpm_tokens[0][0] < minute_ago:
            _, tokens = self.tpm_tokens.popleft()
            self.current_tokens -= tokens
    
    def _can_make_request(self, now: float, estimated_tokens: int) -> bool:
        """Check if request can be made within rate limits."""
        # Check requests per minute
        if len(self.rpm_requests) >= self.config.requests_per_minute:
            return False
        
        # Check requests per day
        if len(self.rpd_requests) >= self.config.requests_per_day:
            return False
        
        # Check tokens per minute
        if self.current_tokens + estimated_tokens > self.config.tokens_per_minute:
            return False
        
        return True
    
    def get_wait_time(self) -> float:
        """Get recommended wait time before next request."""
        now = time.time()
        
        if not self.rpm_requests:
            return 0.0
        
        # Time until oldest request in current minute expires
        oldest_request = self.rpm_requests[0]
        wait_time = 60 - (now - oldest_request)
        
        return max(0.0, wait_time)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        now = time.time()
        self._cleanup_old_entries(now)
        
        return {
            "requests_per_minute": len(self.rpm_requests),
            "requests_per_day": len(self.rpd_requests),
            "tokens_per_minute": self.current_tokens,
            "rpm_limit": self.config.requests_per_minute,
            "rpd_limit": self.config.requests_per_day,
            "tpm_limit": self.config.tokens_per_minute,
            "wait_time": self.get_wait_time()
        }


# ============================================================================
# LLM SERVICE INTERFACES
# ============================================================================


class LLMService(ABC):
    """Abstract base class for LLM services with rate limiting."""
    
    @abstractmethod
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using the LLM."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the LLM service is available."""
        pass
    
    @abstractmethod
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        pass


class OpenAILLMService(LLMService):
    """OpenAI API-based LLM service with rate limiting and .env support."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", 
                 timeout: int = 600, rate_limit_config: Optional[RateLimitConfig] = None):
        
        # Load API key from environment if not provided
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter. Create .env file with OPENAI_API_KEY=your_key"
            )
        
        self.model = model
        self.timeout = timeout
        
        # Initialize rate limiter
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.rate_limiter = RateLimiter(self.rate_limit_config)
        
        # Will need: pip install openai
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using OpenAI API with rate limiting."""
        # Estimate token usage (rough approximation: 1 token ≈ 4 characters)
        max_tokens = kwargs.get("max_tokens", 4096)
        estimated_tokens = (len(prompt) + max_tokens) // 4
        
        # Attempt with exponential backoff
        for attempt in range(self.rate_limit_config.max_retries):
            try:
                # Check rate limits
                if not await self.rate_limiter.acquire(estimated_tokens):
                    wait_time = self.rate_limiter.get_wait_time()
                    if wait_time > 0:
                        logger.info(f"Rate limited. Waiting {wait_time:.1f} seconds...")
                        await asyncio.sleep(wait_time + 1)  # Add 1 second buffer
                        continue
                    else:
                        raise Exception("Daily rate limit exceeded")
                
                # Make the request
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
                    max_tokens=max_tokens,
                    timeout=self.timeout
                )
                
                content = response.choices[0].message.content
                if not content or not content.strip():
                    raise Exception("Empty response from OpenAI")
                
                # Log successful request
                logger.info(f"OpenAI request successful. Rate limit status: {self.get_rate_limit_status()}")
                return content
                
            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    # Rate limit error - apply exponential backoff
                    delay = min(
                        self.rate_limit_config.base_delay * (2 ** attempt),
                        self.rate_limit_config.max_delay
                    )
                    logger.warning(f"Rate limit hit. Retrying in {delay} seconds... (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                    continue
                
                # Other errors
                if attempt == self.rate_limit_config.max_retries - 1:
                    logger.error(f"OpenAI generation failed after {attempt + 1} attempts: {e}")
                    raise Exception(f"LLM generation failed: {e}")
                
                # Retry with exponential backoff
                delay = min(
                    self.rate_limit_config.base_delay * (2 ** attempt),
                    self.rate_limit_config.max_delay
                )
                logger.warning(f"Request failed. Retrying in {delay} seconds... (attempt {attempt + 1})")
                await asyncio.sleep(delay)
        
        raise Exception("Max retries exceeded")
    
    async def test_connection(self) -> bool:
        """Test OpenAI API connection."""
        try:
            await self.generate_content("Test", max_tokens=1, temperature=0)
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return self.rate_limiter.get_status()


class AnthropicLLMService(LLMService):
    """Anthropic Claude API-based LLM service with rate limiting and .env support."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-haiku-20240307", 
                 timeout: int = 600, rate_limit_config: Optional[RateLimitConfig] = None):
        
        # Load API key from environment if not provided
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter. Create .env file with ANTHROPIC_API_KEY=your_key"
            )
        
        self.model = model
        self.timeout = timeout
        
        # Initialize rate limiter (use more conservative limits for Anthropic)
        if not rate_limit_config:
            rate_limit_config = RateLimitConfig(
                requests_per_minute=5,
                requests_per_day=1000,
                tokens_per_minute=10000
            )
        self.rate_limit_config = rate_limit_config
        self.rate_limiter = RateLimiter(self.rate_limit_config)
        
        # Will need: pip install anthropic
        try:
            import anthropic
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using Anthropic API with rate limiting."""
        
        # Estimate token usage
        estimated_tokens = (len(prompt) + kwargs.get("max_tokens", 1024)) // 4
        
        # Attempt with exponential backoff
        for attempt in range(self.rate_limit_config.max_retries):
            try:
                # Check rate limits
                if not await self.rate_limiter.acquire(estimated_tokens):
                    wait_time = self.rate_limiter.get_wait_time()
                    if wait_time > 0:
                        logger.info(f"Rate limited. Waiting {wait_time:.1f} seconds...")
                        await asyncio.sleep(wait_time + 1)
                        continue
                    else:
                        raise Exception("Daily rate limit exceeded")
                
                # Make the request
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
                
                # Log successful request
                logger.info(f"Anthropic request successful. Rate limit status: {self.get_rate_limit_status()}")
                return content
                
            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    # Rate limit error - apply exponential backoff
                    delay = min(
                        self.rate_limit_config.base_delay * (2 ** attempt),
                        self.rate_limit_config.max_delay
                    )
                    logger.warning(f"Rate limit hit. Retrying in {delay} seconds... (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                    continue
                
                # Other errors
                if attempt == self.rate_limit_config.max_retries - 1:
                    logger.error(f"Anthropic generation failed after {attempt + 1} attempts: {e}")
                    raise Exception(f"LLM generation failed: {e}")
                
                # Retry with exponential backoff
                delay = min(
                    self.rate_limit_config.base_delay * (2 ** attempt),
                    self.rate_limit_config.max_delay
                )
                logger.warning(f"Request failed. Retrying in {delay} seconds... (attempt {attempt + 1})")
                await asyncio.sleep(delay)
        
        raise Exception("Max retries exceeded")
    
    async def test_connection(self) -> bool:
        """Test Anthropic API connection."""
        try:
            await self.generate_content("Test", max_tokens=1, temperature=0)
            return True
        except Exception as e:
            logger.error(f"Anthropic connection test failed: {e}")
            return False
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return self.rate_limiter.get_status()


class HTTPLLMService(LLMService):
    """Generic HTTP-based LLM service for custom endpoints with rate limiting."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, 
                 model: str = "default", timeout: int = 600,
                 rate_limit_config: Optional[RateLimitConfig] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        
        # Initialize rate limiter with conservative defaults
        if not rate_limit_config:
            rate_limit_config = RateLimitConfig(
                requests_per_minute=10,
                requests_per_day=500,
                tokens_per_minute=20000
            )
        self.rate_limit_config = rate_limit_config
        self.rate_limiter = RateLimiter(self.rate_limit_config)
        
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
        """Generate content using custom HTTP endpoint with rate limiting."""
        
        # Estimate token usage
        estimated_tokens = (len(prompt) + kwargs.get("max_tokens", 1024)) // 4
        
        # Attempt with exponential backoff
        for attempt in range(self.rate_limit_config.max_retries):
            try:
                # Check rate limits
                if not await self.rate_limiter.acquire(estimated_tokens):
                    wait_time = self.rate_limiter.get_wait_time()
                    if wait_time > 0:
                        logger.info(f"Rate limited. Waiting {wait_time:.1f} seconds...")
                        await asyncio.sleep(wait_time + 1)
                        continue
                    else:
                        raise Exception("Daily rate limit exceeded")
                
                # Make the request
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
                
                # Log successful request
                logger.info(f"HTTP LLM request successful. Rate limit status: {self.get_rate_limit_status()}")
                return content
                
            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    # Rate limit error - apply exponential backoff
                    delay = min(
                        self.rate_limit_config.base_delay * (2 ** attempt),
                        self.rate_limit_config.max_delay
                    )
                    logger.warning(f"Rate limit hit. Retrying in {delay} seconds... (attempt {attempt + 1})")
                    await asyncio.sleep(delay)
                    continue
                
                # Other errors
                if attempt == self.rate_limit_config.max_retries - 1:
                    logger.error(f"HTTP LLM service generation failed after {attempt + 1} attempts: {e}")
                    raise Exception(f"LLM generation failed: {e}")
                
                # Retry with exponential backoff
                delay = min(
                    self.rate_limit_config.base_delay * (2 ** attempt),
                    self.rate_limit_config.max_delay
                )
                logger.warning(f"Request failed. Retrying in {delay} seconds... (attempt {attempt + 1})")
                await asyncio.sleep(delay)
        
        raise Exception("Max retries exceeded")
    
    async def test_connection(self) -> bool:
        """Test HTTP LLM service connection."""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"HTTP LLM connection test failed: {e}")
            return False
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return self.rate_limiter.get_status()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()


class OllamaLLMService(LLMService):
    """Ollama local LLM service - ideal for testing without API costs."""
    
    def __init__(self, model: str = "llama3:latest", base_url: str = "http://localhost:11434", 
                 timeout: int = 600):
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Ollama is local, so no strict rate limiting needed
        # But we'll implement the interface for consistency
        self.request_count = 0
        self.last_request_time = 0
        
        logger.info(f"Initialized Ollama LLM service with model '{model}' at {base_url}")
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Generate content using Ollama API.
        
        Args:
            prompt: Input prompt for the model
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated text content
        """
        import httpx
        
        # Track request for rate limit interface compliance
        self.request_count += 1
        self.last_request_time = time.time()
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,  # Get complete response
            "options": {}
        }
        
        # Add any additional parameters
        payload["options"]["num_predict"] = kwargs.get("max_tokens", 4096)
        if "temperature" in kwargs:
            payload["options"]["temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            payload["options"]["top_p"] = kwargs["top_p"]
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Sending request to Ollama: {self.base_url}/api/generate")
                
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get("response", "")
                    
                    logger.info(f"Ollama generated {len(generated_text)} characters")
                    return generated_text
                else:
                    error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                    
        except httpx.TimeoutException:
            error_msg = f"Ollama request timed out after {self.timeout} seconds"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Ollama API error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def test_connection(self) -> bool:
        """Test if Ollama is available and the model is accessible."""
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # First check if Ollama is running
                response = await client.get(f"{self.base_url}/api/tags")
                
                if response.status_code != 200:
                    logger.error(f"Ollama not responding: {response.status_code}")
                    return False
                
                # Check if our model is available
                models = response.json()
                model_names = [model["name"] for model in models.get("models", [])]
                
                if self.model not in model_names:
                    logger.warning(f"Model '{self.model}' not found. Available models: {model_names}")
                    logger.info(f"You may need to run: ollama pull {self.model}")
                    return False
                
                logger.info(f"Ollama connection successful. Model '{self.model}' is available.")
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {str(e)}")
            logger.info("Make sure Ollama is installed and running:")
            logger.info("1. Install: https://ollama.ai/")
            logger.info("2. Start: ollama serve")
            logger.info(f"3. Pull model: ollama pull {self.model}")
            return False
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get rate limit status (Ollama has no limits, but interface compliance)."""
        return {
            "provider": "ollama",
            "model": self.model,
            "base_url": self.base_url,
            "requests_made": self.request_count,
            "last_request": self.last_request_time,
            "rate_limited": False,  # Ollama is local, no rate limits
            "available": True
        }


def create_llm_service(provider: str = "ollama", **kwargs) -> LLMService:
    """
    Factory function to create LLM service instances with automatic .env loading.
    
    Args:
        provider: LLM provider ("ollama", "openai", "anthropic", "http")
                 Default: "ollama" for local testing
        **kwargs: Provider-specific configuration
    
    Returns:
        Configured LLM service instance
        
    Examples:
        # Default Ollama for testing (no API key needed):
        llm_service = create_llm_service()  # Uses Ollama with llama3
        
        # Explicit Ollama with custom model:
        llm_service = create_llm_service("ollama", model="llama3:8b")
        
        # OpenAI with .env file:
        llm_service = create_llm_service("openai")
        
        # Explicit API key:
        llm_service = create_llm_service("openai", api_key="...")
    """
    if provider.lower() == "ollama":
        return OllamaLLMService(**kwargs)
    elif provider.lower() == "openai":
        return OpenAILLMService(**kwargs)
    elif provider.lower() == "anthropic":
        return AnthropicLLMService(**kwargs)
    elif provider.lower() == "http":
        return HTTPLLMService(**kwargs)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Supported: 'ollama', 'openai', 'anthropic', 'http'")


def create_ollama_service(
    model: str = "llama3:latest",
    base_url: str = "http://localhost:11434",
    timeout: int = 60
) -> OllamaLLMService:
    """
    Convenience function to create Ollama service for local testing.
    
    Args:
        model: Ollama model to use (default: "llama3:latest")
        base_url: Ollama server URL (default: "http://localhost:11434")
        timeout: Request timeout in seconds (default: 60)
        
    Returns:
        Ollama service configured for local testing
        
    Examples:
        # Default configuration:
        llm_service = create_ollama_service()
        
        # Custom model:
        llm_service = create_ollama_service(model="codellama:latest")
        
        # Remote Ollama server:
        llm_service = create_ollama_service(base_url="http://your-server:11434")
    """
    return OllamaLLMService(model=model, base_url=base_url, timeout=timeout)


def create_rate_limited_openai_service(
    api_key: Optional[str] = None,
    model: str = "gpt-3.5-turbo",
    requests_per_minute: int = 3,
    requests_per_day: int = 200
) -> OpenAILLMService:
    """
    Convenience function to create OpenAI service with strict Tier 1 rate limits.
    
    Args:
        api_key: OpenAI API key (will use .env if not provided)
        model: Model to use
        requests_per_minute: Max requests per minute (default: 3 for free tier)
        requests_per_day: Max requests per day (default: 200 for free tier)
        
    Returns:
        OpenAI service configured for free tier limits
    """
    config = RateLimitConfig(
        requests_per_minute=requests_per_minute,
        requests_per_day=requests_per_day,
        tokens_per_minute=40000,  # Free tier TPM limit
        max_retries=3,
        base_delay=1.0,
        max_delay=60.0
    )
    
    return OpenAILLMService(
        api_key=api_key,
        model=model,
        rate_limit_config=config
    )


# ============================================================================
# USAGE EXAMPLES AND DOCUMENTATION
# ============================================================================

"""
SETUP INSTRUCTIONS:

OPTION 1: LOCAL OLLAMA (RECOMMENDED FOR TESTING)
1. Install Ollama: https://ollama.ai/
2. Start Ollama server: ollama serve
3. Pull Llama3 model: ollama pull llama3
4. Use without any API keys:
   llm_service = create_llm_service()  # Defaults to Ollama with llama3:latest
   result = await llm_service.generate_content("Create a D&D character")

OPTION 2: CLOUD PROVIDERS (FOR PRODUCTION)
1. Install required packages:
   pip install openai anthropic httpx python-dotenv

2. Create .env file in your project root:
   OPENAI_API_KEY=your-openai-api-key-here
   ANTHROPIC_API_KEY=your-anthropic-api-key-here

3. Usage examples:

   # Default (Ollama for testing):
   llm_service = create_llm_service()
   
   # OpenAI with .env file:
   llm_service = create_llm_service("openai")
   result = await llm_service.generate_content("Create a D&D character")
   
   # Custom Ollama model:
   llm_service = create_llm_service("ollama", model="codellama")
   
   # With custom rate limits for paid tiers:
   config = RateLimitConfig(requests_per_minute=60, requests_per_day=10000)
   llm_service = create_llm_service("openai", rate_limit_config=config)
   
   # Strict free tier compliance:
   llm_service = create_rate_limited_openai_service()
   
   # Test connection:
   is_available = await llm_service.test_connection()
   if is_available:
       print("LLM service is ready!")

PROVIDER COMPARISON:
- Ollama: Free, local, no API keys needed, slower, good for testing
- OpenAI: Fast, cloud-based, requires API key, rate limited, good for production
- Anthropic: Fast, cloud-based, requires API key, rate limited, alternative to OpenAI

RATE LIMITING (Cloud providers only):
- Free tier limits are strictly enforced
- Automatic exponential backoff on rate limit errors
- Token usage estimation and tracking
- Per-minute and per-day request tracking
- Comprehensive logging of rate limit status

ENVIRONMENT VARIABLES:
- OPENAI_API_KEY: Your OpenAI API key
- ANTHROPIC_API_KEY: Your Anthropic API key
"""
