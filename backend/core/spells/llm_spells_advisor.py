# Customizing Spell System with Llama 3/Ollama Integration
# Each function in spell.py can be enhanced through LLM interactions to provide a personalized spellcasting experience:

import re
import json
import os
from typing import Dict, List, Any, Optional, Union, Tuple
from functools import lru_cache

from backend.core.ollama_service import OllamaService

class LLMSpellsAdvisor:
    """
    LLM-powered advisor for enhancing D&D spellcasting experience with personalized
    recommendations, creative uses, and custom spells using Ollama/Llama 3.
    """
    
    def __init__(self):
        """Initialize the LLM spells advisor with Ollama service and caching."""
        self.ollama_service = OllamaService()
        
        # System message for D&D spell advice
        self.system_message = (
            "You are a D&D 5e (2024 Edition) expert assistant specializing in spellcasting. "
            "Provide rule-consistent, creative, and personalized advice about spells and "
            "spellcasting. Keep responses concise and focused on the question."
        )
        
        # For caching common responses
        self._response_cache = {}
        
        # Standard D&D spell schools for validation
        self.spell_schools = [
            "abjuration", "conjuration", "divination", "enchantment",
            "evocation", "illusion", "necromancy", "transmutation"
        ]
    
    @lru_cache(maxsize=100)
    def recommend_spells_by_personality(
        self, 
        personality_traits: str, 
        class_name: str, 
        values: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recommend spells based on character personality.
        
        Args:
            personality_traits (str): Character's personality traits
            class_name (str): Character's class
            values (str): Character's values or ideals
            limit (int): Maximum number of spells to recommend
            
        Returns:
            List[Dict[str, Any]]: List of recommended spells
        """
        prompt = (
            f"You are a {class_name} who values {values} and has these personality traits: {personality_traits}. "
            f"Recommend {limit} thematically appropriate spells that would resonate with your character's nature. "
            f"Format your response as JSON with an array of spell objects containing 'name', 'level', 'school', and "
            f"'thematic_reason' fields. Only include official D&D 5e (2024) spells."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            # Extract JSON from response
            spell_data = self._extract_json(response)
            if isinstance(spell_data, list):
                return spell_data
            if isinstance(spell_data, dict) and "spells" in spell_data:
                return spell_data["spells"]
                
            # If we couldn't extract a list directly, try to parse the response
            return self._parse_spell_list(response)
            
        except Exception as e:
            print(f"Error recommending spells by personality: {e}")
            return []
    
    def get_creative_spell_uses(self, spell_name: str, spell_details: Dict[str, Any] = None) -> List[str]:
        """
        Provide creative examples of how a spell could be used beyond its obvious applications.
        
        Args:
            spell_name (str): Name of the spell
            spell_details (Dict[str, Any], optional): Known spell details
            
        Returns:
            List[str]: List of creative uses
        """
        details_text = ""
        if spell_details:
            details_text = (
                f"Spell description: {spell_details.get('description', 'Not provided')}. "
                f"Level: {spell_details.get('level', 'Unknown')}. "
                f"School: {spell_details.get('school', 'Unknown')}."
            )
        
        prompt = (
            f"Provide 3-5 creative and unconventional ways to use the spell '{spell_name}' "
            f"beyond its obvious applications in D&D 5e (2024). {details_text} "
            f"Focus on applications that are technically allowed by the rules but that "
            f"players might not immediately consider. List each use in a brief paragraph."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        # Extract creative uses from response
        uses = []
        for line in response.split("\n"):
            # Clean the line
            line = line.strip()
            
            # Skip empty lines and numbering
            if not line or re.match(r'^\d+[\.\)]?\s*$', line):
                continue
                
            # Remove numbering if present
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            
            # If the line seems substantial enough to be a creative use
            if len(line) > 20:  # Arbitrary threshold
                uses.append(line)
        
        return uses
    
    @lru_cache(maxsize=50)
    def recommend_class_spells(
        self, 
        class_name: str, 
        level: Optional[int] = None, 
        character_background: Optional[str] = None, 
        playstyle: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend spells based on class, background, and playstyle.
        
        Args:
            class_name (str): Character's class
            level (int, optional): Character level or spell level
            character_background (str, optional): Character's background
            playstyle (str, optional): Character's preferred playstyle
            
        Returns:
            List[Dict[str, Any]]: List of recommended spells
        """
        level_text = f" at level {level}" if level is not None else ""
        background_text = f" with a background as a {character_background}" if character_background else ""
        playstyle_text = f" who focuses on {playstyle}" if playstyle else ""
        
        prompt = (
            f"I'm playing a {class_name}{level_text}{background_text}{playstyle_text}. "
            f"What spells would align well with this character concept? "
            f"Return at least 6 spells as JSON with fields: name, level, and why it fits my concept."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            # Extract JSON from response
            spell_data = self._extract_json(response)
            if isinstance(spell_data, list):
                return spell_data
            if isinstance(spell_data, dict) and "spells" in spell_data:
                return spell_data["spells"]
                
            # If we couldn't extract JSON, try to parse the response
            return self._parse_spell_list(response)
            
        except Exception as e:
            print(f"Error recommending class spells: {e}")
            return []
    
    def explain_spell_save_dc_implications(self, dc: int, character_level: Optional[int] = None) -> str:
        """
        Explain the tactical implications of a spell save DC.
        
        Args:
            dc (int): Spell save DC value
            character_level (int, optional): Character's level for context
            
        Returns:
            str: Explanation of tactical implications
        """
        level_text = f" for a level {character_level} character" if character_level else ""
        
        prompt = (
            f"My spell save DC is {dc}{level_text}. What does this mean for my effectiveness "
            f"against different types of enemies in D&D 5e (2024)? Provide a brief tactical "
            f"analysis of how this DC compares to typical saving throw bonuses for monsters "
            f"of appropriate challenge ratings, and which types of saving throws would be "
            f"more effective with this DC."
        )
        
        return self.ollama_service.generate_text(prompt, self.system_message)
    
    def compare_spell_attack_vs_saves(self, attack_bonus: int, save_dc: int) -> str:
        """
        Compare advantages of spell attacks vs. saving throw spells.
        
        Args:
            attack_bonus (int): Spell attack bonus
            save_dc (int): Spell save DC
            
        Returns:
            str: Comparison and strategic advice
        """
        # Check if we have this in cache
        cache_key = f"attack_vs_saves_{attack_bonus}_{save_dc}"
        if cache_key in self._response_cache:
            return self._response_cache[cache_key]
        
        prompt = (
            f"With a +{attack_bonus} spell attack bonus and DC {save_dc} saves, when should I "
            f"prefer attack roll spells vs. save spells in D&D 5e (2024)? Please provide a "
            f"brief strategic analysis considering factors like target AC vs. saving throw "
            f"bonuses, advantage/disadvantage mechanics, critical hits, and common monster types."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        # Cache the response
        self._response_cache[cache_key] = response
        return response
    
    def suggest_spell_loadout(
        self, 
        class_name: str, 
        level: int, 
        ability_score: int, 
        environment: str = "dungeon", 
        adventure_context: str = ""
    ) -> Dict[str, List[str]]:
        """
        Suggest optimal spell loadout based on context.
        
        Args:
            class_name (str): Character's class
            level (int): Character level
            ability_score (int): Spellcasting ability score
            environment (str): Adventure environment
            adventure_context (str): Additional context about the adventure
            
        Returns:
            Dict[str, List[str]]: Dictionary of spell levels and recommended spells
        """
        # Calculate rough spell limit
        ability_mod = (ability_score - 10) // 2
        if class_name.lower() in ["wizard", "cleric", "druid"]:
            spell_limit = level + ability_mod
        elif class_name.lower() in ["paladin", "ranger"]:
            spell_limit = level // 2 + ability_mod
        else:
            spell_limit = level + ability_mod
        
        context = f" We're {adventure_context}" if adventure_context else ""
        
        prompt = (
            f"I can prepare {spell_limit} spells as a level {level} {class_name}. "
            f"We're traveling through {environment}.{context} What's a good spell selection? "
            f"Organize by spell level and provide a brief reason for each spell. "
            f"Format as JSON with spell levels as keys and arrays of spell objects as values. "
            f"Each spell object should have 'name' and 'reason' fields."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            # Try to extract JSON
            result = self._extract_json(response)
            
            # If result is already in the format we need
            if isinstance(result, dict) and all(isinstance(key, (str, int)) and isinstance(value, list) for key, value in result.items()):
                return result
                
            # Process the response into the desired format
            spell_loadout = {}
            lines = response.split("\n")
            current_level = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if line is a spell level header
                level_match = re.match(r'(?:Level|Spell Level)\s*(\d+)', line, re.IGNORECASE)
                if level_match or line.lower().startswith("cantrips"):
                    if line.lower().startswith("cantrips"):
                        current_level = "0"
                    else:
                        current_level = level_match.group(1)
                    spell_loadout[current_level] = []
                    continue
                
                # If we're within a level section and find a spell
                if current_level is not None:
                    spell_match = re.match(r'[-*•]?\s*([A-Za-z\s]+)(?:[:-]\s*(.+))?', line)
                    if spell_match:
                        spell_name = spell_match.group(1).strip()
                        reason = spell_match.group(2).strip() if spell_match.group(2) else "Recommended spell"
                        spell_loadout[current_level].append({"name": spell_name, "reason": reason})
            
            return spell_loadout
            
        except Exception as e:
            print(f"Error suggesting spell loadout: {e}")
            # Return a basic structure if parsing fails
            return {"0": [], "1": [], "2": []}
    
    def create_custom_spell(
        self, 
        concept: str, 
        class_name: str, 
        level: Optional[int] = None, 
        similar_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a custom spell based on character concept.
        
        Args:
            concept (str): Brief description of the spell concept
            class_name (str): Character class creating the spell
            level (int, optional): Desired spell level
            similar_to (str, optional): Existing spell to use as reference
            
        Returns:
            Dict[str, Any]: Custom spell details
        """
        level_text = f" at level {level}" if level is not None else ""
        reference_text = f" similar to {similar_to} but with unique aspects" if similar_to else ""
        
        prompt = (
            f"Create a custom D&D 5e (2024) spell for a {class_name}{level_text} with this concept: '{concept}'{reference_text}. "
            f"The spell should be balanced and follow D&D spell design principles. "
            f"Return the spell in JSON format with these fields: name, level, school, casting_time, range, "
            f"components, duration, description, higher_levels (if applicable), classes, "
            f"and damage/healing (if applicable)."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            # Extract JSON from response
            spell_data = self._extract_json(response)
            
            # Basic validation
            required_fields = ["name", "level", "school", "casting_time", "range", "components", "duration", "description"]
            for field in required_fields:
                if field not in spell_data:
                    spell_data[field] = "Unknown"
                    
            # Ensure classes includes the requesting class
            if "classes" not in spell_data or not spell_data["classes"]:
                spell_data["classes"] = [class_name]
            elif class_name not in spell_data["classes"]:
                spell_data["classes"].append(class_name)
                
            return spell_data
            
        except Exception as e:
            print(f"Error creating custom spell: {e}")
            # Return a basic spell structure
            return {
                "name": f"{concept.title()} Spell",
                "level": level or 1,
                "school": "evocation",
                "casting_time": "1 action",
                "range": "60 feet",
                "components": "V, S",
                "duration": "Instantaneous",
                "description": f"A custom spell that embodies the concept: {concept}",
                "classes": [class_name]
            }
    
    def get_spell_details(self, spell_name: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a spell using LLM if not in standard database.
        
        Args:
            spell_name (str): Name of the spell
            
        Returns:
            Dict[str, Any] or None: Spell details or None if not found/created
        """
        prompt = (
            f"Provide detailed information about the D&D 5e (2024) spell '{spell_name}'. "
            f"Return the information in JSON format with these fields: name, level, school, "
            f"casting_time, range, components, duration, description, higher_levels (if applicable), "
            f"classes, and damage/healing details (if applicable)."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            # Extract JSON from response
            spell_data = self._extract_json(response)
            
            # If the response indicates the spell doesn't exist
            if "unknown" in response.lower() or "not found" in response.lower():
                return None
                
            return spell_data
            
        except Exception as e:
            print(f"Error getting spell details: {e}")
            return None
    
    def get_class_spell_list(self, class_name: str, level: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get a list of spells for a class at a specific level.
        
        Args:
            class_name (str): Name of the class
            level (int, optional): Character level or spell level
            
        Returns:
            List[Dict[str, Any]]: List of spells
        """
        level_text = f" at level {level}" if level is not None else ""
        
        prompt = (
            f"List the standard spells available to a {class_name}{level_text} in D&D 5e (2024). "
            f"Return the list in JSON format as an array of spell objects, each with 'name', 'level', "
            f"and 'school' fields. If level refers to spell level, list spells of that level; "
            f"if it refers to character level, list all spells available up to the appropriate spell level."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            # Extract JSON from response
            spell_data = self._extract_json(response)
            
            if isinstance(spell_data, list):
                return spell_data
            if isinstance(spell_data, dict) and "spells" in spell_data:
                return spell_data["spells"]
                
            # If we couldn't extract structured data, parse the response
            return self._parse_spell_list(response)
            
        except Exception as e:
            print(f"Error getting class spell list: {e}")
            return []
    
    def search_spells(self, query: str, **filters) -> List[Dict[str, Any]]:
        """
        Search for spells matching query and filters.
        
        Args:
            query (str): Search query
            **filters: Additional filters like level, school, class, etc.
            
        Returns:
            List[Dict[str, Any]]: List of matching spells
        """
        filters_text = ", ".join(f"{k}={v}" for k, v in filters.items())
        
        prompt = (
            f"Search for D&D 5e (2024) spells matching the query: '{query}' "
            f"with these filters: {filters_text if filters else 'none'}. "
            f"Return the results in JSON format as an array of spell objects, "
            f"each with 'name', 'level', 'school', and 'classes' fields."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            # Extract JSON from response
            spell_data = self._extract_json(response)
            
            if isinstance(spell_data, list):
                return spell_data
            if isinstance(spell_data, dict) and "spells" in spell_data:
                return spell_data["spells"]
                
            # If we couldn't extract structured data, parse the response
            return self._parse_spell_list(response)
            
        except Exception as e:
            print(f"Error searching spells: {e}")
            return []
    
    def explain_optimal_spellcasting(
        self,
        spell_name: str,
        character_class: str,
        character_level: int,
        target_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Provides tactical advice for optimal use of a spell.
        
        Args:
            spell_name (str): Name of the spell
            character_class (str): Character's class
            character_level (int): Character's level
            target_info (str, optional): Information about the target(s)
            
        Returns:
            Dict[str, Any]: Tactical advice and optimization tips
        """
        target_text = f" against {target_info}" if target_info else ""
        
        prompt = (
            f"Provide tactical advice for optimal use of the spell '{spell_name}' by a level {character_level} "
            f"{character_class}{target_text}. Include spell slot optimization, positioning, "
            f"timing, and any class features that enhance this spell. Return as JSON with 'tactical_advice', "
            f"'optimization_tips', and 'class_synergies' fields."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            # Extract JSON from response
            return self._extract_json(response)
        except Exception as e:
            print(f"Error explaining optimal spellcasting: {e}")
            return {
                "tactical_advice": "Use the spell when it provides the most tactical advantage.",
                "optimization_tips": "Consider the spell slot level based on the encounter difficulty.",
                "class_synergies": f"Leverage your {character_class} class features with this spell."
            }
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        # Find JSON pattern in response
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})```', text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
            else:
                # Look for array pattern
                array_match = re.search(r'\[.*\]', text, re.DOTALL)
                if array_match:
                    json_text = array_match.group(0)
                else:
                    raise ValueError("No JSON found in response")
        
        # Clean up potential markdown and whitespace
        json_text = re.sub(r'^\s*```.*\n', '', json_text)
        json_text = re.sub(r'\n\s*```\s*$', '', json_text)
        
        return json.loads(json_text)
    
    def _parse_spell_list(self, text: str) -> List[Dict[str, Any]]:
        """Parse spell list from text when JSON extraction fails"""
        spells = []
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to match spell entries like "Fireball (3rd level, Evocation)"
            spell_match = re.match(r'(?:\d+\.\s*)?([A-Za-z\s]+)(?:\s*\((?:(\d)(?:st|nd|rd|th)? level)?(?:,\s*([A-Za-z]+))?\))?', line)
            if spell_match:
                spell_name = spell_match.group(1).strip()
                level_str = spell_match.group(2) if spell_match.group(2) else "0"
                school = spell_match.group(3).strip().lower() if spell_match.group(3) else "unknown"
                
                # Add to the list if it looks like a valid spell
                if len(spell_name) > 2:
                    spells.append({
                        "name": spell_name,
                        "level": int(level_str),
                        "school": school
                    })
        
        return spells