# weapons.py
# Description: Handles weapon equipment and combat calculations

from typing import Dict, List, Optional, Union, Any, Tuple
import json
import re
from enum import Enum

from backend.core.equipment.equipment import Equipment, WeaponCategory, DamageType, RarityType

class WeaponProperty(Enum):
    """Properties that weapons can have"""
    AMMUNITION = "ammunition"
    FINESSE = "finesse"
    HEAVY = "heavy"
    LIGHT = "light"
    LOADING = "loading"
    REACH = "reach"
    SPECIAL = "special"
    THROWN = "thrown"
    TWO_HANDED = "two_handed"
    VERSATILE = "versatile"
    MAGICAL = "magical"  # For magic weapons

class WeaponRange:
    """Represents range values for ranged weapons"""

    def __init__(self, normal_range: int, long_range: int = None):
        self.normal_range = normal_range
        self.long_range = long_range or normal_range * 3
    
    def __str__(self) -> str:
        return f"Range ({self.normal_range}/{self.long_range})"
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "normal_range": self.normal_range,
            "long_range": self.long_range
        }

class Weapon(Equipment):
    """
    Class for handling weapon equipment, combat calculations, and customization.
    
    Extends the Equipment class with weapon-specific functionality for creating,
    customizing, and analyzing weapons for character builds.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the weapon manager with parent equipment functionality."""
        super().__init__(llm_service)
        
        # Additional weapon configuration
        self.weapon_proficiency_groups = {
            "martial": set([
                WeaponCategory.MARTIAL_MELEE.value,
                WeaponCategory.MARTIAL_RANGED.value
            ]),
            "simple": set([
                WeaponCategory.SIMPLE_MELEE.value,
                WeaponCategory.SIMPLE_RANGED.value
            ])
        }
        
        # Common weapon properties by type
        self.common_properties = {
            WeaponCategory.SIMPLE_MELEE: ["light"],
            WeaponCategory.MARTIAL_MELEE: ["versatile", "heavy"],
            WeaponCategory.SIMPLE_RANGED: ["ammunition", "loading"],
            WeaponCategory.MARTIAL_RANGED: ["ammunition", "heavy", "two_handed"]
        }
    
    def get_weapons_by_category(self, category: Union[WeaponCategory, str]) -> List[Dict[str, Any]]:
        """
        Get weapons filtered by category.
        
        Args:
            category: Category to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of weapons in the category
        """
        if isinstance(category, str):
            # Try to convert string to enum
            try:
                category = WeaponCategory(category.lower())
            except ValueError:
                # If not a valid category, return empty list
                return []
        
        return [w for w in self.weapons.values() if w["category"] == category]
    
    def get_weapons_by_property(self, property_name: Union[WeaponProperty, str]) -> List[Dict[str, Any]]:
        """
        Get weapons that have a specific property.
        
        Args:
            property_name: Property to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of weapons with the property
        """
        property_str = property_name.value if isinstance(property_name, WeaponProperty) else str(property_name).lower()
        
        return [
            w for w in self.weapons.values() 
            if "properties" in w and any(property_str in prop.lower() for prop in w["properties"])
        ]
    
    def get_weapons_by_damage_type(self, damage_type: Union[DamageType, str]) -> List[Dict[str, Any]]:
        """
        Get weapons that deal a specific damage type.
        
        Args:
            damage_type: Damage type to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of weapons with the damage type
        """
        damage_str = damage_type.value if isinstance(damage_type, DamageType) else str(damage_type).lower()
        
        return [
            w for w in self.weapons.values() 
            if "damage_type" in w and (
                (isinstance(w["damage_type"], DamageType) and w["damage_type"].value == damage_str) or
                (isinstance(w["damage_type"], str) and w["damage_type"].lower() == damage_str)
            )
        ]
    
    def check_weapon_proficiency(self, character_data: Dict[str, Any], weapon_id: str) -> bool:
        """
        Check if a character is proficient with a specific weapon.
        
        Args:
            character_data: Character data including proficiencies
            weapon_id: ID of the weapon to check
            
        Returns:
            bool: True if proficient, False otherwise
        """
        weapon_data = self._find_item_by_id(weapon_id)
        if not weapon_data:
            return False
        
        # Get character proficiencies
        proficiencies = character_data.get("proficiencies", {}).get("weapons", [])
        if not proficiencies:
            return False
        
        # Check for weapon name in specific proficiencies
        if weapon_data.get("name", "").lower() in [p.lower() for p in proficiencies]:
            return True
        
        # Check for weapon category in group proficiencies
        if "category" in weapon_data:
            category = weapon_data["category"]
            category_str = category.value if isinstance(category, WeaponCategory) else str(category)
            
            # Check simple/martial weapon proficiency
            if (category_str in self.weapon_proficiency_groups["simple"] and
                any("simple weapons" in p.lower() for p in proficiencies)):
                return True
                
            if (category_str in self.weapon_proficiency_groups["martial"] and
                any("martial weapons" in p.lower() for p in proficiencies)):
                return True
                
            # Check for all weapons proficiency
            if any(p.lower() in ["all weapons", "weapon master"] for p in proficiencies):
                return True
        
        return False
    
    def calculate_weapon_critical(self, weapon_id: str) -> Dict[str, Any]:
        """
        Get critical hit information for a weapon.
        
        Args:
            weapon_id: ID of the weapon
            
        Returns:
            Dict[str, Any]: Critical hit details
        """
        weapon_data = self._find_item_by_id(weapon_id)
        if not weapon_data:
            return {"error": "Weapon not found"}
        
        # Default critical values
        crit_range = 20
        crit_multiplier = 2
        
        # Check for special properties
        properties = [p.lower() for p in weapon_data.get("properties", [])]
        
        # Special cases for certain weapons (like Champion fighter features would be handled elsewhere)
        if "keen" in properties:
            crit_range = 19
        
        return {
            "weapon_name": weapon_data.get("name"),
            "critical_range": crit_range,  # Critical hit on this number or higher
            "critical_multiplier": crit_multiplier,  # Multiply dice by this amount on crit
            "description": f"Critical hit on a roll of {crit_range}-20"
        }
    
    def create_custom_weapon(self, 
                           name: str,
                           damage_dice: str, 
                           damage_type: DamageType,
                           category: WeaponCategory = WeaponCategory.MARTIAL_MELEE,
                           properties: List[str] = None,
                           weight: float = 3.0,
                           cost: Dict[str, int] = None,
                           description: str = None,
                           is_magical: bool = False,
                           rarity: RarityType = None) -> Dict[str, Any]:
        """
        Create a custom weapon with specified attributes.
        
        Args:
            name: Name of the weapon
            damage_dice: Damage dice (e.g. "1d8")
            damage_type: Type of damage dealt
            category: Weapon category
            properties: List of weapon properties
            weight: Weight in pounds
            cost: Cost in currency values
            description: Description of the weapon
            is_magical: Whether the weapon is magical
            rarity: Rarity if magical
            
        Returns:
            Dict[str, Any]: Created weapon data
        """
        # Generate a weapon description if none provided
        if description is None:
            description = f"A custom {category.value.replace('_', ' ')} weapon that deals {damage_dice} {damage_type.value} damage."
        
        # Set default properties based on category if none provided
        if properties is None:
            properties = self.common_properties.get(category, [])
        
        # Set default cost if none provided
        if cost is None:
            if category in [WeaponCategory.SIMPLE_MELEE, WeaponCategory.SIMPLE_RANGED]:
                cost = {"gp": 5}
            else:
                cost = {"gp": 25}
        
        # Create the weapon data
        weapon_data = {
            "id": f"custom_{name.lower().replace(' ', '_')}",
            "name": name,
            "category": category,
            "damage_dice": damage_dice,
            "damage_type": damage_type,
            "properties": properties,
            "weight": weight,
            "cost": cost,
            "description": description,
            "is_magical": is_magical
        }
        
        # Add rarity if magical
        if is_magical and rarity:
            weapon_data["rarity"] = rarity
        
        # Add to weapons collection
        self.weapons[weapon_data["id"]] = weapon_data
        
        # If magical, also add to magic items
        if is_magical:
            self.magic_items[weapon_data["id"]] = weapon_data
        
        return weapon_data
    
    def enhance_weapon_with_llm(self, 
                             weapon_id: str, 
                             enhancement_type: str = "tactical", 
                             character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance a weapon with LLM-generated content.
        
        Args:
            weapon_id: ID of the weapon to enhance
            enhancement_type: Type of enhancement (tactical, narrative, creative)
            character_data: Optional character data for contextual enhancements
            
        Returns:
            Dict[str, Any]: Enhanced weapon data
        """
        weapon_data = self._find_item_by_id(weapon_id)
        if not weapon_data:
            return {"error": "Weapon not found"}
            
        # Create a copy to avoid modifying the original
        enhanced_weapon = weapon_data.copy()
        
        if enhancement_type.lower() == "tactical":
            # Generate tactical analysis
            if character_data:
                ability_scores = character_data.get("ability_scores", {})
                proficiency_bonus = character_data.get("proficiency_bonus", 2)
                tactical_analysis = self.llm_advisor.generate_tactical_analysis(
                    weapon_data, ability_scores, proficiency_bonus
                )
                enhanced_weapon["tactical_analysis"] = tactical_analysis
            else:
                enhanced_weapon["tactical_analysis"] = {
                    "note": "Provide character data for personalized tactical analysis"
                }
                
        elif enhancement_type.lower() == "narrative":
            # Generate narrative description
            narrative = self.llm_advisor.generate_equipment_story(
                weapon_data.get("name", ""), 
                character_data or {}
            )
            enhanced_weapon["narrative"] = narrative
            
        elif enhancement_type.lower() == "creative":
            # Generate creative uses
            creative_uses = self.llm_advisor.generate_creative_uses(
                weapon_data.get("name", ""),
                weapon_data.get("description", "")
            )
            enhanced_weapon["creative_uses"] = creative_uses
            
        return enhanced_weapon
    
    def suggest_weapon_upgrades(self, 
                             weapon_id: str, 
                             character_level: int,
                             upgrade_theme: str = None) -> Dict[str, Any]:
        """
        Generate suggested upgrades for a weapon based on character level.
        
        Args:
            weapon_id: ID of the weapon to upgrade
            character_level: Character level for appropriate scaling
            upgrade_theme: Optional theme for the upgrade
            
        Returns:
            Dict[str, Any]: Upgrade suggestions
        """
        weapon_data = self._find_item_by_id(weapon_id)
        if not weapon_data:
            return {"error": "Weapon not found"}
        
        # Generate upgrade suggestions
        upgrades = self.llm_advisor.suggest_equipment_upgrade(
            weapon_data, character_level, upgrade_theme
        )
        
        return {
            "original_weapon": weapon_data.get("name"),
            "character_level": character_level,
            "upgrade_suggestions": upgrades
        }
    
    def analyze_weapon_synergies(self, 
                              weapon_id: str, 
                              character_build: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze how well a weapon synergizes with character abilities, feats, and class features.
        
        Args:
            weapon_id: ID of the weapon to analyze
            character_build: Character build details including class features and feats
            
        Returns:
            Dict[str, Any]: Synergy analysis
        """
        weapon_data = self._find_item_by_id(weapon_id)
        if not weapon_data:
            return {"error": "Weapon not found"}
        
        # Extract relevant character information
        class_name = character_build.get("class", {}).get("name", "Unknown")
        subclass = character_build.get("class", {}).get("subclass", "Unknown")
        feats = character_build.get("feats", [])
        features = character_build.get("features", [])
        fighting_style = next((f for f in features if "fighting style" in f.lower()), None)
        
        # Prepare prompt context for LLM
        context = (
            f"Weapon: {weapon_data.get('name')}\n"
            f"Damage: {weapon_data.get('damage_dice')} {weapon_data.get('damage_type').value if isinstance(weapon_data.get('damage_type'), DamageType) else ''}\n"
            f"Properties: {', '.join(weapon_data.get('properties', []))}\n\n"
            f"Character Class: {class_name}\n"
            f"Subclass: {subclass}\n"
            f"Fighting Style: {fighting_style or 'None'}\n"
            f"Feats: {', '.join(feats)}\n"
        )
        
        # Custom prompt for weapon synergies
        prompt = self.llm_advisor._create_prompt(
            "analyze weapon synergies with this character build",
            context + "\n"
            "Analyze how well this weapon synergizes with the character's class features, fighting style, "
            "and feats. Identify strong mechanical interactions, thematic fits, and possible drawbacks. "
            "Return as JSON with 'synergy_rating', 'synergy_elements', 'drawbacks', and 'optimization_tips' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            analysis = self.llm_advisor._extract_json(response)
            
            if analysis:
                analysis["weapon_name"] = weapon_data.get("name")
                return analysis
        except Exception as e:
            print(f"Error analyzing weapon synergies: {e}")
        
        # Fallback response
        return {
            "weapon_name": weapon_data.get("name"),
            "synergy_rating": "Medium",
            "synergy_elements": ["Basic weapon compatibility"],
            "drawbacks": ["No specific analysis available"],
            "optimization_tips": ["Consider your character's abilities when choosing weapons"]
        }
    
    def calculate_average_damage(self, 
                              weapon_id: str, 
                              ability_scores: Dict[str, int],
                              critical_chance: float = 0.05) -> Dict[str, Any]:
        """
        Calculate average damage per round with a weapon.
        
        Args:
            weapon_id: ID of the weapon
            ability_scores: Character ability scores
            critical_chance: Chance of critical hit (default 5%)
            
        Returns:
            Dict[str, Any]: Average damage calculations
        """
        weapon_data = self._find_item_by_id(weapon_id)
        if not weapon_data:
            return {"error": "Weapon not found"}
        
        damage_dice = weapon_data.get("damage_dice", "1d8")
        
        # Parse dice notation (e.g., "2d6+1")
        dice_match = re.match(r"(\d+)d(\d+)(?:\+(\d+))?", damage_dice)
        if not dice_match:
            return {"error": "Invalid damage dice format"}
        
        num_dice = int(dice_match.group(1))
        die_size = int(dice_match.group(2))
        fixed_bonus = int(dice_match.group(3)) if dice_match.group(3) else 0
        
        # Calculate ability modifier
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
        
        # Calculate average damage
        average_die_result = (die_size + 1) / 2
        average_dice_damage = num_dice * average_die_result
        average_hit_damage = average_dice_damage + fixed_bonus + ability_mod
        
        # Calculate critical hit average damage
        crit_dice_damage = num_dice * 2 * average_die_result
        crit_damage = crit_dice_damage + fixed_bonus + ability_mod
        
        # Combine for expected damage per hit (accounting for crit chance)
        expected_damage = average_hit_damage * (1 - critical_chance) + crit_damage * critical_chance
        
        return {
            "weapon_name": weapon_data.get("name"),
            "ability_used": ability_used,
            "ability_modifier": ability_mod,
            "average_damage_per_hit": round(average_hit_damage, 2),
            "critical_damage": round(crit_damage, 2),
            "expected_damage_per_hit": round(expected_damage, 2)
        }
    
    def compare_weapons(self, 
                      weapon_id_1: str, 
                      weapon_id_2: str,
                      character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Compare two weapons for a specific character.
        
        Args:
            weapon_id_1: First weapon ID
            weapon_id_2: Second weapon ID
            character_data: Character data for context
            
        Returns:
            Dict[str, Any]: Weapon comparison
        """
        weapon1 = self._find_item_by_id(weapon_id_1)
        weapon2 = self._find_item_by_id(weapon_id_2)
        
        if not weapon1 or not weapon2:
            return {"error": "One or both weapons not found"}
        
        return self.llm_advisor.compare_equipment(weapon1, weapon2, character_data)
    
    def generate_weapon_appearance(self, weapon_id: str, style: str = None) -> str:
        """
        Generate a detailed visual description of a weapon.
        
        Args:
            weapon_id: ID of the weapon
            style: Optional style direction (e.g., "ornate", "weathered", "elven")
            
        Returns:
            str: Detailed appearance description
        """
        weapon_data = self._find_item_by_id(weapon_id)
        if not weapon_data:
            return "Weapon not found"
        
        context = f"Weapon: {weapon_data.get('name')}\n"
        context += f"Type: {weapon_data.get('category').value if isinstance(weapon_data.get('category'), WeaponCategory) else 'unknown'}\n"
        context += f"Material: {weapon_data.get('material', 'steel')}\n"
        
        if style:
            context += f"Style Direction: {style}\n"
            
        prompt = self.llm_advisor._create_prompt(
            "describe the physical appearance of this weapon",
            context + "\n"
            "Create a vivid, detailed description of this weapon's physical appearance. "
            "Include details about its craftsmanship, materials, distinctive features, "
            "and overall aesthetic. The description should help a player visualize the "
            "weapon in their character's hands."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            
            # Clean up the response by removing any JSON formatting
            clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
            clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
            
            return clean_response.strip()
        except Exception as e:
            print(f"Error generating weapon appearance: {e}")
            
        # Fallback description
        return f"A well-crafted {weapon_data.get('name')} with standard design elements."