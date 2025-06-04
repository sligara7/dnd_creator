import unittest
from unittest.mock import MagicMock, patch
import pytest

from backend.core.character.character import Character
from backend.core.character.character_progression import CharacterProgression
from backend.core.classes.classes import Classes

class TestCharacterProgression(unittest.TestCase):
    """Test character progression and leveling"""
    
    def setUp(self):
        """Set up test environment"""
        self.character = Character()
        self.progression = CharacterProgression()
        self.classes = Classes()
        
        # Create a test character
        self.test_char_data = {
            "name": "Test Character",
            "level": 1,
            "class": "fighter",
            "subclass": None,
            "ability_scores": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 10,
                "wisdom": 12,
                "charisma": 8
            },
            "hit_points": 12,
            "experience_points": 0
        }
        
        # Create character
        self.char_id = self.character.create_character(self.test_char_data)
    
    def test_level_up_basic(self):
        """Test basic level up functionality"""
        # Set XP to trigger level up
        self.character.update_character(self.char_id, {"experience_points": 300})
        char_data = self.character.get_character(self.char_id)
        
        # Level up the character
        updated_char = self.progression.level_up(char_data)
        
        # Verify level increase
        self.assertEqual(updated_char["level"], 2)
        
        # Verify hit point increase (fighter gets d10 hit die)
        self.assertTrue(updated_char["hit_points"] > 12)
        
        # Update character with level up data
        self.character.update_character(self.char_id, updated_char)
    
    def test_add_subclass(self):
        """Test adding a subclass at appropriate level"""
        # Update to level 3 (fighter gets subclass at level 3)
        self.character.update_character(self.char_id, {
            "level": 2,
            "experience_points": 900  # Enough for level 3
        })
        
        char_data = self.character.get_character(self.char_id)
        
        # Level up to level 3
        updated_char = self.progression.level_up(char_data)
        
        # Verify level and check for subclass option
        self.assertEqual(updated_char["level"], 3)
        
        # Get subclass options
        subclass_options = self.classes.get_subclass_options("fighter")
        self.assertTrue(len(subclass_options) > 0)
        
        # Select a subclass
        subclass = subclass_options[0]
        updated_char["subclass"] = subclass
        
        # Update character with subclass
        self.character.update_character(self.char_id, updated_char)
        
        # Verify subclass was added
        final_char = self.character.get_character(self.char_id)
        self.assertEqual(final_char["subclass"], subclass)
        
    def test_ability_score_improvement(self):
        """Test ability score improvement at level 4"""
        # Update to level 3
        self.character.update_character(self.char_id, {
            "level": 3,
            "experience_points": 2700  # Enough for level 4
        })
        
        char_data = self.character.get_character(self.char_id)
        
        # Level up to level 4
        updated_char = self.progression.level_up(char_data)
        
        # Verify level and check for ASI
        self.assertEqual(updated_char["level"], 4)
        self.assertTrue(self.progression.check_for_ability_score_improvement(updated_char))
        
        # Apply ASI
        asi_choice = {"ability": "strength", "increase": 2}
        updated_char = self.progression.apply_ability_score_improvement(updated_char, asi_choice)
        
        # Verify ability score was increased
        self.assertEqual(updated_char["ability_scores"]["strength"], 18)
        
        # Update character
        self.character.update_character(self.char_id, updated_char)
        
        # Alternative: Select a feat instead of ASI
        # This would involve:
        # 1. Checking if feats are allowed
        # 2. Selecting a feat
        # 3. Applying the feat benefits


@pytest.fixture
def character_with_progression():
    """Fixture for a character with progression tracking"""
    char = Character()
    
    # Create character with tracking
    char_data = {
        "name": "Progression Test",
        "level": 1,
        "class": "wizard",
        "ability_scores": {
            "strength": 8,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 16,
            "wisdom": 12,
            "charisma": 10
        },
        "hit_points": 8,
        "experience_points": 0,
        "progression_log": []  # For tracking development
    }
    
    char_id = char.create_character(char_data)
    return char, char_id

def test_character_progression_tracking(character_with_progression):
    """Test tracking character progression over time"""
    char, char_id = character_with_progression
    progression = CharacterProgression()
    
    # Get initial character
    character_data = char.get_character(char_id)
    
    # Add progression entry for character creation
    progression.add_progression_entry(
        character_data, 
        "character_creation", 
        "Character created at level 1"
    )
    
    # Add XP for defeating enemies
    progression.add_experience(character_data, 100, "Defeated goblin patrol")
    
    # Update character
    char.update_character(char_id, character_data)
    character_data = char.get_character(char_id)
    
    # Add more XP to trigger level up
    progression.add_experience(character_data, 200, "Completed first quest")
    
    # Level up
    updated_char = progression.level_up(character_data)
    
    # Add progression entry for level up
    progression.add_progression_entry(
        updated_char,
        "level_up",
        "Advanced to level 2"
    )
    
    # Update character
    char.update_character(char_id, updated_char)
    
    # Verify progression log entries
    final_char = char.get_character(char_id)
    assert len(final_char["progression_log"]) == 4
    assert final_char["progression_log"][0]["event_type"] == "character_creation"
    assert final_char["progression_log"][3]["event_type"] == "level_up"
    assert final_char["level"] == 2
    assert final_char["experience_points"] == 300