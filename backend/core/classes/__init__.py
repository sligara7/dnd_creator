"""
Character Classes Module

This module contains all the character classes for the Minecraft D&D integration.
All classes adhere to the CharacterClass abstract base class interface.
"""

# Import the abstract base class
from core.classes.abstract_character_class import CharacterClass

# Import standard D&D classes
from core.classes.barbarian import Barbarian
from core.classes.bard import Bard
from core.classes.cleric import Cleric
from core.classes.druid import Druid
from core.classes.fighter import Fighter
from core.classes.monk import Monk
from core.classes.paladin import Paladin
from core.classes.ranger import Ranger
from core.classes.rogue import Rogue
from core.classes.sorcerer import Sorcerer
from core.classes.warlock import Warlock
from core.classes.wizard import Wizard

# Import custom classes
from core.classes.accursed import Accursed

# Import the customizable class and factory
from core.classes.create_class import CustomizableClass, ClassFactory

# Dictionary of available classes for easy lookup
STANDARD_CLASSES = {
    "barbarian": Barbarian,
    "bard": Bard,
    "cleric": Cleric,
    "druid": Druid,
    "fighter": Fighter,
    "monk": Monk,
    "paladin": Paladin,
    "ranger": Ranger,
    "rogue": Rogue,
    "sorcerer": Sorcerer,
    "warlock": Warlock,
    "wizard": Wizard
}

CUSTOM_CLASSES = {
    "accursed": Accursed
}

ALL_CLASSES = {**STANDARD_CLASSES, **CUSTOM_CLASSES}

# Export all classes and utility functions
__all__ = [
    'CharacterClass',
    'Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk',
    'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard',
    'Accursed',
    'CustomizableClass', 'ClassFactory',
    'STANDARD_CLASSES', 'CUSTOM_CLASSES', 'ALL_CLASSES',
    'get_available_classes', 'create_character'
]

def get_available_classes():
    """
    Returns a dictionary of all available character classes.
    
    Returns:
        dict: A dictionary mapping class names to class constructors
    """
    # Get custom classes from saved files
    custom_classes = ClassFactory.get_available_classes()
    
    # Combine with built-in classes
    return {**ALL_CLASSES, **{c: CustomizableClass for c in custom_classes}}

def create_character(class_name, level=1, xp=0, constitution_modifier=0, **kwargs):
    """
    Factory function to create a character of any available class.
    
    Args:
        class_name (str): Name of the class to create
        level (int): Starting level
        xp (int): Starting experience points
        constitution_modifier (int): Character's Constitution modifier
        **kwargs: Additional arguments specific to the class
    
    Returns:
        CharacterClass: An instance of the specified character class
    """
    class_name = class_name.lower()
    
    # Check if it's a standard or custom class
    if class_name in ALL_CLASSES:
        return ALL_CLASSES[class_name](level=level, xp=xp, 
                                      constitution_modifier=constitution_modifier, **kwargs)
    
    # Check if it's a saved customizable class
    custom_classes = ClassFactory.get_available_classes()
    if class_name in custom_classes:
        return ClassFactory.load_class_from_file(
            f"{class_name}.json", 
            level=level, 
            constitution_modifier=constitution_modifier
        )
    
    raise ValueError(f"Unknown character class: {class_name}")