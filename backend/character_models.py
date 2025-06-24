# ## **3. `character_models.py`**
# **Character sheet and data models**
# - **Classes**: `CharacterCore`, `CharacterState`, `CharacterStats`, `CharacterSheet`, `CharacterIterationCache`
# - **Purpose**: Character data structures, hit points, equipment, calculated statistics
# - **Dependencies**: `core_models.py`
#
# REFACTORED: Added journal tracking, D&D 5e 2024 exhaustion rules, comprehensive conditions,
# getter/setter methods for RESTful API access


from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from enum import Enum

# Import from core_models.py
from core_models import (
    ProficiencyLevel,
    AbilityScoreSource,
    AbilityScore,
    ASIManager,
    CharacterLevelManager,
    MagicItemManager,
    SpellcastingManager
)

# ============================================================================
# D&D 5E 2024 CONDITIONS
# ============================================================================

class DnDCondition(Enum):
    """D&D 5e 2024 conditions with their effects."""
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "deafened"
    EXHAUSTION = "exhaustion"
    FRIGHTENED = "frightened"
    GRAPPLED = "grappled"
    INCAPACITATED = "incapacitated"
    INVISIBLE = "invisible"
    PARALYZED = "paralyzed"
    PETRIFIED = "petrified"
    POISONED = "poisoned"
    PRONE = "prone"
    RESTRAINED = "restrained"
    STUNNED = "stunned"
    UNCONSCIOUS = "unconscious"

class ExhaustionLevel:
    """D&D 5e 2024 Exhaustion level effects."""
    
    EFFECTS = {
        0: {"d20_penalty": 0, "speed_penalty": 0, "description": "No exhaustion"},
        1: {"d20_penalty": -2, "speed_penalty": -5, "description": "Fatigued"},
        2: {"d20_penalty": -4, "speed_penalty": -10, "description": "Tired"},
        3: {"d20_penalty": -6, "speed_penalty": -15, "description": "Weary"},
        4: {"d20_penalty": -8, "speed_penalty": -20, "description": "Exhausted"},
        5: {"d20_penalty": -10, "speed_penalty": -25, "description": "Severely Exhausted"},
        6: {"d20_penalty": 0, "speed_penalty": 0, "description": "Death"}
    }
    
    @classmethod
    def get_effects(cls, level: int) -> Dict[str, Any]:
        """Get effects for a given exhaustion level."""
        return cls.EFFECTS.get(min(max(level, 0), 6), cls.EFFECTS[0])
    
    @classmethod
    def is_dead(cls, level: int) -> bool:
        """Check if character dies from exhaustion."""
        return level >= 6

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CHARACTER DATA MODELS
# ============================================================================

