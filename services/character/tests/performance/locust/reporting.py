"""Performance reporting module."""
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class EndpointThreshold:
    """Performance threshold configuration for an endpoint."""
    name: str
    max_latency_ms: int
    max_error_rate: float = 0.01  # 1% error rate threshold
    min_rps: float = 1.0  # Minimum requests per second

@dataclass
class PerformanceReport:
    """Performance test results."""
    timestamp: str
    duration: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_latency: float
    percentile_95: float
    percentile_99: float
    requests_per_second: float
    endpoint_results: Dict[str, Dict[str, Any]]
    thresholds_met: bool
    issues: List[str]

# SRD Performance Thresholds
SRD_THRESHOLDS = {
    "/health": EndpointThreshold(
        name="Health Check",
        max_latency_ms=100,
        min_rps=10.0,  # Higher RPS requirement for health checks
    ),
    "/api/v2/characters/{id}": EndpointThreshold(
        name="Character Sheet",
        max_latency_ms=100,
    ),
    "/api/v2/characters/bulk/*": EndpointThreshold(
        name="Bulk Operations",
        max_latency_ms=2000,
    ),
    "/api/v2/themes/transition/*": EndpointThreshold(
        name="Theme Transitions",
        max_latency_ms=500,
    ),
}

def create_performance_report(stats_history: List[Dict[str, Any]]) -> PerformanceReport:
    """Create a performance report from Locust statistics history."""
    # Initialize report data
    total_reqs = 0
    successful_reqs = 0
    failed_reqs = 0
    endpoint_results = {}
    issues = []
    all_thresholds_met = True

    # Process each stats entry
    for entry in stats_history:
        endpoint = entry.get("name", "")
        if not endpoint:
            continue

        # Accumulate totals
        total_reqs += entry.get("num_requests", 0)
        successful_reqs += entry.get("num_successes", 0)
        failed_reqs += entry.get("num_failures", 0)

        # Calculate endpoint metrics
        latency_avg = entry.get("avg_response_time", 0)
        latency_95 = entry.get("response_time_percentile_95", 0)
        latency_99 = entry.get("response_time_percentile_99", 0)
        rps = entry.get("current_rps", 0)
        error_rate = failed_reqs / total_reqs if total_reqs > 0 else 0

        # Store endpoint results
        endpoint_results[endpoint] = {
            "total_requests": total_reqs,
            "successful_requests": successful_reqs,
            "failed_requests": failed_reqs,
            "average_latency": latency_avg,
            "percentile_95": latency_95,
            "percentile_99": latency_99,
            "requests_per_second": rps,
            "error_rate": error_rate,
        }

        # Check against thresholds
        threshold = None
        for pattern, t in SRD_THRESHOLDS.items():
            if pattern.replace("{id}", "[^/]+") in endpoint:
                threshold = t
                break

        if threshold:
            if latency_95 > threshold.max_latency_ms:
                issues.append(
                    f"{threshold.name}: 95th percentile latency {latency_95:.1f}ms "
                    f"exceeds threshold {threshold.max_latency_ms}ms"
                )
                all_thresholds_met = False
            
            if error_rate > threshold.max_error_rate:
                issues.append(
                    f"{threshold.name}: Error rate {error_rate:.1%} "
                    f"exceeds threshold {threshold.max_error_rate:.1%}"
                )
                all_thresholds_met = False

            if rps < threshold.min_rps:
                issues.append(
                    f"{threshold.name}: Requests/sec {rps:.1f} "
                    f"below minimum {threshold.min_rps:.1f}"
                )
                all_thresholds_met = False

    # Create final report
    return PerformanceReport(
        timestamp=datetime.utcnow().isoformat(),
        duration=sum(s.get("last_request_timestamp", 0) - s.get("start_time", 0)
                    for s in stats_history if s.get("start_time")),
        total_requests=total_reqs,
        successful_requests=successful_reqs,
        failed_requests=failed_reqs,
        average_latency=sum(r["average_latency"] for r in endpoint_results.values()) / len(endpoint_results),
        percentile_95=max(r["percentile_95"] for r in endpoint_results.values()),
        percentile_99=max(r["percentile_99"] for r in endpoint_results.values()),
        requests_per_second=sum(r["requests_per_second"] for r in endpoint_results.values()),
        endpoint_results=endpoint_results,
        thresholds_met=all_thresholds_met,
        issues=issues,
    )

def save_performance_report(report: PerformanceReport, output_dir: str = "reports/locust") -> None:
    """Save performance report to file."""
    os.makedirs(output_dir, exist_ok=True)
    
    report_path = os.path.join(
        output_dir,
        f"performance_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    with open(report_path, 'w') as f:
        # Convert dataclass to dict
        report_dict = {
            k: v for k, v in report.__dict__.items()
            if not k.startswith('_')
        }
        json.dump(report_dict, f, indent=2)

    # Create summary file for quick reference
    summary_path = os.path.join(output_dir, "latest_summary.txt")
    with open(summary_path, 'w') as f:
        f.write(f"Performance Test Summary\n")
        f.write(f"========================\n")
        f.write(f"Timestamp: {report.timestamp}\n")
        f.write(f"Duration: {report.duration} seconds\n")
        f.write(f"Total Requests: {report.total_requests}\n")
        f.write(f"Success Rate: {(report.successful_requests/report.total_requests)*100:.1f}%\n")
        f.write(f"Average Latency: {report.average_latency:.1f}ms\n")
        f.write(f"95th Percentile: {report.percentile_95:.1f}ms\n")
        f.write(f"Requests/Second: {report.requests_per_second:.1f}\n")
        f.write(f"\nSRD Thresholds Met: {'Yes' if report.thresholds_met else 'No'}\n")
        if report.issues:
            f.write(f"\nIssues Found:\n")
            for issue in report.issues:
                f.write(f"- {issue}\n")
