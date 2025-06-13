"""
Content Generator Interface - Domain Service Boundary.

Defines the contract for the core content generation service that orchestrates
the creation of D&D characters and custom content. This is a domain service
that encapsulates the business logic for creative content generation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..enums.content_types import ContentType, CreativityLevel, ThemeCategory
from ..enums.balance_levels import BalanceLevel
from ..enums.progression_types import ProgressionType, ThematicTier


class IContentGenerator(ABC):
    """
    Domain service interface for creative content generation.
    
    This service orchestrates the generation of characters and custom content
    while maintaining D&D rule compliance and thematic consistency.
    """
    
    @abstractmethod
    async def generate_character_concept(self,
                                       user_input: str,
                                       creativity_level: CreativityLevel,
                                       balance_level: BalanceLevel) -> Dict[str, Any]:
        """
        Generate initial character concept from user description.
        
        Args:
            user_input: User's character description
            creativity_level: Level of creative freedom
            balance_level: Balance enforcement level
            
        Returns:
            Character concept with thematic identity
        """
        pass
    
    @abstractmethod
    async def generate_full_character(self,
                                    concept: Dict[str, Any],
                                    progression_type: ProgressionType = ProgressionType.SINGLE_CLASS) -> Dict[str, Any]:
        """
        Generate complete character from validated concept.
        
        Args:
            concept: Character concept data
            progression_type: Type of level progression
            
        Returns:
            Complete character with all custom content
        """
        pass
    
    @abstractmethod
    async def generate_character_progression(self,
                                           character_data: Dict[str, Any],
                                           levels: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        Generate character sheets for specified levels.
        
        Args:
            character_data: Base character information
            levels: List of levels to generate
            
        Returns:
            Dictionary mapping levels to character sheet data
        """
        pass
    
    @abstractmethod
    async def generate_custom_content(self,
                                    content_type: ContentType,
                                    theme_requirements: Dict[str, Any],
                                    balance_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate custom D&D content based on thematic requirements.
        
        Args:
            content_type: Type of content to generate
            theme_requirements: Thematic constraints and elements
            balance_requirements: Balance and power level requirements
            
        Returns:
            Generated custom content
        """
        pass
    
    @abstractmethod
    async def refine_character(self,
                             current_character: Dict[str, Any],
                             user_feedback: str,
                             refinement_scope: List[str]) -> Dict[str, Any]:
        """
        Refine character based on user feedback.
        
        Args:
            current_character: Current character state
            user_feedback: User's refinement requests
            refinement_scope: Areas to focus refinement on
            
        Returns:
            Refined character data
        """
        pass
    
    @abstractmethod
    def validate_character_concept(self,
                                 concept: Dict[str, Any]) -> List[str]:
        """
        Validate that character concept is feasible within D&D framework.
        
        Args:
            concept: Character concept to validate
            
        Returns:
            List of validation issues (empty if valid)
        """
        pass
    
    @abstractmethod
    def get_required_custom_content(self,
                                  concept: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Determine what custom content is needed for character concept.
        
        Args:
            concept: Character concept
            
        Returns:
            List of required custom content specifications
        """
        pass
    
    @abstractmethod
    def generate_thematic_evolution(self,
                                  character_data: Dict[str, Any],
                                  tier_progression: List[ThematicTier]) -> Dict[str, Any]:
        """
        Generate thematic character evolution across tiers.
        
        Args:
            character_data: Character information
            tier_progression: Thematic development tiers
            
        Returns:
            Thematic evolution narrative and milestones
        """
        pass