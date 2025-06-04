import unittest
from unittest.mock import MagicMock, patch
import pytest
import json
import os
import tempfile

# Import core components
from backend.core.character.character import Character
from backend.core.classes.classes import Classes
from backend.core.species.species import Species
from backend.core.ability_scores.ability_scores import AbilityScores
from backend.core.skills.skills import Skills
from backend.core.spells.spell import Spell
from backend.core.services.data_exporter import DataExporter

@pytest.fixture
def temp_export_dir():
    """Create temporary directory for exports"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # Cleanup
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)

@pytest.fixture
def mock_ollama():
    """Mock OllamaService for testing"""
    with patch('backend.core.services.ollama_service.OllamaService') as mock:
        mock.return_value.generate_text.return_value = json.dumps({
            "response": "This is a mock LLM response",
            "personality": {
                "traits": "Brave, curious",
                "backstory": "A simple backstory"
            }
        })
        yield mock

@pytest.mark.integration
def test_full_character_creation_process(mock_ollama, temp_export_dir):
    """Test full character creation process from start to export"""
    # Step 1: Create ability scores
    ability_scores = AbilityScores()
    scores = ability_scores.generate_scores(method="standard_array")
    
    assert len(scores) == 6
    assert "strength" in scores
    
    # Step 2: Select species
    species = Species()
    elf_traits = species.get_species_traits("elf")
    
    assert "ability_score_increase" in elf_traits
    
    # Apply species traits to ability scores
    for ability, increase in elf_traits["ability_score_increase"].items():
        if ability in scores:
            scores[ability] += increase
    
    # Step 3: Select class
    classes = Classes()
    wizard_details = classes.get_class_details("wizard")
    
    assert "hit_die" in wizard_details
    assert wizard_details["hit_die"] == "d6"
    
    # Step 4: Calculate hit points
    constitution_modifier = (scores["constitution"] - 10) // 2
    hit_points = int(wizard_details["hit_die"][1:]) + constitution_modifier
    
    # Step 5: Select skills
    skills_manager = Skills()
    wizard_skills = skills_manager.get_class_skill_proficiencies("wizard")
    selected_skills = ["arcana", "investigation"]
    
    character_skills = skills_manager.apply_proficiencies(selected_skills)
    
    assert character_skills["arcana"]["proficient"] == True
    
    # Step 6: Get starting spells for wizard
    spell_manager = Spell()
    wizard_spells = spell_manager.get_class_spell_list("wizard", level=1)
    selected_spells = [spell["name"] for spell in wizard_spells[:3]]  # Select first 3
    
    # Step 7: Create full character
    character_manager = Character()
    character_data = {
        "name": "Elindra Moonshadow",
        "level": 1,
        "species": "elf",
        "class": "wizard",
        "subclass": None,  # Will be selected at level 3
        "ability_scores": scores,
        "hit_points": hit_points,
        "skills": character_skills,
        "spells": selected_spells,
        "equipment": ["spellbook", "component pouch", "dagger", "scholar's pack"]
    }
    
    char_id = character_manager.create_character(character_data)
    created_char = character_manager.get_character(char_id)
    
    assert created_char["name"] == "Elindra Moonshadow"
    assert created_char["species"] == "elf"
    assert created_char["level"] == 1
    
    # Step 8: Export character
    exporter = DataExporter(export_directory=temp_export_dir)
    export_result = exporter.export_data(
        data=created_char,
        entity_type="character",
        format="json"
    )
    
    assert export_result["success"] == True
    assert os.path.exists(export_result["filepath"])