"""
Environment Configuration Management

Handles environment-specific configuration, environment detection,
and environment-based settings override for different deployment contexts.
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

# Import from core enums
from core.enums import Environment

logger = logging.getLogger(__name__)


class EnvironmentConfig:
    """
    Environment-specific configuration management.
    
    Handles detection of current environment and provides environment-specific
    configuration overrides and behaviors.
    """
    
    def __init__(self, env: Optional[str] = None):
        self._environment = self._detect_environment(env)
        self._config_overrides = {}
        self._setup_environment_defaults()
    
    @property
    def current_environment(self) -> Environment:
        """Get current environment."""
        return self._environment
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self._environment.is_development_like
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self._environment == Environment.TESTING
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self._environment == Environment.STAGING
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self._environment == Environment.PRODUCTION
    
    def _detect_environment(self, env: Optional[str] = None) -> Environment:
        """
        Detect current environment from various sources.
        
        Args:
            env: Explicitly provided environment name
            
        Returns:
            Environment: Detected environment
        """
        # Priority order for environment detection:
        # 1. Explicitly provided parameter
        # 2. ENVIRONMENT environment variable
        # 3. APP_ENV environment variable
        # 4. NODE_ENV environment variable (for compatibility)
        # 5. Detect from other indicators
        # 6. Default to development
        
        env_sources = [
            env,
            os.getenv('ENVIRONMENT'),
            os.getenv('APP_ENV'),
            os.getenv('NODE_ENV'),
            self._detect_from_indicators()
        ]
        
        for env_value in env_sources:
            if env_value:
                try:
                    detected_env = Environment(env_value.lower())
                    logger.info(f"Environment detected: {detected_env.value}")
                    return detected_env
                except ValueError:
                    logger.warning(f"Invalid environment value: {env_value}")
                    continue
        
        # Default to development
        default_env = Environment.DEVELOPMENT
        logger.info(f"Using default environment: {default_env.value}")
        return default_env
    
    # ... rest of the methods remain the same, just update the setup methods:
    
    def _setup_environment_defaults(self):
        """Setup default configuration overrides for each environment."""
        
        if self._environment.is_development_like:
            self._config_overrides.update({
                'debug': True,
                'log_level': 'DEBUG',
                'database_echo': True,
                'enable_hot_reload': True,
                'cors_allow_all': True,
                'cache_ttl': 60,  # Short cache for development
                'generation_timeout': 60,  # Shorter timeout for development
                'enable_profiling': True,
                'show_sql_queries': True
            })
        
        elif self.is_testing:
            self._config_overrides.update({
                'debug': False,
                'log_level': 'WARNING',
                'database_echo': False,
                'database_url': 'sqlite:///:memory:',  # In-memory for tests
                'enable_caching': False,  # Disable caching for consistent tests
                'generation_timeout': 30,
                'enable_external_apis': False,  # Mock external APIs
                'suppress_warnings': True
            })
        
        elif self.is_staging:
            self._config_overrides.update({
                'debug': False,
                'log_level': 'INFO',
                'database_echo': False,
                'enable_metrics': True,
                'cache_ttl': 300,
                'generation_timeout': 180,
                'enable_monitoring': True,
                'cors_allow_all': False
            })
        
        elif self.is_production:
            self._config_overrides.update({
                'debug': False,
                'log_level': 'WARNING',
                'database_echo': False,
                'enable_metrics': True,
                'enable_monitoring': True,
                'enable_alerting': True,
                'cache_ttl': 3600,
                'generation_timeout': 300,
                'cors_allow_all': False,
                'enable_security_headers': True,
                'require_https': True
            })
    
    def should_enable_feature(self, feature_name: str) -> bool:
        """
        Check if a feature should be enabled in current environment.
        
        Args:
            feature_name: Name of the feature to check
            
        Returns:
            bool: True if feature should be enabled
        """
        feature_flags = {
            'hot_reload': self._environment.allows_debug,
            'profiling': self._environment.allows_debug,
            'metrics': not self.is_testing,
            'monitoring': self._environment.is_production_like,
            'alerting': self.is_production,
            'debug_toolbar': self._environment.allows_debug,
            'sql_echo': self._environment.allows_debug,
            'external_apis': not self.is_testing,
            'caching': not self.is_testing,
            'security_headers': self._environment.requires_security,
            'rate_limiting': self._environment.requires_security,
            'request_logging': True,
            'error_tracking': self._environment.is_production_like
        }
        
        return feature_flags.get(feature_name, False)

# Global environment configuration instance
_env_config: Optional[EnvironmentConfig] = None


def get_environment_config() -> EnvironmentConfig:
    """
    Get global environment configuration instance.
    
    Returns:
        EnvironmentConfig: Global environment configuration
    """
    global _env_config
    if _env_config is None:
        _env_config = EnvironmentConfig()
    return _env_config


def get_current_environment() -> Environment:
    """
    Get current environment.
    
    Returns:
        Environment: Current environment
    """
    return get_environment_config().current_environment


def is_development() -> bool:
    """Check if running in development environment."""
    return get_environment_config().is_development


def is_testing() -> bool:
    """Check if running in testing environment."""
    return get_environment_config().is_testing


def is_production() -> bool:
    """Check if running in production environment."""
    return get_environment_config().is_production


def get_environment_info() -> Dict[str, Any]:
    """
    Get comprehensive environment information.
    
    Returns:
        Dict containing environment details
    """
    return get_environment_config().get_environment_info()


# Environment-specific configuration helpers
def configure_for_environment(settings_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment-specific configuration overrides.
    
    Args:
        settings_dict: Base settings dictionary
        
    Returns:
        Dict with environment-specific overrides applied
    """
    env_config = get_environment_config()
    overrides = env_config.get_all_overrides()
    
    # Apply overrides
    configured_settings = settings_dict.copy()
    configured_settings.update(overrides)
    
    return configured_settings


def setup_environment_logging():
    """Setup logging configuration for current environment."""
    import logging.config
    
    env_config = get_environment_config()
    log_config = env_config.setup_logging()
    
    logging.config.dictConfig(log_config)
    logger.info(f"Logging configured for {env_config.current_environment.value} environment")