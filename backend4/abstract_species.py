from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class SpeciesSize(Enum):
    """Official species sizes in D&D 5e (2024 Edition)."""
    TINY = auto()
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()
    HUGE = auto()
    GARGANTUAN = auto()

class AbstractSpecies(ABC):
    """
    Abstract base class defining the contract for character species in D&D 5e (2024 Edition).
    
    Per D&D 2024 rules, species (formerly known as races) define inherent character traits such as:
    - Size (typically Small or Medium for player characters)
    - Base walking speed (typically 25-35 feet)
    - Vision types (normal vision, darkvision, etc.)
    - Languages known
    - Special traits and abilities
    - Damage resistances or immunities (if any)
    - Tool or skill proficiencies (if any)
    
    This interface supports both official D&D species and custom creations.
    """
    
    # Core species from the 2024 Player's Handbook
    CORE_SPECIES = [
        "Aasimar", "Dragonborn", "Dwarf", "Elf", "Gnome",
        "Goliath", "Halfling", "Human", "Orc", "Tiefling"
    ]
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the species.
        
        Returns:
            str: Species name
        """
        pass
    
    @abstractmethod
    def get_size(self) -> SpeciesSize:
        """
        Get the size category of the species.
        
        Per D&D 2024 rules, most playable species are Small or Medium.
        
        Returns:
            SpeciesSize: Size category
        """
        pass
    
    @abstractmethod
    def get_base_speed(self) -> int:
        """
        Get the base walking speed in feet.
        
        Per D&D 2024 rules, this is typically 30 feet, with some exceptions:
        - Dwarves and small species often have 25 feet
        - Some species have enhanced speed (35 or 40 feet)
        
        Returns:
            int: Base walking speed in feet
        """
        pass
    
    @abstractmethod
    def get_movement_types(self) -> Dict[str, int]:
        """
        Get all movement types and speeds.
        
        Some species have additional movement types such as:
        - Flying
        - Swimming
        - Climbing
        - Burrowing
        
        Returns:
            Dict[str, int]: Dictionary mapping movement type to speed in feet
        """
        pass
    
    @abstractmethod
    def get_ability_score_increases(self) -> Dict[str, int]:
        """
        Get ability score increases granted by the species.
        
        Per D&D 2024 rules, species may provide ability score increases.
        
        Returns:
            Dict[str, int]: Dictionary mapping ability names to increases
        """
        pass
    
    @abstractmethod
    def get_vision_types(self) -> Dict[str, int]:
        """
        Get special vision types and their ranges.
        
        Per D&D 2024 rules, vision types include:
        - Normal vision (default)
        - Darkvision (common, 60-120 ft range)
        - Blindsight (rare)
        - Tremorsense (rare)
        - Truesight (very rare)
        
        Returns:
            Dict[str, int]: Dictionary mapping vision type to range in feet
        """
        pass
    
    @abstractmethod
    def get_languages(self) -> List[str]:
        """
        Get languages known by the species.
        
        Per D&D 2024 rules, most species know Common plus additional languages.
        
        Returns:
            List[str]: List of languages
        """
        pass
    
    @abstractmethod
    def get_damage_resistances(self) -> List[str]:
        """
        Get damage types the species has resistance to.
        
        Returns:
            List[str]: List of damage types
        """
        pass
    
    @abstractmethod
    def get_damage_immunities(self) -> List[str]:
        """
        Get damage types the species has immunity to.
        
        Returns:
            List[str]: List of damage types
        """
        pass
    
    @abstractmethod
    def get_condition_immunities(self) -> List[str]:
        """
        Get conditions the species has immunity to.
        
        Returns:
            List[str]: List of conditions
        """
        pass
    
    @abstractmethod
    def get_traits(self) -> Dict[str, Any]:
        """
        Get the species-specific traits and abilities.
        
        Per D&D 2024 rules, species traits define unique capabilities and may include:
        - Natural weapons
        - Magical abilities
        - Environmental adaptations
        - Cultural benefits
        
        Returns:
            Dict[str, Any]: Dictionary mapping trait names to descriptions and mechanics
        """
        pass
    
    @abstractmethod
    def get_proficiencies(self) -> Dict[str, List[str]]:
        """
        Get proficiencies granted by the species.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping proficiency types (skills, tools) to lists
        """
        pass
    
    @abstractmethod
    def get_lineages(self) -> List[str]:
        """
        Get available lineages or subraces for the species.
        
        Per D&D 2024 rules, many species have lineage options that provide additional
        or replacement traits.
        
        Returns:
            List[str]: List of available lineages
        """
        pass
    
    @abstractmethod
    def get_lineage_details(self, lineage: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific lineage.
        
        Args:
            lineage: Name of the lineage
            
        Returns:
            Optional[Dict[str, Any]]: Lineage details or None if not found
        """
        pass
    
    @abstractmethod
    def has_feature(self, feature_name: str) -> bool:
        """
        Check if the species has a specific feature.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            bool: True if the species has the feature
        """
        pass
    
    @abstractmethod
    def get_age_range(self) -> Tuple[int, int]:
        """
        Get the typical age range for the species.
        
        Per D&D 2024 rules, species vary widely in lifespan.
        
        Returns:
            Tuple[int, int]: (Maturity age, Maximum age)
        """
        pass
    
    @abstractmethod
    def get_size_dimensions(self) -> Dict[str, Tuple[float, float]]:
        """
        Get typical height and weight ranges for the species.
        
        Per D&D 2024 rules, each species has typical physical dimensions.
        
        Returns:
            Dict[str, Tuple[float, float]]: Dictionary with height and weight ranges
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert species information to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of species
        """
        pass
    
    @abstractmethod
    def validate(self) -> Tuple[bool, str]:
        """
        Validate the species definition against D&D 2024 rules.
        
        Returns:
            Tuple[bool, str]: (Is valid, explanation message)
        """
        pass
    
    @abstractmethod
    def apply_to_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the species traits and bonuses to a character.
        
        Args:
            character_data: Character information to modify
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        pass


class AbstractSpeciesRegistry(ABC):
    """
    Abstract base class for a registry of species in D&D 5e (2024 Edition).
    
    This interface supports managing collections of species, including custom creations.
    """
    
    @abstractmethod
    def get_all_species(self) -> List[str]:
        """
        Get a list of all available species names.
        
        Returns:
            List[str]: List of species names
        """
        pass
    
    @abstractmethod
    def get_species_details(self, species_name: str) -> Optional[AbstractSpecies]:
        """
        Get detailed information about a species.
        
        Args:
            species_name: Name of the species
            
        Returns:
            Optional[AbstractSpecies]: Species instance or None if not found
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
    def register_custom_species(self, species_data: Dict[str, Any]) -> AbstractSpecies:
        """
        Create and register a custom species.
        
        Args:
            species_data: Custom species definition
            
        Returns:
            AbstractSpecies: New custom species instance
        """
        pass
    
    @abstractmethod
    def get_core_species(self) -> List[str]:
        """
        Get only the core species from the 2024 Player's Handbook.
        
        Returns:
            List[str]: List of core species names
        """
        pass
    
    @abstractmethod
    def validate_custom_species(self, species_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a custom species definition against D&D 2024 design principles.
        
        Args:
            species_data: Custom species definition
            
        Returns:
            Tuple[bool, str]: (Is valid, explanation message)
        """
        pass