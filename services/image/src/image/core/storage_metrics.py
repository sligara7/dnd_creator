"""Prometheus metrics for storage operations."""
import logging
from datetime import datetime
from typing import Optional

from prometheus_client import Counter, Gauge, Histogram
from prometheus_client.utils import INF

logger = logging.getLogger(__name__)

# Storage operation metrics
STORAGE_OPERATIONS = Counter(
    "image_storage_operations_total",
    "Number of storage operations",
    ["operation", "status"]
)

# Storage timing metrics
UPLOAD_TIME = Histogram(
    "image_upload_seconds",
    "Time spent uploading images",
    ["image_type"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, INF)
)

DOWNLOAD_TIME = Histogram(
    "image_download_seconds",
    "Time spent downloading images",
    ["image_type"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, INF)
)

# Storage size metrics
STORAGE_SIZE = Gauge(
    "image_storage_bytes_total",
    "Total storage size in bytes",
    ["storage_type"]  # s3, local, cdn
)

STORAGE_COUNT = Gauge(
    "image_storage_count_total",
    "Total number of stored images",
    ["storage_type", "image_type"]
)

# Deduplication metrics
DEDUPLICATIONS = Counter(
    "image_deduplications_total",
    "Number of deduplicated images",
    ["image_type"]
)

STORAGE_SAVED = Counter(
    "image_storage_saved_bytes",
    "Storage space saved by deduplication",
    ["image_type"]
)

# CDN metrics
CDN_HITS = Counter(
    "image_cdn_hits_total",
    "Number of CDN cache hits",
    ["cdn_region"]
)

CDN_MISSES = Counter(
    "image_cdn_misses_total",
    "Number of CDN cache misses",
    ["cdn_region"]
)

CDN_ERRORS = Counter(
    "image_cdn_errors_total",
    "Number of CDN errors",
    ["error_type"]
)

CDN_BANDWIDTH = Counter(
    "image_cdn_bandwidth_bytes",
    "CDN bandwidth usage in bytes",
    ["direction"]  # ingress/egress
)

# Version control metrics
VERSION_COUNTS = Gauge(
    "image_versions_total",
    "Number of image versions",
    ["image_type"]
)

VERSION_STORAGE = Counter(
    "image_version_storage_bytes",
    "Storage used by image versions",
    ["image_type"]
)


def record_storage_operation(operation: str, status: str = "success") -> None:
    """Record storage operation metric.

    Args:
        operation: Type of operation
        status: Operation status
    """
    STORAGE_OPERATIONS.labels(
        operation=operation,
        status=status
    ).inc()


def record_upload_time(
    seconds: float,
    image_type: Optional[str] = None
) -> None:
    """Record upload time metric.

    Args:
        seconds: Upload duration
        image_type: Optional image type
    """
    UPLOAD_TIME.labels(
        image_type=image_type or "unknown"
    ).observe(seconds)


def record_download_time(
    seconds: float,
    image_type: Optional[str] = None
) -> None:
    """Record download time metric.

    Args:
        seconds: Download duration
        image_type: Optional image type
    """
    DOWNLOAD_TIME.labels(
        image_type=image_type or "unknown"
    ).observe(seconds)


def record_storage_size(
    bytes_count: int,
    storage_type: str = "s3"
) -> None:
    """Record storage size metric.

    Args:
        bytes_count: Size in bytes
        storage_type: Storage location
    """
    STORAGE_SIZE.labels(storage_type=storage_type).inc(bytes_count)


def record_storage_count(
    count: int,
    storage_type: str,
    image_type: str
) -> None:
    """Record storage count metric.

    Args:
        count: Number of images
        storage_type: Storage location
        image_type: Type of image
    """
    STORAGE_COUNT.labels(
        storage_type=storage_type,
        image_type=image_type
    ).set(count)


def record_deduplication(
    image_type: str,
    bytes_saved: int
) -> None:
    """Record deduplication metrics.

    Args:
        image_type: Type of deduplicated image
        bytes_saved: Storage space saved
    """
    DEDUPLICATIONS.labels(image_type=image_type).inc()
    STORAGE_SAVED.labels(image_type=image_type).inc(bytes_saved)


def record_cdn_hit(region: str) -> None:
    """Record CDN cache hit.

    Args:
        region: CDN region
    """
    CDN_HITS.labels(cdn_region=region).inc()


def record_cdn_miss(region: str) -> None:
    """Record CDN cache miss.

    Args:
        region: CDN region
    """
    CDN_MISSES.labels(cdn_region=region).inc()


def record_cdn_error(error_type: str) -> None:
    """Record CDN error.

    Args:
        error_type: Type of error
    """
    CDN_ERRORS.labels(error_type=error_type).inc()


def record_cdn_bandwidth(bytes_count: int, direction: str) -> None:
    """Record CDN bandwidth usage.

    Args:
        bytes_count: Bytes transferred
        direction: Traffic direction (ingress/egress)
    """
    CDN_BANDWIDTH.labels(direction=direction).inc(bytes_count)


def record_version_count(image_type: str, count: int) -> None:
    """Record version count metric.

    Args:
        image_type: Type of image
        count: Number of versions
    """
    VERSION_COUNTS.labels(image_type=image_type).set(count)


def record_version_storage(image_type: str, bytes_count: int) -> None:
    """Record version storage usage.

    Args:
        image_type: Type of image
        bytes_count: Storage used
    """
    VERSION_STORAGE.labels(image_type=image_type).inc(bytes_count)
