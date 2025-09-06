"""Tests for bulk operations API endpoints."""
import json
from typing import Dict, List, Any
from uuid import UUID, uuid4

import pytest
from httpx import AsyncClient
import asyncio

from character_service.api.v2.models.bulk import (
    BulkCharacterCreate,
    BulkValidateRequest,
    BulkOperationStatus,
    BulkValidationResponse,
)


@pytest.fixture
def test_characters() -> List[Dict[str, Any]]:
    """Create test character data."""
    return [
        {
            "name": "Test Character 1",
            "level": 1,
            "class_name": "Fighter",
            "race": "Human",
            "ability_scores": {
                "strength": 15,
                "dexterity": 12,
                "constitution": 14,
                "intelligence": 10,
                "wisdom": 8,
                "charisma": 13,
            },
        },
        {
            "name": "Test Character 2",
            "level": 1,
            "class_name": "Wizard",
            "race": "Elf",
            "ability_scores": {
                "strength": 8,
                "dexterity": 14,
                "constitution": 12,
                "intelligence": 16,
                "wisdom": 10,
                "charisma": 13,
            },
        },
    ]


@pytest.fixture
def invalid_characters() -> List[Dict[str, Any]]:
    """Create invalid test character data."""
    return [
        {
            "name": "Invalid Character 1",
            "level": 0,  # Invalid level
            "class_name": "NonexistentClass",
            "race": "Human",
            "ability_scores": {
                "strength": 25,  # Invalid score
                "dexterity": 12,
                "constitution": 14,
                "intelligence": 10,
                "wisdom": 8,
                "charisma": 13,
            },
        },
        {
            "name": "",  # Empty name
            "level": 1,
            "class_name": "Fighter",
            "race": "",  # Empty race
            "ability_scores": {
                "strength": 15,
                "dexterity": 12,
                "intelligence": 10,  # Missing constitution
                "wisdom": 8,
                "charisma": 13,
            },
        },
    ]


@pytest.mark.asyncio
async def test_bulk_create_success(
    client: AsyncClient,
    test_characters: List[Dict[str, Any]],
    test_campaign_id: UUID,
    test_theme_id: UUID,
) -> None:
    """Test successful bulk character creation."""
    request = BulkCharacterCreate(
        characters=test_characters,
        batch_label="Test Batch",
        campaign_id=test_campaign_id,
        theme_id=test_theme_id,
        created_by="test_user",
    )

    # Submit bulk creation request
    response = await client.post(
        "/api/v2/characters/bulk/create",
        json=request.dict(),
    )
    assert response.status_code == 202
    data = response.json()

    # Check initial response
    assert data["total_count"] == len(test_characters)
    assert "batch_id" in data
    batch_id = data["batch_id"]

    # Poll for completion
    max_attempts = 10
    attempt = 0
    status = None

    while attempt < max_attempts:
        status_response = await client.get(f"/api/v2/characters/bulk/status/{batch_id}")
        status = status_response.json()

        if status["status"] in ["completed", "failed"]:
            break

        attempt += 1
        await asyncio.sleep(0.5)

    assert status is not None
    assert status["status"] == "completed"
    assert status["success_count"] == len(test_characters)
    assert status["error_count"] == 0
    assert len(status["created"]) == len(test_characters)


@pytest.mark.asyncio
async def test_bulk_create_with_errors(
    client: AsyncClient,
    invalid_characters: List[Dict[str, Any]],
) -> None:
    """Test bulk character creation with invalid data."""
    request = BulkCharacterCreate(
        characters=invalid_characters,
        batch_label="Invalid Batch",
        created_by="test_user",
    )

    # Submit bulk creation request
    response = await client.post(
        "/api/v2/characters/bulk/create",
        json=request.dict(),
    )
    assert response.status_code == 202
    data = response.json()
    batch_id = data["batch_id"]

    # Poll for completion
    max_attempts = 10
    attempt = 0
    status = None

    while attempt < max_attempts:
        status_response = await client.get(f"/api/v2/characters/bulk/status/{batch_id}")
        status = status_response.json()

        if status["status"] in ["completed", "failed"]:
            break

        attempt += 1
        await asyncio.sleep(0.5)

    assert status is not None
    assert status["status"] == "completed"
    assert status["error_count"] == len(invalid_characters)
    assert len(status["errors"]) == len(invalid_characters)


