"""Performance tests for bulk operations and high load scenarios."""

import asyncio
import pytest
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from typing import Dict, List

from character_service.main import app
from character_service.core.metrics import get_metrics

# Test utilities
@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture
def bulk_characters() -> List[Dict]:
    """Generate a list of characters for bulk testing."""
    return [
        {
            "name": f"Bulk Test {i}",
            "species": "Human" if i % 2 == 0 else "Elf",
            "background": "Soldier" if i % 3 == 0 else "Scholar",
            "level": 1,
            "character_classes": {"Fighter": 1} if i % 2 == 0 else {"Wizard": 1},
            "backstory": f"Test character {i} for bulk operations."
        }
        for i in range(50)  # 50 test characters
    ]

# Bulk Operation Tests
def test_bulk_character_creation(client: TestClient, bulk_characters: List[Dict]):
    """Test performance of bulk character creation."""
    start = time.time()
    
    # Test bulk endpoint
    resp = client.post("/api/v2/characters/bulk/create", json={
        "characters": bulk_characters,
        "validation_level": "FULL"
    })
    assert resp.status_code == 200
    results = resp.json()

    # Verify results
    creation_time = time.time() - start
    success_count = len([r for r in results["results"] if r["success"]])
    error_count = len(results["results"]) - success_count

    print(f"\nBulk Creation Stats:")
    print(f"Total time: {creation_time:.2f}s")
    print(f"Characters created: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Average time per character: {(creation_time/len(bulk_characters)):.2f}s")

    # Performance assertions
    assert creation_time < len(bulk_characters) * 2  # Less than 2s per character
    assert success_count > len(bulk_characters) * 0.95  # 95% success rate minimum

def test_concurrent_validations(client: TestClient, bulk_characters: List[Dict]):
    """Test concurrent validation requests."""
    n_concurrent = 10  # Number of concurrent validation requests
    chars_per_request = 5  # Characters per validation request
    
    def validate_batch(batch: List[Dict]) -> Dict:
        start = time.time()
        resp = client.post("/api/v2/characters/bulk/validate", json={
            "characters": batch,
            "validation_level": "FULL"
        })
        duration = time.time() - start
        assert resp.status_code == 200
        return {"duration": duration, "results": resp.json()}

    # Split characters into batches
    batches = [
        bulk_characters[i:i + chars_per_request]
        for i in range(0, len(bulk_characters), chars_per_request)
    ][:n_concurrent]

    # Run concurrent validations
    with ThreadPoolExecutor(max_workers=n_concurrent) as executor:
        results = list(executor.map(validate_batch, batches))

    # Analyze results
    durations = [r["duration"] for r in results]
    avg_duration = sum(durations) / len(durations)
    max_duration = max(durations)

    print(f"\nConcurrent Validation Stats:")
    print(f"Average batch duration: {avg_duration:.2f}s")
    print(f"Max batch duration: {max_duration:.2f}s")
    print(f"Total concurrent batches: {len(batches)}")

    # Performance assertions
    assert avg_duration < 5.0  # Average validation under 5s
    assert max_duration < 10.0  # Max validation under 10s

