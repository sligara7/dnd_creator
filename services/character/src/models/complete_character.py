"""
Complete Character Sheet Models

These models represent the complete D&D 5e 2024 character sheet format, including
all character components required by the system:
- Character identity and origin
- Core statistics
- Combat and health
- Actions and traits
- Equipment and inventory
- Spellcasting (if applicable)
- Additional details
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum, auto
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from uuid import UUID
from math import floor
from typing import Set

class DamageType(str, Enum):
    """D&D 5e damage types."""
    SLASHING = "slashing"
    PIERCING = "piercing"
    BLUDGEONING = "bludgeoning"
    POISON = "poison"
    ACID = "acid"
    FIRE = "fire"
    COLD = "cold"
    RADIANT = "radiant"
    NECROTIC = "necrotic"
    LIGHTNING = "lightning"
    THUNDER = "thunder"
    FORCE = "force"
    PSYCHIC = "psychic"

class WeaponProperty(str, Enum):
    """D&D 5e weapon properties."""
    AMMUNITION = "ammunition"
    FINESSE = "finesse"
    HEAVY = "heavy"
    LIGHT = "light"
    LOADING = "loading"
    RANGE = "range"
    REACH = "reach"
    SPECIAL = "special"
    THROWN = "thrown"
    TWO_HANDED = "two-handed"
    VERSATILE = "versatile"

class InventoryItem(BaseModel):
    """Represents an item in the character's inventory."""
    name: str = Field(..., description="Name of the item")
    quantity: int = Field(1, description="Number of items")
    weight: float = Field(0.0, description="Weight per item in pounds")
    value: Decimal = Field(Decimal('0'), description="Value per item in gold pieces")
    description: Optional[str] = Field(None, description="Item description")
    equipped: bool = Field(False, description="Whether the item is equipped")
    attunement_required: bool = Field(False, description="Whether attunement is required")
    attuned: bool = Field(False, description="Whether currently attuned")
    notes: Optional[str] = Field(None, description="Additional notes about the item")
    tags: List[str] = Field(default_factory=list, description="Item tags/categories")

class Equipment(BaseModel):
    """Complete equipment and inventory management."""
    # Inventory
    inventory: List[InventoryItem] = Field(
        default_factory=list,
        description="List of all items in inventory"
    )
    
    # Currency tracking (in copper pieces)
    currency: Dict[str, int] = Field(
        default_factory=lambda: {
            "cp": 0,  # Copper pieces
            "sp": 0,  # Silver pieces
            "ep": 0,  # Electrum pieces
            "gp": 0,  # Gold pieces
            "pp": 0   # Platinum pieces
        },
        description="Currency amounts by type"
    )
    
    # Carrying capacity
    strength_score: int = Field(..., description="Character's Strength score for capacity calculation")
    size_multiplier: float = Field(
        1.0,
        description="Size-based carrying capacity multiplier"
    )
    capacity_multiplier: float = Field(
        1.0,
        description="Additional carrying capacity multiplier (e.g., Powerful Build)"
    )
    
    @property
    def carrying_capacity(self) -> float:
        """Calculate maximum carrying capacity in pounds."""
        return self.strength_score * 15 * self.size_multiplier * self.capacity_multiplier
    
    @property
    def current_load(self) -> float:
        """Calculate current carried weight in pounds."""
        return sum(item.weight * item.quantity for item in self.inventory)
    
    @property
    def total_currency_weight(self) -> float:
        """Calculate weight of carried currency (50 coins = 1 pound)."""
        total_coins = sum(self.currency.values())
        return total_coins / 50
    
    @property
    def is_encumbered(self) -> bool:
        """Check if character is encumbered."""
        total_weight = self.current_load + self.total_currency_weight
        return total_weight > (self.carrying_capacity / 2)
    
    @property
    def is_heavily_encumbered(self) -> bool:
        """Check if character is heavily encumbered."""
        total_weight = self.current_load + self.total_currency_weight
        return total_weight > self.carrying_capacity

