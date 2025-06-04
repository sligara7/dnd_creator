# tools.py
# Description: Handles tool equipment for crafting, thieving, and specialized tasks

from typing import Dict, List, Optional, Union, Any, Tuple
import json
import re
from enum import Enum

from backend.core.equipment.equipment import Equipment, EquipmentCategory, RarityType

class ToolCategory(Enum):
    """Categories of tools"""
    ARTISANS = "artisans"  # Blacksmith's tools, carpenter's tools, etc.
    GAMING = "gaming"      # Dice sets, playing card set, etc.
    MUSICAL = "musical"    # Musical instruments
    NAVIGATION = "navigation"  # Navigator's tools, cartographer's tools
    THIEVING = "thieving"  # Thieves' tools, forgery kit, disguise kit
    HERBALISM = "herbalism"  # Herbalism kit, poisoner's kit
    VEHICLES = "vehicles"  # Land and water vehicle tools
    SPECIALIZED = "specialized"  # Other specialized tools

class ToolProperty(Enum):
    """Special properties that tools can have"""
    PORTABLE = "portable"  # Easy to carry
    BULKY = "bulky"        # Difficult to transport
    FRAGILE = "fragile"    # Can break easily
    DURABLE = "durable"    # Resistant to damage
    SPECIALIZED = "specialized"  # Highly specific use case
    VERSATILE = "versatile"  # Multiple uses
    MAGICAL = "magical"    # Has magical properties
    ILLEGAL = "illegal"    # Possession may be illegal in some areas
    PRESTIGIOUS = "prestigious"  # Confers social status
    CONSUMABLE = "consumable"  # Contains parts that are used up

class ToolSkill(Enum):
    """Skills associated with tool use"""
    ARCANA = "arcana"
    ATHLETICS = "athletics"
    DECEPTION = "deception"
    HISTORY = "history"
    INSIGHT = "insight"
    INVESTIGATION = "investigation"
    MEDICINE = "medicine"
    NATURE = "nature"
    PERCEPTION = "perception"
    PERFORMANCE = "performance"
    PERSUASION = "persuasion"
    SLEIGHT_OF_HAND = "sleight_of_hand"
    STEALTH = "stealth"
    SURVIVAL = "survival"

