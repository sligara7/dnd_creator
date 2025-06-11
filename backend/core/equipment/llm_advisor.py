# llm_advisor.py
# Description: AI-powered equipment advisor for personalized recommendations and descriptions

from typing import Dict, List, Optional, Union, Any
import re
import json

from backend.core.services.ollama_service import OllamaService

class LLMEquipmentAdvisor:
    """
    LLM-powered advisor for equipment recommendations and descriptions.
    
    This class provides AI-enhanced capabilities for equipment selection,
    personalized recommendations, creative uses, and narrative descriptions
    to enrich the equipment experience for players.
    """
    
    def __init__(self, llm_service=None):
        """Initialize the equipment advisor with an optional LLM service."""
        self.llm_service = llm_service or OllamaService()
        self.model_context_length = 8192  # Default context length for most models
        
        # Temperature settings for different operations
        self.temperatures = {
            "recommendation": 0.7,  # Creative but still relevant recommendations
            "description": 0.8,     # Descriptive and creative text
            "analysis": 0.3,        # More factual tactical analysis
            "generation": 0.9,      # Creative for generating equipment concepts
            "system": 0.2           # More deterministic for system-level operations
        }
        
        # Store recent recommendations for continuity
        self.recent_recommendations = {}
    
    def _create_prompt(self, action_type: str, prompt_content: str) -> str:
        """
        Create a structured prompt for the LLM.
        
        Args:
            action_type: The type of action being requested
            prompt_content: The specific content for the prompt
            
        Returns:
            str: Formatted prompt
        """
        system_prompts = {
            "recommend weapons": (
                "You are an expert D&D equipment advisor specializing in weapons. "
                "Focus on providing mechanically sound weapon recommendations that match the character's "
                "abilities, class features, and fighting style. Include brief reasoning for each suggestion."
            ),
            "recommend armor": (
                "You are an expert D&D equipment advisor specializing in armor and protective gear. "
                "Recommend armor options that balance protection (AC) with the character's abilities "
                "and class features. Consider strength requirements and stealth penalties."
            ),
            "recommend gear": (
                "You are an expert D&D equipment advisor specializing in adventuring gear. "
                "Suggest practical gear that would be useful for the specified adventure context and "
                "character role. Focus on utility and problem-solving capabilities."
            ),
            "generate creative uses": (
                "You are an expert D&D equipment advisor with a talent for creative solutions. "
                "Suggest innovative, practical ways to use the specified item beyond its obvious purpose. "
                "These should be feasible within D&D 5e rules but showcase creative problem-solving."
            ),
            "generate tactical analysis": (
                "You are an expert D&D combat analyst. Provide a concise tactical assessment of this weapon "
                "based on the character's abilities. Include strengths, weaknesses, and optimal situations."
            ),
            "generate defensive analysis": (
                "You are an expert D&D combat analyst. Provide a concise defensive assessment of this armor "
                "based on the character's abilities. Include protection benefits, mobility considerations, "
                "and tactical implications."
            ),
            "suggest qualification path": (
                "You are an expert D&D character development advisor. Suggest realistic paths for the character "
                "to qualify for using this item, whether through training, ability improvements, feats, "
                "multiclassing, or other character development options within D&D 5e rules."
            ),
            "personalize starting equipment": (
                "You are an expert D&D equipment advisor. Suggest personalized starting equipment that "
                "aligns with the character's backstory and concept while remaining within standard starting "
                "equipment value ranges. Focus on thematic coherence and character expression."
            ),
            "create custom equipment": (
                "You are an expert D&D equipment designer. Create a balanced custom equipment item based "
                "on the provided concept. The item should be mechanically sound, appropriately priced, "
                "and fit the character's theme and level. Avoid creating overpowered items."
            ),
            "describe equipment appearance": (
                "You are an expert D&D equipment artisan. Provide a vivid, detailed description of this "
                "equipment's appearance, incorporating materials, craftsmanship, distinctive features, "
                "and aesthetic elements that reflect its origin and purpose."
            ),
            "create trade good description": (
                "You are an expert in D&D commerce and trade goods. Provide detailed information about "
                "this trade good, including its appearance, origins, value factors, and common uses in "
                "D&D economies and trading."
            ),
            "create detailed trade good description": (
                "You are an expert in D&D commerce and trading. Create a detailed description for this "
                "trade good that includes its physical properties, origins, cultural significance, and "
                "economic value in different regions of a fantasy world."
            ),
            "generate market information": (
                "You are an expert in D&D commerce and market systems. Provide detailed market information "
                "for this trade good, including regions where it's in demand, market fluctuations, and "
                "trading opportunities. Format as JSON."
            ),
            "create trade good origin story": (
                "You are a historian specializing in commerce and trade. Create an intriguing origin story "
                "for this trade good that explains how it became valuable, its historical significance, "
                "and any legends associated with it."
            ),
            "generate trade network": (
                "You are an expert in D&D economics and trade routes. Generate a comprehensive trade network "
                "between these regions, showing how goods flow between them and what trade advantages exist. "
                "Format as JSON."
            ),
            "optimize trade investment": (
                "You are a merchant advisor in a fantasy setting. Calculate an optimal investment distribution "
                "across these trade goods based on the given budget and optimization goal. Consider risk, "
                "return, and market factors. Format as JSON."
            ),
            "enhance trinket description": (
                "You are an expert in D&D trinkets and curiosities. Create a rich, detailed physical description "
                "of this trinket that brings it to life, focusing on its unique characteristics and mysterious "
                "qualities."
            ),
            "create trinket history": (
                "You are a collector of rare curiosities in a fantasy world. Create an intriguing history "
                "for this trinket, including potential origins, previous owners, and the circumstances "
                "that might have led to its current state."
            ),
            "create trinket personal significance": (
                "You are a D&D character development expert. Create a meaningful personal connection between "
                "this trinket and the character, explaining why it matters to them and how it might influence "
                "their story or decisions."
            ),
            "generate random trinket": (
                "You are a creator of unique D&D trinkets. Generate a distinctive, interesting trinket that "
                "follows the specified parameters. The trinket should provide flavor and storytelling opportunities "
                "without mechanical benefits. Format as JSON."
            ),
            "generate trinket table": (
                "You are a D&D trinket curator. Create a table of unique and interesting trinkets that players "
                "might discover. Each trinket should be small, intriguing, and potentially spark storytelling "
                "opportunities. Format as JSON."
            ),
            "enhance spellcasting focus description": (
                "You are an expert in magical implements. Create a detailed description of this spellcasting "
                "focus that highlights its unique characteristics, appearance, and subtle magical qualities. "
                "Focus on how it feels to cast spells through this implement."
            ),
            "create spellcasting focus history": (
                "You are a historian of magical artifacts. Create an interesting history for this spellcasting "
                "focus that includes its origins, previous owners, and any notable magical events it may have "
                "witnessed or participated in."
            ),
            "create spellcasting focus affinities": (
                "You are an expert in magical resonance. Describe which types of spells seem to have a particular "
                "affinity with this focus, and how spells might look or feel when cast through it. Format as JSON."
            ),
            "describe spellcasting visuals": (
                "You are a storyteller specializing in magical descriptions. Create a vivid, engaging description "
                "of how this spell appears when cast using the specified focus, including sensory details and "
                "distinctive visual elements."
            ),
            "recommend spellcasting focus": (
                "You are an expert in magical implements. Recommend appropriate spellcasting focuses for this "
                "character based on their class, background, and personal style. Include suggestions for "
                "appearance and materials that would resonate with the character. Format as JSON."
            ),
            "create material component kit": (
                "You are an expert in magical components. Create a comprehensive kit of material components "
                "that would be suitable for a spellcaster of this class and level. Include both common and "
                "specialized components with their magical purposes. Format as JSON."
            ),
            "recommend trinkets": (
                "You are a D&D trinket specialist. Recommend appropriate trinkets for this character based "
                "on their background, class, and backstory. Each trinket should provide storytelling opportunities "
                "and reflect aspects of the character's identity or history."
            ),
            "vehicle recommendations": (
                "You are an expert in D&D transportation and vehicles. Provide vehicle recommendations that "
                "suit the specified needs, terrain, and circumstances. Consider practical factors like speed, "
                "capacity, and terrain suitability as well as thematic elements."
            ),
            "create vehicle customization": (
                "You are a master craftsman specializing in vehicle modifications. Design balanced, creative "
                "customizations for this vehicle that enhance its functionality while maintaining game balance. "
                "Include appearance changes, practical improvements, and any special features."
            ),
            "generate travel scenario": (
                "You are a D&D adventure designer specializing in travel encounters. Create an interesting "
                "travel scenario involving this vehicle that provides challenges, opportunities for character "
                "development, and memorable moments."
            ),
            "generate vehicle challenge": (
                "You are a D&D gameplay designer. Create a balanced, interesting challenge or encounter "
                "that specifically involves this vehicle. The challenge should test the characters' abilities "
                "and the vehicle's capabilities in engaging ways."
            )
        }
        
        # Get the appropriate system prompt or use a generic one
        system_prompt = system_prompts.get(action_type, 
                                         "You are a D&D equipment advisor. Provide helpful, accurate information about D&D equipment.")
        
        # Construct the full prompt
        full_prompt = f"{system_prompt}\n\n{prompt_content}\n\nRespond with relevant, concise information."
        
        return full_prompt
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from the LLM response.
        
        Args:
            text: The text response from the LLM
            
        Returns:
            Dict[str, Any]: Extracted JSON data
        """
        # Try to find JSON between triple backticks
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find a JSON object anywhere in the text
        json_match = re.search(r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        # If no valid JSON was found, try to extract key information into a dict
        result = {}
        key_value_pattern = r"[\"']?(\w+)[\"']?\s*:\s*[\"']?(.*?)[\"']?(?:,|\n|$)"
        matches = re.findall(key_value_pattern, text)
        if matches:
            for key, value in matches:
                result[key.strip()] = value.strip()
            
            if result:
                return result
        
        # Return empty dict if nothing could be extracted
        return {}
    
    def recommend_weapons(self, character_data: Dict[str, Any], 
                        fighting_style: str = None, 
                        character_backstory: str = None) -> List[Dict[str, Any]]:
        """
        Recommend weapons based on character data.
        
        Args:
            character_data: Character information (class, abilities, etc.)
            fighting_style: Optional fighting style preference
            character_backstory: Optional character backstory for context
            
        Returns:
            List[Dict[str, Any]]: Recommended weapons with reasoning
        """
        # Prepare context for the LLM
        character_class = character_data.get("class", "Unknown")
        ability_scores = character_data.get("ability_scores", {})
        level = character_data.get("level", 1)
        
        # Extract key ability modifiers
        str_mod = (ability_scores.get("strength", 10) - 10) // 2
        dex_mod = (ability_scores.get("dexterity", 10) - 10) // 2
        
        # Create abbreviated backstory if provided
        backstory_excerpt = ""
        if character_backstory:
            # Limit backstory length to avoid overly long prompts
            backstory_excerpt = character_backstory[:500] + "..." if len(character_backstory) > 500 else character_backstory
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "recommend weapons",
            f"Character Class: {character_class}\n"
            f"Level: {level}\n"
            f"Strength Modifier: {str_mod}\n"
            f"Dexterity Modifier: {dex_mod}\n"
            f"Fighting Style: {fighting_style if fighting_style else 'Not specified'}\n"
            f"Backstory: {backstory_excerpt}\n\n"
            f"Recommend 5 weapons that would be suitable for this character, considering their abilities, "
            f"class features, and fighting style. For each weapon, provide a brief explanation of why it "
            f"would be effective for this character.\n\n"
            f"Format your response as a JSON array of objects, each with 'name', 'type', and 'reasoning' fields."
        )
        
        # Generate response
        response = self.llm_service.generate(prompt, temperature=self.temperatures["recommendation"])
        
        # Parse response
        parsed_data = self._extract_json(response)
        
        # Check if we got an array directly or need to extract it
        if isinstance(parsed_data, list):
            recommendations = parsed_data
        elif "recommendations" in parsed_data:
            recommendations = parsed_data["recommendations"]
        elif "weapons" in parsed_data:
            recommendations = parsed_data["weapons"]
        else:
            # Fallback: Create structured data from the raw response
            recommendations = []
            weapon_sections = re.split(r'\d+\.\s+', response)[1:]  # Split by numbered list
            
            for section in weapon_sections:
                if not section.strip():
                    continue
                
                # Try to extract weapon name and reasoning
                name_match = re.search(r'^([^:]+):', section)
                if name_match:
                    weapon_name = name_match.group(1).strip()
                    reasoning = section[name_match.end():].strip()
                    
                    recommendations.append({
                        "name": weapon_name,
                        "reasoning": reasoning
                    })
        
        # Store recommendations for context in future calls
        self.recent_recommendations["weapons"] = recommendations
        
        return recommendations
    
    def recommend_armor(self, character_data: Dict[str, Any],
                      character_style: str = None,
                      mobility_priority: int = 5) -> List[Dict[str, Any]]:
        """
        Recommend armor based on character data.
        
        Args:
            character_data: Character information (class, abilities, etc.)
            character_style: Optional character style/aesthetic preference
            mobility_priority: Importance of mobility (1-10)
            
        Returns:
            List[Dict[str, Any]]: Recommended armor with reasoning
        """
        # Prepare context for the LLM
        character_class = character_data.get("class", "Unknown")
        ability_scores = character_data.get("ability_scores", {})
        level = character_data.get("level", 1)
        
        # Extract key ability modifiers
        str_mod = (ability_scores.get("strength", 10) - 10) // 2
        dex_mod = (ability_scores.get("dexterity", 10) - 10) // 2
        strength_score = ability_scores.get("strength", 10)
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "recommend armor",
            f"Character Class: {character_class}\n"
            f"Level: {level}\n"
            f"Strength Score: {strength_score} (Modifier: {str_mod})\n"
            f"Dexterity Modifier: {dex_mod}\n"
            f"Style Preference: {character_style if character_style else 'Not specified'}\n"
            f"Mobility Priority: {mobility_priority}/10\n\n"
            f"Recommend 3-5 armor options that would be suitable for this character, considering their class, "
            f"abilities, style preference, and mobility needs. For each armor, provide a brief explanation "
            f"of why it would be effective for this character.\n\n"
            f"Format your response as a JSON array of objects, each with 'name', 'type', and 'reasoning' fields."
        )
        
        # Generate response
        response = self.llm_service.generate(prompt, temperature=self.temperatures["recommendation"])
        
        # Parse response
        parsed_data = self._extract_json(response)
        
        # Check if we got an array directly or need to extract it
        if isinstance(parsed_data, list):
            recommendations = parsed_data
        elif "recommendations" in parsed_data:
            recommendations = parsed_data["recommendations"]
        elif "armor" in parsed_data:
            recommendations = parsed_data["armor"]
        else:
            # Fallback: Create structured data from the raw response
            recommendations = []
            armor_sections = re.split(r'\d+\.\s+', response)[1:]  # Split by numbered list
            
            for section in armor_sections:
                if not section.strip():
                    continue
                
                # Try to extract armor name and reasoning
                name_match = re.search(r'^([^:]+):', section)
                if name_match:
                    armor_name = name_match.group(1).strip()
                    reasoning = section[name_match.end():].strip()
                    
                    recommendations.append({
                        "name": armor_name,
                        "reasoning": reasoning
                    })
        
        # Store recommendations for context in future calls
        self.recent_recommendations["armor"] = recommendations
        
        return recommendations
    
    def recommend_gear(self, adventure_context: str = None,
                    character_role: str = None,
                    budget: int = None) -> List[Dict[str, Any]]:
        """
        Recommend adventuring gear based on adventure context.
        
        Args:
            adventure_context: Description of upcoming adventure/environment
            character_role: Character's role in the party
            budget: Optional budget limit in gold pieces
            
        Returns:
            List[Dict[str, Any]]: Recommended gear with reasoning
        """
        # Create prompt for the LLM
        budget_str = f"Budget: {budget} gold pieces" if budget else "Budget: Unspecified"
        
        prompt = self._create_prompt(
            "recommend gear",
            f"Adventure Context: {adventure_context if adventure_context else 'General adventuring'}\n"
            f"Character Role: {character_role if character_role else 'Not specified'}\n"
            f"{budget_str}\n\n"
            f"Recommend 5-8 pieces of adventuring gear that would be useful for this context and role. "
            f"For each item, provide a brief explanation of how it would be useful in this specific situation. "
            f"{'Ensure the total stays within the specified budget.' if budget else ''}\n\n"
            f"Format your response as a JSON array of objects, each with 'name', 'cost', and 'reasoning' fields."
        )
        
        # Generate response
        response = self.llm_service.generate(prompt, temperature=self.temperatures["recommendation"])
        
        # Parse response
        parsed_data = self._extract_json(response)
        
        # Check if we got an array directly or need to extract it
        if isinstance(parsed_data, list):
            recommendations = parsed_data
        elif "recommendations" in parsed_data:
            recommendations = parsed_data["recommendations"]
        elif "gear" in parsed_data:
            recommendations = parsed_data["gear"]
        else:
            # Fallback: Create structured data from the raw response
            recommendations = []
            gear_sections = re.split(r'\d+\.\s+', response)[1:]  # Split by numbered list
            
            for section in gear_sections:
                if not section.strip():
                    continue
                
                # Try to extract gear name and reasoning
                name_match = re.search(r'^([^:]+):', section)
                if name_match:
                    gear_name = name_match.group(1).strip()
                    reasoning = section[name_match.end():].strip()
                    
                    # Try to extract cost if mentioned
                    cost_match = re.search(r'(\d+)(?:\s*)(gp|sp|cp)', reasoning)
                    cost = cost_match.group(1) + " " + cost_match.group(2) if cost_match else "unknown"
                    
                    recommendations.append({
                        "name": gear_name,
                        "cost": cost,
                        "reasoning": reasoning
                    })
        
        return recommendations
    
    def generate_creative_uses(self, item_name: str, 
                             item_description: str = "",
                             situation: str = None) -> List[Dict[str, Any]]:
        """
        Generate creative uses for an equipment item.
        
        Args:
            item_name: Name of the item
            item_description: Description of the item
            situation: Optional specific situation to consider
            
        Returns:
            List[Dict[str, Any]]: List of creative uses
        """
        situation_context = f"Situation: {situation}\n" if situation else ""
        
        prompt = self._create_prompt(
            "generate creative uses",
            f"Item: {item_name}\n"
            f"Description: {item_description}\n"
            f"{situation_context}\n"
            f"Generate 5 creative, unconventional uses for this item that are possible within D&D 5e rules. "
            f"These should go beyond the item's standard purpose but remain plausible. "
            f"{'Consider how this item could be particularly useful in the specified situation.' if situation else ''}\n\n"
            f"For each use, provide a brief name/title and a description of how it would work.\n\n"
            f"Format your response as a JSON array of objects, each with 'title' and 'description' fields."
        )
        
        # Generate response
        response = self.llm_service.generate(prompt, temperature=self.temperatures["generation"])
        
        # Parse response
        parsed_data = self._extract_json(response)
        
        # Check if we got an array directly or need to extract it
        if isinstance(parsed_data, list):
            creative_uses = parsed_data
        elif "uses" in parsed_data:
            creative_uses = parsed_data["uses"]
        elif "creative_uses" in parsed_data:
            creative_uses = parsed_data["creative_uses"]
        else:
            # Fallback: Create structured data from the raw response
            creative_uses = []
            use_sections = re.split(r'\d+\.\s+', response)[1:]  # Split by numbered list
            
            for section in use_sections:
                if not section.strip():
                    continue
                
                # Try to extract use title and description
                title_match = re.search(r'^([^:]+):', section)
                if title_match:
                    use_title = title_match.group(1).strip()
                    description = section[title_match.end():].strip()
                    
                    creative_uses.append({
                        "title": use_title,
                        "description": description
                    })
        
        return creative_uses
    
    def generate_tactical_analysis(self, weapon_data: Dict[str, Any],
                                ability_scores: Dict[str, int],
                                proficiency_bonus: int = 2) -> Dict[str, Any]:
        """
        Generate tactical analysis for a weapon.
        
        Args:
            weapon_data: Weapon data
            ability_scores: Character ability scores
            proficiency_bonus: Character proficiency bonus
            
        Returns:
            Dict[str, Any]: Tactical analysis
        """
        # Extract relevant weapon information
        weapon_name = weapon_data.get("name", "Unknown")
        weapon_type = weapon_data.get("category", "Unknown")
        damage_dice = weapon_data.get("damage_dice", "1d6")
        damage_type = weapon_data.get("damage_type", "Unknown")
        properties = ", ".join(weapon_data.get("properties", []))
        
        # Extract relevant ability scores
        str_mod = (ability_scores.get("strength", 10) - 10) // 2
        dex_mod = (ability_scores.get("dexterity", 10) - 10) // 2
        
        prompt = self._create_prompt(
            "generate tactical analysis",
            f"Weapon: {weapon_name}\n"
            f"Type: {weapon_type}\n"
            f"Damage: {damage_dice} {damage_type}\n"
            f"Properties: {properties}\n"
            f"Character Strength Modifier: {str_mod}\n"
            f"Character Dexterity Modifier: {dex_mod}\n"
            f"Proficiency Bonus: {proficiency_bonus}\n\n"
            f"Provide a concise tactical analysis of this weapon that includes:\n"
            f"1. Overall assessment of effectiveness\n"
            f"2. Optimal combat scenarios\n"
            f"3. Limitations or weaknesses\n"
            f"4. Special tactics or techniques\n"
            f"5. Synergies with common class features\n\n"
            f"Format your response as a JSON object with 'overall_assessment', 'optimal_scenarios', 'limitations', 'special_tactics', and 'synergies' fields."
        )
        
        # Generate response
        response = self.llm_service.generate(prompt, temperature=self.temperatures["analysis"])
        
        # Parse response
        parsed_data = self._extract_json(response)
        
        # If parsing failed, create a simple structure from the text
        if not parsed_data:
            # Split response into sections based on common headers
            sections = {}
            current_section = "overall_assessment"
            section_text = ""
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a section header
                lower_line = line.lower()
                if any(header in lower_line for header in ["overall", "assessment", "effectiveness"]):
                    current_section = "overall_assessment"
                    section_text = ""
                elif any(header in lower_line for header in ["optimal", "scenarios", "situations"]):
                    sections[current_section] = section_text.strip()
                    current_section = "optimal_scenarios"
                    section_text = ""
                elif any(header in lower_line for header in ["limitations", "weaknesses", "drawbacks"]):
                    sections[current_section] = section_text.strip()
                    current_section = "limitations"
                    section_text = ""
                elif any(header in lower_line for header in ["special", "tactics", "techniques"]):
                    sections[current_section] = section_text.strip()
                    current_section = "special_tactics"
                    section_text = ""
                elif any(header in lower_line for header in ["synergies", "class features"]):
                    sections[current_section] = section_text.strip()
                    current_section = "synergies"
                    section_text = ""
                else:
                    section_text += line + " "
            
            # Add the last section
            sections[current_section] = section_text.strip()
            
            parsed_data = sections
        
        return parsed_data
    
    def generate_defensive_analysis(self, armor_data: Dict[str, Any],
                                 dexterity_modifier: int) -> Dict[str, Any]:
        """
        Generate defensive analysis for armor.
        
        Args:
            armor_data: Armor data
            dexterity_modifier: Character's dexterity modifier
            
        Returns:
            Dict[str, Any]: Defensive analysis
        """
        # Extract relevant armor information
        armor_name = armor_data.get("name", "Unknown")
        armor_type = armor_data.get("category", "Unknown")
        base_ac = armor_data.get("base_ac", 10)
        dex_bonus_allowed = armor_data.get("dex_bonus_allowed", True)
        max_dex_bonus = armor_data.get("max_dex_bonus", None)
        stealth_disadvantage = armor_data.get("stealth_disadvantage", False)
        strength_required = armor_data.get("strength_required", 0)
        
        # Calculate total AC
        applied_dex_mod = 0
        if dex_bonus_allowed:
            if max_dex_bonus is not None:
                applied_dex_mod = min(dexterity_modifier, max_dex_bonus)
            else:
                applied_dex_mod = dexterity_modifier
                
        total_ac = base_ac + applied_dex_mod
        
        prompt = self._create_prompt(
            "generate defensive analysis",
            f"Armor: {armor_name}\n"
            f"Type: {armor_type}\n"
            f"Base AC: {base_ac}\n"
            f"Dexterity Modifier: {dexterity_modifier}\n"
            f"Applied Dexterity Modifier: {applied_dex_mod}\n"
            f"Total AC: {total_ac}\n"
            f"Stealth Disadvantage: {stealth_disadvantage}\n"
            f"Strength Required: {strength_required}\n\n"
            f"Provide a concise defensive analysis of this armor that includes:\n"
            f"1. Overall protection assessment\n"
            f"2. Mobility implications\n"
            f"3. Stealth considerations\n"
            f"4. Suitable combat situations\n"
            f"5. Class synergies\n\n"
            f"Format your response as a JSON object with 'protection_assessment', 'mobility_impact', 'stealth_considerations', 'suitable_situations', and 'class_synergies' fields."
        )
        
        # Generate response
        response = self.llm_service.generate(prompt, temperature=self.temperatures["analysis"])
        
        # Parse response
        parsed_data = self._extract_json(response)
        
        # If parsing failed, create a simple structure from the text
        if not parsed_data:
            # Split response into sections based on common headers
            sections = {}
            current_section = "protection_assessment"
            section_text = ""
            
            for line in response.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a section header
                lower_line = line.lower()
                if any(header in lower_line for header in ["protection", "assessment", "overview"]):
                    current_section = "protection_assessment"
                    section_text = ""
                elif any(header in lower_line for header in ["mobility", "movement", "agility"]):
                    sections[current_section] = section_text.strip()
                    current_section = "mobility_impact"
                    section_text = ""
                elif any(header in lower_line for header in ["stealth", "hiding", "detection"]):
                    sections[current_section] = section_text.strip()
                    current_section = "stealth_considerations"
                    section_text = ""
                elif any(header in lower_line for header in ["suitable", "situations", "combat"]):
                    sections[current_section] = section_text.strip()
                    current_section = "suitable_situations"
                    section_text = ""
                elif any(header in lower_line for header in ["class", "synergies", "synergy"]):
                    sections[current_section] = section_text.strip()
                    current_section = "class_synergies"
                    section_text = ""
                else:
                    section_text += line + " "
            
            # Add the last section
            sections[current_section] = section_text.strip()
            
            parsed_data = sections
        
        return parsed_data
    
    def suggest_qualification_path(self, character_data: Dict[str, Any],
                                item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest ways for a character to qualify for using an item.
        
        Args:
            character_data: Character data
            item_data: Equipment item data
            
        Returns:
            Dict[str, Any]: Qualification path suggestions
        """
        # Extract character information
        character_class = character_data.get("class", "Unknown")
        level = character_data.get("level", 1)
        ability_scores = character_data.get("ability_scores", {})
        proficiencies = character_data.get("proficiencies", {})
        
        # Extract item information
        item_name = item_data.get("name", "Unknown")
        item_category = item_data.get("category", "Unknown")
        requirements = []
        
        # Determine requirements
        if "strength_required" in item_data and item_data["strength_required"] > 0:
            requirements.append(f"Strength {item_data['strength_required']}+")
        
        if isinstance(item_category, str) and "martial" in item_category.lower():
            requirements.append("Martial weapon proficiency")
            
        requirements_str = ", ".join(requirements) if requirements else "No specific requirements"
        
        prompt = self._create_prompt(
            "suggest qualification path",
            f"Character Class: {character_class}\n"
            f"Level: {level}\n"
            f"Ability Scores: {json.dumps(ability_scores)}\n"
            f"Proficiencies: {json.dumps(proficiencies)}\n\n"
            f"Item: {item_name}\n"
            f"Category: {item_category}\n"
            f"Requirements: {requirements_str}\n\n"
            f"The character currently does not meet the requirements to use this item effectively. "
            f"Suggest practical paths for the character to qualify for using this item, such as:\n"
            f"1. Ability score improvements\n"
            f"2. Feats that grant necessary proficiencies\n"
            f"3. Multiclassing options\n"
            f"4. Training opportunities (if using downtime rules)\n"
            f"5. Items that could compensate for requirements\n\n"
            f"For each suggestion, explain the benefits and any tradeoffs involved.\n\n"
            f"Format your response as a JSON object with 'qualification_paths', 'recommended_approach', and 'time_required' fields."
        )
        
        # Generate response
        response = self.llm_service.generate(prompt, temperature=self.temperatures["recommendation"])
        
        # Parse response
        parsed_data = self._extract_json(response)
        
        # Add the original requirements for reference
        if parsed_data:
            parsed_data["item_requirements"] = requirements
        else:
            # Create a basic structure if parsing failed
            parsed_data = {
                "item_requirements": requirements,
                "qualification_paths": ["Ability score improvement", "Multiclassing", "Feats"],
                "recommended_approach": "Choose a path based on your character's goals and playstyle",
                "time_required": "Varies based on approach chosen"
            }
        
        return parsed_data
    
    def generate_personalized_starting_equipment(self, 
                                              class_name: str,
                                              background_name: str,
                                              backstory: str = None) -> Dict[str, Any]:
        """
        Generate personalized starting equipment based on character details.
        
        Args:
            class_name: Character class
            background_name: Character background
            backstory: Character backstory
            
        Returns:
            Dict[str, Any]: Personalized equipment suggestions
        """
        backstory_excerpt = ""
        if backstory:
            # Limit backstory length to avoid overly long prompts
            backstory_excerpt = backstory[:500] + "..." if len(backstory) > 500 else backstory
        
        prompt = self._create_prompt(
            "personalize starting equipment",
            f"Character Class: {class_name}\n"
            f"Background: {background_name}\n"
            f"Backstory: {backstory_excerpt}\n\n"
            f"Based on this character's class, background, and backstory, suggest personalized starting equipment "
            f"that fits their theme and narrative. Consider their life experiences, skills, and connections "
            f"mentioned in the backstory. Suggest equipment that would be meaningful to them or reflect "
            f"their history.\n\n"
            f"Your suggestions should be reasonable alternatives to standard starting equipment, not additional items. "
            f"Maintain approximate equivalent value to standard starting equipment.\n\n"
            f"Provide your response as a JSON object with 'weapon_suggestions', 'armor_suggestions', 'gear_suggestions', "
            f"'personal_items', and 'rationale' fields."
        )
        
        # Generate response
        response = self.llm_service.generate(prompt, temperature=self.temperatures["recommendation"])
        
        # Parse response
        parsed_data = self._extract_json(response)
        
        # If parsing failed, return a simple structure
        if not parsed_data:
            parsed_data = {
                "weapon_suggestions": [f"Standard {class_name} weapons"],
                "armor_suggestions": [f"Standard {class_name} armor"],
                "gear_suggestions": [f"Standard {background_name} equipment"],
                "personal_items": ["Personalized token based on backstory"],
                "rationale": "Based on standard equipment packages with slight personalization"
            }
        
        return parsed_data
    
    def create_custom_equipment(self, concept: str = None,
                             equipment_type: str = None,
                             partial_data: Dict[str, Any] = None,
                             character_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create custom equipment based on a concept.
        
        Args:
            concept: Equipment concept description
            equipment_type: Type of equipment to create
            partial_data: Partial equipment data to complete
            character_data: Character data for context
            
        Returns:
            Dict[str, Any]: Custom equipment data
        """
        # Build character context if provided
        character_context = ""
        if character_data:
            character_context = (f"Character Class: {character_data.get('class', 'Unknown')}\n"
                               f"Level: {character_data.get('level', 1)}\n"
                               f"Background: {character_data.get('background', 'Unknown')}\n")
        
        # Build partial data context if provided
        partial_data_context = ""
        if partial_data:
            partial_data_context = f"Existing Equipment Data: {json.dumps(partial_data)}\n"
        
        equipment_type_str = equipment_type if equipment_type else "general equipment"
        
        prompt = self._create_prompt(
            "create custom equipment",
            f"Equipment Concept: {concept}\n"
            f"Equipment Type: {equipment_type_str}\n"
            f"{partial_data_context}"
            f"{character_context}\n"
            f"Create a balanced custom {equipment_type_str} item based on this concept. The item should follow D&D 5e "
            f"equipment design principles and be appropriate for the character's level and needs. "
            f"Provide complete details including name, description, mechanical properties, and a reasonable cost.\n\n"
            f"Format your response as a complete JSON object with all necessary fields for this equipment type."
        )
        
        # Generate response
        response = self.llm_service.generate(prompt, temperature=self.temperatures["generation"])
        
        # Parse response
        custom_item = self._extract_json(response)
        
        # If parsing failed, create a minimal structure
        if not custom_item:
            custom_item = {
                "name": f"Custom {equipment_type_str}" if equipment_type else "Custom Item",
                "type": equipment_type if equipment_type else "item",
                "description": concept if concept else "A custom piece of equipment",
                "cost": {"gp": 10},
                "weight": 1
            }
        
        return custom_item
    
    def recommend_trinkets(self, background: str = None, 
                        character_class: str = None, 
                        backstory: str = None,
                        count: int = 1) -> List[Dict[str, Any]]:
        """
        Recommend appropriate trinkets for a character based on their details.
        
        Args:
            background: Character background
            character_class: Character class
            backstory: Character backstory for LLM matching
            count: Number of trinkets to return
            
        Returns:
            List[Dict[str, Any]]: List of suitable trinkets
        """
        backstory_excerpt = ""
        if backstory:
            # Limit backstory length to avoid overly long prompts
            backstory_excerpt = backstory[:500] + "..." if len(backstory) > 500 else backstory
            
        prompt = self._create_prompt(
            "recommend trinkets",
            f"Character Class: {character_class if character_class else 'Not specified'}\n"
            f"Background: {background if background else 'Not specified'}\n"
            f"Backstory: {backstory_excerpt}\n"
            f"Number of Trinkets: {count}\n\n"
            f"Create {count} unique and interesting trinkets that would be particularly meaningful or appropriate "
            f"for this character based on their background, class, and backstory. Each trinket should be small, "
            f"non-magical (though possibly magical in appearance), and provide flavor and storytelling opportunities.\n\n"
            f"For each trinket, provide a name, description, and how it might connect to the character's story.\n\n"
            f"Format your response as a JSON array of objects, each with 'name', 'description', and 'connection' fields."
        )
        
        # Generate response
        response = self.llm_service.generate(prompt, temperature=self.temperatures["generation"])
        
        # Parse response
        parsed_data = self._extract_json(response)
        
        # Check if we got an array directly or need to extract it
        if isinstance(parsed_data, list):
            trinkets = parsed_data
        elif "trinkets" in parsed_data:
            trinkets = parsed_data["trinkets"]
        elif "recommendations" in parsed_data:
            trinkets = parsed_data["recommendations"]
        else:
            # Fallback: Create structured data from the raw response
            trinkets = []
            trinket_sections = re.split(r'\d+\.\s+', response)[1:]  # Split by numbered list
            
            for section in trinket_sections[:count]:  # Limit to requested count
                if not section.strip():
                    continue
                
                # Try to extract trinket name and description
                name_match = re.search(r'^([^:]+):', section)
                if name_match:
                    trinket_name = name_match.group(1).strip()
                    description = section[name_match.end():].strip()
                    
                    trinkets.append({
                        "name": trinket_name,
                        "description": description,
                        "connection": f"Related to {background if background else 'character'} background"
                    })
        
        # Ensure we have the requested number of trinkets
        while len(trinkets) < count:
            trinkets.append({
                "name": f"Mysterious Trinket {len(trinkets) + 1}",
                "description": "A curious item with an unclear purpose.",
                "connection": "Its significance may be revealed in time."
            })
        
        return trinkets[:count]  # Return only the requested number
    
    def generate_vehicle_options(self, terrain_types: List[str],
                              passenger_capacity: int,
                              purpose: str,
                              distance: str = None) -> List[Dict[str, Any]]:
        """
        Generate appropriate vehicle options for given needs.
        
        Args:
            terrain_types: List of terrain types the vehicle must traverse
            passenger_capacity: Required passenger capacity
            purpose: Main purpose of the vehicle
            distance: Optional travel distance requirement
            
        Returns:
            List[Dict[str, Any]]: List of vehicle recommendations
        """
        terrain_str = ", ".join(terrain_types)
        distance_str = f"Travel Distance: {distance}\n" if distance else ""
        
        prompt = self._create_prompt(
            "vehicle recommendations",
            f"Terrain Types: {terrain_str}\n"
            f"Passenger Capacity: {passenger_capacity}\n"
            f"Purpose: {purpose}\n"
            f"{distance_str}\n"
            f"Recommend 3-5 vehicle options suitable for these requirements in a D&D 5e setting. "
            f"For each vehicle, provide its name, basic description, pros and cons for the specified requirements, "
            f"and approximate cost.\n\n"
            f"Format your response as a JSON array of objects, each with 'name', 'description', 'pros', 'cons', and 'cost' fields."
        )
        
        # Generate response
        response = self.llm_service.generate(prompt, temperature=self.temperatures["recommendation"])
        
        # Parse response
        parsed_data = self._extract_json(response)
        
        # Check if we got an array directly or need to extract it
        if isinstance(parsed_data, list):
            vehicles = parsed_data
        elif "vehicles" in parsed_data:
            vehicles = parsed_data["vehicles"]
        elif "recommendations" in parsed_data:
            vehicles = parsed_data["recommendations"]
        else:
            # Fallback: Create structured data from the raw response
            vehicles = []
            vehicle_sections = re.split(r'\d+\.\s+', response)[1:]  # Split by numbered list
            
            for section in vehicle_sections:
                if not section.strip():
                    continue
                
                # Try to extract vehicle name and details
                name_match = re.search(r'^([^:]+):', section)
                if name_match:
                    vehicle_name = name_match.group(1).strip()
                    details = section[name_match.end():].strip()
                    
                    # Try to extract structured information
                    desc_match = re.search(r'Description:?\s*(.*?)(?:Pros:|Advantages:|Cost:|$)', details, re.DOTALL)
                    pros_match = re.search(r'Pros:?\s*(.*?)(?:Cons:|Disadvantages:|Cost:|$)', details, re.DOTALL)
                    cons_match = re.search(r'Cons:?\s*(.*?)(?:Cost:|Price:|$)', details, re.DOTALL)
                    cost_match = re.search(r'Cost:?\s*(.*?)(?:$)', details, re.DOTALL)
                    
                    description = desc_match.group(1).strip() if desc_match else "No description available"
                    pros = pros_match.group(1).strip() if pros_match else "Standard vehicle advantages"
                    cons = cons_match.group(1).strip() if cons_match else "Standard vehicle limitations"
                    cost = cost_match.group(1).strip() if cost_match else "Price varies by quality and region"
                    
                    vehicles.append({
                        "name": vehicle_name,
                        "description": description,
                        "pros": pros,
                        "cons": cons,
                        "cost": cost
                    })
        
        return vehicles
    
    def generate_vehicle_customization(self, vehicle_data: Dict[str, Any],
                                    customization_goal: str,
                                    budget: int = None) -> Dict[str, Any]:
        """
        Generate customization options for a vehicle.
        
        Args:
            vehicle_data: Base vehicle data
            customization_goal: Goal of the customization
            budget: Optional budget in gold pieces
            
        Returns:
            Dict[str, Any]: Customization suggestions
        """
        vehicle_name = vehicle_data.get("name", "Unknown vehicle")
        vehicle_description = vehicle_data.get("description", "No description available")
        budget_str = f"Budget: {budget} gold pieces" if budget else "Budget: Unspecified"
        
        prompt = self._create_prompt(
            "create vehicle customization",
            f"Vehicle: {vehicle_name}\n"
            f"Base Description: {vehicle_description}\n"
            f"Customization Goal: {customization_goal}\n"
            f"{budget_str}\n\n"
            f"Suggest balanced, creative customizations for this vehicle that would help achieve the stated goal while "
            f"maintaining game balance. Include cosmetic changes, functional modifications, and any special features "
            f"that could be added. {'Ensure suggestions stay within the specified budget.' if budget else ''}\n\n"
            f"Provide your response as a JSON object with 'appearance_changes', 'functional_modifications', 'special_features', "
            f"'total_cost', and 'time_required' fields."
        )
        
        # Generate response
        response = self.llm_service.generate(prompt, temperature=self.temperatures["generation"])
        
        # Parse response
        parsed_data = self._extract_json(response)
        
        # If parsing failed, return a basic structure
        if not parsed_data:
            parsed_data = {
                "appearance_changes": ["Custom paint or decoration", "Thematic detailing"],
                "functional_modifications": ["Basic improvements based on goal"],
                "special_features": ["One special feature aligned with customization goal"],
                "total_cost": budget if budget else "Varies based on implementation",
                "time_required": "Several days of work by skilled craftspeople"
            }
        
        return parsed_data