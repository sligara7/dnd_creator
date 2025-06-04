import unittest
from unittest.mock import MagicMock, patch
import json
import os
import sys
import pytest

# Import the core modules
from backend.core.character.character import Character
from backend.core.ability_scores.ability_scores import AbilityScores
from backend.core.species.species import Species
from backend.core.classes.classes import Classes
from backend.core.skills.skills import Skills
from backend.core.personality_and_backstory.abstract_personality import AbstractPersonality
from backend.core.services.ollama_service import OllamaService

class TestCharacterCreation(unittest.TestCase):
    """Test suite for character creation functionality"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Mock the OllamaService to avoid actual API calls during tests
        self.ollama_patcher = patch('backend.core.services.ollama_service.OllamaService')
        self.mock_ollama = self.ollama_patcher.start()
        
        # Create instances of core components with mocked dependencies
        self.ability_scores = AbilityScores()
        self.species = Species()
        self.character = Character()
        
    def tearDown(self):
        """Clean up after each test"""
        self.ollama_patcher.stop()
    
    def test_character_basic_creation(self):
        """Test creating a basic character with minimal information"""
        character_data = {
            "name": "Test Character",
            "level": 1,
            "species": "human",
            "class": "fighter"
        }
        
        # Create a character
        character_id = self.character.create_character(character_data)
        
        # Verify the character was created with correct basic attributes
        created_character = self.character.get_character(character_id)
        self.assertEqual(created_character["name"], "Test Character")
        self.assertEqual(created_character["level"], 1)
        self.assertEqual(created_character["species"], "human")
        self.assertEqual(created_character["class"], "fighter")
    
    def test_ability_score_generation(self):
        """Test generating ability scores"""
        # Test standard array
        scores = self.ability_scores.generate_scores(method="standard_array")
        self.assertEqual(len(scores), 6)
        self.assertEqual(sum(scores.values()), 72)  # Standard array sums to 72
        
        # Test rolling method (check ranges only, since it's random)
        scores = self.ability_scores.generate_scores(method="roll")
        self.assertEqual(len(scores), 6)
        for stat, value in scores.items():
            self.assertTrue(3 <= value <= 18)
        
        # Test point buy
        scores = self.ability_scores.generate_scores(method="point_buy", 
                                                    custom_scores={"strength": 15, "dexterity": 14, 
                                                                  "constitution": 13, "intelligence": 12, 
                                                                  "wisdom": 10, "charisma": 8})
        self.assertEqual(scores["strength"], 15)
        self.assertEqual(scores["charisma"], 8)
    
    def test_species_selection(self):
        """Test selecting a species and getting appropriate traits"""
        # Test a standard species
        human_traits = self.species.get_species_traits("human")
        self.assertIn("ability_score_increase", human_traits)
        self.assertIn("traits", human_traits)
        
        # Test an invalid species
        with self.assertRaises(ValueError):
            self.species.get_species_traits("invalid_species")
    
    def test_skill_proficiency_selection(self):
        """Test selecting skill proficiencies"""
        skills = Skills()
        
        # Create a fighter with proficiencies
        fighter_profs = skills.get_class_skill_proficiencies("fighter")
        
        # Check number of choices
        self.assertEqual(fighter_profs["num_choices"], 2)
        
        # Select some skills and verify
        selected_skills = ["athletics", "intimidation"]
        
        # Validate selection
        validation = skills.validate_skill_selection("fighter", selected_skills)
        self.assertTrue(validation["valid"])
        
        # Apply proficiencies
        character_skills = skills.apply_proficiencies(selected_skills)
        
        # Check proficiencies were applied
        self.assertTrue(character_skills["athletics"]["proficient"])
        self.assertTrue(character_skills["intimidation"]["proficient"])
        self.assertFalse(character_skills["arcana"]["proficient"])

    def test_personality_and_backstory_generation(self):
        """Test generating personality traits and backstory"""
        # Mock the LLM response for personality generation
        self.mock_ollama.return_value.generate_text.return_value = json.dumps({
            "personality_traits": "Brave, loyal, but quick to anger",
            "ideals": "Honor above all else",
            "bonds": "Sworn to protect my homeland",
            "flaws": "Stubborn to a fault",
            "backstory": "A soldier who lost everything in the war..."
        })
        
        # Create an actual personality
        personality = AbstractPersonality()  # This would actually use a concrete implementation
        
        # Generate traits based on inputs
        traits = personality.generate_traits("fighter", "soldier", "lawful good")
        
        # Verify traits were generated
        self.assertIn("personality_traits", traits)
        self.assertIn("ideals", traits)
        self.assertIn("bonds", traits)
        self.assertIn("flaws", traits)
        self.assertIn("backstory", traits)


# Using pytest for more complex tests with fixtures
@pytest.fixture
def mock_ollama_service():
    """Fixture for mocking OllamaService"""
    with patch('backend.core.services.ollama_service.OllamaService') as mock:
        yield mock

@pytest.fixture
def character():
    """Fixture for creating a test character"""
    return Character()

def test_full_character_creation(mock_ollama_service, character):
    """Test creating a full character with all components"""
    # Setup mock responses
    mock_ollama_service.return_value.generate_text.return_value = json.dumps({
        "personality": {
            "traits": "Curious and analytical",
            "ideals": "Knowledge is power",
            "bonds": "Dedicated to my arcane studies",
            "flaws": "Often overlooks practical concerns"
        },
        "backstory": "A scholar who discovered hidden magical talent..."
    })
    
    # Create comprehensive character data
    character_data = {
        "name": "Elara Nightwind",
        "level": 1,
        "species": "elf",
        "class": "wizard",
        "background": "sage",
        "alignment": "neutral good",
        "ability_scores": {
            "strength": 8,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 16,
            "wisdom": 13,
            "charisma": 10
        },
        "skills": ["arcana", "history", "investigation", "perception"],
        "equipment": ["spellbook", "dagger", "component pouch", "scholar's pack"]
    }
    
    # Create the character
    character_id = character.create_character(character_data)
    
    # Verify full character creation
    created_character = character.get_character(character_id)
    
    assert created_character["name"] == "Elara Nightwind"
    assert created_character["species"] == "elf"
    assert created_character["class"] == "wizard"
    assert created_character["ability_scores"]["intelligence"] == 16
    assert "arcana" in created_character["skills"]
    assert "spellbook" in created_character["equipment"]
    
    # Verify the LLM was called for personality/backstory generation
    mock_ollama_service.return_value.generate_text.assert_called_once()