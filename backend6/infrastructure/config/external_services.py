"""
External Services Configuration

Configuration for external APIs and services used by the D&D Character Creator.
Handles API keys, endpoints, timeouts, and service-specific settings.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseSettings, validator, Field
import logging

from .settings import get_settings
from .environment import get_environment_config
# Import enum from core domain
from core.enums import LLMProvider

logger = logging.getLogger(__name__)
settings = get_settings()
env_config = get_environment_config()


class ExternalServicesConfig(BaseSettings):
    """
    Configuration for external services and APIs.
    
    Manages authentication, endpoints, and service-specific settings
    for all external integrations.
    """
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(None, env='OPENAI_API_KEY')
    openai_organization: Optional[str] = Field(None, env='OPENAI_ORGANIZATION')
    openai_base_url: str = Field("https://api.openai.com/v1", env='OPENAI_BASE_URL')
    openai_model: str = Field("gpt-4", env='OPENAI_MODEL')
    openai_temperature: float = Field(0.7, env='OPENAI_TEMPERATURE')
    openai_max_tokens: int = Field(2000, env='OPENAI_MAX_TOKENS')
    openai_timeout: int = Field(60, env='OPENAI_TIMEOUT')
    
    # Azure OpenAI Configuration
    azure_openai_api_key: Optional[str] = Field(None, env='AZURE_OPENAI_API_KEY')
    azure_openai_endpoint: Optional[str] = Field(None, env='AZURE_OPENAI_ENDPOINT')
    azure_openai_deployment: Optional[str] = Field(None, env='AZURE_OPENAI_DEPLOYMENT')
    azure_openai_api_version: str = Field("2024-02-15-preview", env='AZURE_OPENAI_API_VERSION')
    
    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(None, env='ANTHROPIC_API_KEY')
    anthropic_base_url: str = Field("https://api.anthropic.com", env='ANTHROPIC_BASE_URL')
    anthropic_model: str = Field("claude-3-sonnet-20240229", env='ANTHROPIC_MODEL')
    anthropic_max_tokens: int = Field(2000, env='ANTHROPIC_MAX_TOKENS')
    anthropic_timeout: int = Field(60, env='ANTHROPIC_TIMEOUT')
    
    # Google AI Configuration
    google_api_key: Optional[str] = Field(None, env='GOOGLE_API_KEY')
    google_model: str = Field("gemini-pro", env='GOOGLE_MODEL')
    google_base_url: str = Field("https://generativelanguage.googleapis.com", env='GOOGLE_BASE_URL')
    
    # Local LLM Configuration
    local_llm_endpoint: Optional[str] = Field(None, env='LOCAL_LLM_ENDPOINT')
    local_llm_model: str = Field("llama2", env='LOCAL_LLM_MODEL')
    
    # Content Generation Settings (using domain enum)
    primary_llm_provider: LLMProvider = Field(LLMProvider.OPENAI, env='PRIMARY_LLM_PROVIDER')
    fallback_llm_provider: Optional[LLMProvider] = Field(LLMProvider.ANTHROPIC, env='FALLBACK_LLM_PROVIDER')
    
    # Rate limiting and retry settings
    max_requests_per_minute: int = Field(60, env='MAX_REQUESTS_PER_MINUTE')
    max_retries: int = Field(3, env='MAX_RETRIES')
    retry_delay: float = Field(1.0, env='RETRY_DELAY')
    
    # Cache settings for external API responses
    cache_api_responses: bool = Field(True, env='CACHE_API_RESPONSES')
    api_cache_ttl: int = Field(3600, env='API_CACHE_TTL')  # 1 hour
    
    # Monitoring and logging
    log_api_requests: bool = Field(True, env='LOG_API_REQUESTS')
    log_api_responses: bool = Field(False, env='LOG_API_RESPONSES')  # Potentially large
    enable_api_metrics: bool = Field(True, env='ENABLE_API_METRICS')
    
    # Content filtering and safety
    enable_content_filtering: bool = Field(True, env='ENABLE_CONTENT_FILTERING')
    content_filter_threshold: float = Field(0.8, env='CONTENT_FILTER_THRESHOLD')
    
    # External validation services
    grammar_check_api_key: Optional[str] = Field(None, env='GRAMMAR_CHECK_API_KEY')
    spell_check_service_url: Optional[str] = Field(None, env='SPELL_CHECK_SERVICE_URL')
    
    @validator('primary_llm_provider', 'fallback_llm_provider', pre=True)
    def validate_llm_provider(cls, v):
        """Validate LLM provider values."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                return LLMProvider(v.lower())
            except ValueError:
                raise ValueError(f"Invalid LLM provider: {v}")
        return v
    
    @validator('openai_temperature', 'content_filter_threshold')
    def validate_float_range(cls, v):
        """Validate float values are in valid range."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Value must be between 0.0 and 1.0")
        return v
    
    @validator('openai_max_tokens', 'anthropic_max_tokens')
    def validate_max_tokens(cls, v):
        """Validate max tokens are reasonable."""
        if v < 1 or v > 8192:
            raise ValueError("Max tokens must be between 1 and 8192")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class ServiceManager:
    """
    Manager for external service configurations and health checks.
    
    Provides service discovery, health monitoring, and configuration management
    for all external service integrations.
    """
    
    def __init__(self, config: Optional[ExternalServicesConfig] = None):
        self.config = config or ExternalServicesConfig()
        self._service_health = {}
        self._service_stats = {}
    
    def get_llm_config(self, provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
        """
        Get configuration for a specific LLM provider.
        
        Args:
            provider: LLM provider to get config for (defaults to primary)
            
        Returns:
            Dictionary containing provider configuration
        """
        provider = provider or self.config.primary_llm_provider
        
        configs = {
            LLMProvider.OPENAI: {
                'api_key': self.config.openai_api_key,
                'base_url': self.config.openai_base_url,
                'model': self.config.openai_model,
                'temperature': self.config.openai_temperature,
                'max_tokens': self.config.openai_max_tokens,
                'timeout': self.config.openai_timeout,
                'organization': self.config.openai_organization
            },
            LLMProvider.ANTHROPIC: {
                'api_key': self.config.anthropic_api_key,
                'base_url': self.config.anthropic_base_url,
                'model': self.config.anthropic_model,
                'max_tokens': self.config.anthropic_max_tokens,
                'timeout': self.config.anthropic_timeout
            },
            LLMProvider.AZURE_OPENAI: {
                'api_key': self.config.azure_openai_api_key,
                'endpoint': self.config.azure_openai_endpoint,
                'deployment': self.config.azure_openai_deployment,
                'api_version': self.config.azure_openai_api_version
            },
            LLMProvider.GOOGLE: {
                'api_key': self.config.google_api_key,
                'base_url': self.config.google_base_url,
                'model': self.config.google_model
            },
            LLMProvider.LOCAL: {
                'endpoint': self.config.local_llm_endpoint,
                'model': self.config.local_llm_model
            }
        }
        
        return configs.get(provider, {})
    
    def is_service_available(self, provider: LLMProvider) -> bool:
        """
        Check if a service is available and properly configured.
        
        Args:
            provider: LLM provider to check
            
        Returns:
            True if service is available
        """
        config = self.get_llm_config(provider)
        
        # Check for required configuration
        required_fields = {
            LLMProvider.OPENAI: ['api_key'],
            LLMProvider.ANTHROPIC: ['api_key'],
            LLMProvider.AZURE_OPENAI: ['api_key', 'endpoint', 'deployment'],
            LLMProvider.GOOGLE: ['api_key'],
            LLMProvider.LOCAL: ['endpoint']
        }
        
        required = required_fields.get(provider, [])
        return all(config.get(field) for field in required)
    
    def get_available_providers(self) -> List[LLMProvider]:
        """
        Get list of available LLM providers.
        
        Returns:
            List of configured and available providers
        """
        return [
            provider for provider in LLMProvider
            if self.is_service_available(provider)
        ]
    
    def get_primary_provider(self) -> LLMProvider:
        """
        Get the primary LLM provider, falling back if necessary.
        
        Returns:
            Available LLM provider
        """
        if self.is_service_available(self.config.primary_llm_provider):
            return self.config.primary_llm_provider
        
        if (self.config.fallback_llm_provider and 
            self.is_service_available(self.config.fallback_llm_provider)):
            logger.warning(f"Primary provider {self.config.primary_llm_provider} unavailable, using fallback")
            return self.config.fallback_llm_provider
        
        # Find any available provider
        available = self.get_available_providers()
        if available:
            logger.warning(f"Using first available provider: {available[0]}")
            return available[0]
        
        raise RuntimeError("No LLM providers are available")
    
    async def health_check(self, provider: LLMProvider) -> Dict[str, Any]:
        """
        Perform health check on a service.
        
        Args:
            provider: Provider to check
            
        Returns:
            Health check results
        """
        result = {
            'provider': provider.value,
            'available': False,
            'response_time': None,
            'error': None,
            'timestamp': None
        }
        
        try:
            import time
            start_time = time.time()
            
            # Basic availability check
            if not self.is_service_available(provider):
                result['error'] = 'Service not configured'
                return result
            
            # TODO: Implement actual API health checks for each provider
            # For now, just check configuration
            result['available'] = True
            result['response_time'] = time.time() - start_time
            result['timestamp'] = time.time()
            
            self._service_health[provider] = result
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Health check failed for {provider}: {e}")
        
        return result
    
    def get_service_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all external services.
        
        Returns:
            Dictionary containing service statistics
        """
        return {
            'available_providers': [p.value for p in self.get_available_providers()],
            'primary_provider': self.config.primary_llm_provider.value,
            'fallback_provider': self.config.fallback_llm_provider.value if self.config.fallback_llm_provider else None,
            'health_status': self._service_health,
            'configuration': {
                'cache_enabled': self.config.cache_api_responses,
                'content_filtering': self.config.enable_content_filtering,
                'max_requests_per_minute': self.config.max_requests_per_minute,
                'max_retries': self.config.max_retries
            }
        }
    
    def get_rate_limit_config(self) -> Dict[str, Any]:
        """
        Get rate limiting configuration.
        
        Returns:
            Rate limiting settings
        """
        return {
            'max_requests_per_minute': self.config.max_requests_per_minute,
            'max_retries': self.config.max_retries,
            'retry_delay': self.config.retry_delay,
            'timeout_settings': {
                'openai': self.config.openai_timeout,
                'anthropic': self.config.anthropic_timeout
            }
        }


