"""
Character Interface - Domain Entity Boundary.

Defines the contract for the Character aggregate root in the domain model.
This represents the complete character entity with all progression and custom content.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..enums.progression_types import ProgressionType, MilestoneType, ThematicTier


class ICharacter(ABC):
    """
    Interface for the Character aggregate root.
    
    Represents a complete D&D character with progression from levels 1-20,
    including all custom content and thematic evolution.
    """
    
    @property
    @abstractmethod
    def character_id(self) -> str:
        """Unique character identifier."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Character name."""
        pass
    
    @property
    @abstractmethod
    def concept(self) -> str:
        """Original character concept description."""
        pass
    
    @abstractmethod
    def apply_concept(self, concept_data: Dict[str, Any]) -> None:
        """Apply initial character concept and thematic identity."""
        pass
    
    @abstractmethod
    def generate_progression(self, levels: List[int], progression_type: ProgressionType) -> None:
        """Generate character sheets for specified levels."""
        pass
    
    @abstractmethod
    def add_custom_content(self, content: Dict[str, Any]) -> None:
        """Add custom content to character."""
        pass
    
    @abstractmethod
    def get_character_sheet(self, level: int) -> Optional[Dict[str, Any]]:
        """Get character sheet for specific level."""
        pass
    
    @abstractmethod
    def get_complete_progression(self) -> Dict[int, Dict[str, Any]]:
        """Get all generated character sheets."""
        pass
    
    @abstractmethod
    def get_custom_content(self) -> List[Dict[str, Any]]:
        """Get all custom content associated with character."""
        pass
    
    @abstractmethod
    def get_milestones(self, milestone_type: MilestoneType = None) -> List[Dict[str, Any]]:
        """Get character progression milestones."""
        pass
    
    @abstractmethod
    def get_thematic_evolution(self) -> Dict[ThematicTier, str]:
        """Get thematic evolution narrative across tiers."""
        pass
    
    @abstractmethod
    def validate_character(self) -> List[str]:
        """Validate complete character for consistency and balance."""
        pass