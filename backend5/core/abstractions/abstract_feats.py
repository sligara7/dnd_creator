from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Set, Tuple

class FeatCategory(Enum):
    """Enumeration of official feat categories in D&D 5e (2024 Edition)."""
    GENERAL = auto()      # General feats available to anyone
    HEROIC = auto()       # Heroic tier feats (1st-level+)
    EPIC = auto()         # Epic tier feats (higher-level only)
    SPECIES = auto()      # Species-specific feats
    CLASS = auto()        # Class-specific feats
    BACKGROUND = auto()   # Background-specific feats
    # Additional categories can be created for custom feats

class AbstractFeat(ABC):
    """
    Abstract base class for feats in D&D 5e (2024 Edition).
    
    Per 2024 rules, feats represent special talents or expertise that give a character
    capabilities beyond what their class normally provides. They can be acquired:
    - At character creation (Background feat)
    - When reaching ability score improvement levels
    - Through certain class or species features
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the feat's name.
        
        Returns:
            str: Feat name
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the feat's description.
        
        Returns:
            str: Feat description
        """
        pass
    
    @abstractmethod
    def get_category(self) -> FeatCategory:
        """
        Get the feat's category.
        
        Returns:
            FeatCategory: Feat category
        """
        pass
    
    @abstractmethod
    def get_prerequisites(self) -> Dict[str, Any]:
        """
        Get the feat's prerequisites.
        
        Per 2024 rules, prerequisites can include:
        - Minimum ability scores
        - Specific class/species/background requirements
        - Character level requirements
        - Other feat requirements (feat chains)
        
        Returns:
            Dict[str, Any]: Dictionary of prerequisites
        """
        pass
    
    @abstractmethod
    def get_benefits(self) -> Dict[str, Any]:
        """
        Get the feat's benefits.
        
        Per 2024 rules, benefits may include:
        - Ability score improvements
        - Skill proficiencies
        - New actions or bonus actions
        - Special abilities or resources
        
        Returns:
            Dict[str, Any]: Dictionary of benefits
        """
        pass
    
    @abstractmethod
    def get_min_level(self) -> int:
        """
        Get minimum character level required for the feat.
        
        Returns:
            int: Minimum level required
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert feat to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of feat
        """
        pass


class AbstractFeats(ABC):
    """
    Abstract base class for managing feats in D&D 5e (2024 Edition).
    
    Per 2024 rules:
    - Characters typically receive one feat at 1st level from their background
    - Additional feats can be gained at ASI levels (4th, 8th, 12th, 16th, 19th)
    - Some classes or species provide additional feat options
    - Feats can provide one-time benefits or ongoing abilities
    """
    
    @abstractmethod
    def get_all_feats(self) -> List[AbstractFeat]:
        """
        Return a list of all available feats.
        
        Returns:
            List[AbstractFeat]: List of all feats
        """
        pass
    
    @abstractmethod
    def get_feat_details(self, feat_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a feat.
        
        Args:
            feat_name: Name of the feat
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary with feat details or None if not found
        """
        pass
    
    @abstractmethod
    def get_available_feats(self, character_data: Dict[str, Any]) -> List[AbstractFeat]:
        """
        Get feats available to a specific character based on prerequisites.
        
        Per 2024 rules, availability depends on:
        - Character level
        - Ability scores
        - Class, species, and background
        - Previously selected feats
        
        Args:
            character_data: Character information
            
        Returns:
            List[AbstractFeat]: List of feats available to the character
        """
        pass
    
    @abstractmethod
    def validate_feat_prerequisites(self, character_data: Dict[str, Any], feat_name: str) -> Tuple[bool, str]:
        """
        Check if character meets feat prerequisites.
        
        Args:
            character_data: Character information
            feat_name: Name of the feat to check
            
        Returns:
            Tuple[bool, str]: (True if prerequisites met, explanation message)
        """
        pass
    
    @abstractmethod
    def apply_feat_benefits(self, character_data: Dict[str, Any], feat_name: str) -> Dict[str, Any]:
        """
        Apply the benefits of a feat to character stats.
        
        Args:
            character_data: Character information to modify
            feat_name: Name of the feat to apply
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        pass
    
    @abstractmethod
    def get_feats_by_category(self, category: FeatCategory) -> List[AbstractFeat]:
        """
        Get feats by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List[AbstractFeat]: List of feats in the category
        """
        pass
    
    @abstractmethod
    def get_background_feats(self) -> List[AbstractFeat]:
        """
        Get feats available for selection at 1st level via background.
        
        Per 2024 rules, every character receives one feat from their background.
        
        Returns:
            List[AbstractFeat]: List of background-appropriate feats
        """
        pass
    
    @abstractmethod
    def get_asi_replacement_feats(self, character_data: Dict[str, Any]) -> List[AbstractFeat]:
        """
        Get feats that can be taken instead of an Ability Score Improvement.
        
        Per 2024 rules, characters can select a feat instead of an ASI.
        
        Args:
            character_data: Character information
            
        Returns:
            List[AbstractFeat]: List of feats available as ASI replacements
        """
        pass
    
    @abstractmethod
    def get_feat_usage_rules(self, feat_name: str) -> Optional[Dict[str, Any]]:
        """
        Get rules for how a feat can be used (usage limits, recharge conditions).
        
        Args:
            feat_name: Name of the feat
            
        Returns:
            Optional[Dict[str, Any]]: Usage rules or None if feat has no special usage limits
        """
        pass
    
    @abstractmethod
    def create_custom_feat(self, feat_data: Dict[str, Any]) -> AbstractFeat:
        """
        Create a custom feat from provided specifications.
        
        Args:
            feat_data: Feat specifications
            
        Returns:
            AbstractFeat: New custom feat
        """
        pass
    
    @abstractmethod
    def validate_custom_feat(self, feat_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a custom feat against D&D 2024 design principles.
        
        Args:
            feat_data: Custom feat specifications
            
        Returns:
            Tuple[bool, str]: (Is valid, explanation message)
        """
        pass
    
    @abstractmethod
    def get_suggested_feat_progressions(self, character_concept: Dict[str, Any]) -> List[List[str]]:
        """
        Get suggested feat progressions for a character concept.
        
        Args:
            character_concept: Character concept including class, playstyle, etc.
            
        Returns:
            List[List[str]]: List of feat progression paths
        """
        pass