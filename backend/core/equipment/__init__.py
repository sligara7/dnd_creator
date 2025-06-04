"""
D&D 2024 Equipment System

This package provides classes for managing character equipment in D&D,
including weapons, armor, gear, and other items.

Classes:
    Equipment: Base class for all equipment handling
    Weapons: Specialized handling for weapons and combat items
    Armor: Specialized handling for armor and protective gear
    Vehicles: Specialized handling for mounts and vehicles
    TradeGoods: Specialized handling for trade goods
    Trinkets: Specialized handling for small flavor items
    SpellcastingComponents: Specialized handling for magical components
    LLMEquipmentAdvisor: AI-powered equipment recommendations

Enumerations:
    EquipmentCategory: Categories of equipment
    ArmorCategory: Types of armor
    WeaponCategory: Types of weapons
    DamageType: Types of damage
    RarityType: Item rarity levels
    ComponentType: Types of spellcasting components
    FocusProperty: Properties of arcane/divine foci

Functions:
    get_equipment_handler: Factory function to get appropriate equipment handler
"""

# Import enums for external use
from backend.core.equipment.equipment import (
    EquipmentCategory, 
    ArmorCategory, 
    WeaponCategory, 
    DamageType, 
    RarityType
)

# Import the base Equipment class
from backend.core.equipment.equipment import Equipment

# Import specialized equipment classes
# Use lazy imports to prevent circular dependencies
try:
    from backend.core.equipment.weapons import Weapons
except ImportError:
    Weapons = None

try:
    from backend.core.equipment.armor import Armor
except ImportError:
    Armor = None

try:
    from backend.core.equipment.vehicles import Vehicles
except ImportError:
    Vehicles = None

try:
    from backend.core.equipment.trade_goods import TradeGoods
except ImportError:
    TradeGoods = None

try:
    from backend.core.equipment.trinkets import Trinkets
except ImportError:
    Trinkets = None

try:
    from backend.core.equipment.spellcasting_components import (
        SpellcastingComponents, 
        ComponentType,
        FocusProperty
    )
except ImportError:
    SpellcastingComponents = None
    ComponentType = None
    FocusProperty = None

# Import LLM advisor
from backend.core.equipment.llm_advisor import LLMEquipmentAdvisor

# Create a convenient function to get the appropriate equipment class
def get_equipment_handler(equipment_type=None, llm_service=None):
    """
    Get the appropriate equipment handler class based on equipment type.
    
    Args:
        equipment_type: String indicating the type of equipment to handle
        llm_service: Optional LLM service to use for AI assistance
        
    Returns:
        An instance of the appropriate equipment class
    """
    if equipment_type is None:
        return Equipment(llm_service)
        
    equipment_type = equipment_type.lower()
    
    if equipment_type == 'weapons' and Weapons is not None:
        return Weapons(llm_service)
    elif equipment_type == 'armor' and Armor is not None:
        return Armor(llm_service)
    elif equipment_type == 'vehicles' and Vehicles is not None:
        return Vehicles(llm_service)
    elif equipment_type in ('trade_goods', 'trade', 'goods') and TradeGoods is not None:
        return TradeGoods(llm_service)
    elif equipment_type in ('trinkets', 'trinket') and Trinkets is not None:
        return Trinkets(llm_service)
    elif equipment_type in ('spellcasting', 'components', 'spell_components') and SpellcastingComponents is not None:
        return SpellcastingComponents(llm_service)
    else:
        # Fall back to base Equipment class
        return Equipment(llm_service)

# Define public exports
__all__ = [
    'Equipment',
    'Weapons',
    'Armor',
    'Vehicles',
    'TradeGoods',
    'Trinkets',
    'SpellcastingComponents',
    'LLMEquipmentAdvisor',
    'get_equipment_handler',
    'EquipmentCategory',
    'ArmorCategory',
    'WeaponCategory',
    'DamageType',
    'RarityType',
    'ComponentType',
    'FocusProperty'
]