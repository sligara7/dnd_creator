from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class SpeciesSize(Enum):
    """Enumeration of species sizes in D&D 5e (2024 Edition)."""
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()

class AbstractSpecies(ABC):
    """
    Abstract base class for character species in D&D 5e (2024 Edition).
    
    Species (formerly known as races) define inherent character traits like size,
    movement speed, darkvision, and special abilities. The 2024 Player's Handbook
    features a core list of 10 playable species with various traits and abilities.
    """
    
    # Core species from the 2024 Player's Handbook
    CORE_SPECIES = [
        "Aasimar", "Dragonborn", "Dwarf", "Elf", "Gnome",
        "Goliath", "Halfling", "Human", "Orc", "Tiefling"
    ]
    
    # Common additional species from other sourcebooks
    EXTENDED_SPECIES = [
        "Aarakocra", "Genasi", "Githyanki", "Githzerai", "Kenku",
        "Lizardfolk", "Tabaxi", "Tortle", "Triton", "Warforged"
    ]
    
    def __init__(self, 
                 name: str, 
                 size: SpeciesSize = SpeciesSize.MEDIUM,
                 speed: int = 30,
                 darkvision: int = 0,
                 languages: List[str] = None,
                 resistances: List[str] = None,
                 traits: Dict[str, Any] = None,
                 proficiencies: List[str] = None,
                 vision_types: List[str] = None):
        """
        Initialize a species.
        
        Args:
            name: Species name
            size: Size category of the species
            speed: Base walking speed in feet
            darkvision: Range of darkvision in feet (0 for none)
            languages: Languages known by the species
            resistances: Damage types the species has resistance to
            traits: Special traits of the species
            proficiencies: Skill or tool proficiencies granted by the species
            vision_types: Special vision types (e.g., "Blindsight", "Truesight")
        """
        self.name = name
        self.size = size
        self.speed = speed
        self.darkvision = darkvision
        self.languages = languages or ["Common"]
        self.resistances = resistances or []
        self.traits = traits or {}
        self.proficiencies = proficiencies or []
        self.vision_types = vision_types or []
    
    @abstractmethod
    def get_all_species(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available species.
        
        Returns:
            List[Dict[str, Any]]: List of species with basic information
        """
        pass
    
    @abstractmethod
    def get_species_details(self, species_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a species.
        
        Args:
            species_name: Name of the species
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary with species details or None if not found
        """
        pass
    
    @abstractmethod
    def get_traits(self) -> Dict[str, str]:
        """
        Get the traits specific to this species.
        
        Returns:
            Dict[str, str]: Dictionary mapping trait names to descriptions
        """
        pass
    
    @abstractmethod
    def apply_species_bonuses(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the species-specific bonuses to a character.
        
        Args:
            character_data: Character information to modify
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        pass
    
    @abstractmethod
    def get_species_by_size(self, size: SpeciesSize) -> List[str]:
        """
        Get species that are of a specific size.
        
        Args:
            size: Size category to filter by
            
        Returns:
            List[str]: List of species names
        """
        pass
    
    @abstractmethod
    def get_species_by_ability_bonus(self, ability: str) -> List[str]:
        """
        Get species that provide a bonus to a specific ability.
        
        Args:
            ability: Ability score name
            
        Returns:
            List[str]: List of species names
        """
        pass
    
    @abstractmethod
    def get_species_by_feature(self, feature: str) -> List[str]:
        """
        Get species that have a specific feature.
        
        Args:
            feature: Feature to search for
            
        Returns:
            List[str]: List of species names
        """
        pass
    
    @abstractmethod
    def get_lineage_options(self, species_name: str) -> List[Dict[str, Any]]:
        """
        Get lineage options for a species.
        
        Args:
            species_name: Name of the species
            
        Returns:
            List[Dict[str, Any]]: List of lineage options
        """
        pass
    
    @abstractmethod
    def create_custom_species(self, custom_data: Dict[str, Any]) -> 'AbstractSpecies':
        """
        Create a custom species.
        
        Args:
            custom_data: Custom species definition
            
        Returns:
            AbstractSpecies: New custom species instance
        """
        pass
    
    def has_darkvision(self) -> bool:
        """
        Check if the species has darkvision.
        
        Returns:
            bool: True if the species has darkvision
        """
        return self.darkvision > 0
    
    def has_resistance(self, damage_type: str) -> bool:
        """
        Check if the species has resistance to a specific damage type.
        
        Args:
            damage_type: The type of damage to check
            
        Returns:
            bool: True if the species has resistance
        """
        return damage_type in self.resistances
    
    def can_speak(self, language: str) -> bool:
        """
        Check if the species can speak a specific language.
        
        Args:
            language: The language to check
            
        Returns:
            bool: True if the species can speak the language
        """
        return language in self.languages
    
    def get_size_multiplier(self) -> float:
        """
        Get the size multiplier for the species.
        
        Returns:
            float: Size multiplier for various game mechanics
        """
        if self.size == SpeciesSize.SMALL:
            return 0.5
        elif self.size == SpeciesSize.MEDIUM:
            return 1.0
        elif self.size == SpeciesSize.LARGE:
            return 2.0
        return 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert species to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of species
        """
        return {
            "name": self.name,
            "size": self.size.name,
            "speed": self.speed,
            "darkvision": self.darkvision,
            "languages": self.languages,
            "resistances": self.resistances,
            "traits": self.traits,
            "proficiencies": self.proficiencies,
            "vision_types": self.vision_types
        }
    
    def __str__(self) -> str:
        """
        String representation of species.
        
        Returns:
            str: Formatted species string
        """
        result = f"{self.name} ({self.size.name})\n"
        result += f"Speed: {self.speed} ft.\n"
        
        if self.darkvision > 0:
            result += f"Darkvision: {self.darkvision} ft.\n"
        
        if self.languages:
            result += f"Languages: {', '.join(self.languages)}\n"
        
        if self.resistances:
            result += f"Resistances: {', '.join(self.resistances)}\n"
        
        if self.traits:
            result += "Traits:\n"
            for trait, desc in self.traits.items():
                result += f"  {trait}: {desc}\n"
        
        return result