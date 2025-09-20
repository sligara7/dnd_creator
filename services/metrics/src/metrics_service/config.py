"""Service configuration module."""

from typing import Any
from pydantic import BaseModel, Field

class PrometheusConfig(BaseModel):
    """Prometheus configuration settings."""
    scrape_interval: int = Field(default=15, description="Scrape interval in seconds")
    evaluation_interval: int = Field(default=15, description="Rule evaluation interval in seconds")
    retention_days: int = Field(default=15, description="Metrics retention period in days")

class ServiceConfig(BaseModel):
    """Main service configuration."""
    prometheus: PrometheusConfig = Field(default_factory=PrometheusConfig)
    storage_service_url: str = Field(default="http://storage:8000", description="Storage Service URL")
    message_hub_url: str = Field(default="amqp://guest:guest@message-hub:5672/", description="Message Hub URL")
    service_name: str = Field(default="metrics", description="Service name")

    @classmethod
    def from_env(cls, **env_vars: dict[str, Any]) -> "ServiceConfig":
        """Create configuration from environment variables."""
        return cls(
            prometheus=PrometheusConfig(
                scrape_interval=int(env_vars.get("PROMETHEUS_SCRAPE_INTERVAL", 15)),
                evaluation_interval=int(env_vars.get("PROMETHEUS_EVAL_INTERVAL", 15)),
                retention_days=int(env_vars.get("PROMETHEUS_RETENTION_DAYS", 15)),
            ),
            storage_service_url=env_vars.get("STORAGE_SERVICE_URL", "http://storage:8000"),
            message_hub_url=env_vars.get("MESSAGE_HUB_URL", "amqp://guest:guest@message-hub:5672/"),
            service_name=env_vars.get("SERVICE_NAME", "metrics"),
        )