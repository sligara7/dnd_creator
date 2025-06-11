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

class AbstractPersonality(ABC):
    """
    Abstract base class defining the contract for character personality in D&D 5e (2024 Edition).
    
    According to D&D 2024 rules, a character's personality is defined by:
    - Traits: Short statements that describe character behavior and attitudes
    - Ideals: Core principles and beliefs that motivate the character
    - Bonds: Connections to people, places, or things in the world
    - Flaws: Character weaknesses or vulnerabilities
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
    
    @abstractmethod
    def get_character_personality(self) -> Dict[str, List[str]]:
        """
        Get current personality elements for the character.
        
        Returns:
            Dict[str, List[str]]: Dictionary with traits, ideals, bonds, flaws
        """
        pass
    
    @abstractmethod
    def set_character_personality(self, personality_elements: Dict[str, List[str]]) -> bool:
        """
        Set personality elements for the character.
        
        Args:
            personality_elements: Dictionary with traits, ideals, bonds, flaws
            
        Returns:
            bool: True if successfully set
        """
        pass
    
    @abstractmethod
    def get_backstory(self) -> Dict[BackstoryElement, str]:
        """
        Get the character's backstory elements.
        
        Returns:
            Dict[BackstoryElement, str]: Backstory elements
        """
        pass
    
    @abstractmethod
    def set_backstory(self, backstory: Dict[BackstoryElement, str]) -> bool:
        """
        Set the character's backstory elements.
        
        Args:
            backstory: Backstory elements
            
        Returns:
            bool: True if successfully set
        """
        pass