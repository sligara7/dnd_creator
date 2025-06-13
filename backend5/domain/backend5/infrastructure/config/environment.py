# This file defines environment-specific configurations.

import os

class EnvironmentConfig:
    """Class to manage environment-specific configurations."""

    @staticmethod
    def get_database_url():
        """Get the database URL from environment variables."""
        return os.getenv("DATABASE_URL", "sqlite:///default.db")

    @staticmethod
    def get_external_service_api_key():
        """Get the API key for external services from environment variables."""
        return os.getenv("EXTERNAL_SERVICE_API_KEY", "default_api_key")

    @staticmethod
    def is_debug_mode():
        """Check if the application is in debug mode."""
        return os.getenv("DEBUG_MODE", "false").lower() == "true"

    @staticmethod
    def get_environment():
        """Get the current environment (development, testing, production)."""
        return os.getenv("ENVIRONMENT", "development")