class Attack(BaseModel):
    """Represents a weapon attack."""
    name: str = Field(..., description="Name of the attack")
    weapon_type: str = Field(..., description="Type of weapon (simple, martial, natural)")
    damage_dice: str = Field(..., description="Damage dice expression (e.g., '1d8')")
    damage_type: DamageType = Field(..., description="Type of damage dealt")
    properties: List[WeaponProperty] = Field(
        default_factory=list,
        description="Weapon properties"
    )
    
    # Attack bonuses
    bonus_to_hit: int = Field(0, description="Additional bonus to hit")
    bonus_to_damage: int = Field(0, description="Additional bonus to damage")
    
    # Ranged weapon properties
    range_normal: Optional[int] = Field(None, description="Normal range in feet")
    range_maximum: Optional[int] = Field(None, description="Maximum range in feet")
    ammunition_type: Optional[str] = Field(None, description="Type of ammunition used")
    
    # Versatile weapons
    versatile_damage_dice: Optional[str] = Field(
        None,
        description="Damage when used two-handed (for versatile weapons)"
    )
    
    # Special effects
    special_effects: List[str] = Field(
        default_factory=list,
        description="Special effects or abilities"
    )
    notes: Optional[str] = Field(None, description="Additional notes about the attack")

class DeathSaves(BaseModel):
    """Tracks death saving throw progress."""
    successes: int = Field(
        0,
        description="Number of successful death saves (3 needed to stabilize)",
        ge=0,
        le=3
    )
    failures: int = Field(
        0,
        description="Number of failed death saves (3 causes death)",
        ge=0,
        le=3
    )
    stabilized: bool = Field(
        False,
        description="Whether the character has been stabilized"
    )
    last_roll: Optional[int] = Field(
        None,
        description="The last death save roll (nat 20 = heal 1 HP, nat 1 = 2 failures)"
    )
    
    def reset(self) -> None:
        """Reset death saving throws."""
        self.successes = 0
        self.failures = 0
        self.stabilized = False
        self.last_roll = None
    
    def add_roll(self, roll: int) -> Tuple[str, Optional[str]]:
        """Add a death saving throw roll and return the result.
        
        Args:
            roll: The d20 roll result
            
        Returns:
            Tuple of (result_type, effect)
            result_type: 'success', 'failure', 'critical_success', or 'critical_failure'
            effect: Additional effect description if any
        """
        self.last_roll = roll
        
        if roll == 20:
            self.stabilized = True
            return 'critical_success', 'Regain 1 hit point'
        elif roll == 1:
            self.failures += 2
            return 'critical_failure', 'Count as two failures'
        elif roll >= 10:
            self.successes += 1
            if self.successes >= 3:
                self.stabilized = True
            return 'success', None
        else:
            self.failures += 1
            return 'failure', None
    
    @property
    def is_dead(self) -> bool:
        """Check if character has died from failed saves."""
        return self.failures >= 3
    
    @property
    def is_stable(self) -> bool:
        """Check if character is stable."""
        return self.stabilized or self.successes >= 3

class CombatStats(BaseModel):
    """Complete combat statistics for a character."""
    # Core combat stats
    armor_class: int = Field(..., description="Base armor class")
    armor_class_bonus: int = Field(0, description="Additional AC bonuses")
    initiative: int = Field(..., description="Initiative modifier")
    initiative_advantage: bool = Field(False, description="Advantage on initiative rolls")
    speed: Dict[str, int] = Field(
        default_factory=lambda: {"walking": 30},
        description="Movement speeds by type (walking, flying, swimming, etc.)"
    )
    
    # Attack bonuses and proficiencies
    weapon_proficiencies: Set[str] = Field(default_factory=set)
    armor_proficiencies: Set[str] = Field(default_factory=set)
    attack_bonuses: Dict[str, int] = Field(default_factory=dict)
    damage_bonuses: Dict[str, int] = Field(default_factory=dict)
    
    # Combat options and resources
    actions_per_turn: int = Field(1, description="Number of actions per turn")
    bonus_actions_per_turn: int = Field(1, description="Number of bonus actions per turn")
    reactions_per_turn: int = Field(1, description="Number of reactions per turn")
    special_abilities: List[str] = Field(default_factory=list)
    
    @property
    def total_ac(self) -> int:
        """Calculate total armor class including bonuses."""
        return self.armor_class + self.armor_class_bonus

