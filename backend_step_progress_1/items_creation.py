"""
D&D 5e 2024 Item Creation Module - Refactored

This module provides item creation workflow using shared components
to eliminate code duplication. It handles the complete item creation
process including validation, generation, and level-appropriate content.

Key goals:
- Ensure items are consistent with character concepts
- Ensure items are appropriate for character level
- Generate weapons, armor, spells, and magic items
- Integrate with custom content models

Uses shared_character_generation.py for all common logic.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Import shared components to eliminate duplication
from shared_character_generation import (
    CreationConfig, CreationResult, CharacterDataGenerator, 
    CharacterValidator, create_specialized_prompt
)

# Import core D&D components
from core_models import AbilityScore, MagicItemManager, ProficiencyLevel
from character_models import DnDCondition
from llm_service import create_llm_service, LLMService
from database_models import CustomContent
from custom_content_models import ContentRegistry
from generators import CustomContentGenerator

logger = logging.getLogger(__name__)

# ============================================================================
# ITEM-SPECIFIC DEFINITIONS
# ============================================================================

class ItemType(Enum):
    """Types of items that can be created."""
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    SPELL = "spell"
    MAGIC_ITEM = "magic_item"
    POTION = "potion"
    SCROLL = "scroll"
    TOOL = "tool"
    ADVENTURING_GEAR = "adventuring_gear"

class ItemRarity(Enum):
    """D&D 5e item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"

class WeaponCategory(Enum):
    """D&D 5e weapon categories."""
    SIMPLE_MELEE = "simple_melee"
    SIMPLE_RANGED = "simple_ranged"
    MARTIAL_MELEE = "martial_melee"
    MARTIAL_RANGED = "martial_ranged"

class ArmorCategory(Enum):
    """D&D 5e armor categories."""
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    SHIELD = "shield"

# ============================================================================
# ITEM CORE CLASSES
# ============================================================================

@dataclass
class ItemCore:
    """Base class for all D&D items."""
    name: str
    item_type: ItemType
    description: str
    rarity: ItemRarity = ItemRarity.COMMON
    requires_attunement: bool = False
    weight: float = 0.0
    value: int = 0  # in copper pieces
    properties: List[str] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = []

@dataclass
class WeaponCore(ItemCore):
    """D&D weapon implementation."""
    category: WeaponCategory = WeaponCategory.SIMPLE_MELEE
    damage_dice: str = "1d4"
    damage_type: str = "bludgeoning"
    weapon_range: str = "5 feet"  # melee range or ranged distance
    
    def __post_init__(self):
        super().__post_init__()
        self.item_type = ItemType.WEAPON

@dataclass
class ArmorCore(ItemCore):
    """D&D armor implementation."""
    category: ArmorCategory = ArmorCategory.LIGHT
    armor_class_base: int = 10
    dex_bonus_limit: Optional[int] = None  # None means no limit
    strength_requirement: int = 0
    stealth_disadvantage: bool = False
    
    def __post_init__(self):
        super().__post_init__()
        self.item_type = ItemType.ARMOR

@dataclass
class SpellCore(ItemCore):
    """D&D spell implementation."""
    level: int = 0  # 0 for cantrips
    school: str = "abjuration"
    casting_time: str = "1 action"
    spell_range: str = "self"
    components: List[str] = None
    duration: str = "instantaneous"
    classes: List[str] = None  # Which classes can cast this spell
    
    def __post_init__(self):
        super().__post_init__()
        self.item_type = ItemType.SPELL
        if self.components is None:
            self.components = ["V", "S"]
        if self.classes is None:
            self.classes = ["Wizard"]

# ============================================================================
# ITEM CREATOR CLASS
# ============================================================================

