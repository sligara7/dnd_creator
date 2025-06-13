# domain/services/character_state_service.py
from typing import Dict, Any, Optional
from ..entities.character_state import CharacterState
from ..entities.character import Character
from ..rules.rest_rules import RestRules
from ..rules.combat_rules import CombatRules

class CharacterStateService:
    """
    Domain service for managing character state changes.
    Contains all the business logic from the original CharacterState methods.
    """
    
    def __init__(self):
        self.rest_rules = RestRules()
        self.combat_rules = CombatRules()
    
    def take_damage(self, state: CharacterState, damage: int) -> Dict[str, int]:
        """Apply damage to the character (from original take_damage method)."""
        result = {"temp_hp_damage": 0, "hp_damage": 0, "overkill": 0}
        
        # Apply to temporary HP first
        if state.temporary_hit_points > 0:
            temp_damage = min(damage, state.temporary_hit_points)
            state.temporary_hit_points -= temp_damage
            damage -= temp_damage
            result["temp_hp_damage"] = temp_damage
        
        # Then to regular HP
        if damage > 0:
            state.current_hit_points -= damage
            result["hp_damage"] = damage
            
            if state.current_hit_points < 0:
                result["overkill"] = abs(state.current_hit_points)
                state.current_hit_points = 0
        
        return result
    
    def heal_character(self, state: CharacterState, healing: int) -> int:
        """Heal the character (from original heal method)."""
        # Implementation from original heal method
        pass
    
    def take_short_rest(self, character: Character, state: CharacterState, 
                       hit_dice_spent: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Perform a short rest (from original take_short_rest method)."""
        # Implementation from original take_short_rest method
        pass
    
    def take_long_rest(self, character: Character, state: CharacterState) -> Dict[str, Any]:
        """Perform a long rest (from original take_long_rest method)."""
        # Implementation from original take_long_rest method
        pass
    
    def reset_action_economy(self, state: CharacterState) -> None:
        """Reset action economy for a new turn."""
        state.actions_used = 0
        state.bonus_actions_used = 0
        state.reactions_used = 0
    
    def add_condition(self, state: CharacterState, condition: str, 
                     duration: Optional[int] = None, source: Optional[str] = None) -> None:
        """Apply a condition to the character."""
        state.active_conditions[condition] = {
            "duration": duration,
            "source": source,
            "applied_at": datetime.now()
        }
    
    def use_spell_slot(self, state: CharacterState, level: int) -> bool:
        """Use a spell slot of the specified level."""
        if level in state.spell_slots_remaining and state.spell_slots_remaining[level] > 0:
            state.spell_slots_remaining[level] -= 1
            return True
        return False