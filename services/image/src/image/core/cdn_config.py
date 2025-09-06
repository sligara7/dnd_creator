"""CDN configuration and settings."""
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class CdnRegion(str, Enum):
    """Available CDN regions."""
    US_EAST = "us-east"
    US_WEST = "us-west"
    EU_WEST = "eu-west"
    EU_CENTRAL = "eu-central"
    ASIA_EAST = "asia-east"
    ASIA_SOUTHEAST = "asia-southeast"


class CdnZone(BaseModel):
    """CDN zone configuration."""

    zone_id: str = Field(..., description="Zone identifier")
    region: CdnRegion = Field(..., description="Geographic region")
    base_url: str = Field(..., description="Base URL for zone")
    cache_ttl: int = Field(3600, description="Default cache TTL in seconds")
    max_age: int = Field(86400, description="Browser cache max-age")
    stale_ttl: int = Field(300, description="Stale-while-revalidate TTL")
    error_ttl: int = Field(60, description="Stale-if-error TTL")


class CdnConfig(BaseModel):
    """CDN service configuration."""

    default_region: CdnRegion = Field(
        CdnRegion.US_EAST,
        description="Default region for new uploads"
    )
    zones: Dict[CdnRegion, CdnZone] = Field(
        ...,
        description="Zone configurations by region"
    )
    token: str = Field(..., description="CDN API token")
    retry_limit: int = Field(3, description="Maximum retry attempts")
    retry_delay: float = Field(1.0, description="Delay between retries")
    timeout: float = Field(30.0, description="Request timeout in seconds")
    max_batch_size: int = Field(100, description="Maximum batch operation size")

    # Cache optimization settings
    browser_cache_control: str = Field(
        "public, max-age=86400",
        description="Browser Cache-Control header"
    )
    cdn_cache_control: str = Field(
        "public, max-age=3600, stale-while-revalidate=300",
        description="CDN Cache-Control header"
    )

    # Performance settings
    min_compress_size: int = Field(
        1024,
        description="Minimum size for compression"
    )
    compression_level: int = Field(
        6,
        description="Compression level (1-9)"
    )
    read_chunk_size: int = Field(
        8192,
        description="Chunk size for streaming reads"
    )

    # Security settings
    allowed_origins: list[str] = Field(
        ["*"],
        description="Allowed CORS origins"
    )
    allowed_methods: list[str] = Field(
        ["GET", "HEAD"],
        description="Allowed HTTP methods"
    )
    max_file_size: int = Field(
        100 * 1024 * 1024,  # 100MB
        description="Maximum file size"
    )

    # Metrics and monitoring
    metrics_enabled: bool = Field(
        True,
        description="Enable metrics collection"
    )
    metrics_interval: int = Field(
        60,
        description="Metrics collection interval"
    )

    # Zone-specific overrides
    zone_overrides: Dict[str, Dict] = Field(
        default_factory=dict,
        description="Zone-specific setting overrides"
    )

    class Config:
        """Model configuration."""
        frozen = True


def get_default_cdn_config() -> CdnConfig:
    """Get default CDN configuration.

    Returns:
        Default CDN configuration
    """
    return CdnConfig(
        default_region=CdnRegion.US_EAST,
        zones={
            CdnRegion.US_EAST: CdnZone(
                zone_id="use1",
                region=CdnRegion.US_EAST,
                base_url="https://use1.cdn.dndcreator.com"
            ),
            CdnRegion.US_WEST: CdnZone(
                zone_id="usw1",
                region=CdnRegion.US_WEST,
                base_url="https://usw1.cdn.dndcreator.com"
            ),
            CdnRegion.EU_WEST: CdnZone(
                zone_id="euw1",
                region=CdnRegion.EU_WEST,
                base_url="https://euw1.cdn.dndcreator.com"
            ),
            CdnRegion.EU_CENTRAL: CdnZone(
                zone_id="euc1",
                region=CdnRegion.EU_CENTRAL,
                base_url="https://euc1.cdn.dndcreator.com"
            ),
            CdnRegion.ASIA_EAST: CdnZone(
                zone_id="ape1",
                region=CdnRegion.ASIA_EAST,
                base_url="https://ape1.cdn.dndcreator.com"
            ),
            CdnRegion.ASIA_SOUTHEAST: CdnZone(
                zone_id="aps1",
                region=CdnRegion.ASIA_SOUTHEAST,
                base_url="https://aps1.cdn.dndcreator.com"
            )
        },
        token="${CDN_TOKEN}",  # Placeholder for env var
        max_batch_size=100,
        browser_cache_control=(
            "public, max-age=86400, "
            "stale-while-revalidate=300, "
            "stale-if-error=60"
        ),
        cdn_cache_control=(
            "public, s-maxage=3600, "
            "stale-while-revalidate=300, "
            "stale-if-error=60"
        ),
        compression_level=6,
        allowed_origins=[
            "https://*.dndcreator.com",
            "http://localhost:*"
        ],
        allowed_methods=[
            "GET",
            "HEAD",
            "OPTIONS"
        ],
        max_file_size=100 * 1024 * 1024,  # 100MB
        metrics_enabled=True,
        metrics_interval=60,
    )
