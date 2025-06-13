"""
Character Repository Interface - Application Layer Boundary.

Defines the contract for persisting and retrieving character data.
This abstraction allows the domain layer to remain independent of
specific storage implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..enums.progression_types import ProgressionType


class ICharacterRepository(ABC):
    """Interface for character data persistence."""
    
    @abstractmethod
    async def save_character(self, character_id: str, character_data: Dict[str, Any]) -> bool:
        """Save complete character data."""
        pass
    
    @abstractmethod 
    async def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve character by ID."""
        pass
    
    @abstractmethod
    async def save_character_progression(self, 
                                       character_id: str, 
                                       progression_data: Dict[int, Dict[str, Any]]) -> bool:
        """Save character progression (levels 1-20)."""
        pass
    
    @abstractmethod
    async def get_character_progression(self, character_id: str) -> Optional[Dict[int, Dict[str, Any]]]:
        """Get complete character progression."""
        pass
    
    @abstractmethod
    async def save_custom_content(self, 
                                character_id: str, 
                                custom_content: List[Dict[str, Any]]) -> bool:
        """Save custom content associated with character."""
        pass
    
    @abstractmethod
    async def get_custom_content(self, character_id: str) -> List[Dict[str, Any]]:
        """Get custom content for character."""
        pass
    
    @abstractmethod
    async def list_characters(self, user_id: str = None) -> List[Dict[str, Any]]:
        """List available characters."""
        pass
    
    @abstractmethod
    async def delete_character(self, character_id: str) -> bool:
        """Delete character and all associated data."""
        pass