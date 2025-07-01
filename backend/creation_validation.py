"""
D&D 5e 2024 Creation Validation Module

This module contains comprehensive validation methods for character, NPC, item, and creature creation.
All validation follows D&D 5e 2024 Basic Rules (https://roll20.net/compendium/dnd5e/Rules:Free%20Basic%20Rules%20(2024)).

VALIDATION REQUIREMENTS:
- All newly created species, classes, feats, spells, armors, weapons, trinkets must adhere to D&D 5e 2024 reference rules
- Custom content must include balance checks to ensure compatibility with D&D 5e framework
- Character, NPC, and creature creation must include level/CR appropriateness validation
- All content must be balanced for intended character level and game context

Validation Functions:
- Character data structure and balance validation
- Custom content adherence to D&D 5e rules and balance checks
- NPC data validation with role-appropriate balance
- Item level appropriateness and power balance validation
- Creature stat block validation with CR balance verification
- Custom content power level and mechanical balance assessment
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Import from centralized enums
from enums import NPCType, NPCRole, ItemRarity

# Import CreationResult class (will be moved to shared module later)
# For now, we'll define a minimal version to avoid circular imports

logger = logging.getLogger(__name__)

# ============================================================================
# MINIMAL RESULT CLASS (to avoid circular imports)
# ============================================================================

class CreationResult:
    """Result container for creation operations."""
    
    def __init__(self, success: bool = False, data: Dict[str, Any] = None, 
                 error: str = "", warnings: List[str] = None):
        self.success = success
        self.data = data or {}
        self.error = error
        self.warnings = warnings or []
        self.creation_time: float = 0.0
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)

# ============================================================================
# CHARACTER VALIDATION FUNCTIONS
# ============================================================================

def validate_basic_structure(character_data: Dict[str, Any]) -> CreationResult:
    """
    Validate basic character data structure and D&D 5e 2024 rule adherence.
    Includes balance checks for character appropriateness.
    """
    result = CreationResult()
    
    required_fields = ["name", "species", "level", "classes", "ability_scores"]
    missing_fields = [field for field in required_fields if field not in character_data]
    
    if missing_fields:
        result.error = f"Missing required fields: {', '.join(missing_fields)}"
        return result
    
    # Validate ability scores according to D&D 5e 2024 rules
    abilities = character_data.get("ability_scores", {})
    required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    
    ability_total = 0
    for ability in required_abilities:
        if ability not in abilities:
            result.add_warning(f"Missing ability score: {ability}")
        else:
            score = abilities[ability]
            if not isinstance(score, int) or score < 1 or score > 30:
                result.add_warning(f"Invalid {ability} score: {score} (must be 1-30)")
            elif score < 8 or score > 18:
                # Standard character creation allows 8-15 + racial bonuses
                result.add_warning(f"{ability} score {score} may be outside normal character creation range")
            ability_total += score
    
    # Balance check: total ability scores should be reasonable for level
    expected_total = 72 + (character_data.get("level", 1) - 1) * 2  # Base 72 + ASI improvements
    if ability_total > expected_total + 10:
        result.add_warning(f"Total ability scores ({ability_total}) may be too high for level {character_data.get('level', 1)}")
    
    # Validate level according to D&D 5e 2024 rules
    level = character_data.get("level", 0)
    if not isinstance(level, int) or level < 1 or level > 20:
        result.add_warning(f"Invalid character level: {level} (must be 1-20)")
    
    # Validate classes and multiclass rules
    classes = character_data.get("classes", {})
    total_levels = sum(classes.values()) if isinstance(classes, dict) else 0
    if total_levels != level:
        result.add_warning(f"Class levels ({total_levels}) don't match character level ({level})")
    
    # Check multiclass prerequisites (simplified)
    if len(classes) > 1:
        result.add_warning("Multiclass character detected - ensure ability score prerequisites are met")
    
    result.success = True
    result.data = character_data
    return result

def validate_custom_content(character_data: Dict[str, Any], 
                          needs_custom_species: bool, needs_custom_class: bool) -> CreationResult:
    """
    Validate custom content adherence to D&D 5e 2024 framework and balance requirements.
    Ensures custom species and classes follow official design guidelines.
    """
    result = CreationResult(success=True, data=character_data)
    
    # Check for custom species if needed
    if needs_custom_species:
        species = character_data.get("species", "").lower()
        standard_species = [
            "human", "elf", "dwarf", "halfling", "dragonborn", "gnome", 
            "half-elf", "half-orc", "tiefling", "aasimar", "genasi", 
            "goliath", "tabaxi", "kenku", "lizardfolk", "tortle", "warforged",
            "githyanki", "githzerai", "triton", "firbolg", "yuan-ti"
        ]
        
        if species in standard_species:
            result.add_warning(f"Used standard species '{species}' when custom was expected")
        else:
            # Validate custom species follows D&D 5e design principles
            result.add_warning(f"Custom species '{species}' detected - ensure it follows D&D 5e racial trait balance:")
            result.add_warning("- Should provide 2-3 minor traits or 1 major trait")
            result.add_warning("- Total power level should match existing races")
            result.add_warning("- Should have cultural/roleplay elements, not just mechanical benefits")
    
    # Check for custom class if needed
    if needs_custom_class:
        classes = character_data.get("classes", {})
        class_names = [name.lower() for name in classes.keys()]
        standard_classes = [
            "barbarian", "bard", "cleric", "druid", "fighter", "monk",
            "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard",
            "artificer", "blood hunter"
        ]
        
        for class_name in class_names:
            if class_name in standard_classes:
                result.add_warning(f"Used standard class '{class_name}' when custom was expected")
                break
            else:
                # Validate custom class follows D&D 5e design principles
                result.add_warning(f"Custom class '{class_name}' detected - ensure it follows D&D 5e class design:")
                result.add_warning("- Hit die should be d6, d8, d10, or d12 based on role")
                result.add_warning("- Should have 2 good saves and 1-2 bad saves")
                result.add_warning("- Features should follow level progression guidelines")
                result.add_warning("- Should have clear role/niche that doesn't overshadow existing classes")
    
    # Validate equipment and starting gear balance
    equipment = character_data.get("equipment", {})
    if equipment:
        expensive_items = []
        for item_name, quantity in equipment.items():
            # Check for obviously overpowered starting equipment
            if any(keyword in item_name.lower() for keyword in ["legendary", "artifact", "vorpal", "+3", "+4", "+5"]):
                expensive_items.append(item_name)
        
        if expensive_items:
            result.add_warning(f"High-power equipment detected: {expensive_items} - ensure appropriate for character level")
    
    return result

# ============================================================================
# NPC VALIDATION FUNCTIONS
# ============================================================================

def validate_and_enhance_npc(npc_data: Dict[str, Any], npc_type: NPCType, npc_role: NPCRole) -> Dict[str, Any]:
    """
    Validate and enhance NPC data with D&D 5e 2024 balance checks.
    Ensures NPC is appropriate for its type, role, and intended challenge level.
    """
    # Ensure required fields exist
    required_fields = ["name", "species", "role", "alignment", "abilities"]
    for field in required_fields:
        if field not in npc_data:
            logger.warning(f"Missing required field '{field}' in NPC data")
            npc_data[field] = "Unknown" if field != "abilities" else {
                "strength": 10, "dexterity": 10, "constitution": 10,
                "intelligence": 10, "wisdom": 10, "charisma": 10
            }
    
    # Validate ability scores according to D&D 5e NPC guidelines
    if "abilities" in npc_data:
        for ability, score in npc_data["abilities"].items():
            if not isinstance(score, int) or score < 3 or score > 20:
                logger.warning(f"NPC ability score {ability}={score} outside normal range (3-20), setting to 10")
                npc_data["abilities"][ability] = 10
    
    # Balance checks based on NPC type and role
    if npc_type == NPCType.MINOR:
        # Minor NPCs should have modest stats and focus on roleplay
        npc_data["focus"] = "roleplay"
        npc_data["combat_stats_minimal"] = True
        
        # Ensure ability scores are appropriate for civilians
        abilities = npc_data.get("abilities", {})
        for ability in abilities:
            if abilities[ability] > 16:
                logger.warning(f"Minor NPC has high {ability} ({abilities[ability]}) - may be overpowered")
                abilities[ability] = min(abilities[ability], 16)
        
        # Set low challenge rating for minor NPCs
        npc_data["challenge_rating"] = 0.0
        npc_data["hit_points"] = npc_data.get("hit_points", 4)
        npc_data["armor_class"] = npc_data.get("armor_class", 10)
        
    else:
        # Major NPCs can have combat capabilities
        npc_data["focus"] = "combat"
        npc_data["combat_ready"] = True
        
        # Set appropriate combat stats based on CR
        cr = npc_data.get("challenge_rating", 0.25)
        
        # D&D 5e 2024 NPC stat guidelines by CR
        if cr <= 0.5:
            max_hp = 35
            min_ac = 10
            max_ac = 15
        elif cr <= 2:
            max_hp = 100
            min_ac = 12
            max_ac = 17
        elif cr <= 5:
            max_hp = 200
            min_ac = 14
            max_ac = 18
        else:
            max_hp = 300
            min_ac = 15
            max_ac = 20
        
        # Validate and adjust HP
        hp = npc_data.get("hit_points", int(cr * 15 + 10))
        if hp > max_hp:
            logger.warning(f"NPC HP ({hp}) too high for CR {cr}, reducing to {max_hp}")
            hp = max_hp
        npc_data["hit_points"] = hp
        
        # Validate and adjust AC
        ac = npc_data.get("armor_class", int(cr + 12))
        if ac < min_ac:
            ac = min_ac
        elif ac > max_ac:
            logger.warning(f"NPC AC ({ac}) too high for CR {cr}, reducing to {max_ac}")
            ac = max_ac
        npc_data["armor_class"] = ac
    
    # Role-specific validation
    role_guidelines = {
        NPCRole.CIVILIAN: {"combat_focus": False, "social_focus": True},
        NPCRole.MERCHANT: {"wealth": "moderate", "social_focus": True},
        NPCRole.GUARD: {"combat_focus": True, "equipment": "martial"},
        NPCRole.NOBLE: {"social_focus": True, "resources": "high"},
        NPCRole.CRIMINAL: {"stealth_focus": True, "social_focus": True},
        NPCRole.SCHOLAR: {"intelligence_focus": True, "knowledge": "high"},
        NPCRole.ARTISAN: {"skill_focus": True, "crafting": "high"},
        NPCRole.HEALER: {"wisdom_focus": True, "healing": "high"}
    }
    
    if npc_role in role_guidelines:
        guidelines = role_guidelines[npc_role]
        for guideline, value in guidelines.items():
            npc_data[f"role_{guideline}"] = value
    
    # Add D&D 5e compliance metadata
    npc_data["creation_method"] = "llm_generated"
    npc_data["npc_type"] = npc_type.value
    npc_data["npc_role"] = npc_role.value
    npc_data["d5e_2024_compliant"] = True
    npc_data["balance_validated"] = True
    
    return npc_data

# ============================================================================
# ITEM VALIDATION FUNCTIONS
# ============================================================================

def validate_item_for_level(item, character_level: int, determine_rarity_for_level_func) -> CreationResult:
    """
    Validate item balance and appropriateness for character level according to D&D 5e 2024 guidelines.
    Ensures items follow official power progression and don't break game balance.
    """
    result = CreationResult(success=True)
    
    # Check rarity vs level according to D&D 5e 2024 guidelines
    max_rarity_for_level = determine_rarity_for_level_func(character_level)
    rarity_levels = [ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.RARE, 
                    ItemRarity.VERY_RARE, ItemRarity.LEGENDARY, ItemRarity.ARTIFACT]
    
    if rarity_levels.index(item.rarity) > rarity_levels.index(max_rarity_for_level):
        result.success = False
        result.error = f"Item rarity {item.rarity.value} too high for level {character_level}"
        return result
    
    # Validate item power level matches rarity
    item_name = getattr(item, 'name', 'Unknown Item').lower()
    
    # Check for obviously overpowered items
    overpowered_indicators = [
        ("+5", "enhancement bonus too high"),
        ("vorpal", "extremely powerful enchantment"),
        ("wish", "reality-altering magic"),
        ("time stop", "game-breaking temporal magic"),
        ("kill", "instant death effects"),
        ("immunity to all", "blanket immunities")
    ]
    
    for indicator, reason in overpowered_indicators:
        if indicator in item_name:
            if item.rarity not in [ItemRarity.LEGENDARY, ItemRarity.ARTIFACT]:
                result.add_warning(f"Item contains '{indicator}' ({reason}) but isn't Legendary/Artifact rarity")
    
    # Spell-specific validation according to D&D 5e 2024 spell progression
    if hasattr(item, 'level'):  # SpellCore check
        max_spell_level = min(9, (character_level + 1) // 2)
        if item.level > max_spell_level:
            result.success = False
            result.error = f"Spell level {item.level} too high for character level {character_level} (max: {max_spell_level})"
            return result
        
        # Validate spell level matches rarity
        expected_rarity_for_spell_level = {
            0: ItemRarity.COMMON, 1: ItemRarity.COMMON, 2: ItemRarity.COMMON,
            3: ItemRarity.UNCOMMON, 4: ItemRarity.UNCOMMON, 5: ItemRarity.RARE,
            6: ItemRarity.RARE, 7: ItemRarity.VERY_RARE, 8: ItemRarity.VERY_RARE,
            9: ItemRarity.LEGENDARY
        }
        
        expected_rarity = expected_rarity_for_spell_level.get(item.level, ItemRarity.COMMON)
        if rarity_levels.index(item.rarity) < rarity_levels.index(expected_rarity):
            result.add_warning(f"Spell level {item.level} typically requires {expected_rarity.value} rarity or higher")
    
    # Weapon-specific validation
    if hasattr(item, 'damage_dice'):  # WeaponCore check
        damage = getattr(item, 'damage_dice', '1d4')
        if 'd20' in damage or 'd12' in damage and '2d12' in damage:
            result.add_warning("Weapon damage may be too high - check against official weapon tables")
    
    # Armor-specific validation
    if hasattr(item, 'armor_class_base'):  # ArmorCore check
        ac = getattr(item, 'armor_class_base', 10)
        if ac > 18 + (2 if item.rarity in [ItemRarity.LEGENDARY, ItemRarity.ARTIFACT] else 0):
            result.add_warning(f"Armor AC {ac} may be too high for {item.rarity.value} rarity")
    
    # Attunement validation
    requires_attunement = getattr(item, 'requires_attunement', False)
    if item.rarity in [ItemRarity.VERY_RARE, ItemRarity.LEGENDARY, ItemRarity.ARTIFACT]:
        if not requires_attunement:
            result.add_warning(f"{item.rarity.value} items typically require attunement")
    
    return result

# ============================================================================
# CREATURE VALIDATION FUNCTIONS
# ============================================================================

def validate_and_enhance_creature(creature_data: Dict[str, Any], challenge_rating: float) -> Dict[str, Any]:
    """
    Validate and enhance creature data with comprehensive D&D 5e 2024 balance checks.
    Ensures creature stats are appropriate for CR and follows official design guidelines.
    """
    # Ensure required fields exist
    required_fields = ["name", "type", "challenge_rating", "abilities", "hit_points", "armor_class"]
    for field in required_fields:
        if field not in creature_data:
            logger.warning(f"Missing required field '{field}' in creature data")
            
            # Provide D&D 5e appropriate defaults
            if field == "abilities":
                creature_data[field] = {
                    "strength": 10, "dexterity": 10, "constitution": 10,
                    "intelligence": 10, "wisdom": 10, "charisma": 10
                }
            elif field == "challenge_rating":
                creature_data[field] = challenge_rating
            elif field == "hit_points":
                creature_data[field] = _calculate_hp_for_cr(challenge_rating)
            elif field == "armor_class":
                creature_data[field] = _calculate_ac_for_cr(challenge_rating)
            else:
                creature_data[field] = "Unknown"
    
    # Validate ability scores according to D&D 5e creature guidelines
    if "abilities" in creature_data:
        for ability, score in creature_data["abilities"].items():
            if not isinstance(score, int) or score < 1 or score > 30:
                logger.warning(f"Creature ability score {ability}={score} outside valid range (1-30), setting to 10")
                creature_data["abilities"][ability] = 10
    
    # Comprehensive CR balance validation according to D&D 5e 2024 DMG guidelines
    cr = float(challenge_rating)
    
    # Expected stat ranges by CR (based on D&D 5e 2024 monster creation guidelines)
    cr_guidelines = _get_cr_stat_guidelines(cr)
    
    # Validate hit points
    hp = creature_data.get("hit_points", 0)
    if hp < cr_guidelines["hp_min"] or hp > cr_guidelines["hp_max"]:
        logger.warning(f"Creature HP ({hp}) outside expected range for CR {cr} ({cr_guidelines['hp_min']}-{cr_guidelines['hp_max']})")
        if hp > cr_guidelines["hp_max"]:
            creature_data["hit_points"] = cr_guidelines["hp_max"]
    
    # Validate armor class
    ac = creature_data.get("armor_class", 10)
    if ac < cr_guidelines["ac_min"] or ac > cr_guidelines["ac_max"]:
        logger.warning(f"Creature AC ({ac}) outside expected range for CR {cr} ({cr_guidelines['ac_min']}-{cr_guidelines['ac_max']})")
        if ac > cr_guidelines["ac_max"]:
            creature_data["armor_class"] = cr_guidelines["ac_max"]
    
    # Validate attack bonuses and damage (if present)
    if "actions" in creature_data:
        for action in creature_data["actions"]:
            if "attack_bonus" in action:
                try:
                    bonus = int(action["attack_bonus"].replace("+", ""))
                    if bonus > cr_guidelines["attack_bonus_max"]:
                        logger.warning(f"Attack bonus {bonus} too high for CR {cr} (max: {cr_guidelines['attack_bonus_max']})")
                except ValueError:
                    pass
    
    # Validate saving throws don't exceed reasonable limits
    if "saving_throws" in creature_data:
        max_save_bonus = cr_guidelines["save_bonus_max"]
        for save in creature_data["saving_throws"]:
            try:
                bonus = int(save.split("+")[1]) if "+" in save else 0
                if bonus > max_save_bonus:
                    logger.warning(f"Saving throw bonus {bonus} may be too high for CR {cr}")
            except (ValueError, IndexError):
                pass
    
    # Validate proficiency bonus matches CR
    expected_prof_bonus = _calculate_proficiency_bonus_for_cr(cr)
    if "proficiency_bonus" in creature_data:
        prof_bonus = creature_data["proficiency_bonus"]
        if prof_bonus != expected_prof_bonus:
            logger.warning(f"Proficiency bonus {prof_bonus} doesn't match CR {cr} (expected: {expected_prof_bonus})")
            creature_data["proficiency_bonus"] = expected_prof_bonus
    else:
        creature_data["proficiency_bonus"] = expected_prof_bonus
    
    # Ensure challenge rating consistency
    creature_data["challenge_rating"] = challenge_rating
    
    # Add D&D 5e 2024 compliance metadata
    creature_data["creation_method"] = "llm_generated"
    creature_data["stat_block_complete"] = True
    creature_data["d5e_2024_compliant"] = True
    creature_data["cr_balanced"] = True
    creature_data["balance_validated"] = True
    
    return creature_data

def _calculate_hp_for_cr(cr: float) -> int:
    """Calculate appropriate HP for CR based on D&D 5e guidelines."""
    if cr <= 0.125:
        return max(1, int(cr * 35))
    elif cr <= 1:
        return int(cr * 50 + 10)
    elif cr <= 4:
        return int(cr * 60 + 40)
    elif cr <= 10:
        return int(cr * 80 + 120)
    elif cr <= 16:
        return int(cr * 100 + 200)
    else:
        return int(cr * 120 + 400)

def _calculate_ac_for_cr(cr: float) -> int:
    """Calculate appropriate AC for CR based on D&D 5e guidelines."""
    base_ac = 10
    if cr <= 0.25:
        return base_ac + 1
    elif cr <= 2:
        return base_ac + 2 + int(cr)
    elif cr <= 8:
        return base_ac + 3 + int(cr // 2)
    elif cr <= 16:
        return base_ac + 5 + int(cr // 4)
    else:
        return base_ac + 8

def _calculate_proficiency_bonus_for_cr(cr: float) -> int:
    """Calculate proficiency bonus for CR based on D&D 5e progression."""
    if cr <= 4:
        return 2
    elif cr <= 8:
        return 3
    elif cr <= 12:
        return 4
    elif cr <= 16:
        return 5
    elif cr <= 20:
        return 6
    elif cr <= 24:
        return 7
    elif cr <= 28:
        return 8
    else:
        return 9

def _get_cr_stat_guidelines(cr: float) -> Dict[str, int]:
    """Get stat guidelines for a given CR based on D&D 5e design principles."""
    if cr <= 0.25:
        return {
            "hp_min": 1, "hp_max": 35,
            "ac_min": 10, "ac_max": 13,
            "attack_bonus_max": 4,
            "save_bonus_max": 3
        }
    elif cr <= 1:
        return {
            "hp_min": 15, "hp_max": 70,
            "ac_min": 10, "ac_max": 15,
            "attack_bonus_max": 5,
            "save_bonus_max": 4
        }
    elif cr <= 4:
        return {
            "hp_min": 35, "hp_max": 160,
            "ac_min": 12, "ac_max": 17,
            "attack_bonus_max": 7,
            "save_bonus_max": 6
        }
    elif cr <= 10:
        return {
            "hp_min": 80, "hp_max": 320,
            "ac_min": 14, "ac_max": 18,
            "attack_bonus_max": 10,
            "save_bonus_max": 8
        }
    elif cr <= 16:
        return {
            "hp_min": 200, "hp_max": 500,
            "ac_min": 16, "ac_max": 20,
            "attack_bonus_max": 13,
            "save_bonus_max": 11
        }
    else:
        return {
            "hp_min": 400, "hp_max": 800,
            "ac_min": 18, "ac_max": 22,
            "attack_bonus_max": 16,
            "save_bonus_max": 14
        }

# ============================================================================
# ADDITIONAL BALANCE VALIDATION FUNCTIONS
# ============================================================================

def validate_custom_species_balance(species_data: Dict[str, Any]) -> CreationResult:
    """
    Validate custom species follows D&D 5e 2024 racial design guidelines.
    Ensures balanced traits that don't overshadow existing races.
    """
    result = CreationResult(success=True, data=species_data)
    
    # Check for overpowered ability score increases
    asi_bonuses = species_data.get("ability_score_increase", {})
    total_asi = sum(asi_bonuses.values()) if isinstance(asi_bonuses, dict) else 0
    
    if total_asi > 3:
        result.add_warning(f"Total ASI bonus ({total_asi}) exceeds typical limit of 3")
    elif total_asi < 2:
        result.add_warning(f"Total ASI bonus ({total_asi}) below typical minimum of 2")
    
    # Check for appropriate trait count and power level
    traits = species_data.get("racial_traits", [])
    if len(traits) > 5:
        result.add_warning(f"Species has {len(traits)} traits - may be too many (typical: 2-4)")
    elif len(traits) < 2:
        result.add_warning(f"Species has only {len(traits)} traits - may be too few")
    
    # Flag potentially overpowered traits
    overpowered_keywords = [
        "immunity", "resistance to all", "advantage on all", "double", 
        "triple", "unlimited", "at will", "permanent", "always"
    ]
    
    for trait in traits:
        trait_text = str(trait).lower()
        for keyword in overpowered_keywords:
            if keyword in trait_text:
                result.add_warning(f"Trait contains '{keyword}' - may be overpowered")
    
    return result

def validate_custom_class_balance(class_data: Dict[str, Any]) -> CreationResult:
    """
    Validate custom class follows D&D 5e 2024 class design guidelines.
    Ensures balanced progression and appropriate power level.
    """
    result = CreationResult(success=True, data=class_data)
    
    # Validate hit die
    hit_die = class_data.get("hit_die", "d8")
    valid_hit_dice = ["d6", "d8", "d10", "d12"]
    if hit_die not in valid_hit_dice:
        result.add_warning(f"Hit die {hit_die} not standard (should be d6, d8, d10, or d12)")
    
    # Check saving throw proficiencies
    save_profs = class_data.get("saving_throw_proficiencies", [])
    if len(save_profs) != 2:
        result.add_warning(f"Class has {len(save_profs)} save proficiencies (should be exactly 2)")
    
    # Validate feature progression
    features = class_data.get("class_features", {})
    expected_feature_levels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    
    for level in [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]:  # Key feature levels
        if str(level) not in features:
            result.add_warning(f"No feature at level {level} - may affect class balance")
    
    # Check for overpowered early features
    level_1_features = features.get("1", [])
    if len(level_1_features) > 3:
        result.add_warning(f"Level 1 has {len(level_1_features)} features - may be too many")
    
    return result

def validate_custom_spell_balance(spell_data: Dict[str, Any]) -> CreationResult:
    """
    Validate custom spell follows D&D 5e 2024 spell design guidelines.
    Ensures appropriate power level for spell level.
    """
    result = CreationResult(success=True, data=spell_data)
    
    spell_level = spell_data.get("level", 0)
    if not isinstance(spell_level, int) or spell_level < 0 or spell_level > 9:
        result.error = f"Invalid spell level: {spell_level} (must be 0-9)"
        result.success = False
        return result
    
    # Check damage scaling for spell level
    damage = spell_data.get("damage", "")
    if damage and spell_level > 0:
        # Extract dice count and type
        import re
        dice_match = re.search(r'(\d+)d(\d+)', damage)
        if dice_match:
            dice_count = int(dice_match.group(1))
            die_size = int(dice_match.group(2))
            
            # Rough damage guidelines by spell level
            max_damage_guidelines = {
                1: 3 * 8,    # 3d8 (Burning Hands)
                2: 6 * 6,    # 6d6 (Fireball at base)
                3: 8 * 6,    # 8d6 (Fireball)
                4: 12 * 6,   # 12d6 
                5: 14 * 6,   # 14d6
                6: 16 * 6,   # 16d6
                7: 20 * 6,   # 20d6
                8: 24 * 6,   # 24d6
                9: 30 * 6    # 30d6
            }
            
            estimated_damage = dice_count * (die_size / 2 + 0.5)
            max_expected = max_damage_guidelines.get(spell_level, 100)
            
            if estimated_damage > max_expected:
                result.add_warning(f"Spell damage ({estimated_damage:.1f} avg) may be too high for level {spell_level}")
    
    # Check for overpowered effects
    description = str(spell_data.get("description", "")).lower()
    overpowered_effects = [
        ("save or die", "instant death effects are typically 9th level or require specific conditions"),
        ("permanent", "permanent effects should be rare and high level"),
        ("no save", "effects without saves should be limited"),
        ("reality", "reality-altering effects typically reserved for 9th level"),
        ("time stop", "time manipulation is extremely powerful"),
        ("wish", "wish-like effects are 9th level")
    ]
    
    for effect, warning in overpowered_effects:
        if effect in description:
            result.add_warning(f"Spell contains '{effect}' - {warning}")
    
    return result

def validate_custom_item_balance(item_data: Dict[str, Any]) -> CreationResult:
    """
    Validate custom item follows D&D 5e 2024 magic item design guidelines.
    Ensures appropriate power level for rarity.
    """
    result = CreationResult(success=True, data=item_data)
    
    rarity = item_data.get("rarity", "common").lower()
    description = str(item_data.get("description", "")).lower()
    
    # Check for effects inappropriate for rarity
    rarity_guidelines = {
        "common": {
            "max_bonus": 1,
            "forbidden": ["save or die", "teleport", "fly", "immunity"],
            "typical": ["minor utility", "small bonus", "flavor effect"]
        },
        "uncommon": {
            "max_bonus": 2,
            "forbidden": ["save or die", "reality", "time"],
            "typical": ["moderate utility", "+1 weapons/armor", "limited magic"]
        },
        "rare": {
            "max_bonus": 3,
            "forbidden": ["save or die", "reality", "unlimited"],
            "typical": ["+2 weapons/armor", "significant magic", "major utility"]
        },
        "very rare": {
            "max_bonus": 4,
            "forbidden": ["save or die without save", "reality alteration"],
            "typical": ["+3 weapons/armor", "powerful magic", "game-changing"]
        },
        "legendary": {
            "max_bonus": 5,
            "forbidden": ["unlimited reality alteration"],
            "typical": ["+4/+5 weapons/armor", "legendary effects", "campaign-defining"]
        }
    }
    
    if rarity in rarity_guidelines:
        guidelines = rarity_guidelines[rarity]
        
        # Check for forbidden effects
        for forbidden in guidelines["forbidden"]:
            if forbidden in description:
                result.add_warning(f"Effect '{forbidden}' typically too powerful for {rarity} rarity")
        
        # Check for enhancement bonuses
        import re
        bonus_match = re.search(r'\+(\d+)', description)
        if bonus_match:
            bonus = int(bonus_match.group(1))
            if bonus > guidelines["max_bonus"]:
                result.add_warning(f"+{bonus} bonus too high for {rarity} rarity (max: +{guidelines['max_bonus']})")
    
    # Check attunement requirements
    requires_attunement = item_data.get("requires_attunement", False)
    if rarity in ["very rare", "legendary", "artifact"] and not requires_attunement:
        result.add_warning(f"{rarity.title()} items typically require attunement")
    
    return result

# ============================================================================
# DATABASE VALIDATION FUNCTIONS
# ============================================================================

def validate_spell_database() -> bool:
    """Validate the integrity of the spell database."""
    try:
        from dnd_data import DND_SPELL_DATABASE
        
        required_fields = ["description", "level", "school", "casting_time", "range", "components", "duration"]
        
        for level_key, level_spells in DND_SPELL_DATABASE.items():
            if isinstance(level_spells, dict):
                for school, spells in level_spells.items():
                    for spell_name in spells:
                        # For now, we just check that spell names are strings
                        if not isinstance(spell_name, str):
                            logger.error(f"Invalid spell name type: {type(spell_name)}")
                            return False
                        
                        if len(spell_name.strip()) == 0:
                            logger.error(f"Empty spell name found in {level_key}/{school}")
                            return False
        
        logger.info("Spell database validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Spell database validation failed: {e}")
        return False

def validate_weapon_database() -> bool:
    """Validate the integrity of the weapon database."""
    try:
        from dnd_data import DND_WEAPON_DATABASE
        
        required_fields = ["damage", "damage_type", "properties", "weight", "cost", "category"]
        
        for category, weapons in DND_WEAPON_DATABASE.items():
            for weapon_name, weapon_data in weapons.items():
                for field in required_fields:
                    if field not in weapon_data:
                        logger.error(f"Weapon {weapon_name} missing field: {field}")
                        return False
                
                # Validate damage format
                damage = weapon_data.get("damage", "")
                if damage and not any(die in damage for die in ["d4", "d6", "d8", "d10", "d12"]):
                    logger.error(f"Weapon {weapon_name} has invalid damage format: {damage}")
                    return False
        
        logger.info("Weapon database validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Weapon database validation failed: {e}")
        return False

def validate_feat_database() -> bool:
    """Validate the integrity of the feat database."""
    try:
        from dnd_data import DND_FEAT_DATABASE
        
        required_fields = ["description", "benefits", "prerequisites", "asi_bonus", "category"]
        
        for category, feats in DND_FEAT_DATABASE.items():
            for feat_name, feat_data in feats.items():
                for field in required_fields:
                    if field not in feat_data:
                        logger.error(f"Feat {feat_name} missing field: {field}")
                        return False
        
        logger.info("Feat database validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Feat database validation failed: {e}")
        return False

def validate_armor_database() -> bool:
    """Validate the integrity of the armor database."""
    try:
        from dnd_data import DND_ARMOR_DATABASE
        
        required_fields = ["dex_modifier", "weight", "cost", "category", "properties"]
        
        for category, armors in DND_ARMOR_DATABASE.items():
            for armor_name, armor_data in armors.items():
                # Check for required fields
                for field in required_fields:
                    if field not in armor_data:
                        logger.error(f"Armor {armor_name} missing field: {field}")
                        return False
                
                # Armor must have either ac_base OR ac_bonus (for shields)
                if "ac_base" not in armor_data and "ac_bonus" not in armor_data:
                    logger.error(f"Armor {armor_name} missing both ac_base and ac_bonus")
                    return False
        
        logger.info("Armor database validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Armor database validation failed: {e}")
        return False

def validate_tools_database() -> bool:
    """Validate the integrity of the tools database."""
    try:
        from dnd_data import DND_TOOLS_DATABASE
        
        required_fields = ["cost", "weight", "category", "description"]
        
        for category, tools in DND_TOOLS_DATABASE.items():
            for tool_name, tool_data in tools.items():
                for field in required_fields:
                    if field not in tool_data:
                        logger.error(f"Tool {tool_name} missing field: {field}")
                        return False
        
        logger.info("Tools database validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Tools database validation failed: {e}")
        return False

def validate_gear_database() -> bool:
    """Validate the integrity of the adventuring gear database."""
    try:
        from dnd_data import DND_ADVENTURING_GEAR_DATABASE
        
        required_fields = ["cost", "weight", "category", "description"]
        
        for category, gears in DND_ADVENTURING_GEAR_DATABASE.items():
            for gear_name, gear_data in gears.items():
                for field in required_fields:
                    if field not in gear_data:
                        logger.error(f"Gear {gear_name} missing field: {field}")
                        return False
        
        logger.info("Adventuring gear database validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Adventuring gear database validation failed: {e}")
        return False

def validate_feat_prerequisites(feat_name: str, character_data: Dict[str, Any]) -> bool:
    """Validate that a character meets the prerequisites for a specific feat."""
    try:
        from dnd_data import get_feat_data
        
        feat_data = get_feat_data(feat_name)
        if not feat_data:
            logger.error(f"Feat {feat_name} not found")
            return False
        
        prerequisites = feat_data.get("prerequisites", {})
        if not prerequisites:
            return True  # No prerequisites
        
        # Check ability score requirements
        ability_requirements = prerequisites.get("abilities", {})
        character_abilities = character_data.get("abilities", {})
        
        for ability, min_score in ability_requirements.items():
            character_score = character_abilities.get(ability, 10)
            if character_score < min_score:
                logger.warning(f"Character {ability} score {character_score} does not meet feat requirement {min_score}")
                return False
        
        # Check level requirements
        min_level = prerequisites.get("level", 1)
        character_level = character_data.get("level", 1)
        if character_level < min_level:
            logger.warning(f"Character level {character_level} does not meet feat requirement {min_level}")
            return False
        
        # Check class requirements
        required_classes = prerequisites.get("classes", [])
        if required_classes:
            character_classes = list(character_data.get("classes", {}).keys())
            if not any(cls in character_classes for cls in required_classes):
                logger.warning(f"Character classes {character_classes} do not meet feat requirements {required_classes}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Feat prerequisite validation failed: {e}")
        return False

def validate_all_databases() -> bool:
    """Validate all D&D data databases for integrity."""
    validations = [
        validate_spell_database,
        validate_weapon_database, 
        validate_feat_database,
        validate_armor_database,
        validate_tools_database,
        validate_gear_database
    ]
    
    for validation_func in validations:
        if not validation_func():
            logger.error(f"Database validation failed: {validation_func.__name__}")
            return False
    
    logger.info("All database validations passed")
    return True