@pytest.mark.asyncio
async def test_high_load_requests():
    """Test service behavior under high load."""
    async with TestClient(app) as client:
        n_requests = 100  # Total number of requests
        concurrent_limit = 20  # Max concurrent requests
        request_types = ["create", "validate", "sheet", "inventory"]
        results = defaultdict(list)

        # Test request generators
        async def create_request():
            start = time.time()
            resp = await client.post("/api/v2/characters", json={
                "name": "Load Test",
                "species": "Human",
                "level": 1,
                "character_classes": {"Fighter": 1}
            })
            duration = time.time() - start
            return "create", resp.status_code, duration

        async def validate_request():
            start = time.time()
            resp = await client.post("/api/v2/characters/bulk/validate", json={
                "characters": [{
                    "name": "Validation Test",
                    "species": "Human",
                    "level": 1,
                    "character_classes": {"Fighter": 1}
                }]
            })
            duration = time.time() - start
            return "validate", resp.status_code, duration

        async def sheet_request(char_id: str):
            start = time.time()
            resp = await client.get(f"/api/v2/characters/{char_id}/sheet")
            duration = time.time() - start
            return "sheet", resp.status_code, duration

        async def inventory_request(char_id: str):
            start = time.time()
            resp = await client.get(f"/api/v2/characters/{char_id}/inventory")
            duration = time.time() - start
            return "inventory", resp.status_code, duration

        # Create a test character first
        resp = await client.post("/api/v2/characters", json={
            "name": "Load Test Character",
            "species": "Human",
            "level": 1,
            "character_classes": {"Fighter": 1}
        })
        assert resp.status_code == 200
        test_char_id = resp.json()["id"]

        # Generate mixed request workload
        request_funcs = [
            create_request,
            validate_request,
            lambda: sheet_request(test_char_id),
            lambda: inventory_request(test_char_id)
        ]

        async def execute_request():
            func = request_funcs[len(results["requests"]) % len(request_funcs)]
            return await func()

        # Execute requests with concurrency limit
        tasks = [execute_request() for _ in range(n_requests)]
        completed = await asyncio.gather(*tasks)

        # Analyze results by request type
        for req_type, status, duration in completed:
            results[req_type].append((status, duration))

        # Print statistics
        print("\nHigh Load Test Results:")
        for req_type, measurements in results.items():
            statuses = [s for s, _ in measurements]
            durations = [d for _, d in measurements]
            success_rate = (statuses.count(200) / len(statuses)) * 100
            avg_duration = sum(durations) / len(durations)
            print(f"\n{req_type.title()} Requests:")
            print(f"Success Rate: {success_rate:.1f}%")
            print(f"Average Duration: {avg_duration:.2f}s")
            print(f"Max Duration: {max(durations):.2f}s")

        # Check metrics
        metrics = get_metrics()
        print("\nService Metrics:")
        print(f"Total Requests: {metrics.total_requests}")
        print(f"Error Rate: {metrics.error_rate:.2f}%")
        print(f"Average Response Time: {metrics.avg_response_time:.2f}s")
        print(f"Resource Utilization: {metrics.resource_utilization:.1f}%")

        # Performance assertions
        assert all(status == 200 for status, _ in completed), "All requests should succeed"
        assert all(duration < 10.0 for _, duration in completed), "Individual requests should complete under 10s"
        assert metrics.error_rate < 5.0, "Error rate should be under 5%"
        assert metrics.resource_utilization < 80.0, "Resource utilization should be under 80%"

def test_resource_management(client: TestClient, bulk_characters: List[Dict]):
    """Test resource management under load."""
    start_metrics = get_metrics()
    
    # Create multiple characters with resources
    chars_created = []
    for char in bulk_characters[:10]:  # Create 10 characters
        resp = client.post("/api/v2/characters", json=char)
        assert resp.status_code == 200
        chars_created.append(resp.json()["id"])

    # Simulate resource-intensive operations
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Generate concurrent resource updates
        def update_resources(char_id: str):
            # Update spell slots
            client.put(f"/api/v2/characters/{char_id}/resources", json={
                "spell_slots_used": {
                    "1": 2,
                    "2": 1
                }
            })
            # Update hit points
            client.put(f"/api/v2/characters/{char_id}/combat-state", json={
                "hp_delta": -5,
                "temp_hp": 10
            })
            # Add conditions
            client.put(f"/api/v2/characters/{char_id}/combat-state", json={
                "add_conditions": ["poisoned", "frightened"]
            })

        # Execute updates
        list(executor.map(update_resources, chars_created))

    # Get final metrics
    end_metrics = get_metrics()
    
    # Calculate resource utilization
    duration = time.time() - start_metrics.timestamp
    memory_delta = end_metrics.memory_usage - start_metrics.memory_usage
    cpu_delta = end_metrics.cpu_usage - start_metrics.cpu_usage

    print("\nResource Management Test Results:")
    print(f"Duration: {duration:.2f}s")
    print(f"Memory Usage Delta: {memory_delta:.1f}MB")
    print(f"CPU Usage Delta: {cpu_delta:.1f}%")
    print(f"Final Error Rate: {end_metrics.error_rate:.2f}%")

    # Performance assertions
    assert duration < 30.0, "Resource updates should complete in reasonable time"
    assert memory_delta < 100.0, "Memory usage should remain reasonable"
    assert cpu_delta < 50.0, "CPU usage should remain under 50%"
    assert end_metrics.error_rate < 5.0, "Error rate should stay low"
