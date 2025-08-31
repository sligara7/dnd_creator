"""Performance tests for critical character service operations."""

import asyncio
import pytest
import time
from fastapi.testclient import TestClient
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor

from character_service.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def base_character() -> Dict:
    """Basic character template for testing."""
    return {
        "name": "Test Character",
        "species": "Human",
        "background": "Soldier",
        "level": 1,
        "character_classes": {"Fighter": 1},
        "backstory": "A brave warrior seeking adventure."
    }


def test_character_creation_performance(client: TestClient, base_character: Dict):
    """Test character creation performance under load."""
    n_requests = 10  # Number of concurrent requests
    
    def create_character():
        start = time.time()
        resp = client.post("/api/v2/characters", json=base_character)
        duration = time.time() - start
        assert resp.status_code == 200
        return duration

    # Execute concurrent requests
    with ThreadPoolExecutor(max_workers=n_requests) as executor:
        durations = list(executor.map(lambda _: create_character(), range(n_requests)))

    # Analyze results
    avg_duration = sum(durations) / len(durations)
    max_duration = max(durations)
    assert avg_duration < 30.0  # SRD requirement: < 30 seconds
    assert max_duration < 35.0  # Allow slight variance for max


def test_antitheticon_generation_performance(client: TestClient):
    """Test Antitheticon generation performance."""
    start = time.time()
    
    # Create test party
    party = [
        {
            "id": "perf_char1",
            "name": "Performance Test 1",
            "class": "Fighter",
            "level": 5,
            "traits": ["Bold", "Strategic"],
            "methods": ["Melee combat", "Tactics"]
        },
        {
            "id": "perf_char2",
            "name": "Performance Test 2",
            "class": "Wizard",
            "level": 5,
            "traits": ["Intelligent", "Cautious"],
            "methods": ["Spellcasting", "Research"]
        }
    ]
    
    # Generate Antitheticon
    resp = client.post("/api/v2/antitheticon/analyze-party", json={
        "party": party,
        "campaign_notes": []
    })
    assert resp.status_code == 200
    party_profile = resp.json()
    
    resp = client.post("/api/v2/antitheticon/generate", json={
        "party_profile": party_profile,
        "dm_notes": {
            "theme": "Performance test theme",
            "desired_conflicts": ["Test conflict"]
        },
        "focus": "TACTICAL",
        "development": "CORRUPTED"
    })
    assert resp.status_code == 200
    
    duration = time.time() - start
    assert duration < 45.0  # Should complete in under 45 seconds


@pytest.mark.asyncio
async def test_concurrent_evolution_performance():
    """Test performance of concurrent character evolutions."""
    async with TestClient(app) as client:
        # Create test characters
        characters = []
        for i in range(5):
            resp = await client.post("/api/v2/characters", json={
                "name": f"Evolution Test {i}",
                "species": "Human",
                "level": 1,
                "character_classes": {"Fighter": 1}
            })
            assert resp.status_code == 200
            characters.append(resp.json()["id"])

        # Evolution requests
        async def evolve_character(char_id: str):
            start = time.time()
            resp = await client.post(f"/api/v2/evolution/{char_id}/apply", json={
                "evolution_type": "level_up",
                "choices": {
                    "class": "Fighter",
                    "features": ["Second Wind"]
                }
            })
            duration = time.time() - start
            assert resp.status_code == 200
            return duration

        # Execute concurrent evolutions
        durations = await asyncio.gather(
            *[evolve_character(char_id) for char_id in characters]
        )

        # Analyze results
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        assert avg_duration < 5.0  # SRD requirement: < 5 seconds
        assert max_duration < 7.0  # Allow slight variance for max


def test_inventory_operation_performance(client: TestClient):
    """Test inventory management performance."""
    # Create test character
    resp = client.post("/api/v2/characters", json={
        "name": "Inventory Test",
        "species": "Human",
        "level": 1,
        "character_classes": {"Fighter": 1}
    })
    assert resp.status_code == 200
    char_id = resp.json()["id"]

    # Add multiple items concurrently
    n_items = 20
    
    def add_item(i: int):
        start = time.time()
        resp = client.post(f"/api/v2/inventory", json={
            "character_id": char_id,
            "item_data": {
                "name": f"Test Item {i}",
                "type": "weapon" if i % 2 == 0 else "armor",
                "properties": {"damage": "1d6"} if i % 2 == 0 else {"ac": 12}
            },
            "quantity": 1
        })
        duration = time.time() - start
        assert resp.status_code == 200
        return duration

    with ThreadPoolExecutor(max_workers=n_items) as executor:
        durations = list(executor.map(lambda i: add_item(i), range(n_items)))

    avg_duration = sum(durations) / len(durations)
    max_duration = max(durations)
    assert avg_duration < 1.0  # SRD requirement: < 1 second for DB operations
    assert max_duration < 2.0  # Allow slight variance for max
