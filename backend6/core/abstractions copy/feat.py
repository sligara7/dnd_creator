from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from ..enums.content_types import FeatCategory, ContentSource
from ..enums.validation_types import ValidationResult


class AbstractFeat(ABC):
    """
    Abstract contract for all D&D feats in the Creative Content Framework.
    
    This interface defines the rules that both official and generated feats
    must follow, ensuring D&D 2024 rule compliance while enabling creative freedom.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Feat name."""
        pass
    
    @property
    @abstractmethod
    def category(self) -> FeatCategory:
        """Feat category (General, Heroic, Epic, etc.)."""
        pass
    
    @property
    @abstractmethod
    def content_source(self) -> ContentSource:
        """Source of this feat (core rules, generated, custom, etc.)."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get feat description.
        
        Returns:
            Full feat description
        """
        pass
    
    @abstractmethod
    def get_prerequisites(self) -> Dict[str, Any]:
        """
        Get feat prerequisites.
        
        Returns:
            Dictionary of prerequisites (ability scores, level, etc.)
        """
        pass
    
    @abstractmethod
    def get_benefits(self) -> Dict[str, Any]:
        """
        Get feat benefits.
        
        Returns:
            Dictionary of mechanical benefits
        """
        pass
    
    @abstractmethod
    def get_minimum_level(self) -> int:
        """
        Get minimum character level for this feat.
        
        Returns:
            Minimum level required
        """
        pass
    
    @abstractmethod
    def validate_prerequisites(self, character_data: Dict[str, Any]) -> List[str]:
        """
        Validate if character meets feat prerequisites.
        
        Args:
            character_data: Character information
            
        Returns:
            List of prerequisite violations (empty if valid)
        """
        pass
    
    @abstractmethod
    def apply_benefits(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply feat benefits to character.
        
        Args:
            character_data: Character information to modify
            
        Returns:
            Updated character data
        """
        pass
    
    @abstractmethod
    def validate_feat_balance(self) -> List[ValidationResult]:
        """
        Validate feat power level for its category.
        
        Returns:
            List of validation results
        """
        pass
    
    @abstractmethod
    def get_thematic_elements(self) -> Dict[str, Any]:
        """
        Get thematic elements for content generation.
        
        Returns:
            Dictionary of themes and flavor elements
        """
        pass