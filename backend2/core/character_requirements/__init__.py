"""
Character Requirements Package

This package contains all class interfaces and contract requirements 
for character development in the D&D character creator application.

These abstract base classes define the contractual obligations that
implementations must follow to be compatible with the system.
"""

# Package metadata
__version__ = '0.1.0'
__author__ = 'DnD Tools Team'

# Import core abstract classes to make them available at package level
# When implementing specific modules, uncomment and add the appropriate imports:

from .abstract_character_class import AbstractCharacterClass
from .abstract_equipment import AbstractEquipment, AbstractWeapon, AbstractArmor
from .abstract_feats import AbstractFeat
from .abstract_multiclass_and_level_up import AbstractMulticlassAndLevelUp
from .abstract_personality import AbstractPersonalityAndBackstory
from .abstract_skills import AbstractSkills
from .abstract_species import AbstractSpecies
from .abstract_spells import AbstractSpell, AbstractSpells

# Export key types that should be available directly from the package
__all__ = [
    'AbstractCharacterClass',
    'AbstractCreature',
    'AbstractEquipment',
    'AbstractWeapon', 
    'AbstractArmor',
    'AbstractFeat',
    'AbstractMulticlassAndLevelUp',
    'AbstractPersonalityAndBackstory',
    'AbstractSkills',
    'AbstractSpecies',
    'AbstractSpell',
    'AbstractSpells',
]