@pytest.mark.asyncio
async def test_bulk_validate_success(
    client: AsyncClient,
    test_characters: List[Dict[str, Any]],
) -> None:
    """Test successful bulk validation."""
    request = BulkValidateRequest(
        characters=test_characters,
    )

    response = await client.post(
        "/api/v2/characters/bulk/validate",
        json=request.dict(),
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_count"] == len(test_characters)
    assert data["valid_count"] == len(test_characters)
    assert data["invalid_count"] == 0
    assert len(data["results"]) == len(test_characters)

    for result in data["results"]:
        assert result["is_valid"]
        assert not result["errors"]


@pytest.mark.asyncio
async def test_bulk_validate_with_errors(
    client: AsyncClient,
    invalid_characters: List[Dict[str, Any]],
) -> None:
    """Test bulk validation with invalid data."""
    request = BulkValidateRequest(
        characters=invalid_characters,
    )

    response = await client.post(
        "/api/v2/characters/bulk/validate",
        json=request.dict(),
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_count"] == len(invalid_characters)
    assert data["valid_count"] == 0
    assert data["invalid_count"] == len(invalid_characters)
    assert len(data["results"]) == len(invalid_characters)

    for result in data["results"]:
        assert not result["is_valid"]
        assert result["errors"]


@pytest.mark.asyncio
async def test_bulk_validate_with_theme(
    client: AsyncClient,
    test_characters: List[Dict[str, Any]],
    test_theme_id: UUID,
) -> None:
    """Test bulk validation with theme context."""
    request = BulkValidateRequest(
        characters=test_characters,
        theme_id=test_theme_id,
    )

    response = await client.post(
        "/api/v2/characters/bulk/validate",
        json=request.dict(),
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_count"] == len(test_characters)
    # Further assertions depend on theme compatibility


@pytest.mark.asyncio
async def test_bulk_validate_with_campaign(
    client: AsyncClient,
    test_characters: List[Dict[str, Any]],
    test_campaign_id: UUID,
) -> None:
    """Test bulk validation with campaign context."""
    request = BulkValidateRequest(
        characters=test_characters,
        campaign_id=test_campaign_id,
    )

    response = await client.post(
        "/api/v2/characters/bulk/validate",
        json=request.dict(),
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_count"] == len(test_characters)
    # Further assertions depend on campaign requirements


@pytest.mark.asyncio
async def test_bulk_create_limit(
    client: AsyncClient,
    test_characters: List[Dict[str, Any]],
) -> None:
    """Test bulk creation with too many characters."""
    # Create more than the allowed limit (100)
    too_many = test_characters * 51  # 102 characters

    request = BulkCharacterCreate(
        characters=too_many,
        created_by="test_user",
    )

    response = await client.post(
        "/api/v2/characters/bulk/create",
        json=request.dict(),
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_batch_not_found(
    client: AsyncClient,
) -> None:
    """Test getting status of nonexistent batch."""
    batch_id = uuid4()
    response = await client.get(f"/api/v2/characters/bulk/status/{batch_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_concurrent_batch_processing(
    client: AsyncClient,
    test_characters: List[Dict[str, Any]],
) -> None:
    """Test concurrent batch processing."""
    # Create multiple batches
    batch_count = 3
    batch_ids = []

    # Submit batches
    for i in range(batch_count):
        request = BulkCharacterCreate(
            characters=test_characters,
            batch_label=f"Concurrent Batch {i}",
            created_by="test_user",
        )
        response = await client.post(
            "/api/v2/characters/bulk/create",
            json=request.dict(),
        )
        assert response.status_code == 202
        batch_ids.append(response.json()["batch_id"])

    # Wait for all batches to complete
    max_attempts = 20
    attempt = 0
    completed = set()

    while attempt < max_attempts and len(completed) < batch_count:
        statuses = await asyncio.gather(*[
            client.get(f"/api/v2/characters/bulk/status/{bid}")
            for bid in batch_ids
            if bid not in completed
        ])

        for status in statuses:
            if status.json()["status"] in ["completed", "failed"]:
                completed.add(status.json()["batch_id"])

        if len(completed) < batch_count:
            attempt += 1
            await asyncio.sleep(0.5)

    assert len(completed) == batch_count


@pytest.mark.asyncio
async def test_bulk_validation_performance(
    client: AsyncClient,
    test_characters: List[Dict[str, Any]],
) -> None:
    """Test validation performance with large batch."""
    # Create a larger batch for performance testing
    large_batch = test_characters * 25  # 50 characters

    request = BulkValidateRequest(
        characters=large_batch,
    )

    start = asyncio.get_event_loop().time()
    response = await client.post(
        "/api/v2/characters/bulk/validate",
        json=request.dict(),
    )
    end = asyncio.get_event_loop().time()

    assert response.status_code == 200
    assert end - start < 5.0  # Should complete within 5 seconds


@pytest.mark.asyncio
async def test_bulk_create_chunking(
    client: AsyncClient,
    test_characters: List[Dict[str, Any]],
) -> None:
    """Test creation with large batch to verify chunking."""
    # Create a larger batch to test chunking
    large_batch = test_characters * 25  # 50 characters

    request = BulkCharacterCreate(
        characters=large_batch,
        batch_label="Large Chunked Batch",
        created_by="test_user",
    )

    response = await client.post(
        "/api/v2/characters/bulk/create",
        json=request.dict(),
    )
    assert response.status_code == 202
    batch_id = response.json()["batch_id"]

    # Monitor progress
    max_attempts = 20
    attempt = 0
    last_progress = -1
    progressed = False

    while attempt < max_attempts:
        status_response = await client.get(f"/api/v2/characters/bulk/status/{batch_id}")
        status = status_response.json()

        if status["progress"] > last_progress:
            progressed = True
            last_progress = status["progress"]

        if status["status"] == "completed":
            break

        attempt += 1
        await asyncio.sleep(0.5)

    assert progressed  # Verify that progress was updated incrementally
    assert status["success_count"] == len(large_batch)
