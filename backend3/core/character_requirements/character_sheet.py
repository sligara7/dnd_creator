from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Union, Tuple, Any

class ProficiencyLevel(Enum):
    NONE = 0
    PROFICIENT = 1
    EXPERT = 2

class AbilityScore:
    """
    Class representing a D&D ability score with its component values.
    
    This breakdown allows for precise tracking of different bonuses and their sources,
    which is essential for proper stacking rules and temporary effects.
    """
    
    def __init__(self, base_score: int = 10):
        # Core Independent Variable
        self.base_score: int = base_score  # Starting value from character creation
        
        # In-Game Independent Variables
        self.bonus: int = 0  # Temporary or permanent flat bonuses
        self.set_score: Optional[int] = None  # Direct override (e.g., from Belt of Giant Strength)
        self.stacking_bonuses: Dict[str, int] = {}  # Named bonuses that can stack (source -> value)
    
    @property
    def total_score(self) -> int:
        """Calculate the final ability score value applying all bonuses and overrides."""
        # Dependent Variable (calculated)
        if self.set_score is not None:
            return self.set_score
        
        return self.base_score + self.bonus + sum(self.stacking_bonuses.values())
    
    @property
    def modifier(self) -> int:
        """Calculate the ability modifier using D&D 5e formula."""
        # Dependent Variable (calculated)
        return (self.total_score - 10) // 2
    
    def add_stacking_bonus(self, source: str, value: int) -> None:
        """Add a stacking bonus from a specific source."""
        self.stacking_bonuses[source] = value
    
    def remove_stacking_bonus(self, source: str) -> None:
        """Remove a stacking bonus from a specific source."""
        if source in self.stacking_bonuses:
            del self.stacking_bonuses[source]
            
    def reset_bonuses(self) -> None:
        """Reset all bonuses to default values."""
        self.bonus = 0
        self.set_score = None
        self.stacking_bonuses.clear()
        
    def __int__(self) -> int:
        """Allow casting the ability score to an integer."""
        return self.total_score