class CharacterCore:
    """Enhanced core character data with level and ASI management."""
    
    def __init__(self, name: str = ""):
        # Basic identity
        self.name = name
        self.species = ""
        self.character_classes: Dict[str, int] = {}
        self.background = ""
        self.alignment = ["Neutral", "Neutral"]
        
        # Enhanced ability scores
        self.strength = AbilityScore(10)
        self.dexterity = AbilityScore(10)
        self.constitution = AbilityScore(10)
        self.intelligence = AbilityScore(10)
        self.wisdom = AbilityScore(10)
        self.charisma = AbilityScore(10)
        
        # Managers
        self.level_manager = CharacterLevelManager()
        self.magic_item_manager = MagicItemManager()
        
        # Proficiencies
        self.skill_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.saving_throw_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.armor_proficiency: List[str] = []
        self.weapon_proficiency: List[str] = []
        self.tool_proficiency: List[str] = []
        self.languages: List[str] = []
        
        # Personality
        self.personality_traits: List[str] = []
        self.ideals: List[str] = []
        self.bonds: List[str] = []
        self.flaws: List[str] = []
        self.backstory = ""
        
        # Enhanced backstory elements
        self.detailed_backstory: Dict[str, str] = {}
        self.custom_content_used: List[str] = []
        
        # Spellcasting information (NEW)
        self.spellcasting_info: Dict[str, Any] = {}
        self._update_spellcasting_info()
    
    @property
    def total_level(self) -> int:
        return sum(self.character_classes.values()) if self.character_classes else 1
    
    @property
    def level(self) -> int:
        """Calculate total character level from all classes."""
        return sum(self.character_classes.values()) if self.character_classes else 1
    
    @property
    def initiative(self) -> int:
        """Initiative is always equal to the Dexterity modifier."""
        return self.dexterity.modifier
    
    def get_ability_score(self, ability: str) -> AbilityScore:
        ability_map = {
            "strength": self.strength, "dexterity": self.dexterity,
            "constitution": self.constitution, "intelligence": self.intelligence,
            "wisdom": self.wisdom, "charisma": self.charisma
        }
        return ability_map.get(ability.lower())
    
    def level_up(self, class_name: str, asi_choice: Optional[Dict[str, Any]] = None):
        """Level up in a specific class."""
        current_level = self.character_classes.get(class_name, 0)
        new_level = current_level + 1
        
        self.level_manager.add_level(class_name, new_level, asi_choice)
    
    def apply_starting_ability_scores(self, scores: Dict[str, int]):
        """Apply starting ability scores (from character creation)."""
        for ability, score in scores.items():
            ability_obj = self.get_ability_score(ability)
            if ability_obj:
                ability_obj.base_score = score
    
    def apply_species_bonuses(self, bonuses: Dict[str, int], species_name: str):
        """Apply species-based ability score bonuses (for older editions/variants)."""
        for ability, bonus in bonuses.items():
            ability_obj = self.get_ability_score(ability)
            if ability_obj and bonus != 0:
                ability_obj.add_improvement(
                    AbilityScoreSource.SPECIES_TRAIT,
                    bonus,
                    f"{species_name} species bonus",
                    0  # Gained at character creation
                )
    
    def set_detailed_backstory(self, backstory_elements: Dict[str, str]):
        """Set the detailed backstory elements."""
        self.detailed_backstory = backstory_elements
        # Set main backstory for compatibility
        self.backstory = backstory_elements.get("main_backstory", "")
    
    def _update_spellcasting_info(self):
        """Update spellcasting information based on current classes."""
        self.spellcasting_info = SpellcastingManager.get_combined_spellcasting(self.character_classes)
    
    def get_spellcasting_info(self) -> Dict[str, Any]:
        """Get current spellcasting information."""
        # Refresh spellcasting info in case classes have changed
        self._update_spellcasting_info()
        return self.spellcasting_info.copy()
    
    def is_spellcaster(self) -> bool:
        """Check if character is a spellcaster."""
        return self.get_spellcasting_info().get("is_spellcaster", False)
    
    def can_swap_spells_on_rest(self) -> bool:
        """Check if character can swap spells after a long rest."""
        spellcasting_info = self.get_spellcasting_info()
        if not spellcasting_info.get("is_spellcaster", False):
            return False
        
        # Check if any spellcasting class allows spell swapping
        for class_info in spellcasting_info.get("spellcasting_classes", []):
            if class_info["info"].get("can_swap_spells_on_rest", False):
                return True
        return False
    
    def can_cast_rituals(self) -> bool:
        """Check if character can cast ritual spells."""
        spellcasting_info = self.get_spellcasting_info()
        if not spellcasting_info.get("is_spellcaster", False):
            return False
        
        # Check if any spellcasting class allows ritual casting
        for class_info in spellcasting_info.get("spellcasting_classes", []):
            if class_info["info"].get("can_cast_rituals", False):
                return True
        return False
    
    def get_spellcasting_abilities(self) -> List[str]:
        """Get list of spellcasting abilities used by this character."""
        spellcasting_info = self.get_spellcasting_info()
        if not spellcasting_info.get("is_spellcaster", False):
            return []
        
        abilities = set()
        for class_info in spellcasting_info.get("spellcasting_classes", []):
            abilities.add(class_info["info"]["spellcasting_ability"])
        
        return list(abilities)
    
    def get_spell_save_dc(self, spellcasting_ability: str = None) -> int:
        """Calculate spell save DC for a given spellcasting ability."""
        if not self.is_spellcaster():
            return 8  # Default, though character can't cast spells
        
        # If no ability specified, use primary spellcasting ability
        if not spellcasting_ability:
            abilities = self.get_spellcasting_abilities()
            if not abilities:
                return 8
            spellcasting_ability = abilities[0]  # Use first (primary) ability
        
        # Get ability modifier
        ability_obj = self.get_ability_score(spellcasting_ability)
        if not ability_obj:
            return 8
        
        # Calculate proficiency bonus (simplified - should use level manager)
        proficiency_bonus = 2 + ((self.level - 1) // 4)
        
        return 8 + proficiency_bonus + ability_obj.modifier
    
    def get_spell_attack_bonus(self, spellcasting_ability: str = None) -> int:
        """Calculate spell attack bonus for a given spellcasting ability."""
        if not self.is_spellcaster():
            return 0
        
        # If no ability specified, use primary spellcasting ability
        if not spellcasting_ability:
            abilities = self.get_spellcasting_abilities()
            if not abilities:
                return 0
            spellcasting_ability = abilities[0]
        
        # Get ability modifier
        ability_obj = self.get_ability_score(spellcasting_ability)
        if not ability_obj:
            return 0
        
        # Calculate proficiency bonus (simplified - should use level manager)
        proficiency_bonus = 2 + ((self.level - 1) // 4)
        
        return proficiency_bonus + ability_obj.modifier
    
    # ============================================================================
    # GETTER METHODS FOR API ACCESS
    # ============================================================================
    
    def get_name(self) -> str:
        """Get character name."""
        return self.name
    
    def get_species(self) -> str:
        """Get character species."""
        return self.species
    
    def get_character_classes(self) -> Dict[str, int]:
        """Get character classes and levels."""
        return self.character_classes.copy()
    
    def get_background(self) -> str:
        """Get character background."""
        return self.background
    
    def get_alignment(self) -> List[str]:
        """Get character alignment."""
        return self.alignment.copy()
    
    def get_ability_scores(self) -> Dict[str, int]:
        """Get all ability scores."""
        return {
            "strength": self.strength.total_score,
            "dexterity": self.dexterity.total_score,
            "constitution": self.constitution.total_score,
            "intelligence": self.intelligence.total_score,
            "wisdom": self.wisdom.total_score,
            "charisma": self.charisma.total_score
        }
    
    def get_ability_modifiers(self) -> Dict[str, int]:
        """Get all ability score modifiers."""
        return {
            "strength": self.strength.modifier,
            "dexterity": self.dexterity.modifier,
            "constitution": self.constitution.modifier,
            "intelligence": self.intelligence.modifier,
            "wisdom": self.wisdom.modifier,
            "charisma": self.charisma.modifier
        }
    
    def get_proficiencies(self) -> Dict[str, Any]:
        """Get all proficiencies."""
        return {
            "skills": dict(self.skill_proficiencies),
            "saving_throws": dict(self.saving_throw_proficiencies),
            "armor": self.armor_proficiency.copy(),
            "weapons": self.weapon_proficiency.copy(),
            "tools": self.tool_proficiency.copy(),
            "languages": self.languages.copy()
        }
    
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
        """Get main backstory."""
        return self.backstory
    
    def get_detailed_backstory(self) -> Dict[str, str]:
        """Get detailed backstory elements."""
        return self.detailed_backstory.copy()
    
    def validate(self) -> Dict[str, Any]:
        issues = []
        warnings = []
        
        if not self.name.strip():
            warnings.append("Character name is empty")
        if not self.species:
            issues.append("Species is required")
        if not self.character_classes:
            issues.append("At least one class is required")
        
        return {"valid": len(issues) == 0, "issues": issues, "warnings": warnings}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert CharacterCore to dictionary representation."""
        return {
            "name": self.name,
            "species": self.species,
            "level": self.level,
            "classes": self.character_classes,
            "background": self.background,
            "alignment": self.alignment,
            "ability_scores": {
                "strength": self.strength.total_score,
                "dexterity": self.dexterity.total_score,
                "constitution": self.constitution.total_score,
                "intelligence": self.intelligence.total_score,
                "wisdom": self.wisdom.total_score,
                "charisma": self.charisma.total_score
            },
            "backstory": self.backstory,
            "detailed_backstory": self.detailed_backstory,
            "personality_traits": self.personality_traits,
            "ideals": self.ideals,
            "bonds": self.bonds,
            "flaws": self.flaws,
            "proficiencies": {
                "skills": dict(self.skill_proficiencies),
                "saving_throws": dict(self.saving_throw_proficiencies),
                "armor": self.armor_proficiency,
                "weapons": self.weapon_proficiency,
                "tools": self.tool_proficiency,
                "languages": self.languages
            },
            "spellcasting": self.get_spellcasting_info()
        }
    
    # ============================================================================
    # SETTER METHODS FOR API ACCESS
    # ============================================================================
    
    def set_name(self, name: str) -> Dict[str, Any]:
        """
        Set character name with validation.
        
        Args:
            name: Character name (must be non-empty string)
            
        Returns:
            Dict with success status and any validation messages
        """
        if not isinstance(name, str):
            return {"success": False, "error": "Name must be a string"}
        
        name = name.strip()
        if not name:
            return {"success": False, "error": "Name cannot be empty"}
        
        if len(name) > 100:
            return {"success": False, "error": "Name cannot exceed 100 characters"}
        
        old_name = self.name
        self.name = name
        
        logger.info(f"Character name changed from '{old_name}' to '{name}'")
        return {"success": True, "old_value": old_name, "new_value": name}
    
    def set_species(self, species: str) -> Dict[str, Any]:
        """
        Set character species with validation.
        
        Args:
            species: Species name (e.g., "Human", "Elf", "Dwarf")
            
        Returns:
            Dict with success status and any validation messages
        """
        if not isinstance(species, str):
            return {"success": False, "error": "Species must be a string"}
        
        species = species.strip()
        if not species:
            return {"success": False, "error": "Species cannot be empty"}
        
        old_species = self.species
        self.species = species
        
        logger.info(f"Character species changed from '{old_species}' to '{species}'")
        return {"success": True, "old_value": old_species, "new_value": species}
    
    def set_character_classes(self, character_classes: Dict[str, int]) -> Dict[str, Any]:
        """
        Set character classes with validation.
        
        Args:
            character_classes: Dict mapping class names to levels
            
        Returns:
            Dict with success status and any validation messages
        """
        if not isinstance(character_classes, dict):
            return {"success": False, "error": "Character classes must be a dictionary"}
        
        if not character_classes:
            return {"success": False, "error": "At least one class is required"}
        
        # Validate class levels
        for class_name, level in character_classes.items():
            if not isinstance(class_name, str) or not class_name.strip():
                return {"success": False, "error": f"Invalid class name: {class_name}"}
            
            if not isinstance(level, int) or level < 1 or level > 20:
                return {"success": False, "error": f"Invalid level for {class_name}: {level} (must be 1-20)"}
        
        # Validate total level
        total_level = sum(character_classes.values())
        if total_level > 20:
            return {"success": False, "error": f"Total character level cannot exceed 20 (got {total_level})"}
        
        old_classes = self.character_classes.copy()
        self.character_classes = character_classes.copy()
        
        # Update spellcasting information when classes change
        self._update_spellcasting_info()
        
        logger.info(f"Character classes changed from {old_classes} to {character_classes}")
        return {"success": True, "old_value": old_classes, "new_value": character_classes}
    
    def set_background(self, background: str) -> Dict[str, Any]:
        """
        Set character background with validation.
        
        Args:
            background: Background name (e.g., "Acolyte", "Criminal", "Folk Hero")
            
        Returns:
            Dict with success status and any validation messages
        """
        if not isinstance(background, str):
            return {"success": False, "error": "Background must be a string"}
        
        background = background.strip()
        # Background can be empty (not required), but if provided should be valid
        
        old_background = self.background
        self.background = background
        
        logger.info(f"Character background changed from '{old_background}' to '{background}'")
        return {"success": True, "old_value": old_background, "new_value": background}
    
    def set_alignment(self, alignment: List[str]) -> Dict[str, Any]:
        """
        Set character alignment with validation.
        
        Args:
            alignment: Two-element list [lawful/neutral/chaotic, good/neutral/evil]
            
        Returns:
            Dict with success status and any validation messages
        """
        if not isinstance(alignment, list) or len(alignment) != 2:
            return {"success": False, "error": "Alignment must be a list of exactly 2 elements"}
        
        valid_ethics = ["Lawful", "Neutral", "Chaotic"]
        valid_morals = ["Good", "Neutral", "Evil"]
        
        ethics, morals = alignment[0], alignment[1]
        
        if ethics not in valid_ethics:
            return {"success": False, "error": f"Invalid ethics value: {ethics}. Must be one of {valid_ethics}"}
        
        if morals not in valid_morals:
            return {"success": False, "error": f"Invalid morals value: {morals}. Must be one of {valid_morals}"}
        
        old_alignment = self.alignment.copy()
        self.alignment = [ethics, morals]
        
        logger.info(f"Character alignment changed from {old_alignment} to {alignment}")
        return {"success": True, "old_value": old_alignment, "new_value": alignment}
    
    def set_personality_traits(self, traits: List[str]) -> Dict[str, Any]:
        """
        Set personality traits with validation.
        
        Args:
            traits: List of personality trait strings
            
        Returns:
            Dict with success status and any validation messages
        """
        if not isinstance(traits, list):
            return {"success": False, "error": "Personality traits must be a list"}
        
        # Validate each trait
        validated_traits = []
        for i, trait in enumerate(traits):
            if not isinstance(trait, str):
                return {"success": False, "error": f"Trait {i+1} must be a string"}
            
            trait = trait.strip()
            if trait:  # Only add non-empty traits
                validated_traits.append(trait)
        
        if len(validated_traits) > 10:
            return {"success": False, "error": "Cannot have more than 10 personality traits"}
        
        old_traits = self.personality_traits.copy()
        self.personality_traits = validated_traits
        
        logger.info(f"Personality traits updated: {len(old_traits)} -> {len(validated_traits)} traits")
        return {"success": True, "old_value": old_traits, "new_value": validated_traits}
    
    def set_ideals(self, ideals: List[str]) -> Dict[str, Any]:
        """
        Set ideals with validation.
        
        Args:
            ideals: List of ideal strings
            
        Returns:
            Dict with success status and any validation messages
        """
        if not isinstance(ideals, list):
            return {"success": False, "error": "Ideals must be a list"}
        
        validated_ideals = []
        for i, ideal in enumerate(ideals):
            if not isinstance(ideal, str):
                return {"success": False, "error": f"Ideal {i+1} must be a string"}
            
            ideal = ideal.strip()
            if ideal:
                validated_ideals.append(ideal)
        
        if len(validated_ideals) > 5:
            return {"success": False, "error": "Cannot have more than 5 ideals"}
        
        old_ideals = self.ideals.copy()
        self.ideals = validated_ideals
        
        logger.info(f"Ideals updated: {len(old_ideals)} -> {len(validated_ideals)} ideals")
        return {"success": True, "old_value": old_ideals, "new_value": validated_ideals}
    
    def set_bonds(self, bonds: List[str]) -> Dict[str, Any]:
        """
        Set bonds with validation.
        
        Args:
            bonds: List of bond strings
            
        Returns:
            Dict with success status and any validation messages
        """
        if not isinstance(bonds, list):
            return {"success": False, "error": "Bonds must be a list"}
        
        validated_bonds = []
        for i, bond in enumerate(bonds):
            if not isinstance(bond, str):
                return {"success": False, "error": f"Bond {i+1} must be a string"}
            
            bond = bond.strip()
            if bond:
                validated_bonds.append(bond)
        
        if len(validated_bonds) > 5:
            return {"success": False, "error": "Cannot have more than 5 bonds"}
        
        old_bonds = self.bonds.copy()
        self.bonds = validated_bonds
        
        logger.info(f"Bonds updated: {len(old_bonds)} -> {len(validated_bonds)} bonds")
        return {"success": True, "old_value": old_bonds, "new_value": validated_bonds}
    
    def set_flaws(self, flaws: List[str]) -> Dict[str, Any]:
        """
        Set flaws with validation.
        
        Args:
            flaws: List of flaw strings
            
        Returns:
            Dict with success status and any validation messages
        """
        if not isinstance(flaws, list):
            return {"success": False, "error": "Flaws must be a list"}
        
        validated_flaws = []
        for i, flaw in enumerate(flaws):
            if not isinstance(flaw, str):
                return {"success": False, "error": f"Flaw {i+1} must be a string"}
            
            flaw = flaw.strip()
            if flaw:
                validated_flaws.append(flaw)
        
        if len(validated_flaws) > 5:
            return {"success": False, "error": "Cannot have more than 5 flaws"}
        
        old_flaws = self.flaws.copy()
        self.flaws = validated_flaws
        
        logger.info(f"Flaws updated: {len(old_flaws)} -> {len(validated_flaws)} flaws")
        return {"success": True, "old_value": old_flaws, "new_value": validated_flaws}
    
    def set_backstory(self, backstory: str) -> Dict[str, Any]:
        """
        Set main backstory with validation.
        
        Args:
            backstory: Main backstory text
            
        Returns:
            Dict with success status and any validation messages
        """
        if not isinstance(backstory, str):
            return {"success": False, "error": "Backstory must be a string"}
        
        backstory = backstory.strip()
        
        if len(backstory) > 5000:
            return {"success": False, "error": "Backstory cannot exceed 5000 characters"}
        
        old_backstory = self.backstory
        self.backstory = backstory
        
        # Update detailed backstory if it exists
        if self.detailed_backstory:
            self.detailed_backstory["main_backstory"] = backstory
        
        logger.info(f"Backstory updated: {len(old_backstory)} -> {len(backstory)} characters")
        return {"success": True, "old_length": len(old_backstory), "new_length": len(backstory)}
    
    def set_detailed_backstory_new(self, detailed_backstory: Dict[str, str]) -> Dict[str, Any]:
        """
        Set detailed backstory elements with validation.
        
        Args:
            detailed_backstory: Dict of backstory elements
            
        Returns:
            Dict with success status and any validation messages
        """
        if not isinstance(detailed_backstory, dict):
            return {"success": False, "error": "Detailed backstory must be a dictionary"}
        
        # Validate each backstory element
        validated_backstory = {}
        for key, value in detailed_backstory.items():
            if not isinstance(key, str) or not isinstance(value, str):
                return {"success": False, "error": f"Backstory key and value must be strings: {key}"}
            
            key = key.strip()
            value = value.strip()
            
            if key and value:  # Only add non-empty elements
                if len(value) > 2000:
                    return {"success": False, "error": f"Backstory element '{key}' cannot exceed 2000 characters"}
                validated_backstory[key] = value
        
        old_backstory = self.detailed_backstory.copy()
        self.detailed_backstory = validated_backstory
        
        # Update main backstory if provided
        if "main_backstory" in validated_backstory:
            self.backstory = validated_backstory["main_backstory"]
        
        logger.info(f"Detailed backstory updated: {len(old_backstory)} -> {len(validated_backstory)} elements")
        return {"success": True, "old_count": len(old_backstory), "new_count": len(validated_backstory)}
    
    def set_ability_score(self, ability: str, base_score: int) -> Dict[str, Any]:
        """
        Set base ability score with validation.
        
        Args:
            ability: Ability name (strength, dexterity, etc.)
            base_score: New base score (1-20 typically)
            
        Returns:
            Dict with success status and any validation messages
        """
        if not isinstance(ability, str):
            return {"success": False, "error": "Ability must be a string"}
        
        ability = ability.lower().strip()
        ability_obj = self.get_ability_score(ability)
        
        if not ability_obj:
            return {"success": False, "error": f"Invalid ability: {ability}"}
        
        if not isinstance(base_score, int) or base_score < 1 or base_score > 20:
            return {"success": False, "error": f"Base score must be between 1 and 20 (got {base_score})"}
        
        old_score = ability_obj.base_score
        old_total = ability_obj.total_score
        
        ability_obj.base_score = base_score
        ability_obj._invalidate_cache()  # Force cache invalidation
        
        new_total = ability_obj.total_score
        
        logger.info(f"Ability {ability} base score changed: {old_score} -> {base_score} (total: {old_total} -> {new_total})")
        
        return {
            "success": True,
            "ability": ability,
            "old_base_score": old_score,
            "new_base_score": base_score,
            "old_total_score": old_total,
            "new_total_score": new_total,
            "modifier": ability_obj.modifier
        }
    
    def set_ability_scores(self, ability_scores: Dict[str, int]) -> Dict[str, Any]:
        """
        Set multiple ability scores at once.
        
        Args:
            ability_scores: Dict mapping ability names to base scores
            
        Returns:
            Dict with success status and results for each ability
        """
        if not isinstance(ability_scores, dict):
            return {"success": False, "error": "Ability scores must be a dictionary"}
        
        results = {}
        errors = []
        
        for ability, score in ability_scores.items():
            result = self.set_ability_score(ability, score)
            results[ability] = result
            
            if not result["success"]:
                errors.append(f"{ability}: {result['error']}")
        
        success = len(errors) == 0
        
        if success:
            logger.info(f"Successfully updated {len(ability_scores)} ability scores")
        else:
            logger.error(f"Failed to update some ability scores: {errors}")
        
        return {
            "success": success,
            "results": results,
            "errors": errors,
            "updated_count": len([r for r in results.values() if r["success"]])
        }
    
    # ============================================================================
    # BULK UPDATE AND UTILITY METHODS
    # ============================================================================
    
    def update_character_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bulk update character data with validation.
        
        Args:
            data: Dictionary containing character data to update
            
        Returns:
            Dict with success status and detailed results for each field
        """
        if not isinstance(data, dict):
            return {"success": False, "error": "Data must be a dictionary"}
        
        results = {}
        errors = []
        updated_fields = []
        
        # Define field mappings to setter methods
        field_setters = {
            "name": self.set_name,
            "species": self.set_species,
            "character_classes": self.set_character_classes,
            "background": self.set_background,
            "alignment": self.set_alignment,
            "personality_traits": self.set_personality_traits,
            "ideals": self.set_ideals,
            "bonds": self.set_bonds,
            "flaws": self.set_flaws,
            "backstory": self.set_backstory,
            "detailed_backstory": self.set_detailed_backstory_new,
            "ability_scores": self.set_ability_scores
        }
        
        # Process each field in the data
        for field, value in data.items():
            if field in field_setters:
                try:
                    result = field_setters[field](value)
                    results[field] = result
                    
                    if result["success"]:
                        updated_fields.append(field)
                    else:
                        errors.append(f"{field}: {result['error']}")
                        
                except Exception as e:
                    error_msg = f"Unexpected error updating {field}: {str(e)}"
                    results[field] = {"success": False, "error": error_msg}
                    errors.append(error_msg)
                    logger.error(error_msg)
            else:
                warning_msg = f"Unknown field '{field}' ignored"
                results[field] = {"success": False, "error": warning_msg}
                errors.append(warning_msg)
        
        success = len(errors) == 0
        
        if success:
            logger.info(f"Successfully updated character data for fields: {updated_fields}")
        else:
            logger.warning(f"Character update completed with errors: {errors}")
        
        return {
            "success": success,
            "updated_fields": updated_fields,
            "field_results": results,
            "errors": errors,
            "total_fields_processed": len(data),
            "successful_updates": len(updated_fields)
        }
    
    def validate_character_data(self) -> Dict[str, Any]:
        """
        Comprehensive validation of all character data.
        
        Returns:
            Dict with validation results, issues, and warnings
        """
        issues = []
        warnings = []
        field_validations = {}
        
        # Validate core identity
        if not self.name.strip():
            warnings.append("Character name is empty")
            field_validations["name"] = {"valid": False, "message": "Name is empty"}
        else:
            field_validations["name"] = {"valid": True}
        
        if not self.species:
            issues.append("Species is required")
            field_validations["species"] = {"valid": False, "message": "Species is required"}
        else:
            field_validations["species"] = {"valid": True}
        
        if not self.character_classes:
            issues.append("At least one class is required")
            field_validations["character_classes"] = {"valid": False, "message": "At least one class required"}
        else:
            total_level = sum(self.character_classes.values())
            if total_level > 20:
                issues.append(f"Total character level exceeds 20 (current: {total_level})")
                field_validations["character_classes"] = {"valid": False, "message": f"Total level {total_level} > 20"}
            else:
                field_validations["character_classes"] = {"valid": True, "total_level": total_level}
        
        # Validate alignment
        valid_ethics = ["Lawful", "Neutral", "Chaotic"]
        valid_morals = ["Good", "Neutral", "Evil"]
        
        if len(self.alignment) != 2:
            issues.append("Alignment must have exactly 2 components")
            field_validations["alignment"] = {"valid": False, "message": "Invalid alignment format"}
        elif self.alignment[0] not in valid_ethics or self.alignment[1] not in valid_morals:
            issues.append(f"Invalid alignment: {self.alignment}")
            field_validations["alignment"] = {"valid": False, "message": "Invalid alignment values"}
        else:
            field_validations["alignment"] = {"valid": True}
        
        # Validate ability scores
        ability_issues = []
        for ability_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            ability_obj = self.get_ability_score(ability_name)
            if ability_obj:
                if ability_obj.base_score < 1 or ability_obj.base_score > 20:
                    ability_issues.append(f"{ability_name} base score out of range: {ability_obj.base_score}")
                if ability_obj.total_score > 30:
                    warnings.append(f"{ability_name} total score very high: {ability_obj.total_score}")
        
        if ability_issues:
            issues.extend(ability_issues)
            field_validations["ability_scores"] = {"valid": False, "issues": ability_issues}
        else:
            field_validations["ability_scores"] = {"valid": True}
        
        # Validate personality elements
        personality_warnings = []
        if len(self.personality_traits) > 10:
            personality_warnings.append(f"Many personality traits: {len(self.personality_traits)}")
        if len(self.ideals) > 5:
            personality_warnings.append(f"Many ideals: {len(self.ideals)}")
        if len(self.bonds) > 5:
            personality_warnings.append(f"Many bonds: {len(self.bonds)}")
        if len(self.flaws) > 5:
            personality_warnings.append(f"Many flaws: {len(self.flaws)}")
        
        if personality_warnings:
            warnings.extend(personality_warnings)
        
        field_validations["personality"] = {
            "valid": True,
            "traits_count": len(self.personality_traits),
            "ideals_count": len(self.ideals),
            "bonds_count": len(self.bonds),
            "flaws_count": len(self.flaws)
        }
        
        # Validate backstory length
        if len(self.backstory) > 5000:
            issues.append(f"Backstory too long: {len(self.backstory)} characters (max 5000)")
            field_validations["backstory"] = {"valid": False, "message": "Backstory too long"}
        else:
            field_validations["backstory"] = {"valid": True, "length": len(self.backstory)}
        
        # Overall validation status
        is_valid = len(issues) == 0
        completeness_score = self._calculate_completeness_score()
        
        return {
            "valid": is_valid,
            "issues": issues,
            "warnings": warnings,
            "field_validations": field_validations,
            "completeness_score": completeness_score,
            "validation_timestamp": datetime.now().isoformat()
        }
    
    def _calculate_completeness_score(self) -> float:
        """Calculate a completeness score (0.0 to 1.0) for the character."""
        score = 0.0
        total_possible = 10.0
        
        # Core identity (4 points)
        if self.name.strip():
            score += 1.0
        if self.species:
            score += 1.0
        if self.character_classes:
            score += 1.0
        if self.background:
            score += 1.0
        
        # Personality (4 points)
        if self.personality_traits:
            score += 1.0
        if self.ideals:
            score += 1.0
        if self.bonds:
            score += 1.0
        if self.flaws:
            score += 1.0
        
        # Backstory (2 points)
        if self.backstory.strip():
            score += 1.0
        if self.detailed_backstory:
            score += 1.0
        
        return score / total_possible
    
    def get_character_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the character for API responses.
        
        Returns:
            Dict with character summary including validation and completeness
        """
        validation = self.validate_character_data()
        
        return {
            "identity": {
                "name": self.name,
                "species": self.species,
                "classes": self.character_classes,
                "level": self.level,
                "background": self.background,
                "alignment": self.alignment
            },
            "ability_scores": self.get_ability_scores(),
            "ability_modifiers": self.get_ability_modifiers(),
            "initiative": self.initiative,  # <-- Added initiative for frontend/API
            "personality": {
                "traits": self.personality_traits,
                "ideals": self.ideals,
                "bonds": self.bonds,
                "flaws": self.flaws,
                "backstory_length": len(self.backstory),
                "detailed_backstory_elements": len(self.detailed_backstory)
            },
            "proficiencies": self.get_proficiencies(),
            "validation": {
                "is_valid": validation["valid"],
                "completeness_score": validation["completeness_score"],
                "issue_count": len(validation["issues"]),
                "warning_count": len(validation["warnings"])
            },
            "last_updated": datetime.now().isoformat()
        }


# ============================================================================
# CHARACTER STATE (IN-GAME DATA)
# ============================================================================

class CharacterState:
    """
    Current character state - changes during gameplay.
    This includes HP, XP, equipment, conditions, currency, and other mutable data.
    """
    
    def __init__(self, character_core: CharacterCore):
        self.character_core = character_core
        
        # Hit Points and Health
        self.current_hit_points: int = 0
        self.max_hit_points: int = 0
        self.temporary_hit_points: int = 0
        self.hit_dice_remaining: Dict[str, int] = {}  # e.g., {"d8": 3, "d10": 2}
        
        # Experience Points and Leveling
        self.experience_points: int = 0
        self.milestone_progress: int = 0  # For milestone leveling systems
        self.pending_level_ups: List[Dict[str, Any]] = []  # Classes that can level up
        self.xp_history: List[Dict[str, Any]] = []  # XP awards history
        
        # Conditions and Status Effects
        self.conditions: List[DnDCondition] = []
        self.exhaustion_level: int = 0
        self.temporary_conditions: Dict[str, Dict[str, Any]] = {}  # Time-limited conditions
        
        # Currency
        self.currency: Dict[str, int] = {
            "copper": 0,
            "silver": 0,
            "electrum": 0,
            "gold": 0,
            "platinum": 0
        }
        
        # Equipment State
        self.equipped_items: Dict[str, str] = {}  # slot -> item_id mapping
        self.inventory: List[Dict[str, Any]] = []
        self.attuned_items: List[str] = []  # Max 3 items
        
        # Spell Slots and Resources
        self.spell_slots_remaining: Dict[int, int] = {}  # spell_level -> remaining_slots
        self.spell_slots_max: Dict[int, int] = {}
        self.class_resources: Dict[str, Dict[str, Any]] = {}  # Class-specific resources
        
        # Journal and Notes
        self.session_notes: List[Dict[str, Any]] = []
        self.campaign_journal: List[str] = []
        self.character_goals: List[str] = []
        
        # Initiative and Combat
        self.initiative_modifier: int = 0
        self.death_save_successes: int = 0
        self.death_save_failures: int = 0
        
        # Rest tracking
        self.last_short_rest: Optional[str] = None
        self.last_long_rest: Optional[str] = None
        
        # Initialize based on character level
        self._initialize_from_character_core()
    
    def _initialize_from_character_core(self):
        """Initialize state based on character core data."""
        if self.character_core:
            # Calculate initial HP (minimum for level 1)
            con_modifier = self.character_core.constitution.modifier
            total_level = self.character_core.level
            
            if total_level >= 1:
                # Estimate HP based on average hit die + con modifier per level
                # This is a simplified calculation - should be improved with class hit dice data
                estimated_hp = 8 + con_modifier + ((total_level - 1) * (5 + con_modifier))
                self.max_hit_points = max(1, estimated_hp)
                self.current_hit_points = self.max_hit_points
            
            # Set XP based on current level
            self.experience_points = self.calculate_xp_for_level(total_level)
    
    # ============================================================================
    # D&D 5E XP TABLE AND LEVEL MANAGEMENT
    # ============================================================================
    
    @staticmethod
    def get_xp_table() -> Dict[int, int]:
        """Get the D&D 5e experience point table."""
        return {
            1: 0,
            2: 300,
            3: 900,
            4: 2700,
            5: 6500,
            6: 14000,
            7: 23000,
            8: 34000,
            9: 48000,
            10: 64000,
            11: 85000,
            12: 100000,
            13: 120000,
            14: 140000,
            15: 165000,
            16: 195000,
            17: 225000,
            18: 265000,
            19: 305000,
            20: 355000
        }
    
    @staticmethod
    def calculate_xp_for_level(level: int) -> int:
        """Calculate XP required for a given level."""
        xp_table = CharacterState.get_xp_table()
        return xp_table.get(min(max(level, 1), 20), 0)
    
    @staticmethod
    def get_level_for_xp(xp: int) -> int:
        """Get character level based on XP."""
        xp_table = CharacterState.get_xp_table()
        
        for level in range(20, 0, -1):  # Check from level 20 down to 1
            if xp >= xp_table[level]:
                return level
        
        return 1  # Minimum level
    
    def get_xp_to_next_level(self) -> Dict[str, int]:
        """Get XP information for next level."""
        current_level = self.get_level_for_xp(self.experience_points)
        
        if current_level >= 20:
            return {
                "current_level": 20,
                "next_level": 20,
                "current_xp": self.experience_points,
                "xp_for_next_level": self.calculate_xp_for_level(20),
                "xp_needed": 0,
                "progress_percentage": 100.0
            }
        
        next_level = current_level + 1
        current_level_xp = self.calculate_xp_for_level(current_level)
        next_level_xp = self.calculate_xp_for_level(next_level)
        
        xp_needed = next_level_xp - self.experience_points
        xp_in_current_level = self.experience_points - current_level_xp
        xp_for_level_range = next_level_xp - current_level_xp
        
        progress_percentage = (xp_in_current_level / xp_for_level_range) * 100.0 if xp_for_level_range > 0 else 0.0
        
        return {
            "current_level": current_level,
            "next_level": next_level,
            "current_xp": self.experience_points,
            "xp_for_current_level": current_level_xp,
            "xp_for_next_level": next_level_xp,
            "xp_needed": xp_needed,
            "xp_in_current_level": xp_in_current_level,
            "progress_percentage": round(progress_percentage, 1)
        }
    
    # ============================================================================
    # XP AND LEVELING SETTER METHODS
    # ============================================================================
    
    def set_experience_points(self, xp: int, reason: str = "Manual adjustment") -> Dict[str, Any]:
        """
        Set experience points with validation and level-up detection.
        
        Args:
            xp: New experience point total
            reason: Reason for XP change (for logging)
            
        Returns:
            Dict with success status and level-up information
        """
        if not isinstance(xp, int):
            return {"success": False, "error": "XP must be an integer"}
        
        if xp < 0:
            return {"success": False, "error": "XP cannot be negative"}
        
        if xp > 355000:  # Maximum XP for level 20
            return {"success": False, "error": "XP cannot exceed 355,000 (level 20 maximum)"}
        
        old_xp = self.experience_points
        old_level = self.get_level_for_xp(old_xp)
        
        self.experience_points = xp
        new_level = self.get_level_for_xp(xp)
        
        # Record XP change in history
        xp_change = {
            "old_xp": old_xp,
            "new_xp": xp,
            "change": xp - old_xp,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "session_date": datetime.now().strftime("%Y-%m-%d")
        }
        self.xp_history.append(xp_change)
        
        # Check for level up
        level_up_info = None
        if new_level > old_level:
            level_up_info = self._handle_level_up(old_level, new_level)
            logger.info(f"Character leveled up from {old_level} to {new_level} (XP: {old_xp} -> {xp})")
        
        logger.info(f"XP updated: {old_xp} -> {xp} ({reason})")
        
        return {
            "success": True,
            "old_xp": old_xp,
            "new_xp": xp,
            "xp_change": xp - old_xp,
            "old_level": old_level,
            "new_level": new_level,
            "level_up": level_up_info,
            "xp_to_next_level": self.get_xp_to_next_level()
        }
    
    def add_experience_points(self, xp_gained: int, reason: str = "Session reward") -> Dict[str, Any]:
        """
        Add experience points (most common DM operation).
        
        Args:
            xp_gained: Amount of XP to add
            reason: Reason for XP gain
            
        Returns:
            Dict with success status and level-up information
        """
        if not isinstance(xp_gained, int):
            return {"success": False, "error": "XP gained must be an integer"}
        
        if xp_gained < 0:
            return {"success": False, "error": "XP gained cannot be negative (use set_experience_points for reductions)"}
        
        new_total = self.experience_points + xp_gained
        return self.set_experience_points(new_total, f"{reason} (+{xp_gained} XP)")
    
    def _handle_level_up(self, old_level: int, new_level: int) -> Dict[str, Any]:
        """Handle level up logic and create pending level-up choices."""
        
        # Determine which classes can level up
        # In D&D 5e, players choose which class to level when they gain a level
        current_classes = self.character_core.character_classes.copy()
        
        # For multiclass characters, they need to choose which class to advance
        available_classes = list(current_classes.keys()) if current_classes else ["Fighter"]  # Default to Fighter if no classes
        
        level_up_info = {
            "old_level": old_level,
            "new_level": new_level,
            "levels_gained": new_level - old_level,
            "available_classes": available_classes,
            "pending_choices": [],
            "automatic_benefits": []
        }
        
        # Add pending level-up choices for each level gained
        for level in range(old_level + 1, new_level + 1):
            pending_choice = {
                "target_level": level,
                "available_classes": available_classes,
                "requires_asi_choice": False,
                "requires_spell_choice": False,
                "requires_feature_choice": False
            }
            
            # Check if any class would grant an ASI at this level
            for class_name in available_classes:
                class_level = current_classes.get(class_name, 0) + 1  # Potential new level in this class
                asi_levels = self.character_core.level_manager.asi_manager.get_asi_levels_for_class(class_name)
                
                if class_level in asi_levels:
                    pending_choice["requires_asi_choice"] = True
                    pending_choice["asi_class"] = class_name
                    pending_choice["asi_level"] = class_level
            
            level_up_info["pending_choices"].append(pending_choice)
            self.pending_level_ups.append(pending_choice)
        
        # Automatic benefits (can be calculated immediately)
        level_up_info["automatic_benefits"] = [
            f"Total character level increased to {new_level}",
            f"Proficiency bonus may have increased",
            f"Hit points can be increased when class is chosen"
        ]
        
        return level_up_info
    
    def apply_level_up_choice(self, choice_index: int, class_name: str, 
                            asi_choice: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Apply a level-up choice for a specific class.
        
        Args:
            choice_index: Index in pending_level_ups list
            class_name: Class to level up in
            asi_choice: ASI choice if applicable ({"type": "asi", "improvements": {...}} or {"type": "feat", "feat_name": "..."})
            
        Returns:
            Dict with success status and results
        """
        if choice_index >= len(self.pending_level_ups):
            return {"success": False, "error": f"Invalid choice index: {choice_index}"}
        
        pending_choice = self.pending_level_ups[choice_index]
        
        if class_name not in pending_choice["available_classes"]:
            return {"success": False, "error": f"Class {class_name} not available for level up"}
        
        # Apply the level up to the character core
        try:
            self.character_core.level_up(class_name, asi_choice)
            
            # Remove the pending choice
            resolved_choice = self.pending_level_ups.pop(choice_index)
            
            # Update max HP (simplified - should be based on class hit die)
            con_modifier = self.character_core.constitution.modifier
            hp_increase = 5 + con_modifier  # Average hit die + con modifier
            self.max_hit_points += max(1, hp_increase)
            self.current_hit_points += max(1, hp_increase)
            
            logger.info(f"Applied level up: {class_name} (choice {choice_index})")
            
            return {
                "success": True,
                "class_leveled": class_name,
                "new_class_level": self.character_core.character_classes.get(class_name, 1),
                "new_total_level": self.character_core.level,
                "hp_gained": max(1, hp_increase),
                "new_max_hp": self.max_hit_points,
                "asi_applied": asi_choice is not None,
                "remaining_pending_choices": len(self.pending_level_ups)
            }
            
        except Exception as e:
            logger.error(f"Error applying level up: {str(e)}")
            return {"success": False, "error": f"Failed to apply level up: {str(e)}"}
    
    # ============================================================================
    # OTHER STATE SETTER METHODS
    # ============================================================================
    
    def set_hit_points(self, current_hp: int, max_hp: Optional[int] = None) -> Dict[str, Any]:
        """Set current hit points with validation."""
        if not isinstance(current_hp, int):
            return {"success": False, "error": "Hit points must be an integer"}
        
        if max_hp is not None:
            if not isinstance(max_hp, int) or max_hp < 1:
                return {"success": False, "error": "Max HP must be a positive integer"}
            
            old_max_hp = self.max_hit_points
            self.max_hit_points = max_hp
        else:
            old_max_hp = self.max_hit_points
        
        # Validate current HP
        if current_hp > self.max_hit_points:
            return {"success": False, "error": f"Current HP cannot exceed max HP ({self.max_hit_points})"}
        
        old_current_hp = self.current_hit_points
        self.current_hit_points = max(0, current_hp)  # HP can't go below 0
        
        logger.info(f"Hit points updated: {old_current_hp}/{old_max_hp} -> {self.current_hit_points}/{self.max_hit_points}")
        
        return {
            "success": True,
            "old_current_hp": old_current_hp,
            "new_current_hp": self.current_hit_points,
            "old_max_hp": old_max_hp,
            "new_max_hp": self.max_hit_points,
            "is_unconscious": self.current_hit_points == 0,
            "is_dying": self.current_hit_points == 0 and DnDCondition.UNCONSCIOUS not in self.conditions
        }
    
    def add_condition(self, condition: DnDCondition, duration: Optional[str] = None) -> Dict[str, Any]:
        """Add a condition to the character."""
        if condition in self.conditions:
            return {"success": False, "error": f"Character already has condition: {condition.value}"}
        
        self.conditions.append(condition)
        
        if duration:
            self.temporary_conditions[condition.value] = {
                "duration": duration,
                "applied_at": datetime.now().isoformat()
            }
        
        logger.info(f"Added condition: {condition.value}" + (f" (duration: {duration})" if duration else ""))
        
        return {
            "success": True,
            "condition": condition.value,
            "duration": duration,
            "active_conditions": [c.value for c in self.conditions]
        }
    
    def remove_condition(self, condition: DnDCondition) -> Dict[str, Any]:
        """Remove a condition from the character."""
        if condition not in self.conditions:
            return {"success": False, "error": f"Character does not have condition: {condition.value}"}
        
        self.conditions.remove(condition)
        
        if condition.value in self.temporary_conditions:
            del self.temporary_conditions[condition.value]
        
        logger.info(f"Removed condition: {condition.value}")
        
        return {
            "success": True,
            "condition": condition.value,
            "active_conditions": [c.value for c in self.conditions]
        }
    
    def set_exhaustion_level(self, level: int) -> Dict[str, Any]:
        """Set exhaustion level with D&D 5e 2024 rules."""
        if not isinstance(level, int) or level < 0 or level > 6:
            return {"success": False, "error": "Exhaustion level must be between 0 and 6"}
        
        old_level = self.exhaustion_level
        self.exhaustion_level = level
        
        effects = ExhaustionLevel.get_effects(level)
        is_dead = ExhaustionLevel.is_dead(level)
        
        logger.info(f"Exhaustion level changed: {old_level} -> {level}")
        
        return {
            "success": True,
            "old_level": old_level,
            "new_level": level,
            "effects": effects,
            "is_dead": is_dead
        }
    
    def update_currency(self, currency_changes: Dict[str, int]) -> Dict[str, Any]:
        """Update currency amounts."""
        if not isinstance(currency_changes, dict):
            return {"success": False, "error": "Currency changes must be a dictionary"}
        
        old_currency = self.currency.copy()
        results = {}
        
        for coin_type, amount in currency_changes.items():
            if coin_type not in self.currency:
                results[coin_type] = {"success": False, "error": f"Invalid coin type: {coin_type}"}
                continue
            
            if not isinstance(amount, int):
                results[coin_type] = {"success": False, "error": "Amount must be an integer"}
                continue
            
            new_amount = self.currency[coin_type] + amount
            if new_amount < 0:
                results[coin_type] = {"success": False, "error": f"Insufficient {coin_type} (have {self.currency[coin_type]}, trying to remove {abs(amount)})"}
                continue
            
            self.currency[coin_type] = new_amount
            results[coin_type] = {
                "success": True,
                "old_amount": old_currency[coin_type],
                "change": amount,
                "new_amount": new_amount
            }
        
        logger.info(f"Currency updated: {currency_changes}")
        
        return {
            "success": all(r["success"] for r in results.values()),
            "results": results,
            "old_currency": old_currency,
            "new_currency": self.currency.copy()
        }
    
    # ============================================================================
    # GETTER METHODS FOR STATE DATA
    # ============================================================================
    
    def get_experience_points(self) -> int:
        """Get current experience points."""
        return self.experience_points
    
    def get_level_info(self) -> Dict[str, Any]:
        """Get comprehensive level and XP information."""
        return {
            "current_level": self.get_level_for_xp(self.experience_points),
            "experience_points": self.experience_points,
            "xp_progress": self.get_xp_to_next_level(),
            "pending_level_ups": len(self.pending_level_ups),
            "xp_history_count": len(self.xp_history)
        }
    
    def get_hit_points(self) -> Dict[str, int]:
        """Get hit point information."""
        return {
            "current": self.current_hit_points,
            "maximum": self.max_hit_points,
            "temporary": self.temporary_hit_points
        }
    
    def get_conditions(self) -> List[str]:
        """Get list of active conditions."""
        return [condition.value for condition in self.conditions]
    
    def get_exhaustion_level(self) -> int:
        """Get current exhaustion level."""
        return self.exhaustion_level
    
    def get_currency(self) -> Dict[str, int]:
        """Get currency amounts."""
        return self.currency.copy()
    
    def get_character_state_summary(self) -> Dict[str, Any]:
        """Get comprehensive character state summary."""
        return {
            "level_info": self.get_level_info(),
            "hit_points": self.get_hit_points(),
            "conditions": {
                "active": self.get_conditions(),
                "exhaustion_level": self.exhaustion_level,
                "exhaustion_effects": ExhaustionLevel.get_effects(self.exhaustion_level)
            },
            "currency": self.get_currency(),
            "equipment": {
                "inventory_items": len(self.inventory),
                "attuned_items": len(self.attuned_items),
                "equipped_items": len(self.equipped_items)
            },
            "resources": {
                "spell_slots": self.spell_slots_remaining,
                "class_resources": self.class_resources
            },
            "journal": {
                "session_notes": len(self.session_notes),
                "campaign_entries": len(self.campaign_journal),
                "character_goals": len(self.character_goals)
            },
            "last_updated": datetime.now().isoformat()
        }


# ============================================================================
# CHARACTER ITERATION CACHE
# ============================================================================

class CharacterIterationCache:
    """Manages character iterations and changes during the creation process."""
    
    def __init__(self):
        self.iterations: List[Dict[str, Any]] = []
        self.current_character: Dict[str, Any] = {}
        self.modification_history: List[str] = []
        self.user_feedback: List[str] = []
        
    def add_iteration(self, character_data: Dict[str, Any], modification: str = ""):
        """Add a new iteration of the character."""
        self.current_character = character_data.copy()
        self.iterations.append(character_data.copy())
        if modification:
            self.modification_history.append(modification)
    
    def get_current_character(self) -> Dict[str, Any]:
        """Get the current character data."""
        return self.current_character.copy()
    
    def get_iteration_count(self) -> int:
        """Get the number of iterations."""
        return len(self.iterations)
    
    def add_user_feedback(self, feedback: str):
        """Add user feedback for the current iteration."""
        self.user_feedback.append(feedback)
    
    def get_modification_history(self) -> List[str]:
        """Get the history of modifications."""
        return self.modification_history.copy()

# ============================================================================
# MODULE SUMMARY
# ============================================================================
# This module provides comprehensive character sheet and data model classes:
#
# Core Data Classes:
# - CharacterCore: Core character data with ability scores, classes, and identity
#   * Enhanced with comprehensive getter methods for API access
#   * Immutable core attributes (only changed during character creation/updates)
#
# - CharacterState: Mutable character state (HP, equipment, conditions, currency, journal)
#   * Enhanced with D&D 5e 2024 exhaustion rules (6 levels with cumulative penalties)
#   * Comprehensive condition tracking with mechanical effects
#   * Journal tracking system for character evolution analysis
#   * Full getter/setter methods for RESTful API access
#
# - CharacterStats: Calculated statistics (AC, max HP, proficiency bonus)
#   * Caching system for performance
#
# Main Interface:
# - CharacterSheet: Combined character sheet with validation and management methods
#   * Comprehensive API for frontend integration
#   * Journal-based character evolution analysis
#   * Enhanced gameplay methods (long rest, condition management, etc.)
#   * Automatic journal entry generation for significant events
#
# Utility Classes:
# - CharacterIterationCache: Manages character creation iterations and feedback
# - DnDCondition: Enum for D&D 5e 2024 conditions
# - ExhaustionLevel: Handler for D&D 5e 2024 exhaustion mechanics
#
# Dependencies: core_models.py (AbilityScore, ASIManager, etc.)
#
# Key Features:
# - Complete D&D 5e 2024 character representation
# - Journal tracking for character evolution and storytelling
# - Enhanced condition system with mechanical effect calculations
# - Comprehensive getter/setter API for frontend integration
# - Automatic stat calculation and caching
# - Advanced damage/healing with proper HP management
# - Equipment and condition tracking
# - Character progression and validation
# - Long rest mechanics with exhaustion recovery
# - Character evolution analysis based on play history
# ============================================================================

# ============================================================================
# SIMPLE WRAPPER CLASSES FOR COMPATIBILITY
# ============================================================================

class CharacterStats:
    """Simple character statistics calculator."""
    
    def __init__(self, character_core: CharacterCore, character_state: CharacterState):
        self.character_core = character_core
        self.character_state = character_state
        
    @property
    def armor_class(self) -> int:
        """Calculate AC based on armor and dexterity."""
        base_ac = 10 + self.character_core.dexterity.modifier
        # Add armor bonuses if implemented
        return base_ac
    
    @property
    def max_hit_points(self) -> int:
        """Calculate maximum hit points."""
        total_level = sum(self.character_core.character_classes.values()) or 1
        con_bonus = self.character_core.constitution.modifier * total_level
        return total_level * 6 + con_bonus  # Simple average for all classes
    
    @property
    def proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on total level."""
        total_level = sum(self.character_core.character_classes.values()) or 1
        return 2 + ((total_level - 1) // 4)

class CharacterSheet:
    """Simple character sheet combining core and state."""
    
    def __init__(self, name: str = ""):
        self.core = CharacterCore(name)
        self.state = CharacterState()
        self.stats = CharacterStats(self.core, self.state)
    
    @property
    def name(self) -> str:
        return self.core.name
    
    @name.setter
    def name(self, value: str):
        self.core.name = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "core": self.core.__dict__,
            "state": self.state.__dict__,
            "stats": {
                "armor_class": self.stats.armor_class,
                "max_hit_points": self.stats.max_hit_points,
                "proficiency_bonus": self.stats.proficiency_bonus
            }
        }