class Condition(BaseModel):
    """Represents a condition affecting the character."""
    name: str = Field(..., description="Name of the condition")
    level: Optional[int] = Field(None, description="Level of the condition (e.g., exhaustion)")
    source: str = Field(..., description="What caused this condition")
    duration: Optional[str] = Field(None, description="How long the condition lasts")
    effects: List[str] = Field(default_factory=list, description="Mechanical effects of the condition")
    notes: Optional[str] = Field(None, description="Additional details about the condition")

class HitDice(BaseModel):
    """Tracks hit dice usage and recovery."""
    die_type: str = Field(..., description="Type of hit die (d6, d8, d10, d12)")
    total: int = Field(..., description="Total number of hit dice of this type")
    used: int = Field(0, description="Number of hit dice used")
    recovery_rate: int = Field(
        default=2,
        description="Number of hit dice recovered on long rest"
    )
    
    @property
    def available(self) -> int:
        """Calculate number of hit dice currently available."""
        return self.total - self.used

class SpellcastingStats(BaseModel):
    """Core spellcasting statistics and resources."""
    ability: Optional[str] = Field(None, description="Primary spellcasting ability")
    spell_attack_bonus: int = Field(0, description="Bonus to spell attack rolls")
    spell_save_dc: int = Field(0, description="Save DC for your spells")
    spell_slots_max: Dict[int, int] = Field(
        default_factory=dict,
        description="Maximum spell slots by level"
    )
    spell_slots_current: Dict[int, int] = Field(
        default_factory=dict,
        description="Current available spell slots by level"
    )
    concentration_active: bool = Field(
        False,
        description="Whether currently concentrating on a spell"
    )
    ritual_casting: bool = Field(
        False,
        description="Whether able to cast spells as rituals"
    )
    spellcasting_focus: Optional[str] = Field(
        None,
        description="Type of spellcasting focus used"
    )

class AlignmentType(str, Enum):
    """D&D 5e 2024 alignment types."""
    LAWFUL_GOOD = "Lawful Good"
    NEUTRAL_GOOD = "Neutral Good"
    CHAOTIC_GOOD = "Chaotic Good"
    LAWFUL_NEUTRAL = "Lawful Neutral"
    TRUE_NEUTRAL = "True Neutral"
    CHAOTIC_NEUTRAL = "Chaotic Neutral"
    LAWFUL_EVIL = "Lawful Evil"
    NEUTRAL_EVIL = "Neutral Evil"
    CHAOTIC_EVIL = "Chaotic Evil"

class PersonalityTraits(BaseModel):
    """Character personality traits, ideals, bonds, and flaws."""
    traits: List[str] = Field(default_factory=list, description="Character's personality traits")
    ideals: List[str] = Field(default_factory=list, description="Character's ideals and beliefs")
    bonds: List[str] = Field(default_factory=list, description="Character's bonds and connections")
    flaws: List[str] = Field(default_factory=list, description="Character's flaws and weaknesses")
    notes: Optional[str] = Field(None, description="Additional personality notes")

class Appearance(BaseModel):
    """Character physical appearance details."""
    age: Optional[int] = Field(None, description="Character's age in years")
    height: Optional[str] = Field(None, description="Character's height (e.g., '6'0\"')")
    weight: Optional[str] = Field(None, description="Character's weight (e.g., '180 lbs')")
    eyes: Optional[str] = Field(None, description="Eye color and description")
    skin: Optional[str] = Field(None, description="Skin tone and description")
    hair: Optional[str] = Field(None, description="Hair color and style")
    other: Optional[str] = Field(None, description="Other notable features")

class AuditEntry(BaseModel):
    """Record of changes made to the character sheet."""
    timestamp: datetime
    action: str = Field(..., description="Type of change made")
    fields_changed: List[str] = Field(default_factory=list, description="Fields that were modified")
    notes: Optional[str] = Field(None, description="Additional context about the change")
    username: Optional[str] = Field(None, description="User who made the change")

