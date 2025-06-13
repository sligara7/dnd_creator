from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from ..enums.dnd_constants import Ability, SpeciesSize, Skill
from ..enums.content_types import ContentSource
from ..enums.validation_types import ValidationResult


class AbstractSpecies(ABC):
    """
    Abstract contract for all D&D character species in the Creative Content Framework.
    
    This interface defines the rules that both official and generated species
    must follow, ensuring D&D 2024 rule compliance while enabling creative freedom.
    
    Per D&D 2024 rules, all species must provide:
    - Size and movement characteristics
    - Ability score increases (total not exceeding +3)
    - Species traits and features
    - Languages and proficiencies
    - Balanced power level appropriate for 1st level characters
    """
    
    # Balance guidelines for generated species
    MAX_ABILITY_SCORE_TOTAL = 3
    TYPICAL_TRAIT_COUNT = (2, 4)  # Min, Max recommended
    
    @property
    @abstractmethod
    def species_name(self) -> str:
        """Official name of the species."""
        pass
    
    @property
    @abstractmethod
    def size(self) -> SpeciesSize:
        """Creature size category."""
        pass
    
    @property
    @abstractmethod
    def base_speed(self) -> int:
        """Base walking speed in feet."""
        pass
    
    @property
    @abstractmethod
    def content_source(self) -> ContentSource:
        """Source of this species (core rules, generated, custom, etc.)."""
        pass
    
    @abstractmethod
    def get_ability_score_increases(self) -> Dict[Ability, int]:
        """
        Get ability score increases granted by this species.
        
        Per D&D 2024 rules, total increases should not exceed +3,
        and individual increases are typically +1 or +2.
        
        Returns:
            Dictionary mapping abilities to their increases
        """
        pass
    
    @abstractmethod
    def get_movement_types(self) -> Dict[str, int]:
        """
        Get all movement types and their speeds.
        
        Returns:
            Dictionary mapping movement types to speeds in feet
            Example: {"walk": 30, "fly": 30, "swim": 30}
        """
        pass
    
    @abstractmethod
    def get_senses(self) -> Dict[str, int]:
        """
        Get special senses and their ranges.
        
        Returns:
            Dictionary mapping sense types to ranges in feet
            Example: {"darkvision": 60, "blindsight": 10}
        """
        pass
    
    @abstractmethod
    def get_languages(self) -> List[str]:
        """
        Get languages known by this species.
        
        Per D&D 2024 rules, most species know Common plus
        one or more additional languages.
        
        Returns:
            List of language names
        """
        pass
    
    @abstractmethod
    def get_species_traits(self) -> List[Dict[str, Any]]:
        """
        Get all special traits granted by this species.
        
        Each trait should include:
        - name: Trait name
        - description: What the trait does
        - type: "passive", "active", "reaction", etc.
        - usage: Usage limitations if any
        
        Returns:
            List of trait dictionaries
        """
        pass
    
    @abstractmethod
    def get_proficiencies(self) -> Dict[str, List[str]]:
        """
        Get proficiencies granted by this species.
        
        Returns:
            Dictionary with categories like "skills", "tools", "weapons"
        """
        pass
    
    @abstractmethod
    def get_damage_resistances(self) -> List[str]:
        """
        Get damage types this species resists.
        
        Returns:
            List of damage type names
        """
        pass
    
    @abstractmethod
    def get_damage_immunities(self) -> List[str]:
        """
        Get damage types this species is immune to.
        
        Returns:
            List of damage type names
        """
        pass
    
    @abstractmethod
    def get_condition_immunities(self) -> List[str]:
        """
        Get conditions this species is immune to.
        
        Returns:
            List of condition names
        """
        pass
    
    @abstractmethod
    def get_age_range(self) -> Tuple[int, int]:
        """
        Get typical age range for this species.
        
        Returns:
            Tuple of (maturity age, maximum lifespan)
        """
        pass
    
    @abstractmethod
    def get_size_dimensions(self) -> Dict[str, Tuple[float, float]]:
        """
        Get typical physical dimensions.
        
        Returns:
            Dictionary with "height" and "weight" ranges
            Example: {"height": (4.5, 6.0), "weight": (100, 200)}
        """
        pass
    
    @abstractmethod
    def get_cultural_elements(self) -> Dict[str, Any]:
        """
        Get cultural and societal information about this species.
        
        Used by the Creative Content Framework for generating
        thematically appropriate content.
        
        Returns:
            Dictionary of cultural elements and traditions
        """
        pass
    
    @abstractmethod
    def validate_species_balance(self) -> List[ValidationResult]:
        """
        Validate that this species meets D&D balance guidelines.
        
        For generated/custom species, this ensures:
        - Ability score increases within limits
        - Appropriate trait power level
        - Balanced utility and combat capabilities
        
        Returns:
            List of validation results
        """
        pass
    
    @abstractmethod
    def get_lineage_options(self) -> List[str]:
        """
        Get available lineage variants for this species.
        
        Per D&D 2024 rules, many species have lineage options
        that modify or replace certain traits.
        
        Returns:
            List of available lineage names
        """
        pass
    
    @abstractmethod
    def get_lineage_details(self, lineage_name: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific lineage variant.
        
        Args:
            lineage_name: Name of the lineage
            
        Returns:
            Dictionary with lineage modifications or None if not found
        """
        pass
    
    @abstractmethod
    def apply_to_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply species traits and bonuses to a character.
        
        Args:
            character_data: Character information to modify
            
        Returns:
            Updated character data with species benefits applied
        """
        pass
    
    def calculate_ability_score_total(self) -> int:
        """Calculate total ability score increases granted."""
        increases = self.get_ability_score_increases()
        return sum(increases.values())
    
    def validate_ability_score_increases(self) -> bool:
        """Validate that ability score increases are within D&D limits."""
        total = self.calculate_ability_score_total()
        if total > self.MAX_ABILITY_SCORE_TOTAL:
            return False
        
        # Check individual increases don't exceed +2
        increases = self.get_ability_score_increases()
        return all(increase <= 2 for increase in increases.values())
    
    def get_trait_count(self) -> int:
        """Get the number of species traits."""
        return len(self.get_species_traits())