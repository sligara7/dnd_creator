"""Integration tests for Antitheticon system flows."""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, List

from character_service.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def test_party() -> List[Dict]:
    """Sample party for testing."""
    return [
        {
            "id": "test_char1",
            "name": "Aethon Test",
            "class": "Paladin",
            "alignment": "Lawful Good",
            "traits": ["Honorable", "Protective", "Just"],
            "methods": ["Direct confrontation", "Holy magic", "Leadership"],
            "beliefs": ["Light conquers darkness", "Protect the innocent"]
        },
        {
            "id": "test_char2",
            "name": "Sylvana Test",
            "class": "Druid",
            "alignment": "Neutral Good",
            "traits": ["Wise", "Patient", "Nurturing"],
            "methods": ["Natural magic", "Healing", "Transformation"],
            "beliefs": ["Balance in all things", "Preserve life"]
        }
    ]


@pytest.fixture
def dm_notes() -> Dict:
    """Sample DM notes for testing."""
    return {
        "theme": "Corruption of justice",
        "desired_conflicts": ["Moral gray areas", "Ends vs means"],
        "specific_oppositions": {
            "test_char1": "Former paladin who chose power over justice",
            "test_char2": "Nature corrupter who believes in survival of fittest"
        }
    }


def test_antitheticon_creation_flow(client: TestClient, test_party: List[Dict], dm_notes: Dict):
    """Test complete Antitheticon creation flow."""
    
    # Test party analysis
    resp = client.post("/api/v2/antitheticon/analyze-party", json={
        "party": test_party,
        "campaign_notes": [{
            "entry": "Party has been protecting villages",
            "outcome": "Successfully defended three settlements",
            "party_methods": "Open confrontation, moral leadership",
            "impact": "Growing reputation as defenders of justice"
        }]
    })
    assert resp.status_code == 200
    party_profile = resp.json()
    assert "members" in party_profile
    assert "shared_beliefs" in party_profile
    assert len(party_profile["members"]) == 2

    # Test Antitheticon generation
    resp = client.post("/api/v2/antitheticon/generate", json={
        "party_profile": party_profile,
        "dm_notes": dm_notes,
        "focus": "MORAL",
        "development": "CORRUPTED"
    })
    assert resp.status_code == 200
    antitheticon = resp.json()
    assert "leader" in antitheticon
    assert "core_members" in antitheticon
    assert len(antitheticon["core_members"]) > 0

    # Test evolution after party changes
    resp = client.post(f"/api/v2/antitheticon/{antitheticon['leader']['character_id']}/evolve", json={
        "party_changes": [{
            "character_id": "test_char1",
            "type": "level_up",
            "new_abilities": ["Divine intervention", "Greater smite"],
            "character_growth": "Growing into inspiring leader"
        }],
        "dm_notes": dm_notes,
        "events": [{
            "event": "Failed to corrupt a town",
            "reaction": "Growing desperate"
        }]
    })
    assert resp.status_code == 200
    evolved = resp.json()
    assert "leader" in evolved
    assert "tactical_changes" in evolved
    assert "new_abilities" in evolved["leader"]

    # Test encounter generation
    resp = client.post(f"/api/v2/antitheticon/{antitheticon['leader']['character_id']}/encounters", json={
        "location_type": "corrupted_church",
        "environment": {
            "type": "Defiled temple",
            "features": ["Corrupted altar", "Dark mists"]
        }
    })
    assert resp.status_code == 200
    encounter = resp.json()
    assert "setup" in encounter
    assert "phases" in encounter
    assert len(encounter["phases"]) > 0

    # Test relationship evolution
    resp = client.post(f"/api/v2/antitheticon/{antitheticon['leader']['character_id']}/relationships/test_char1", json={
        "events": [{
            "type": "confrontation",
            "outcome": "Revealed shared past"
        }]
    })
    assert resp.status_code == 200
    relationship = resp.json()
    assert "relationship_stage" in relationship
    assert "new_elements" in relationship
    assert "evolution" in relationship
