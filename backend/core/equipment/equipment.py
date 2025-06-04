# equipment.py
# Description: Master class for equipment management with support for specialized subclasses

from typing import Dict, List, Optional, Union, Any, Set
import json
import re
import uuid
from enum import Enum
import math
import importlib

from backend.core.ollama_service import OllamaService

class EquipmentCategory(Enum):
    """Categories of equipment"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ADVENTURING_GEAR = "adventuring_gear"
    TOOL = "tool"
    MOUNT = "mount"
    VEHICLE = "vehicle"
    TRADE_GOOD = "trade_good"
    TRINKET = "trinket"
    SPELLCASTING = "spellcasting"
    CUSTOM = "custom"

class ArmorCategory(Enum):
    """Types of armor"""
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    SHIELD = "shield"

class WeaponCategory(Enum):
    """Types of weapons"""
    SIMPLE_MELEE = "simple_melee"
    SIMPLE_RANGED = "simple_ranged"
    MARTIAL_MELEE = "martial_melee"
    MARTIAL_RANGED = "martial_ranged"
    NATURAL = "natural"
    IMPROVISED = "improvised"
    MAGICAL = "magical"

class DamageType(Enum):
    """Types of damage"""
    BLUDGEONING = "bludgeoning"
    PIERCING = "piercing"
    SLASHING = "slashing"
    ACID = "acid"
    COLD = "cold"
    FIRE = "fire"
    FORCE = "force"
    LIGHTNING = "lightning"
    NECROTIC = "necrotic"
    POISON = "poison"
    PSYCHIC = "psychic"
    RADIANT = "radiant"
    THUNDER = "thunder"

class RarityType(Enum):
    """Rarity types for magic items"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"

