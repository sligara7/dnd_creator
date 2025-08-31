"""Journal API Tests"""

from datetime import datetime
from fastapi.testclient import TestClient
from tests.api.test_characters import create_test_character

def create_test_journal_entry(client: TestClient, character_id: int, title: str = "Test Entry") -> dict:
    """Helper to create a test journal entry via HTTP."""
    entry_data = {
        "character_id": character_id,
        "title": title,
        "content": "Test content for journal entry",
        "entry_type": "session"
    }
    response = client.post("/api/v2/journals", json=entry_data)
    assert response.status_code == 200
    return response.json()

def test_list_journal_entries(client: TestClient):
    """Test listing journal entries."""
    # Create test character and journal entry
    character = create_test_character(client)
    entry = create_test_journal_entry(client, character["id"])
    
    # Test listing
    response = client.get(f"/api/v2/journals?character_id={character['id']}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(e["id"] == entry["id"] for e in data)

def test_get_journal_entry(client: TestClient):
    """Test getting a specific journal entry."""
    # Create test character and journal entry
    character = create_test_character(client)
    entry = create_test_journal_entry(client, character["id"])
    
    # Test retrieval
    response = client.get(f"/api/v2/journals/{entry['id']}?character_id={character['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == entry["title"]

def test_create_journal_entry(client: TestClient):
    """Test journal entry creation."""
    character = create_test_character(client)
    entry = create_test_journal_entry(client, character["id"], title="New Journal Entry")
    assert entry["title"] == "New Journal Entry"
    assert entry["character_id"] == character["id"]

def test_direct_edit_journal_entry(client: TestClient):
    """Test direct journal entry edit."""
    # Create test character and journal entry
    character = create_test_character(client)
    entry = create_test_journal_entry(client, character["id"])
    
    # Test direct edit
    edit_data = {
        "updates": {
            "title": "Edited Journal Entry",
            "content": "Updated content for testing",
            "entry_type": "milestone"
        },
        "notes": "Testing journal entry direct edit"
    }
    response = client.post(
        f"/api/v2/journals/{entry['id']}/direct-edit?character_id={character['id']}",
        json=edit_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Edited Journal Entry"
    assert data["entry_type"] == "milestone"

def test_list_journal_entries_invalid_character(client: TestClient):
    """Test listing journal entries for invalid character."""
    response = client.get("/api/v2/journals?character_id=999999")
    assert response.status_code == 404

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