class Tools(Equipment):
    """
    Class for handling tool equipment for crafting, specialized tasks, and professions.
    
    Extends the Equipment class with tool-specific functionality for creating,
    customizing, and analyzing tools for character professions and skills.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the tools manager with parent equipment functionality."""
        super().__init__(llm_service)
        
        # Additional tool configuration
        self.skill_tool_mapping = {
            "arcana": ["alchemist_supplies", "arcane_focus"],
            "athletics": ["climbers_kit", "vehicles_land"],
            "deception": ["disguise_kit", "forgery_kit"],
            "history": ["calligraphers_supplies", "cartographers_tools"],
            "insight": ["gaming_set", "herbalism_kit"],
            "investigation": ["magnifying_glass", "thieves_tools"],
            "medicine": ["herbalism_kit", "healers_kit"],
            "nature": ["herbalism_kit", "poisoners_kit"],
            "perception": ["navigators_tools", "magnifying_glass"],
            "performance": ["musical_instrument", "disguise_kit"],
            "persuasion": ["brewers_supplies", "calligraphers_supplies"],
            "sleight_of_hand": ["thieves_tools", "forgery_kit"],
            "stealth": ["thieves_tools", "poisoners_kit"],
            "survival": ["herbalism_kit", "cartographers_tools"]
        }
        
        # Crafting output mapping
        self.crafting_outputs = {
            "alchemists_supplies": ["potions", "alchemical items", "acid"],
            "blacksmiths_tools": ["metal weapons", "armor", "metal items"],
            "brewers_supplies": ["ale", "beer", "mead"],
            "calligraphers_supplies": ["scrolls", "documents", "maps"],
            "carpenters_tools": ["wooden structures", "furniture", "wooden items"],
            "cobblers_tools": ["shoes", "boots", "leather goods"],
            "cooks_utensils": ["meals", "preserved foods", "special dishes"],
            "glassblowers_tools": ["glass items", "vials", "lenses"],
            "jewelers_tools": ["jewelry", "gem cutting", "precious items"],
            "leatherworkers_tools": ["leather armor", "saddles", "leather goods"],
            "masons_tools": ["stone structures", "sculptures", "stone items"],
            "painters_supplies": ["paintings", "murals", "artistic works"],
            "potters_tools": ["pottery", "clay items", "ceramic goods"],
            "tinkers_tools": ["small mechanical items", "repairs", "gadgets"],
            "weavers_tools": ["clothing", "tapestries", "cloth goods"],
            "woodcarvers_tools": ["wooden trinkets", "figurines", "decorated items"]
        }
    
    def get_tools_by_category(self, category: Union[ToolCategory, str]) -> List[Dict[str, Any]]:
        """
        Get tools filtered by category.
        
        Args:
            category: Category to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of tools in the category
        """
        if isinstance(category, str):
            # Try to convert string to enum
            try:
                category = ToolCategory(category.lower())
            except ValueError:
                # If not a valid category, return empty list
                return []
        
        return [
            t for t in self.tools.values() 
            if "tool_category" in t and t["tool_category"] == category
        ]
    
    def get_tools_by_property(self, property_name: Union[ToolProperty, str]) -> List[Dict[str, Any]]:
        """
        Get tools that have a specific property.
        
        Args:
            property_name: Property to filter by (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of tools with the property
        """
        property_str = property_name.value if isinstance(property_name, ToolProperty) else str(property_name).lower()
        
        return [
            t for t in self.tools.values() 
            if "properties" in t and any(property_str in prop.lower() for prop in t["properties"])
        ]
    
    def get_tools_by_skill(self, skill: Union[ToolSkill, str]) -> List[Dict[str, Any]]:
        """
        Get tools particularly useful for a specific skill.
        
        Args:
            skill: Associated skill (enum or string)
            
        Returns:
            List[Dict[str, Any]]: List of tools related to the skill
        """
        skill_str = skill.value if isinstance(skill, ToolSkill) else str(skill).lower()
        
        if skill_str not in self.skill_tool_mapping:
            return []
            
        related_tools = self.skill_tool_mapping[skill_str]
        
        # Find tools that match the related tool types
        matched_tools = []
        
        for tool_id, tool_data in self.tools.items():
            # Check if tool ID is in the related tools list
            if any(related in tool_id.lower() for related in related_tools):
                matched_tools.append(tool_data)
                continue
                
            # Check if tool name contains related tool terms
            if any(related in tool_data.get("name", "").lower() for related in related_tools):
                matched_tools.append(tool_data)
                continue
                
            # Check if associated skills are listed
            if "associated_skills" in tool_data and any(skill_str == s.lower() for s in tool_data["associated_skills"]):
                matched_tools.append(tool_data)
        
        return matched_tools
    
    def check_tool_proficiency(self, character_data: Dict[str, Any], tool_id: str) -> bool:
        """
        Check if a character is proficient with a specific tool.
        
        Args:
            character_data: Character data including proficiencies
            tool_id: ID of the tool to check
            
        Returns:
            bool: True if proficient, False otherwise
        """
        tool_data = self._find_item_by_id(tool_id)
        if not tool_data:
            return False
        
        # Get character proficiencies
        proficiencies = character_data.get("proficiencies", {}).get("tools", [])
        if not proficiencies:
            return False
        
        # Check for tool name in specific proficiencies
        tool_name = tool_data.get("name", "").lower()
        if any(tool_name in p.lower() for p in proficiencies):
            return True
        
        # Check for tool category in group proficiencies
        if "tool_category" in tool_data:
            category = tool_data["tool_category"]
            category_str = category.value if isinstance(category, ToolCategory) else str(category)
            
            # Check for category proficiencies
            if category_str == ToolCategory.ARTISANS.value and "artisan's tools" in [p.lower() for p in proficiencies]:
                return True
            elif category_str == ToolCategory.GAMING.value and "gaming set" in [p.lower() for p in proficiencies]:
                return True
            elif category_str == ToolCategory.MUSICAL.value and "musical instrument" in [p.lower() for p in proficiencies]:
                return True
        
        # Check for specific tool proficiency
        if tool_id in [p.lower().replace(" ", "_") for p in proficiencies]:
            return True
            
        # Check for tool type in proficiencies
        tool_types = [
            "thieves_tools", "herbalism_kit", "poisoners_kit", "navigators_tools", 
            "disguise_kit", "forgery_kit", "brewers_supplies"
        ]
        
        for tool_type in tool_types:
            if tool_type in tool_id and any(tool_type.replace("_", " ") in p.lower() for p in proficiencies):
                return True
        
        return False
    
    def calculate_check_bonus(self, 
                           tool_id: str, 
                           character_data: Dict[str, Any],
                           skill: str = None) -> Dict[str, Any]:
        """
        Calculate bonus for tool check based on proficiency and abilities.
        
        Args:
            tool_id: ID of the tool
            character_data: Character data including proficiencies and abilities
            skill: Optional specific skill to use with the tool
            
        Returns:
            Dict[str, Any]: Check bonus calculation results
        """
        tool_data = self._find_item_by_id(tool_id)
        if not tool_data:
            return {"error": "Tool not found"}
        
        # Check if character is proficient
        is_proficient = self.check_tool_proficiency(character_data, tool_id)
        proficiency_bonus = character_data.get("proficiency_bonus", 2) if is_proficient else 0
        
        # Determine associated ability and skill
        ability_scores = character_data.get("ability_scores", {})
        associated_skills = tool_data.get("associated_skills", [])
        
        # Default ability and skill mappings based on tool category
        default_ability = "intelligence"
        best_skill = None
        
        if "tool_category" in tool_data:
            category = tool_data["tool_category"]
            if isinstance(category, ToolCategory):
                category_str = category.value
            else:
                category_str = str(category)
                
            # Set default ability based on category
            if category_str == ToolCategory.ARTISANS.value:
                default_ability = "intelligence"
            elif category_str == ToolCategory.GAMING.value:
                default_ability = "wisdom"
            elif category_str == ToolCategory.MUSICAL.value:
                default_ability = "charisma"
            elif category_str == ToolCategory.THIEVING.value:
                default_ability = "dexterity"
            
            # Determine best skill based on category if not specified
            if not skill:
                if category_str == ToolCategory.ARTISANS.value:
                    if tool_id.startswith("alchemist"):
                        best_skill = "arcana"
                    else:
                        best_skill = "history"
                elif category_str == ToolCategory.THIEVING.value:
                    if "thieves" in tool_id:
                        best_skill = "sleight_of_hand"
                    elif "forgery" in tool_id:
                        best_skill = "deception"
                    else:
                        best_skill = "stealth"
                elif category_str == ToolCategory.NAVIGATION.value:
                    best_skill = "survival"
        
        # Override with specified skill if provided
        if skill:
            best_skill = skill.lower()
        
        # Determine ability modifier based on skill
        ability_to_use = default_ability
        if best_skill:
            # Map skill to ability
            skill_ability_map = {
                "athletics": "strength",
                "acrobatics": "dexterity",
                "sleight_of_hand": "dexterity",
                "stealth": "dexterity",
                "arcana": "intelligence",
                "history": "intelligence",
                "investigation": "intelligence",
                "nature": "intelligence",
                "religion": "intelligence",
                "animal_handling": "wisdom",
                "insight": "wisdom",
                "medicine": "wisdom",
                "perception": "wisdom",
                "survival": "wisdom",
                "deception": "charisma",
                "intimidation": "charisma",
                "performance": "charisma",
                "persuasion": "charisma"
            }
            if best_skill in skill_ability_map:
                ability_to_use = skill_ability_map[best_skill]
        
        # Calculate ability modifier
        ability_score = ability_scores.get(ability_to_use, 10)
        ability_modifier = (ability_score - 10) // 2
        
        # Calculate total bonus
        total_bonus = ability_modifier + proficiency_bonus
        
        # Return result
        return {
            "tool_name": tool_data.get("name"),
            "is_proficient": is_proficient,
            "ability_used": ability_to_use,
            "ability_score": ability_score,
            "ability_modifier": ability_modifier,
            "proficiency_bonus": proficiency_bonus,
            "total_bonus": total_bonus,
            "recommended_skill": best_skill,
            "check_description": f"{total_bonus:+d} ({ability_to_use} {ability_modifier:+d} + "
                               f"proficiency {proficiency_bonus})"
        }
    
    def create_custom_tool(self, 
                         name: str,
                         tool_category: ToolCategory = None, 
                         description: str = None,
                         associated_skills: List[str] = None,
                         properties: List[str] = None,
                         weight: float = 5.0,
                         cost: Dict[str, int] = None,
                         is_magical: bool = False,
                         rarity: RarityType = None) -> Dict[str, Any]:
        """
        Create a custom tool with specified attributes.
        
        Args:
            name: Name of the tool
            tool_category: Tool category
            description: Description of the tool
            associated_skills: Skills associated with the tool
            properties: List of tool properties
            weight: Weight in pounds
            cost: Cost in currency values
            is_magical: Whether the tool is magical
            rarity: Rarity if magical
            
        Returns:
            Dict[str, Any]: Created tool data
        """
        # Set default category if none provided
        if tool_category is None:
            tool_category = ToolCategory.SPECIALIZED
            
        # Generate a description if none provided
        if description is None:
            description = f"A custom {tool_category.value} tool used for specialized tasks."
        
        # Set default associated skills if none provided
        if associated_skills is None:
            if tool_category == ToolCategory.ARTISANS:
                associated_skills = ["intelligence"]
            elif tool_category == ToolCategory.GAMING:
                associated_skills = ["wisdom", "intelligence"]
            elif tool_category == ToolCategory.MUSICAL:
                associated_skills = ["performance", "charisma"]
            elif tool_category == ToolCategory.NAVIGATION:
                associated_skills = ["survival", "nature"]
            elif tool_category == ToolCategory.THIEVING:
                associated_skills = ["sleight_of_hand", "deception"]
            elif tool_category == ToolCategory.HERBALISM:
                associated_skills = ["nature", "medicine"]
            else:
                associated_skills = ["intelligence"]
        
        # Set default properties if none provided
        if properties is None:
            properties = [ToolProperty.PORTABLE.value]
            
        # Set default cost if none provided
        if cost is None:
            cost = {"gp": 25}
        
        # Create the tool data
        tool_data = {
            "id": f"custom_{name.lower().replace(' ', '_')}",
            "name": name,
            "category": EquipmentCategory.TOOL,
            "tool_category": tool_category,
            "cost": cost,
            "weight": weight,
            "properties": properties,
            "associated_skills": associated_skills,
            "description": description,
            "is_magical": is_magical
        }
        
        # Add rarity if magical
        if is_magical and rarity:
            tool_data["rarity"] = rarity
        
        # Add to tools collection
        self.tools[tool_data["id"]] = tool_data
        
        # If magical, also add to magic items
        if is_magical:
            self.magic_items[tool_data["id"]] = tool_data
        
        return tool_data
    
    def enhance_tool_with_llm(self, 
                          tool_id: str, 
                          enhancement_type: str = "uses",
                          character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance tool with LLM-generated content.
        
        Args:
            tool_id: ID of the tool to enhance
            enhancement_type: Type of enhancement (uses, narrative, crafting)
            character_data: Optional character data for contextual enhancements
            
        Returns:
            Dict[str, Any]: Enhanced tool data
        """
        tool_data = self._find_item_by_id(tool_id)
        if not tool_data:
            return {"error": "Tool not found"}
            
        # Create a copy to avoid modifying the original
        enhanced_tool = tool_data.copy()
        
        if enhancement_type.lower() == "uses":
            # Generate creative uses
            creative_uses = self.llm_advisor.generate_creative_uses(
                tool_data.get("name", ""),
                tool_data.get("description", "")
            )
            enhanced_tool["creative_uses"] = creative_uses
                
        elif enhancement_type.lower() == "narrative":
            # Generate narrative description
            narrative = self.llm_advisor.generate_equipment_story(
                tool_data.get("name", ""), 
                character_data or {}
            )
            enhanced_tool["narrative"] = narrative
            
        elif enhancement_type.lower() == "crafting":
            # Generate crafting possibilities
            tool_name = tool_data.get("name", "").lower()
            
            # Find potential crafting outputs
            crafting_products = []
            for tool_key, products in self.crafting_outputs.items():
                if tool_key in tool_id.lower() or tool_key.replace("_", " ") in tool_name:
                    crafting_products = products
                    break
            
            if not crafting_products:
                crafting_products = ["specialized items"]
            
            # Generate detailed crafting information with LLM
            prompt = self.llm_advisor._create_prompt(
                "describe crafting possibilities with this tool",
                f"Tool: {tool_data.get('name')}\n"
                f"Description: {tool_data.get('description', '')}\n"
                f"Typical Products: {', '.join(crafting_products)}\n\n"
                "Describe in detail what a character can craft with this tool, including:\n"
                "1. Common items that can be created\n"
                "2. Rare or special items that require greater skill\n"
                "3. Approximate crafting times and material costs\n"
                "4. Skill checks that might be required\n"
                "5. Creative or unusual applications of these crafting skills\n"
                "Return as JSON with 'common_items', 'special_items', 'crafting_details', 'skill_challenges', and 'creative_applications' keys."
            )
            
            try:
                response = self.llm_advisor.llm_service.generate(prompt)
                crafting_data = self.llm_advisor._extract_json(response)
                
                if crafting_data:
                    enhanced_tool["crafting_possibilities"] = crafting_data
                else:
                    # Fallback if JSON extraction fails
                    enhanced_tool["crafting_possibilities"] = {
                        "common_items": crafting_products,
                        "note": "Use this tool with appropriate skill checks to craft various items."
                    }
            except Exception as e:
                print(f"Error generating crafting possibilities: {e}")
                enhanced_tool["crafting_possibilities"] = {
                    "common_items": crafting_products,
                    "note": "Use this tool with appropriate skill checks to craft various items."
                }
            
        return enhanced_tool
    
    def suggest_tool_dc(self, 
                     tool_id: str, 
                     task_description: str) -> Dict[str, Any]:
        """
        Suggest appropriate DC for a tool check based on the task description.
        
        Args:
            tool_id: ID of the tool
            task_description: Description of the task to accomplish
            
        Returns:
            Dict[str, Any]: DC suggestion and task breakdown
        """
        tool_data = self._find_item_by_id(tool_id)
        if not tool_data:
            return {"error": "Tool not found"}
        
        # Use LLM to analyze task difficulty
        prompt = self.llm_advisor._create_prompt(
            "analyze tool task difficulty",
            f"Tool: {tool_data.get('name')}\n"
            f"Tool Description: {tool_data.get('description', '')}\n"
            f"Task: {task_description}\n\n"
            "Analyze this task to determine an appropriate Difficulty Class (DC) for a D&D 5e tool check. "
            "Consider standard D&D 5e DC ranges:\n"
            "- Very Easy: DC 5\n"
            "- Easy: DC 10\n"
            "- Medium: DC 15\n"
            "- Hard: DC 20\n"
            "- Very Hard: DC 25\n"
            "- Nearly Impossible: DC 30\n\n"
            "Return as JSON with 'suggested_dc', 'difficulty_assessment', 'recommended_skill', 'task_breakdown', and 'special_considerations' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            dc_data = self.llm_advisor._extract_json(response)
            
            if dc_data and "suggested_dc" in dc_data:
                dc_data["tool_name"] = tool_data.get("name")
                return dc_data
        except Exception as e:
            print(f"Error suggesting tool DC: {e}")
        
        # Fallback response with reasonable defaults
        return {
            "tool_name": tool_data.get("name"),
            "suggested_dc": 15,
            "difficulty_assessment": "Medium",
            "recommended_skill": "Intelligence",
            "task_breakdown": "This appears to be a standard task with this tool.",
            "special_considerations": "The DM may adjust the DC based on circumstances."
        }
    
    def generate_tool_results(self, 
                           tool_id: str,
                           check_result: int,
                           task_description: str) -> Dict[str, Any]:
        """
        Generate narrative results for a tool check based on the roll result.
        
        Args:
            tool_id: ID of the tool
            check_result: Result of the ability check
            task_description: Description of the task attempted
            
        Returns:
            Dict[str, Any]: Narrative results of the tool use
        """
        tool_data = self._find_item_by_id(tool_id)
        if not tool_data:
            return {"error": "Tool not found"}
        
        # Get suggested DC for comparison
        dc_info = self.suggest_tool_dc(tool_id, task_description)
        suggested_dc = dc_info.get("suggested_dc", 15)
        
        # Determine success level
        if check_result >= suggested_dc + 10:
            success_level = "critical_success"
        elif check_result >= suggested_dc:
            success_level = "success"
        elif check_result >= suggested_dc - 5:
            success_level = "partial_success"
        else:
            success_level = "failure"
        
        # Use LLM to generate narrative results
        prompt = self.llm_advisor._create_prompt(
            "generate tool check narrative results",
            f"Tool: {tool_data.get('name')}\n"
            f"Task: {task_description}\n"
            f"Check Result: {check_result}\n"
            f"Suggested DC: {suggested_dc}\n"
            f"Success Level: {success_level}\n\n"
            "Generate a detailed narrative description of what happens when the character uses this tool "
            "with the given check result. The description should be vivid and specific to the tool and task, "
            "describing the process, challenges encountered, and outcome. If successful, describe what was created "
            "or accomplished. If unsuccessful, explain what went wrong and any consequences."
            "Return as JSON with 'success_level', 'narrative_result', 'time_taken', 'outcomes', and 'side_effects' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            result_data = self.llm_advisor._extract_json(response)
            
            if result_data:
                result_data["tool_name"] = tool_data.get("name")
                result_data["check_result"] = check_result
                result_data["dc"] = suggested_dc
                return result_data
        except Exception as e:
            print(f"Error generating tool results: {e}")
        
        # Fallback response
        return {
            "tool_name": tool_data.get("name"),
            "check_result": check_result,
            "dc": suggested_dc,
            "success_level": success_level,
            "narrative_result": f"The character {'succeeded' if check_result >= suggested_dc else 'failed'} at the task.",
            "time_taken": "As expected",
            "outcomes": ["Standard result"],
            "side_effects": []
        }
    
    def suggest_appropriate_tools(self, 
                               task_description: str,
                               available_tools: List[str] = None) -> Dict[str, Any]:
        """
        Suggest appropriate tools for a given task.
        
        Args:
            task_description: Description of the task to accomplish
            available_tools: Optional list of available tool IDs to choose from
            
        Returns:
            Dict[str, Any]: Tool suggestions
        """
        # Create context for the LLM prompt
        context = f"Task Description: {task_description}\n"
        
        if available_tools:
            available_tool_names = []
            for tool_id in available_tools:
                tool_data = self._find_item_by_id(tool_id)
                if tool_data:
                    available_tool_names.append(tool_data.get("name"))
            
            if available_tool_names:
                context += f"Available Tools: {', '.join(available_tool_names)}\n"
        
        prompt = self.llm_advisor._create_prompt(
            "suggest appropriate tools for task",
            context + "\n"
            "Suggest appropriate tools for accomplishing this task in D&D 5e. For each suggested tool, "
            "explain why it would be helpful, how it could be used, and what ability check or skill would "
            "typically be associated with it. If multiple tools could work together, explain how. "
            "Return as JSON with 'primary_tool_suggestions', 'alternative_tools', 'skill_pairings', and 'approach_description' keys."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            suggestions = self.llm_advisor._extract_json(response)
            
            if suggestions:
                return {
                    "task": task_description,
                    "tool_suggestions": suggestions
                }
        except Exception as e:
            print(f"Error suggesting tools: {e}")
        
        # Fallback response
        return {
            "task": task_description,
            "tool_suggestions": {
                "primary_tool_suggestions": ["Appropriate tools depend on the specific task"],
                "alternative_tools": ["Consider asking your DM for guidance"],
                "skill_pairings": ["Intelligence or Wisdom checks are common with tools"],
                "approach_description": "The approach would depend on the specific tools available."
            }
        }
    
    def generate_tool_appearance(self, tool_id: str, style: str = None) -> str:
        """
        Generate a detailed visual description of a tool.
        
        Args:
            tool_id: ID of the tool
            style: Optional style direction (e.g., "ornate", "weathered", "elven")
            
        Returns:
            str: Detailed appearance description
        """
        tool_data = self._find_item_by_id(tool_id)
        if not tool_data:
            return "Tool not found"
        
        context = f"Tool: {tool_data.get('name')}\n"
        context += f"Type: {tool_data.get('tool_category').value if isinstance(tool_data.get('tool_category'), ToolCategory) else 'specialized tool'}\n"
        
        if style:
            context += f"Style Direction: {style}\n"
            
        prompt = self.llm_advisor._create_prompt(
            "describe the physical appearance of this tool",
            context + "\n"
            "Create a vivid, detailed description of this tool's physical appearance. "
            "Include details about its components, materials, craftsmanship, container or carrying case, "
            "distinctive features, and overall aesthetic. The description should help a player "
            "visualize what their character is working with when using this tool."
        )
        
        try:
            response = self.llm_advisor.llm_service.generate(prompt)
            
            # Clean up the response by removing any JSON formatting
            clean_response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
            clean_response = re.sub(r'\{.*?\}', '', clean_response, flags=re.DOTALL)
            
            return clean_response.strip()
        except Exception as e:
            print(f"Error generating tool appearance: {e}")
            
        # Fallback description
        return f"A standard set of {tool_data.get('name')} with typical components and construction."