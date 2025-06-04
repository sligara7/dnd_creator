from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Set, Tuple

class FeatCategory(Enum):
    """Enumeration of feat categories in D&D 5e (2024 Edition)."""
    GENERAL = auto()      # General feats available to anyone
    HEROIC = auto()       # Heroic tier feats (1st-level+)
    EPIC = auto()         # Epic tier feats (higher-level only)
    SPECIES = auto()      # Species-specific feats
    CLASS = auto()        # Class-specific feats
    BACKGROUND = auto()   # Background-specific feats

class AbstractFeat(ABC):
    """
    Abstract base class for a single feat in D&D 5e (2024 Edition).
    
    A feat in D&D represents a special talent or expertise that gives a character
    special capabilities beyond what their class normally provides.
    """
    
    def __init__(self, 
                 name: str, 
                 description: str, 
                 category: FeatCategory, 
                 prerequisites: Dict[str, Any],
                 benefits: Dict[str, Any],
                 min_level: int = 1):
        """
        Initialize a feat.
        
        Args:
            name: Feat name
            description: Feat description
            category: Feat category
            prerequisites: Dictionary of prerequisites (ability_scores, class, species, etc.)
            benefits: Dictionary of benefits provided by the feat
            min_level: Minimum character level required
        """
        self.name = name
        self.description = description
        self.category = category
        self.prerequisites = prerequisites
        self.benefits = benefits
        self.min_level = min_level
    
    def __str__(self) -> str:
        """String representation of the feat."""
        return f"{self.name} ({self.category.name.lower()} feat)"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert feat to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.name,
            "prerequisites": self.prerequisites,
            "benefits": self.benefits,
            "min_level": self.min_level
        }

class AbstractFeats(ABC):
    """
    Abstract base class for handling feats in D&D 5e (2024 Edition).
    
    This class provides methods to interact with the feat system, including:
    - Retrieving information about feats
    - Checking prerequisites
    - Applying feat benefits
    - Managing feat selections for characters
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
        Get feats available to a specific character.
        
        Args:
            character_data: Character information including class, level, species, etc.
            
        Returns:
            List[AbstractFeat]: List of feats available to the character
        """
        pass
    
    @abstractmethod
    def validate_feat_prerequisites(self, character_data: Dict[str, Any], feat_name: str) -> Tuple[bool, str]:
        """
        Check if character meets feat prerequisites.
        
        Args:
            character_data: Character information including ability scores, class, level, etc.
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
    def get_feats_by_level_range(self, min_level: int, max_level: Optional[int] = None) -> List[AbstractFeat]:
        """
        Get feats available within a level range.
        
        Args:
            min_level: Minimum character level
            max_level: Maximum character level (None for no upper limit)
            
        Returns:
            List[AbstractFeat]: List of feats available in the level range
        """
        pass
    
    @abstractmethod
    def get_feat_prerequisites(self, feat_name: str) -> Optional[Dict[str, Any]]:
        """
        Get prerequisites for a feat.
        
        Args:
            feat_name: Name of the feat
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary of prerequisites or None if feat not found
        """
        pass
    
    @abstractmethod
    def get_feats_for_asi(self, character_data: Dict[str, Any]) -> List[AbstractFeat]:
        """
        Get feats that could be taken instead of an Ability Score Improvement.
        
        Args:
            character_data: Character information
            
        Returns:
            List[AbstractFeat]: List of feats available as ASI replacements
        """
        pass
    
    @abstractmethod
    def get_feat_chains(self) -> Dict[str, List[str]]:
        """
        Get feat chains (feats that build on each other).
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping prerequisite feats to their follow-up feats
        """
        pass
    
    @abstractmethod
    def simulate_feat_benefit(self, character_data: Dict[str, Any], feat_name: str) -> Dict[str, Any]:
        """
        Simulate how a feat would affect a character without actually applying it.
        
        Args:
            character_data: Character information
            feat_name: Name of the feat to simulate
            
        Returns:
            Dict[str, Any]: Dictionary of changes that would occur
        """
        pass
    
    @abstractmethod
    def get_feat_usage_resources(self, feat_name: str) -> Optional[Dict[str, Any]]:
        """
        Get resource tracking information for feats with limited uses.
        
        Args:
            feat_name: Name of the feat
            
        Returns:
            Optional[Dict[str, Any]]: Resource usage information or None if feat has no usage limits
        """
        pass
    
    def feat_exists(self, feat_name: str) -> bool:
        """
        Check if a feat exists.
        
        Args:
            feat_name: Name of the feat
            
        Returns:
            bool: True if feat exists, False otherwise
        """
        return self.get_feat_details(feat_name) is not None