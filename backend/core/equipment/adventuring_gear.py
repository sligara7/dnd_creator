# adventuring_gear.py
# Description: Handles adventuring gear for exploration, survival and utility

from typing import Dict, List, Optional, Union, Any, Tuple
import json
import re
from enum import Enum

from backend.core.equipment.equipment import Equipment, EquipmentCategory, RarityType

class GearCategory(Enum):
    """Categories of adventuring gear"""
    CONTAINER = "container"  # Backpacks, pouches, etc.
    LIGHT_SOURCE = "light_source"  # Torches, lanterns, etc.
    TOOL = "tool"  # Non-proficiency tools like crowbars
    SURVIVAL = "survival"  # Rations, waterskins, etc.
    CLIMBING = "climbing"  # Ropes, pitons, etc.
    NAVIGATION = "navigation"  # Maps, compasses, etc.
    UTILITY = "utility"  # Miscellaneous useful items
    HOLY_SYMBOL = "holy_symbol"  # Religious items
    ARCANE_FOCUS = "arcane_focus"  # Spellcasting foci
    MUSICAL = "musical"  # Musical instruments
    GAMING = "gaming"  # Games and entertainment
    COMMUNICATION = "communication"  # Writing supplies, etc.
    CLOTHING = "clothing"  # Special clothing items
    HEALER = "healer"  # Healing supplies
    SPECIALTY = "specialty"  # Special-purpose gear

class GearProperty(Enum):
    """Special properties that gear can have"""
    CONSUMABLE = "consumable"  # Used up when used
    REUSABLE = "reusable"  # Can be used multiple times
    FRAGILE = "fragile"  # Can break easily
    DURABLE = "durable"  # Particularly hard to break
    FLAMMABLE = "flammable"  # Can catch fire
    WATERPROOF = "waterproof"  # Resistant to water damage
    BULKY = "bulky"  # Difficult to carry or store
    COMPACT = "compact"  # Easy to carry or store
    NOISY = "noisy"  # Makes noise when used
    QUIET = "quiet"  # Particularly quiet when used
    ILLUMINATING = "illuminating"  # Produces light
    SPECIALIZED = "specialized"  # Has a specialized purpose

