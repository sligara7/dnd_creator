from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from .character_state import CharacterState

from ..value_objects.proficiency import ProficiencyLevel
from ..value_objects.ability_score import AbilityScore
from ..value_objects.alignment import Alignment

@dataclass
class Character:
    """
    Core Character entity representing a D&D 5e character.
    
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
    
    # === CURRENT STATE ===
    current_hit_points: int = 0
    maximum_hit_points: int = 0
    temporary_hit_points: int = 0
    experience_points: int = 0

    # === Gameplay State ===
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
    def armor_class_base(self) -> int:
        """Get base armor class (10 + Dex modifier)."""
        return 10 + self.get_ability_modifier("dexterity")
    
    # === STATISTICAL CALCULATIONS ===
    
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
    def passive_investigation(self) -> int:
        """Calculate passive Investigation score."""
        return 10 + self.get_skill_modifier("investigation")
    
    @property
    def passive_insight(self) -> int:
        """Calculate passive Insight score."""
        return 10 + self.get_skill_modifier("insight")
    
    @property
    def speed(self) -> int:
        """Get character's movement speed."""
        # Base speed from species, modified by conditions/equipment
        base_speed = self._get_base_speed()
        # Apply modifications
        return base_speed
    
    def get_attack_bonus(self, weapon_type: str = "melee") -> int:
        """Calculate attack bonus for weapon type."""
        if weapon_type == "melee":
            ability_mod = max(
                self.get_ability_modifier("strength"),
                self.get_ability_modifier("dexterity")  # finesse weapons
            )
        else:  # ranged
            ability_mod = self.get_ability_modifier("dexterity")
        
        return ability_mod + self.proficiency_bonus
    
    def get_spell_attack_bonus(self) -> int:
        """Calculate spell attack bonus."""
        if not self.spellcasting_ability:
            return 0
        ability_mod = self.get_ability_modifier(self.spellcasting_ability)
        return ability_mod + self.proficiency_bonus
    
    def get_spell_save_dc(self) -> int:
        """Calculate spell save DC."""
        if not self.spellcasting_ability:
            return 8
        ability_mod = self.get_ability_modifier(self.spellcasting_ability)
        return 8 + self.proficiency_bonus + ability_mod

    # === DATA ACCESS METHODS ===
    
    def get_ability_score(self, ability: str) -> AbilityScore:
        """
        Get the AbilityScore object for a specific ability.
        
        Args:
            ability: Name of ability (full name or abbreviation)
            
        Returns:
            AbilityScore object for the requested ability
        """
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
        """
        Calculate skill modifier including proficiency bonus.
        
        Args:
            skill: Name of the skill
            
        Returns:
            Total skill modifier (ability modifier + proficiency if applicable)
        """
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
        """
        Calculate saving throw modifier including proficiency bonus.
        
        Args:
            ability: Name of the ability for the saving throw
            
        Returns:
            Total saving throw modifier
        """
        base_modifier = self.get_ability_modifier(ability)
        proficiency_level = self.saving_throw_proficiencies.get(ability, ProficiencyLevel.NONE)
        proficiency_bonus = self.proficiency_bonus * proficiency_level.multiplier
        
        return base_modifier + proficiency_bonus
    
    def has_proficiency(self, proficiency_type: str, item: str) -> bool:
        """
        Check if character has proficiency in a specific item.
        
        Args:
            proficiency_type: Type of proficiency ('skill', 'weapon', 'armor', 'tool', 'language')
            item: Specific item to check
            
        Returns:
            True if character has the proficiency
        """
        if proficiency_type == "skill":
            return self.skill_proficiencies.get(item, ProficiencyLevel.NONE) != ProficiencyLevel.NONE
        elif proficiency_type == "weapon":
            return item in self.weapon_proficiencies
        elif proficiency_type == "armor":
            return item in self.armor_proficiencies
        elif proficiency_type == "tool":
            return self.tool_proficiencies.get(item, ProficiencyLevel.NONE) != ProficiencyLevel.NONE
        elif proficiency_type == "language":
            return item in self.languages
        return False
    
    def get_spell_slots_for_level(self, spell_level: int) -> int:
        """Get number of spell slots for a specific spell level."""
        return self.spell_slots.get(spell_level, 0)
    
    def has_spell(self, spell_name: str, class_name: Optional[str] = None) -> bool:
        """
        Check if character knows a specific spell.
        
        Args:
            spell_name: Name of the spell
            class_name: Optional class to check (if None, checks all classes)
            
        Returns:
            True if character knows the spell
        """
        if class_name:
            return spell_name in self.spells_known.get(class_name, [])
        
        # Check all classes
        for spells in self.spells_known.values():
            if spell_name in spells:
                return True
        return False
    
    def has_feat(self, feat_name: str) -> bool:
        """Check if character has a specific feat."""
        return feat_name in self.feats
    
    def get_class_features_for_class(self, class_name: str) -> Dict[str, Any]:
        """Get all class features for a specific class."""
        return self.class_features.get(class_name, {})
    
    def has_class_feature(self, feature_name: str, class_name: Optional[str] = None) -> bool:
        """
        Check if character has a specific class feature.
        
        Args:
            feature_name: Name of the feature
            class_name: Optional class to check (if None, checks all classes)
            
        Returns:
            True if character has the feature
        """
        if class_name:
            class_features = self.class_features.get(class_name, {})
            return feature_name in class_features
        
        # Check all classes
        for features in self.class_features.values():
            if feature_name in features:
                return True
        return False
    
    # === MUTATION METHODS (for use by domain services) ===
    
    def update_ability_score(self, ability: str, new_score: AbilityScore) -> None:
        """
        Update an ability score.
        
        Args:
            ability: Name of ability to update
            new_score: New AbilityScore object
        """
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
    
    def add_feat(self, feat_name: str) -> None:
        """Add a feat to the character."""
        if feat_name not in self.feats:
            self.feats.append(feat_name)
            self.last_modified = datetime.now()
    
    def add_spell(self, class_name: str, spell_name: str) -> None:
        """Add a spell to a specific class's spell list."""
        if class_name not in self.spells_known:
            self.spells_known[class_name] = []
        
        if spell_name not in self.spells_known[class_name]:
            self.spells_known[class_name].append(spell_name)
            self.last_modified = datetime.now()
    
    def set_spell_slots(self, spell_level: int, slots: int) -> None:
        """Set number of spell slots for a specific level."""
        self.spell_slots[spell_level] = slots
        self.last_modified = datetime.now()
    
    def add_class_feature(self, class_name: str, feature_name: str, feature_data: Any) -> None:
        """Add a class feature."""
        if class_name not in self.class_features:
            self.class_features[class_name] = {}
        
        self.class_features[class_name][feature_name] = feature_data
        self.last_modified = datetime.now()
    
    # === UTILITY METHODS ===
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert character to dictionary representation.
        
        Returns:
            Dictionary containing all character data
        """
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
            
            # Proficiencies
            "skill_proficiencies": {k: v.name for k, v in self.skill_proficiencies.items()},
            "saving_throw_proficiencies": {k: v.name for k, v in self.saving_throw_proficiencies.items()},
            "weapon_proficiencies": list(self.weapon_proficiencies),
            "armor_proficiencies": list(self.armor_proficiencies),
            "tool_proficiencies": {k: v.name for k, v in self.tool_proficiencies.items()},
            "languages": list(self.languages),
            
            # Features
            "species_traits": self.species_traits,
            "class_features": self.class_features,
            "background_feature": self.background_feature,
            "feats": self.feats,
            
            # Current state
            "current_hit_points": self.current_hit_points,
            "maximum_hit_points": self.maximum_hit_points,
            "temporary_hit_points": self.temporary_hit_points,
            "experience_points": self.experience_points,
            
            # Spellcasting
            "spellcasting_ability": self.spellcasting_ability,
            "spellcasting_classes": self.spellcasting_classes,
            "ritual_casting_classes": self.ritual_casting_classes,
            "spell_slots": self.spell_slots,
            "spells_known": self.spells_known,
            
            # Equipment
            "equipment": self.equipment,
            
            # Metadata
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "player_name": self.player_name,
            "campaign": self.campaign,
            "sources_used": list(self.sources_used),
            
            # Computed values
            "total_level": self.total_level,
            "primary_class": self.primary_class,
            "proficiency_bonus": self.proficiency_bonus
        }
    
    def __str__(self) -> str:
        """String representation of character."""
        level_str = f"Level {self.total_level}"
        if self.is_multiclass:
            class_levels = [f"{cls} {lvl}" for cls, lvl in self.character_classes.items()]
            level_str = f"Level {self.total_level} ({'/'.join(class_levels)})"
        
        return f"{self.name}, {level_str} {self.species} {self.primary_class}"
    
    def __repr__(self) -> str:
        """Developer representation of character."""
        return f"Character(name='{self.name}', species='{self.species}', level={self.total_level})"

    # === DATA UTILITIES ===

    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary representation."""
        return {
            "name": self.name,
            "species": self.species,
            "character_classes": self.character_classes,
            "ability_scores": {
                ability: getattr(self, ability).total_score 
                for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
            },
            # ... rest of character data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Create character from dictionary data."""
        # Implementation for creating character from dict
        pass
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Get a summary of character information."""
        return {
            "name": self.name,
            "level": self.total_level,
            "class": self.primary_class,
            "species": self.species,
            "hit_points": f"{self.current_hit_points}/{self.maximum_hit_points}",
            "armor_class": self.armor_class,
            "proficiency_bonus": self.proficiency_bonus
        }

    # Basic identity
    name: str = ""
    species: str = ""
    character_classes: Dict[str, int] = field(default_factory=dict)
    background: str = ""
    level: int = 1
    
    # Core attributes from character_creator template
    ability_scores: Dict[str, int] = field(default_factory=dict)
    hit_points: int = 0
    armor_class: int = 10
    proficiency_bonus: int = 2
    
    # Simple calculated properties
    @property
    def total_level(self) -> int:
        return sum(self.character_classes.values())
    
    @property
    def primary_class(self) -> str:
        if not self.character_classes:
            return ""
        return max(self.character_classes.items(), key=lambda x: x[1])[0]