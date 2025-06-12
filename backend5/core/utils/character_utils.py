from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from ..entities.character import Character

class CharacterFormatter:
    """Utility class for formatting character data."""
    
    @staticmethod
    def format_character_summary(character: Character) -> str:
        """Format character as a readable summary."""
        summary = character.get_character_summary()
        
        return f"""
=== {summary['name']} ===
Level {summary['level']} {summary['species']} {summary['class']}
Hit Points: {summary['hit_points']}
Armor Class: {summary['armor_class']}
Proficiency Bonus: +{summary['proficiency_bonus']}

Ability Scores:
  STR: {character.strength} ({character.get_ability_modifier('strength'):+d})
  DEX: {character.dexterity} ({character.get_ability_modifier('dexterity'):+d})
  CON: {character.constitution} ({character.get_ability_modifier('constitution'):+d})
  INT: {character.intelligence} ({character.get_ability_modifier('intelligence'):+d})
  WIS: {character.wisdom} ({character.get_ability_modifier('wisdom'):+d})
  CHA: {character.charisma} ({character.get_ability_modifier('charisma'):+d})
        """.strip()
    
    @staticmethod
    def format_character_sheet(character: Character) -> str:
        """Format character as a complete character sheet."""
        # Implementation for full character sheet formatting
        pass
    
    @staticmethod
    def format_level_progression(character: Character) -> str:
        """Format character level progression summary."""
        if not character.is_multiclass:
            return f"Level {character.total_level} {character.primary_class}"
        
        class_levels = [f"{cls} {lvl}" for cls, lvl in character.character_classes.items()]
        return f"Level {character.total_level} ({'/'.join(class_levels)})"

class CharacterValidator:
    """Utility class for basic character validation."""
    
    @staticmethod
    def validate_character_data(data: Dict[str, Any]) -> List[str]:
        """Validate basic character data structure."""
        errors = []
        
        # Required fields
        required_fields = ["name", "species"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Ability scores
        if "ability_scores" in data:
            for ability, score in data["ability_scores"].items():
                if not isinstance(score, int) or score < 1 or score > 30:
                    errors.append(f"Invalid {ability} score: {score}")
        
        return errors
    
    @staticmethod
    def validate_level_data(classes: Dict[str, int]) -> List[str]:
        """Validate character class levels."""
        errors = []
        
        if not classes:
            errors.append("Character must have at least one class level")
            return errors
        
        total_level = sum(classes.values())
        if total_level > 20:
            errors.append(f"Total level ({total_level}) exceeds maximum (20)")
        
        for class_name, level in classes.items():
            if level < 1 or level > 20:
                errors.append(f"Invalid level for {class_name}: {level}")
        
        return errors

class CharacterSerializer:
    """Utility class for character serialization."""
    
    @staticmethod
    def to_json(character: Character, indent: int = 2) -> str:
        """Serialize character to JSON string."""
        data = character.to_dict()
        return json.dumps(data, indent=indent, default=str)
    
    @staticmethod
    def from_json(json_str: str) -> Character:
        """Deserialize character from JSON string."""
        data = json.loads(json_str)
        return Character.from_dict(data)
    
    @staticmethod
    def to_file(character: Character, filename: str) -> None:
        """Save character to JSON file."""
        with open(filename, 'w') as f:
            f.write(CharacterSerializer.to_json(character))
    
    @staticmethod
    def from_file(filename: str) -> Character:
        """Load character from JSON file."""
        with open(filename, 'r') as f:
            return CharacterSerializer.from_json(f.read())