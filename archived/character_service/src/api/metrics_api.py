"""
Metrics API Endpoints

This module provides endpoints for exposing application metrics,
with support for both custom formats and Prometheus.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.core.logging_config import get_logger
from src.services.metrics_service import get_metrics_service
from src.models.database_models import get_db

logger = get_logger(__name__)

router = APIRouter()

def format_prometheus_metrics(metrics: Dict[str, Any]) -> str:
    """Format metrics in Prometheus format."""
    output = []
    
    # CPU metrics
    output.extend([
        "# HELP cpu_usage_percent CPU usage percentage",
        "# TYPE cpu_usage_percent gauge",
        f"cpu_usage_percent {metrics['cpu']['usage_percent']}",
        "",
        "# HELP cpu_load_average System load average",
        "# TYPE cpu_load_average gauge",
        f"cpu_load_average{{interval=\"1min\"}} {metrics['cpu']['load_avg_1min']}",
        f"cpu_load_average{{interval=\"5min\"}} {metrics['cpu']['load_avg_5min']}",
        f"cpu_load_average{{interval=\"15min\"}} {metrics['cpu']['load_avg_15min']}"
    ])
    
    # Memory metrics
    output.extend([
        "",
        "# HELP memory_usage_bytes Memory usage in bytes",
        "# TYPE memory_usage_bytes gauge",
        f"memory_usage_bytes{{type=\"total\"}} {metrics['memory']['total']}",
        f"memory_usage_bytes{{type=\"used\"}} {metrics['memory']['used']}",
        f"memory_usage_bytes{{type=\"free\"}} {metrics['memory']['free']}",
        f"memory_usage_bytes{{type=\"available\"}} {metrics['memory']['available']}",
        "",
        "# HELP memory_usage_percent Memory usage percentage",
        "# TYPE memory_usage_percent gauge",
        f"memory_usage_percent {metrics['memory']['percent']}"
    ])
    
    # Database metrics
    output.extend([
        "",
        "# HELP db_pool_connections Database connection pool stats",
        "# TYPE db_pool_connections gauge",
        f"db_pool_connections{{state=\"total\"}} {metrics['database']['pool']['size']}",
        f"db_pool_connections{{state=\"in_use\"}} {metrics['database']['pool']['checked_out']}",
        f"db_pool_connections{{state=\"overflow\"}} {metrics['database']['pool']['overflow']}"
    ])
    
    # Query metrics
    query_stats = metrics['database']['queries']
    output.extend([
        "",
        "# HELP db_query_count Total number of database queries",
        "# TYPE db_query_count counter",
        f"db_query_count {query_stats['query_count']}"
    ])
    
    # Table metrics
    for table in query_stats.get('table_stats', []):
        output.extend([
            "",
            f"# HELP table_{table['table']}_rows Number of rows in table",
            f"# TYPE table_{table['table']}_rows gauge",
            f"table_rows{{table=\"{table['table']}\",type=\"live\"}} {table['live_rows']}",
            f"table_rows{{table=\"{table['table']}\",type=\"dead\"}} {table['dead_rows']}"
        ])
    
    # Request metrics
    for path, stats in metrics['requests'].items():
        safe_path = path.replace("/", "_").replace("-", "_").strip("_")
        output.extend([
            "",
            f"# HELP request_{safe_path}_count Request count for {path}",
            f"# TYPE request_{safe_path}_count counter",
            f"request_count{{path=\"{path}\"}} {stats['count']}",
            "",
            f"# HELP request_{safe_path}_errors Error count for {path}",
            f"# TYPE request_{safe_path}_errors counter",
            f"request_errors{{path=\"{path}\"}} {stats['error_count']}",
            "",
            f"# HELP request_{safe_path}_duration_seconds Request duration for {path}",
            f"# TYPE request_{safe_path}_duration_seconds histogram"
        ])
        
        # Add histogram buckets
        for bucket, count in stats['latency_buckets'].items():
            threshold = bucket.replace("le_", "")
            output.append(f"request_duration_seconds_bucket{{path=\"{path}\",le=\"{threshold}\"}} {count}")
        
        # Add histogram stats
        output.extend([
            f"request_duration_seconds_sum{{path=\"{path}\"}} {stats['avg_duration'] * stats['count']}",
            f"request_duration_seconds_count{{path=\"{path}\"}} {stats['count']}"
        ])
    
    return "\n".join(output)

@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get all metrics in JSON format."""
    metrics_service = get_metrics_service(db)
    
    try:
        # Collect all metrics
        metrics = {
            "cpu": await metrics_service.get_cpu_metrics(),
            "memory": await metrics_service.get_memory_metrics(),
            "database": await metrics_service.get_db_metrics(),
            "requests": metrics_service.get_request_metrics()
        }
        
        logger.info(
            "metrics_fetched",
            cpu_metrics=len(metrics["cpu"]),
            memory_metrics=len(metrics["memory"]),
            db_metrics=len(metrics["database"]),
            request_metrics=len(metrics["requests"])
        )
        
        return metrics
        
    except Exception as e:
        logger.error(
            "metrics_fetch_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise

@router.get("/metrics/prometheus", response_class=PlainTextResponse)
async def get_prometheus_metrics(db: Session = Depends(get_db)) -> str:
    """Get metrics in Prometheus format."""
    try:
        # Get raw metrics
        metrics = await get_metrics(db)
        
        # Convert to Prometheus format
        prometheus_output = format_prometheus_metrics(metrics)
        
        logger.info("prometheus_metrics_generated")
        return prometheus_output
        
    except Exception as e:
        logger.error(
            "prometheus_metrics_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise
