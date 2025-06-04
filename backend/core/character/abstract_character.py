from abc import ABC, abstractmethod
import math
import json
from typing import Dict, List, Optional, Union, Any, Tuple, Set

# Import abstract classes from other modules
from backend.core.classes.abstract_character_class import AbstractCharacterClass
from backend.core.species.abstract_species import AbstractSpecies
from backend.core.spells.abstract_spells import AbstractSpell
from backend.core.alignment.abstract_alignment import Alignment
from backend.core.skills.abstract_skills import AbstractSkill
from backend.core.feats.abstract_feats import AbstractFeat
from backend.core.equipment.abstract_equipment import AbstractEquipment
from backend.core.backgrounds.abstract_background import AbstractBackground

class AbstractCharacter(ABC):
    """
    Abstract base class for D&D character creation following the 2024 revised rules.
    
    A character in D&D is defined by:
    - Ability Scores: STR, DEX, CON, INT, WIS, CHA
    - Species (formerly Race): Biological traits and inherent abilities
    - Class: Primary abilities, combat style, and progression
    - Background: Formative experiences and upbringing
    - Alignment: Moral and ethical compass
    - Skills: Specific abilities for various actions
    - Feats: Special abilities and traits
    - Equipment: Weapons, armor, and gear
    - Personality and Backstory: Character traits and history
    """
    
    # Default skill list based on 2024 rules
    SKILLS = [
        "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
        "History", "Insight", "Intimidation", "Investigation", "Medicine",
        "Nature", "Perception", "Performance", "Persuasion", "Religion",
        "Sleight of Hand", "Stealth", "Survival"
    ]
    
    # Saving throws correspond to ability scores
    SAVING_THROWS = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    
    def __init__(self, name: str, species: AbstractSpecies, character_class: AbstractCharacterClass,
                background: Union[str, AbstractBackground], alignment: Alignment, level: int = 1,
                ability_scores: Dict[str, int] = None):
        """
        Initialize a new character.
        
        Args:
            name: Character name
            species: Character species (formerly race)
            character_class: Character class
            background: Character background
            alignment: Character alignment
            level: Character level (default: 1)
            ability_scores: Dictionary with ability scores (default: standard array)
        """
        self.name = name
        self.species = species
        self.character_class = character_class
        self.background = background
        self.alignment = alignment
        self.level = level
        
        # Set ability scores (default to standard array if not provided)
        if ability_scores:
            self.ability_scores = ability_scores
        else:
            # Standard array: 15, 14, 13, 12, 10, 8
            self.ability_scores = {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12, 
                "wisdom": 10,
                "charisma": 8
            }
        
        # Initialize other character attributes
        self.hit_points = 0
        self.temporary_hit_points = 0
        self.armor_class = 10  # Base AC
        self.proficiency_bonus = self._calculate_proficiency_bonus()
        
        # Proficiencies
        self.skill_proficiencies = []
        self.skill_expertise = []
        self.tool_proficiencies = []
        self.armor_proficiencies = []
        self.weapon_proficiencies = []
        self.saving_throw_proficiencies = []
        
        # Character elements
        self.feats = []
        self.equipment = []
        self.spells = []
        self.known_spells = []
        self.prepared_spells = []
        self.spell_slots = {}
        self.experience_points = 0
        self.inspiration = False
        
        # Personality and backstory
        self.personality_traits = []
        self.ideals = []
        self.bonds = []
        self.flaws = []
        self.appearance = ""
        self.backstory = ""
        self.allies_and_organizations = []
        self.additional_features = {}
        self.treasure = []
        
        # Combat tracking
        self.death_saves = {"successes": 0, "failures": 0}
        self.conditions = []
        self.exhaustion_level = 0
        
        # Derived traits from species
        self.languages = []
        self.speed = {"walk": 30, "swim": 0, "climb": 0, "fly": 0, "burrow": 0}
        self.senses = {"darkvision": 0, "blindsight": 0, "tremorsense": 0, "truesight": 0}
        self.resistances = []
        self.immunities = []
        self.vulnerabilities = []
        
        # Multiclass tracking
        self.class_levels = {character_class.name: level}
        
        # Apply species traits
        self._apply_species_traits()
        
        # Apply class features
        self._apply_class_features()
        
        # Apply background features
        self._apply_background_features()
        
        # Calculate initial hit points
        self._calculate_initial_hit_points()
        
        # Calculate initial armor class
        self._calculate_armor_class()
    
    def _calculate_proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on level."""
        return math.ceil(1 + (self.level / 4))
    
    def _calculate_ability_modifier(self, score: int) -> int:
        """Calculate ability modifier from score."""
        return math.floor((score - 10) / 2)
    
    def _apply_species_traits(self):
        """Apply species traits to the character."""
        # Apply species-specific bonuses
        if hasattr(self.species, 'apply_species_bonuses'):
            self.species.apply_species_bonuses(self)
        
        # Set base speed
        if hasattr(self.species, 'speed'):
            self.speed["walk"] = self.species.speed
        
        # Set darkvision if applicable
        if hasattr(self.species, 'darkvision') and self.species.darkvision > 0:
            self.senses["darkvision"] = self.species.darkvision
        
        # Add languages
        if hasattr(self.species, 'languages'):
            self.languages = list(self.species.languages)
        
        # Apply resistances
        if hasattr(self.species, 'resistances'):
            self.resistances.extend(self.species.resistances)
    
    def _apply_class_features(self):
        """Apply class features to the character."""
        # Add saving throw proficiencies
        if hasattr(self.character_class, 'saving_throws'):
            self.saving_throw_proficiencies = list(self.character_class.saving_throws)
        
        # Add weapon and armor proficiencies
        if hasattr(self.character_class, 'proficiencies'):
            if 'armor' in self.character_class.proficiencies:
                self.armor_proficiencies = list(self.character_class.proficiencies['armor'])
            if 'weapons' in self.character_class.proficiencies:
                self.weapon_proficiencies = list(self.character_class.proficiencies['weapons'])
            if 'tools' in self.character_class.proficiencies:
                self.tool_proficiencies = list(self.character_class.proficiencies['tools'])
    
    def _apply_background_features(self):
        """Apply background features to the character."""
        # This will be implemented based on the background system
        # For now, a placeholder that might add skills, tools, languages, etc.
        pass
    
    def _calculate_initial_hit_points(self):
        """Calculate initial hit points based on class, level, and Constitution."""
        con_mod = self.get_ability_modifier("constitution")
        
        # First level: maximum hit die + CON modifier
        if hasattr(self.character_class, 'hit_dice'):
            hit_die = int(self.character_class.hit_dice[1:])  # Remove the 'd' prefix
            self.hit_points = hit_die + con_mod
            
            # Additional levels
            for _ in range(1, self.level):
                # This would be an average value; for real rolls, this would be different
                average_roll = math.ceil((hit_die + 1) / 2)  # Average roll on the hit die
                self.hit_points += average_roll + con_mod
    
    def _calculate_armor_class(self):
        """Calculate armor class based on equipment and abilities."""
        # Base AC is 10 + DEX modifier
        dex_mod = self.get_ability_modifier("dexterity")
        self.armor_class = 10 + dex_mod
        
        # Check for armor in equipment
        # This is a placeholder; actual implementation would check equipped armor
        pass
    
    @abstractmethod
    def level_up(self, new_class: Optional[str] = None) -> Dict[str, Any]:
        """
        Level up the character.
        
        Args:
            new_class: Class to level up in (for multiclassing, None for primary class)
            
        Returns:
            Dict[str, Any]: Results of the level up process
        """
        pass
    
    @abstractmethod
    def add_experience(self, xp: int) -> Dict[str, Any]:
        """
        Add experience points and level up if threshold is reached.
        
        Args:
            xp: Experience points to add
            
        Returns:
            Dict[str, Any]: Results including new level if applicable
        """
        pass
    
    @abstractmethod
    def can_multiclass_into(self, new_class: str) -> Tuple[bool, str]:
        """
        Check if character can multiclass into a new class.
        
        Args:
            new_class: Class to check for multiclassing
            
        Returns:
            Tuple[bool, str]: (Can multiclass, explanation)
        """
        pass
    
    def get_ability_modifier(self, ability: str) -> int:
        """
        Get the modifier for a specific ability.
        
        Args:
            ability: The ability to get the modifier for
            
        Returns:
            int: The ability modifier
        """
        score = self.ability_scores.get(ability.lower(), 10)
        return self._calculate_ability_modifier(score)
    
    def get_saving_throw_modifier(self, ability: str) -> int:
        """
        Get the modifier for a specific saving throw.
        
        Args:
            ability: The ability for the saving throw
            
        Returns:
            int: The saving throw modifier
        """
        modifier = self.get_ability_modifier(ability)
        
        # Add proficiency bonus if proficient
        if ability.capitalize() in self.saving_throw_proficiencies:
            modifier += self.proficiency_bonus
            
        return modifier
    
    def get_skill_modifier(self, skill: str) -> int:
        """
        Get the modifier for a specific skill.
        
        Args:
            skill: The skill to get the modifier for
            
        Returns:
            int: The skill modifier
        """
        # Map skills to their primary abilities
        skill_to_ability = {
            "Acrobatics": "dexterity",
            "Animal Handling": "wisdom",
            "Arcana": "intelligence",
            "Athletics": "strength",
            "Deception": "charisma",
            "History": "intelligence",
            "Insight": "wisdom",
            "Intimidation": "charisma",
            "Investigation": "intelligence",
            "Medicine": "wisdom",
            "Nature": "intelligence",
            "Perception": "wisdom",
            "Performance": "charisma",
            "Persuasion": "charisma",
            "Religion": "intelligence",
            "Sleight of Hand": "dexterity",
            "Stealth": "dexterity",
            "Survival": "wisdom"
        }
        
        ability = skill_to_ability.get(skill, "dexterity")
        modifier = self.get_ability_modifier(ability)
        
        # Add proficiency bonus if proficient
        if skill in self.skill_proficiencies:
            modifier += self.proficiency_bonus
            
        # Add additional proficiency if expertise
        if skill in self.skill_expertise:
            modifier += self.proficiency_bonus
            
        return modifier
    
    def get_passive_score(self, skill: str) -> int:
        """
        Calculate passive score for a skill (typically perception).
        
        Args:
            skill: The skill to calculate passive score for
            
        Returns:
            int: The passive score (10 + skill modifier)
        """
        return 10 + self.get_skill_modifier(skill)
    
    def take_damage(self, damage: int, damage_type: str = None) -> int:
        """
        Apply damage to the character.
        
        Args:
            damage: Amount of damage to take
            damage_type: Type of damage (used for resistances/immunities)
            
        Returns:
            int: Remaining hit points
        """
        # Apply resistances/immunities if damage type provided
        if damage_type:
            if damage_type in self.immunities:
                return self.hit_points  # No damage
            if damage_type in self.resistances:
                damage = damage // 2  # Half damage
            if damage_type in self.vulnerabilities:
                damage = damage * 2  # Double damage
        
        # First apply damage to temporary hit points
        if self.temporary_hit_points > 0:
            if damage <= self.temporary_hit_points:
                self.temporary_hit_points -= damage
                return self.hit_points
            else:
                damage -= self.temporary_hit_points
                self.temporary_hit_points = 0
        
        # Then apply to regular hit points
        self.hit_points = max(0, self.hit_points - damage)
        
        # Handle death saves if hit points reach 0
        if self.hit_points == 0:
            self._handle_unconsciousness()
            
        return self.hit_points
    
    def _handle_unconsciousness(self):
        """Handle effects of being reduced to 0 hit points."""
        # Add the unconscious condition
        if "Unconscious" not in self.conditions:
            self.conditions.append("Unconscious")
    
    def heal(self, amount: int) -> int:
        """
        Heal the character.
        
        Args:
            amount: Amount of healing to receive
            
        Returns:
            int: New hit point total
        """
        # Calculate max hit points
        con_mod = self.get_ability_modifier("constitution")
        hit_die_size = int(self.character_class.hit_dice[1:])
        max_hp = 0
        
        # For multiclassing, need to calculate based on each class
        for class_name, class_level in self.class_levels.items():
            if class_name == self.character_class.name:
                # First level of primary class is max hit die + CON
                first_level_hp = hit_die_size + con_mod
                # Remaining levels use average or rolled values + CON
                remaining_levels_hp = (class_level - 1) * ((hit_die_size/2 + 1) + con_mod)
                max_hp += first_level_hp + remaining_levels_hp
        
        # If no multiclassing, use simpler calculation
        if not max_hp:
            max_hp = hit_die_size + (con_mod * self.level)
            remaining_levels = self.level - 1
            max_hp += remaining_levels * ((hit_die_size/2 + 1) + con_mod)
        
        # You cannot heal beyond your maximum hit points
        self.hit_points = min(max_hp, self.hit_points + amount)
        
        # Remove unconscious condition if healed above 0
        if self.hit_points > 0 and "Unconscious" in self.conditions:
            self.conditions.remove("Unconscious")
        
        return self.hit_points
    
    def add_temporary_hit_points(self, amount: int) -> int:
        """
        Add temporary hit points.
        
        Args:
            amount: Amount of temporary hit points to add
            
        Returns:
            int: New temporary hit point total
        """
        # Temporary hit points don't stack, take the higher value
        self.temporary_hit_points = max(self.temporary_hit_points, amount)
        return self.temporary_hit_points
    
    def add_spell(self, spell: AbstractSpell) -> bool:
        """
        Add a spell to the character's spell list.
        
        Args:
            spell: The spell to add
            
        Returns:
            bool: True if added successfully
        """
        if spell not in self.spells:
            self.spells.append(spell)
            return True
        return False
    
    def learn_spell(self, spell: AbstractSpell) -> bool:
        """
        Learn a new spell (for classes with known spells).
        
        Args:
            spell: The spell to learn
            
        Returns:
            bool: True if learned successfully
        """
        if spell not in self.known_spells:
            self.known_spells.append(spell)
            return True
        return False
    
    def prepare_spell(self, spell: AbstractSpell) -> bool:
        """
        Prepare a spell (for classes with prepared spells).
        
        Args:
            spell: The spell to prepare
            
        Returns:
            bool: True if prepared successfully
        """
        if (spell in self.known_spells or spell in self.spells) and spell not in self.prepared_spells:
            self.prepared_spells.append(spell)
            return True
        return False
    
    def can_cast_spell(self, spell: AbstractSpell, slot_level: Optional[int] = None) -> Tuple[bool, str]:
        """
        Check if character can cast a specific spell.
        
        Args:
            spell: The spell to cast
            slot_level: Level of spell slot to use
            
        Returns:
            Tuple[bool, str]: (Can cast, explanation)
        """
        # Check if spell is known/prepared
        if self.character_class.spellcasting_type == "prepared" and spell not in self.prepared_spells:
            return False, "Spell not prepared"
        
        if self.character_class.spellcasting_type == "known" and spell not in self.known_spells:
            return False, "Spell not known"
        
        # Determine appropriate slot level
        if slot_level is None:
            slot_level = spell.level
        
        # Check if slot level is valid
        if slot_level < spell.level:
            return False, f"Requires at least a level {spell.level} slot"
        
        # Check if spell slot is available
        if slot_level not in self.spell_slots or self.spell_slots[slot_level] <= 0:
            return False, f"No level {slot_level} spell slots remaining"
        
        return True, "Can cast spell"
    
    def cast_spell(self, spell: AbstractSpell, slot_level: Optional[int] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Cast a spell, using a spell slot.
        
        Args:
            spell: The spell to cast
            slot_level: Level of spell slot to use
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (Success, casting result)
        """
        can_cast, reason = self.can_cast_spell(spell, slot_level)
        
        if not can_cast:
            return False, {"success": False, "reason": reason}
        
        # Determine slot level if not specified
        if slot_level is None:
            slot_level = spell.level
        
        # Use a spell slot
        self.spell_slots[slot_level] -= 1
        
        # Cast the spell
        result = spell.cast(self)
        
        return True, {"success": True, "result": result, "slot_used": slot_level}
    
    def add_equipment(self, item: AbstractEquipment) -> bool:
        """
        Add an equipment item to the character's inventory.
        
        Args:
            item: The item to add
            
        Returns:
            bool: True if added successfully
        """
        self.equipment.append(item)
        return True
    
    def add_feat(self, feat: AbstractFeat) -> bool:
        """
        Add a feat to the character.
        
        Args:
            feat: The feat to add
            
        Returns:
            bool: True if added successfully
        """
        if feat.name not in [f.name for f in self.feats]:
            self.feats.append(feat)
            # Apply feat benefits
            if hasattr(feat, 'apply_benefits'):
                feat.apply_benefits(self)
            return True
        return False
    
    def add_skill_proficiency(self, skill: str) -> bool:
        """
        Add a skill proficiency.
        
        Args:
            skill: The skill to add proficiency in
            
        Returns:
            bool: True if added successfully
        """
        if skill not in self.skill_proficiencies and skill in self.SKILLS:
            self.skill_proficiencies.append(skill)
            return True
        return False
    
    def add_skill_expertise(self, skill: str) -> bool:
        """
        Add expertise in a skill.
        
        Args:
            skill: The skill to add expertise in
            
        Returns:
            bool: True if added successfully
        """
        if skill in self.skill_proficiencies and skill not in self.skill_expertise:
            self.skill_expertise.append(skill)
            return True
        return False
    
    def add_language(self, language: str) -> bool:
        """
        Add a language.
        
        Args:
            language: The language to add
            
        Returns:
            bool: True if added successfully
        """
        if language not in self.languages:
            self.languages.append(language)
            return True
        return False
    
    def gain_inspiration(self) -> bool:
        """
        Gain inspiration.
        
        Returns:
            bool: True if gained successfully
        """
        self.inspiration = True
        return True
    
    def use_inspiration(self) -> bool:
        """
        Use inspiration if available.
        
        Returns:
            bool: True if used successfully
        """
        if self.inspiration:
            self.inspiration = False
            return True
        return False
    
    def add_condition(self, condition: str) -> bool:
        """
        Add a condition to the character.
        
        Args:
            condition: The condition to add
            
        Returns:
            bool: True if added successfully
        """
        if condition not in self.conditions:
            self.conditions.append(condition)
            return True
        return False
    
    def remove_condition(self, condition: str) -> bool:
        """
        Remove a condition from the character.
        
        Args:
            condition: The condition to remove
            
        Returns:
            bool: True if removed successfully
        """
        if condition in self.conditions:
            self.conditions.remove(condition)
            return True
        return False
    
    def has_condition(self, condition: str) -> bool:
        """
        Check if the character has a specific condition.
        
        Args:
            condition: The condition to check
            
        Returns:
            bool: True if character has the condition
        """
        return condition in self.conditions
    
    def add_exhaustion_level(self) -> int:
        """
        Increase exhaustion level.
        
        Returns:
            int: New exhaustion level
        """
        if self.exhaustion_level < 10:  # 2024 rules use 10-level exhaustion
            self.exhaustion_level += 1
        return self.exhaustion_level
    
    def remove_exhaustion_level(self, levels: int = 1) -> int:
        """
        Reduce exhaustion level.
        
        Args:
            levels: Number of exhaustion levels to remove
            
        Returns:
            int: New exhaustion level
        """
        self.exhaustion_level = max(0, self.exhaustion_level - levels)
        return self.exhaustion_level
    
    def get_exhaustion_penalty(self) -> int:
        """
        Get the exhaustion penalty to ability checks, etc.
        
        Returns:
            int: Exhaustion penalty
        """
        # Under 2024 rules, penalties scale with exhaustion level
        return -self.exhaustion_level if self.exhaustion_level > 0 else 0
    
    def short_rest(self) -> Dict[str, Any]:
        """
        Take a short rest.
        
        Returns:
            Dict[str, Any]: Result of the short rest
        """
        # Track what's recovered during the rest
        results = {
            "hit_points_before": self.hit_points,
            "hit_dice_used": 0,
            "hit_points_healed": 0,
            "hit_points_after": self.hit_points,
            "features_refreshed": []
        }
        
        # Let each class handle its features that recover on short rest
        class_rest_results = self.character_class.short_rest()
        
        # Merge results
        for key, value in class_rest_results.items():
            if key in results and isinstance(results[key], list):
                results[key].extend(value)
            else:
                results[key] = value
        
        return results
    
    def long_rest(self) -> Dict[str, Any]:
        """
        Take a long rest.
        
        Returns:
            Dict[str, Any]: Result of the long rest
        """
        # Track initial state
        hp_before = self.hit_points
        
        # Reset hit points to maximum
        con_mod = self.get_ability_modifier("constitution")
        hit_die_size = int(self.character_class.hit_dice[1:])
        max_hp = hit_die_size + (hit_die_size/2 + 1 + con_mod) * (self.level - 1)
        self.hit_points = int(max_hp)
        
        # Reset class resources
        class_rest_results = self.character_class.long_rest()
        
        # Reset spell slots
        spell_slots_before = self.spell_slots.copy()
        if hasattr(self.character_class, "get_spellcasting_info"):
            spellcasting_info = self.character_class.get_spellcasting_info(self.level)
            if "slots" in spellcasting_info:
                self.spell_slots = spellcasting_info["slots"]
        
        # Remove exhaustion
        exhaustion_before = self.exhaustion_level
        self.exhaustion_level = max(0, self.exhaustion_level - 1)
        
        # Recover hit dice (up to half total)
        hit_dice_recovered = min(self.level // 2, self.level - self.character_class.hit_dice_count)
        self.character_class.hit_dice_count += hit_dice_recovered
        
        # Build results dict
        results = {
            "hit_points_before": hp_before,
            "hit_points_healed": self.hit_points - hp_before,
            "hit_points_after": self.hit_points,
            "hit_dice_recovered": hit_dice_recovered,
            "spell_slots_before": spell_slots_before,
            "spell_slots_after": self.spell_slots,
            "exhaustion_before": exhaustion_before,
            "exhaustion_after": self.exhaustion_level,
            "features_refreshed": class_rest_results.get("features_refreshed", [])
        }
        
        return results
    
    def make_death_saving_throw(self, roll: Optional[int] = None) -> Dict[str, Any]:
        """
        Make a death saving throw.
        
        Args:
            roll: Optional roll value (for testing)
            
        Returns:
            Dict[str, Any]: Result of the saving throw
        """
        if self.hit_points > 0:
            return {"success": False, "reason": "Character is not dying"}
        
        # Roll d20 if not provided
        if roll is None:
            roll = random.randint(1, 20)
        
        result = {
            "roll": roll,
            "natural_1": roll == 1,
            "natural_20": roll == 20,
            "success": roll >= 10,
            "critical_success": roll == 20,
            "critical_failure": roll == 1
        }
        
        # Apply results
        if roll == 20:
            # Natural 20 regains 1 hit point
            self.hit_points = 1
            self.death_saves = {"successes": 0, "failures": 0}
            result["stabilized"] = True
            result["healed"] = True
            # Remove unconscious condition
            if "Unconscious" in self.conditions:
                self.conditions.remove("Unconscious")
        elif roll == 1:
            # Natural 1 counts as two failures
            self.death_saves["failures"] += 2
        elif roll >= 10:
            self.death_saves["successes"] += 1
        else:
            self.death_saves["failures"] += 1
        
        # Check for stabilization or death
        if self.death_saves["successes"] >= 3:
            result["stabilized"] = True
            self.death_saves = {"successes": 0, "failures": 0}
        elif self.death_saves["failures"] >= 3:
            result["died"] = True
            # Add the dead condition
            self.conditions.append("Dead")
        
        result["current_death_saves"] = self.death_saves.copy()
        return result
    
    def stabilize(self) -> bool:
        """
        Stabilize a dying character.
        
        Returns:
            bool: True if stabilized successfully
        """
        if self.hit_points <= 0 and "Dead" not in self.conditions:
            self.death_saves = {"successes": 0, "failures": 0}
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert character to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the character
        """
        return {
            "name": self.name,
            "species": self.species.name if hasattr(self.species, 'name') else str(self.species),
            "class": self.character_class.name,
            "level": self.level,
            "class_levels": self.class_levels,
            "background": self.background.name if hasattr(self.background, 'name') else str(self.background),
            "alignment": str(self.alignment),
            "ability_scores": self.ability_scores,
            "hit_points": self.hit_points,
            "temporary_hit_points": self.temporary_hit_points,
            "armor_class": self.armor_class,
            "proficiency_bonus": self.proficiency_bonus,
            "skill_proficiencies": self.skill_proficiencies,
            "skill_expertise": self.skill_expertise,
            "saving_throw_proficiencies": self.saving_throw_proficiencies,
            "languages": self.languages,
            "speed": self.speed,
            "senses": self.senses,
            "feats": [feat.name for feat in self.feats],
            "spellcasting": {
                "spells_known": [spell.name for spell in self.known_spells],
                "spells_prepared": [spell.name for spell in self.prepared_spells],
                "spell_slots": self.spell_slots
            },
            "equipment": [item.name if hasattr(item, 'name') else str(item) for item in self.equipment],
            "personality": {
                "traits": self.personality_traits,
                "ideals": self.ideals,
                "bonds": self.bonds,
                "flaws": self.flaws,
                "backstory": self.backstory
            },
            "resources": {
                "inspiration": self.inspiration,
                "exhaustion": self.exhaustion_level
            },
            "combat_status": {
                "conditions": self.conditions,
                "death_saves": self.death_saves,
            },
            "experience_points": self.experience_points
        }
    
    def save_to_file(self, filename: str) -> bool:
        """
        Save character to a JSON file.
        
        Args:
            filename: The filename to save to
            
        Returns:
            bool: True if saved successfully
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving character: {e}")
            return False
    
    @classmethod
    @abstractmethod
    def load_from_file(cls, filename: str):
        """
        Load character from a JSON file.
        
        Args:
            filename: The filename to load from
            
        Returns:
            AbstractCharacter: A new character instance
        """
        pass


class AbstractCharacters(ABC):
    """
    Abstract base class for managing D&D characters in the 2024 Edition.
    
    This class provides methods to interact with the character system, including:
    - Creating new characters
    - Retrieving existing characters
    - Updating character information
    - Filtering and sorting characters
    - Exporting and importing character data
    """
    
    @abstractmethod
    def create_character(self, character_data: Dict[str, Any]) -> AbstractCharacter:
        """
        Create a new character.
        
        Args:
            character_data: Character definition data
            
        Returns:
            AbstractCharacter: New character instance
        """
        pass
    
    @abstractmethod
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """
        Get a list of all available characters.
        
        Returns:
            List[Dict[str, Any]]: List of character summary information
        """
        pass
    
    @abstractmethod
    def get_character_details(self, character_id: str) -> Optional[AbstractCharacter]:
        """
        Get detailed information about a character.
        
        Args:
            character_id: Unique identifier for the character
            
        Returns:
            Optional[AbstractCharacter]: The character object or None if not found
        """
        pass
    
    @abstractmethod
    def update_character(self, character_id: str, updates: Dict[str, Any]) -> Optional[AbstractCharacter]:
        """
        Update an existing character.
        
        Args:
            character_id: Character identifier
            updates: Changes to apply
            
        Returns:
            Optional[AbstractCharacter]: Updated character or None if not found
        """
        pass
    
    @abstractmethod
    def delete_character(self, character_id: str) -> bool:
        """
        Delete a character.
        
        Args:
            character_id: Character identifier
            
        Returns:
            bool: True if deleted successfully
        """
        pass
    
    @abstractmethod
    def filter_characters(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter characters based on multiple criteria.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List[Dict[str, Any]]: List of filtered character summaries
        """
        pass
    
    @abstractmethod
    def get_characters_by_level_range(self, min_level: int, max_level: int) -> List[Dict[str, Any]]:
        """
        Get characters within a level range.
        
        Args:
            min_level: Minimum level
            max_level: Maximum level
            
        Returns:
            List[Dict[str, Any]]: List of matching character summaries
        """
        pass
    
    @abstractmethod
    def get_characters_by_class(self, class_name: str) -> List[Dict[str, Any]]:
        """
        Get characters of a specific class.
        
        Args:
            class_name: Class name to filter by
            
        Returns:
            List[Dict[str, Any]]: List of matching character summaries
        """
        pass
    
    @abstractmethod
    def get_characters_by_species(self, species_name: str) -> List[Dict[str, Any]]:
        """
        Get characters of a specific species.
        
        Args:
            species_name: Species name to filter by
            
        Returns:
            List[Dict[str, Any]]: List of matching character summaries
        """
        pass
    
    @abstractmethod
    def export_character(self, character_id: str, format_type: str = "json") -> Union[str, bytes]:
        """
        Export a character in a specific format.
        
        Args:
            character_id: Character identifier
            format_type: Export format (json, pdf, etc.)
            
        Returns:
            Union[str, bytes]: Exported character data
        """
        pass
    
    @abstractmethod
    def import_character(self, character_data: Union[str, bytes], format_type: str = "json") -> Optional[AbstractCharacter]:
        """
        Import a character from external data.
        
        Args:
            character_data: Character data to import
            format_type: Import format (json, pdf, etc.)
            
        Returns:
            Optional[AbstractCharacter]: Imported character or None if failed
        """
        pass
    
    @abstractmethod
    def level_up_character(self, character_id: str, new_class: Optional[str] = None) -> Dict[str, Any]:
        """
        Level up a character.
        
        Args:
            character_id: Character identifier
            new_class: Class to level up in (for multiclassing)
            
        Returns:
            Dict[str, Any]: Results of the level up process
        """
        pass
    
    @abstractmethod
    def add_experience(self, character_id: str, xp: int) -> Dict[str, Any]:
        """
        Add experience to a character.
        
        Args:
            character_id: Character identifier
            xp: Amount of experience to add
            
        Returns:
            Dict[str, Any]: Results including new level if applicable
        """
        pass
    
    @abstractmethod
    def generate_random_character(self, parameters: Dict[str, Any] = None) -> AbstractCharacter:
        """
        Generate a random character based on optional parameters.
        
        Args:
            parameters: Optional parameters to guide generation
            
        Returns:
            AbstractCharacter: Randomly generated character
        """
        pass
    
    def character_exists(self, character_id: str) -> bool:
        """
        Check if a character exists.
        
        Args:
            character_id: Character identifier
            
        Returns:
            bool: True if character exists, False otherwise
        """
        return self.get_character_details(character_id) is not None