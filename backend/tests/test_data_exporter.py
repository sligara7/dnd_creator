import unittest
from unittest.mock import MagicMock, patch
import json
import tempfile
import os
import pytest

from backend.core.services.data_exporter import DataExporter, CharacterExporter

class TestDataExporter(unittest.TestCase):
    """Test the data export functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test exports
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = DataExporter(export_directory=self.temp_dir)
        
        # Sample test data
        self.test_character = {
            "name": "Export Test",
            "level": 3,
            "class": "ranger",
            "species": "elf",
            "ability_scores": {
                "strength": 12,
                "dexterity": 16,
                "constitution": 14,
                "intelligence": 10,
                "wisdom": 14,
                "charisma": 8
            }
        }
    
    def tearDown(self):
        """Clean up after test"""
        # Remove temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_json_export(self):
        """Test exporting character to JSON"""
        result = self.exporter.export_to_json(
            data=self.test_character,
            entity_type="character"
        )
        
        # Verify export was successful
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(result["filepath"]))
        
        # Verify file content
        with open(result["filepath"], 'r') as f:
            exported_data = json.load(f)
            self.assertEqual(exported_data["name"], "Export Test")
            self.assertEqual(exported_data["level"], 3)
            self.assertEqual(exported_data["ability_scores"]["dexterity"], 16)
    
    def test_markdown_export(self):
        """Test exporting character to markdown"""
        result = self.exporter.export_data(
            data=self.test_character,
            entity_type="character",
            format="markdown"
        )
        
        # Verify export was successful
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(result["filepath"]))
        
        # Verify file content
        with open(result["filepath"], 'r') as f:
            content = f.read()
            self.assertIn("# Export Test", content)
            self.assertIn("**Level**: 3", content)
            self.assertIn("**Species**: elf", content)

    def test_legacy_character_exporter(self):
        """Test the legacy CharacterExporter class"""
        char_exporter = CharacterExporter(export_directory=self.temp_dir)
        
        result = char_exporter.export_character_to_json(self.test_character)
        
        # Verify export was successful
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(result["filepath"]))
        
        # Verify file content
        with open(result["filepath"], 'r') as f:
            exported_data = json.load(f)
            self.assertEqual(exported_data["name"], "Export Test")


@pytest.fixture
def exporter():
    """Fixture for DataExporter with temporary directory"""
    temp_dir = tempfile.mkdtemp()
    yield DataExporter(export_directory=temp_dir)
    
    # Cleanup
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    os.rmdir(temp_dir)

def test_npc_export(exporter):
    """Test exporting NPCs"""
    npc_data = {
        "name": "Guard Captain",
        "role": "town guard",
        "challenge_rating": 3,
        "personality": {
            "traits": "Stern but fair"
        },
        "motivations": ["Protect the town", "Maintain order"]
    }
    
    # Export to JSON
    result = exporter.export_data(
        data=npc_data,
        entity_type="npc",
        format="json"
    )
    
    # Verify export
    assert result["success"]
    assert os.path.exists(result["filepath"])
    
    # Verify exported data has extra metadata
    with open(result["filepath"], 'r') as f:
        exported_data = json.load(f)
        assert exported_data["name"] == "Guard Captain"
        assert "_export_metadata" in exported_data
        assert exported_data["_export_metadata"]["entity_type"] == "npc"

def test_creature_export(exporter):
    """Test exporting creatures"""
    creature_data = {
        "name": "Ancient Dragon",
        "type": "dragon",
        "challenge_rating": 20,
        "size": "huge",
        "hit_points": 330,
        "armor_class": 22,
        "abilities": [
            {"name": "Fire Breath", "description": "The dragon exhales fire..."}
        ]
    }
    
    # Export to markdown
    result = exporter.export_data(
        data=creature_data,
        entity_type="creature",
        format="markdown"
    )
    
    # Verify export
    assert result["success"]
    assert os.path.exists(result["filepath"])
    
    # Check markdown content
    with open(result["filepath"], 'r') as f:
        content = f.read()
        assert "# Ancient Dragon" in content
        assert "**CR**: 20" in content
        assert "**Size**: huge" in content
        assert "Fire Breath" in content