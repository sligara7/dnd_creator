from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Set, Tuple

class PersonalityTraitSource(Enum):
    """Enumeration of sources for personality traits in D&D 5e (2024 Edition)."""
    BACKGROUND = auto()   # From character background
    CUSTOM = auto()       # Player-defined
    RANDOM = auto()       # Randomly generated
    CLASS = auto()        # From character class
    SPECIES = auto()      # From character species
    ALIGNMENT = auto()    # From character alignment

class BackstoryElement(Enum):
    """Key elements that make up a character's backstory according to D&D 2024 rules."""
    ORIGIN = auto()       # Where the character comes from
    FAMILY = auto()       # Family details
    EDUCATION = auto()    # Training and learning
    DEFINING_EVENT = auto() # Major event that shaped the character
    MOTIVATION = auto()   # Why they became an adventurer
    CONNECTIONS = auto()  # Relationships with others
    GOALS = auto()        # Future aspirations

class AbstractPersonalityAndBackstory(ABC):
    """
    Abstract base class defining the contract for character personality and backstory in D&D 5e (2024 Edition).
    
    According to D&D 2024 rules, a character's personality is defined by:
    - Traits: Short statements that describe character behavior and attitudes
    - Ideals: Core principles and beliefs that motivate the character
    - Bonds: Connections to people, places, or things in the world
    - Flaws: Character weaknesses or vulnerabilities
    
    Backgrounds provide a character's personal history and include:
    - Skill proficiencies
    - Tool proficiencies
    - Languages
    - Equipment
    - Background feature
    - A 1st-level feat
    """
    
    @abstractmethod
    def get_personality_options(self, background: str) -> Dict[str, List[str]]:
        """
        Get official personality options based on background.
        
        Per D&D 2024 rules, each background suggests several personality traits,
        ideals, bonds, and flaws that fit its theme.
        
        Args:
            background: Character background
            
        Returns:
            Dict[str, List[str]]: Dictionary with personality options for traits, ideals, bonds, flaws
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
    def validate_personality(self, traits: List[str], ideals: List[str], 
                          bonds: List[str], flaws: List[str]) -> Tuple[bool, str]:
        """
        Validate personality elements against D&D 2024 rules.
        
        Per D&D 2024 rules, these elements should be concise and roleplay-focused.
        
        Args:
            traits: List of personality traits
            ideals: List of character ideals
            bonds: List of character bonds
            flaws: List of character flaws
            
        Returns:
            Tuple[bool, str]: (True if valid, explanation message)
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
    def get_personality_suggested_by_alignment(self, alignment: Tuple[str, str]) -> Dict[str, List[str]]:
        """
        Get personality traits suggested by a character's alignment.
        
        Per D&D 2024 rules, alignment can influence personality.
        
        Args:
            alignment: (ethical, moral) alignment tuple
            
        Returns:
            Dict[str, List[str]]: Suggested traits, ideals, bonds, flaws
        """
        pass
    
    @abstractmethod
    def format_backstory_template(self, background: str) -> Dict[BackstoryElement, str]:
        """
        Get a template for creating a backstory based on a background.
        
        Args:
            background: Character background
            
        Returns:
            Dict[BackstoryElement, str]: Template prompts for each backstory element
        """
        pass