class Equipment:
    """
    Master class for handling all D&D equipment types.
    
    This class manages inventory, equipment details, and calculations related to
    weapons, armor, and other equipment. It coordinates with LLMEquipmentAdvisor
    for personalized equipment recommendations and descriptions.
    
    It also serves as the parent class for specialized equipment subclasses.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the equipment manager with an optional LLM service."""
        self.llm_service = llm_service or OllamaService()
        
        # Initialize LLM advisor
        from backend.core.equipment.llm_advisor import LLMEquipmentAdvisor
        self.llm_advisor = LLMEquipmentAdvisor(self.llm_service)
        
        # Core equipment collections - shared across parent and subclasses
        self.weapons = {}          # Weapon data indexed by ID
        self.armor = {}            # Armor data indexed by ID
        self.gear = {}             # Adventuring gear indexed by ID
        self.tools = {}            # Tools indexed by ID
        self.mounts = {}           # Mounts indexed by ID
        self.vehicles = {}         # Vehicles indexed by ID
        self.trade_goods = {}      # Trade goods indexed by ID
        self.trinkets = {}         # Trinkets indexed by ID
        self.spell_components = {} # Spellcasting components indexed by ID
        
        # Magic item registry (across all equipment types)
        self.magic_items = {}      # Magic items indexed by ID
        
        # Starting equipment by class and background
        self.starting_equipment = {
            "classes": {},
            "backgrounds": {}
        }
        
        # Dictionary to store subclass instances
        self._subclass_instances = {}
        
        # Load equipment data
        self._load_equipment_data()
        
        # Initialize subclasses if this is the parent class instance
        # (Avoids circular initialization when instantiated by subclasses)
        if self.__class__.__name__ == "Equipment":
            self._initialize_subclasses()
    
    def _initialize_subclasses(self):
        """Initialize equipment subclasses and store them for coordination."""
        # Only initialize subclasses if they haven't been created already
        if not self._subclass_instances:
            try:
                # Import and initialize weapons subclass
                from backend.core.equipment.weapons import Weapons
                self._subclass_instances["weapons"] = Weapons(self.llm_service)
                
                # Import and initialize armor subclass
                from backend.core.equipment.armor import Armor
                self._subclass_instances["armor"] = Armor(self.llm_service)
                
                # Import and initialize vehicles subclass
                from backend.core.equipment.vehicles import Vehicles
                self._subclass_instances["vehicles"] = Vehicles(self.llm_service)
                
                # Import and initialize trade_goods subclass
                from backend.core.equipment.trade_goods import TradeGoods
                self._subclass_instances["trade_goods"] = TradeGoods(self.llm_service)
                
                # Import and initialize trinkets subclass
                from backend.core.equipment.trinkets import Trinkets
                self._subclass_instances["trinkets"] = Trinkets(self.llm_service)
                
                # Import and initialize spellcasting_components subclass
                from backend.core.equipment.spellcasting_components import SpellcastingComponents
                self._subclass_instances["spell_components"] = SpellcastingComponents(self.llm_service)
                
                # Additional subclasses can be added here as they're created
                
            except ImportError as e:
                print(f"Warning: Could not import equipment subclass: {e}")
    
    def _load_equipment_data(self):
        """
        Load equipment data from data sources.
        
        This base implementation loads core equipment data.
        Subclasses can override to load specialized data.
        """
        # Load basic equipment data (simplified example for base class)
        # In a full implementation, this would load from JSON files or a database
        
        # Load weapons (simplified example)
        weapons = [
            {
                "id": "longsword",
                "name": "Longsword",
                "category": WeaponCategory.MARTIAL_MELEE,
                "cost": {"gp": 15},
                "damage_dice": "1d8",
                "damage_type": DamageType.SLASHING,
                "weight": 3,
                "properties": ["Versatile (1d10)"],
                "description": "A versatile weapon favored by many fighters."
            },
            {
                "id": "shortbow",
                "name": "Shortbow",
                "category": WeaponCategory.SIMPLE_RANGED,
                "cost": {"gp": 25},
                "damage_dice": "1d6",
                "damage_type": DamageType.PIERCING,
                "weight": 2,
                "properties": ["Ammunition", "Range (80/320)", "Two-Handed"],
                "description": "A simple ranged weapon used for hunting and warfare."
            }
        ]
        
        for weapon in weapons:
            self.weapons[weapon["id"]] = weapon
        
        # Load armor (simplified example)
        armor = [
            {
                "id": "chain_mail",
                "name": "Chain Mail",
                "category": ArmorCategory.HEAVY,
                "cost": {"gp": 75},
                "base_ac": 16,
                "dex_bonus_allowed": False,
                "strength_required": 13,
                "stealth_disadvantage": True,
                "weight": 55,
                "description": "Made of interlocking metal rings, chain mail includes a layer of quilted fabric worn underneath."
            },
            {
                "id": "leather",
                "name": "Leather Armor",
                "category": ArmorCategory.LIGHT,
                "cost": {"gp": 10},
                "base_ac": 11,
                "dex_bonus_allowed": True,
                "weight": 10,
                "description": "The breastplate and shoulder protectors of this armor are made of leather that has been stiffened by being boiled in oil."
            }
        ]
        
        for armor_item in armor:
            self.armor[armor_item["id"]] = armor_item
        
        # Load adventuring gear (simplified example)
        gear = [
            {
                "id": "backpack",
                "name": "Backpack",
                "category": EquipmentCategory.ADVENTURING_GEAR,
                "cost": {"gp": 2},
                "weight": 5,
                "description": "A backpack can hold one cubic foot or 30 pounds of gear."
            },
            {
                "id": "rope",
                "name": "Rope, hempen (50 feet)",
                "category": EquipmentCategory.ADVENTURING_GEAR,
                "cost": {"gp": 1},
                "weight": 10,
                "description": "Rope has 2 hit points and can be burst with a DC 17 Strength check."
            }
        ]
        
        for gear_item in gear:
            self.gear[gear_item["id"]] = gear_item
        
        # Initialize starting equipment (simplified example)
        self.starting_equipment["classes"] = {
            "fighter": {
                "options": [
                    {"items": [{"id": "longsword", "quantity": 1}, {"id": "chain_mail", "quantity": 1}]},
                    {"items": [{"id": "shortbow", "quantity": 1}, {"id": "leather", "quantity": 1}]}
                ]
            }
        }
        
        self.starting_equipment["backgrounds"] = {
            "soldier": {
                "items": [{"id": "backpack", "quantity": 1}, {"id": "rope", "quantity": 1}]
            }
        }
    
    # === CORE EQUIPMENT METHODS ===
    
    def get_all_weapons(self, filtered_by_character: bool = False, 
                     character_data: Dict[str, Any] = None,
                     fighting_style: str = None) -> List[Dict[str, Any]]:
        """
        Get a list of all available weapons, optionally filtered by character preferences.
        
        Args:
            filtered_by_character: Whether to filter/rank weapons by character attributes
            character_data: Character data for personalized filtering
            fighting_style: Character's fighting style preference
            
        Returns:
            List[Dict[str, Any]]: List of weapon data
        """
        # If weapons subclass is available, delegate to it
        if "weapons" in self._subclass_instances:
            return self._subclass_instances["weapons"].get_all_weapons(
                filtered_by_character=filtered_by_character,
                character_data=character_data,
                fighting_style=fighting_style
            )
        
        # Fallback implementation if weapons subclass is not available
        weapons_list = list(self.weapons.values())
        
        # If no character filtering is requested, return all weapons
        if not filtered_by_character or not character_data:
            return weapons_list
        
        # Use LLM to recommend weapons based on character data
        recommendations = self.llm_advisor.recommend_weapons(
            character_data, 
            fighting_style=fighting_style, 
            character_backstory=character_data.get("backstory")
        )
        
        # Add recommendation reasoning to the weapon data
        for weapon in weapons_list:
            for rec in recommendations:
                if weapon["name"].lower() == rec["name"].lower():
                    weapon["recommendation_reason"] = rec.get("reasoning")
                    weapon["recommendation_rank"] = recommendations.index(rec) + 1
        
        # Sort weapons, putting recommended ones first
        return sorted(weapons_list, key=lambda x: x.get("recommendation_rank", 999))
    
    def get_all_armor(self, filtered_by_character: bool = False,
                   character_data: Dict[str, Any] = None,
                   character_style: str = None,
                   mobility_priority: int = 5) -> List[Dict[str, Any]]:
        """
        Get a list of all available armor, optionally filtered by character preferences.
        
        Args:
            filtered_by_character: Whether to filter/rank armor by character attributes
            character_data: Character data for personalized filtering
            character_style: Description of character's aesthetic style
            mobility_priority: Importance of mobility (1-10)
            
        Returns:
            List[Dict[str, Any]]: List of armor data
        """
        # If armor subclass is available, delegate to it
        if "armor" in self._subclass_instances:
            return self._subclass_instances["armor"].get_all_armor(
                filtered_by_character=filtered_by_character,
                character_data=character_data,
                character_style=character_style,
                mobility_priority=mobility_priority
            )
        
        # Fallback implementation if armor subclass is not available
        armor_list = list(self.armor.values())
        
        # If no character filtering is requested, return all armor
        if not filtered_by_character or not character_data:
            return armor_list
        
        # Use LLM to recommend armor based on character data
        recommendations = self.llm_advisor.recommend_armor(
            character_data,
            character_style=character_style,
            mobility_priority=mobility_priority
        )
        
        # Add recommendation reasoning to the armor data
        for armor_item in armor_list:
            for rec in recommendations:
                if armor_item["name"].lower() == rec["name"].lower():
                    armor_item["recommendation_reason"] = rec.get("reasoning")
                    armor_item["recommendation_rank"] = recommendations.index(rec) + 1
        
        # Sort armor, putting recommended ones first
        return sorted(armor_list, key=lambda x: x.get("recommendation_rank", 999))
    
    def get_all_gear(self, filtered_by_adventure: bool = False,
                  adventure_context: str = None,
                  character_role: str = None) -> List[Dict[str, Any]]:
        """
        Get a list of all available adventuring gear, optionally filtered by adventure context.
        
        Args:
            filtered_by_adventure: Whether to filter gear by adventure context
            adventure_context: Description of upcoming adventure/environment
            character_role: Character's role in the party
            
        Returns:
            List[Dict[str, Any]]: List of gear data
        """
        gear_list = list(self.gear.values())
        
        # If no adventure filtering is requested, return all gear
        if not filtered_by_adventure or not adventure_context:
            return gear_list
        
        # Use LLM to recommend gear based on adventure context
        recommendations = self.llm_advisor.recommend_gear(
            adventure_context=adventure_context,
            character_role=character_role
        )
        
        # Add recommendation reasoning to the gear data
        for gear_item in gear_list:
            for rec in recommendations:
                if gear_item["name"].lower() == rec["name"].lower():
                    gear_item["recommendation_reason"] = rec.get("reasoning")
                    gear_item["recommendation_rank"] = recommendations.index(rec) + 1
        
        # Sort gear, putting recommended ones first
        return sorted(gear_list, key=lambda x: x.get("recommendation_rank", 999))
    
    def get_equipment_details(self, item_id: str, 
                           include_creative_uses: bool = False) -> Dict[str, Any]:
        """
        Get detailed information about a specific equipment item.
        
        Args:
            item_id: ID of the equipment item
            include_creative_uses: Whether to include LLM-generated creative uses
            
        Returns:
            Dict[str, Any]: Equipment details
        """
        # Find the item in all equipment categories
        item_data = self._find_item_by_id(item_id)
        if not item_data:
            return None
        
        # If creative uses are requested, add them to the item data
        if include_creative_uses:
            creative_uses = self.llm_advisor.generate_creative_uses(
                item_data["name"],
                item_data.get("description", "")
            )
            
            # Add to a copy of the item data to avoid modifying the original
            item_data = item_data.copy()
            item_data["creative_uses"] = creative_uses
        
        return item_data
    
    def calculate_weapon_damage(self, weapon_id: str, 
                             ability_scores: Dict[str, int],
                             proficiency_bonus: int = 2,
                             include_tactical_analysis: bool = False) -> Dict[str, Any]:
        """
        Calculate attack bonus and damage for a weapon with given ability scores.
        
        Args:
            weapon_id: ID of the weapon
            ability_scores: Character ability scores
            proficiency_bonus: Character proficiency bonus
            include_tactical_analysis: Whether to include tactical analysis
            
        Returns:
            Dict[str, Any]: Damage calculation results
        """
        # If weapons subclass is available, delegate to it
        if "weapons" in self._subclass_instances:
            return self._subclass_instances["weapons"].calculate_weapon_damage(
                weapon_id=weapon_id,
                ability_scores=ability_scores,
                proficiency_bonus=proficiency_bonus,
                include_tactical_analysis=include_tactical_analysis
            )
        
        # Fallback implementation if weapons subclass is not available
        weapon_data = self._find_item_by_id(weapon_id)
        if not weapon_data or "category" not in weapon_data or not isinstance(weapon_data["category"], WeaponCategory):
            return {"error": "Weapon not found or invalid"}
        
        # Calculate attack modifier
        is_finesse = "finesse" in [p.lower() for p in weapon_data.get("properties", [])]
        is_ranged = any(ranged in weapon_data.get("category", "").value for ranged in ["ranged", "thrown"])
        
        str_mod = (ability_scores.get("strength", 10) - 10) // 2
        dex_mod = (ability_scores.get("dexterity", 10) - 10) // 2
        
        if is_finesse:
            ability_mod = max(str_mod, dex_mod)
            ability_used = "Dexterity" if dex_mod > str_mod else "Strength"
        elif is_ranged:
            ability_mod = dex_mod
            ability_used = "Dexterity"
        else:
            ability_mod = str_mod
            ability_used = "Strength"
        
        attack_modifier = ability_mod + proficiency_bonus
        damage_modifier = ability_mod
        
        result = {
            "weapon_name": weapon_data["name"],
            "attack_bonus": attack_modifier,
            "damage_dice": weapon_data.get("damage_dice", "1d6"),
            "damage_modifier": damage_modifier,
            "damage_type": weapon_data.get("damage_type", "").value if isinstance(weapon_data.get("damage_type", ""), DamageType) else "unknown",
            "total_damage": f"{weapon_data.get('damage_dice', '1d6')} + {damage_modifier}",
            "ability_used": ability_used
        }
        
        # Add tactical analysis if requested
        if include_tactical_analysis:
            tactical_analysis = self.llm_advisor.generate_tactical_analysis(
                weapon_data, ability_scores, proficiency_bonus
            )
            result["tactical_analysis"] = tactical_analysis
        
        return result
    
    def calculate_armor_class(self, armor_id: str, 
                           dexterity_modifier: int,
                           include_defensive_analysis: bool = False) -> Dict[str, Any]:
        """
        Calculate AC from armor and dexterity modifier.
        
        Args:
            armor_id: ID of the armor
            dexterity_modifier: Character's dexterity modifier
            include_defensive_analysis: Whether to include defensive analysis
            
        Returns:
            Dict[str, Any]: AC calculation results
        """
        # If armor subclass is available, delegate to it
        if "armor" in self._subclass_instances:
            return self._subclass_instances["armor"].calculate_armor_class(
                armor_id=armor_id,
                dexterity_modifier=dexterity_modifier,
                include_defensive_analysis=include_defensive_analysis
            )
            
        # Fallback implementation if armor subclass is not available
        armor_data = self._find_item_by_id(armor_id)
        if not armor_data or "category" not in armor_data or not isinstance(armor_data["category"], ArmorCategory):
            return {"error": "Armor not found or invalid"}
        
        # Calculate AC based on armor type
        base_ac = armor_data.get("base_ac", 10)
        dex_bonus_allowed = armor_data.get("dex_bonus_allowed", True)
        max_dex_bonus = armor_data.get("max_dex_bonus")
        
        applied_dex_mod = 0
        if dex_bonus_allowed:
            if max_dex_bonus is not None:
                applied_dex_mod = min(dexterity_modifier, max_dex_bonus)
            else:
                applied_dex_mod = dexterity_modifier
        
        total_ac = base_ac + applied_dex_mod
        
        result = {
            "armor_name": armor_data["name"],
            "base_ac": base_ac,
            "dexterity_modifier": dexterity_modifier,
            "applied_dex_modifier": applied_dex_mod,
            "total_ac": total_ac,
            "stealth_disadvantage": armor_data.get("stealth_disadvantage", False)
        }
        
        # Add defensive analysis if requested
        if include_defensive_analysis:
            defensive_analysis = self.llm_advisor.generate_defensive_analysis(
                armor_data, dexterity_modifier
            )
            result["defensive_analysis"] = defensive_analysis
        
        return result
    
    def validate_equipment_requirements(self, character_data: Dict[str, Any], 
                                     item_id: str,
                                     suggest_qualification_path: bool = False) -> Union[bool, Dict[str, Any]]:
        """
        Check if a character meets the requirements to use an equipment item.
        
        Args:
            character_data: Character attributes
            item_id: ID of the equipment item
            suggest_qualification_path: Whether to suggest a path to qualification
            
        Returns:
            Union[bool, Dict[str, Any]]: True if qualified, or qualification info
        """
        item_data = self._find_item_by_id(item_id)
        if not item_data:
            return False
        
        # Check requirements (if any)
        requirements = {}
        
        # Check armor strength requirements
        if "category" in item_data and isinstance(item_data["category"], ArmorCategory) and item_data["category"] == ArmorCategory.HEAVY:
            if "strength_required" in item_data and item_data["strength_required"] > 0:
                requirements["ability_scores"] = {"strength": item_data["strength_required"]}
        
        # Check weapon proficiency requirements
        if "category" in item_data and isinstance(item_data["category"], WeaponCategory):
            if item_data["category"] in [WeaponCategory.MARTIAL_MELEE, WeaponCategory.MARTIAL_RANGED]:
                requirements["proficiencies"] = ["martial_weapons"]
        
        # If no requirements, automatically qualified
        if not requirements:
            return True
        
        # Check ability score requirements
        ability_scores = character_data.get("ability_scores", {})
        ability_requirements = requirements.get("ability_scores", {})
        
        for ability, required_score in ability_requirements.items():
            if ability_scores.get(ability.lower(), 0) < required_score:
                if not suggest_qualification_path:
                    return False
                
                # Generate qualification path with LLM
                return self.llm_advisor.suggest_qualification_path(character_data, item_data)
        
        # Check proficiency requirements
        proficiency_requirements = requirements.get("proficiencies", [])
        character_proficiencies = character_data.get("proficiencies", {}).get("weapons", [])
        
        for req in proficiency_requirements:
            if req not in character_proficiencies and "all_weapons" not in character_proficiencies:
                if not suggest_qualification_path:
                    return False
                
                # Generate qualification path with LLM
                return self.llm_advisor.suggest_qualification_path(character_data, item_data)
        
        # All requirements met
        return True
    
    def get_starting_equipment(self, class_name: str, 
                            background_name: str = None) -> Dict[str, Any]:
        """
        Get standard starting equipment for a class and background.
        
        Args:
            class_name: Character class
            background_name: Character background
            
        Returns:
            Dict[str, Any]: Starting equipment options
        """
        result = {
            "class_equipment": {},
            "background_equipment": {}
        }
        
        # Get class equipment options
        class_key = class_name.lower()
        if class_key in self.starting_equipment["classes"]:
            result["class_equipment"] = self.starting_equipment["classes"][class_key]
        
        # Get background equipment
        if background_name:
            background_key = background_name.lower()
            if background_key in self.starting_equipment["backgrounds"]:
                result["background_equipment"] = self.starting_equipment["backgrounds"][background_key]
        
        return result
    
    def get_personalized_starting_equipment(self, class_name: str,
                                         background_name: str,
                                         backstory: str = None) -> Dict[str, Any]:
        """
        Get personalized starting equipment based on character backstory.
        
        Args:
            class_name: Character class
            background_name: Character background
            backstory: Character backstory text
            
        Returns:
            Dict[str, Any]: Personalized equipment suggestions
        """
        # Get standard equipment first
        standard_equipment = self.get_starting_equipment(class_name, background_name)
        
        # Use LLM to personalize equipment
        personalized = self.llm_advisor.generate_personalized_starting_equipment(
            class_name, background_name, backstory
        )
        
        # Combine standard and personalized
        result = {
            "standard_equipment": standard_equipment,
            "personalized_suggestions": personalized
        }
        
        return result
    
    def create_custom_equipment(self, concept: str = None,
                             equipment_type: str = None,
                             partial_data: Dict[str, Any] = None,
                             character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create custom equipment based on a concept or partial data.
        
        Args:
            concept: Equipment concept description
            equipment_type: Type of equipment to create
            partial_data: Partial equipment data to complete
            character_data: Character data for context
            
        Returns:
            Dict[str, Any]: Custom equipment data
        """
        # Check if there's a specialized subclass for this equipment type
        if equipment_type and equipment_type.lower() in self._subclass_instances:
            subclass = self._subclass_instances[equipment_type.lower()]
            # Check if the subclass has a create_custom method
            if hasattr(subclass, "create_custom_" + equipment_type.lower()):
                create_method = getattr(subclass, "create_custom_" + equipment_type.lower())
                return create_method(concept=concept, partial_data=partial_data, character_data=character_data)
        
        # Default implementation using LLM advisor
        custom_item = self.llm_advisor.create_custom_equipment(
            concept=concept,
            equipment_type=equipment_type,
            partial_data=partial_data,
            character_data=character_data
        )
        
        # Generate a unique ID for the item
        item_id = f"custom_{str(uuid.uuid4())[:8]}"
        custom_item["id"] = item_id
        
        # Store the custom item in the appropriate category
        self._store_equipment_item(custom_item)
        
        return custom_item
    
    def calculate_inventory_weight(self, inventory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate the total weight of an inventory and check for encumbrance.
        
        Args:
            inventory: List of items with quantities
            
        Returns:
            Dict[str, Any]: Weight calculation and encumbrance info
        """
        total_weight = 0.0
        item_weights = []
        
        for item_entry in inventory:
            item_id = item_entry.get("id")
            quantity = item_entry.get("quantity", 1)
            
            item_data = self._find_item_by_id(item_id)
            if item_data and "weight" in item_data:
                item_weight = item_data["weight"] * quantity
                total_weight += item_weight
                item_weights.append({
                    "name": item_data["name"],
                    "quantity": quantity,
                    "unit_weight": item_data["weight"],
                    "total_weight": item_weight
                })
        
        return {
            "total_weight": total_weight,
            "item_weights": item_weights,
            "weight_unit": "lb."
        }
    
    def analyze_encumbrance(self, total_weight: float, strength_score: int) -> Dict[str, Any]:
        """
        Analyze encumbrance based on total weight and character strength.
        
        Args:
            total_weight: Total weight being carried (in pounds)
            strength_score: Character's Strength ability score
            
        Returns:
            Dict[str, Any]: Encumbrance analysis
        """
        # Calculate carrying capacity thresholds
        carrying_capacity = strength_score * 15  # Maximum carrying capacity in pounds
        encumbered_threshold = strength_score * 5
        heavily_encumbered_threshold = strength_score * 10
        
        # Determine encumbrance status
        if total_weight > carrying_capacity:
            status = "over_capacity"
            movement_penalty = "cannot move"
        elif total_weight > heavily_encumbered_threshold:
            status = "heavily_encumbered"
            movement_penalty = "speed reduced by 20 feet"
        elif total_weight > encumbered_threshold:
            status = "encumbered"
            movement_penalty = "speed reduced by 10 feet"
        else:
            status = "unencumbered"
            movement_penalty = "none"
        
        return {
            "status": status,
            "carrying_capacity": carrying_capacity,
            "encumbered_threshold": encumbered_threshold,
            "heavily_encumbered_threshold": heavily_encumbered_threshold,
            "movement_penalty": movement_penalty,
            "total_weight": total_weight
        }
        
    # === SPECIALIZED EQUIPMENT ACCESS METHODS ===
    
    def get_trinket(self, trinket_id: str) -> Optional[Dict[str, Any]]:
        """Access a specific trinket by ID."""
        if "trinkets" in self._subclass_instances:
            return self._subclass_instances["trinkets"]._find_item_by_id(trinket_id)
        return self._find_item_by_id(trinket_id)
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        """Access a specific vehicle by ID."""
        if "vehicles" in self._subclass_instances:
            return self._subclass_instances["vehicles"]._find_item_by_id(vehicle_id)
        return self._find_item_by_id(vehicle_id)
    
    def get_trade_good(self, good_id: str) -> Optional[Dict[str, Any]]:
        """Access a specific trade good by ID."""
        if "trade_goods" in self._subclass_instances:
            return self._subclass_instances["trade_goods"]._find_item_by_id(good_id)
        return self._find_item_by_id(good_id)
    
    def get_spellcasting_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Access a specific spellcasting component by ID."""
        if "spell_components" in self._subclass_instances:
            return self._subclass_instances["spell_components"]._find_item_by_id(component_id)
        return self._find_item_by_id(component_id)
        
    # === HELPER METHODS ===
    
    def _find_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Find an item by ID across all equipment categories.
        
        This method searches all equipment collections for an item with the specified ID.
        It also checks for items in specialized subclass collections.
        
        Args:
            item_id: ID of the equipment item to find
            
        Returns:
            Optional[Dict[str, Any]]: Item data if found, None otherwise
        """
        # Check all standard equipment categories
        collections = [
            self.weapons, self.armor, self.gear, self.tools,
            self.mounts, self.vehicles, self.trade_goods, self.trinkets,
            self.spell_components, self.magic_items
        ]
        
        for collection in collections:
            if item_id in collection:
                return collection[item_id]
        
        # If not found and this is the parent class, check subclasses
        if self.__class__.__name__ == "Equipment":
            for subclass_name, subclass in self._subclass_instances.items():
                # If the subclass has its own _find_item_by_id method, use it
                if hasattr(subclass, "_find_item_by_id"):
                    item = subclass._find_item_by_id(item_id)
                    if item:
                        return item
        
        return None
    
    def _store_equipment_item(self, item: Dict[str, Any]) -> None:
        """
        Store an equipment item in the appropriate collection based on its category.
        
        Args:
            item: Equipment item data with category information
        """
        if "id" not in item:
            return
        
        item_id = item["id"]
        
        # Determine which collection to store the item in
        if "category" in item:
            category = item["category"]
            if isinstance(category, EquipmentCategory):
                if category == EquipmentCategory.WEAPON:
                    self.weapons[item_id] = item
                elif category == EquipmentCategory.ARMOR:
                    self.armor[item_id] = item
                elif category == EquipmentCategory.ADVENTURING_GEAR:
                    self.gear[item_id] = item
                elif category == EquipmentCategory.TOOL:
                    self.tools[item_id] = item
                elif category == EquipmentCategory.MOUNT:
                    self.mounts[item_id] = item
                elif category == EquipmentCategory.VEHICLE:
                    self.vehicles[item_id] = item
                elif category == EquipmentCategory.TRADE_GOOD:
                    self.trade_goods[item_id] = item
                elif category == EquipmentCategory.TRINKET:
                    self.trinkets[item_id] = item
                elif category == EquipmentCategory.SPELLCASTING:
                    self.spell_components[item_id] = item
            elif isinstance(category, WeaponCategory):
                self.weapons[item_id] = item
            elif isinstance(category, ArmorCategory):
                self.armor[item_id] = item
            else:
                # Default to adventuring gear if category is not recognized
                self.gear[item_id] = item
        else:
            # Default to adventuring gear if no category specified
            self.gear[item_id] = item
        
        # If item is magical, also add to magic items
        if item.get("is_magical", False):
            self.magic_items[item_id] = item