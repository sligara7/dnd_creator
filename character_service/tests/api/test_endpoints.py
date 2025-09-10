"""Tests for API endpoints."""
import uuid
from copy import deepcopy
from typing import Dict

import pytest
from fastapi import status
from httpx import AsyncClient

from character_service.models.character import Character
from character_service.repositories.character import CharacterRepository


@pytest.mark.asyncio
async def test_create_character_success(
    client: AsyncClient,
    valid_character_data: Dict
):
    """Test successful character creation."""
    response = await client.post("/characters", json=valid_character_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    
    # Check response data
    assert data["name"] == valid_character_data["name"]
    assert data["race"] == valid_character_data["race"]
    assert data["character_class"] == valid_character_data["character_class"]
    assert data["background"] == valid_character_data["background"]
    assert data["level"] == valid_character_data["level"]
    assert data["strength"] == valid_character_data["ability_scores"]["strength"]
    assert data["dexterity"] == valid_character_data["ability_scores"]["dexterity"]
    assert data["constitution"] == valid_character_data["ability_scores"]["constitution"]
    assert data["intelligence"] == valid_character_data["ability_scores"]["intelligence"]
    assert data["wisdom"] == valid_character_data["ability_scores"]["wisdom"]
    assert data["charisma"] == valid_character_data["ability_scores"]["charisma"]
    
    # Check derived fields
    assert "id" in data
    assert "max_hit_points" in data
    assert "current_hit_points" in data
    assert "temporary_hit_points" in data
    assert data["current_hit_points"] == data["max_hit_points"]


@pytest.mark.asyncio
async def test_create_character_validation_error(
    client: AsyncClient,
    valid_character_data: Dict
):
    """Test character creation with invalid data."""
    # Test with invalid ability scores
    invalid_data = deepcopy(valid_character_data)
    invalid_data["ability_scores"]["strength"] = 0  # Invalid score
    
    response = await client.post("/characters", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_get_character_success(
    client: AsyncClient,
    test_character: Character
):
    """Test successful character retrieval."""
    response = await client.get(f"/characters/{test_character.id}")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == str(test_character.id)
    assert data["name"] == test_character.name
    assert data["race"] == test_character.race
    assert data["character_class"] == test_character.character_class
    assert data["background"] == test_character.background
    assert data["level"] == test_character.level


@pytest.mark.asyncio
async def test_get_character_not_found(client: AsyncClient):
    """Test character retrieval with non-existent ID."""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/characters/{fake_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_list_characters_empty(
    client: AsyncClient,
    test_repository: CharacterRepository
):
    """Test character listing with empty database."""
    response = await client.get("/characters")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_characters_with_data(
    client: AsyncClient,
    test_character: Character
):
    """Test character listing with existing data."""
    response = await client.get("/characters")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(test_character.id)
    assert data[0]["name"] == test_character.name


@pytest.mark.asyncio
async def test_update_character_success(
    client: AsyncClient,
    test_character: Character
):
    """Test successful character update."""
    update_data = {
        "name": "Updated Name",
        "current_hit_points": 5,
        "temporary_hit_points": 3
    }
    
    response = await client.patch(
        f"/characters/{test_character.id}",
        json=update_data
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["current_hit_points"] == update_data["current_hit_points"]
    assert data["temporary_hit_points"] == update_data["temporary_hit_points"]


@pytest.mark.asyncio
async def test_update_character_not_found(
    client: AsyncClient
):
    """Test character update with non-existent ID."""
    fake_id = str(uuid.uuid4())
    update_data = {"name": "New Name"}
    
    response = await client.patch(f"/characters/{fake_id}", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_update_character_validation_error(
    client: AsyncClient,
    test_character: Character
):
    """Test character update with invalid data."""
    # Try to set current_hit_points higher than max_hit_points
    update_data = {
        "current_hit_points": 999  # Invalid value
    }
    
    response = await client.patch(
        f"/characters/{test_character.id}",
        json=update_data
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in response.json()