# Environment-specific configuration overrides
def get_environment_specific_config() -> Dict[str, Any]:
    """
    Get environment-specific external service configuration.
    
    Returns:
        Dictionary of environment-specific overrides
    """
    overrides = {}
    
    if env_config.is_development:
        overrides.update({
            'log_api_requests': True,
            'log_api_responses': True,
            'cache_api_responses': False,  # Disable cache in development
            'max_requests_per_minute': 10,  # Lower limits for development
            'enable_content_filtering': False  # Disable filtering for testing
        })
    
    elif env_config.is_testing:
        overrides.update({
            'log_api_requests': False,
            'log_api_responses': False,
            'cache_api_responses': False,
            'max_requests_per_minute': 1,  # Very low for tests
            'primary_llm_provider': LLMProvider.LOCAL,  # Use mock/local for tests
            'enable_content_filtering': False
        })
    
    elif env_config.is_production:
        overrides.update({
            'log_api_requests': True,
            'log_api_responses': False,  # Don't log responses in production
            'cache_api_responses': True,
            'max_requests_per_minute': 100,  # Higher limits for production
            'enable_content_filtering': True,
            'enable_api_metrics': True
        })
    
    return overrides


# Global service manager instance
_service_manager: Optional[ServiceManager] = None


def get_service_manager() -> ServiceManager:
    """
    Get global service manager instance.
    
    Returns:
        ServiceManager: Global service manager
    """
    global _service_manager
    if _service_manager is None:
        config = ExternalServicesConfig()
        
        # Apply environment-specific overrides
        env_overrides = get_environment_specific_config()
        for key, value in env_overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        _service_manager = ServiceManager(config)
    
    return _service_manager


