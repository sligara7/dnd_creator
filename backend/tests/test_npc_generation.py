import unittest
from unittest.mock import MagicMock, patch
import pytest
import json

from backend.core.npc.npc import NPC
from backend.core.creature.creature import Creature

class TestNPCGeneration(unittest.TestCase):
    """Test NPC generation functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock the LLM advisors
        self.llm_patcher = patch('backend.core.npc.llm_npc_advisor.LLMNPCAdvisor')
        self.mock_llm = self.llm_patcher.start()
        
        # Setup mock responses
        self.mock_llm.return_value.generate_quick_npc.return_value = {
            "name": "Gundren Rockseeker",
            "role": "merchant",
            "description": "A stout dwarf merchant with a long beard",
            "personality": "Gruff but fair, always looking for a good deal"
        }
        
        self.npc = NPC()
    
    def tearDown(self):
        """Clean up after test"""
        self.llm_patcher.stop()
    
    def test_quick_npc_generation(self):
        """Test generating a quick NPC"""
        npc_data = self.npc.generate_quick_npc(role="merchant", importance_level="minor")
        
        # Verify basic NPC data
        self.assertEqual(npc_data["name"], "Gundren Rockseeker")
        self.assertEqual(npc_data["role"], "merchant")
        
        # Verify the LLM advisor was called correctly
        self.mock_llm.return_value.generate_quick_npc.assert_called_with("merchant", "minor")
    
    def test_npc_validation(self):
        """Test NPC validation"""
        # Valid NPC
        valid_npc = {
            "name": "Test NPC",
            "role": "guard",
            "ability_scores": {
                "strength": 14,
                "dexterity": 12,
                "constitution": 13,
                "intelligence": 10,
                "wisdom": 11,
                "charisma": 9
            }
        }
        
        result = self.npc.validate_npc(valid_npc)
        self.assertTrue(result["valid"])
        
        # Invalid NPC (missing name)
        invalid_npc = {
            "role": "guard"
        }
        
        result = self.npc.validate_npc(invalid_npc)
        self.assertFalse(result["valid"])
        self.assertTrue(any("name" in err for err in result["errors"]))


@pytest.fixture
def mock_creature_llm():
    """Fixture for mocking creature LLM advisor"""
    with patch('backend.core.creature.llm_creature_advisor.LLMCreatureAdvisor') as mock:
        # Setup mock response
        mock.return_value.generate_creature.return_value = {
            "name": "Forest Wolf",
            "type": "beast",
            "challenge_rating": 1,
            "size": "medium",
            "hit_points": 24,
            "armor_class": 13,
            "abilities": [
                {"name": "Pack Tactics", "description": "The wolf has advantage on attack rolls..."}
            ]
        }
        yield mock

def test_creature_generation(mock_creature_llm):
    """Test generating a creature"""
    creature = Creature()
    
    # Generate a creature
    wolf = creature.generate_creature(
        name="Forest Wolf",
        type="beast",
        challenge_rating=1
    )
    
    # Verify creature data
    assert wolf["name"] == "Forest Wolf"
    assert wolf["type"] == "beast"
    assert wolf["challenge_rating"] == 1
    assert wolf["hit_points"] == 24
    assert len(wolf["abilities"]) == 1
    
    # Verify LLM advisor was called
    mock_creature_llm.return_value.generate_creature.assert_called_once()

def test_mass_creature_generation(mock_creature_llm):
    """Test generating a group of related creatures"""
    with patch('backend.core.creature.llm_mass_creature_advisor.LLMMassCreatureAdvisor') as mock_mass:
        mock_mass.return_value.generate_creature_group.return_value = [
            {"name": "Wolf Alpha", "hit_points": 32},
            {"name": "Wolf 1", "hit_points": 24},
            {"name": "Wolf 2", "hit_points": 24}
        ]
        
        creature = Creature()
        
        # Generate a group of creatures
        wolf_pack = creature.generate_creature_group(
            base_creature="wolf",
            count=3,
            variation="pack hierarchy"
        )
        
        # Verify group generation
        assert len(wolf_pack) == 3
        assert wolf_pack[0]["name"] == "Wolf Alpha"
        assert wolf_pack[0]["hit_points"] > wolf_pack[1]["hit_points"]
        
        # Verify mass advisor was called
        mock_mass.return_value.generate_creature_group.assert_called_once()