class CharacterIdentity(BaseModel):
    """
    Complete character identity and origin information.
    This includes all core character defining elements.
    """
    # Basic Information
    name: str = Field(..., description="Character's full name")
    player_name: str = Field(..., description="Player's name")
    
    # Character Details
    species: str = Field(..., description="Character's species/race")
    class_levels: Dict[str, int] = Field(
        ..., 
        description="Character's class levels (e.g., {'Fighter': 5, 'Wizard': 2})"
    )
    background: str = Field(..., description="Character's background")
    alignment: AlignmentType = Field(..., description="Character's alignment")
    
    # Experience and Inspiration
    xp: int = Field(0, description="Current experience points")
    xp_level_up: Optional[int] = Field(None, description="XP needed for next level")
    heroic_inspiration: bool = Field(False, description="Whether the character has inspiration")
    
    # Additional Details
    personality: PersonalityTraits = Field(
        default_factory=PersonalityTraits,
        description="Character's personality traits"
    )
    appearance: Appearance = Field(
        default_factory=Appearance,
        description="Character's physical appearance"
    )
    backstory: str = Field("", description="Character's background story")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    last_session: Optional[datetime] = Field(None, description="Last played session")
    version: str = Field("1.0", description="Character sheet version")
    user_modified: bool = Field(False, description="Whether the sheet has been manually modified")
    audit_trail: List[AuditEntry] = Field(default_factory=list)
    
    @property
    def total_level(self) -> int:
        """Calculate total character level from class levels."""
        return sum(self.class_levels.values())
    
    @validator('class_levels')
    def validate_class_levels(cls, v):
        """Validate class levels are positive integers."""
        for class_name, level in v.items():
            if not isinstance(level, int) or level < 1:
                raise ValueError(f"Invalid level {level} for class {class_name}")
        return v
    
    @validator('xp')
    def validate_xp(cls, v):
        """Validate XP is non-negative."""
        if v < 0:
            raise ValueError("XP cannot be negative")
        return v
    
    def update_audit_trail(self, action: str, fields: List[str], notes: Optional[str] = None,
                          username: Optional[str] = None) -> None:
        """Add an entry to the audit trail."""
        self.audit_trail.append(
            AuditEntry(
                timestamp=datetime.utcnow(),
                action=action,
                fields_changed=fields,
                notes=notes,
                username=username
            )
        )
        self.last_updated = datetime.utcnow()
        self.user_modified = True

class ProficiencyType(str, Enum):
    """Types of proficiency available in D&D 5e 2024."""
    NONE = "none"
    PROFICIENT = "proficient"
    EXPERT = "expert"

class AbilityType(str, Enum):
    """The six ability scores in D&D 5e."""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"

class Skill(BaseModel):
    """Represents a skill and its proficiency level."""
    name: str = Field(..., description="Name of the skill")
    ability: AbilityType = Field(..., description="Ability score this skill is based on")
    proficiency: ProficiencyType = Field(default=ProficiencyType.NONE)
    bonus: int = Field(default=0, description="Additional bonus beyond ability and proficiency")
    notes: Optional[str] = Field(None, description="Additional notes about skill usage")

class Tool(BaseModel):
    """Represents a tool proficiency."""
    name: str = Field(..., description="Name of the tool")
    category: str = Field(..., description="Category of tool (artisan's tools, gaming set, etc.)")
    proficiency: ProficiencyType = Field(default=ProficiencyType.PROFICIENT)
    ability_options: List[AbilityType] = Field(
        default_factory=list,
        description="Abilities that can be used with this tool"
    )
    notes: Optional[str] = Field(None, description="Special notes about tool usage")

