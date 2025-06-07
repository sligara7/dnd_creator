"""
LLM NPC Advisor Module

Provides AI-powered assistance for single NPC creation and enhancement using LLM integration.
This module helps DMs create rich, detailed non-player characters with unique personalities,
backgrounds, and motivations.
"""

from typing import Dict, List, Any, Optional, Union
import json
import datetime
import re
from pathlib import Path

from backend.core.advisor.base_advisor import BaseAdvisor
from backend.core.ability_scores.ability_scores import AbilityScores
from backend.core.npc.abstract_npc import AbstractNPC

import logging
logger = logging.getLogger(__name__)

class LLMNPCAdvisor(BaseAdvisor):
    """
    Provides AI-powered assistance for D&D NPC creation and enhancement.
    
    This class integrates with Language Learning Models (LLMs) to provide creative
    assistance for individual NPC creation, focusing on personality, background,
    motivations, mannerisms, and other roleplay elements.
    """

    def __init__(self, llm_service=None, data_path: str = None, cache_enabled=True):
        """
        Initialize the LLM NPC advisor.
        
        Args:
            llm_service: LLM service client for generating responses
            data_path: Optional path to NPC data
            cache_enabled: Whether to enable response caching
        """
        # Initialize base advisor with NPC-specific system prompt
        system_prompt = "You are a D&D 5e NPC creation expert specializing in creating rich, believable characters with compelling personalities and backgrounds."
        super().__init__(llm_service, system_prompt, cache_enabled)
            
        # Set up paths and data
        self.data_path = Path(data_path) if data_path else Path("backend/data/npcs")
        self.ability_scores = AbilityScores()
        self._load_reference_data()

    def _load_reference_data(self):
        """Load reference data for NPC creation."""
        try:
            # Load occupation data
            occupation_path = self.data_path / "occupations.json"
            if occupation_path.exists():
                with open(occupation_path, "r") as f:
                    self.occupation_data = json.load(f)
            else:
                self.occupation_data = {}
                
            # Load culture/race data
            culture_path = self.data_path / "cultures.json"
            if culture_path.exists():
                with open(culture_path, "r") as f:
                    self.culture_data = json.load(f)
            else:
                self.culture_data = {}
                
            # Load personality trait data
            personality_path = self.data_path / "personality_traits.json"
            if personality_path.exists():
                with open(personality_path, "r") as f:
                    self.personality_data = json.load(f)
            else:
                self.personality_data = {}
                
        except Exception as e:
            logger.error(f"Error loading reference data: {e}")
            self.occupation_data = {}
            self.culture_data = {}
            self.personality_data = {}

    def create_npc(self, role_description: str, campaign_theme: str = None, 
                  location: str = None) -> Dict[str, Any]:
        """
        Generate a thematically coherent NPC based on role and campaign needs.
        
        Args:
            role_description: Description of the NPC's role in the story/world
            campaign_theme: Optional campaign theme for thematic consistency
            location: Optional location where the NPC is based
            
        Returns:
            Dict[str, Any]: Suggested NPC data
        """
        # Build context for LLM
        context = f"Role Description: {role_description}\n"
        
        if campaign_theme:
            context += f"Campaign Theme: {campaign_theme}\n"
            
        if location:
            context += f"Location: {location}\n"
            
        # Create prompt using base advisor's format_prompt method
        prompt = self._format_prompt(
            "generate a detailed NPC",
            context,
            [
                "Name, gender, race, and age",
                "Occupation and social status",
                "Physical appearance and distinctive features",
                "Personality traits, ideals, bonds, and flaws",
                "Brief background and personal history",
                "Motivations, goals, and secrets",
                "Speech patterns and mannerisms"
            ]
        )
        
        try:
            # Generate NPC concept with LLM using base advisor's method
            response = self._get_llm_response(
                "npc_create", 
                prompt, 
                {"role": role_description[:50], "theme": campaign_theme}
            )
            
            # Parse the response into structured NPC data
            npc_data = self._parse_npc_response(response)
            
            # Add metadata
            npc_data["metadata"] = {
                "generated_at": datetime.datetime.now().isoformat(),
                "role_description": role_description,
                "generation_method": "llm_assisted"
            }
            
            return {
                "success": True,
                "npc_concept": npc_data,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to generate NPC concept: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate NPC concept: {str(e)}"
            }

    def validate_npc(self, npc_data: Dict[str, Any], 
                   check_narrative_coherence: bool = True) -> Dict[str, Any]:
        """
        Validate NPC and provide feedback on narrative coherence and roleplaying potential.
        
        Args:
            npc_data: NPC data to validate
            check_narrative_coherence: Whether to include detailed narrative feedback
            
        Returns:
            Dict[str, Any]: Validation results with suggestions
        """
        # Basic validation first (standard checks)
        standard_validation = self._validate_npc_basics(npc_data)
        
        # If not requesting narrative feedback or validation failed critically, return basic results
        if not check_narrative_coherence or not standard_validation.get("is_valid", False):
            return standard_validation
            
        # Create context for narrative assessment
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'unknown')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'unknown')}\n"
        
        # Add personality info
        personality = npc_data.get("personality", {})
        if personality:
            if "traits" in personality:
                context += f"Traits: {', '.join(personality['traits'])}\n"
            if "ideals" in personality:
                context += f"Ideals: {personality['ideals']}\n"
            if "bonds" in personality:
                context += f"Bonds: {personality['bonds']}\n"
            if "flaws" in personality:
                context += f"Flaws: {personality['flaws']}\n"
                
        # Add background info
        if "background" in npc_data:
            context += f"Background: {npc_data['background'][:100]}...\n"
            
        # Use base advisor's format_prompt method
        prompt = self._format_prompt(
            "assess npc narrative coherence",
            context,
            [
                "Assessment of overall narrative coherence",
                "Specific elements that might be inconsistent",
                "Suggestions to enhance the NPC's roleplaying potential",
                "Additional details that could make this NPC more memorable"
            ]
        )
        
        try:
            # Generate narrative assessment using base advisor's method
            response = self._get_llm_response(
                "npc_validate", 
                prompt, 
                {"npc": npc_data.get("name", "unknown")}
            )
            
            # Parse the assessment
            assessment = self._parse_narrative_assessment(response)
            
            # Combine with standard validation
            standard_validation["narrative_assessment"] = assessment
            standard_validation["has_narrative_feedback"] = True
            
            return standard_validation
        except Exception as e:
            logger.error(f"Error during narrative assessment: {str(e)}")
            standard_validation["narrative_assessment"] = {"error": str(e)}
            standard_validation["has_narrative_feedback"] = False
            return standard_validation

    def generate_npc_stat_block(self, npc_data: Dict[str, Any], 
                              competence_level: str = "average",
                              include_class_levels: bool = False) -> Dict[str, Any]:
        """
        Generate appropriate stats for an NPC based on their role and background.
        
        Args:
            npc_data: Basic NPC data (name, race, background, etc.)
            competence_level: Level of competence (novice, average, expert, legendary)
            include_class_levels: Whether to treat as character with class levels
            
        Returns:
            Dict[str, Any]: NPC stats suitable for gameplay
        """
        # Build context for LLM
        context = f"NPC: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'Human')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'Commoner')}\n"
        context += f"Competence Level: {competence_level}\n"
        
        if "background" in npc_data:
            context += f"Background Summary: {npc_data['background'][:100]}...\n"
            
        if include_class_levels:
            context += "Include Character Class Levels: Yes\n"
            
        # Use base advisor's format_prompt method
        prompt = self._format_prompt(
            "generate npc stats",
            context,
            [
                "Ability scores (STR, DEX, CON, INT, WIS, CHA)",
                "HP, AC, and proficiency bonus",
                "Key skill proficiencies aligned with background",
                "Notable equipment or items they possess",
                f"{'Class levels and class features' if include_class_levels else 'Special abilities related to occupation'}"
            ]
        )
        
        try:
            # Generate NPC stats using base advisor's method
            response = self._get_llm_response(
                "npc_stats", 
                prompt, 
                {"npc": npc_data.get("name", "unknown"), "level": competence_level}
            )
            
            # Parse the response into structured stats
            stat_data = self._parse_stat_block_response(response)
            
            # Calculate any derived values
            if "ability_scores" in stat_data:
                modifiers = {}
                for ability, score in stat_data["ability_scores"].items():
                    modifiers[ability] = self.ability_scores.calculate_modifier(score)
                stat_data["ability_modifiers"] = modifiers
            
            return {
                "success": True,
                "npc_stats": stat_data,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to generate NPC stats: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate NPC stats: {str(e)}"
            }

    def generate_npc_dialog(self, npc_data: Dict[str, Any],
                          conversation_context: str,
                          player_statement: str = None) -> Dict[str, Any]:
        """
        Generate dialogue for an NPC based on their personality and the context.
        
        Args:
            npc_data: NPC data containing personality and background
            conversation_context: Context of the conversation
            player_statement: Optional statement from player to respond to
            
        Returns:
            Dict[str, Any]: Dialogue options for the NPC
        """
        # Build context for LLM
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'Human')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'Commoner')}\n\n"
        
        # Add personality info
        personality = npc_data.get("personality", {})
        if personality:
            context += "Personality:\n"
            if "traits" in personality:
                context += f"- Traits: {', '.join(personality['traits'])}\n"
            if "ideals" in personality:
                context += f"- Ideals: {personality['ideals']}\n"
            if "bonds" in personality:
                context += f"- Bonds: {personality['bonds']}\n"
            if "flaws" in personality:
                context += f"- Flaws: {personality['flaws']}\n"
                
        # Add speech pattern if available
        if "speech_pattern" in npc_data:
            context += f"\nSpeech Pattern: {npc_data['speech_pattern']}\n"
            
        # Add conversation context
        context += f"\nConversation Context: {conversation_context}\n"
        
        if player_statement:
            context += f"Player Statement: \"{player_statement}\"\n"
            
        # Use base advisor's format_prompt method
        prompt = self._format_prompt(
            "generate npc dialogue",
            context,
            [
                "A friendly/helpful response with appropriate tone and mannerisms",
                "A neutral/cautious response with appropriate tone and mannerisms",
                "A hostile/suspicious response with appropriate tone and mannerisms",
                "Include appropriate speech patterns and non-verbal cues in each response"
            ]
        )
        
        try:
            # Generate dialogue using base advisor's method
            response = self._get_llm_response(
                "npc_dialogue", 
                prompt, 
                {"npc": npc_data.get("name", "unknown"), "context": conversation_context[:50]}
            )
            
            # Parse the response into structured dialogue options
            dialogue_options = self._parse_dialogue_response(response)
            
            return {
                "success": True,
                "dialogue_options": dialogue_options,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to generate dialogue: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate dialogue: {str(e)}"
            }

    def generate_npc_backstory(self, npc_data: Dict[str, Any], 
                             detail_level: str = "moderate",
                             focus_area: str = None) -> Dict[str, Any]:
        """
        Generate a detailed backstory for an NPC expanding on their basic information.
        
        Args:
            npc_data: Basic NPC data
            detail_level: Level of detail desired (brief, moderate, detailed)
            focus_area: Optional area to focus on (e.g., "childhood", "profession", "trauma")
            
        Returns:
            Dict[str, Any]: Expanded backstory elements
        """
        # Build context for LLM
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'Human')}\n"
        context += f"Age: {npc_data.get('age', 'Adult')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'Commoner')}\n"
        context += f"Detail Level: {detail_level}\n"
        
        # Add existing background if available
        if "background" in npc_data:
            context += f"\nExisting Background: {npc_data['background']}\n"
            
        # Add personality info
        personality = npc_data.get("personality", {})
        if personality:
            context += "\nPersonality Summary:\n"
            if "traits" in personality:
                context += f"- Traits: {', '.join(personality['traits'])}\n"
            if "ideals" in personality:
                context += f"- Ideals: {personality['ideals']}\n"
            if "bonds" in personality:
                context += f"- Bonds: {personality['bonds']}\n"
            if "flaws" in personality:
                context += f"- Flaws: {personality['flaws']}\n"
        
        if focus_area:
            context += f"\nFocus Area: {focus_area}\n"
            
        # Use base advisor's format_prompt method
        prompt = self._format_prompt(
            "generate npc backstory",
            context,
            [
                "Formative childhood experiences",
                "Key relationships and their influence",
                "Significant life events that shaped them",
                "How they entered their current occupation",
                "Recent history leading to their current situation",
                "A secret or hidden aspect of their past"
            ]
        )
        
        try:
            # Generate backstory using base advisor's method
            response = self._get_llm_response(
                "npc_backstory", 
                prompt, 
                {"npc": npc_data.get("name", "unknown"), "detail": detail_level}
            )
            
            # Parse the response into structured backstory elements
            backstory = self._parse_backstory_response(response)
            
            return {
                "success": True,
                "backstory": backstory,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to generate backstory: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate backstory: {str(e)}"
            }

    def generate_npc_connections(self, npc_data: Dict[str, Any], 
                               location_description: str = None,
                               num_connections: int = 3) -> Dict[str, Any]:
        """
        Generate social connections for an NPC within their community.
        
        Args:
            npc_data: Basic NPC data
            location_description: Description of where the NPC lives
            num_connections: Number of connections to generate
            
        Returns:
            Dict[str, Any]: Social connections and relationships
        """
        # Build context for LLM
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'Human')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'Commoner')}\n"
        context += f"Number of Connections: {num_connections}\n"
        
        if "background" in npc_data:
            context += f"\nBackground Summary: {npc_data['background'][:100]}...\n"
            
        if location_description:
            context += f"Location: {location_description}\n"
            
        # Add personality info
        personality = npc_data.get("personality", {})
        if personality:
            if "bonds" in personality:
                context += f"Existing Bonds: {personality['bonds']}\n"
                
        # Use base advisor's format_prompt method
        prompt = self._format_prompt(
            "generate npc connections",
            context,
            [
                "For each connection, provide name and basic details",
                "Nature of the relationship (family, friend, rival, mentor, etc.)",
                "History of how they became connected",
                "Current state of the relationship",
                "How this relationship influences the NPC's decisions or behavior"
            ]
        )
        
        try:
            # Generate connections using base advisor's method
            response = self._get_llm_response(
                "npc_connections", 
                prompt, 
                {"npc": npc_data.get("name", "unknown"), "count": num_connections}
            )
            
            # Parse the response into structured connections
            connections = self._parse_connections_response(response)
            
            return {
                "success": True,
                "connections": connections,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to generate connections: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate connections: {str(e)}"
            }

    def generate_npc_secrets_and_hooks(self, npc_data: Dict[str, Any],
                                      hook_type: str = "mixed",
                                      num_hooks: int = 3) -> Dict[str, Any]:
        """
        Generate secrets and adventure hooks related to this NPC.
        
        Args:
            npc_data: NPC data
            hook_type: Type of hooks to generate (personal, quest, faction, mixed)
            num_hooks: Number of hooks to generate
            
        Returns:
            Dict[str, Any]: Secrets and adventure hooks
        """
        # Build context for LLM
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'Human')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'Commoner')}\n"
        context += f"Hook Type: {hook_type}\n"
        context += f"Number of Hooks: {num_hooks}\n"
        
        # Add background/personality if available
        if "background" in npc_data:
            context += f"\nBackground Summary: {npc_data['background'][:100]}...\n"
            
        if "personality" in npc_data and "flaws" in npc_data["personality"]:
            context += f"Flaws: {npc_data['personality']['flaws']}\n"
            
        # Use base advisor's format_prompt method
        prompt = self._format_prompt(
            "generate npc secrets and hooks",
            context,
            [
                "For each hook/secret, provide the basic secret or situation",
                "How players might discover it",
                "Potential adventure developments if pursued",
                "NPCs or locations connected to this hook",
                "Possible rewards or consequences for the players"
            ]
        )
        
        try:
            # Generate hooks using base advisor's method
            response = self._get_llm_response(
                "npc_hooks", 
                prompt, 
                {"npc": npc_data.get("name", "unknown"), "type": hook_type, "count": num_hooks}
            )
            
            # Parse the response into structured hooks
            hooks_and_secrets = self._parse_hooks_response(response)
            
            return {
                "success": True,
                "hooks_and_secrets": hooks_and_secrets,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to generate hooks and secrets: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate hooks and secrets: {str(e)}"
            }

    def suggest_npc_development(self, npc_data: Dict[str, Any],
                              campaign_events: List[str] = None,
                              time_passed: str = "one month") -> Dict[str, Any]:
        """
        Suggest how an NPC might develop or change over time.
        
        Args:
            npc_data: Current NPC data
            campaign_events: List of significant events that have occurred
            time_passed: Amount of time that has passed
            
        Returns:
            Dict[str, Any]: Suggested developments for the NPC
        """
        # Build context for LLM
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Time Passed: {time_passed}\n"
        
        # Add personality info
        personality = npc_data.get("personality", {})
        if personality:
            context += "\nPersonality:\n"
            if "traits" in personality:
                context += f"- Traits: {', '.join(personality['traits'])}\n"
            if "ideals" in personality:
                context += f"- Ideals: {personality['ideals']}\n"
            if "bonds" in personality:
                context += f"- Bonds: {personality['bonds']}\n"
            if "flaws" in personality:
                context += f"- Flaws: {personality['flaws']}\n"
                
        if "goals" in npc_data:
            context += f"\nCurrent Goals: {npc_data['goals']}\n"
            
        if campaign_events:
            context += "\nSignificant Events:\n"
            for event in campaign_events:
                context += f"- {event}\n"
                
        # Use base advisor's format_prompt method
        prompt = self._format_prompt(
            "suggest npc development",
            context,
            [
                "Changes to their immediate circumstances or status",
                "Evolution of their goals or motivations",
                "Changes to their emotional state or outlook",
                "New relationships or modified existing relationships",
                "Practical actions they've taken during this time",
                "New secrets or knowledge they've acquired"
            ]
        )
        
        try:
            # Generate development ideas using base advisor's method
            response = self._get_llm_response(
                "npc_development", 
                prompt, 
                {"npc": npc_data.get("name", "unknown"), "time": time_passed}
            )
            
            # Parse the response
            development = self._parse_development_response(response)
            
            return {
                "success": True,
                "development": development,
                "time_frame": time_passed,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to generate NPC development: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate NPC development: {str(e)}"
            }

    # Domain-specific helper methods

    def _validate_npc_basics(self, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform basic validation of NPC data."""
        errors = []
        warnings = []
        
        # Check for required fields
        required_fields = ["name", "race"]
        for field in required_fields:
            if field not in npc_data:
                errors.append(f"Missing required field: {field}")
        
        # Check personality components
        personality = npc_data.get("personality", {})
        if not personality:
            warnings.append("Missing personality information")
        else:
            for trait_type in ["traits", "ideals", "bonds", "flaws"]:
                if trait_type not in personality:
                    warnings.append(f"Personality is missing {trait_type}")
        
        # Check for background
        if "background" not in npc_data:
            warnings.append("Missing background information")
            
        # Check for occupation
        if "occupation" not in npc_data:
            warnings.append("Missing occupation information")
        
        return {
            "is_valid": len(errors) == 0,
            "validation_errors": errors,
            "validation_warnings": warnings
        }

    def _convert_to_markdown(self, npc_data: Dict[str, Any]) -> str:
        """Convert NPC data to markdown format."""
        md = f"# {npc_data.get('name', 'Unnamed NPC')}\n\n"
        md += f"*{npc_data.get('race', 'Unknown Race')} {npc_data.get('occupation', '')}*\n\n"
        
        # Basic information
        md += "## Basic Information\n\n"
        
        if "age" in npc_data:
            md += f"**Age:** {npc_data['age']}\n\n"
            
        if "gender" in npc_data:
            md += f"**Gender:** {npc_data['gender']}\n\n"
            
        if "appearance" in npc_data:
            md += f"**Appearance:** {npc_data['appearance']}\n\n"
        
        # Personality
        personality = npc_data.get("personality", {})
        if personality:
            md += "## Personality\n\n"
            
            if "traits" in personality:
                md += f"**Traits:** {', '.join(personality['traits'])}\n\n"
                
            if "ideals" in personality:
                md += f"**Ideals:** {personality['ideals']}\n\n"
                
            if "bonds" in personality:
                md += f"**Bonds:** {personality['bonds']}\n\n"
                
            if "flaws" in personality:
                md += f"**Flaws:** {personality['flaws']}\n\n"
        
        # Background
        if "background" in npc_data:
            md += "## Background\n\n"
            md += f"{npc_data['background']}\n\n"
            
        # Motivations & Goals
        if "motivations" in npc_data or "goals" in npc_data:
            md += "## Motivations & Goals\n\n"
            
            if "motivations" in npc_data:
                md += f"**Motivations:** {npc_data['motivations']}\n\n"
                
            if "goals" in npc_data:
                md += f"**Goals:** {npc_data['goals']}\n\n"
                
        # Secrets
        if "secrets" in npc_data:
            md += "## Secrets\n\n"
            md += f"{npc_data['secrets']}\n\n"
            
        # Connections
        if "connections" in npc_data:
            md += "## Connections\n\n"
            connections = npc_data["connections"]
            for connection in connections:
                md += f"- **{connection.get('name', 'Unnamed')}** ({connection.get('relationship', 'Unknown')}): {connection.get('description', '')}\n"
            md += "\n"
            
        # Stats if available
        if "stats" in npc_data:
            stats = npc_data["stats"]
            md += "## Game Statistics\n\n"
            
            if "ability_scores" in stats:
                ability_scores = stats["ability_scores"]
                md += "| STR | DEX | CON | INT | WIS | CHA |\n"
                md += "|-----|-----|-----|-----|-----|-----|\n"
                md += f"| {ability_scores.get('strength', 10)} | {ability_scores.get('dexterity', 10)} | "
                md += f"{ability_scores.get('constitution', 10)} | {ability_scores.get('intelligence', 10)} | "
                md += f"{ability_scores.get('wisdom', 10)} | {ability_scores.get('charisma', 10)} |\n\n"
                
            if "hp" in stats:
                md += f"**HP:** {stats['hp']}\n\n"
                
            if "ac" in stats:
                md += f"**AC:** {stats['ac']}\n\n"
                
            if "skills" in stats:
                md += f"**Skills:** {', '.join(stats['skills'])}\n\n"
                
        return md

    # Parser methods for LLM responses
    
    def _parse_npc_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for NPC generation."""
        # First try to use the BaseAdvisor's JSON extraction
        extracted_json = self._extract_json(response)
        if extracted_json:
            npc_data = {
                "name": "Unknown NPC",
                "race": "Human",
                "gender": "Unknown",
                "age": "Adult",
                "occupation": "Commoner",
                "personality": {
                    "traits": [],
                    "ideals": "",
                    "bonds": "",
                    "flaws": ""
                }
            }
            return {**npc_data, **extracted_json}
        
        # If JSON extraction fails, fall back to regex parsing
        npc_data = {
            "name": "Unknown NPC",
            "race": "Human",
            "gender": "Unknown",
            "age": "Adult",
            "occupation": "Commoner",
            "personality": {
                "traits": [],
                "ideals": "",
                "bonds": "",
                "flaws": ""
            }
        }
        
        # Try to extract name
        name_match = re.search(r"(?:Name|NPC):\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            npc_data["name"] = name_match.group(1).strip()
            
        # Try to extract race
        race_match = re.search(r"(?:Race|Species):\s*([^\n]+)", response, re.IGNORECASE)
        if race_match:
            npc_data["race"] = race_match.group(1).strip()
            
        # Try to extract gender
        gender_match = re.search(r"(?:Gender|Sex):\s*([^\n]+)", response, re.IGNORECASE)
        if gender_match:
            npc_data["gender"] = gender_match.group(1).strip()
            
        # Try to extract age
        age_match = re.search(r"(?:Age):\s*([^\n]+)", response, re.IGNORECASE)
        if age_match:
            npc_data["age"] = age_match.group(1).strip()
            
        # Try to extract occupation
        occupation_match = re.search(r"(?:Occupation|Profession|Job):\s*([^\n]+)", response, re.IGNORECASE)
        if occupation_match:
            npc_data["occupation"] = occupation_match.group(1).strip()
            
        # Try to extract appearance
        appearance_match = re.search(r"(?:Appearance|Looks|Physical)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if appearance_match:
            npc_data["appearance"] = appearance_match.group(1).strip()
            
        # Try to extract distinctive features
        features_match = re.search(r"(?:Distinctive|Features|Characteristics)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if features_match:
            npc_data["distinctive_features"] = features_match.group(1).strip()
            
        # Try to extract personality traits
        traits_match = re.search(r"(?:Personality|Traits)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if traits_match:
            traits_text = traits_match.group(1).strip()
            # Split by commas or bullet points
            traits = re.findall(r"(?:[-•*]\s*|^)([^,\n-•*][^,\n]*)", traits_text)
            if traits:
                npc_data["personality"]["traits"] = [t.strip() for t in traits if t.strip()]
            else:
                traits = [t.strip() for t in traits_text.split(",")]
                npc_data["personality"]["traits"] = [t for t in traits if t]
                
        # Try to extract ideals
        ideals_match = re.search(r"(?:Ideals|Values)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if ideals_match:
            npc_data["personality"]["ideals"] = ideals_match.group(1).strip()
            
        # Try to extract bonds
        bonds_match = re.search(r"(?:Bonds|Connections)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if bonds_match:
            npc_data["personality"]["bonds"] = bonds_match.group(1).strip()
            
        # Try to extract flaws
        flaws_match = re.search(r"(?:Flaws|Weaknesses)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if flaws_match:
            npc_data["personality"]["flaws"] = flaws_match.group(1).strip()
            
        # Try to extract background
        background_match = re.search(r"(?:Background|History|Past)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if background_match:
            npc_data["background"] = background_match.group(1).strip()
            
        # Try to extract motivations
        motivation_match = re.search(r"(?:Motivation|Drive|Desire)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if motivation_match:
            npc_data["motivations"] = motivation_match.group(1).strip()
            
        # Try to extract goals
        goals_match = re.search(r"(?:Goals|Ambitions|Objectives)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if goals_match:
            npc_data["goals"] = goals_match.group(1).strip()
            
        # Try to extract secrets
        secrets_match = re.search(r"(?:Secrets|Hidden)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if secrets_match:
            npc_data["secrets"] = secrets_match.group(1).strip()
            
        # Try to extract speech pattern
        speech_match = re.search(r"(?:Speech|Mannerisms|Voice)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if speech_match:
            npc_data["speech_pattern"] = speech_match.group(1).strip()
        
        return npc_data
    
    def _parse_narrative_assessment(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for narrative assessment."""
        # First try to use the BaseAdvisor's JSON extraction
        extracted_json = self._extract_json(response)
        if extracted_json:
            return extracted_json
        
        # If JSON extraction fails, fall back to regex parsing
        assessment = {
            "coherence_rating": "average",
            "inconsistencies": [],
            "enhancement_suggestions": [],
            "memorable_elements": []
        }
        
        # Try to determine coherence rating
        coherence_text = response.lower()
        if "highly coherent" in coherence_text or "very coherent" in coherence_text:
            assessment["coherence_rating"] = "high"
        elif "incoherent" in coherence_text or "poor coherence" in coherence_text:
            assessment["coherence_rating"] = "low"
        
        # Use BaseAdvisor's extract_list_items method if available
        inconsistencies = self._extract_list_items(response, ["inconsistent", "issue", "problem"])
        if inconsistencies:
            assessment["inconsistencies"] = inconsistencies
            
        suggestions = self._extract_list_items(response, ["enhance", "suggest", "improve"])
        if suggestions:
            assessment["enhancement_suggestions"] = suggestions
            
        memorable = self._extract_list_items(response, ["memorable", "distinctive", "unique"])
        if memorable:
            assessment["memorable_elements"] = memorable
        
        return assessment
    
    def _parse_stat_block_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for NPC stat block."""
        # First try to use the BaseAdvisor's JSON extraction
        extracted_json = self._extract_json(response)
        if extracted_json:
            stats = {
                "ability_scores": {
                    "strength": 10,
                    "dexterity": 10,
                    "constitution": 10,
                    "intelligence": 10,
                    "wisdom": 10,
                    "charisma": 10
                },
                "hp": 0,
                "ac": 10,
                "proficiency_bonus": 2,
                "skills": [],
                "equipment": [],
                "features": []
            }
            return {**stats, **extracted_json}
        
        # If JSON extraction fails, fall back to regex parsing
        stats = {
            "ability_scores": {
                "strength": 10,
                "dexterity": 10,
                "constitution": 10,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            },
            "hp": 0,
            "ac": 10,
            "proficiency_bonus": 2,
            "skills": [],
            "equipment": [],
            "features": []
        }
        
        # Try to extract ability scores
        ability_block = re.search(r"(?:Ability Scores|Abilities)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if ability_block:
            ability_text = ability_block.group(1).strip()
            
            # Try different regex patterns for ability scores
            # Pattern for "STR: 14, DEX: 16" format
            score_matches = re.findall(r"(?:STR|DEX|CON|INT|WIS|CHA)(?:[^:]*?):\s*(\d+)", ability_text, re.IGNORECASE)
            if len(score_matches) >= 6:
                ability_names = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
                for i, score in enumerate(score_matches[:6]):
                    stats["ability_scores"][ability_names[i]] = int(score)
            else:
                # Try looking for individual ability scores
                str_match = re.search(r"(?:STR|Strength)(?:[^:]*?):\s*(\d+)", response, re.IGNORECASE)
                dex_match = re.search(r"(?:DEX|Dexterity)(?:[^:]*?):\s*(\d+)", response, re.IGNORECASE)
                con_match = re.search(r"(?:CON|Constitution)(?:[^:]*?):\s*(\d+)", response, re.IGNORECASE)
                int_match = re.search(r"(?:INT|Intelligence)(?:[^:]*?):\s*(\d+)", response, re.IGNORECASE)
                wis_match = re.search(r"(?:WIS|Wisdom)(?:[^:]*?):\s*(\d+)", response, re.IGNORECASE)
                cha_match = re.search(r"(?:CHA|Charisma)(?:[^:]*?):\s*(\d+)", response, re.IGNORECASE)
                
                if str_match: stats["ability_scores"]["strength"] = int(str_match.group(1))
                if dex_match: stats["ability_scores"]["dexterity"] = int(dex_match.group(1))
                if con_match: stats["ability_scores"]["constitution"] = int(con_match.group(1))
                if int_match: stats["ability_scores"]["intelligence"] = int(int_match.group(1))
                if wis_match: stats["ability_scores"]["wisdom"] = int(wis_match.group(1))
                if cha_match: stats["ability_scores"]["charisma"] = int(cha_match.group(1))
        
        # Try to extract HP
        hp_match = re.search(r"(?:HP|Hit Points)(?:[^:]*?):\s*(\d+)", response, re.IGNORECASE)
        if hp_match:
            stats["hp"] = int(hp_match.group(1))
            
        # Try to extract AC
        ac_match = re.search(r"(?:AC|Armor Class)(?:[^:]*?):\s*(\d+)", response, re.IGNORECASE)
        if ac_match:
            stats["ac"] = int(ac_match.group(1))
            
        # Try to extract proficiency bonus
        prof_match = re.search(r"(?:Proficiency Bonus)(?:[^:]*?):\s*([+]\d+)", response, re.IGNORECASE)
        if prof_match:
            stats["proficiency_bonus"] = int(prof_match.group(1).replace("+", ""))
            
        # Try to extract skills - use BaseAdvisor's extract_list_items method
        skills = self._extract_list_items(response, ["skills", "proficiencies"])
        if skills:
            stats["skills"] = skills
            
        # Try to extract equipment - use BaseAdvisor's extract_list_items method
        equipment = self._extract_list_items(response, ["equipment", "items", "possessions"])
        if equipment:
            stats["equipment"] = equipment
            
        # Try to extract features - more complex, keep the original regex approach
        features_match = re.search(r"(?:Features|Abilities|Special|Class Features)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if features_match:
            features_text = features_match.group(1).strip()
            # Look for feature blocks
            feature_blocks = re.findall(r"(?:[-•*]\s*|^)([^,\n-•*][^:\n]*?)(?::|–|-)([^\n]+)", features_text)
            
            if feature_blocks:
                for name, desc in feature_blocks:
                    stats["features"].append({
                        "name": name.strip(),
                        "description": desc.strip()
                    })
            else:
                # Simple split by bullet points or numbers
                features = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", features_text, re.MULTILINE)
                stats["features"] = [{"name": f"Feature {i+1}", "description": f.strip()} for i, f in enumerate(features) if f.strip()]
        
        return stats
    
    def _parse_dialogue_response(self, response: str) -> List[Dict[str, str]]:
        """Parse LLM response for NPC dialogue options."""
        # First try to use the BaseAdvisor's JSON extraction
        extracted_json = self._extract_json(response)
        if extracted_json and isinstance(extracted_json, list):
            return extracted_json
        
        # If JSON extraction fails, fall back to regex parsing
        dialogue_options = []
        
        # Look for numbered response options or section headers
        # Pattern 1: Numbered options (1., 2., 3.)
        option_blocks = re.findall(r"(?:\d+\.)\s*([^\n]+(?:\n(?!\d+\.)[^\n]+)*)", response)
        
        # Pattern 2: Response types (Friendly:, Neutral:, Hostile:)
        if not option_blocks:
            option_blocks = re.findall(r"(?:Friendly|Helpful|Neutral|Cautious|Hostile|Suspicious)(?:[^:]*?):\s*([^\n]+(?:\n(?!(?:Friendly|Helpful|Neutral|Cautious|Hostile|Suspicious))[^\n]+)*)", response, re.IGNORECASE)
            
        # Extract response types
        response_types = ["friendly", "neutral", "hostile"]
        
        # Create dialogue options
        for i, block in enumerate(option_blocks):
            if i < len(response_types):
                response_type = response_types[i]
            else:
                response_type = "additional"
                
            dialogue = {
                "type": response_type,
                "text": block.strip()
            }
            
            # Attempt to separate actual spoken dialogue from description
            # Look for quotation marks
            quotes = re.findall(r'"([^"]*)"', block)
            if quotes:
                dialogue["spoken"] = ' '.join(quotes)
                
                # Try to extract action/description
                remaining = block
                for quote in quotes:
                    remaining = remaining.replace(f'"{quote}"', '')
                    
                dialogue["action"] = remaining.strip()
            
            dialogue_options.append(dialogue)
            
        return dialogue_options
    
    def _parse_backstory_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response for NPC backstory."""
        # First try to use the BaseAdvisor's JSON extraction
        extracted_json = self._extract_json(response)
        if extracted_json:
            return extracted_json
        
        # If JSON extraction fails, fall back to regex parsing
        backstory = {
            "childhood": "",
            "relationships": "",
            "significant_events": "",
            "career_path": "",
            "recent_history": "",
            "secret": "",
            "full_text": response
        }
        
        # Use BaseAdvisor's extract_section method for each section
        sections = {
            "childhood": ["Childhood", "Early Life", "Youth", "Formative"],
            "relationships": ["Relationships", "Family", "Connections", "Key Relations"],
            "significant_events": ["Events", "Significant", "Defining", "Life Events"],
            "career_path": ["Career", "Occupation", "Profession", "Training"],
            "recent_history": ["Recent", "Current", "Present", "Situation"],
            "secret": ["Secret", "Hidden", "Unknown", "Mystery"]
        }
        
        for key, terms in sections.items():
            for term in terms:
                pattern = rf"(?:{term})(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)"
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    backstory[key] = match.group(1).strip()
                    break
            
        return backstory
    
    def _parse_connections_response(self, response: str) -> List[Dict[str, str]]:
        """Parse LLM response for NPC connections."""
        # First try to use the BaseAdvisor's JSON extraction
        extracted_json = self._extract_json(response)
        if extracted_json and isinstance(extracted_json, list):
            return extracted_json
        
        # If JSON extraction fails, fall back to regex parsing
        connections = []
        
        # Look for numbered connections or sections
        connection_blocks = re.findall(r"(?:\d+\.)\s*([^\n]+(?:\n(?!\d+\.)[^\n]+)*)", response)
        
        if not connection_blocks:
            # Try another pattern for connection names followed by descriptions
            connection_blocks = re.findall(r"(?:Connection|Relationship)(?:[^:]*?):\s*([^\n]+(?:\n(?!(?:Connection|Relationship))[^\n]+)*)", response, re.IGNORECASE)
            
        for block in connection_blocks:
            connection = {
                "name": "Unknown Connection",
                "relationship": "",
                "description": block.strip()
            }
            
            # Try to extract name
            name_match = re.search(r"^([^,\n]+)", block)
            if name_match:
                connection["name"] = name_match.group(1).strip()
                
            # Try to extract relationship type
            relationship_match = re.search(r"(?:Relationship|Nature|Connection)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if relationship_match:
                connection["relationship"] = relationship_match.group(1).strip()
            elif "," in connection["name"]:
                # Try to get relationship from name line: "John Smith, old friend"
                parts = connection["name"].split(",", 1)
                connection["name"] = parts[0].strip()
                connection["relationship"] = parts[1].strip()
                
            # Try to extract history
            history_match = re.search(r"(?:History|Past|How They Met|Background)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if history_match:
                connection["history"] = history_match.group(1).strip()
                
            # Try to extract current state
            current_match = re.search(r"(?:Current|Status|Present|Now)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if current_match:
                connection["current_state"] = current_match.group(1).strip()
                
            # Try to extract influence
            influence_match = re.search(r"(?:Influence|Impact|Effect|Sway)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if influence_match:
                connection["influence"] = influence_match.group(1).strip()
                
            connections.append(connection)
            
        return connections

    def _parse_hooks_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for NPC hooks and secrets."""
        # First try to use the BaseAdvisor's JSON extraction
        extracted_json = self._extract_json(response)
        if extracted_json and isinstance(extracted_json, list):
            return extracted_json
        
        # If JSON extraction fails, fall back to regex parsing
        hooks_and_secrets = []
        
        # Look for numbered hooks or sections
        hook_blocks = re.findall(r"(?:\d+\.)\s*([^\n]+(?:\n(?!\d+\.)[^\n]+)*)", response)
        
        if not hook_blocks:
            # Try another pattern for hook titles followed by descriptions
            hook_blocks = re.findall(r"(?:Hook|Secret|Plot)(?:[^:]*?):\s*([^\n]+(?:\n(?!(?:Hook|Secret|Plot))[^\n]+)*)", response, re.IGNORECASE)
            
        for i, block in enumerate(hook_blocks):
            hook = {
                "title": f"Hook {i+1}",
                "description": block.strip(),
                "discovery": "",
                "development": "",
                "connections": [],
                "rewards": ""
            }
            
            # Try to extract title/basic concept
            title_match = re.search(r"^([^.\n]+)", block)
            if title_match:
                hook["title"] = title_match.group(1).strip()
                
            # Try to extract components using BaseAdvisor's pattern matching helpers
            sections = {
                "discovery": ["Discover", "Find Out", "Learn", "Reveal"],
                "development": ["Development", "Adventure", "Unfolds", "Progress", "Pursue"],
                "rewards": ["Rewards", "Consequences", "Results", "Outcome"]
            }
            
            for key, terms in sections.items():
                for term in terms:
                    pattern = rf"(?:{term})(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)"
                    match = re.search(pattern, block, re.IGNORECASE)
                    if match:
                        hook[key] = match.group(1).strip()
                        break
                
            # Try to extract connections
            connections_match = re.search(r"(?:Connected|Related|NPCs|Locations|Involves)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if connections_match:
                connections_text = connections_match.group(1).strip()
                connections = [conn.strip() for conn in re.split(r',|\n|;', connections_text) if conn.strip()]
                hook["connections"] = connections
                
            hooks_and_secrets.append(hook)
            
        return hooks_and_secrets
        
    def _parse_development_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response for NPC development suggestions."""
        # First try to use the BaseAdvisor's JSON extraction
        extracted_json = self._extract_json(response)
        if extracted_json:
            return extracted_json
            
        # If JSON extraction fails, create a structured response manually
        development = {
            "circumstances": "",
            "goals": "",
            "emotional_state": "",
            "relationships": "",
            "actions": "",
            "secrets": "",
            "full_text": response
        }
        
        # Use BaseAdvisor's extract_section method for each section
        sections = {
            "circumstances": ["Circumstances", "Status", "Situation", "Changes"],
            "goals": ["Goals", "Motivations", "Evolution", "Wants"],
            "emotional_state": ["Emotional", "Outlook", "Feelings", "State"],
            "relationships": ["Relationships", "Connections", "Social"],
            "actions": ["Actions", "Activities", "Practical", "Taken"],
            "secrets": ["Secrets", "Knowledge", "Acquired", "Learned"]
        }
        
        for key, terms in sections.items():
            for term in terms:
                pattern = rf"(?:{term})(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)"
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    development[key] = match.group(1).strip()
                    break
                    
        return development