class ItemCreator:
    """
    D&D 5e 2024 Item Creation Service with LLM Integration.
    Creates level-appropriate items that fit character concepts.
    Uses shared components to eliminate code duplication.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None, 
                 config: Optional[CreationConfig] = None):
        self.llm_service = llm_service or create_llm_service()
        self.config = config or CreationConfig()
        
        # Initialize shared components
        self.validator = CharacterValidator()
        self.data_generator = CharacterDataGenerator(self.llm_service, self.config)
        self.content_registry = ContentRegistry()
        self.content_generator = CustomContentGenerator(self.llm_service, self.content_registry)
        self.magic_item_manager = MagicItemManager()
        
        logger.info("ItemCreator initialized with shared components")
    
    async def create_item(self, description: str, item_type: ItemType, 
                   character_level: int = 1, character_concept: str = "",
                   rarity: Optional[ItemRarity] = None) -> CreationResult:
        """
        Create an item that fits the character concept and level.
        
        Args:
            description: Description of the desired item
            item_type: Type of item to create
            character_level: Level of the character (affects item power)
            character_concept: Brief description of the character concept
            rarity: Desired rarity (auto-determined if None)
            
        Returns:
            CreationResult with item data
        """
        start_time = time.time()
        
        try:
            logger.info(f"Creating {item_type.value}: {description}")
            
            # Determine appropriate rarity for level
            if rarity is None:
                rarity = self._determine_rarity_for_level(character_level)
            
            # Create item-specific prompt
            item_prompt = self._create_item_prompt(
                description, item_type, character_level, character_concept, rarity
            )
            
            # Use shared data generator with item preferences
            item_preferences = {
                "content_type": "item",
                "item_type": item_type.value,
                "character_level": character_level,
                "rarity": rarity.value,
                "character_concept": character_concept
            }
            
            result = await self.data_generator.generate_character_data(item_prompt, item_preferences)
            
            if result.success:
                # Build item from generated data
                item_core = self._build_item_from_data(result.data, item_type, rarity)
                
                # Validate item is appropriate for level
                validation_result = self._validate_item_for_level(item_core, character_level)
                if not validation_result.success:
                    result.add_warning(f"Item validation warning: {validation_result.error}")
                
                # Update result with item data
                result.data = {
                    "item_core": item_core,
                    "item_stats": self._get_item_stats(item_core),
                    "raw_data": result.data
                }
                
                result.creation_time = time.time() - start_time
                logger.info(f"Item creation completed in {result.creation_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Item creation failed: {str(e)}")
            result = CreationResult()
            result.error = f"Item creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    def create_item_set(self, character_data: Dict[str, Any]) -> CreationResult:
        """Create a complete set of items for a character."""
        start_time = time.time()
        items = {}
        warnings = []
        
        try:
            character_level = character_data.get("level", 1)
            character_concept = self._extract_character_concept(character_data)
            
            # Create weapons
            if self._needs_weapons(character_data):
                weapon_result = self.create_item(
                    f"Primary weapon for {character_concept}",
                    ItemType.WEAPON,
                    character_level,
                    character_concept
                )
                if weapon_result.success:
                    items["primary_weapon"] = weapon_result.data
                else:
                    warnings.append(f"Failed to create weapon: {weapon_result.error}")
            
            # Create armor
            if self._needs_armor(character_data):
                armor_result = self.create_item(
                    f"Armor for {character_concept}",
                    ItemType.ARMOR,
                    character_level,
                    character_concept
                )
                if armor_result.success:
                    items["armor"] = armor_result.data
                else:
                    warnings.append(f"Failed to create armor: {armor_result.error}")
            
            # Create spells if spellcaster
            if self._is_spellcaster(character_data):
                spell_result = self.create_item(
                    f"Signature spell for {character_concept}",
                    ItemType.SPELL,
                    character_level,
                    character_concept
                )
                if spell_result.success:
                    items["signature_spell"] = spell_result.data
                else:
                    warnings.append(f"Failed to create spell: {spell_result.error}")
            
            # Create magic item for higher levels
            if character_level >= 5:
                magic_item_result = self.create_item(
                    f"Magic item for {character_concept}",
                    ItemType.MAGIC_ITEM,
                    character_level,
                    character_concept
                )
                if magic_item_result.success:
                    items["magic_item"] = magic_item_result.data
                else:
                    warnings.append(f"Failed to create magic item: {magic_item_result.error}")
            
            result = CreationResult(success=True, data={"items": items})
            result.warnings = warnings
            result.creation_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Item set creation failed: {str(e)}")
            result = CreationResult()
            result.error = f"Item set creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    def _determine_rarity_for_level(self, level: int) -> ItemRarity:
        """Determine appropriate item rarity for character level."""
        if level <= 4:
            return ItemRarity.COMMON
        elif level <= 8:
            return ItemRarity.UNCOMMON
        elif level <= 12:
            return ItemRarity.RARE
        elif level <= 16:
            return ItemRarity.VERY_RARE
        else:
            return ItemRarity.LEGENDARY
    
    def _create_item_prompt(self, description: str, item_type: ItemType,
                           character_level: int, character_concept: str,
                           rarity: ItemRarity) -> str:
        """Create item-specific prompt for generation."""
        prompt_parts = [
            f"Create a D&D 5e 2024 {item_type.value}: {description}",
            f"Character Level: {character_level}",
            f"Character Concept: {character_concept}",
            f"Item Rarity: {rarity.value}",
        ]
        
        # Add item-type specific guidance
        if item_type == ItemType.WEAPON:
            prompt_parts.extend([
                "Include:",
                "- Appropriate damage dice for level and rarity",
                "- Weapon properties (finesse, versatile, etc.)",
                "- Special abilities if magical",
                "- Weight and value"
            ])
        elif item_type == ItemType.ARMOR:
            prompt_parts.extend([
                "Include:",
                "- Appropriate AC for armor type",
                "- Strength requirements if heavy armor",
                "- Special properties if magical",
                "- Weight and value"
            ])
        elif item_type == ItemType.SPELL:
            prompt_parts.extend([
                "Include:",
                "- Appropriate spell level for character level",
                "- School of magic",
                "- Casting time, range, duration",
                "- Components (V, S, M)",
                "- Spell description and effects"
            ])
        elif item_type == ItemType.MAGIC_ITEM:
            prompt_parts.extend([
                "Include:",
                "- Appropriate power level for character level",
                "- Attunement requirement if needed",
                "- Charges or uses per day if applicable",
                "- Activation method"
            ])
        
        prompt_parts.extend([
            f"Ensure the item fits the character concept: {character_concept}",
            "Follow D&D 5e 2024 item format and balance guidelines."
        ])
        
        return "\n".join(prompt_parts)
    
    def _build_item_from_data(self, item_data: Dict[str, Any], 
                             item_type: ItemType, rarity: ItemRarity) -> ItemCore:
        """Build ItemCore from generated data."""
        name = item_data.get("name", "Unknown Item")
        description = item_data.get("description", "")
        
        # Create appropriate item type
        if item_type == ItemType.WEAPON:
            item = WeaponCore(
                name=name,
                item_type=ItemType.WEAPON,
                description=description,
                rarity=rarity,
                damage_dice=item_data.get("damage_dice", "1d6"),
                damage_type=item_data.get("damage_type", "slashing"),
                weapon_range=item_data.get("range", "5 feet")
            )
            
            # Set weapon category
            if "category" in item_data:
                try:
                    item.category = WeaponCategory(item_data["category"])
                except ValueError:
                    logger.warning(f"Unknown weapon category: {item_data['category']}")
                    
        elif item_type == ItemType.ARMOR:
            item = ArmorCore(
                name=name,
                item_type=ItemType.ARMOR,
                description=description,
                rarity=rarity,
                armor_class_base=item_data.get("armor_class", 11),
                dex_bonus_limit=item_data.get("dex_bonus_limit"),
                strength_requirement=item_data.get("strength_requirement", 0),
                stealth_disadvantage=item_data.get("stealth_disadvantage", False)
            )
            
            # Set armor category
            if "category" in item_data:
                try:
                    item.category = ArmorCategory(item_data["category"])
                except ValueError:
                    logger.warning(f"Unknown armor category: {item_data['category']}")
                    
        elif item_type == ItemType.SPELL:
            item = SpellCore(
                name=name,
                item_type=ItemType.SPELL,
                description=description,
                rarity=rarity,
                level=item_data.get("level", 1),
                school=item_data.get("school", "evocation"),
                casting_time=item_data.get("casting_time", "1 action"),
                spell_range=item_data.get("range", "60 feet"),
                components=item_data.get("components", ["V", "S"]),
                duration=item_data.get("duration", "instantaneous"),
                classes=item_data.get("classes", ["Wizard"])
            )
        else:
            # Generic item
            item = ItemCore(
                name=name,
                item_type=item_type,
                description=description,
                rarity=rarity
            )
        
        # Set common properties
        item.requires_attunement = item_data.get("requires_attunement", False)
        item.weight = item_data.get("weight", 0.0)
        item.value = item_data.get("value", 0)
        item.properties = item_data.get("properties", [])
        
        return item
    
    def _validate_item_for_level(self, item: ItemCore, character_level: int) -> CreationResult:
        """Validate that item is appropriate for character level."""
        result = CreationResult(success=True)
        
        # Check rarity vs level
        max_rarity_for_level = self._determine_rarity_for_level(character_level)
        rarity_levels = [ItemRarity.COMMON, ItemRarity.UNCOMMON, ItemRarity.RARE, 
                        ItemRarity.VERY_RARE, ItemRarity.LEGENDARY, ItemRarity.ARTIFACT]
        
        if rarity_levels.index(item.rarity) > rarity_levels.index(max_rarity_for_level):
            result.success = False
            result.error = f"Item rarity {item.rarity.value} too high for level {character_level}"
        
        # Spell-specific validation
        if isinstance(item, SpellCore):
            max_spell_level = min(9, (character_level + 1) // 2)
            if item.level > max_spell_level:
                result.success = False
                result.error = f"Spell level {item.level} too high for character level {character_level}"
        
        return result
    
    def _get_item_stats(self, item: ItemCore) -> Dict[str, Any]:
        """Get item statistics for display."""
        stats = {
            "name": item.name,
            "type": item.item_type.value,
            "rarity": item.rarity.value,
            "description": item.description,
            "weight": item.weight,
            "value": item.value,
            "properties": item.properties,
            "requires_attunement": item.requires_attunement
        }
        
        # Add type-specific stats
        if isinstance(item, WeaponCore):
            stats.update({
                "damage_dice": item.damage_dice,
                "damage_type": item.damage_type,
                "range": item.weapon_range,
                "category": item.category.value
            })
        elif isinstance(item, ArmorCore):
            stats.update({
                "armor_class": item.armor_class_base,
                "dex_bonus_limit": item.dex_bonus_limit,
                "strength_requirement": item.strength_requirement,
                "stealth_disadvantage": item.stealth_disadvantage,
                "category": item.category.value
            })
        elif isinstance(item, SpellCore):
            stats.update({
                "level": item.level,
                "school": item.school,
                "casting_time": item.casting_time,
                "range": item.spell_range,
                "components": item.components,
                "duration": item.duration,
                "classes": item.classes
            })
        
        return stats
    
    def _extract_character_concept(self, character_data: Dict[str, Any]) -> str:
        """Extract a brief character concept from character data."""
        parts = []
        
        if "species" in character_data:
            parts.append(character_data["species"])
        
        if "classes" in character_data:
            classes = character_data["classes"]
            if isinstance(classes, dict):
                primary_class = max(classes.items(), key=lambda x: x[1])[0]
                parts.append(primary_class)
            elif isinstance(classes, list) and classes:
                parts.append(classes[0])
        
        if "background" in character_data:
            parts.append(character_data["background"])
        
        return " ".join(parts) if parts else "adventurer"
    
    def _needs_weapons(self, character_data: Dict[str, Any]) -> bool:
        """Check if character needs weapons."""
        # Most characters need weapons, spellcasters might not need as many
        return True
    
    def _needs_armor(self, character_data: Dict[str, Any]) -> bool:
        """Check if character needs armor."""
        # Most characters need armor
        return True
    
    def _is_spellcaster(self, character_data: Dict[str, Any]) -> bool:
        """Check if character is a spellcaster."""
        spellcasting_classes = ["wizard", "sorcerer", "warlock", "cleric", "druid", 
                               "bard", "paladin", "ranger", "artificer", "eldritch knight", 
                               "arcane trickster"]
        
        classes = character_data.get("classes", [])
        if isinstance(classes, dict):
            class_names = list(classes.keys())
        elif isinstance(classes, list):
            class_names = classes
        else:
            return False
        
        return any(cls.lower() in spellcasting_classes for cls in class_names)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def create_item_from_prompt(prompt: str, item_type: ItemType = ItemType.MAGIC_ITEM,
                           character_level: int = 1) -> CreationResult:
    """Utility function for simple item creation."""
    creator = ItemCreator()
    return await creator.create_item(prompt, item_type, character_level)

def create_character_items(character_data: Dict[str, Any]) -> CreationResult:
    """Create a complete item set for a character."""
    creator = ItemCreator()
    return creator.create_item_set(character_data)

def quick_item_creation(concept: str, item_type: str = "magic_item", 
                       level: int = 1) -> CreationResult:
    """Quick item creation utility."""
    creator = ItemCreator()
    
    # Map string to enum
    type_mapping = {
        "weapon": ItemType.WEAPON,
        "armor": ItemType.ARMOR,
        "spell": ItemType.SPELL,
        "magic_item": ItemType.MAGIC_ITEM,
        "potion": ItemType.POTION,
        "scroll": ItemType.SCROLL,
        "tool": ItemType.TOOL
    }
    
    item_type_enum = type_mapping.get(item_type.lower(), ItemType.MAGIC_ITEM)
    return creator.create_item(concept, item_type_enum, level)
