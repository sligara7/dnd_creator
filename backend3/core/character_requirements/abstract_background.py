from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Set, Tuple


class BackstoryElement(Enum):
    """Key elements that make up a character's backstory according to D&D 2024 rules."""
    ORIGIN = auto()       # Where the character comes from
    FAMILY = auto()       # Family details
    EDUCATION = auto()    # Training and learning
    DEFINING_EVENT = auto() # Major event that shaped the character
    MOTIVATION = auto()   # Why they became an adventurer
    CONNECTIONS = auto()  # Relationships with others
    GOALS = auto()        # Future aspirations


class AbstractBackground(ABC):
    """
    Abstract base class defining the contract for character backgrounds in D&D 5e (2024 Edition).
    
    Per D&D 2024 rules, backgrounds provide a character's personal history and include mechanical benefits:
    - Two skill proficiencies
    - Tool proficiencies
    - Languages
    - Equipment
    - Background feature
    - A 1st-level feat
    """
    
    @abstractmethod
    def get_all_backgrounds(self) -> List[str]:
        """
        Get a list of all official backgrounds.
        
        Returns:
            List[str]: List of official background names
        """
        pass
    
    @abstractmethod
    def get_background_details(self, background: str) -> Dict[str, Any]:
        """
        Get complete details for a background.
        
        Args:
            background: Character background
            
        Returns:
            Dict[str, Any]: Complete background details
        """
        pass
    
    @abstractmethod
    def get_background_proficiencies(self, background: str) -> Dict[str, List[str]]:
        """
        Get proficiencies granted by a background.
        
        Per D&D 2024 rules, backgrounds typically provide:
        - Two skill proficiencies
        - One or more tool proficiencies
        - One language
        
        Args:
            background: Character background
            
        Returns:
            Dict[str, List[str]]: Dictionary with skill, tool, and language proficiencies
        """
        pass
    
    @abstractmethod
    def get_background_equipment(self, background: str) -> List[str]:
        """
        Get starting equipment granted by a background.
        
        Per D&D 2024 rules, backgrounds provide a set of starting equipment.
        
        Args:
            background: Character background
            
        Returns:
            List[str]: List of starting equipment items
        """
        pass
    
    @abstractmethod
    def get_background_feature(self, background: str) -> Dict[str, Any]:
        """
        Get the special feature associated with a background.
        
        Per D&D 2024 rules, each background provides a special feature
        that grants a unique benefit.
        
        Args:
            background: Character background
            
        Returns:
            Dict[str, Any]: Background feature details
        """
        pass
    
    @abstractmethod
    def get_background_feat(self, background: str) -> str:
        """
        Get the 1st-level feat granted by a background.
        
        Per D&D 2024 rules, each background provides a 1st-level feat.
        
        Args:
            background: Character background
            
        Returns:
            str: Name of the feat
        """
        pass
    
    @abstractmethod
    def validate_custom_background(self, background_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a custom background against D&D 2024 rules.
        
        Per D&D 2024 rules, custom backgrounds should provide:
        - Two skill proficiencies
        - A total of two between tool proficiencies and languages
        - A standard equipment package
        - A background feature
        - A 1st-level feat
        
        Args:
            background_data: Custom background definition
            
        Returns:
            Tuple[bool, str]: (True if valid, explanation message)
        """
        pass
    
    @abstractmethod
    def create_custom_background(self, background_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Create a custom character background.
        
        Per D&D 2024 rules, players can create custom backgrounds that fit their character concept.
        
        Args:
            background_data: Background specification
            
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        pass
    
    @abstractmethod
    def apply_background_benefits(self, character_data: Dict[str, Any], background: str) -> Dict[str, Any]:
        """
        Apply all mechanical benefits of a background to a character.
        
        Args:
            character_data: Character information
            background: Background to apply
            
        Returns:
            Dict[str, Any]: Updated character data
        """
        pass
    
    @abstractmethod
    def get_character_background(self) -> str:
        """
        Get the character's current background.
        
        Returns:
            str: Background name
        """
        pass
    
    @abstractmethod
    def set_character_background(self, background: str) -> bool:
        """
        Set the character's background.
        
        Args:
            background: Background name
            
        Returns:
            bool: True if successfully set
        """
        pass