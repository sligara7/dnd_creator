"""Item allocation validation rules.

This module provides validation rules for allocating items, spells,
and other resources to characters, ensuring proper requirements and
restrictions are met.
"""

from typing import Dict, Any, List
from ..core.validation import (
    ValidationResult,
    Validator,
    required_fields,
    field_type,
    field_range,
    field_choices,
)
from ..models.character import Character
from ..models.character import Equipment, Weapon, Armor
from ..models.spellcasting import Spell
from ..models.enums import WeaponType, ArmorType, AbilityType

def validate_item_allocation(
    character: Character,
    item: Any,
    allocation_type: str,
) -> ValidationResult:
    """Validate an item allocation to a character.
    
    Args:
        character: Character receiving allocation
        item: Item being allocated
        allocation_type: Type of allocation
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Basic validation
    if character is None:
        result.add_error("Character is required")
        return result
        
    if item is None:
        result.add_error("Item is required")
        return result
        
    # Type-specific validation
    if isinstance(item, Weapon):
        weapon = validate_weapon_allocation(character, item, allocation_type)
        result.merge(weapon)
        
    elif isinstance(item, Armor):
        armor = validate_armor_allocation(character, item, allocation_type)
        result.merge(armor)
        
    elif isinstance(item, Spell):
        spell = validate_spell_allocation(character, item, allocation_type)
        result.merge(spell)
        
    elif isinstance(item, Equipment):
        equipment = validate_equipment_allocation(character, item, allocation_type)
        result.merge(equipment)
        
    else:
        result.add_error(f"Unknown item type: {type(item)}")
        
    return result

def validate_weapon_allocation(
    character: Character,
    weapon: Weapon,
    allocation_type: str,
) -> ValidationResult:
    """Validate weapon allocation.
    
    Args:
        character: Character receiving weapon
        weapon: Weapon being allocated
        allocation_type: Type of allocation
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Check proficiency
    if allocation_type == "equipped":
        if weapon.weapon_type not in character.weapon_proficiencies:
            result.add_error(
                f"Character is not proficient with {weapon.weapon_type} weapons"
            )
            
        if weapon.finesse and weapon.two_handed:
            result.add_warning(
                "Unusual weapon properties: both finesse and two-handed"
            )
            
    return result

def validate_armor_allocation(
    character: Character,
    armor: Armor,
    allocation_type: str,
) -> ValidationResult:
    """Validate armor allocation.
    
    Args:
        character: Character receiving armor
        armor: Armor being allocated
        allocation_type: Type of allocation
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Check proficiency
    if allocation_type == "equipped":
        if armor.armor_type not in character.armor_proficiencies:
            result.add_error(
                f"Character is not proficient with {armor.armor_type} armor"
            )
            
        # Check strength requirement
        if armor.strength_requirement:
            strength = character.abilities.get("strength", {}).get("score", 0)
            if strength < armor.strength_requirement:
                result.add_error(
                    f"Strength score of {armor.strength_requirement} required "
                    f"to wear this armor (current: {strength})"
                )
                
        # Check existing armor
        if character.armor and allocation_type == "equipped":
            result.add_warning("Character already has equipped armor")
            
    return result

def validate_spell_allocation(
    character: Character,
    spell: Spell,
    allocation_type: str,
) -> ValidationResult:
    """Validate spell allocation.
    
    Args:
        character: Character receiving spell
        spell: Spell being allocated
        allocation_type: Type of allocation
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Must have spellcasting ability
    if not character.spellcasting_ability:
        result.add_error("Character does not have spellcasting ability")
        return result
        
    # Check spell level
    max_level = character.get_max_spell_level()
    if spell.level > max_level:
        result.add_error(
            f"Spell level {spell.level} too high "
            f"(max: {max_level})"
        )
        
    # Check if spell is on class list
    primary_class = character.get_primary_class()
    if primary_class and primary_class not in spell.classes:
        result.add_warning(
            f"Spell not on {primary_class} spell list"
        )
        
    # Check preparation limits
    if allocation_type == "prepared":
        prepared_count = len(character.spells_prepared)
        prep_limit = character.get_prepared_spells_limit()
        if prep_limit and prepared_count >= prep_limit:
            result.add_error(
                f"Cannot prepare more spells "
                f"(limit: {prep_limit})"
            )
            
    return result

def validate_equipment_allocation(
    character: Character,
    equipment: Equipment,
    allocation_type: str,
) -> ValidationResult:
    """Validate equipment allocation.
    
    Args:
        character: Character receiving equipment
        equipment: Equipment being allocated
        allocation_type: Type of allocation
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Attunement validation
    if allocation_type == "equipped" and equipment.requires_attunement:
        attuned_count = len(character.attuned_items)
        if attuned_count >= character.attunement_slots:
            result.add_error(
                f"No available attunement slots "
                f"(limit: {character.attunement_slots})"
            )
            
    # Weight validation
    if equipment.weight:
        total_weight = sum(
            i.weight * i.quantity 
            for i in character.equipment
        )
        max_weight = character.get_carrying_capacity()
        new_total = total_weight + (equipment.weight * equipment.quantity)
        
        if new_total > max_weight:
            result.add_warning(
                f"Equipment weight would exceed carrying capacity "
                f"({new_total}/{max_weight})"
            )
            
    return result

def validate_deallocation(
    character: Character,
    item: Any,
    quantity: int,
) -> ValidationResult:
    """Validate removing an allocation.
    
    Args:
        character: Character to remove from
        item: Item to remove
        quantity: Quantity to remove
        
    Returns:
        Validation result
    """
    result = ValidationResult()
    
    # Basic validation
    if quantity < 1:
        result.add_error("Quantity must be at least 1")
        
    # Check if item exists
    item_id = getattr(item, "id", None)
    if not item_id:
        result.add_error("Invalid item reference")
        return result
        
    # Find allocation
    allocation = None
    if isinstance(item, Equipment):
        allocation = next(
            (i for i in character.equipment if i.id == item_id),
            None
        )
    elif isinstance(item, Spell):
        allocation = next(
            (s for s in character.spells_known if s.id == item_id),
            None
        )
        
    if not allocation:
        result.add_error("Item allocation not found")
        return result
        
    # Check quantity
    if quantity > allocation.quantity:
        result.add_error(
            f"Cannot remove {quantity} items "
            f"(only {allocation.quantity} allocated)"
        )
        
    return result
