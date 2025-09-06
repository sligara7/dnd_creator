"""Monitoring and analytics for generation pipeline."""
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from prometheus_client import Counter, Gauge, Histogram, Summary
import structlog

from ..models.theme import ContentType, GenerationConfig, GenerationMetadata, ThemeContext


# Prometheus metrics
GENERATION_REQUESTS = Counter(
    "generation_requests_total",
    "Total number of generation requests",
    ["content_type", "theme_type", "model"]
)

GENERATION_ERRORS = Counter(
    "generation_errors_total",
    "Total number of generation errors",
    ["content_type", "theme_type", "error_type"]
)

GENERATION_TIME = Histogram(
    "generation_time_seconds",
    "Time spent generating content",
    ["content_type", "theme_type", "model"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

TOKEN_USAGE = Counter(
    "token_usage_total",
    "Total number of tokens used",
    ["content_type", "theme_type", "token_type"]
)

CACHE_HITS = Counter(
    "cache_hits_total",
    "Total number of cache hits",
    ["content_type", "theme_type"]
)

THEME_VALIDATION_TIME = Summary(
    "theme_validation_time_seconds",
    "Time spent validating theme compatibility",
    ["content_type", "theme_type"]
)

ACTIVE_GENERATIONS = Gauge(
    "active_generations",
    "Number of active generation requests",
    ["content_type", "theme_type"]
)


@dataclass
class GenerationStats:
    """Statistics for a generation request."""
    start_time: datetime
    end_time: Optional[datetime] = None
    content_type: Optional[ContentType] = None
    theme_type: Optional[str] = None
    model: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    generation_time_ms: int = 0
    cache_hit: bool = False
    errors: List[str] = None

    @property
    def duration_seconds(self) -> float:
        """Calculate duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class MetricsTracker:
    """Tracker for generation metrics and analytics."""

    def __init__(self, logger: Optional[structlog.BoundLogger] = None):
        """Initialize the metrics tracker."""
        self.logger = logger or structlog.get_logger()

    def _get_theme_type(self, theme_context: Optional[ThemeContext]) -> str:
        """Get theme type string."""
        if not theme_context:
            return "none"
        return theme_context.type.value

    def record_generation_start(
        self,
        content_type: ContentType,
        theme_context: Optional[ThemeContext] = None
    ) -> GenerationStats:
        """Record the start of a generation request."""
        stats = GenerationStats(
            start_time=datetime.now(),
            content_type=content_type,
            theme_type=self._get_theme_type(theme_context)
        )

        # Update active generations gauge
        ACTIVE_GENERATIONS.labels(
            content_type=content_type.value,
            theme_type=stats.theme_type
        ).inc()

        return stats

    def record_generation_complete(
        self,
        stats: GenerationStats,
        metadata: GenerationMetadata
    ) -> None:
        """Record completion of a generation request."""
        stats.end_time = datetime.now()
        stats.model = metadata.model_name
        stats.prompt_tokens = metadata.prompt_tokens
        stats.completion_tokens = metadata.completion_tokens
        stats.total_tokens = metadata.total_tokens
        stats.generation_time_ms = metadata.generation_time_ms
        stats.cache_hit = metadata.cached

        # Update metrics
        GENERATION_REQUESTS.labels(
            content_type=stats.content_type.value,
            theme_type=stats.theme_type,
            model=stats.model
        ).inc()

        GENERATION_TIME.labels(
            content_type=stats.content_type.value,
            theme_type=stats.theme_type,
            model=stats.model
        ).observe(stats.duration_seconds)

        TOKEN_USAGE.labels(
            content_type=stats.content_type.value,
            theme_type=stats.theme_type,
            token_type="prompt"
        ).inc(stats.prompt_tokens)

        TOKEN_USAGE.labels(
            content_type=stats.content_type.value,
            theme_type=stats.theme_type,
            token_type="completion"
        ).inc(stats.completion_tokens)

        if stats.cache_hit:
            CACHE_HITS.labels(
                content_type=stats.content_type.value,
                theme_type=stats.theme_type
            ).inc()

        # Update active generations gauge
        ACTIVE_GENERATIONS.labels(
            content_type=stats.content_type.value,
            theme_type=stats.theme_type
        ).dec()

        # Log completion
        self.logger.info(
            "generation_complete",
            content_type=stats.content_type.value,
            theme_type=stats.theme_type,
            model=stats.model,
            duration_seconds=stats.duration_seconds,
            total_tokens=stats.total_tokens,
            cache_hit=stats.cache_hit
        )

    def record_generation_error(
        self,
        stats: GenerationStats,
        error: Exception
    ) -> None:
        """Record a generation error."""
        stats.end_time = datetime.now()
        stats.errors = [str(error)]

        # Update error metrics
        GENERATION_ERRORS.labels(
            content_type=stats.content_type.value,
            theme_type=stats.theme_type,
            error_type=error.__class__.__name__
        ).inc()

        # Update active generations gauge
        ACTIVE_GENERATIONS.labels(
            content_type=stats.content_type.value,
            theme_type=stats.theme_type
        ).dec()

        # Log error
        self.logger.error(
            "generation_error",
            content_type=stats.content_type.value,
            theme_type=stats.theme_type,
            error=str(error),
            duration_seconds=stats.duration_seconds
        )

    def time_theme_validation(
        self,
        content_type: ContentType,
        theme_context: ThemeContext
    ) -> None:
        """Record theme validation timing."""
        start_time = time.time()
        theme_type = self._get_theme_type(theme_context)

        try:
            yield
        finally:
            duration = time.time() - start_time
            THEME_VALIDATION_TIME.labels(
                content_type=content_type.value,
                theme_type=theme_type
            ).observe(duration)


class TokenAnalytics:
    """Analytics for token usage."""

    @staticmethod
    def analyze_token_usage(
        metadata: GenerationMetadata,
        content_type: ContentType,
        theme_context: Optional[ThemeContext] = None
    ) -> Dict[str, float]:
        """Analyze token usage patterns."""
        theme_type = theme_context.type.value if theme_context else "none"
        
        return {
            "efficiency": metadata.completion_tokens / metadata.total_tokens,
            "prompt_ratio": metadata.prompt_tokens / metadata.total_tokens,
            "tokens_per_second": metadata.total_tokens / (metadata.generation_time_ms / 1000),
            "content_type": content_type.value,
            "theme_type": theme_type,
        }

    @staticmethod
    def get_token_usage_recommendations(
        analytics: Dict[str, float]
    ) -> List[str]:
        """Get recommendations for token usage optimization."""
        recommendations = []

        if analytics["efficiency"] < 0.5:
            recommendations.append(
                "Consider reducing prompt size to improve completion ratio"
            )

        if analytics["tokens_per_second"] < 10:
            recommendations.append(
                "Generation speed is below target, consider request optimization"
            )

        if analytics["prompt_ratio"] > 0.7:
            recommendations.append(
                "High prompt token usage, consider prompt compression"
            )

        return recommendations
