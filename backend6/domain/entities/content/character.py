from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from ..value_objects.ability_score import AbilityScore
from ..value_objects.proficiency import ProficiencyLevel
from ..value_objects.alignment import Alignment
from .generated_content import GeneratedContent


@dataclass
class CharacterState:
    """
    Pure entity representing character's current gameplay state.
    Contains only data and simple getters - no business logic.
    """
    
    # Health and Resources
    current_hit_points: int = 0
    temporary_hit_points: int = 0
    hit_dice_remaining: Dict[str, int] = field(default_factory=dict)
    
    # Spellcasting State
    spell_slots_remaining: Dict[int, int] = field(default_factory=dict)
    spells_prepared: List[str] = field(default_factory=list)
    
    # Action Economy
    actions_used: int = 0
    bonus_actions_used: int = 0
    reactions_used: int = 0
    
    # Conditions and Effects
    active_conditions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    exhaustion_level: int = 0
    
    # Equipment State
    armor: Optional[str] = None
    shield: bool = False
    attuned_items: List[str] = field(default_factory=list)
    
    # Currency
    currency: Dict[str, int] = field(default_factory=lambda: {
        "copper": 0, "silver": 0, "electrum": 0, "gold": 0, "platinum": 0
    })
    
    # Session Tracking
    last_long_rest: Optional[datetime] = None
    last_short_rest: Optional[datetime] = None
    notes: Dict[str, str] = field(default_factory=dict)


