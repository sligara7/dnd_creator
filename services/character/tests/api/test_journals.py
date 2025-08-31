"""Journal API Tests"""

import pytest
from fastapi.testclient import TestClient

def test_list_journal_entries(client: TestClient, test_character, test_journal_entry):
    """Test listing journal entries."""
    response = client.get(f"/api/v2/journals?character_id={test_character.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["title"] == test_journal_entry.title

def test_get_journal_entry(client: TestClient, test_character, test_journal_entry):
    """Test getting a specific journal entry."""
    response = client.get(
        f"/api/v2/journals/{test_journal_entry.id}?character_id={test_character.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_journal_entry.title
    assert data["content"] == test_journal_entry.content
    assert data["character_id"] == test_character.id

def test_create_journal_entry(client: TestClient, test_character):
    """Test journal entry creation."""
    entry_data = {
        "character_id": test_character.id,
        "title": "New Journal Entry",
        "content": "This is a test journal entry.",
        "entry_type": "session"
    }
    response = client.post("/api/v2/journals", json=entry_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Journal Entry"
    assert data["content"] == "This is a test journal entry."
    assert data["character_id"] == test_character.id

def test_direct_edit_journal_entry(client: TestClient, test_character, test_journal_entry):
    """Test direct journal entry edit."""
    edit_data = {
        "updates": {
            "title": "Edited Journal Entry",
            "content": "Updated content for testing",
            "entry_type": "milestone"
        },
        "notes": "Testing journal entry direct edit"
    }
    response = client.post(
        f"/api/v2/journals/{test_journal_entry.id}/direct-edit?character_id={test_character.id}"
        json=edit_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Edited Journal Entry"
    assert data["content"] == "Updated content for testing"
    assert data["entry_type"] == "milestone"
    assert data["user_modified"] is True

def test_list_journal_entries_invalid_character(client: TestClient):
    """Test listing journal entries for invalid character."""
    response = client.get("/api/v2/journals?character_id=999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"

def test_create_journal_entry_invalid_character(client: TestClient):
    """Test creating journal entry for invalid character."""
    entry_data = {
        "character_id": 999999,
        "title": "Invalid Entry",
        "content": "This should fail",
        "entry_type": "session"
    }
    response = client.post("/api/v2/journals", json=entry_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Character not found"
