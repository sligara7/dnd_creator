"""Test utilities for cache service tests."""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

def generate_test_key(prefix: Optional[str] = None) -> str:
    """Generate a unique test key.
    
    Args:
        prefix: Optional prefix for the key
        
    Returns:
        A unique key string
    """
    key = str(uuid4())
    return f"{prefix}:{key}" if prefix else key

def generate_test_value(size_bytes: int = 100) -> str:
    """Generate a test value of approximately the specified size.
    
    Args:
        size_bytes: Target size in bytes
        
    Returns:
        JSON string of specified size
    """
    # Create a base object
    data = {
        "id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": "x" * (size_bytes - 100)  # Approximate adjustment for metadata
    }
    return json.dumps(data)

def build_test_event(
    event_type: str,
    payload: Dict[str, Any],
    service: str = "test-service"
) -> Dict[str, Any]:
    """Build a test event object.
    
    Args:
        event_type: Type of event
        payload: Event payload
        service: Source service name
        
    Returns:
        Complete event object
    """
    return {
        "id": str(uuid4()),
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": service,
        "payload": payload
    }

async def wait_for_condition(
    condition_func,
    timeout: float = 5.0,
    check_interval: float = 0.1
) -> bool:
    """Wait for a condition to be true.
    
    Args:
        condition_func: Async function that returns bool
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds
        
    Returns:
        True if condition was met, False if timeout occurred
    """
    start_time = datetime.now()
    while (datetime.now() - start_time).total_seconds() < timeout:
        if await condition_func():
            return True
        await asyncio.sleep(check_interval)
    return False

def assert_json_equal(actual: str, expected: Dict[str, Any]):
    """Assert that a JSON string equals an expected dict.
    
    Args:
        actual: JSON string to test
        expected: Expected dictionary value
    """
    assert json.loads(actual) == expected

def simulate_redis_error():
    """Simulate a Redis connection error."""
    raise redis.ConnectionError("Simulated Redis connection error")

def simulate_message_hub_error():
    """Simulate a Message Hub connection error."""
    raise Exception("Simulated Message Hub connection error")

class AsyncContextManager:
    """Utility class for creating async context managers in tests."""
    
    def __init__(self, enter_result=None, exit_error=None):
        self.enter_result = enter_result
        self.exit_error = exit_error
        
    async def __aenter__(self):
        if isinstance(self.enter_result, Exception):
            raise self.enter_result
        return self.enter_result
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.exit_error:
            raise self.exit_error