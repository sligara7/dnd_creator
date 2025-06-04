# armor.py
# Description: Handles armor equipment and defensive calculations

from typing import Dict, List, Optional, Union, Any, Tuple
import json
import re
from enum import Enum

from backend.core.equipment.equipment import Equipment, ArmorCategory, RarityType

class ArmorMaterial(Enum):
    """Materials that armor can be made of"""
    CLOTH = "cloth"
    LEATHER = "leather"
    HIDE = "hide"
    CHAIN = "chain"
    SCALE = "scale"
    PLATE = "plate"
    WOOD = "wood"
    SPECIAL = "special"  # For exotic or magical materials

class ArmorProperty(Enum):
    """Special properties that armor can have"""
    BULKY = "bulky"  # Restricts movement
    FLEXIBLE = "flexible"  # Greater freedom of movement
    NOISY = "noisy"  # Makes noise when moving
    FITTED = "fitted"  # Tailored to wearer
    FIREPROOF = "fireproof"  # Resistant to fire
    MAGICAL = "magical"  # Has magical properties
    REINFORCED = "reinforced"  # Extra protection at vital areas
    LIGHTWEIGHT = "lightweight"  # Lighter than normal for its type
    SPIKED = "spiked"  # Has damaging spikes or barbs
    ORNATE = "ornate"  # Decorative and possibly prestigious