class CharacterSheet:
    """
    A comprehensive class for storing all attributes needed to generate a D&D 5e character sheet.
    Variables are organized into three categories:
    1. CORE INDEPENDENT - Set during character creation/leveling (species, class, ability scores)
    2. IN-GAME INDEPENDENT - Updated during gameplay (XP, HP, conditions, equipment)
    3. DEPENDENT - Calculated from other variables (AC, initiative, proficiency bonus)
    """
    
    def __init__(self, name: str = ""):
        #============================================================
        # CORE INDEPENDENT VARIABLES - Character Creation & Leveling
        #============================================================
        
        # Basic Character Identity
        self._name: str = name
        self._species: str = ""
        self._species_variants: List[str] = []
        self._lineage: Optional[str] = None
        self._character_class: Dict[str, int] = {}  # {"Fighter": 3, "Wizard": 2}
        self._subclasses: Dict[str, str] = {}  # {"Fighter": "Champion"}
        self._background: str = ""
        self._alignment_ethical: str = ""  # Lawful, Neutral, Chaotic
        self._alignment_moral: str = ""    # Good, Neutral, Evil
        self._level: int = 1
        
        # Appearance and Identity
        self._height: str = ""
        self._weight: str = ""
        self._age: int = 0
        self._eyes: str = ""
        self._hair: str = ""
        self._skin: str = ""
        self._gender: str = ""
        self._pronouns: str = ""
        self._size: str = "Medium"
        
        # Base Ability Scores (core stats from character creation)
        self._strength: AbilityScore = AbilityScore(10)
        self._dexterity: AbilityScore = AbilityScore(10)
        self._constitution: AbilityScore = AbilityScore(10)
        self._intelligence: AbilityScore = AbilityScore(10)
        self._wisdom: AbilityScore = AbilityScore(10)
        self._charisma: AbilityScore = AbilityScore(10)
        
        # Core Proficiencies (gained during character creation/leveling)
        self._skill_proficiencies: Dict[str, ProficiencyLevel] = {}
        self._saving_throw_proficiencies: Dict[str, ProficiencyLevel] = {}
        self._weapon_proficiencies: Set[str] = set()
        self._armor_proficiencies: Set[str] = set()
        self._tool_proficiencies: Dict[str, ProficiencyLevel] = {}
        self._languages: Set[str] = set()
        
        # Core Features and Traits
        self._species_traits: Dict[str, Any] = {}
        self._class_features: Dict[str, Any] = {}
        self._background_feature: str = ""
        self._feats: List[str] = []
        
        # Core Movement and Senses
        self._base_speed: int = 30
        self._base_vision_types: Dict[str, int] = {}  # {"darkvision": 60}
        self._base_movement_types: Dict[str, int] = {}  # {"swim": 30, "fly": 0}
        
        # Core Defenses from race/class
        self._base_damage_resistances: Set[str] = set()
        self._base_damage_immunities: Set[str] = set()
        self._base_damage_vulnerabilities: Set[str] = set()
        self._base_condition_immunities: Set[str] = set()
        
        # Core Spellcasting Abilities
        self._spellcasting_ability: Optional[str] = None
        self._spellcasting_classes: Dict[str, Dict[str, Any]] = {}
        self._ritual_casting_classes: Dict[str, bool] = {}
        
        # Character Background & Personality
        self._personality_traits: List[str] = []
        self._ideals: List[str] = []
        self._bonds: List[str] = []
        self._flaws: List[str] = []
        self._backstory: str = ""
        
        # Hit Dice (base values from class)
        self._hit_dice: Dict[str, int] = {}  # {"d8": 3, "d6": 2}
        
        # Character Sheet Metadata
        self._creation_date: str = ""
        self._player_name: str = ""
        self._campaign: str = ""
        self._sources_used: Set[str] = set()  # PHB, XGE, etc.
        
        #============================================================
        # IN-GAME INDEPENDENT VARIABLES - Updated During Gameplay
        #============================================================
        
        # Experience Points
        self._experience_points: int = 0
        
        # Hit Points - Current Values
        self._current_hit_points: int = 0
        self._temporary_hit_points: int = 0
        self._hit_point_maximum_modifier: int = 0  # From effects, items, etc.
        
        # Hit Dice - Current Values
        self._hit_dice_remaining: Dict[str, int] = {}  # {"d8": 3, "d6": 2}
        
        # Spell Slots - Current Values
        self._spell_slots_total: Dict[int, int] = {}     # {1: 4, 2: 3, 3: 2}
        self._spell_slots_remaining: Dict[int, int] = {}  # {1: 2, 2: 1, 3: 0}
        self._spells_known: Dict[int, List[str]] = {}    # {0: ["Fire Bolt", "Mage Hand"], 1: ["Magic Missile"]}
        self._spells_prepared: List[str] = []
        self._ritual_book_spells: List[str] = []
        
        # Equipment - Current Items
        self._armor: Optional[str] = None
        self._shield: bool = False
        self._weapons: List[Dict[str, Any]] = []
        self._equipment: List[Dict[str, Any]] = []
        self._attuned_items: List[str] = []
        self._max_attunement_slots: int = 3
        
        # Currency
        self._currency: Dict[str, int] = {
            "copper": 0,
            "silver": 0,
            "electrum": 0,
            "gold": 0,
            "platinum": 0
        }
        
        # Conditions
        self._active_conditions: Dict[str, Dict[str, Any]] = {}  # {"stunned": {"duration": 2, "source": "spell"}}
        self._exhaustion_level: int = 0
        
        # Temporary Defenses (from spells, items, etc.)
        self._temp_damage_resistances: Set[str] = set()
        self._temp_damage_immunities: Set[str] = set()
        self._temp_damage_vulnerabilities: Set[str] = set()
        self._temp_condition_immunities: Set[str] = set()
        
        # Action Economy - Current State
        self._actions_per_turn: int = 1
        self._bonus_actions_per_turn: int = 1
        self._reactions_per_turn: int = 1
        self._actions_used: int = 0
        self._bonus_actions_used: int = 0
        self._reactions_used: int = 0
        
        # Companion Creatures
        self._beast_companion: Optional[Dict[str, Any]] = None
        
        # Adventure Notes
        self._notes: Dict[str, str] = {
            'organizations': "",
            'allies': "",
            'enemies': "",
            'backstory': "",
            'other': ""
        }
        
        # Last updated timestamp
        self._last_updated: str = ""
        
        #============================================================
        # DEPENDENT VARIABLES - Calculated from Other Variables
        #============================================================
        
        # Combat Stats
        self._proficiency_bonus: int = 2  # Calculated from level
        self._initiative: int = 0         # Calculated from DEX and features
        self._armor_class: int = 10       # Calculated from DEX, armor, etc.
        self._max_hit_points: int = 0     # Calculated from CON, level, etc.
        
        # Passive Skills
        self._passive_perception: int = 10
        self._passive_investigation: int = 10
        self._passive_insight: int = 10
        
        # Spellcasting Stats
        self._spell_attack_bonus: int = 0
        self._spell_save_dc: int = 0
        
        # Available Actions
        self._available_actions: Dict[str, Dict[str, Any]] = {
            # Standard actions every character has
            "Attack": {"type": "action", "description": "Make an attack with a weapon"},
            "Dash": {"type": "action", "description": "Double your movement speed"},
            "Disengage": {"type": "action", "description": "Your movement doesn't provoke opportunity attacks"},
            "Dodge": {"type": "action", "description": "Attacks against you have disadvantage"},
            "Help": {"type": "action", "description": "Give another creature advantage on its next ability check or attack"},
            "Hide": {"type": "action", "description": "Make a Stealth check to hide"},
            "Ready": {"type": "action", "description": "Prepare an action to take in response to a trigger"},
            "Search": {"type": "action", "description": "Make a Perception or Investigation check to find something"},
            "Use Object": {"type": "action", "description": "Interact with an object that requires your action"}
        }
        
        # Available Reactions
        self._available_reactions: Dict[str, Dict[str, Any]] = {
            "Opportunity Attack": {
                "type": "reaction", 
                "description": "Make a melee attack against a creature leaving your reach",
                "trigger": "enemy_leaves_reach"
            },
        }

    #============================================================
    # CORE INDEPENDENT VARIABLE METHODS - Getters
    #============================================================
    
    # Basic Character Identity Getters
    def get_name(self) -> str:
        """Get character's name."""
        return self._name
    
    def get_species(self) -> str:
        """Get character's species."""
        return self._species
    
    def get_species_variants(self) -> List[str]:
        """Get character's species variants."""
        return self._species_variants.copy()
    
    def get_lineage(self) -> Optional[str]:
        """Get character's lineage if any."""
        return self._lineage
    
    def get_class_levels(self) -> Dict[str, int]:
        """Get character's classes and levels."""
        return self._character_class.copy()
    
    def get_subclass(self, class_name: str) -> Optional[str]:
        """Get subclass for a specific class."""
        return self._subclasses.get(class_name)
    
    def get_background(self) -> str:
        """Get character's background."""
        return self._background
    
    def get_alignment(self) -> Tuple[str, str]:
        """Get character's ethical and moral alignment."""
        return (self._alignment_ethical, self._alignment_moral)
    
    def get_level(self) -> int:
        """Get character's level if single-classed."""
        return self._level
    
    # Appearance and Identity Getters
    def get_appearance(self) -> Dict[str, Any]:
        """Get character's physical appearance details."""
        return {
            "height": self._height,
            "weight": self._weight,
            "age": self._age,
            "eyes": self._eyes,
            "hair": self._hair,
            "skin": self._skin,
            "gender": self._gender,
            "pronouns": self._pronouns,
            "size": self._size
        }
    
    # Ability Score Getters
    def get_ability_score_object(self, ability: str) -> AbilityScore:
        """Get the AbilityScore object for a specific ability."""
        ability = ability.lower()
        if ability == "strength" or ability == "str":
            return self._strength
        elif ability == "dexterity" or ability == "dex":
            return self._dexterity
        elif ability == "constitution" or ability == "con":
            return self._constitution
        elif ability == "intelligence" or ability == "int":
            return self._intelligence
        elif ability == "wisdom" or ability == "wis":
            return self._wisdom
        elif ability == "charisma" or ability == "cha":
            return self._charisma
        else:
            raise ValueError(f"Unknown ability: {ability}")
    
    def get_ability_score(self, ability: str) -> int:
        """Get a specific ability score's total value."""
        ability_obj = self.get_ability_score_object(ability)
        return ability_obj.total_score
    
    def get_ability_scores(self) -> Dict[str, int]:
        """Get all ability scores' total values."""
        return {
            "strength": self._strength.total_score,
            "dexterity": self._dexterity.total_score,
            "constitution": self._constitution.total_score,
            "intelligence": self._intelligence.total_score,
            "wisdom": self._wisdom.total_score,
            "charisma": self._charisma.total_score
        }
    
    def get_ability_base_score(self, ability: str) -> int:
        """Get the base score for a specific ability."""
        ability_obj = self.get_ability_score_object(ability)
        return ability_obj.base_score
    
    def get_ability_base_scores(self) -> Dict[str, int]:
        """Get all ability base scores."""
        return {
            "strength": self._strength.base_score,
            "dexterity": self._dexterity.base_score,
            "constitution": self._constitution.base_score,
            "intelligence": self._intelligence.base_score,
            "wisdom": self._wisdom.base_score,
            "charisma": self._charisma.base_score
        }
    
    def get_ability_modifier(self, ability: str) -> int:
        """Get the modifier for a specific ability."""
        ability_obj = self.get_ability_score_object(ability)
        return ability_obj.modifier
    
    def get_ability_modifiers(self) -> Dict[str, int]:
        """Get all ability modifiers."""
        return {
            "strength": self._strength.modifier,
            "dexterity": self._dexterity.modifier,
            "constitution": self._constitution.modifier,
            "intelligence": self._intelligence.modifier,
            "wisdom": self._wisdom.modifier,
            "charisma": self._charisma.modifier
        }
    
    # Proficiency Getters
    def get_skill_proficiency(self, skill: str) -> ProficiencyLevel:
        """Get proficiency level for a specific skill."""
        return self._skill_proficiencies.get(skill, ProficiencyLevel.NONE)
    
    def get_saving_throw_proficiency(self, ability: str) -> ProficiencyLevel:
        """Get proficiency level for a specific saving throw."""
        return self._saving_throw_proficiencies.get(ability, ProficiencyLevel.NONE)
    
    def get_weapon_proficiencies(self) -> Set[str]:
        """Get all weapon proficiencies."""
        return self._weapon_proficiencies.copy()
    
    def get_armor_proficiencies(self) -> Set[str]:
        """Get all armor proficiencies."""
        return self._armor_proficiencies.copy()
    
    def get_tool_proficiencies(self) -> Dict[str, ProficiencyLevel]:
        """Get all tool proficiencies."""
        return self._tool_proficiencies.copy()
    
    def get_languages(self) -> Set[str]:
        """Get all known languages."""
        return self._languages.copy()
    
    # Features and Traits Getters
    def get_species_traits(self) -> Dict[str, Any]:
        """Get all species traits."""
        return self._species_traits.copy()
    
    def get_class_features(self) -> Dict[str, Any]:
        """Get all class features."""
        return self._class_features.copy()
    
    def get_background_feature(self) -> str:
        """Get background feature."""
        return self._background_feature
    
    def get_feats(self) -> List[str]:
        """Get all feats."""
        return self._feats.copy()
    
    # Movement and Senses Getters
    def get_base_speed(self) -> int:
        """Get base walking speed."""
        return self._base_speed
    
    def get_base_vision_types(self) -> Dict[str, int]:
        """Get base vision types and ranges."""
        return self._base_vision_types.copy()
    
    def get_base_movement_types(self) -> Dict[str, int]:
        """Get base movement types and speeds."""
        return self._base_movement_types.copy()
    
    # Spellcasting Getters
    def get_spellcasting_ability(self) -> Optional[str]:
        """Get primary spellcasting ability."""
        return self._spellcasting_ability
    
    def get_spellcasting_classes(self) -> Dict[str, Dict[str, Any]]:
        """Get all spellcasting class details."""
        return self._spellcasting_classes.copy()
    
    # Character Personality Getters
    def get_personality_traits(self) -> List[str]:
        """Get personality traits."""
        return self._personality_traits.copy()
    
    def get_ideals(self) -> List[str]:
        """Get ideals."""
        return self._ideals.copy()
    
    def get_bonds(self) -> List[str]:
        """Get bonds."""
        return self._bonds.copy()
    
    def get_flaws(self) -> List[str]:
        """Get flaws."""
        return self._flaws.copy()
    
    def get_backstory(self) -> str:
        """Get character backstory."""
        return self._backstory
    
    # Hit Dice Getters
    def get_hit_dice(self) -> Dict[str, int]:
        """Get total hit dice by type."""
        return self._hit_dice.copy()
    
    # Metadata Getters
    def get_creation_date(self) -> str:
        """Get character creation date."""
        return self._creation_date
    
    def get_player_name(self) -> str:
        """Get player name."""
        return self._player_name
    
    def get_campaign(self) -> str:
        """Get campaign name."""
        return self._campaign
    
    def get_sources_used(self) -> Set[str]:
        """Get source books used for this character."""
        return self._sources_used.copy()
    
    #============================================================
    # CORE INDEPENDENT VARIABLE METHODS - Setters
    #============================================================
    
    def set_name(self, name: str) -> None:
        """Set character name."""
        self._name = name
    
    def set_species(self, species: str) -> None:
        """Set character species."""
        self._species = species
        # This might trigger recalculation of dependent variables
        self.calculate_all_derived_stats()
    
    def add_species_variant(self, variant: str) -> None:
        """Add a species variant."""
        if variant not in self._species_variants:
            self._species_variants.append(variant)
            self.calculate_all_derived_stats()
    
    def set_lineage(self, lineage: str) -> None:
        """Set character lineage."""
        self._lineage = lineage
        self.calculate_all_derived_stats()
    
    def set_class_level(self, class_name: str, level: int) -> None:
        """Set level in a specific class."""
        if level <= 0:
            if class_name in self._character_class:
                del self._character_class[class_name]
        else:
            self._character_class[class_name] = level
        self.calculate_all_derived_stats()
    
    def set_subclass(self, class_name: str, subclass: str) -> None:
        """Set subclass for a specific class."""
        self._subclasses[class_name] = subclass
        self.calculate_all_derived_stats()
    
    def set_background(self, background: str) -> None:
        """Set character background."""
        self._background = background
        self.calculate_all_derived_stats()
    
    def set_alignment(self, ethical: str, moral: str) -> None:
        """Set character alignment."""
        self._alignment_ethical = ethical
        self._alignment_moral = moral
    
    def set_appearance(self, key: str, value: Any) -> None:
        """Set appearance attribute."""
        if key == "height":
            self._height = value
        elif key == "weight":
            self._weight = value
        elif key == "age":
            self._age = value
        elif key == "eyes":
            self._eyes = value
        elif key == "hair":
            self._hair = value
        elif key == "skin":
            self._skin = value
        elif key == "gender":
            self._gender = value
        elif key == "pronouns":
            self._pronouns = value
        elif key == "size":
            self._size = value
            self.calculate_all_derived_stats()  # Size can affect game mechanics
        else:
            raise ValueError(f"Unknown appearance attribute: {key}")
    
    def set_base_ability_score(self, ability: str, value: int) -> None:
        """Set the base value for a specific ability score."""
        ability_obj = self.get_ability_score_object(ability)
        ability_obj.base_score = value
        self.calculate_all_derived_stats()
    
    def set_skill_proficiency(self, skill: str, level: ProficiencyLevel) -> None:
        """Set proficiency level for a skill."""
        self._skill_proficiencies[skill] = level
        self.calculate_all_derived_stats()
    
    def set_saving_throw_proficiency(self, ability: str, level: ProficiencyLevel) -> None:
        """Set proficiency level for a saving throw."""
        self._saving_throw_proficiencies[ability] = level
        self.calculate_all_derived_stats()
    
    def add_weapon_proficiency(self, weapon_type: str) -> None:
        """Add weapon proficiency."""
        self._weapon_proficiencies.add(weapon_type)
        self.calculate_all_derived_stats()
    
    def add_armor_proficiency(self, armor_type: str) -> None:
        """Add armor proficiency."""
        self._armor_proficiencies.add(armor_type)
        self.calculate_all_derived_stats()
    
    def set_tool_proficiency(self, tool: str, level: ProficiencyLevel) -> None:
        """Set proficiency level for a tool."""
        self._tool_proficiencies[tool] = level
        self.calculate_all_derived_stats()
    
    def add_language(self, language: str) -> None:
        """Add a known language."""
        self._languages.add(language)
    
    def add_species_trait(self, trait_name: str, trait_details: Any) -> None:
        """Add a species trait."""
        self._species_traits[trait_name] = trait_details
        self.calculate_all_derived_stats()
    
    def add_class_feature(self, feature_name: str, feature_details: Any) -> None:
        """Add a class feature."""
        self._class_features[feature_name] = feature_details
        self.calculate_all_derived_stats()
    
    def set_background_feature(self, feature: str) -> None:
        """Set background feature."""
        self._background_feature = feature
        self.calculate_all_derived_stats()
    
    def add_feat(self, feat: str) -> None:
        """Add a feat."""
        if feat not in self._feats:
            self._feats.append(feat)
            self.calculate_all_derived_stats()
    
    def set_base_speed(self, speed: int) -> None:
        """Set base walking speed."""
        self._base_speed = speed
        self.calculate_all_derived_stats()
    
    def set_vision_type(self, vision_type: str, range_feet: int) -> None:
        """Set a vision type and its range."""
        self._base_vision_types[vision_type] = range_feet
    
    def set_movement_type(self, movement_type: str, speed: int) -> None:
        """Set a movement type and its speed."""
        self._base_movement_types[movement_type] = speed
        self.calculate_all_derived_stats()
    
    def add_base_resistance(self, damage_type: str) -> None:
        """Add base damage resistance."""
        self._base_damage_resistances.add(damage_type.lower())
        self.calculate_all_derived_stats()
    
    def add_base_immunity(self, damage_type: str) -> None:
        """Add base damage immunity."""
        self._base_damage_immunities.add(damage_type.lower())
        self.calculate_all_derived_stats()
    
    def add_base_vulnerability(self, damage_type: str) -> None:
        """Add base damage vulnerability."""
        self._base_damage_vulnerabilities.add(damage_type.lower())
        self.calculate_all_derived_stats()
    
    def add_base_condition_immunity(self, condition: str) -> None:
        """Add base condition immunity."""
        self._base_condition_immunities.add(condition.lower())
        self.calculate_all_derived_stats()
    
    def set_spellcasting_ability(self, ability: str) -> None:
        """Set primary spellcasting ability."""
        self._spellcasting_ability = ability.lower()
        self.calculate_all_derived_stats()
    
    def add_spellcasting_class(self, class_name: str, details: Dict[str, Any]) -> None:
        """Add a spellcasting class with details."""
        self._spellcasting_classes[class_name] = details
        self.calculate_all_derived_stats()
    
    def set_ritual_casting(self, class_name: str, has_ritual: bool) -> None:
        """Set whether a class has ritual casting ability."""
        self._ritual_casting_classes[class_name] = has_ritual
    
    def add_personality_trait(self, trait: str) -> None:
        """Add a personality trait."""
        self._personality_traits.append(trait)
    
    def add_ideal(self, ideal: str) -> None:
        """Add an ideal."""
        self._ideals.append(ideal)
    
    def add_bond(self, bond: str) -> None:
        """Add a bond."""
        self._bonds.append(bond)
    
    def add_flaw(self, flaw: str) -> None:
        """Add a flaw."""
        self._flaws.append(flaw)
    
    def set_backstory(self, backstory: str) -> None:
        """Set character backstory."""
        self._backstory = backstory
    
    def set_hit_dice(self, dice_type: str, count: int) -> None:
        """Set hit dice for a specific type."""
        self._hit_dice[dice_type] = count
        # Initialize remaining hit dice
        if dice_type not in self._hit_dice_remaining:
            self._hit_dice_remaining[dice_type] = count
        self.calculate_all_derived_stats()
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        if key == "creation_date":
            self._creation_date = value
        elif key == "player_name":
            self._player_name = value
        elif key == "campaign":
            self._campaign = value
        else:
            raise ValueError(f"Unknown metadata key: {key}")
    
    def add_source(self, source: str) -> None:
        """Add a source book used for this character."""
        self._sources_used.add(source)
    
    #============================================================
    # IN-GAME INDEPENDENT VARIABLE METHODS
    #============================================================
    
    # Experience Points
    def add_experience_points(self, xp: int) -> int:
        """Add experience points and return new total."""
        self._experience_points += xp
        # Check if this triggers a level up opportunity
        return self._experience_points
    
    def set_experience_points(self, xp: int) -> None:
        """Set experience points to a specific value."""
        self._experience_points = max(0, xp)
    
    # Hit Points
    def set_current_hit_points(self, hp: int) -> None:
        """Set current hit points."""
        self._current_hit_points = min(hp, self._max_hit_points)
    
    def add_temporary_hit_points(self, temp_hp: int) -> None:
        """Add temporary hit points (doesn't stack, takes highest value)."""
        self._temporary_hit_points = max(self._temporary_hit_points, temp_hp)
    
    def remove_temporary_hit_points(self) -> None:
        """Remove all temporary hit points."""
        self._temporary_hit_points = 0
    
    def take_damage(self, damage: int) -> Dict[str, int]:
        """
        Apply damage to the character.
        Returns a dictionary with the breakdown of how damage was applied.
        """
        result = {
            "temp_hp_damage": 0,
            "hp_damage": 0,
            "overkill": 0
        }
        
        # First apply damage to temporary HP
        if self._temporary_hit_points > 0:
            temp_damage = min(damage, self._temporary_hit_points)
            self._temporary_hit_points -= temp_damage
            damage -= temp_damage
            result["temp_hp_damage"] = temp_damage
        
        # Then apply to regular HP
        if damage > 0:
            self._current_hit_points -= damage
            result["hp_damage"] = damage
            
            # Check for overkill
            if self._current_hit_points < 0:
                result["overkill"] = abs(self._current_hit_points)
                self._current_hit_points = 0
        
        return result
    
    def heal(self, healing: int) -> int:
        """Heal the character and return amount healed."""
        old_hp = self._current_hit_points
        self._current_hit_points = min(self._max_hit_points, old_hp + healing)
        return self._current_hit_points - old_hp
    
    def set_hit_point_maximum_modifier(self, modifier: int) -> None:
        """Set modifier to maximum hit points."""
        self._hit_point_maximum_modifier = modifier
        self.calculate_max_hit_points()
    
    # Hit Dice
    def set_hit_dice_remaining(self, dice_type: str, count: int) -> None:
        """Set remaining hit dice for a specific type."""
        max_dice = self._hit_dice.get(dice_type, 0)
        self._hit_dice_remaining[dice_type] = min(count, max_dice)
    
    # Spell Slots
    def set_spell_slots_total(self, level: int, count: int) -> None:
        """Set total spell slots for a specific level."""
        if count > 0:
            self._spell_slots_total[level] = count
            if level not in self._spell_slots_remaining:
                self._spell_slots_remaining[level] = count
        elif level in self._spell_slots_total:
            del self._spell_slots_total[level]
            if level in self._spell_slots_remaining:
                del self._spell_slots_remaining[level]
    
    def set_spell_slots_remaining(self, level: int, count: int) -> None:
        """Set remaining spell slots for a specific level."""
        total = self._spell_slots_total.get(level, 0)
        self._spell_slots_remaining[level] = min(count, total)
    
    def use_spell_slot(self, level: int) -> bool:
        """Use a spell slot of the specified level. Returns success."""
        if level not in self._spell_slots_remaining or self._spell_slots_remaining[level] <= 0:
            return False
        
        self._spell_slots_remaining[level] -= 1
        return True
    
    def add_spell_known(self, level: int, spell_name: str) -> None:
        """Add a spell to known spells."""
        if level not in self._spells_known:
            self._spells_known[level] = []
        
        if spell_name not in self._spells_known[level]:
            self._spells_known[level].append(spell_name)
    
    def remove_spell_known(self, level: int, spell_name: str) -> bool:
        """Remove a spell from known spells. Returns success."""
        if level in self._spells_known and spell_name in self._spells_known[level]:
            self._spells_known[level].remove(spell_name)
            return True
        return False
    
    def prepare_spell(self, spell_name: str) -> None:
        """Add a spell to prepared spells."""
        if spell_name not in self._spells_prepared:
            self._spells_prepared.append(spell_name)
    
    def unprepare_spell(self, spell_name: str) -> bool:
        """Remove a spell from prepared spells. Returns success."""
        if spell_name in self._spells_prepared:
            self._spells_prepared.remove(spell_name)
            return True
        return False
    
    def add_ritual_spell(self, spell_name: str) -> None:
        """Add a spell to ritual book."""
        if spell_name not in self._ritual_book_spells:
            self._ritual_book_spells.append(spell_name)
    
    # Equipment
    def equip_armor(self, armor_name: str) -> bool:
        """Equip armor if proficient. Returns success."""
        # Check proficiency
        armor_type = self._get_armor_type(armor_name)
        if armor_type not in self._armor_proficiencies:
            return False
        
        self._armor = armor_name
        self.calculate_armor_class()
        return True
    
    def unequip_armor(self) -> None:
        """Unequip armor."""
        self._armor = None
        self.calculate_armor_class()
    
    def equip_shield(self) -> bool:
        """Equip a shield if proficient. Returns success."""
        if "shield" not in self._armor_proficiencies:
            return False
        
        self._shield = True
        self.calculate_armor_class()
        return True
    
    def unequip_shield(self) -> None:
        """Unequip shield."""
        self._shield = False
        self.calculate_armor_class()
    
    def add_weapon(self, weapon_data: Dict[str, Any]) -> int:
        """Add a weapon and return its index."""
        self._weapons.append(weapon_data)
        return len(self._weapons) - 1
    
    def remove_weapon(self, index: int) -> bool:
        """Remove a weapon by index. Returns success."""
        if 0 <= index < len(self._weapons):
            self._weapons.pop(index)
            return True
        return False
    
    def add_equipment(self, item_data: Dict[str, Any]) -> int:
        """Add equipment and return its index."""
        self._equipment.append(item_data)
        return len(self._equipment) - 1
    
    def remove_equipment(self, index: int) -> bool:
        """Remove equipment by index. Returns success."""
        if 0 <= index < len(self._equipment):
            self._equipment.pop(index)
            return True
        return False
    
    # Currency
    def add_currency(self, currency_type: str, amount: int) -> bool:
        """Add currency of specified type. Returns success."""
        if currency_type not in self._currency:
            return False
        
        self._currency[currency_type] += amount
        return True
    
    def remove_currency(self, currency_type: str, amount: int) -> bool:
        """Remove currency if enough is available. Returns success."""
        if currency_type not in self._currency or self._currency[currency_type] < amount:
            return False
        
        self._currency[currency_type] -= amount
        return True
    
    def convert_currency(self, from_type: str, to_type: str, amount: int) -> bool:
        """Convert currency from one type to another. Returns success."""
        # Currency conversion rates
        conversion_rates = {
            ("copper", "silver"): 0.1,
            ("copper", "electrum"): 0.05,
            ("copper", "gold"): 0.01,
            ("copper", "platinum"): 0.001,
            ("silver", "copper"): 10,
            ("silver", "electrum"): 0.5,
            ("silver", "gold"): 0.1,
            ("silver", "platinum"): 0.01,
            ("electrum", "copper"): 20,
            ("electrum", "silver"): 2,
            ("electrum", "gold"): 0.5,
            ("electrum", "platinum"): 0.05,
            ("gold", "copper"): 100,
            ("gold", "silver"): 10,
            ("gold", "electrum"): 2,
            ("gold", "platinum"): 0.1,
            ("platinum", "copper"): 1000,
            ("platinum", "silver"): 100,
            ("platinum", "electrum"): 50,
            ("platinum", "gold"): 10
        }
        
        if from_type not in self._currency or to_type not in self._currency:
            return False
        
        if self._currency[from_type] < amount:
            return False
        
        rate = conversion_rates.get((from_type, to_type))
        if rate is None:
            return False
        
        converted_amount = int(amount * rate)
        if converted_amount <= 0:
            return False
        
        self._currency[from_type] -= amount
        self._currency[to_type] += converted_amount
        return True
    
    # Magic Item Attunement
    def attune_to_item(self, item_name: str) -> bool:
        """Attempt to attune to a magic item. Returns success."""
        if len(self._attuned_items) >= self._max_attunement_slots:
            return False
        
        if item_name not in self._attuned_items:
            self._attuned_items.append(item_name)
            # Apply any bonuses from the item
            self.calculate_all_derived_stats()
            return True
        
        return False
    
    def unattune_from_item(self, item_name: str) -> bool:
        """Unattune from a magic item. Returns success."""
        if item_name in self._attuned_items:
            self._attuned_items.remove(item_name)
            # Remove any bonuses from the item
            self.calculate_all_derived_stats()
            return True
        
        return False
    
    def set_max_attunement_slots(self, slots: int) -> None:
        """Set maximum attunement slots."""
        self._max_attunement_slots = slots
    
    # Conditions
    def add_condition(self, condition: str, duration: Optional[int] = None, 
                     source: Optional[str] = None, end_trigger: Optional[str] = None) -> bool:
        """Apply a condition to the character. Returns success."""
        if condition in self._base_condition_immunities:
            return False  # Character is immune
        
        self._active_conditions[condition] = {
            "duration": duration,  # None = indefinite, int = rounds
            "source": source,      # What caused the condition
            "end_trigger": end_trigger  # "save", "action", etc.
        }
        
        # Apply condition effects
        self.calculate_all_derived_stats()
        return True
    
    def remove_condition(self, condition: str) -> bool:
        """Remove a condition from the character. Returns success."""
        if condition in self._active_conditions:
            del self._active_conditions[condition]
            # Recalculate stats after condition removal
            self.calculate_all_derived_stats()
            return True
        return False
    
    def has_condition(self, condition: str) -> bool:
        """Check if character has a specific condition."""
        return condition in self._active_conditions
    
    # Exhaustion
    def add_exhaustion(self, levels: int = 1) -> int:
        """Add levels of exhaustion. Returns new level."""
        old_level = self._exhaustion_level
        self._exhaustion_level = min(6, old_level + levels)
        # Apply exhaustion effects
        self.calculate_all_derived_stats()
        return self._exhaustion_level
    
    def reduce_exhaustion(self, levels: int = 1) -> int:
        """Reduce levels of exhaustion. Returns new level."""
        old_level = self._exhaustion_level
        self._exhaustion_level = max(0, old_level - levels)
        # Apply exhaustion effects
        self.calculate_all_derived_stats()
        return self._exhaustion_level
    
    # Temporary Defenses
    def add_temp_resistance(self, damage_type: str) -> None:
        """Add temporary damage resistance."""
        self._temp_damage_resistances.add(damage_type.lower())
    
    def remove_temp_resistance(self, damage_type: str) -> bool:
        """Remove temporary damage resistance. Returns success."""
        damage_type = damage_type.lower()
        if damage_type in self._temp_damage_resistances:
            self._temp_damage_resistances.remove(damage_type)
            return True
        return False
    
    def add_temp_immunity(self, damage_type: str) -> None:
        """Add temporary damage immunity."""
        self._temp_damage_immunities.add(damage_type.lower())
    
    def remove_temp_immunity(self, damage_type: str) -> bool:
        """Remove temporary damage immunity. Returns success."""
        damage_type = damage_type.lower()
        if damage_type in self._temp_damage_immunities:
            self._temp_damage_immunities.remove(damage_type)
            return True
        return False
    
    def add_temp_vulnerability(self, damage_type: str) -> None:
        """Add temporary damage vulnerability."""
        self._temp_damage_vulnerabilities.add(damage_type.lower())
    
    def remove_temp_vulnerability(self, damage_type: str) -> bool:
        """Remove temporary damage vulnerability. Returns success."""
        damage_type = damage_type.lower()
        if damage_type in self._temp_damage_vulnerabilities:
            self._temp_damage_vulnerabilities.remove(damage_type)
            return True
        return False
    
    def add_temp_condition_immunity(self, condition: str) -> None:
        """Add temporary condition immunity."""
        self._temp_condition_immunities.add(condition.lower())
    
    def remove_temp_condition_immunity(self, condition: str) -> bool:
        """Remove temporary condition immunity. Returns success."""
        condition = condition.lower()
        if condition in self._temp_condition_immunities:
            self._temp_condition_immunities.remove(condition)
            return True
        return False
    
    # Action Economy
    def reset_action_economy(self) -> None:
        """Reset action economy for a new turn."""
        self._actions_used = 0
        self._bonus_actions_used = 0
        self._reactions_used = 0
    
    def use_action(self, action_name: str) -> bool:
        """Use an action if available. Returns success."""
        if action_name not in self._available_actions or self._actions_used >= self._actions_per_turn:
            return False
        
        self._actions_used += 1
        # Implement action-specific logic here
        return True
    
    def use_bonus_action(self, action_name: str) -> bool:
        """Use a bonus action if available. Returns success."""
        if self._bonus_actions_used >= self._bonus_actions_per_turn:
            return False
        
        self._bonus_actions_used += 1
        # Implement bonus action-specific logic here
        return True
    
    def use_reaction(self, reaction_name: str, **context) -> bool:
        """Use a reaction if available. Returns success."""
        if reaction_name not in self._available_reactions or self._reactions_used >= self._reactions_per_turn:
            return False
        
        self._reactions_used += 1
        # Implement reaction-specific logic here
        return True
    
    # Beast Companion
    def set_beast_companion(self, companion_data: Dict[str, Any]) -> None:
        """Set beast companion data."""
        self._beast_companion = companion_data
    
    def remove_beast_companion(self) -> None:
        """Remove beast companion."""
        self._beast_companion = None
    
    # Notes
    def add_note(self, category: str, content: str) -> bool:
        """Add a note to a category. Returns success."""
        if category not in self._notes:
            return False
        
        # Append to existing notes with a separator if there are existing notes
        if self._notes[category]:
            self._notes[category] += f"\n\n{content}"
        else:
            self._notes[category] = content
        
        return True
    
    def set_note(self, category: str, content: str) -> bool:
        """Set note content for a category. Returns success."""
        if category not in self._notes:
            return False
        
        self._notes[category] = content
        return True
    
    def get_note(self, category: str) -> str:
        """Get notes for a category."""
        return self._notes.get(category, "")
    
    # Last Updated
    def update_timestamp(self, timestamp: str) -> None:
        """Update the last updated timestamp."""
        self._last_updated = timestamp
    
    #============================================================
    # RESTING MECHANICS
    #============================================================
    
    def take_short_rest(self, hit_dice_spent: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Perform a short rest, optionally spending hit dice to recover HP.
        
        Args:
            hit_dice_spent: Dictionary mapping hit die type to number spent
        
        Returns:
            Dict with results of short rest
        """
        result = {
            "hp_recovered": 0,
            "hit_dice_spent": {},
            "abilities_refreshed": []
        }
        
        # Process hit dice recovery
        if hit_dice_spent:
            for die_type, count in hit_dice_spent.items():
                # Validate we have enough hit dice
                available = self._hit_dice_remaining.get(die_type, 0)
                if available < count:
                    raise ValueError(f"Not enough {die_type} hit dice remaining")
                
                # Calculate HP recovery (die average + CON mod per die)
                die_size = int(die_type.replace('d', ''))
                con_mod = self._constitution.modifier
                hp_per_die = (die_size // 2) + 1 + con_mod
                hp_recovered = count * hp_per_die
                
                # Update tracking
                self._hit_dice_remaining[die_type] = available - count
                result["hp_recovered"] += hp_recovered
                result["hit_dice_spent"][die_type] = count
        
        # Recover HP
        self._current_hit_points = min(self._max_hit_points, 
                                     self._current_hit_points + result["hp_recovered"])
        
        # Refresh short-rest abilities
        # This would check class features that refresh on short rest
        # For example, a Monk's Ki points or a Wizard's Arcane Recovery
        
        # Check for features that reduce exhaustion on short rest
        if "Deft Explorer: Tireless" in self._class_features and self._exhaustion_level > 0:
            self.reduce_exhaustion(1)
            result["abilities_refreshed"].append("Deft Explorer: Tireless (reduced exhaustion)")
        
        return result
    
    def take_long_rest(self) -> Dict[str, Any]:
        """
        Perform a long rest, restoring HP, spell slots, and other resources.
        
        Returns:
            Dict with results of long rest
        """
        result = {
            "hp_recovered": 0,
            "hit_dice_recovered": {},
            "abilities_refreshed": [],
            "spell_slots_recovered": {},
            "exhaustion_reduced": 0
        }
        
        # Recover all HP
        old_hp = self._current_hit_points
        self._current_hit_points = self._max_hit_points
        result["hp_recovered"] = self._max_hit_points - old_hp
        
        # Recover hit dice (up to half total)
        for die_type, total in self._hit_dice.items():
            max_recovery = max(1, total // 2)
            current = self._hit_dice_remaining.get(die_type, 0)
            recovered = min(max_recovery, total - current)
            
            if recovered > 0:
                self._hit_dice_remaining[die_type] = current + recovered
                result["hit_dice_recovered"][die_type] = recovered
        
        # Restore all spell slots
        for level, total in self._spell_slots_total.items():
            old_slots = self._spell_slots_remaining.get(level, 0)
            self._spell_slots_remaining[level] = total
            result["spell_slots_recovered"][level] = total - old_slots
        
        # Reduce exhaustion by 1 level
        if self._exhaustion_level > 0:
            old_level = self._exhaustion_level
            self.reduce_exhaustion(1)
            result["exhaustion_reduced"] = old_level - self._exhaustion_level
        
        # Reset temporary ability score effects that end on long rest
        # For example, temporarily from spells like Enhance Ability
        # Don't reset permanent bonuses like from items
        
        return result
    
    #============================================================
    # DEPENDENT VARIABLE METHODS - Calculations
    #============================================================
    
    @property
    def total_level(self) -> int:
        """Calculate total character level from all classes."""
        return sum(self._character_class.values()) if self._character_class else self._level
    
    @property
    def primary_class(self) -> str:
        """Determine primary class (highest level or first class)."""
        if not self._character_class:
            return ""
        return max(self._character_class.items(), key=lambda x: x[1])[0]
    
    def calculate_all_derived_stats(self) -> None:
        """Calculate all derived statistics in the proper order."""
        # Calculate proficiency bonus first (used by many other calculations)
        self.calculate_proficiency_bonus()
        
        # Then calculate everything else
        self.calculate_initiative()
        self.calculate_armor_class()
        self.calculate_max_hit_points()
        self.calculate_passive_perception()
        self.calculate_passive_investigation()
        self.calculate_passive_insight()
        self.calculate_spell_save_dc()
        self.calculate_spell_attack_bonus()
        self.update_available_actions()
        
        # If current hit points are unset, set them to max
        if self._current_hit_points == 0 and self._max_hit_points > 0:
            self._current_hit_points = self._max_hit_points
    
    def calculate_proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on character level."""
        level = self.total_level
        self._proficiency_bonus = 2 + ((level - 1) // 4)
        return self._proficiency_bonus
    
    def calculate_initiative(self) -> int:
        """Calculate initiative bonus."""
        dex_mod = self._dexterity.modifier
        
        # Check for feats that modify initiative
        initiative_bonus = 0
        if "Alert" in self._feats:
            initiative_bonus += 5
        
        # Check for class features that modify initiative
        if "Bard" in self._character_class and self.get_level_in_class("Bard") >= 2:
            # Jack of All Trades
            if self._proficiency_bonus > 0:
                initiative_bonus += self._proficiency_bonus // 2
        
        # Remarkable Athlete for Champion Fighters
        if "Fighter" in self._character_class and self.get_subclass("Fighter") == "Champion" and self.get_level_in_class("Fighter") >= 7:
            if self._proficiency_bonus > 0:
                initiative_bonus += self._proficiency_bonus // 2
        
        self._initiative = dex_mod + initiative_bonus
        return self._initiative
    
    def calculate_armor_class(self) -> int:
        """Calculate armor class based on equipment and abilities."""
        base_ac = 10
        dex_mod = self._dexterity.modifier
        
        # Check for worn armor
        if self._armor is not None:
            # This would require a more detailed armor database
            # For now using a simplified approach
            armor_type = self._armor.lower()
            
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
            if "Barbarian" in self._character_class:
                con_mod = self._constitution.modifier
                barbarian_ac = 10 + dex_mod + con_mod
                base_ac = max(base_ac, barbarian_ac)
                
            if "Monk" in self._character_class:
                wis_mod = self._wisdom.modifier
                monk_ac = 10 + dex_mod + wis_mod
                base_ac = max(base_ac, monk_ac)
        
        # Add shield bonus
        if self._shield:
            base_ac += 2
        
        # Check for special features/feats that affect AC
        if "defensive_fighting_style" in self._class_features:
            if any(self._is_armor_worn("medium") or self._is_armor_worn("heavy")):
                base_ac += 1
        
        self._armor_class = base_ac
        return self._armor_class
    
    def calculate_max_hit_points(self) -> int:
        """Calculate maximum hit points."""
        if not self._character_class:
            self._max_hit_points = 0
            return 0
        
        con_mod = self._constitution.modifier
        total = 0
        
        # Process each class level
        for class_name, level in self._character_class.items():
            if level <= 0:
                continue
                
            # Get hit die for this class
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
        total += self._hit_point_maximum_modifier
        
        self._max_hit_points = max(1, total)  # Minimum 1 hit point
        return self._max_hit_points
    
    def calculate_passive_perception(self) -> int:
        """Calculate passive Perception score."""
        wis_mod = self._wisdom.modifier
        prof_bonus = 0
        
        # Check for proficiency/expertise in Perception
        prof_level = self.get_skill_proficiency("Perception")
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self._proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self._proficiency_bonus * 2
        
        # Check for Observant feat
        feat_bonus = 5 if "Observant" in self._feats else 0
        
        self._passive_perception = 10 + wis_mod + prof_bonus + feat_bonus
        return self._passive_perception
    
    def calculate_passive_investigation(self) -> int:
        """Calculate passive Investigation score."""
        int_mod = self._intelligence.modifier
        prof_bonus = 0
        
        # Check for proficiency/expertise in Investigation
        prof_level = self.get_skill_proficiency("Investigation")
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self._proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self._proficiency_bonus * 2
        
        # Check for Observant feat
        feat_bonus = 5 if "Observant" in self._feats else 0
        
        self._passive_investigation = 10 + int_mod + prof_bonus + feat_bonus
        return self._passive_investigation
    
    def calculate_passive_insight(self) -> int:
        """Calculate passive Insight score."""
        wis_mod = self._wisdom.modifier
        prof_bonus = 0
        
        # Check for proficiency/expertise in Insight
        prof_level = self.get_skill_proficiency("Insight")
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self._proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self._proficiency_bonus * 2
        
        self._passive_insight = 10 + wis_mod + prof_bonus
        return self._passive_insight
    
    def calculate_spell_save_dc(self) -> int:
        """Calculate spell save DC."""
        if not self._spellcasting_ability:
            self._spell_save_dc = 0
            return 0
        
        ability_mod = self.get_ability_modifier(self._spellcasting_ability)
        self._spell_save_dc = 8 + self._proficiency_bonus + ability_mod
        return self._spell_save_dc
    
    def calculate_spell_attack_bonus(self) -> int:
        """Calculate spell attack bonus."""
        if not self._spellcasting_ability:
            self._spell_attack_bonus = 0
            return 0
        
        ability_mod = self.get_ability_modifier(self._spellcasting_ability)
        self._spell_attack_bonus = self._proficiency_bonus + ability_mod
        return self._spell_attack_bonus
    
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
        ability_mod = self.get_ability_modifier(ability)
        
        # Check for proficiency/expertise
        prof_level = self.get_skill_proficiency(skill_name)
        prof_bonus = 0
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self._proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self._proficiency_bonus * 2
            
        # Check for Jack of All Trades (Bard feature)
        if prof_level == ProficiencyLevel.NONE and "Bard" in self._character_class and self.get_level_in_class("Bard") >= 2:
            prof_bonus = self._proficiency_bonus // 2
            
        # Check for Remarkable Athlete (Champion Fighter feature)
        if prof_level == ProficiencyLevel.NONE and "Fighter" in self._character_class and self.get_subclass("Fighter") == "Champion" and self.get_level_in_class("Fighter") >= 7:
            if ability in ["strength", "dexterity", "constitution"]:
                prof_bonus = self._proficiency_bonus // 2
            
        # Check for effects from conditions
        condition_mod = 0
        if self._exhaustion_level >= 1:
            condition_mod -= 1  # Disadvantage effectively -5, but we're just returning the modifier
        
        return ability_mod + prof_bonus + condition_mod
    
    def calculate_saving_throw_bonus(self, ability: str) -> int:
        """Calculate bonus for a specific saving throw."""
        ability_mod = self.get_ability_modifier(ability)
        
        # Check for proficiency
        prof_level = self.get_saving_throw_proficiency(ability)
        prof_bonus = 0
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self._proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:  # Rare, but possible with feats or magic items
            prof_bonus = self._proficiency_bonus * 2
            
        # Check for special features
        feature_bonus = 0
        
        # Paladin's Aura of Protection
        if "Paladin" in self._character_class and self.get_level_in_class("Paladin") >= 6:
            # Aura of Protection applies to all saves
            feature_bonus += self.get_ability_modifier("charisma")
        
        # Check for magic item bonuses (simplified, would need item database)
        item_bonus = 0
        for item in self._attuned_items:
            if "cloak of protection" in item.lower():
                item_bonus += 1
            elif "ring of protection" in item.lower():
                item_bonus += 1
                
        return ability_mod + prof_bonus + feature_bonus + item_bonus
    
    def calculate_weapon_attack_bonus(self, weapon_index: int) -> int:
        """Calculate attack bonus for a specific weapon."""
        if weapon_index < 0 or weapon_index >= len(self._weapons):
            return 0
            
        weapon = self._weapons[weapon_index]
        
        # Determine which ability modifier to use
        ability = "strength"
        if "finesse" in weapon.get("properties", []) or weapon.get("weapon_type") == "ranged":
            # Use higher of STR or DEX for finesse weapons, or DEX for ranged
            str_mod = self.get_ability_modifier("strength")
            dex_mod = self.get_ability_modifier("dexterity")
            if dex_mod > str_mod:
                ability = "dexterity"
        
        ability_mod = self.get_ability_modifier(ability)
        
        # Check for proficiency
        prof_bonus = 0
        weapon_name = weapon.get("name", "").lower()
        weapon_type = weapon.get("weapon_type", "").lower()
        
        # Check if proficient with this specific weapon or weapon category
        is_proficient = False
        for prof in self._weapon_proficiencies:
            prof_lower = prof.lower()
            if (prof_lower in weapon_name or 
                prof_lower == "all" or
                prof_lower == weapon_type or
                (prof_lower == "martial weapons" and weapon.get("is_martial", False)) or
                (prof_lower == "simple weapons" and not weapon.get("is_martial", False))):
                is_proficient = True
                break
                
        if is_proficient:
            prof_bonus = self._proficiency_bonus
        
        # Check for magic bonus
        magic_bonus = weapon.get("magic_bonus", 0)
        
        # Check for other bonuses (fighting styles, etc.)
        other_bonus = 0
        if "archery" in self._class_features and weapon.get("weapon_type") == "ranged":
            other_bonus += 2
            
        # Apply penalties if conditions warrant
        condition_penalty = 0
        if self._exhaustion_level >= 3:
            condition_penalty -= 1  # Disadvantage on attack rolls
        
        return ability_mod + prof_bonus + magic_bonus + other_bonus + condition_penalty
    
    def calculate_weapon_damage_bonus(self, weapon_index: int) -> int:
        """Calculate damage bonus for a specific weapon."""
        if weapon_index < 0 or weapon_index >= len(self._weapons):
            return 0
            
        weapon = self._weapons[weapon_index]
        
        # Determine which ability modifier to use (same logic as attack bonus)
        ability = "strength"
        if "finesse" in weapon.get("properties", []) or weapon.get("weapon_type") == "ranged":
            str_mod = self.get_ability_modifier("strength")
            dex_mod = self.get_ability_modifier("dexterity")
            if dex_mod > str_mod:
                ability = "dexterity"
        
        ability_mod = self.get_ability_modifier(ability)
        
        # Check for magic bonus
        magic_bonus = weapon.get("magic_bonus", 0)
        
        # Check for fighting styles
        style_bonus = 0
        if "dueling" in self._class_features and not "two_handed" in weapon.get("properties", []) and not self._shield:
            style_bonus = 2
        elif "great_weapon_fighting" in self._class_features and "two_handed" in weapon.get("properties", []):
            # No flat bonus, but allows rerolling 1s and 2s on damage dice
            pass
        elif "archery" in self._class_features and weapon.get("weapon_type") == "ranged":
            # Archery only affects attack rolls, not damage
            pass
        
        return ability_mod + magic_bonus + style_bonus
    
    def calculate_spell_slots(self) -> Dict[int, int]:
        """Calculate available spell slots based on class and level."""
        spell_slots = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
        
        # Handle Warlock separately (they use Pact Magic, not Spellcasting)
        warlock_level = self.get_level_in_class("Warlock")
        
        # Full casters: Bard, Cleric, Druid, Sorcerer, Wizard
        full_caster_levels = sum([
            self.get_level_in_class("Bard"),
            self.get_level_in_class("Cleric"),
            self.get_level_in_class("Druid"),
            self.get_level_in_class("Sorcerer"),
            self.get_level_in_class("Wizard")
        ])
        
        # Half casters: Paladin, Ranger (round down)
        half_caster_levels = sum([
            self.get_level_in_class("Paladin") // 2,
            self.get_level_in_class("Ranger") // 2
        ])
        
        # Third casters: Arcane Trickster (Rogue), Eldritch Knight (Fighter) (round down)
        third_caster_levels = sum([
            (self.get_level_in_class("Rogue") if self.get_subclass("Rogue") == "Arcane Trickster" else 0) // 3,
            (self.get_level_in_class("Fighter") if self.get_subclass("Fighter") == "Eldritch Knight" else 0) // 3
        ])
        
        # Calculate effective spellcasting level
        effective_level = full_caster_levels + half_caster_levels + third_caster_levels
        
        # Apply multiclass spellcaster rules from PHB
        if effective_level > 0:
            # Table lookup based on PHB multiclass spellcaster table
            slots_by_level = {
                1: {1: 2},
                2: {1: 3},
                3: {1: 4, 2: 2},
                4: {1: 4, 2: 3},
                5: {1: 4, 2: 3, 3: 2},
                6: {1: 4, 2: 3, 3: 3},
                7: {1: 4, 2: 3, 3: 3, 4: 1},
                8: {1: 4, 2: 3, 3: 3, 4: 2},
                9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
                10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
                11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
                12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
                13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
                14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
                15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
                16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
                17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
                18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
                19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
                20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1}
            }
            
            # Use the appropriate row from the table
            effective_level = min(20, max(1, effective_level))
            level_slots = slots_by_level.get(effective_level, {})
            
            for level, count in level_slots.items():
                spell_slots[level] = count
        
        # Handle Warlock Pact Magic
        if warlock_level > 0:
            warlock_slots = {
                1: {"slot_level": 1, "num_slots": 1},
                2: {"slot_level": 1, "num_slots": 2},
                3: {"slot_level": 2, "num_slots": 2},
                4: {"slot_level": 2, "num_slots": 2},
                5: {"slot_level": 3, "num_slots": 2},
                6: {"slot_level": 3, "num_slots": 2},
                7: {"slot_level": 4, "num_slots": 2},
                8: {"slot_level": 4, "num_slots": 2},
                9: {"slot_level": 5, "num_slots": 2},
                10: {"slot_level": 5, "num_slots": 2},
                11: {"slot_level": 5, "num_slots": 3},
                12: {"slot_level": 5, "num_slots": 3},
                13: {"slot_level": 5, "num_slots": 3},
                14: {"slot_level": 5, "num_slots": 3},
                15: {"slot_level": 5, "num_slots": 3},
                16: {"slot_level": 5, "num_slots": 3},
                17: {"slot_level": 5, "num_slots": 4},
                18: {"slot_level": 5, "num_slots": 4},
                19: {"slot_level": 5, "num_slots": 4},
                20: {"slot_level": 5, "num_slots": 4}
            }
            
            warlock_info = warlock_slots.get(warlock_level, {"slot_level": 1, "num_slots": 1})
            spell_slots[warlock_info["slot_level"]] += warlock_info["num_slots"]
        
        # Update the character sheet's spell slot information
        for level, count in spell_slots.items():
            if count > 0:
                self._spell_slots_total[level] = count
                # Initialize remaining slots if needed
                if level not in self._spell_slots_remaining:
                    self._spell_slots_remaining[level] = count
        
        return spell_slots
    
    def calculate_spells_known_limit(self, class_name: str) -> int:
        """Calculate how many spells a character can know for classes with fixed known spells."""
        level = self.get_level_in_class(class_name)
        if level <= 0:
            return 0
            
        # Different classes have different spells known progression
        if class_name == "Bard":
            # Bard spells known table
            spells_known = {
                1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11, 9: 12, 10: 14,
                11: 15, 12: 15, 13: 16, 14: 18, 15: 19, 16: 19, 17: 20, 18: 22, 19: 22, 20: 22
            }
            return spells_known.get(level, 0)
            
        elif class_name == "Ranger":
            # Ranger spells known table
            spells_known = {
                1: 0, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5, 8: 5, 9: 6, 10: 6,
                11: 7, 12: 7, 13: 8, 14: 8, 15: 9, 16: 9, 17: 10, 18: 10, 19: 11, 20: 11
            }
            return spells_known.get(level, 0)
            
        elif class_name == "Sorcerer":
            # Sorcerer spells known table
            spells_known = {
                1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11,
                11: 12, 12: 12, 13: 13, 14: 13, 15: 14, 16: 14, 17: 15, 18: 15, 19: 15, 20: 15
            }
            return spells_known.get(level, 0)
            
        elif class_name == "Warlock":
            # Warlock spells known table
            spells_known = {
                1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 10,
                11: 11, 12: 11, 13: 12, 14: 12, 15: 13, 16: 13, 17: 14, 18: 14, 19: 15, 20: 15
            }
            return spells_known.get(level, 0)
            
        elif class_name == "Artificer" or class_name == "Cleric" or class_name == "Druid" or class_name == "Paladin" or class_name == "Wizard":
            # These classes prepare spells rather than knowing a fixed number
            return -1  # Special value indicating they don't have a spells known limit
            
        return 0  # Default for non-spellcasting classes
    
    def calculate_spells_prepared_limit(self, class_name: str) -> int:
        """Calculate how many spells a character can prepare."""
        level = self.get_level_in_class(class_name)
        if level <= 0:
            return 0
            
        # Different classes have different preparation formulas
        if class_name == "Artificer":
            int_mod = self.get_ability_modifier("intelligence")
            return max(1, int_mod + (level // 2))
            
        elif class_name == "Cleric" or class_name == "Druid":
            wis_mod = self.get_ability_modifier("wisdom")
            return max(1, wis_mod + level)
            
        elif class_name == "Paladin":
            cha_mod = self.get_ability_modifier("charisma")
            return max(1, cha_mod + (level // 2))
            
        elif class_name == "Wizard":
            int_mod = self.get_ability_modifier("intelligence")
            return max(1, int_mod + level)
            
        return 0  # Default for classes that don't prepare spells
    
    def update_available_actions(self) -> None:
        """Update available actions based on character class features, etc."""
        # Start with standard actions every character has
        self._available_actions = {
            "Attack": {"type": "action", "description": "Make an attack with a weapon"},
            "Dash": {"type": "action", "description": "Double your movement speed"},
            "Disengage": {"type": "action", "description": "Your movement doesn't provoke opportunity attacks"},
            "Dodge": {"type": "action", "description": "Attacks against you have disadvantage"},
            "Help": {"type": "action", "description": "Give another creature advantage on its next ability check or attack"},
            "Hide": {"type": "action", "description": "Make a Stealth check to hide"},
            "Ready": {"type": "action", "description": "Prepare an action to take in response to a trigger"},
            "Search": {"type": "action", "description": "Make a Perception or Investigation check to find something"},
            "Use Object": {"type": "action", "description": "Interact with an object that requires your action"}
        }
        
        # Add class-specific actions
        if "Barbarian" in self._character_class:
            self._available_actions["Rage"] = {
                "type": "bonus_action",
                "description": "Enter a rage, gaining damage bonus and resistance to bludgeoning, piercing, and slashing damage"
            }
            
        if "Monk" in self._character_class:
            self._available_actions["Flurry of Blows"] = {
                "type": "bonus_action",
                "description": "After taking the Attack action, spend 1 ki point to make two unarmed strikes"
            }
            self._available_actions["Patient Defense"] = {
                "type": "bonus_action",
                "description": "Spend 1 ki point to take the Dodge action"
            }
            self._available_actions["Step of the Wind"] = {
                "type": "bonus_action",
                "description": "Spend 1 ki point to take the Disengage or Dash action and your jump distance is doubled for the turn"
            }
            
        # Add actions from feats
        if "Healer" in self._feats:
            self._available_actions["Use Healer's Kit"] = {
                "type": "action",
                "description": "Use a healer's kit to restore 1d6+4 hit points and additional hit points equal to the creature's maximum number of Hit Dice"
            }
            
        # Add special actions for beast companions
        if self._beast_companion is not None:
            if "Beast Master" in self._subclasses.get("Ranger", ""):
                self._available_actions["Command Beast"] = {
                    "type": "bonus_action",
                    "description": "Command your beast companion to take the Dash, Disengage, Help, or Attack action"
                }
                
                # Add Bestial Fury for level 11+ Beast Masters
                if self.get_level_in_class("Ranger") >= 11:
                    self._available_actions["Bestial Fury"] = {
                        "type": "special",
                        "description": "When you command your beast companion to take the Attack action, it can make two attacks or use Multiattack"
                    }
    
    def get_exhaustion_effects(self) -> Dict[str, Any]:
        """Get current effects of exhaustion based on level."""
        effects = {}
        
        if self._exhaustion_level >= 1:
            effects["disadvantage"] = ["ability_checks"]
            
        if self._exhaustion_level >= 2:
            effects["speed_halved"] = True
            
        if self._exhaustion_level >= 3:
            effects["disadvantage"] = ["attack_rolls", "saving_throws"]
            
        if self._exhaustion_level >= 4:
            effects["hit_point_maximum_halved"] = True
            
        if self._exhaustion_level >= 5:
            effects["speed"] = 0  # Speed reduced to 0
            
        if self._exhaustion_level >= 6:
            effects["death"] = True  # Death
            
        return effects
    
    def get_condition_effects(self) -> Dict[str, Any]:
        """Get mechanical effects of all current conditions."""
        effects = {}
        
        for condition in self._active_conditions:
            if condition == "blinded":
                if "disadvantage" not in effects:
                    effects["disadvantage"] = []
                effects["disadvantage"].append("attack_rolls")
                if "advantage_against" not in effects:
                    effects["advantage_against"] = []
                effects["advantage_against"].append("attack_rolls")
                
            elif condition == "charmed":
                if "cannot_attack" not in effects:
                    effects["cannot_attack"] = []
                effects["cannot_attack"].append("charmer")
                
            elif condition == "deafened":
                effects["cannot_hear"] = True
                
            elif condition == "frightened":
                if "disadvantage" not in effects:
                    effects["disadvantage"] = []
                effects["disadvantage"].append("ability_checks")
                effects["disadvantage"].append("attack_rolls")
                effects["cannot_approach"] = "source_of_fear"
                
            elif condition == "grappled":
                effects["speed"] = 0
                
            elif condition == "incapacitated":
                effects["cannot_take_actions"] = True
                effects["cannot_take_reactions"] = True
                
            elif condition == "invisible":
                if "advantage" not in effects:
                    effects["advantage"] = []
                effects["advantage"].append("attack_rolls")
                if "disadvantage_against" not in effects:
                    effects["disadvantage_against"] = []
                effects["disadvantage_against"].append("attack_rolls")
                
            elif condition == "paralyzed":
                effects["incapacitated"] = True
                effects["cannot_move"] = True
                effects["cannot_speak"] = True
                if "auto_critical" not in effects:
                    effects["auto_critical"] = []
                effects["auto_critical"].append("if_within_5_feet")
                effects["fail_strength_dexterity_saves"] = True
                
            elif condition == "petrified":
                # Many effects same as paralyzed, plus more
                effects["incapacitated"] = True
                effects["cannot_move"] = True
                effects["cannot_speak"] = True
                if "auto_critical" not in effects:
                    effects["auto_critical"] = []
                effects["auto_critical"].append("if_within_5_feet")
                effects["fail_strength_dexterity_saves"] = True
                effects["damage_resistance"] = "all"
                effects["disease_immunity"] = True
                effects["poison_immunity"] = True
                effects["does_not_age"] = True
                
            elif condition == "poisoned":
                if "disadvantage" not in effects:
                    effects["disadvantage"] = []
                effects["disadvantage"].append("ability_checks")
                effects["disadvantage"].append("attack_rolls")
                
            elif condition == "prone":
                if "disadvantage" not in effects:
                    effects["disadvantage"] = []
                effects["disadvantage"].append("attack_rolls")
                if "advantage_against" not in effects:
                    effects["advantage_against"] = []
                effects["advantage_against"].append("attack_rolls_if_within_5_feet")
                if "disadvantage_against" not in effects:
                    effects["disadvantage_against"] = []
                effects["disadvantage_against"].append("attack_rolls_if_beyond_5_feet")
                
            elif condition == "restrained":
                effects["speed"] = 0
                if "disadvantage" not in effects:
                    effects["disadvantage"] = []
                effects["disadvantage"].append("attack_rolls")
                effects["disadvantage"].append("dexterity_saving_throws")
                if "advantage_against" not in effects:
                    effects["advantage_against"] = []
                effects["advantage_against"].append("attack_rolls")
                
            elif condition == "stunned":
                effects["incapacitated"] = True
                effects["cannot_move"] = True
                effects["can_speak_only_falteringly"] = True
                effects["fail_strength_dexterity_saves"] = True
                if "advantage_against" not in effects:
                    effects["advantage_against"] = []
                effects["advantage_against"].append("attack_rolls")
                
            elif condition == "unconscious":
                effects["incapacitated"] = True
                effects["cannot_move"] = True
                effects["cannot_speak"] = True
                effects["unaware_of_surroundings"] = True
                effects["drop_everything_held"] = True
                effects["fall_prone"] = True
                effects["fail_strength_dexterity_saves"] = True
                if "auto_critical" not in effects:
                    effects["auto_critical"] = []
                effects["auto_critical"].append("if_within_5_feet")
                
        return effects
    
    def get_effective_movement_speed(self, movement_type: str = "walk") -> int:
        """Calculate effective movement speed considering all effects."""
        # Get base speed for the requested movement type
        base_speed = self._base_movement_types.get(movement_type, 0)
        if movement_type == "walk":
            base_speed = self._base_speed
            
        # Apply exhaustion effects
        if self._exhaustion_level >= 5:
            return 0  # Speed reduced to 0
        elif self._exhaustion_level >= 2:
            base_speed //= 2  # Speed halved
            
        # Apply condition effects
        if any(c in self._active_conditions for c in ["grappled", "restrained"]):
            return 0  # Speed reduced to 0
            
        # Add speed bonuses (e.g., from magic items, spells, etc.)
        bonus_speed = 0
        # Check for specific features like Monk's Unarmored Movement
        if "Monk" in self._character_class:
            monk_level = self.get_level_in_class("Monk")
            if monk_level >= 2:
                if monk_level >= 18:
                    bonus_speed += 30
                elif monk_level >= 14:
                    bonus_speed += 25
                elif monk_level >= 10:
                    bonus_speed += 20
                elif monk_level >= 6:
                    bonus_speed += 15
                else:
                    bonus_speed += 10
                    
        # Check for items that modify speed
        for item in self._attuned_items:
            if "boots of speed" in item.lower():
                bonus_speed += base_speed  # Doubles speed
                
        # Check for encumbrance (simplified, would need weight tracking)
        # If character is heavily encumbered, speed reduced by 20 ft
        
        return max(0, base_speed + bonus_speed)
    
    def get_level_in_class(self, class_name: str) -> int:
        """Get character's level in a specific class."""
        return self._character_class.get(class_name, 0)
    
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
        # This is a simplified approach - in a real character history tracker
        # you would need to know the actual order classes were taken
        return class_name == self.primary_class
    
    def _get_armor_type(self, armor_name: str) -> str:
        """Determine armor type from name."""
        armor_name = armor_name.lower()
        
        # Light armor
        if any(a in armor_name for a in ["padded", "leather", "studded"]):
            return "light armor"
            
        # Medium armor
        elif any(a in armor_name for a in ["hide", "chain shirt", "scale", "breastplate", "half plate"]):
            return "medium armor"
            
        # Heavy armor
        elif any(a in armor_name for a in ["ring mail", "chain mail", "splint", "plate"]):
            return "heavy armor"
            
        return "unknown"
    
    def _is_armor_worn(self, armor_type: str) -> bool:
        """Helper method to check if certain armor type is being worn."""
        if not self._armor:
            return False
            
        armor = self._armor.lower()
        if armor_type == "light":
            return any(a in armor for a in ["padded", "leather"])
        elif armor_type == "medium":
            return any(a in armor for a in ["hide", "chain shirt", "scale", "breastplate", "half plate"])
        elif armor_type == "heavy":
            return any(a in armor for a in ["ring mail", "chain mail", "splint", "plate"])
        return False
    
    # character summary methods
    def get_character_summary(self) -> Dict[str, Any]:
        """
        Create a concise summary of the character's core attributes suitable for LLM context.
        
        Returns:
            Dict[str, Any]: Dictionary containing key character information
        """
        # Calculate total level and primary class for the summary
        total_level = self.total_level
        primary_class = self.primary_class
        
        # Build a summary dictionary with key character information
        summary = {
            # Basic identity
            "name": self._name,
            "species": self._species,
            "variants": self._species_variants,
            "level": total_level,
            "classes": self._character_class,
            "background": self._background,
            "alignment": f"{self._alignment_ethical} {self._alignment_moral}",
            
            # Ability scores and modifiers
            "ability_scores": {
                "strength": self._strength.total_score,
                "dexterity": self._dexterity.total_score, 
                "constitution": self._constitution.total_score,
                "intelligence": self._intelligence.total_score,
                "wisdom": self._wisdom.total_score,
                "charisma": self._charisma.total_score
            },
            "ability_modifiers": {
                "strength": self._strength.modifier,
                "dexterity": self._dexterity.modifier,
                "constitution": self._constitution.modifier,
                "intelligence": self._intelligence.modifier,
                "wisdom": self._wisdom.modifier,
                "charisma": self._charisma.modifier
            },
            
            # Combat stats
            "ac": self._armor_class,
            "hp": {
                "current": self._current_hit_points,
                "max": self._max_hit_points,
                "temp": self._temporary_hit_points
            },
            "initiative": self._initiative,
            "proficiency_bonus": self._proficiency_bonus,
            
            # Key proficiencies (simplified)
            "proficient_skills": [skill for skill, level in self._skill_proficiencies.items() 
                                if level == ProficiencyLevel.PROFICIENT],
            "expert_skills": [skill for skill, level in self._skill_proficiencies.items() 
                            if level == ProficiencyLevel.EXPERT],
            "saving_throws": [ability for ability, level in self._saving_throw_proficiencies.items() 
                            if level == ProficiencyLevel.PROFICIENT],
            
            # Core features
            "features": list(self._class_features.keys()),
            "feats": self._feats,
            "species_traits": list(self._species_traits.keys()),
            
            # Equipment summary
            "weapon_count": len(self._weapons),
            "armor": self._armor,
            "shield": self._shield,
            
            # Personality
            "personality_traits": self._personality_traits,
            "ideals": self._ideals,
            "bonds": self._bonds,
            "flaws": self._flaws,
            "backstory_summary": self._backstory[:200] + "..." if len(self._backstory) > 200 else self._backstory
        }
        
        # Add spellcasting information if character is a spellcaster
        if self._spellcasting_ability:
            summary["spellcasting"] = {
                "ability": self._spellcasting_ability,
                "spell_save_dc": self._spell_save_dc,
                "spell_attack_bonus": self._spell_attack_bonus,
                "spells_known_count": sum(len(spells) for spells in self._spells_known.values()),
                "prepared_count": len(self._spells_prepared)
            }
        
        # Add condition information if any are active
        if self._active_conditions:
            summary["conditions"] = list(self._active_conditions.keys())
        
        # Add exhaustion if present
        if self._exhaustion_level > 0:
            summary["exhaustion_level"] = self._exhaustion_level
        
        return summary

    def get_character_summary_json(self) -> str:
        """
        Generate a JSON string representation of the character summary.
        
        Returns:
            str: JSON string of character summary
        """
        import json
        return json.dumps(self.get_character_summary(), indent=2)