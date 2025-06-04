"""
Character Species Module

This module contains all the character species for the Minecraft D&D integration.
All species adhere to the Species abstract base class interface.
"""

# Import the abstract base class
from core.species.abstract_character_species import Species

# Import standard D&D species
from core.species.aasimar import Aasimar
from core.species.dragonborn import Dragonborn
from core.species.dwarf import Dwarf
from core.species.elf import Elf
from core.species.gnome import Gnome
from core.species.goliath import Goliath
from core.species.halfling import Halfling
from core.species.human import Human
from core.species.orc import Orc
from core.species.tiefling import Tiefling

# Import additional species
from core.species.tortle import Tortle
from core.species.fairy import Fairy
from core.species.simic_hybrid import SimicHybrid
from core.species.sith import Sith

# Import the customizable species and factory
from core.species.create_species import CustomizableSpecies, SpeciesFactory

# Dictionary of available species for easy lookup
STANDARD_SPECIES = {
    "aasimar": Aasimar,
    "dragonborn": Dragonborn,
    "dwarf": Dwarf,
    "elf": Elf,
    "gnome": Gnome,
    "goliath": Goliath,
    "halfling": Halfling,
    "human": Human,
    "orc": Orc,
    "tiefling": Tiefling
}

ADDITIONAL_SPECIES = {
    "tortle": Tortle,
    "fairy": Fairy,
    "simic_hybrid": SimicHybrid,
    "sith": Sith
}

ALL_SPECIES = {**STANDARD_SPECIES, **ADDITIONAL_SPECIES}

# Export all species and utility functions
__all__ = [
    'Species',
    'Aasimar', 'Dragonborn', 'Dwarf', 'Elf', 'Gnome', 
    'Goliath', 'Halfling', 'Human', 'Orc', 'Tiefling',
    'Tortle', 'Fairy', 'SimicHybrid', 'Sith',
    'CustomizableSpecies', 'SpeciesFactory',
    'STANDARD_SPECIES', 'ADDITIONAL_SPECIES', 'ALL_SPECIES',
    'get_available_species', 'create_species_instance'
]

def get_available_species():
    """
    Returns a dictionary of all available character species.
    
    Returns:
        dict: A dictionary mapping species names to species constructors
    """
    # Get custom species from saved files
    custom_species = SpeciesFactory.get_available_species()
    
    # Combine with built-in species
    return {**ALL_SPECIES, **{s: CustomizableSpecies for s in custom_species}}

def create_species_instance(species_name, **kwargs):
    """
    Factory function to create a species instance of any available species.
    
    Args:
        species_name (str): Name of the species to create
        **kwargs: Additional arguments specific to the species
    
    Returns:
        Species: An instance of the specified species
    """
    species_name = species_name.lower()
    
    # Check if it's a standard or additional species
    if species_name in ALL_SPECIES:
        return ALL_SPECIES[species_name](**kwargs)
    
    # Check if it's a saved customizable species
    custom_species = SpeciesFactory.get_available_species()
    if species_name in custom_species:
        return SpeciesFactory.load_species_from_file(f"{species_name}.json")
    
    raise ValueError(f"Unknown character species: {species_name}")