def get_llm_config(provider: Optional[LLMProvider] = None) -> Dict[str, Any]:
    """
    Convenience function to get LLM configuration.
    
    Args:
        provider: LLM provider (defaults to primary)
        
    Returns:
        Provider configuration dictionary
    """
    return get_service_manager().get_llm_config(provider)


def get_primary_llm_provider() -> LLMProvider:
    """
    Get the primary available LLM provider.
    
    Returns:
        Primary LLM provider
    """
    return get_service_manager().get_primary_provider()


async def check_service_health() -> Dict[str, Any]:
    """
    Check health of all configured external services.
    
    Returns:
        Health check results for all services
    """
    service_manager = get_service_manager()
    results = {}
    
    for provider in service_manager.get_available_providers():
        results[provider.value] = await service_manager.health_check(provider)
    
    return {
        'services': results,
        'summary': {
            'total_services': len(results),
            'healthy_services': sum(1 for r in results.values() if r['available']),
            'timestamp': None  # Will be set by caller
        }
    }


# Configuration validation
def validate_external_services_config() -> List[str]:
    """
    Validate external services configuration.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    service_manager = get_service_manager()
    
    # Check if at least one provider is available
    available_providers = service_manager.get_available_providers()
    if not available_providers:
        errors.append("No LLM providers are configured and available")
    
    # Check primary provider availability
    try:
        primary = service_manager.get_primary_provider()
        logger.info(f"Primary LLM provider: {primary.value}")
    except RuntimeError as e:
        errors.append(f"Primary provider issue: {e}")
    
    # Validate configuration values
    config = service_manager.config
    if config.openai_temperature < 0 or config.openai_temperature > 1:
        errors.append("OpenAI temperature must be between 0 and 1")
    
    if config.max_requests_per_minute <= 0:
        errors.append("Max requests per minute must be positive")
    
    return errors