"""
Character Generation Module

This module handles the creation and management of all character types in the game:
- Player Characters (PCs): Fully featured characters controlled by players
- Non-Player Characters (NPCs): Complete characters controlled by the DM
- Monsters, Beasts, and Animals: Simplified entities with limited features

The character generation system supports the D&D 2024 rules and can be used
for both Minecraft integration and standalone tabletop play.
"""

# Import the abstract character class
from backend.core.character.abstract_character import AbstractCharacter

# Import concrete character implementations
from backend.core.character.player_character import PlayerCharacter
from backend.core.character.non_player_character import NonPlayerCharacter
from backend.core.character.monster import Monster
from backend.core.character.beast import Beast
from backend.core.character.animal import Animal

# Import character factory and generators
from backend.core.character.character_factory import CharacterFactory
from backend.core.character.random_character_generator import RandomCharacterGenerator
from backend.core.character.character_builder import CharacterBuilder

# Character types
CHARACTER_TYPES = {
    "pc": PlayerCharacter,
    "npc": NonPlayerCharacter,
    "monster": Monster,
    "beast": Beast, 
    "animal": Animal
}

def create_character(character_type="pc", **kwargs):
    """
    Create a character of the specified type with the given parameters.
    
    Args:
        character_type (str): Type of character to create ("pc", "npc", "monster", "beast", "animal")
        **kwargs: Additional parameters for character creation
        
    Returns:
        AbstractCharacter: The created character
        
    Raises:
        ValueError: If the character type is not recognized
    """
    if character_type.lower() not in CHARACTER_TYPES:
        raise ValueError(f"Unknown character type: {character_type}")
        
    return CHARACTER_TYPES[character_type.lower()](**kwargs)

def generate_random_character(character_type="pc", level=1, **kwargs):
    """
    Generate a random character of the specified type.
    
    Args:
        character_type (str): Type of character to create
        level (int): Character level
        **kwargs: Additional parameters to guide random generation
        
    Returns:
        AbstractCharacter: The generated character
    """
    return RandomCharacterGenerator.generate(
        character_type=character_type,
        level=level,
        **kwargs
    )

def load_character_from_file(filename):
    """
    Load a character from a JSON file.
    
    Args:
        filename (str): Path to the character file
        
    Returns:
        AbstractCharacter: The loaded character
    """
    return CharacterFactory.load_from_file(filename)

__all__ = [
    'AbstractCharacter',
    'PlayerCharacter', 'NonPlayerCharacter',
    'Monster', 'Beast', 'Animal',
    'CharacterFactory', 'RandomCharacterGenerator', 'CharacterBuilder',
    'create_character', 'generate_random_character', 'load_character_from_file',
    'CHARACTER_TYPES'
]