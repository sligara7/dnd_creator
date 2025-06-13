# File: /backend5/infrastructure/config/external_services.py

# This file defines external API configurations.

class ExternalServiceConfig:
    """
    Configuration class for external services.
    """

    def __init__(self):
        self.api_base_url = "https://api.example.com"
        self.api_key = "your_api_key_here"
        self.timeout = 30  # seconds

    def get_api_url(self, endpoint: str) -> str:
        """
        Constructs the full API URL for a given endpoint.
        """
        return f"{self.api_base_url}/{endpoint}"

    def get_headers(self) -> dict:
        """
        Returns the headers required for API requests.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }