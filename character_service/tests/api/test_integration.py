"""Integration tests for character API."""
import pytest
from copy import deepcopy
from fastapi import status
from httpx import AsyncClient

from character_service.models.character import Character
from character_service.repositories.character import CharacterRepository


@pytest.mark.asyncio
@pytest.mark.integration
async def test_character_lifecycle(
    client: AsyncClient,
    valid_character_data: dict,
    test_repository: CharacterRepository
):
    """Test complete character lifecycle through the API."""
    # Create character
    create_response = await client.post("/characters", json=valid_character_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    data = create_response.json()
    char_id = data["id"]
    
    # Get created character
    get_response = await client.get(f"/characters/{char_id}")
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["id"] == char_id
    
    # List characters and verify presence
    list_response = await client.get("/characters")
    assert list_response.status_code == status.HTTP_200_OK
    characters = list_response.json()
    assert len(characters) == 1
    assert characters[0]["id"] == char_id
    
    # Update character
    update_data = {
        "name": "Updated Character",
        "current_hit_points": data["current_hit_points"] - 5,
        "temporary_hit_points": 3
    }
    update_response = await client.patch(f"/characters/{char_id}", json=update_data)
    assert update_response.status_code == status.HTTP_200_OK
    updated_data = update_response.json()
    assert updated_data["name"] == update_data["name"]
    assert updated_data["current_hit_points"] == update_data["current_hit_points"]
    assert updated_data["temporary_hit_points"] == update_data["temporary_hit_points"]
    
    # Verify database state directly
    character = await test_repository.get(char_id)
    assert character is not None
    assert character.name == update_data["name"]
    assert character.current_hit_points == update_data["current_hit_points"]
    assert character.temporary_hit_points == update_data["temporary_hit_points"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_character_validation(
    client: AsyncClient,
    valid_character_data: dict
):
    """Test character validation through API."""
    # Create character with invalid ability scores
    invalid_data = deepcopy(valid_character_data)
    invalid_data["ability_scores"]["strength"] = 0  # Invalid score
    
    response = await client.post("/characters", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Create valid character with original data
    create_response = await client.post("/characters", json=valid_character_data)
    assert create_response.status_code == status.HTTP_201_CREATED
    data = create_response.json()
    char_id = data["id"]
    
    # Try invalid hit points update
    invalid_update = {
        "current_hit_points": 999  # Higher than max_hit_points
    }
    update_response = await client.patch(f"/characters/{char_id}", json=invalid_update)
    assert update_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Verify character state remains unchanged
    get_response = await client.get(f"/characters/{char_id}")
    assert get_response.status_code == status.HTTP_200_OK
    unchanged_data = get_response.json()
    assert unchanged_data["current_hit_points"] == data["current_hit_points"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_character_not_found_handling(
    client: AsyncClient
):
    """Test API handling of non-existent characters."""
    fake_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # Try to get non-existent character
    get_response = await client.get(f"/characters/{fake_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    # Try to update non-existent character
    update_data = {"name": "New Name"}
    update_response = await client.patch(f"/characters/{fake_id}", json=update_data)
    assert update_response.status_code == status.HTTP_404_NOT_FOUND