class AdventuringGear(Equipment):
    """
    Class for handling adventuring gear, exploration equipment, and utility items.
    
    Extends the Equipment class with gear-specific functionality for creating,
    customizing, and analyzing utility items for adventures.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the adventuring gear manager with parent equipment functionality."""
        super().__init__(llm_service)
        
        # Additional gear configuration
        self.environment_gear_mapping = {
            "arctic": ["blanket", "winter_clothes", "snowshoes", "fishing_tackle"],
            "desert": ["waterskin", "desert_clothes", "parasol", "sand_goggles"],
            "forest": ["herbalism_kit", "animal_trap", "insect_repellent", "climbing_gear"],
            "mountain": ["climbing_kit", "warm_clothes", "crampons", "altitude_tent"],
            "ocean": ["fishing_tackle", "sea_chart", "navigation_tools", "waterproof_bag"],
            "swamp": ["mud_boots", "insect_repellent", "ten_foot_pole", "water_purifier"],
            "underdark": ["extra_light_sources", "chalk", "rope", "mirror"],
            "urban": ["disguise_kit", "forgery_kit", "thieves_tools", "fine_clothes"]
        }
        
        # Common durations for consumable items
        self.common_durations = {
            "torch": "1 hour",
            "lantern_oil": "6 hours",
            "rations": "1 day",
            "waterskin": "1 day",
            "antitoxin": "immediate",
            "healer_kit_use": "immediate",
            "potion": "immediate"
        }
    
    def get_gear_by_category(self, category: Union[GearCategory, str]) -> List[Dict[str, Any]]:
        """
        Get adventuring gear filtered by category.
        
        Args:
            category: Category to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of gear in the category
        """
        if isinstance(category, str):
            # Try to convert string to enum
            try:
                category = GearCategory(category.lower())
            except ValueError:
                # If not a valid category, return empty list
                return []
        
        return [
            g for g in self.gear.values() 
            if "gear_category" in g and g["gear_category"] == category
        ]
    
    def get_gear_by_property(self, property_name: Union[GearProperty, str]) -> List[Dict[str, Any]]:
        """
        Get gear that has a specific property.
        
        Args:
            property_name: Property to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of gear with the property
        """
        property_str = property_name.value if isinstance(property_name, GearProperty) else str(property_name).lower()
        
        return [
            g for g in self.gear.values() 
            if "properties" in g and any(property_str in prop.lower() for prop in g["properties"])
        ]
    
    def get_gear_by_environment(self, environment: str) -> List[Dict[str, Any]]:
        """
        Get gear particularly useful for a specific environment.
        
        Args:
            environment: Target environment (desert, arctic, forest, etc.)
            
        Returns:
            List[Dict[str, Any]]: List of gear suitable for the environment
        """
        environment = environment.lower()
        
        # Check if environment is in our mapping
        if environment not in self.environment_gear_mapping:
            return []
        
        relevant_items = self.environment_gear_mapping[environment]
        
        # Find items that match the environment needs
        matched_gear = []
        
        for gear_id, gear_data in self.gear.items():
            # Check if the gear is explicitly in the environment list
            if gear_id in relevant_items:
                matched_gear.append(gear_data)
                continue
            
            # Check if any tags match
            if "tags" in gear_data and any(tag in relevant_items for tag in gear_data["tags"]):
                matched_gear.append(gear_data)
                continue
                
            # Check if name contains environment-specific terms
            if any(term in gear_data.get("name", "").lower() for term in [environment, *relevant_items]):
                matched_gear.append(gear_data)
        
        return matched_gear
    
    def get_gear_by_purpose(self, purpose: str) -> List[Dict[str, Any]]:
        """
        Get gear suitable for a specific purpose.
        
        Args:
            purpose: Intended purpose (exploration, stealth, survival, etc.)
            
        Returns:
            List[Dict[str, Any]]: List of gear suited for the purpose
        """
        purpose = purpose.lower()
        
        # Define purpose mappings
        purpose_mappings = {
            "exploration": ["light_source", "climbing", "navigation", "container"],
            "stealth": ["quiet", "disguise", "dark_colored", "lockpick"],
            "survival": ["rations", "water", "shelter", "cooking", "fire"],
            "social": ["fine_clothes", "perfume", "jewelry", "gaming"],
            "arcane": ["arcane_focus", "component_pouch", "scroll", "chalk"],
            "divine": ["holy_symbol", "incense", "offering", "sacred_text"],
            "healing": ["healer", "bandage", "herb", "antitoxin"],
            "crafting": ["tool", "material", "workbench", "kit"]
        }
        
        if purpose not in purpose_mappings:
            return []
            
        purpose_keywords = purpose_mappings[purpose]
        
        # Find items that match the purpose
        matched_gear = []
        
        for gear_data in self.gear.values():
            name_lower = gear_data.get("name", "").lower()
            desc_lower = gear_data.get("description", "").lower()
            
            # Check if gear has relevant keywords in name or description
            if any(keyword in name_lower or keyword in desc_lower for keyword in purpose_keywords):
                matched_gear.append(gear_data)
                continue
                
            # Check categories
            if "gear_category" in gear_data:
                category = gear_data["gear_category"]
                category_str = category.value if isinstance(category, GearCategory) else str(category)
                if any(keyword in category_str.lower() for keyword in purpose_keywords):
                    matched_gear.append(gear_data)
                    continue
                    
            # Check tags
            if "tags" in gear_data and any(keyword in tag.lower() for keyword in purpose_keywords for tag in gear_data["tags"]):
                matched_gear.append(gear_data)
                
        return matched_gear
    
    def create_custom_gear(self, 
                         name: str,
                         category: GearCategory = None,
                         description: str = None,
                         weight: float = 1.0,
                         cost: Dict[str, int] = None,
                         properties: List[str] = None,
                         tags: List[str] = None,
                         is_magical: bool = False,
                         rarity: RarityType = None) -> Dict[str, Any]:
        """
        Create a custom gear item with specified attributes.
        
        Args:
            name: Name of the gear
            category: Gear category
            description: Description of the gear
            weight: Weight in pounds
            cost: Cost in currency values
            properties: List of gear properties
            tags: List of tags for categorization
            is_magical: Whether the gear is magical
            rarity: Rarity if magical
            
        Returns:
            Dict[str, Any]: Created gear data
        """
        # Generate a description if none provided
        if description is None:
            description = f"A custom {category.value if category else 'utility'} item for adventures."
        
        # Set default category if none provided
        if category is None:
            category = GearCategory.UTILITY
            
        # Set default properties if none provided
        if properties is None:
            properties = [GearProperty.REUSABLE.value]
            
        # Set default tags if none provided
        if tags is None:
            tags = [category.value if category else "utility"]
            
        # Set default cost if none provided
        if cost is None:
            cost = {"gp": 1}
        
        # Create the gear data
        gear_data = {
            "id": f"custom_{name.lower().replace(' ', '_')}",
            "name": name,
            "category": EquipmentCategory.ADVENTURING_GEAR,
            "gear_category": category,
            "cost": cost,
            "weight": weight,
            "properties": properties,
            "tags": tags,
            "description": description,
            "is_magical": is_magical
        }
        
        # Add rarity if magical
        if is_magical and rarity:
            gear_data["rarity"] = rarity
        
        # Add to gear collection
        self.gear[gear_data["id"]] = gear_data
        
        # If magical, also add to magic items
        if is_magical:
            self.magic_items[gear_data["id"]] = gear_data
        
        return gear_data
    
    def calculate_gear_duration(self, 
                             gear_id: str, 
                             quantity: int = 1) -> Dict[str, Any]:
        """
        Calculate how long a consumable gear item will last.
        
        Args:
            gear_id: ID of the gear item
            quantity: Quantity of the item
            
        Returns:
            Dict[str, Any]: Duration calculation results
        """
        gear_data = self._find_item_by_id(gear_id)
        if not gear_data:
            return {"error": "Gear item not found"}
        
        # Check if it's a consumable
        is_consumable = False
        if "properties" in gear_data:
            is_consumable = any("consumable" in p.lower() for p in gear_data["properties"])
        
        if not is_consumable:
            return {
                "gear_name": gear_data.get("name"),
                "is_consumable": False,
                "message": "This item is not consumable and has no limited duration."
            }
        
        # Get the base duration for this item
        base_duration = None
        for key, duration in self.common_durations.items():
            if key in gear_id.lower() or key in gear_data.get("name", "").lower():
                base_duration = duration
                break
        
        if not base_duration:
            # Try to extract from the description
            desc = gear_data.get("description", "").lower()
            duration_match = re.search(r'lasts (?:for )?([\w\s]+)', desc)
            if duration_match:
                base_duration = duration_match.group(1)
            else:
                base_duration = "varies"
        
        # Calculate total duration if applicable
        total_duration = None
        if base_duration != "immediate" and base_duration != "varies":
            # Try to extract numeric value
            value_match = re.match(r'(\d+)\s+(.*)', base_duration)
            if value_match:
                value = int(value_match.group(1)) * quantity
                unit = value_match.group(2)
                total_duration = f"{value} {unit}"
            else:
                total_duration = f"{quantity} × {base_duration}"
        else:
            total_duration = f"{quantity} uses"
        
        return {
            "gear_name": gear_data.get("name"),
            "is_consumable": True,
            "base_duration": base_duration,
            "quantity": quantity,
            "total_duration": total_duration
        }
    
    def enhance_gear_with_llm(self, 
                           gear_id: str, 
                           enhancement_type: str = "creative",
                           context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance gear with LLM-generated content.
        
        Args:
            gear_id: ID of the gear to enhance
            enhancement_type: Type of enhancement (creative, narrative, etc.)
            context: Optional contextual information
            
        Returns:
            Dict[str, Any]: Enhanced gear data
        """
        gear_data = self._find_item_by_id(gear_id)
        if not gear_data:
            return {"error": "Gear item not found"}
            
        # Create a copy to avoid modifying the original
        enhanced_gear = gear_data.copy()
        
        if enhancement_type.lower() == "creative":
            # Generate creative uses
            creative_uses = self.llm_advisor.generate_creative_uses(
                gear_data.get("name", ""),
                gear_data.get("description", "")
            )
            enhanced_gear["creative_uses"] = creative_uses
                
        elif enhancement_type.lower() == "narrative":
            # Generate narrative description
            narrative = self.llm_advisor.generate_equipment_story(
                gear_data.get("name", ""), 
                context or {}
            )
            enhanced_gear["narrative"] = narrative
            
        elif enhancement_type.lower() == "survival":
            # Generate survival applications
            prompt = self.llm_advisor._create_prompt(
                "describe survival applications for this gear",
                f"Item: {gear_data.get('name')}\n"
                f"Description: {gear_data.get('description', '')}\n\n"
                "Describe 3-5 specific survival applications for this item in wilderness settings. "
                "Focus on practical, creative survival uses that could help adventurers in dire situations. "
                "Include applications for different environments if relevant."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                
                # Clean up the response
                clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
                clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
                
                # Extract the applications (either as list or text)
                applications = []
                for line in clean_response.split("\n"):
                    # Look for numbered or bullet point lines
                    if re.search(r'^[\d\-\*\•]\s+', line):
                        # Clean up the line
                        clean_line = re.sub(r'^[\d\-\*\•]\s+', '', line).strip()
                        if clean_line:
                            applications.append(clean_line)
                
                if not applications:
                    # If no clear bullet points, use paragraphs
                    applications = [p.strip() for p in clean_response.split("\n\n") if p.strip()]
                    
                enhanced_gear["survival_applications"] = applications
            except Exception as e:
                print(f"Error generating survival applications: {e}")
                enhanced_gear["survival_applications"] = ["Standard survival use"]
            
        return enhanced_gear
    
    def suggest_gear_combinations(self, 
                               gear_id: str,
                               scenario: str = None) -> Dict[str, Any]:
        """
        Suggest complementary gear that works well with a specific item.
        
        Args:
            gear_id: ID of the gear item
            scenario: Optional scenario context
            
        Returns:
            Dict[str, Any]: Gear combination suggestions
        """
        gear_data = self._find_item_by_id(gear_id)
        if not gear_data:
            return {"error": "Gear item not found"}
        
        # Create context for the prompt
        context = f"Item: {gear_data.get('name')}\n"
        context += f"Description: {gear_data.get('description', '')}\n"
        
        if scenario:
            context += f"Scenario: {scenario}\n"
        
        prompt = self.llm_advisor._create_prompt(
            "suggest complementary gear combinations",
            context + "\n"
            "Suggest 3-4 other equipment items that would work well in combination with this item. "
            "For each suggested item, explain how it complements or enhances the functionality of the primary item. "
            "Consider both mechanical and narrative synergies between the items."
            "Return as JSON with 'combinations' as an array of objects containing 'item_name', 'synergy_description', and 'use_case' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            combinations = self.llm_advisor._extract_json(response)
            
            if combinations and "combinations" in combinations:
                return {
                    "primary_item": gear_data.get("name"),
                    "complementary_combinations": combinations["combinations"]
                }
        except Exception as e:
            print(f"Error suggesting gear combinations: {e}")
        
        # Fallback response
        return {
            "primary_item": gear_data.get("name"),
            "complementary_combinations": [
                {
                    "item_name": "Backpack",
                    "synergy_description": "Provides a way to carry the item",
                    "use_case": "Basic transportation"
                },
                {
                    "item_name": "Rope",
                    "synergy_description": "Multipurpose tool that complements most equipment",
                    "use_case": "General utility"
                }
            ]
        }
    
    def calculate_gear_utility(self, 
                            gear_id: str, 
                            environment: str,
                            task: str = None) -> Dict[str, Any]:
        """
        Calculate the utility value of gear in a specific environment or task.
        
        Args:
            gear_id: ID of the gear item
            environment: Target environment (desert, arctic, etc.)
            task: Optional specific task
            
        Returns:
            Dict[str, Any]: Utility calculation results
        """
        gear_data = self._find_item_by_id(gear_id)
        if not gear_data:
            return {"error": "Gear item not found"}
            
        # Check if this item is listed in our environment mapping
        environment = environment.lower()
        environment_utility = 5  # Default medium utility on 1-10 scale
        
        if environment in self.environment_gear_mapping:
            relevant_items = self.environment_gear_mapping[environment]
            
            # Check for direct matches
            if gear_id in relevant_items:
                environment_utility = 9
            elif "tags" in gear_data and any(tag in relevant_items for tag in gear_data["tags"]):
                environment_utility = 8
            elif any(term in gear_data.get("name", "").lower() for term in relevant_items):
                environment_utility = 7
        
        # Adjust for specific tasks if provided
        task_utility = None
        if task:
            # We'll use LLM to evaluate ta utility
            prompt = self.llm_advisor._create_prompt(
                "evaluate gear utility for specific task",
                f"Item: {gear_data.get('name')}\n"
                f"Description: {gear_data.get('description', '')}\n"
                f"Environment: {environment}\n"
                f"Task: {task}\n\n"
                f"On a scale of 1-10, how useful would this specific item be for accomplishing the task "
                f"in this environment? Explain your rating with specific examples of how the item would help "
                f"or why it would be less useful than alternatives."
                f"Return as JSON with 'utility_rating', 'explanation', and 'suggested_uses' keys."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                utility_data = self.llm_advisor._extract_json(response)
                
                if utility_data and "utility_rating" in utility_data:
                    task_utility = utility_data
            except Exception as e:
                print(f"Error calculating task utility: {e}")
        
        # Prepare the result
        result = {
            "gear_name": gear_data.get("name"),
            "environment": environment,
            "environment_utility_rating": environment_utility,
            "environment_utility_level": self._utility_level_name(environment_utility)
        }
        
        if task:
            if task_utility:
                result["task"] = task
                result["task_utility"] = task_utility
            else:
                result["task"] = task
                result["task_utility"] = {
                    "utility_rating": 5,
                    "explanation": "Average utility for this task",
                    "suggested_uses": ["Basic application"]
                }
        
        return result
    
    def generate_gear_appearance(self, gear_id: str, style: str = None) -> str:
        """
        Generate a detailed visual description of a gear item.
        
        Args:
            gear_id: ID of the gear
            style: Optional style direction (e.g., "rustic", "elegant", "exotic")
            
        Returns:
            str: Detailed appearance description
        """
        gear_data = self._find_item_by_id(gear_id)
        if not gear_data:
            return "Gear item not found"
        
        context = f"Item: {gear_data.get('name')}\n"
        context += f"Type: {gear_data.get('gear_category').value if isinstance(gear_data.get('gear_category'), GearCategory) else 'utility item'}\n"
        context += f"Description: {gear_data.get('description', '')}\n"
        
        if style:
            context += f"Style Direction: {style}\n"
            
        prompt = self.llm_advisor._create_prompt(
            "describe the physical appearance of this gear",
            context + "\n"
            "Create a vivid, detailed description of this item's physical appearance. "
            "Include details about its materials, craftsmanship, distinctive features, "
            "wear patterns, and overall aesthetic. The description should help a player "
            "visualize the item clearly when their character uses it."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            
            # Clean up the response by removing any JSON formatting
            clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
            clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
            
            return clean_response.strip()
        except Exception as e:
            print(f"Error generating gear appearance: {e}")
            
        # Fallback description
        return f"A standard {gear_data.get('name')} with typical construction and appearance."
    
    def pack_adventure_kit(self, 
                        environment: str,
                        duration_days: int = 3,
                        party_size: int = 4,
                        budget: int = 100,
                        specialized_needs: List[str] = None) -> Dict[str, Any]:
        """
        Assemble a recommended kit of adventuring gear for a specific scenario.
        
        Args:
            environment: Target environment (desert, arctic, forest, etc.)
            duration_days: Expected duration of adventure in days
            party_size: Number of adventurers
            budget: Budget in gold pieces
            specialized_needs: Optional list of specialized requirements
            
        Returns:
            Dict[str, Any]: Recommended adventure kit
        """
        # Create context for the LLM prompt
        context = f"Environment: {environment}\n"
        context += f"Adventure Duration: {duration_days} days\n"
        context += f"Party Size: {party_size} adventurers\n"
        context += f"Budget: {budget} gold pieces\n"
        
        if specialized_needs:
            context += f"Specialized Needs: {', '.join(specialized_needs)}\n"
        
        prompt = self.llm_advisor._create_prompt(
            "assemble optimal adventure kit",
            context + "\n"
            "Create a comprehensive kit of adventuring gear tailored to this specific scenario. "
            "The kit should include essential gear for the environment and duration, "
            "while staying within budget. Include quantities needed for the party, "
            "and explain the purpose of key items. Organize by categories (survival, exploration, etc.). "
            "Return as JSON with 'essential_gear', 'recommended_gear', 'specialized_gear', 'total_cost', and 'weight_estimate' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            kit_data = self.llm_advisor._extract_json(response)
            
            if kit_data:
                # Add metadata
                kit_data["environment"] = environment
                kit_data["duration_days"] = duration_days
                kit_data["party_size"] = party_size
                kit_data["budget"] = budget
                
                return kit_data
        except Exception as e:
            print(f"Error assembling adventure kit: {e}")
        
        # Fallback kit
        return {
            "environment": environment,
            "duration_days": duration_days,
            "party_size": party_size,
            "budget": budget,
            "essential_gear": [
                {"name": "Backpack", "quantity": party_size, "purpose": "Carrying gear"},
                {"name": "Waterskin", "quantity": party_size, "purpose": "Hydration"},
                {"name": "Rations (1 day)", "quantity": party_size * duration_days, "purpose": "Food"},
                {"name": "Bedroll", "quantity": party_size, "purpose": "Rest"},
                {"name": "Torch", "quantity": party_size * 2, "purpose": "Light source"}
            ],
            "recommended_gear": [
                {"name": "Rope, hempen (50 feet)", "quantity": 2, "purpose": "Climbing, binding"},
                {"name": "Tinderbox", "quantity": 2, "purpose": "Starting fires"}
            ],
            "specialized_gear": [],
            "total_cost": 50,
            "weight_estimate": "15 pounds per person"
        }
    
    # === HELPER METHODS ===
    
    def _utility_level_name(self, utility_rating: int) -> str:
        """Convert numeric utility rating to descriptive level."""
        if utility_rating >= 9:
            return "essential"
        elif utility_rating >= 7:
            return "highly useful"
        elif utility_rating >= 5:
            return "moderately useful"
        elif utility_rating >= 3:
            return "situationally useful"
        else:
            return "minimally useful"