class Armor(Equipment):
    """
    Class for handling armor equipment, defensive calculations, and customization.
    
    Extends the Equipment class with armor-specific functionality for creating,
    customizing, and analyzing protective gear for character builds.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the armor manager with parent equipment functionality."""
        super().__init__(llm_service)
        
        # Additional armor configuration
        self.armor_proficiency_groups = {
            "light": set([ArmorCategory.LIGHT.value]),
            "medium": set([ArmorCategory.MEDIUM.value]),
            "heavy": set([ArmorCategory.HEAVY.value]),
            "shield": set([ArmorCategory.SHIELD.value])
        }
        
        # Typical AC ranges by armor category for validation
        self.typical_ac_ranges = {
            ArmorCategory.LIGHT: (11, 12),  # (min, max)
            ArmorCategory.MEDIUM: (12, 15),
            ArmorCategory.HEAVY: (14, 18),
            ArmorCategory.SHIELD: (2, 3)  # Bonus AC rather than base
        }
        
        # Typical dex bonus limitations by category
        self.dex_bonus_rules = {
            ArmorCategory.LIGHT: {"allowed": True, "max_bonus": None},
            ArmorCategory.MEDIUM: {"allowed": True, "max_bonus": 2},
            ArmorCategory.HEAVY: {"allowed": False, "max_bonus": 0},
            ArmorCategory.SHIELD: {"allowed": False, "max_bonus": 0}  # Shields don't apply dex bonus directly
        }
    
    def get_armor_by_category(self, category: Union[ArmorCategory, str]) -> List[Dict[str, Any]]:
        """
        Get armor filtered by category.
        
        Args:
            category: Category to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of armor in the category
        """
        if isinstance(category, str):
            # Try to convert string to enum
            try:
                category = ArmorCategory(category.lower())
            except ValueError:
                # If not a valid category, return empty list
                return []
        
        return [a for a in self.armor.values() if a["category"] == category]
    
    def get_armor_by_property(self, property_name: Union[ArmorProperty, str]) -> List[Dict[str, Any]]:
        """
        Get armor that has a specific property.
        
        Args:
            property_name: Property to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of armor with the property
        """
        property_str = property_name.value if isinstance(property_name, ArmorProperty) else str(property_name).lower()
        
        return [
            a for a in self.armor.values() 
            if "properties" in a and any(property_str in prop.lower() for prop in a["properties"])
        ]
    
    def get_armor_by_material(self, material: Union[ArmorMaterial, str]) -> List[Dict[str, Any]]:
        """
        Get armor made of a specific material.
        
        Args:
            material: Material to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of armor with the material
        """
        material_str = material.value if isinstance(material, ArmorMaterial) else str(material).lower()
        
        return [
            a for a in self.armor.values() 
            if "material" in a and (
                (isinstance(a["material"], ArmorMaterial) and a["material"].value == material_str) or
                (isinstance(a["material"], str) and a["material"].lower() == material_str)
            )
        ]
    
    def check_armor_proficiency(self, character_data: Dict[str, Any], armor_id: str) -> bool:
        """
        Check if a character is proficient with a specific armor.
        
        Args:
            character_data: Character data including proficiencies
            armor_id: ID of the armor to check
            
        Returns:
            bool: True if proficient, False otherwise
        """
        armor_data = self._find_item_by_id(armor_id)
        if not armor_data:
            return False
        
        # Get character proficiencies
        proficiencies = character_data.get("proficiencies", {}).get("armor", [])
        if not proficiencies:
            return False
        
        # Check for armor name in specific proficiencies
        if armor_data.get("name", "").lower() in [p.lower() for p in proficiencies]:
            return True
        
        # Check for armor category in group proficiencies
        if "category" in armor_data:
            category = armor_data["category"]
            category_str = category.value if isinstance(category, ArmorCategory) else str(category)
            
            # Check specific armor type proficiencies
            if category_str in self.armor_proficiency_groups["light"] and "light armor" in [p.lower() for p in proficiencies]:
                return True
                
            if category_str in self.armor_proficiency_groups["medium"] and "medium armor" in [p.lower() for p in proficiencies]:
                return True
                
            if category_str in self.armor_proficiency_groups["heavy"] and "heavy armor" in [p.lower() for p in proficiencies]:
                return True
                
            if category_str in self.armor_proficiency_groups["shield"] and "shields" in [p.lower() for p in proficiencies]:
                return True
                
            # Check for all armor proficiency
            if "all armor" in [p.lower() for p in proficiencies]:
                return True
        
        return False
    
    def analyze_mobility_impact(self, armor_id: str, dexterity_score: int = 10) -> Dict[str, Any]:
        """
        Analyze how armor affects mobility and stealth.
        
        Args:
            armor_id: ID of the armor
            dexterity_score: Character's dexterity score
            
        Returns:
            Dict[str, Any]: Mobility impact analysis
        """
        armor_data = self._find_item_by_id(armor_id)
        if not armor_data:
            return {"error": "Armor not found"}
        
        # Extract armor properties
        stealth_disadvantage = armor_data.get("stealth_disadvantage", False)
        speed_reduction = armor_data.get("speed_reduction", 0)
        str_required = armor_data.get("strength_required", 0)
        
        # Calculate mobility rating (0-10 scale)
        base_mobility = 10
        
        # Adjust for armor category
        category = armor_data.get("category")
        if category == ArmorCategory.LIGHT:
            base_mobility -= 1
        elif category == ArmorCategory.MEDIUM:
            base_mobility -= 2
        elif category == ArmorCategory.HEAVY:
            base_mobility -= 3
        
        # Adjust for stealth disadvantage
        if stealth_disadvantage:
            base_mobility -= 2
        
        # Adjust for speed reduction
        base_mobility -= speed_reduction // 5
        
        # Dexterity can mitigate some mobility issues for lighter armor
        dex_mod = (dexterity_score - 10) // 2
        if category == ArmorCategory.LIGHT:
            base_mobility += min(dex_mod, 2)
        elif category == ArmorCategory.MEDIUM:
            base_mobility += min(dex_mod, 1)
        
        # Ensure mobility stays in range
        mobility_rating = max(1, min(10, base_mobility))
        
        return {
            "armor_name": armor_data.get("name"),
            "mobility_rating": mobility_rating,  # 1-10 scale (10 being most mobile)
            "stealth_impact": "disadvantage" if stealth_disadvantage else "none",
            "speed_reduction": f"-{speed_reduction} ft." if speed_reduction > 0 else "none",
            "recommended_dexterity": "high" if category in [ArmorCategory.LIGHT, ArmorCategory.MEDIUM] else "any"
        }
    
    def create_custom_armor(self, 
                          name: str,
                          category: ArmorCategory,
                          base_ac: int,
                          material: ArmorMaterial = None,
                          dex_bonus_allowed: bool = None,
                          max_dex_bonus: int = None,
                          strength_required: int = 0,
                          stealth_disadvantage: bool = None,
                          properties: List[str] = None,
                          weight: float = None,
                          cost: Dict[str, int] = None,
                          description: str = None,
                          is_magical: bool = False,
                          rarity: RarityType = None) -> Dict[str, Any]:
        """
        Create a custom armor with specified attributes.
        
        Args:
            name: Name of the armor
            category: Armor category
            base_ac: Base armor class value
            material: Material of the armor
            dex_bonus_allowed: Whether dexterity bonus applies
            max_dex_bonus: Maximum dexterity bonus allowed
            strength_required: Minimum strength score required
            stealth_disadvantage: Whether armor gives stealth disadvantage
            properties: List of armor properties
            weight: Weight in pounds
            cost: Cost in currency values
            description: Description of the armor
            is_magical: Whether the armor is magical
            rarity: Rarity if magical
            
        Returns:
            Dict[str, Any]: Created armor data
        """
        # Set defaults based on category if not specified
        if dex_bonus_allowed is None:
            dex_bonus_allowed = self.dex_bonus_rules[category]["allowed"]
            
        if max_dex_bonus is None:
            max_dex_bonus = self.dex_bonus_rules[category]["max_bonus"]
        
        # Default stealth disadvantage based on category
        if stealth_disadvantage is None:
            stealth_disadvantage = (category == ArmorCategory.HEAVY or 
                                  (category == ArmorCategory.MEDIUM and "stealthy" not in (properties or [])))
        
        # Set default weight based on category
        if weight is None:
            if category == ArmorCategory.LIGHT:
                weight = 10.0
            elif category == ArmorCategory.MEDIUM:
                weight = 20.0
            elif category == ArmorCategory.HEAVY:
                weight = 50.0
            elif category == ArmorCategory.SHIELD:
                weight = 6.0
                
        # Set default properties
        if properties is None:
            properties = []
            
        # Add material if specified
        if material and isinstance(material, ArmorMaterial):
            material_str = material.value
        elif material:
            material_str = str(material)
        else:
            # Default material by category
            if category == ArmorCategory.LIGHT:
                material_str = ArmorMaterial.LEATHER.value
            elif category == ArmorCategory.MEDIUM:
                material_str = ArmorMaterial.CHAIN.value
            elif category == ArmorCategory.HEAVY:
                material_str = ArmorMaterial.PLATE.value
            elif category == ArmorCategory.SHIELD:
                material_str = ArmorMaterial.WOOD.value
        
        # Set default cost based on category
        if cost is None:
            if category == ArmorCategory.LIGHT:
                cost = {"gp": 10}
            elif category == ArmorCategory.MEDIUM:
                cost = {"gp": 50}
            elif category == ArmorCategory.HEAVY:
                cost = {"gp": 200}
            elif category == ArmorCategory.SHIELD:
                cost = {"gp": 10}
        
        # Generate a description if none provided
        if description is None:
            if category == ArmorCategory.SHIELD:
                description = f"A custom {material_str} shield that provides +{base_ac} AC."
            else:
                dex_text = ""
                if dex_bonus_allowed:
                    if max_dex_bonus is not None:
                        dex_text = f" It allows adding your Dexterity modifier (max {max_dex_bonus}) to your AC."
                    else:
                        dex_text = " It allows adding your full Dexterity modifier to your AC."
                
                description = f"A custom {material_str} {category.value} armor with a base AC of {base_ac}.{dex_text}"
        
        # Create the armor data
        armor_data = {
            "id": f"custom_{name.lower().replace(' ', '_')}",
            "name": name,
            "category": category,
            "base_ac": base_ac,
            "material": material_str,
            "dex_bonus_allowed": dex_bonus_allowed,
            "max_dex_bonus": max_dex_bonus if dex_bonus_allowed else None,
            "strength_required": strength_required,
            "stealth_disadvantage": stealth_disadvantage,
            "properties": properties,
            "weight": weight,
            "cost": cost,
            "description": description,
            "is_magical": is_magical
        }
        
        # Add rarity if magical
        if is_magical and rarity:
            armor_data["rarity"] = rarity
        
        # Add to armor collection
        self.armor[armor_data["id"]] = armor_data
        
        # If magical, also add to magic items
        if is_magical:
            self.magic_items[armor_data["id"]] = armor_data
        
        return armor_data
    
    def enhance_armor_with_llm(self, 
                             armor_id: str, 
                             enhancement_type: str = "defensive", 
                             character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance armor with LLM-generated content.
        
        Args:
            armor_id: ID of the armor to enhance
            enhancement_type: Type of enhancement (defensive, narrative, aesthetic)
            character_data: Optional character data for contextual enhancements
            
        Returns:
            Dict[str, Any]: Enhanced armor data
        """
        armor_data = self._find_item_by_id(armor_id)
        if not armor_data:
            return {"error": "Armor not found"}
            
        # Create a copy to avoid modifying the original
        enhanced_armor = armor_data.copy()
        
        if enhancement_type.lower() == "defensive":
            # Generate defensive analysis
            if character_data:
                dexterity_modifier = (character_data.get("ability_scores", {}).get("dexterity", 10) - 10) // 2
                defensive_analysis = self.llm_advisor.generate_defensive_analysis(
                    armor_data, dexterity_modifier
                )
                enhanced_armor["defensive_analysis"] = defensive_analysis
            else:
                enhanced_armor["defensive_analysis"] = {
                    "note": "Provide character data for personalized defensive analysis"
                }
                
        elif enhancement_type.lower() == "narrative":
            # Generate narrative description
            narrative = self.llm_advisor.generate_equipment_story(
                armor_data.get("name", ""), 
                character_data or {}
            )
            enhanced_armor["narrative"] = narrative
            
        elif enhancement_type.lower() == "aesthetic":
            # Generate appearance description
            prompt = self.llm_advisor._create_prompt(
                "describe the physical appearance of this armor",
                f"Armor: {armor_data.get('name')}\n"
                f"Type: {armor_data.get('category').value if isinstance(armor_data.get('category'), ArmorCategory) else 'unknown'}\n"
                f"Material: {armor_data.get('material', 'metal')}\n\n"
                "Create a vivid, detailed description of this armor's physical appearance. "
                "Include details about its craftsmanship, materials, distinctive features, "
                "and overall aesthetic. The description should help a player visualize the "
                "armor when their character wears it."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                
                # Clean up the response
                clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
                clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
                
                enhanced_armor["appearance_description"] = clean_response.strip()
            except Exception as e:
                print(f"Error generating armor appearance: {e}")
                enhanced_armor["appearance_description"] = f"A well-crafted {armor_data.get('name')}."
            
        return enhanced_armor
    
    def suggest_armor_upgrades(self, 
                            armor_id: str, 
                            character_level: int,
                            upgrade_theme: str = None) -> Dict[str, Any]:
        """
        Generate suggested upgrades for armor based on character level.
        
        Args:
            armor_id: ID of the armor to upgrade
            character_level: Character level for appropriate scaling
            upgrade_theme: Optional theme for the upgrade
            
        Returns:
            Dict[str, Any]: Upgrade suggestions
        """
        armor_data = self._find_item_by_id(armor_id)
        if not armor_data:
            return {"error": "Armor not found"}
        
        # Generate upgrade suggestions
        upgrades = self.llm_advisor.suggest_equipment_upgrade(
            armor_data, character_level, upgrade_theme
        )
        
        return {
            "original_armor": armor_data.get("name"),
            "character_level": character_level,
            "upgrade_suggestions": upgrades
        }
    
    def analyze_armor_synergies(self, 
                             armor_id: str, 
                             character_build: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze how well armor synergizes with character class features and abilities.
        
        Args:
            armor_id: ID of the armor to analyze
            character_build: Character build details including class features
            
        Returns:
            Dict[str, Any]: Synergy analysis
        """
        armor_data = self._find_item_by_id(armor_id)
        if not armor_data:
            return {"error": "Armor not found"}
        
        # Extract relevant character information
        class_name = character_build.get("class", {}).get("name", "Unknown")
        subclass = character_build.get("class", {}).get("subclass", "Unknown")
        features = character_build.get("features", [])
        ability_scores = character_build.get("ability_scores", {})
        dexterity = ability_scores.get("dexterity", 10)
        strength = ability_scores.get("strength", 10)
        
        # Prepare prompt context for LLM
        context = (
            f"Armor: {armor_data.get('name')}\n"
            f"Type: {armor_data.get('category').value if isinstance(armor_data.get('category'), ArmorCategory) else 'unknown'}\n"
            f"Base AC: {armor_data.get('base_ac')}\n"
            f"Dexterity Bonus Allowed: {armor_data.get('dex_bonus_allowed', True)}\n"
            f"Stealth Disadvantage: {armor_data.get('stealth_disadvantage', False)}\n\n"
            f"Character Class: {class_name}\n"
            f"Subclass: {subclass}\n"
            f"Strength Score: {strength}\n"
            f"Dexterity Score: {dexterity}\n"
            f"Class Features: {', '.join(features[:5])}\n"
        )
        
        # Custom prompt for armor synergies
        prompt = self.llm_advisor._create_prompt(
            "analyze armor synergies with this character build",
            context + "\n"
            "Analyze how well this armor synergizes with the character's class features, ability scores, "
            "and playstyle. Identify strong mechanical interactions, potential drawbacks, and overall fit. "
            "Return as JSON with 'synergy_rating', 'synergy_elements', 'drawbacks', and 'optimization_tips' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            analysis = self.llm_advisor._extract_json(response)
            
            if analysis:
                analysis["armor_name"] = armor_data.get("name")
                return analysis
        except Exception as e:
            print(f"Error analyzing armor synergies: {e}")
        
        # Fallback response
        return {
            "armor_name": armor_data.get("name"),
            "synergy_rating": "Medium",
            "synergy_elements": ["Basic armor compatibility"],
            "drawbacks": ["No specific analysis available"],
            "optimization_tips": ["Consider your class features when selecting armor"]
        }
    
    def calculate_total_ac(self, armor_id: str, 
                         dexterity_modifier: int,
                         shield_id: str = None,
                         bonuses: Dict[str, int] = None) -> Dict[str, Any]:
        """
        Calculate total AC with armor, shield, and other bonuses.
        
        Args:
            armor_id: ID of the armor
            dexterity_modifier: Character's dexterity modifier
            shield_id: Optional ID of shield being used
            bonuses: Optional dictionary of other AC bonuses by source
            
        Returns:
            Dict[str, Any]: Total AC calculation results
        """
        armor_data = self._find_item_by_id(armor_id)
        if not armor_data:
            return {"error": "Armor not found"}
        
        # Calculate armor AC
        base_ac = armor_data.get("base_ac", 10)
        dex_bonus_allowed = armor_data.get("dex_bonus_allowed", True)
        max_dex_bonus = armor_data.get("max_dex_bonus")
        
        applied_dex_mod = 0
        if dex_bonus_allowed:
            if max_dex_bonus is not None:
                applied_dex_mod = min(dexterity_modifier, max_dex_bonus)
            else:
                applied_dex_mod = dexterity_modifier
        
        armor_ac = base_ac + applied_dex_mod
        
        # Calculate shield AC if applicable
        shield_ac = 0
        shield_info = None
        
        if shield_id:
            shield_data = self._find_item_by_id(shield_id)
            if shield_data and "category" in shield_data and shield_data["category"] == ArmorCategory.SHIELD:
                shield_ac = shield_data.get("base_ac", 2)
                shield_info = {
                    "name": shield_data.get("name"),
                    "ac_bonus": shield_ac
                }
        
        # Add other bonuses
        other_bonuses = 0
        bonus_breakdown = []
        
        if bonuses:
            for source, value in bonuses.items():
                other_bonuses += value
                bonus_breakdown.append({"source": source, "value": value})
        
        # Calculate total AC
        total_ac = armor_ac + shield_ac + other_bonuses
        
        return {
            "armor_name": armor_data.get("name"),
            "armor_category": armor_data.get("category").value if isinstance(armor_data.get("category"), ArmorCategory) else "unknown",
            "base_ac": base_ac,
            "dexterity_modifier": dexterity_modifier,
            "applied_dex_modifier": applied_dex_mod,
            "armor_ac": armor_ac,
            "shield": shield_info,
            "other_bonuses": bonus_breakdown,
            "total_ac": total_ac,
            "stealth_disadvantage": armor_data.get("stealth_disadvantage", False),
            "strength_requirement_met": True  # This would normally check against character strength
        }
    
    def compare_armor_options(self, 
                           armor_id_1: str, 
                           armor_id_2: str,
                           character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Compare two armor options for a specific character.
        
        Args:
            armor_id_1: First armor ID
            armor_id_2: Second armor ID
            character_data: Character data for context
            
        Returns:
            Dict[str, Any]: Armor comparison
        """
        armor1 = self._find_item_by_id(armor_id_1)
        armor2 = self._find_item_by_id(armor_id_2)
        
        if not armor1 or not armor2:
            return {"error": "One or both armor pieces not found"}
        
        # Extract character data for comparison
        dexterity_mod = 0
        if character_data:
            dexterity_mod = (character_data.get("ability_scores", {}).get("dexterity", 10) - 10) // 2
        
        # Calculate AC with each armor
        ac1 = self.calculate_armor_class(armor_id_1, dexterity_mod)
        ac2 = self.calculate_armor_class(armor_id_2, dexterity_mod)
        
        # Compare mobility impact
        mobility1 = self.analyze_mobility_impact(armor_id_1)
        mobility2 = self.analyze_mobility_impact(armor_id_2)
        
        # Generate detailed comparison with LLM
        comparison = self.llm_advisor.compare_equipment(armor1, armor2, character_data)
        
        # Combine all information
        return {
            "armor_comparison": {
                "armor1": {
                    "name": armor1.get("name"),
                    "ac_calculation": ac1,
                    "mobility_impact": mobility1
                },
                "armor2": {
                    "name": armor2.get("name"),
                    "ac_calculation": ac2,
                    "mobility_impact": mobility2
                }
            },
            "ac_difference": ac1.get("total_ac", 0) - ac2.get("total_ac", 0),
            "mobility_difference": mobility1.get("mobility_rating", 5) - mobility2.get("mobility_rating", 5),
            "llm_analysis": comparison
        }
    
    def generate_armor_appearance(self, armor_id: str, style: str = None) -> str:
        """
        Generate a detailed visual description of armor.
        
        Args:
            armor_id: ID of the armor
            style: Optional style direction (e.g., "ornate", "weathered", "elven")
            
        Returns:
            str: Detailed appearance description
        """
        armor_data = self._find_item_by_id(armor_id)
        if not armor_data:
            return "Armor not found"
        
        context = f"Armor: {armor_data.get('name')}\n"
        context += f"Type: {armor_data.get('category').value if isinstance(armor_data.get('category'), ArmorCategory) else 'unknown'}\n"
        context += f"Material: {armor_data.get('material', 'metal')}\n"
        
        if style:
            context += f"Style Direction: {style}\n"
            
        prompt = self.llm_advisor._create_prompt(
            "describe the physical appearance of this armor",
            context + "\n"
            "Create a vivid, detailed description of this armor's physical appearance. "
            "Include details about its craftsmanship, materials, distinctive features, "
            "decorations, fastenings, and overall aesthetic. The description should help a player "
            "visualize what their character looks like when wearing this armor."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            
            # Clean up the response by removing any JSON formatting
            clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
            clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
            
            return clean_response.strip()
        except Exception as e:
            print(f"Error generating armor appearance: {e}")
            
        # Fallback description
        return f"A well-crafted {armor_data.get('name')} with standard design elements."