@dataclass
class Character:
    """
    Core Character entity with generated content support for the Creative Content Framework.
    
    This is the heart of the domain model - a clean representation of what
    a character IS. It combines immutable character build aspects with 
    current state that can change during gameplay.
    
    The entity follows Clean Architecture principles by containing only data
    and simple data access methods, with no business logic.
    """
    
    # === BASIC IDENTITY ===
    name: str = ""
    species: str = ""
    species_variants: List[str] = field(default_factory=list)
    lineage: Optional[str] = None
    background: str = ""
    alignment: Optional[Alignment] = None
    
    # === CHARACTER CLASSES ===
    character_classes: Dict[str, int] = field(default_factory=dict)  # {"Fighter": 3, "Wizard": 2}
    subclasses: Dict[str, str] = field(default_factory=dict)  # {"Fighter": "Champion"}
    
    # === ABILITY SCORES ===
    # Using individual fields for type safety and easier access
    strength: AbilityScore = field(default_factory=lambda: AbilityScore(10))
    dexterity: AbilityScore = field(default_factory=lambda: AbilityScore(10))
    constitution: AbilityScore = field(default_factory=lambda: AbilityScore(10))
    intelligence: AbilityScore = field(default_factory=lambda: AbilityScore(10))
    wisdom: AbilityScore = field(default_factory=lambda: AbilityScore(10))
    charisma: AbilityScore = field(default_factory=lambda: AbilityScore(10))
    
    # === PROFICIENCIES ===
    skill_proficiencies: Dict[str, ProficiencyLevel] = field(default_factory=dict)
    saving_throw_proficiencies: Dict[str, ProficiencyLevel] = field(default_factory=dict)
    weapon_proficiencies: Set[str] = field(default_factory=set)
    armor_proficiencies: Set[str] = field(default_factory=set)
    tool_proficiencies: Dict[str, ProficiencyLevel] = field(default_factory=dict)
    languages: Set[str] = field(default_factory=set)
    
    # === FEATURES AND TRAITS ===
    species_traits: Dict[str, Any] = field(default_factory=dict)
    class_features: Dict[str, Any] = field(default_factory=dict)
    background_feature: str = ""
    feats: List[str] = field(default_factory=list)
    
    # === GENERATED CONTENT SUPPORT ===
    generated_content: List[GeneratedContent] = field(default_factory=list)
    custom_content_ids: Set[str] = field(default_factory=set)  # Track which content is custom
    
    # === CURRENT STATE ===
    maximum_hit_points: int = 0
    experience_points: int = 0
    state: CharacterState = field(default_factory=CharacterState)
    
    # === SPELLCASTING ===
    spellcasting_ability: Optional[str] = None
    spellcasting_classes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    ritual_casting_classes: Dict[str, bool] = field(default_factory=dict)
    spell_slots: Dict[int, int] = field(default_factory=dict)  # spell level -> slots
    spells_known: Dict[str, List[str]] = field(default_factory=dict)  # class -> spell list
    
    # === EQUIPMENT ===
    equipment: List[Dict[str, Any]] = field(default_factory=list)
    
    # === METADATA ===
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    player_name: str = ""
    campaign: str = ""
    sources_used: Set[str] = field(default_factory=set)
    
    # === COMPUTED PROPERTIES ===
    
    @property
    def total_level(self) -> int:
        """Calculate total character level from all classes."""
        return sum(self.character_classes.values()) if self.character_classes else 1
    
    @property
    def primary_class(self) -> str:
        """Determine primary class (highest level class)."""
        if not self.character_classes:
            return ""
        return max(self.character_classes.items(), key=lambda x: x[1])[0]
    
    @property
    def proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on total level."""
        level = self.total_level
        if level >= 17:
            return 6
        elif level >= 13:
            return 5
        elif level >= 9:
            return 4
        elif level >= 5:
            return 3
        else:
            return 2
    
    @property
    def is_multiclass(self) -> bool:
        """Check if character has levels in multiple classes."""
        return len(self.character_classes) > 1
    
    @property
    def is_spellcaster(self) -> bool:
        """Check if character has any spellcasting abilities."""
        return bool(self.spellcasting_classes)
    
    @property
    def has_generated_content(self) -> bool:
        """Check if character uses any generated content."""
        return len(self.generated_content) > 0
    
    @property
    def armor_class(self) -> int:
        """Calculate armor class including equipment and bonuses."""
        base_ac = 10 + self.get_ability_modifier("dexterity")
        # Equipment modifiers would be calculated here
        return base_ac
    
    @property
    def initiative_modifier(self) -> int:
        """Calculate initiative modifier."""
        return self.get_ability_modifier("dexterity")
    
    @property
    def passive_perception(self) -> int:
        """Calculate passive Perception score."""
        return 10 + self.get_skill_modifier("perception")
    
    @property
    def speed(self) -> int:
        """Get character's movement speed."""
        # Base speed from species, modified by conditions/equipment
        base_speed = self._get_base_speed()
        return base_speed
    
    # === GENERATED CONTENT METHODS ===
    
    def add_generated_content(self, content: GeneratedContent) -> None:
        """Add generated content to character."""
        if content not in self.generated_content:
            self.generated_content.append(content)
            self.custom_content_ids.add(content.id)
            self.last_modified = datetime.now()
    
    def remove_generated_content(self, content_id: str) -> bool:
        """Remove generated content from character."""
        for i, content in enumerate(self.generated_content):
            if content.id == content_id:
                del self.generated_content[i]
                self.custom_content_ids.discard(content_id)
                self.last_modified = datetime.now()
                return True
        return False
    
    def get_generated_content_by_type(self, content_type: str) -> List[GeneratedContent]:
        """Get all generated content of a specific type."""
        return [
            content for content in self.generated_content 
            if content.content_type.value == content_type
        ]
    
    def has_custom_content(self, content_id: str) -> bool:
        """Check if character uses specific custom content."""
        return content_id in self.custom_content_ids
    
    # === DATA ACCESS METHODS ===
    
    def get_ability_score(self, ability: str) -> AbilityScore:
        """Get the AbilityScore object for a specific ability."""
        ability_map = {
            "strength": self.strength, "str": self.strength,
            "dexterity": self.dexterity, "dex": self.dexterity,
            "constitution": self.constitution, "con": self.constitution,
            "intelligence": self.intelligence, "int": self.intelligence,
            "wisdom": self.wisdom, "wis": self.wisdom,
            "charisma": self.charisma, "cha": self.charisma
        }
        return ability_map.get(ability.lower(), AbilityScore(10))
    
    def get_ability_modifier(self, ability: str) -> int:
        """Get modifier for a specific ability."""
        return self.get_ability_score(ability).modifier
    
    def get_ability_score_value(self, ability: str) -> int:
        """Get the total score value for a specific ability."""
        return self.get_ability_score(ability).total_score
    
    def has_class(self, class_name: str) -> bool:
        """Check if character has levels in a specific class."""
        return class_name in self.character_classes and self.character_classes[class_name] > 0
    
    def get_class_level(self, class_name: str) -> int:
        """Get character's level in a specific class."""
        return self.character_classes.get(class_name, 0)
    
    def get_skill_modifier(self, skill: str) -> int:
        """Calculate skill modifier including proficiency bonus."""
        # Map skills to their associated abilities
        skill_abilities = {
            "acrobatics": "dexterity",
            "animal_handling": "wisdom",
            "arcana": "intelligence",
            "athletics": "strength",
            "deception": "charisma",
            "history": "intelligence",
            "insight": "wisdom",
            "intimidation": "charisma",
            "investigation": "intelligence",
            "medicine": "wisdom",
            "nature": "intelligence",
            "perception": "wisdom",
            "performance": "charisma",
            "persuasion": "charisma",
            "religion": "intelligence",
            "sleight_of_hand": "dexterity",
            "stealth": "dexterity",
            "survival": "wisdom"
        }
        
        ability = skill_abilities.get(skill.lower(), "wisdom")
        base_modifier = self.get_ability_modifier(ability)
        
        # Add proficiency bonus if proficient
        proficiency_level = self.skill_proficiencies.get(skill, ProficiencyLevel.NONE)
        proficiency_bonus = self.proficiency_bonus * proficiency_level.multiplier
        
        return base_modifier + proficiency_bonus
    
    def get_saving_throw_modifier(self, ability: str) -> int:
        """Calculate saving throw modifier including proficiency bonus."""
        base_modifier = self.get_ability_modifier(ability)
        proficiency_level = self.saving_throw_proficiencies.get(ability, ProficiencyLevel.NONE)
        proficiency_bonus = self.proficiency_bonus * proficiency_level.multiplier
        
        return base_modifier + proficiency_bonus
    
    # === MUTATION METHODS (for use by domain services) ===
    
    def update_ability_score(self, ability: str, new_score: AbilityScore) -> None:
        """Update an ability score."""
        ability_attrs = {
            "strength": "strength", "str": "strength",
            "dexterity": "dexterity", "dex": "dexterity", 
            "constitution": "constitution", "con": "constitution",
            "intelligence": "intelligence", "int": "intelligence",
            "wisdom": "wisdom", "wis": "wisdom",
            "charisma": "charisma", "cha": "charisma"
        }
        
        attr_name = ability_attrs.get(ability.lower())
        if attr_name:
            setattr(self, attr_name, new_score)
            self.last_modified = datetime.now()
    
    def add_class_level(self, class_name: str, levels: int = 1) -> None:
        """Add levels to a class."""
        current_level = self.character_classes.get(class_name, 0)
        self.character_classes[class_name] = current_level + levels
        self.last_modified = datetime.now()
    
    def set_proficiency(self, proficiency_type: str, item: str, level: ProficiencyLevel) -> None:
        """Set proficiency level for an item."""
        if proficiency_type == "skill":
            self.skill_proficiencies[item] = level
        elif proficiency_type == "saving_throw":
            self.saving_throw_proficiencies[item] = level
        elif proficiency_type == "tool":
            self.tool_proficiencies[item] = level
        elif proficiency_type == "weapon":
            if level != ProficiencyLevel.NONE:
                self.weapon_proficiencies.add(item)
            else:
                self.weapon_proficiencies.discard(item)
        elif proficiency_type == "armor":
            if level != ProficiencyLevel.NONE:
                self.armor_proficiencies.add(item)
            else:
                self.armor_proficiencies.discard(item)
        elif proficiency_type == "language":
            if level != ProficiencyLevel.NONE:
                self.languages.add(item)
            else:
                self.languages.discard(item)
        
        self.last_modified = datetime.now()
    
    # === UTILITY METHODS ===
    
    def _get_base_speed(self) -> int:
        """Get base speed from species (would be implemented by domain services)."""
        return 30  # Default human speed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary representation."""
        return {
            # Basic identity
            "name": self.name,
            "species": self.species,
            "species_variants": self.species_variants,
            "lineage": self.lineage,
            "background": self.background,
            "alignment": {
                "ethical": self.alignment.ethical,
                "moral": self.alignment.moral
            } if self.alignment else None,
            
            # Classes
            "character_classes": self.character_classes,
            "subclasses": self.subclasses,
            
            # Ability scores
            "ability_scores": {
                "strength": self.strength.total_score,
                "dexterity": self.dexterity.total_score,
                "constitution": self.constitution.total_score,
                "intelligence": self.intelligence.total_score,
                "wisdom": self.wisdom.total_score,
                "charisma": self.charisma.total_score
            },
            
            # Generated content
            "generated_content": [content.to_dict() for content in self.generated_content],
            "custom_content_ids": list(self.custom_content_ids),
            
            # Computed values
            "total_level": self.total_level,
            "primary_class": self.primary_class,
            "proficiency_bonus": self.proficiency_bonus,
            "has_generated_content": self.has_generated_content
        }
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Get a summary of character information."""
        return {
            "name": self.name,
            "level": self.total_level,
            "class": self.primary_class,
            "species": self.species,
            "hit_points": f"{self.state.current_hit_points}/{self.maximum_hit_points}",
            "armor_class": self.armor_class,
            "proficiency_bonus": self.proficiency_bonus,
            "generated_content_count": len(self.generated_content)
        }
    
    def __str__(self) -> str:
        """String representation of character."""
        level_str = f"Level {self.total_level}"
        if self.is_multiclass:
            class_levels = [f"{cls} {lvl}" for cls, lvl in self.character_classes.items()]
            level_str = f"Level {self.total_level} ({'/'.join(class_levels)})"
        
        custom_note = " (with custom content)" if self.has_generated_content else ""
        return f"{self.name}, {level_str} {self.species} {self.primary_class}{custom_note}"
    
    def __repr__(self) -> str:
        """Developer representation of character."""
        return f"Character(name='{self.name}', species='{self.species}', level={self.total_level}, generated_content={len(self.generated_content)})"