# domain/rules/rest_rules.py
from abc import ABC, abstractmethod
from typing import Dict, Any
from ..entities.character import Character
from ..entities.character_state import CharacterState

class RestRules:
    """Rules governing rest mechanics."""
    
    def can_take_short_rest(self, character: Character, state: CharacterState) -> bool:
        """Determine if character can take a short rest."""
        # Business logic for short rest eligibility
        pass
    
    def calculate_short_rest_benefits(self, character: Character, 
                                    hit_dice_spent: Dict[str, int]) -> Dict[str, Any]:
        """Calculate benefits from short rest."""
        # Hit dice healing calculations
        pass
    
    def calculate_long_rest_benefits(self, character: Character) -> Dict[str, Any]:
        """Calculate benefits from long rest."""
        # Full healing, spell slot recovery, etc.
        pass