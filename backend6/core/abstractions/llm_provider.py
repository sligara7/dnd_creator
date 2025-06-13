"""
LLM Provider Interface - Infrastructure Boundary.

Defines the contract for Large Language Model providers used in the
Creative Content Framework. This abstraction allows the system to work
with different LLM providers (OpenAI, Anthropic, etc.) while keeping
the domain logic independent of specific implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..enums.creativity_levels import CreativityLevel
from ..enums.content_types import ContentType, ThemeCategory
from ..enums.balance_levels import BalanceLevel


class ILLMProvider(ABC):
    """
    Interface for LLM providers used in creative content generation.
    
    This interface enforces the dependency inversion principle by ensuring
    that domain services depend on abstractions, not concrete implementations.
    """
    
    @abstractmethod
    async def generate_character_concept(self, 
                                       user_input: str,
                                       creativity_level: CreativityLevel,
                                       theme_categories: List[ThemeCategory] = None) -> Dict[str, Any]:
        """
        Generate initial character concept from user description.
        
        Args:
            user_input: User's character description
            creativity_level: Level of creative freedom
            theme_categories: Optional theme constraints
            
        Returns:
            Dictionary containing character concept data
        """
        pass
    
    @abstractmethod
    async def generate_custom_content(self,
                                    content_type: ContentType,
                                    requirements: Dict[str, Any],
                                    creativity_level: CreativityLevel) -> Dict[str, Any]:
        """
        Generate custom D&D content based on requirements.
        
        Args:
            content_type: Type of content to generate
            requirements: Content requirements and constraints
            creativity_level: Creative freedom level
            
        Returns:
            Generated content data
        """
        pass
    
    @abstractmethod
    async def refine_character(self,
                             current_character: Dict[str, Any],
                             user_feedback: str,
                             creativity_level: CreativityLevel) -> Dict[str, Any]:
        """
        Refine character based on user feedback.
        
        Args:
            current_character: Current character state
            user_feedback: User's refinement requests
            creativity_level: Creative freedom level
            
        Returns:
            Refined character data
        """
        pass
    
    @abstractmethod
    async def validate_balance(self,
                             content_data: Dict[str, Any],
                             content_type: ContentType,
                             balance_level: BalanceLevel) -> Dict[str, Any]:
        """
        Analyze content balance using LLM reasoning.
        
        Args:
            content_data: Content to analyze
            content_type: Type of content
            balance_level: Balance assessment strictness
            
        Returns:
            Balance analysis results
        """
        pass
    
    @abstractmethod 
    async def generate_progression_narrative(self,
                                           character_data: Dict[str, Any],
                                           level_range: tuple[int, int]) -> Dict[str, Any]:
        """
        Generate thematic progression narrative for character levels.
        
        Args:
            character_data: Character information
            level_range: Level range for progression
            
        Returns:
            Progression narrative and thematic evolution
        """
        pass
    
    @abstractmethod
    async def generate_signature_equipment(self,
                                         character_concept: Dict[str, Any],
                                         equipment_type: str,
                                         power_level: int) -> Dict[str, Any]:
        """
        Generate signature equipment for character concept.
        
        Args:
            character_concept: Character thematic information
            equipment_type: Type of equipment (weapon, armor, etc.)
            power_level: Appropriate power level for character
            
        Returns:
            Signature equipment data
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of this LLM provider."""
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """Get list of supported models for this provider."""
        pass
    
    @abstractmethod
    def get_rate_limits(self) -> Dict[str, Any]:
        """Get rate limiting information for this provider."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to the LLM provider."""
        pass