"""Character combat-related models."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum

from ..shared.enums import DamageType
from ..base import BaseModelWithAudit

class Attack(BaseModel):
    """Represents a weapon or spell attack."""
    name: str = Field(..., description="Name of the attack")
    attack_type: str = Field(..., description="Type of attack (melee, ranged, spell)")
    weapon_type: Optional[str] = Field(None, description="Type of weapon if applicable")
    proficient: bool = Field(True, description="Whether proficiency bonus applies")
    damage_dice: str = Field(..., description="Damage dice expression (e.g., '2d6')")
    damage_type: DamageType = Field(..., description="Type of damage dealt")
    bonus_damage: Optional[str] = Field(None, description="Additional damage (e.g., '1d6 fire')")
    range: Optional[str] = Field(None, description="Range of the attack (e.g., '30/120')")
    properties: List[str] = Field(default_factory=list, description="Special properties")
    notes: Optional[str] = Field(None, description="Additional notes")

class DefenseType(str, Enum):
    """Types of defenses a character might have."""
    RESISTANCE = "resistance"
    IMMUNITY = "immunity"
    VULNERABILITY = "vulnerability"
    CONDITION_IMMUNITY = "condition_immunity"

class Defense(BaseModel):
    """Represents a character's defense."""
    type: DefenseType = Field(..., description="Type of defense")
    source: str = Field(..., description="Source of the defense")
    value: str = Field(..., description="What is being defended against")
    notes: Optional[str] = Field(None, description="Additional notes")
    temporary: bool = Field(False, description="Whether this is a temporary effect")

class CombatState(BaseModelWithAudit):
    """Current combat-related state of a character."""
    
    # Core combat stats
    armor_class: int = Field(10, description="Current armor class")
    initiative_bonus: int = Field(0, description="Total initiative bonus")
    speed: Dict[str, int] = Field(
        default_factory=lambda: {"walk": 30},
        description="Movement speeds by type"
    )
    
    # Health tracking
    current_hp: int = Field(0, description="Current hit points")
    temp_hp: int = Field(0, description="Temporary hit points")
    max_hp: int = Field(0, description="Maximum hit points")
    death_saves: Dict[str, int] = Field(
        default_factory=lambda: {"successes": 0, "failures": 0},
        description="Death saving throw tracking"
    )
    
    # Defenses and immunities
    defenses: List[Defense] = Field(
        default_factory=list,
        description="Character's current defenses"
    )
    
    # Combat actions
    attacks: List[Attack] = Field(
        default_factory=list,
        description="Available attacks"
    )
    actions_used: Dict[str, bool] = Field(
        default_factory=lambda: {
            "action": False,
            "bonus_action": False,
            "reaction": False
        },
        description="Track used actions"
    )
    
    # Combat conditions
    conditions: List[str] = Field(
        default_factory=list,
        description="Active conditions"
    )
    exhaustion_level: int = Field(
        0, 
        description="Current exhaustion level",
        ge=0,
        le=10
    )
    
    # Combat resources
    hit_dice: Dict[str, int] = Field(
        default_factory=dict,
        description="Available hit dice by type"
    )
    
    # Combat modifiers
    active_effects: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Active combat effects"
    )
    
    def take_damage(self, amount: int, damage_type: Optional[DamageType] = None) -> Dict[str, int]:
        """Process incoming damage."""
        damage_dealt = {"temp_hp": 0, "hp": 0}
        
        # Apply to temporary HP first
        if self.temp_hp > 0:
            damage_to_temp = min(amount, self.temp_hp)
            self.temp_hp -= damage_to_temp
            amount -= damage_to_temp
            damage_dealt["temp_hp"] = damage_to_temp
        
        # Then to regular HP
        if amount > 0:
            self.current_hp = max(0, self.current_hp - amount)
            damage_dealt["hp"] = amount
        
        # Check for unconsciousness
        if self.current_hp <= 0:
            self.conditions.append("unconscious")
        
        return damage_dealt
    
    def heal(self, amount: int) -> int:
        """Heal the character."""
        if amount <= 0:
            return 0
        
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        
        # Remove unconscious condition if healed above 0
        if self.current_hp > 0 and "unconscious" in self.conditions:
            self.conditions.remove("unconscious")
        
        return self.current_hp - old_hp
    
    def add_temp_hp(self, amount: int) -> int:
        """Add temporary hit points."""
        if amount <= 0:
            return 0
        
        # Temp HP doesn't stack, take the higher value
        self.temp_hp = max(self.temp_hp, amount)
        return self.temp_hp
    
    def reset_combat(self) -> None:
        """Reset combat-specific state."""
        self.actions_used = {
            "action": False,
            "bonus_action": False,
            "reaction": False
        }
        self.death_saves = {"successes": 0, "failures": 0}
        
        # Clear temporary effects
        self.active_effects = []
        self.defenses = [d for d in self.defenses if not d.temporary]
    
    def make_death_save(self, roll: int) -> Dict[str, Any]:
        """Process a death saving throw."""
        result = {
            "roll": roll,
            "critical": False,
            "stabilized": False,
            "dead": False
        }
        
        if roll == 20:
            # Natural 20 regains 1 HP
            result["critical"] = True
            self.heal(1)
            self.death_saves = {"successes": 0, "failures": 0}
            result["stabilized"] = True
        elif roll == 1:
            # Natural 1 counts as two failures
            self.death_saves["failures"] += 2
        else:
            # Normal roll
            if roll >= 10:
                self.death_saves["successes"] += 1
            else:
                self.death_saves["failures"] += 1
        
        # Check for stabilization or death
        if self.death_saves["successes"] >= 3:
            result["stabilized"] = True
            self.death_saves = {"successes": 0, "failures": 0}
            self.conditions = [c for c in self.conditions if c != "unconscious"]
            self.conditions.append("stable")
        elif self.death_saves["failures"] >= 3:
            result["dead"] = True
        
        return result

class CombatAction(BaseModel):
    """Represents a combat action the character can take."""
    name: str = Field(..., description="Name of the action")
    type: str = Field(..., description="Type of action (action, bonus, reaction)")
    source: str = Field(..., description="Source of the action (class, race, etc.)")
    description: str = Field(..., description="What the action does")
    requirements: Optional[str] = Field(None, description="Requirements to use the action")
    resource_cost: Optional[str] = Field(None, description="Resources consumed by the action")
    cooldown: Optional[str] = Field(None, description="How often the action can be used")