class Abilities(BaseModel):
    """Complete ability scores and related proficiencies for a character."""
    
    # Base ability scores
    scores: Dict[AbilityType, int] = Field(
        ...,
        description="Base ability scores before modifications"
    )
    score_improvements: Dict[AbilityType, int] = Field(
        default_factory=lambda: {ability: 0 for ability in AbilityType},
        description="Permanent improvements to ability scores"
    )
    score_modifiers: Dict[AbilityType, int] = Field(
        default_factory=lambda: {ability: 0 for ability in AbilityType},
        description="Temporary modifiers to ability scores"
    )
    
    # Saving throws
    save_proficiencies: Dict[AbilityType, ProficiencyType] = Field(
        default_factory=lambda: {ability: ProficiencyType.NONE for ability in AbilityType},
        description="Proficiency in ability saving throws"
    )
    save_bonuses: Dict[AbilityType, int] = Field(
        default_factory=lambda: {ability: 0 for ability in AbilityType},
        description="Additional bonuses to saving throws"
    )
    save_advantages: Dict[AbilityType, List[str]] = Field(
        default_factory=lambda: {ability: [] for ability in AbilityType},
        description="Sources of advantage on saving throws"
    )
    
# Skills
    skills: Dict[str, Skill] = Field(
        default_factory=dict,
        description="Character's skills and proficiencies"
    )
    
    # Skill advantages/disadvantages
    skill_advantages: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Sources of advantage on skill checks"
    )
    skill_disadvantages: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Sources of disadvantage on skill checks"
    )
    
    @property
    def passive_perception(self) -> int:
        """Calculate passive perception score.
        Base 10 + perception modifier (with advantage = +5)
        """
        base = 10
        perception_mod = self.get_skill_modifier("perception", self.proficiency_bonus)[0]
        
        # Check for advantage/disadvantage
        has_advantage = "perception" in self.skill_advantages and len(self.skill_advantages["perception"]) > 0
        has_disadvantage = "perception" in self.skill_disadvantages and len(self.skill_disadvantages["perception"]) > 0
        
        # Add +5 for advantage, -5 for disadvantage if they don't cancel out
        if has_advantage and not has_disadvantage:
            base += 5
        elif has_disadvantage and not has_advantage:
            base -= 5
            
        return base + perception_mod
    
    # Tools and other proficiencies
    tools: List[Tool] = Field(
        default_factory=list,
        description="Tool proficiencies"
    )
    languages: List[str] = Field(
        default_factory=list,
        description="Known languages"
    )
    
    # Methods to calculate derived statistics
    def get_ability_modifier(self, ability: AbilityType) -> int:
        """Calculate the modifier for an ability score."""
        total_score = (
            self.scores[ability] +
            self.score_improvements[ability] +
            self.score_modifiers[ability]
        )
        return floor((total_score - 10) / 2)
    
    def get_save_modifier(self, ability: AbilityType, proficiency_bonus: int) -> Tuple[int, bool, List[str]]:
        """Calculate saving throw modifier and any advantage/disadvantage.
        
        Returns:
        - Total modifier
        - Whether proficiency applies
        - List of advantage sources (empty if no advantage)
        """
        base_mod = self.get_ability_modifier(ability)
        
        # Add proficiency if applicable
        proficiency = self.save_proficiencies[ability]
        if proficiency == ProficiencyType.PROFICIENT:
            base_mod += proficiency_bonus
        elif proficiency == ProficiencyType.EXPERT:
            base_mod += proficiency_bonus * 2
        
        # Add any extra bonuses
        total_mod = base_mod + self.save_bonuses[ability]
        
        return (total_mod, proficiency != ProficiencyType.NONE, self.save_advantages[ability])
    
    def get_skill_modifier(self, skill_name: str, proficiency_bonus: int) -> Tuple[int, bool, Optional[str]]:
        """Calculate skill check modifier and proficiency status.
        
        Returns:
        - Total modifier
        - Whether proficiency applies
        - Any relevant notes
        """
        skill = self.skills[skill_name]
        base_mod = self.get_ability_modifier(skill.ability)
        
        # Add proficiency if applicable
        if skill.proficiency == ProficiencyType.PROFICIENT:
            base_mod += proficiency_bonus
        elif skill.proficiency == ProficiencyType.EXPERT:
            base_mod += proficiency_bonus * 2
        
        # Add any extra bonuses
        total_mod = base_mod + skill.bonus
        
        return (total_mod, skill.proficiency != ProficiencyType.NONE, skill.notes)
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "scores": {
                    "strength": 16,
                    "dexterity": 14,
                    "constitution": 15,
                    "intelligence": 12,
                    "wisdom": 13,
                    "charisma": 10
                },
                "save_proficiencies": {
                    "strength": "proficient",
                    "constitution": "proficient"
                },
                "skills": {
                    "athletics": {
                        "name": "Athletics",
                        "ability": "strength",
                        "proficiency": "expert"
                    },
                    "intimidation": {
                        "name": "Intimidation",
                        "ability": "charisma",
                        "proficiency": "proficient"
                    }
                },
                "languages": ["Common", "Dwarvish", "Giant"]
            }
        }

