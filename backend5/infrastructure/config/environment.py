"""
Infrastructure Configuration

Application settings, environment configuration, and external service setup.
These are deployment and runtime concerns, not domain knowledge.
"""

from .settings import Settings, get_settings
from .database import DatabaseConfig
from .external_services import ExternalServicesConfig
from .environment import EnvironmentConfig

# Global settings instance
settings = get_settings()

__all__ = [
    'Settings',
    'get_settings', 
    'settings',
    'DatabaseConfig',
    'ExternalServicesConfig',
    'EnvironmentConfig'
]