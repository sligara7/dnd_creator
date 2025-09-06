#!/usr/bin/env python
"""Performance test runner script."""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def run_locust(
    host: str,
    users: int,
    spawn_rate: int,
    runtime: str,
    tags: list[str] = None,
    html_report: bool = True,
) -> int:
    """Run Locust performance tests."""
    print(f"Starting Locust with {users} users, spawn rate {spawn_rate}/s")

    # Prepare Locust command
    cmd = [
        "locust",
        "-f", "tests/performance/locustfile.py",
        "--host", host,
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", runtime,
        "--headless",  # Run without web UI
        "--print-stats",  # Print stats to console
        "--only-summary",  # Only print summary stats
    ]

    # Add tags if specified
    if tags:
        cmd.extend(["--tags", ",".join(tags)])

    # Add HTML report if requested
    if html_report:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        report_dir = "tests/performance/reports"
        Path(report_dir).mkdir(parents=True, exist_ok=True)
        cmd.extend([
            "--html", f"{report_dir}/report_{timestamp}.html"
        ])

    try:
        # Run Locust
        result = subprocess.run(cmd, check=True)
        return result.returncode

    except subprocess.CalledProcessError as e:
        print(f"Locust failed with exit code {e.returncode}")
        return e.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run performance tests")
    parser.add_argument(
        "--host",
        default="http://localhost:8100",
        help="Host to test against",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=10,
        help="Number of concurrent users",
    )
    parser.add_argument(
        "--spawn-rate",
        type=int,
        default=1,
        help="User spawn rate per second",
    )
    parser.add_argument(
        "--runtime",
        default="5m",
        help="Test runtime (e.g., 1h30m)",
    )
    parser.add_argument(
        "--tags",
        nargs="+",
        help="Only run tests with these tags",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Don't generate HTML report",
    )

    args = parser.parse_args()

    try:
        # Run Locust
        result = run_locust(
            host=args.host,
            users=args.users,
            spawn_rate=args.spawn_rate,
            runtime=args.runtime,
            tags=args.tags,
            html_report=not args.no_html,
        )

        sys.exit(result)

    except KeyboardInterrupt:
        print("\nStopped by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