class CompleteCharacterSheet(BaseModel):
    """Complete D&D 5e (2024) character sheet."""
    # Core character information
    identity: CharacterIdentity = Field(
        ...,
        description="Character identity and background information"
    )
    abilities: Abilities = Field(
        ...,
        description="Ability scores and related proficiencies"
    )
    
    # Combat and health
    combat: CombatStats = Field(
        ...,
        description="Combat statistics and resources"
    )
    attacks: List[Attack] = Field(
        default_factory=list,
        description="Character's available attacks"
    )
    health: Dict[str, int] = Field(
        default_factory=lambda: {
            "max_hp": 0,
            "current_hp": 0,
            "temporary_hp": 0
        },
        description="Health points and related values"
    )
    death_saves: DeathSaves = Field(
        default_factory=DeathSaves,
        description="Death saving throw tracking"
    )
    hit_dice: Dict[str, HitDice] = Field(
        default_factory=dict,
        description="Hit dice by type (d6, d8, etc.)"
    )
    
    # Equipment and inventory
    equipment: Equipment = Field(
        ...,
        description="Equipment, inventory, and carried items"
    )
    
    # Magic and special abilities
    spellcasting: Optional[SpellcastingStats] = Field(
        None,
        description="Spellcasting information if applicable"
    )
    conditions: List[Condition] = Field(
        default_factory=list,
        description="Active conditions affecting the character"
    )
    
    @property
    def proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on total level."""
        level = self.identity.total_level
        return 2 + ((level - 1) // 4)
    
    @property
    def passive_perception(self) -> int:
        """Get passive perception score."""
        return self.abilities.passive_perception
    
    @property
    def total_hp(self) -> int:
        """Get total current HP including temporary."""
        return self.health["current_hp"] + self.health["temporary_hp"]
    
    def long_rest(self) -> None:
        """Apply the effects of a long rest."""
        # Restore HP
        self.health["current_hp"] = self.health["max_hp"]
        self.health["temporary_hp"] = 0
        
        # Recover hit dice (up to half total)
        for die in self.hit_dice.values():
            recovery = min(die.recovery_rate, die.used)
            die.used -= recovery
        
        # Reset spell slots if applicable
        if self.spellcasting:
            self.spellcasting.spell_slots_current = self.spellcasting.spell_slots_max.copy()
            self.spellcasting.concentration_active = False
        
        # Remove temporary conditions
        self.conditions = [c for c in self.conditions if c.duration != "temporary"]
    
    def short_rest(self, hit_dice_used: Dict[str, int]) -> int:
        """Apply the effects of a short rest.
        
        Args:
            hit_dice_used: Dictionary of hit die type to number used
            
        Returns:
            Total HP recovered
        """
        hp_recovered = 0
        con_mod = self.abilities.get_ability_modifier(AbilityType.CONSTITUTION)
        
        # Use hit dice for healing
        for die_type, count in hit_dice_used.items():
            if die_type not in self.hit_dice:
                continue
                
            die = self.hit_dice[die_type]
            actual_used = min(count, die.available)
            
            # Roll and add Constitution modifier for each die
            for _ in range(actual_used):
                roll = 1  # Replace with actual die roll
                hp_recovered += max(1, roll + con_mod)  # Minimum 1 HP per die
            
            die.used += actual_used
        
        # Apply healing
        self.health["current_hp"] = min(
            self.health["max_hp"],
            self.health["current_hp"] + hp_recovered
        )
        
        return hp_recovered
