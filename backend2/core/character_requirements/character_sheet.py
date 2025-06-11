from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Union, Tuple, Any

from creative_rules_2024 import CreativeRules2024

class ProficiencyLevel(Enum):
    NONE = 0
    PROFICIENT = 1
    EXPERT = 2

class CharacterSheet:
    """
    A comprehensive class for storing all attributes needed to generate a D&D 5e character sheet.
    This class focuses on character creation data, not in-game mechanics.
    """
    
    def __init__(self, name: str = ""):
        # Basic Character Identity - Independent Variables
        self.name: str = name
        self.species: str = ""
        self.species_variants: List[str] = []
        self.lineage: Optional[str] = None
        self.character_class: Dict[str, int] = {}  # {"Fighter": 3, "Wizard": 2}
        self.subclasses: Dict[str, str] = {}  # {"Fighter": "Champion"}
        self.background: str = ""
        self.alignment_ethical: str = ""  # Lawful, Neutral, Chaotic
        self.alignment_moral: str = ""    # Good, Neutral, Evil
        self.level: int = 1
        self.experience_points: int = 0
        self.hit_dice: Dict[str, int] = {}  # {"d8": 3, "d6": 2}
        
        # Appearance and Identity
        self.height: str = ""
        self.weight: str = ""
        self.age: int = 0
        self.eyes: str = ""
        self.hair: str = ""
        self.skin: str = ""
        self.gender: str = ""
        self.pronouns: str = ""
        self.size: str = "Medium"
        
        # Ability Scores - Independent Variables
        self.strength: int = 10
        self.dexterity: int = 10
        self.constitution: int = 10
        self.intelligence: int = 10
        self.wisdom: int = 10
        self.charisma: int = 10
        
        # Proficiencies and Skills - Independent Variables
        self.skill_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.saving_throw_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.weapon_proficiencies: Set[str] = set()
        self.armor_proficiencies: Set[str] = set()
        self.tool_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.languages: Set[str] = set()
        
        # Features and Traits - Independent Variables
        self.species_traits: Dict[str, Any] = {}
        self.class_features: Dict[str, Any] = {}
        self.background_feature: str = ""
        self.feats: List[str] = []
        
        # Equipment - Independent Variables
        self.armor: Optional[str] = None
        self.shield: bool = False
        self.weapons: List[Dict[str, Any]] = []
        self.equipment: List[Dict[str, Any]] = []
        self.currency: Dict[str, int] = {
            "copper": 0,
            "silver": 0,
            "electrum": 0,
            "gold": 0,
            "platinum": 0
        }
        
        # Spellcasting - Independent Variables
        self.spellcasting_ability: Optional[str] = None
        self.spellcasting_classes: Dict[str, Dict[str, Any]] = {}
        self.spells_known: Dict[int, List[str]] = {}  # {0: ["Fire Bolt", "Mage Hand"], 1: ["Magic Missile"]}
        self.spells_prepared: List[str] = []
        
        # Character Background & Personality - Independent Variables
        self.personality_traits: List[str] = []
        self.ideals: List[str] = []
        self.bonds: List[str] = []
        self.flaws: List[str] = []
        self.backstory: str = ""
        
        # Special Senses and Movement - Independent Variables
        self.base_speed: int = 30
        self.vision_types: Dict[str, int] = {}  # {"darkvision": 60}
        self.movement_types: Dict[str, int] = {}  # {"swim": 30, "fly": 0}
        
        # Derived Stats - Dependent Variables (calculated from independent variables)
        self.ability_modifiers: Dict[str, int] = {}
        self.proficiency_bonus: int = 2
        self.initiative: int = 0
        self.armor_class: int = 10
        self.passive_perception: int = 10
        self.passive_investigation: int = 10
        self.passive_insight: int = 10
        self.spell_attack_bonus: int = 0
        self.spell_save_dc: int = 0
        
        # Hit Points - Part Independent, Part Dependent
        self.max_hit_points: int = 0
        self.current_hit_points: int = 0
        self.temporary_hit_points: int = 0
        self.hit_point_maximum_modifier: int = 0
        
        # Character Advancement and Planning
        self.milestone_level: bool = False
        self.next_feat_options: List[str] = []
        self.next_asi_plan: Dict[str, int] = {}  # {"strength": 1, "constitution": 1}
        
        # Additional Character Information
        self.character_appearance_notes: str = ""
        self.allies_and_organizations: str = ""
        self.additional_features: Dict[str, str] = {}
        self.treasure_notes: str = ""
        
        # Character Sheet Metadata
        self.creation_date: str = ""
        self.last_updated: str = ""
        self.player_name: str = ""
        self.campaign: str = ""
        self.sources_used: Set[str] = set()  # PHB, XGE, etc.
    
    @property
    def total_level(self) -> int:
        """Calculate total character level from all classes."""
        return sum(self.character_class.values()) if self.character_class else self.level
    
    @property
    def primary_class(self) -> str:
        """Determine primary class (highest level or first class)."""
        if not self.character_class:
            return ""
        return max(self.character_class.items(), key=lambda x: x[1])[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the character sheet to a dictionary for serialization."""
        # Implementation would convert all attributes to a dictionary
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterSheet':
        """Create a character sheet from a dictionary."""
        # Implementation would populate a new character sheet from dictionary data
        pass
    
    def calculate_derived_stats(self) -> None:
        """Calculate all dependent variables from independent variables."""
        # This would update all derived stats based on current attribute values
        pass
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate the character sheet for completeness and rule compliance."""
        # Implementation would check for issues and return success/failure with messages
        pass

    # Independent varibles; getters for all attributes - these methods provide access to character data
    def get_name(self) -> str:
        """Get the character's name."""
        return self.name

    def get_species(self) -> str:
        """Get the character's species."""
        return self.species

    def get_species_variants(self) -> List[str]:
        """Get the character's species variants."""
        return self.species_variants.copy()

    def get_lineage(self) -> Optional[str]:
        """Get the character's lineage."""
        return self.lineage

    def get_character_classes(self) -> Dict[str, int]:
        """Get all character classes and their levels."""
        return self.character_class.copy()

    def get_level_in_class(self, class_name: str) -> int:
        """Get character's level in a specific class."""
        return self.character_class.get(class_name, 0)

    def get_subclass(self, class_name: str) -> Optional[str]:
        """Get the subclass for a specific class."""
        return self.subclasses.get(class_name)

    def get_all_subclasses(self) -> Dict[str, str]:
        """Get all subclasses."""
        return self.subclasses.copy()

    def get_background(self) -> str:
        """Get the character's background."""
        return self.background

    def get_alignment(self) -> Tuple[str, str]:
        """Get the character's alignment."""
        return (self.alignment_ethical, self.alignment_moral)

    def get_experience_points(self) -> int:
        """Get the character's experience points."""
        return self.experience_points

    def get_hit_dice(self) -> Dict[str, int]:
        """Get the character's hit dice."""
        return self.hit_dice.copy()

    def get_appearance(self) -> Dict[str, Union[str, int]]:
        """Get the character's appearance details."""
        return {
            "height": self.height,
            "weight": self.weight,
            "age": self.age,
            "eyes": self.eyes,
            "hair": self.hair,
            "skin": self.skin,
            "gender": self.gender,
            "pronouns": self.pronouns,
            "size": self.size
        }

    def get_ability_score(self, ability: str) -> int:
        """Get a specific ability score."""
        ability = ability.lower()
        if ability == "strength" or ability == "str":
            return self.strength
        elif ability == "dexterity" or ability == "dex":
            return self.dexterity
        elif ability == "constitution" or ability == "con":
            return self.constitution
        elif ability == "intelligence" or ability == "int":
            return self.intelligence
        elif ability == "wisdom" or ability == "wis":
            return self.wisdom
        elif ability == "charisma" or ability == "cha":
            return self.charisma
        else:
            raise ValueError(f"Unknown ability: {ability}")

    def get_ability_scores(self) -> Dict[str, int]:
        """Get all ability scores."""
        return {
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma
        }

    def get_skill_proficiency(self, skill: str) -> ProficiencyLevel:
        """Get proficiency level for a specific skill."""
        return self.skill_proficiencies.get(skill, ProficiencyLevel.NONE)

    def get_all_skill_proficiencies(self) -> Dict[str, ProficiencyLevel]:
        """Get all skill proficiencies."""
        return self.skill_proficiencies.copy()

    def get_saving_throw_proficiency(self, ability: str) -> ProficiencyLevel:
        """Get proficiency level for a specific saving throw."""
        return self.saving_throw_proficiencies.get(ability, ProficiencyLevel.NONE)

    def get_all_saving_throw_proficiencies(self) -> Dict[str, ProficiencyLevel]:
        """Get all saving throw proficiencies."""
        return self.saving_throw_proficiencies.copy()

    def get_weapon_proficiencies(self) -> Set[str]:
        """Get all weapon proficiencies."""
        return self.weapon_proficiencies.copy()

    def get_armor_proficiencies(self) -> Set[str]:
        """Get all armor proficiencies."""
        return self.armor_proficiencies.copy()

    def get_tool_proficiencies(self) -> Dict[str, ProficiencyLevel]:
        """Get all tool proficiencies."""
        return self.tool_proficiencies.copy()

    def get_languages(self) -> Set[str]:
        """Get all languages known."""
        return self.languages.copy()

    def get_species_traits(self) -> Dict[str, Any]:
        """Get all species traits."""
        return self.species_traits.copy()

    def get_class_features(self) -> Dict[str, Any]:
        """Get all class features."""
        return self.class_features.copy()

    def get_background_feature(self) -> str:
        """Get the background feature."""
        return self.background_feature

    def get_feats(self) -> List[str]:
        """Get all feats."""
        return self.feats.copy()

    def get_armor(self) -> Optional[str]:
        """Get the character's armor."""
        return self.armor

    def has_shield(self) -> bool:
        """Check if the character has a shield."""
        return self.shield

    def get_weapons(self) -> List[Dict[str, Any]]:
        """Get all weapons."""
        return self.weapons.copy()

    def get_equipment(self) -> List[Dict[str, Any]]:
        """Get all equipment."""
        return self.equipment.copy()

    def get_currency(self) -> Dict[str, int]:
        """Get all currency."""
        return self.currency.copy()

    def get_spellcasting_ability(self) -> Optional[str]:
        """Get the spellcasting ability."""
        return self.spellcasting_ability

    def get_spellcasting_class_details(self, class_name: str) -> Dict[str, Any]:
        """Get spellcasting details for a specific class."""
        return self.spellcasting_classes.get(class_name, {}).copy()

    def get_spells_known_by_level(self, level: int) -> List[str]:
        """Get spells known for a specific level."""
        return self.spells_known.get(level, []).copy()

    def get_all_spells_known(self) -> Dict[int, List[str]]:
        """Get all spells known by level."""
        return {k: v.copy() for k, v in self.spells_known.items()}

    def get_spells_prepared(self) -> List[str]:
        """Get all prepared spells."""
        return self.spells_prepared.copy()

    def get_personality_traits(self) -> List[str]:
        """Get personality traits."""
        return self.personality_traits.copy()

    def get_ideals(self) -> List[str]:
        """Get ideals."""
        return self.ideals.copy()

    def get_bonds(self) -> List[str]:
        """Get bonds."""
        return self.bonds.copy()

    def get_flaws(self) -> List[str]:
        """Get flaws."""
        return self.flaws.copy()

    def get_backstory(self) -> str:
        """Get character backstory."""
        return self.backstory

    def get_base_speed(self) -> int:
        """Get base movement speed."""
        return self.base_speed

    def get_vision_types(self) -> Dict[str, int]:
        """Get all vision types and ranges."""
        return self.vision_types.copy()

    def get_movement_types(self) -> Dict[str, int]:
        """Get all special movement types and speeds."""
        return self.movement_types.copy()

    def is_milestone_leveling(self) -> bool:
        """Check if using milestone leveling."""
        return self.milestone_level

    def get_next_feat_options(self) -> List[str]:
        """Get options for next feat."""
        return self.next_feat_options.copy()

    def get_next_asi_plan(self) -> Dict[str, int]:
        """Get planned ability score improvements."""
        return self.next_asi_plan.copy()

    def get_allies_and_organizations(self) -> str:
        """Get allies and organizations information."""
        return self.allies_and_organizations

    def get_additional_features(self) -> Dict[str, str]:
        """Get additional features."""
        return self.additional_features.copy()

    def get_treasure_notes(self) -> str:
        """Get treasure notes."""
        return self.treasure_notes

    def get_character_metadata(self) -> Dict[str, Any]:
        """Get character sheet metadata."""
        return {
            "creation_date": self.creation_date,
            "last_updated": self.last_updated,
            "player_name": self.player_name,
            "campaign": self.campaign,
            "sources_used": self.sources_used.copy()
        }
    
    # Dependent variables; calculates all derived attributes
    def calculate_ability_modifier(self, ability_score: int) -> int:
        """Calculate ability modifier from score using D&D 5e formula."""
        return (ability_score - 10) // 2

    def calculate_all_ability_modifiers(self) -> Dict[str, int]:
        """Calculate all ability modifiers based on current scores."""
        self.ability_modifiers = {
            "strength": self.calculate_ability_modifier(self.strength),
            "dexterity": self.calculate_ability_modifier(self.dexterity),
            "constitution": self.calculate_ability_modifier(self.constitution),
            "intelligence": self.calculate_ability_modifier(self.intelligence),
            "wisdom": self.calculate_ability_modifier(self.wisdom),
            "charisma": self.calculate_ability_modifier(self.charisma)
        }
        return self.ability_modifiers

    def calculate_proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on character level."""
        level = self.total_level
        self.proficiency_bonus = 2 + ((level - 1) // 4)
        return self.proficiency_bonus

    def calculate_initiative(self) -> int:
        """Calculate initiative bonus."""
        dex_mod = self.ability_modifiers.get("dexterity", 0)
        
        # Check for feats that modify initiative
        initiative_bonus = 0
        if "Alert" in self.feats:
            initiative_bonus += 5
        
        # Check for class features that modify initiative
        if "Bard" in self.character_class and self.get_level_in_class("Bard") >= 2:
            # Jack of All Trades
            if self.proficiency_bonus > 0:
                initiative_bonus += self.proficiency_bonus // 2
        
        # Remarkable Athlete for Champion Fighters
        if "Fighter" in self.character_class and self.get_subclass("Fighter") == "Champion" and self.get_level_in_class("Fighter") >= 7:
            if self.proficiency_bonus > 0:
                initiative_bonus += self.proficiency_bonus // 2
        
        self.initiative = dex_mod + initiative_bonus
        return self.initiative

    def calculate_armor_class(self) -> int:
        """Calculate armor class based on equipment and abilities."""
        base_ac = 10
        dex_mod = self.ability_modifiers.get("dexterity", 0)
        
        # Check for worn armor
        if self.armor is not None:
            # This would require a more detailed armor database
            # For now using a simplified approach
            armor_type = self.armor.lower()
            
            if "padded" in armor_type or "leather" in armor_type:
                # Light armor: base + full DEX
                if "studded" in armor_type:
                    base_ac = 12 + dex_mod
                else:
                    base_ac = 11 + dex_mod
                    
            elif "chain shirt" in armor_type:
                base_ac = 13 + min(dex_mod, 2)
            elif "scale" in armor_type:
                base_ac = 14 + min(dex_mod, 2)
            elif "breastplate" in armor_type:
                base_ac = 14 + min(dex_mod, 2)
            elif "half plate" in armor_type:
                base_ac = 15 + min(dex_mod, 2)
                
            elif "ring mail" in armor_type:
                base_ac = 14  # No DEX bonus
            elif "chain mail" in armor_type:
                base_ac = 16  # No DEX bonus
            elif "splint" in armor_type:
                base_ac = 17  # No DEX bonus
            elif "plate" in armor_type:
                base_ac = 18  # No DEX bonus
        else:
            # Unarmored
            # Check for Unarmored Defense from classes
            if "Barbarian" in self.character_class:
                con_mod = self.ability_modifiers.get("constitution", 0)
                barbarian_ac = 10 + dex_mod + con_mod
                base_ac = max(base_ac, barbarian_ac)
                
            if "Monk" in self.character_class:
                wis_mod = self.ability_modifiers.get("wisdom", 0)
                monk_ac = 10 + dex_mod + wis_mod
                base_ac = max(base_ac, monk_ac)
        
        # Add shield bonus
        if self.shield:
            base_ac += 2
        
        # Check for special features/feats that affect AC
        if "defensive_fighting_style" in self.class_features:
            if any(self._is_armor_worn("medium") or self._is_armor_worn("heavy")):
                base_ac += 1
        
        self.armor_class = base_ac
        return self.armor_class

    def calculate_passive_perception(self) -> int:
        """Calculate passive Perception score."""
        wis_mod = self.ability_modifiers.get("wisdom", 0)
        prof_bonus = 0
        
        # Check for proficiency/expertise in Perception
        prof_level = self.get_skill_proficiency("Perception")
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
        
        # Check for Observant feat
        feat_bonus = 5 if "Observant" in self.feats else 0
        
        self.passive_perception = 10 + wis_mod + prof_bonus + feat_bonus
        return self.passive_perception

    def calculate_passive_investigation(self) -> int:
        """Calculate passive Investigation score."""
        int_mod = self.ability_modifiers.get("intelligence", 0)
        prof_bonus = 0
        
        # Check for proficiency/expertise in Investigation
        prof_level = self.get_skill_proficiency("Investigation")
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
        
        # Check for Observant feat
        feat_bonus = 5 if "Observant" in self.feats else 0
        
        self.passive_investigation = 10 + int_mod + prof_bonus + feat_bonus
        return self.passive_investigation

    def calculate_passive_insight(self) -> int:
        """Calculate passive Insight score."""
        wis_mod = self.ability_modifiers.get("wisdom", 0)
        prof_bonus = 0
        
        # Check for proficiency/expertise in Insight
        prof_level = self.get_skill_proficiency("Insight")
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
        
        self.passive_insight = 10 + wis_mod + prof_bonus
        return self.passive_insight

    def calculate_spell_save_dc(self) -> int:
        """Calculate spell save DC."""
        if not self.spellcasting_ability:
            self.spell_save_dc = 0
            return 0
        
        ability_mod = self.ability_modifiers.get(self.spellcasting_ability.lower(), 0)
        self.spell_save_dc = 8 + self.proficiency_bonus + ability_mod
        return self.spell_save_dc

    def calculate_spell_attack_bonus(self) -> int:
        """Calculate spell attack bonus."""
        if not self.spellcasting_ability:
            self.spell_attack_bonus = 0
            return 0
        
        ability_mod = self.ability_modifiers.get(self.spellcasting_ability.lower(), 0)
        self.spell_attack_bonus = self.proficiency_bonus + ability_mod
        return self.spell_attack_bonus

    def calculate_max_hit_points(self) -> int:
        """Calculate maximum hit points."""
        if not self.character_class:
            self.max_hit_points = 0
            return 0
        
        con_mod = self.ability_modifiers.get("constitution", 0)
        total = 0
        
        # Process each class level
        for class_name, level in self.character_class.items():
            if level <= 0:
                continue
                
            # Get hit die for this class (simplified)
            hit_die_size = self._get_class_hit_die_size(class_name)
            
            # First level is always maximum
            if class_name == self.primary_class or self._is_first_class(class_name):
                total += hit_die_size + con_mod
                level_remaining = level - 1
            else:
                level_remaining = level
                
            # Add average for remaining levels
            total += level_remaining * ((hit_die_size // 2) + 1 + con_mod)
        
        # Add hit point modifiers from feats, items, etc.
        total += self.hit_point_maximum_modifier
        
        self.max_hit_points = max(1, total)  # Minimum 1 hit point
        return self.max_hit_points

    def calculate_skill_bonus(self, skill_name: str) -> int:
        """Calculate bonus for a specific skill check."""
        # Map skills to their ability scores
        skill_abilities = {
            "Athletics": "strength",
            "Acrobatics": "dexterity",
            "Sleight of Hand": "dexterity",
            "Stealth": "dexterity",
            "Arcana": "intelligence",
            "History": "intelligence",
            "Investigation": "intelligence",
            "Nature": "intelligence",
            "Religion": "intelligence",
            "Animal Handling": "wisdom",
            "Insight": "wisdom",
            "Medicine": "wisdom",
            "Perception": "wisdom",
            "Survival": "wisdom",
            "Deception": "charisma",
            "Intimidation": "charisma",
            "Performance": "charisma",
            "Persuasion": "charisma"
        }
        
        if skill_name not in skill_abilities:
            return 0
            
        ability = skill_abilities[skill_name]
        ability_mod = self.ability_modifiers.get(ability, 0)
        
        # Check for proficiency/expertise
        prof_level = self.get_skill_proficiency(skill_name)
        prof_bonus = 0
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
            
        return ability_mod + prof_bonus

    def calculate_saving_throw_bonus(self, ability: str) -> int:
        """Calculate bonus for a specific saving throw."""
        ability_mod = self.ability_modifiers.get(ability.lower(), 0)
        
        # Check for proficiency
        prof_level = self.get_saving_throw_proficiency(ability)
        prof_bonus = 0
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
            
        return ability_mod + prof_bonus

    def calculate_weapon_attack_bonus(self, weapon_index: int) -> int:
        """Calculate attack bonus for a specific weapon."""
        if weapon_index < 0 or weapon_index >= len(self.weapons):
            return 0
            
        weapon = self.weapons[weapon_index]
        
        # Determine which ability modifier to use
        ability = "strength"
        if "finesse" in weapon.get("properties", []) or weapon.get("weapon_type") == "ranged":
            # Use higher of STR or DEX for finesse weapons, or DEX for ranged
            str_mod = self.ability_modifiers.get("strength", 0)
            dex_mod = self.ability_modifiers.get("dexterity", 0)
            if dex_mod > str_mod:
                ability = "dexterity"
        
        ability_mod = self.ability_modifiers.get(ability, 0)
        
        # Check for proficiency
        prof_bonus = 0
        weapon_name = weapon.get("name", "")
        if any(wp for wp in self.weapon_proficiencies if wp.lower() in weapon_name.lower() or wp == "all"):
            prof_bonus = self.proficiency_bonus
        
        # Check for magic bonus
        magic_bonus = weapon.get("magic_bonus", 0)
        
        return ability_mod + prof_bonus + magic_bonus

    def calculate_weapon_damage_bonus(self, weapon_index: int) -> int:
        """Calculate damage bonus for a specific weapon."""
        if weapon_index < 0 or weapon_index >= len(self.weapons):
            return 0
            
        weapon = self.weapons[weapon_index]
        
        # Determine which ability modifier to use (same logic as attack bonus)
        ability = "strength"
        if "finesse" in weapon.get("properties", []) or weapon.get("weapon_type") == "ranged":
            str_mod = self.ability_modifiers.get("strength", 0)
            dex_mod = self.ability_modifiers.get("dexterity", 0)
            if dex_mod > str_mod:
                ability = "dexterity"
        
        ability_mod = self.ability_modifiers.get(ability, 0)
        
        # Check for magic bonus
        magic_bonus = weapon.get("magic_bonus", 0)
        
        # Check for fighting styles
        style_bonus = 0
        if "dueling" in self.class_features and not "two_handed" in weapon.get("properties", []) and not self.shield:
            style_bonus = 2
        
        return ability_mod + magic_bonus + style_bonus

    def calculate_all_derived_stats(self) -> None:
        """Calculate all derived statistics in the proper order."""
        # First calculate ability modifiers as they're needed by other calculations
        self.calculate_all_ability_modifiers()
        
        # Calculate proficiency bonus next
        self.calculate_proficiency_bonus()
        
        # Now calculate everything else
        self.calculate_initiative()
        self.calculate_armor_class()
        self.calculate_passive_perception()
        self.calculate_passive_investigation()
        self.calculate_passive_insight()
        self.calculate_spell_save_dc()
        self.calculate_spell_attack_bonus()
        self.calculate_max_hit_points()
        
        # If current hit points are unset, set them to max
        if self.current_hit_points == 0 and self.max_hit_points > 0:
            self.current_hit_points = self.max_hit_points

    def _is_armor_worn(self, armor_type: str) -> bool:
        """Helper method to check if certain armor type is being worn."""
        if not self.armor:
            return False
            
        # This would ideally check against a database of armor types
        armor = self.armor.lower()
        if armor_type == "light":
            return any(a in armor for a in ["padded", "leather"])
        elif armor_type == "medium":
            return any(a in armor for a in ["hide", "chain shirt", "scale", "breastplate", "half plate"])
        elif armor_type == "heavy":
            return any(a in armor for a in ["ring mail", "chain mail", "splint", "plate"])
        return False

    def _get_class_hit_die_size(self, class_name: str) -> int:
        """Get hit die size for a class."""
        hit_die_sizes = {
            "Barbarian": 12,
            "Fighter": 10, 
            "Paladin": 10,
            "Ranger": 10,
            "Monk": 8,
            "Rogue": 8,
            "Warlock": 8,
            "Bard": 8,
            "Cleric": 8,
            "Druid": 8,
            "Artificer": 8,
            "Wizard": 6,
            "Sorcerer": 6
        }
        return hit_die_sizes.get(class_name, 8)  # Default to d8 if unknown

    def _is_first_class(self, class_name: str) -> bool:
        """Check if this was character's first class (for HP calculation)."""
        # This would need proper tracking of character progression
        # For now, assume primary class (highest level) was first
        return class_name == self.primary_class