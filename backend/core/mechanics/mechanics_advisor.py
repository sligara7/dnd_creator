"""
Mechanics Advisor Module

Provides AI-powered assistance for D&D game mechanics customization and refinement.
This module helps DMs and players adapt and retheme game mechanics while preserving 
their mechanical function.
"""

from typing import Dict, Any, List, Optional
import json
import re
from pathlib import Path

from backend.core.advisors.base_advisor import BaseAdvisor

import logging
logger = logging.getLogger(__name__)

class MechanicsAdvisor(BaseAdvisor):
    """
    Provides AI-powered assistance for D&D mechanics customization and theming.
    
    This class integrates with Language Learning Models (LLMs) to provide creative
    assistance for rethemeing existing game mechanics while preserving their
    mechanical function and game balance.
    """

    def __init__(self, llm_service=None, data_path: str = None, cache_enabled=True):
        """
        Initialize the mechanics advisor.
        
        Args:
            llm_service: LLM service client for generating responses
            data_path: Optional path to mechanics data
            cache_enabled: Whether to enable response caching
        """
        # Initialize base advisor with mechanics-specific system prompt
        system_prompt = "You are a D&D 5e game mechanics expert specializing in creative reskinning and rethemeing of abilities, spells, and features while preserving their mechanical function and game balance."
        super().__init__(llm_service, system_prompt, cache_enabled)
        
        # Set up paths and data
        self.data_path = Path(data_path) if data_path else Path("backend/data/mechanics")
        self._load_reference_data()
        
    def _load_reference_data(self):
        """Load reference data for mechanics customization."""
        try:
            # Load themes data if available
            themes_path = self.data_path / "themes.json"
            if themes_path.exists():
                with open(themes_path, "r") as f:
                    self.themes_data = json.load(f)
            else:
                self.themes_data = {}
                
            # Load mechanics data if available
            mechanics_path = self.data_path / "mechanics.json"
            if mechanics_path.exists():
                with open(mechanics_path, "r") as f:
                    self.mechanics_data = json.load(f)
            else:
                self.mechanics_data = {}
                
        except Exception as e:
            logger.error(f"Error loading reference data: {e}")
            self.themes_data = {}
            self.mechanics_data = {}
                
    def retheme_mechanics(self, mechanics_id: str, new_theme: str) -> Dict[str, Any]:
        """
        Keep same mechanics but apply new theme/flavor.
        
        Args:
            mechanics_id: Identifier for the mechanic to be rethemed
            new_theme: New thematic direction (e.g., "elemental", "necrotic", "celestial")
            
        Returns:
            Dict[str, Any]: Rethemed mechanic with preserved functionality
        """
        # Get the original mechanics details
        mechanic_details = self._get_mechanic_details(mechanics_id)
        if not mechanic_details:
            return {
                "success": False,
                "error": f"Mechanic ID '{mechanics_id}' not found"
            }
            
        # Build context for LLM
        context = f"Original Mechanic Name: {mechanic_details.get('name', 'Unknown')}\n"
        context += f"Mechanic Type: {mechanic_details.get('type', 'Unknown')}\n"
        context += f"New Theme: {new_theme}\n\n"
        
        # Add description and mechanical effects
        context += f"Current Description: {mechanic_details.get('description', 'No description')}\n\n"
        
        if "mechanical_effect" in mechanic_details:
            context += f"Mechanical Effect (must be preserved): {mechanic_details['mechanical_effect']}\n\n"
            
        # Add mechanics details
        if "mechanics_details" in mechanic_details:
            context += "Mechanical Details (must be preserved):\n"
            for key, value in mechanic_details["mechanics_details"].items():
                context += f"- {key}: {value}\n"
                
        # Create prompt using base advisor's format_prompt method
        prompt = self._format_prompt(
            f"retheme a {mechanic_details.get('type', 'mechanic')} to {new_theme} theme",
            context,
            [
                f"New {new_theme}-themed name",
                f"Rethemed description that fits the {new_theme} aesthetic",
                "Same mechanical effects as the original",
                "Visual and thematic descriptions of how the ability looks and feels when used",
                "Suggestion for any cosmetic but mechanically identical variations"
            ]
        )
        
        try:
            # Generate rethemed mechanics with LLM using base advisor's method
            response = self._get_llm_response(
                "retheme_mechanics", 
                prompt, 
                {"mechanic": mechanics_id, "theme": new_theme}
            )
            
            # Parse the response into structured data
            rethemed_data = self._parse_retheme_response(response)
            
            # Make sure we maintain the original mechanical properties
            rethemed_data["original_mechanic_id"] = mechanics_id
            
            # Copy over the mechanical details that must be preserved
            for key in ["mechanical_effect", "mechanics_details", "type", "required_level"]:
                if key in mechanic_details:
                    rethemed_data[key] = mechanic_details[key]
                    
            return {
                "success": True,
                "rethemed_mechanic": rethemed_data,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to retheme mechanic: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to retheme mechanic: {str(e)}"
            }
    
    def suggest_thematic_mechanics(self, character_concept: str, level_range: str = "1-5", 
                                 mechanic_type: str = None) -> Dict[str, Any]:
        """
        Suggest mechanics that fit a specific character concept or theme.
        
        Args:
            character_concept: Brief description of character concept or theme
            level_range: Range of character levels (e.g., "1-5", "6-10")
            mechanic_type: Optional type of mechanic (spell, feature, ability, etc.)
            
        Returns:
            Dict[str, Any]: Suggested mechanics that fit the concept
        """
        # Build context for LLM
        context = f"Character Concept: {character_concept}\n"
        context += f"Level Range: {level_range}\n"
        
        if mechanic_type:
            context += f"Mechanic Type: {mechanic_type}\n"
            
        # Create prompt using base advisor's format_prompt method
        prompt = self._format_prompt(
            "suggest thematic mechanics",
            context,
            [
                "3-5 existing mechanics (spells, features, abilities) that fit this concept",
                "Brief explanation of how each mechanic fits the theme",
                "Any minor flavor adjustments to better match the concept"
            ]
        )
        
        try:
            # Generate suggestions with LLM using base advisor's method
            response = self._get_llm_response(
                "suggest_mechanics", 
                prompt, 
                {"concept": character_concept, "level": level_range, "type": mechanic_type}
            )
            
            # Parse the response into structured suggestions
            mechanic_suggestions = self._parse_suggestions_response(response)
            
            return {
                "success": True,
                "suggestions": mechanic_suggestions,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to generate mechanic suggestions: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate mechanic suggestions: {str(e)}"
            }
            
    def create_custom_mechanic(self, concept: str, mechanic_type: str, 
                             power_level: str = "balanced") -> Dict[str, Any]:
        """
        Create a custom game mechanic based on a concept.
        
        Args:
            concept: Brief description of the mechanic concept
            mechanic_type: Type of mechanic (spell, feature, ability, etc.)
            power_level: Desired power level (weak, balanced, strong)
            
        Returns:
            Dict[str, Any]: Custom mechanic design
        """
        # Build context for LLM
        context = f"Mechanic Concept: {concept}\n"
        context += f"Mechanic Type: {mechanic_type}\n"
        context += f"Power Level: {power_level}\n"
        
        # Create prompt using base advisor's format_prompt method
        prompt = self._format_prompt(
            f"create custom {mechanic_type}",
            context,
            [
                "Name for the custom mechanic",
                "Full description with thematic elements",
                "Precise mechanical effects and rules",
                "Required level, class, or prerequisites if applicable",
                "Comparable existing mechanics for reference",
                "Balance considerations and potential issues"
            ]
        )
        
        try:
            # Generate custom mechanic with LLM using base advisor's method
            response = self._get_llm_response(
                "create_custom_mechanic", 
                prompt, 
                {"concept": concept, "type": mechanic_type, "power": power_level}
            )
            
            # Parse the response into structured data
            custom_mechanic = self._parse_custom_mechanic_response(response)
            
            return {
                "success": True,
                "custom_mechanic": custom_mechanic,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to create custom mechanic: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create custom mechanic: {str(e)}"
            }
    
    # Helper methods
    
    def _get_mechanic_details(self, mechanics_id: str) -> Dict[str, Any]:
        """
        Get details of a mechanic by ID.
        
        This looks up the mechanic in the local data or fetches it from an API.
        """
        # First check if we have this in our local reference data
        if mechanics_id in self.mechanics_data:
            return self.mechanics_data[mechanics_id]
            
        # TODO: Implement API fetch or database lookup for mechanic details
        
        # For now, return a simple mock example for testing
        if mechanics_id == "fireball":
            return {
                "name": "Fireball",
                "type": "spell",
                "level": 3,
                "school": "evocation",
                "casting_time": "1 action",
                "range": "150 feet",
                "components": "V, S, M (a tiny ball of bat guano and sulfur)",
                "duration": "Instantaneous",
                "description": "A bright streak flashes from your pointing finger to a point you choose within range then blossoms with a low roar into an explosion of flame.",
                "mechanical_effect": "Each creature in a 20-foot-radius sphere centered on that point must make a Dexterity saving throw. A target takes 8d6 fire damage on a failed save, or half as much damage on a successful one.",
                "mechanics_details": {
                    "damage_type": "fire",
                    "damage_dice": "8d6",
                    "saving_throw": "DEX",
                    "area_of_effect": "20-foot-radius sphere"
                }
            }
        
        # Return empty dict if not found
        return {}
        
    def _parse_retheme_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for mechanic rethemeing."""
        # First try to use the BaseAdvisor's JSON extraction
        extracted_json = self._extract_json(response)
        if extracted_json:
            return extracted_json
            
        # If JSON extraction fails, fall back to regex parsing
        rethemed_data = {
            "name": "",
            "description": "",
            "visual_description": "",
            "variations": []
        }
        
        # Try to extract name
        name_match = re.search(r"(?:Name|Title):\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            rethemed_data["name"] = name_match.group(1).strip()
            
        # Try to extract description
        desc_match = re.search(r"(?:Description|Flavor Text)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z|\n(?=Visual|Appearance|Mechanics|Variations))", response, re.IGNORECASE)
        if desc_match:
            rethemed_data["description"] = desc_match.group(1).strip()
            
        # Try to extract visual description
        visual_match = re.search(r"(?:Visual|Appearance|Visuals)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z|\n(?=Mechanics|Variations))", response, re.IGNORECASE)
        if visual_match:
            rethemed_data["visual_description"] = visual_match.group(1).strip()
            
        # Try to extract variations
        variations = self._extract_list_items(response, ["Variation", "Alternative", "Option"])
        if variations:
            rethemed_data["variations"] = variations
            
        return rethemed_data
        
    def _parse_suggestions_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for mechanic suggestions."""
        # First try to use the BaseAdvisor's JSON extraction
        extracted_json = self._extract_json(response)
        if extracted_json and isinstance(extracted_json, list):
            return extracted_json
            
        # If JSON extraction fails, fall back to regex parsing
        suggestions = []
        
        # Look for numbered suggestions or sections
        suggestion_blocks = re.findall(r"(?:\d+\.|-)(?:\s*)([^\n]+(?:\n(?!(?:\d+\.|-|\Z))[^\n]+)*)", response)
        
        for block in suggestion_blocks:
            suggestion = {
                "name": "Unknown Mechanic",
                "explanation": "",
                "flavor_adjustments": ""
            }
            
            # Try to extract name
            name_match = re.search(r"^([^:]+)(?::|–|-)", block)
            if name_match:
                suggestion["name"] = name_match.group(1).strip()
            else:
                # Try first line if no colon format
                first_line = block.split("\n")[0].strip()
                if first_line:
                    suggestion["name"] = first_line
                    
            # Try to extract explanation
            explanation_match = re.search(r"(?:Explanation|Fits theme|Reason|How it fits)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z|\n(?=Flavor|Adjustment))", block, re.IGNORECASE)
            if explanation_match:
                suggestion["explanation"] = explanation_match.group(1).strip()
            else:
                # Try to extract from the middle part of the block
                parts = block.split("\n")
                if len(parts) >= 2:
                    suggestion["explanation"] = "\n".join(parts[1:]).strip()
                    
            # Try to extract flavor adjustments
            flavor_match = re.search(r"(?:Flavor|Adjustment|Customization)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if flavor_match:
                suggestion["flavor_adjustments"] = flavor_match.group(1).strip()
                
            suggestions.append(suggestion)
            
        return suggestions
        
    def _parse_custom_mechanic_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for custom mechanic creation."""
        # First try to use the BaseAdvisor's JSON extraction
        extracted_json = self._extract_json(response)
        if extracted_json:
            return extracted_json
            
        # If JSON extraction fails, fall back to regex parsing
        mechanic = {
            "name": "",
            "description": "",
            "mechanical_effect": "",
            "prerequisites": "",
            "comparable_mechanics": [],
            "balance_considerations": ""
        }
        
        # Try to extract name
        name_match = re.search(r"(?:Name|Title):\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            mechanic["name"] = name_match.group(1).strip()
            
        # Try to extract description
        desc_match = re.search(r"(?:Description|Flavor Text)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z|\n(?=Mechanic|Effect|Prerequisites|Level|Balance))", response, re.IGNORECASE)
        if desc_match:
            mechanic["description"] = desc_match.group(1).strip()
            
        # Try to extract mechanical effect
        effect_match = re.search(r"(?:Mechanical Effect|Mechanics|Effect|Rules)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z|\n(?=Prerequisites|Level|Comparable|Balance))", response, re.IGNORECASE)
        if effect_match:
            mechanic["mechanical_effect"] = effect_match.group(1).strip()
            
        # Try to extract prerequisites
        prereq_match = re.search(r"(?:Prerequisites|Required|Level)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z|\n(?=Comparable|Balance))", response, re.IGNORECASE)
        if prereq_match:
            mechanic["prerequisites"] = prereq_match.group(1).strip()
            
        # Try to extract comparable mechanics
        comparable = self._extract_list_items(response, ["Comparable", "Similar", "Reference"])
        if comparable:
            mechanic["comparable_mechanics"] = comparable
            
        # Try to extract balance considerations
        balance_match = re.search(r"(?:Balance|Considerations|Issues)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if balance_match:
            mechanic["balance_considerations"] = balance_match.group(1).strip()
            
        return mechanic