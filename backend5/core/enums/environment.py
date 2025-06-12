"""
Environment Enumeration

Core application environment types used across all layers.
"""

from enum import Enum


class Environment(Enum):
    """
    Application environment types.
    
    Defines the different deployment/runtime environments the application
    can operate in, each with specific behavior and configuration.
    """
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    LOCAL = "local"
    
    @property
    def is_development_like(self) -> bool:
        """Check if environment is development-like (development or local)."""
        return self in [self.DEVELOPMENT, self.LOCAL]
    
    @property
    def is_production_like(self) -> bool:
        """Check if environment is production-like (staging or production)."""
        return self in [self.STAGING, self.PRODUCTION]
    
    @property
    def requires_security(self) -> bool:
        """Check if environment requires enhanced security measures."""
        return self in [self.STAGING, self.PRODUCTION]
    
    @property
    def allows_debug(self) -> bool:
        """Check if environment allows debug features."""
        return self in [self.DEVELOPMENT, self.LOCAL, self.TESTING]