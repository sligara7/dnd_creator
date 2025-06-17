from typing import Dict, List, Optional, Any
from datetime import datetime

class CharacterState:
    """
    IN-GAME INDEPENDENT VARIABLES - Updated during gameplay.
    
    These variables track the character's current state and resources,
    changing frequently during gameplay sessions.
    """
    
    def __init__(self):
        # Experience Points
        self.experience_points: int = 0
        
        # Hit Points - Current Values
        self.current_hit_points: int = 0
        self.temporary_hit_points: int = 0
        self.hit_point_maximum_modifier: int = 0
        
        # Hit Dice - Current Values
        self.hit_dice_remaining: Dict[str, int] = {}  # {"d8": 3, "d6": 2}
        
        # Spell Slots - Current Values
        self.spell_slots_total: Dict[int, int] = {}     # {1: 4, 2: 3, 3: 2}
        self.spell_slots_remaining: Dict[int, int] = {}  # {1: 2, 2: 1, 3: 0}
        self.spells_known: Dict[int, List[str]] = {}    # {0: ["Fire Bolt"], 1: ["Magic Missile"]}
        self.spells_prepared: List[str] = []
        self.ritual_book_spells: List[str] = []
        
        # Equipment - Current Items
        self.armor: Optional[str] = None
        self.shield: bool = False
        self.weapons: List[Dict[str, Any]] = []
        self.equipment: List[Dict[str, Any]] = []
        self.magical_items: List[Dict[str, Any]] = []
        self.attuned_items: List[str] = []
        self.max_attunement_slots: int = 3
        
        # Currency
        self.currency: Dict[str, int] = {
            "copper": 0, "silver": 0, "electrum": 0, "gold": 0, "platinum": 0
        }
        
        # Conditions and Effects
        self.active_conditions: Dict[str, Dict[str, Any]] = {}
        self.exhaustion_level: int = 0
        
        # Temporary Defenses
        self.temp_damage_resistances: Set[str] = set()
        self.temp_damage_immunities: Set[str] = set()
        self.temp_damage_vulnerabilities: Set[str] = set()
        self.temp_condition_immunities: Set[str] = set()
        
        # Action Economy - Current State
        self.actions_per_turn: int = 1
        self.bonus_actions_per_turn: int = 1
        self.reactions_per_turn: int = 1
        self.actions_used: int = 0
        self.bonus_actions_used: int = 0
        self.reactions_used: int = 0
        
        # Companion Creatures
        self.beast_companion: Optional[Dict[str, Any]] = None
        
        # Adventure Notes
        self.notes: Dict[str, str] = {
            'organizations': "", 'allies': "", 'enemies': "", 'backstory': "", 'other': ""
        }
        
        # Timestamps
        self.last_updated: str = ""
        self.last_long_rest: Optional[str] = None
        self.last_short_rest: Optional[str] = None
    
    def reset_action_economy(self) -> None:
        """Reset action economy for a new turn."""
        self.actions_used = 0
        self.bonus_actions_used = 0
        self.reactions_used = 0
    
    def take_damage(self, damage: int) -> Dict[str, int]:
        """Apply damage to the character."""
        result = {"temp_hp_damage": 0, "hp_damage": 0, "overkill": 0}
        
        # Apply to temporary HP first
        if self.temporary_hit_points > 0:
            temp_damage = min(damage, self.temporary_hit_points)
            self.temporary_hit_points -= temp_damage
            damage -= temp_damage
            result["temp_hp_damage"] = temp_damage
        
        # Then to regular HP
        if damage > 0:
            self.current_hit_points -= damage
            result["hp_damage"] = damage
            
            if self.current_hit_points < 0:
                result["overkill"] = abs(self.current_hit_points)
                self.current_hit_points = 0
        
        return result
    
    def heal(self, healing: int) -> int:
        """Heal the character and return amount healed."""
        # Note: This needs max_hit_points from CharacterStats
        # Will be handled by the main CharacterSheet class
        pass
    
    def use_spell_slot(self, level: int) -> bool:
        """Use a spell slot of the specified level."""
        if level not in self.spell_slots_remaining or self.spell_slots_remaining[level] <= 0:
            return False
        
        self.spell_slots_remaining[level] -= 1
        return True
    
    def add_condition(self, condition: str, duration: Optional[int] = None, 
                     source: Optional[str] = None) -> None:
        """Apply a condition to the character."""
        self.active_conditions[condition] = {
            "duration": duration,
            "source": source,
            "applied_at": datetime.now().isoformat()
        }
    
    def remove_condition(self, condition: str) -> bool:
        """Remove a condition from the character."""
        if condition in self.active_conditions:
            del self.active_conditions[condition]
            return True
        return False
    
    def take_short_rest(self, hit_dice_spent: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Perform a short rest."""
        result = {"hp_recovered": 0, "hit_dice_spent": {}}
        
        if hit_dice_spent:
            # Process hit dice healing
            for die_type, count in hit_dice_spent.items():
                available = self.hit_dice_remaining.get(die_type, 0)
                if available >= count:
                    self.hit_dice_remaining[die_type] = available - count
                    result["hit_dice_spent"][die_type] = count
                    # HP recovery calculation would need CharacterStats
        
        self.last_short_rest = datetime.now().isoformat()
        return result
    
    def take_long_rest(self) -> Dict[str, Any]:
        """Perform a long rest."""
        result = {"hp_recovered": 0, "spell_slots_recovered": {}, "hit_dice_recovered": {}}
        
        # Restore spell slots
        for level, total in self.spell_slots_total.items():
            old_slots = self.spell_slots_remaining.get(level, 0)
            self.spell_slots_remaining[level] = total
            result["spell_slots_recovered"][level] = total - old_slots
        
        # Reduce exhaustion by 1
        if self.exhaustion_level > 0:
            self.exhaustion_level -= 1
        
        self.last_long_rest = datetime.now().isoformat()
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "experience_points": self.experience_points,
            "hit_points": {
                "current": self.current_hit_points,
                "temporary": self.temporary_hit_points,
                "max_modifier": self.hit_point_maximum_modifier
            },
            "spell_slots": {
                "total": self.spell_slots_total,
                "remaining": self.spell_slots_remaining
            },
            "spells": {
                "known": self.spells_known,
                "prepared": self.spells_prepared,
                "ritual_book": self.ritual_book_spells
            },
            "equipment": {
                "armor": self.armor,
                "shield": self.shield,
                "weapons": self.weapons,
                "items": self.equipment,
                "magical_items": self.magical_items,
                "attuned": self.attuned_items
            },
            "currency": self.currency,
            "conditions": {
                "active": self.active_conditions,
                "exhaustion": self.exhaustion_level
            },
            "action_economy": {
                "actions_used": self.actions_used,
                "bonus_actions_used": self.bonus_actions_used,
                "reactions_used": self.reactions_used
            },
            "notes": self.notes,
            "timestamps": {
                "last_updated": self.last_updated,
                "last_long_rest": self.last_long_rest,
                "last_short_rest": self.last_short_rest
            }
        }