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

try:
    from backend.core.ability_scores.ability_scores import AbilityScores
    from backend.core.ollama_service import OllamaService
    from backend.core.npc.abstract_npc import AbstractNPC
except ImportError:
    # Fallback for development
    class AbilityScores:
        def calculate_modifier(self, score): return (score - 10) // 2
    
    class OllamaService:
        def __init__(self): pass
        def generate(self, prompt): return "LLM service not available"
    
    AbstractNPC = object


class LLMNPCAdvisor:
    """
    Provides AI-powered assistance for D&D NPC creation and enhancement.
    
    This class integrates with Language Learning Models (LLMs) to provide creative
    assistance for individual NPC creation, focusing on personality, background,
    motivations, mannerisms, and other roleplay elements.
    """

    def __init__(self, llm_service=None, data_path: str = None):
        """
        Initialize the LLM NPC advisor.
        
        Args:
            llm_service: LLM service client for generating responses
            data_path: Optional path to NPC data
        """
        # Initialize LLM service
        self.llm_service = llm_service or OllamaService()
            
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
            print(f"Error loading reference data: {e}")
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
            
        # Create prompt for NPC generation
        prompt = self._create_prompt(
            "generate a detailed NPC",
            context + "\n"
            "Create a detailed D&D NPC that fits this role and campaign needs.\n"
            "Include the following information in your response:\n"
            "- Name, gender, race, and age\n"
            "- Occupation and social status\n"
            "- Physical appearance and distinctive features\n"
            "- Personality traits, ideals, bonds, and flaws\n"
            "- Brief background and personal history\n"
            "- Motivations, goals, and secrets\n"
            "- Speech patterns and mannerisms\n\n"
            "Make sure the NPC is coherent with the campaign theme and location if provided."
        )
        
        try:
            # Generate NPC concept with LLM
            response = self.llm_service.generate(prompt)
            
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
            
        # Create prompt for narrative assessment
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
                
        prompt = self._create_prompt(
            "assess npc narrative coherence",
            context + "\n"
            "Analyze this NPC for narrative coherence and roleplaying potential. Provide:\n"
            "1. Assessment of overall narrative coherence\n"
            "2. Specific elements that might be inconsistent\n"
            "3. Suggestions to enhance the NPC's roleplaying potential\n"
            "4. Additional details that could make this NPC more memorable\n\n"
            "Focus on making this NPC compelling and believable within a D&D world."
        )
        
        try:
            # Generate narrative assessment
            response = self.llm_service.generate(prompt)
            
            # Parse the assessment
            assessment = self._parse_narrative_assessment(response)
            
            # Combine with standard validation
            standard_validation["narrative_assessment"] = assessment
            standard_validation["has_narrative_feedback"] = True
            
            return standard_validation
        except Exception as e:
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
            
        # Create prompt for stat generation
        prompt = self._create_prompt(
            "generate npc stats",
            context + "\n"
            "Create game statistics for this NPC appropriate for their background and competence level.\n"
            "Include the following:\n"
            "1. Ability scores (STR, DEX, CON, INT, WIS, CHA)\n"
            "2. HP, AC, and proficiency bonus\n"
            "3. Key skill proficiencies aligned with background\n"
            "4. Notable equipment or items they possess\n"
            f"5. {'Class levels and class features' if include_class_levels else 'Special abilities related to occupation'}\n\n"
            f"Make sure the stats reflect a {competence_level} level of competence in their occupation."
        )
        
        try:
            # Generate NPC stats with LLM
            response = self.llm_service.generate(prompt)
            
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
            
        # Create prompt for dialogue generation
        prompt = self._create_prompt(
            "generate npc dialogue",
            context + "\n"
            "Generate realistic dialogue for this NPC based on their personality and the conversation context.\n"
            "Create three different response options:\n"
            "1. A friendly/helpful response\n"
            "2. A neutral/cautious response\n"
            "3. A hostile/suspicious response\n\n"
            "Each response should:\n"
            "- Reflect the NPC's personality and background\n"
            "- Use appropriate speech patterns and vocabulary\n"
            "- Include appropriate mannerisms or gestures\n"
            "- Address the player's statement directly (if provided)\n\n"
            "Write the dialogue as it would appear in a novel, including tone and non-verbal cues."
        )
        
        try:
            # Generate dialogue with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured dialogue options
            dialogue_options = self._parse_dialogue_response(response)
            
            return {
                "success": True,
                "dialogue_options": dialogue_options,
                "raw_response": response
            }
        except Exception as e:
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
            
        # Create prompt for backstory generation
        prompt = self._create_prompt(
            "generate npc backstory",
            context + "\n"
            f"Create a {detail_level} backstory for this NPC that explains how they became who they are today.\n"
            "Include the following elements:\n"
            "1. Formative childhood experiences\n"
            "2. Key relationships and their influence\n"
            "3. Significant life events that shaped them\n"
            "4. How they entered their current occupation\n"
            "5. Recent history leading to their current situation\n"
            "6. A secret or hidden aspect of their past\n\n"
            f"{'Focus particularly on their ' + focus_area if focus_area else 'Balance all aspects of their life'}"
        )
        
        try:
            # Generate backstory with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured backstory elements
            backstory = self._parse_backstory_response(response)
            
            return {
                "success": True,
                "backstory": backstory,
                "raw_response": response
            }
        except Exception as e:
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
                
        # Create prompt for social connections
        prompt = self._create_prompt(
            "generate npc connections",
            context + "\n"
            f"Create {num_connections} meaningful social connections for this NPC within their community.\n"
            "For each connection, provide:\n"
            "1. Name and basic details of the connected person\n"
            "2. Nature of the relationship (family, friend, rival, mentor, etc.)\n"
            "3. History of how they became connected\n"
            "4. Current state of the relationship\n"
            "5. How this relationship influences the NPC's decisions or behavior\n\n"
            "Include a mix of positive and negative/complicated relationships."
        )
        
        try:
            # Generate connections with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured connections
            connections = self._parse_connections_response(response)
            
            return {
                "success": True,
                "connections": connections,
                "raw_response": response
            }
        except Exception as e:
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
            
        # Create prompt for hooks and secrets
        prompt = self._create_prompt(
            "generate npc secrets and hooks",
            context + "\n"
            f"Create {num_hooks} compelling secrets and adventure hooks involving this NPC.\n"
            "For each hook/secret, provide:\n"
            "1. The basic secret or situation\n"
            "2. How players might discover it\n"
            "3. Potential adventure developments if pursued\n"
            "4. NPCs or locations connected to this hook\n"
            "5. Possible rewards or consequences for the players\n\n"
            f"Focus on {hook_type} hooks that would create engaging gameplay."
        )
        
        try:
            # Generate hooks with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured hooks
            hooks_and_secrets = self._parse_hooks_response(response)
            
            return {
                "success": True,
                "hooks_and_secrets": hooks_and_secrets,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate hooks and secrets: {str(e)}"
            }

    def export_npc_character_sheet(self, npc_data: Dict[str, Any],
                                 include_artwork_prompt: bool = False,
                                 format: str = 'pdf') -> Dict[str, Any]:
        """
        Export NPC to different formats with option for artwork prompt.
        
        Args:
            npc_data: NPC data to export
            include_artwork_prompt: Whether to include prompt for AI art generation
            format: Export format ('pdf', 'json', 'markdown', etc.)
            
        Returns:
            Dict[str, Any]: Export result with path or data
        """
        # Start with base NPC data
        export_data = npc_data.copy()
        
        # If requested, generate artwork prompt
        if include_artwork_prompt:
            artwork_prompt = self._generate_artwork_prompt(npc_data)
            export_data["artwork_prompt"] = artwork_prompt
        
        # Format-specific export handling
        export_result = {
            "format": format,
            "npc_id": npc_data.get("id", "unknown"),
            "export_time": datetime.datetime.now().isoformat()
        }
        
        if format.lower() == 'pdf':
            # PDF generation would happen here
            export_result["status"] = "PDF generation not implemented"
        elif format.lower() == 'json':
            export_result["data"] = export_data
            export_result["status"] = "success"
        elif format.lower() == 'markdown':
            export_result["data"] = self._convert_to_markdown(export_data)
            export_result["status"] = "success"
        else:
            export_result["status"] = f"Unsupported format: {format}"
            
        return {
            "enhanced_npc": export_data,
            "export_result": export_result
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
                
        # Create prompt for development suggestions
        prompt = self._create_prompt(
            "suggest npc development",
            context + "\n"
            f"Suggest how this NPC would logically develop over {time_passed} given their personality and recent events.\n"
            "Include the following elements:\n"
            "1. Changes to their immediate circumstances or status\n"
            "2. Evolution of their goals or motivations\n"
            "3. Changes to their emotional state or outlook\n"
            "4. New relationships or modified existing relationships\n"
            "5. Practical actions they've taken during this time\n"
            "6. New secrets or knowledge they've acquired\n\n"
            "Make the development feel organic and consistent with their established character."
        )
        
        try:
            # Generate development ideas with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            development = self._parse_development_response(response)
            
            return {
                "success": True,
                "development": development,
                "time_frame": time_passed,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate NPC development: {str(e)}"
            }

    # Helper methods

    def _create_prompt(self, task: str, content: str) -> str:
        """Create a structured prompt for the LLM."""
        return f"Task: {task}\n\n{content}"
    
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
    
    def _generate_artwork_prompt(self, npc_data: Dict[str, Any]) -> str:
        """Generate a prompt for AI artwork generation."""
        # Build basic description
        name = npc_data.get("name", "Unnamed NPC")
        race = npc_data.get("race", "Human")
        
        appearance = npc_data.get("appearance", "")
        if not appearance:
            appearance = "average build and features"
            
        # Create prompt
        description = f"{name}, a {race} {npc_data.get('occupation', '')}. "
        description += appearance
        
        # Add distinctive features
        if "distinctive_features" in npc_data:
            description += f" Distinctive features include {npc_data['distinctive_features']}."
            
        # Add clothing and equipment
        if "clothing" in npc_data:
            description += f" Wearing {npc_data['clothing']}."
            
        if "equipment" in npc_data:
            description += f" Equipped with {npc_data['equipment']}."
            
        # Add emotional state if available
        personality = npc_data.get("personality", {})
        if personality and "traits" in personality and personality["traits"]:
            traits = personality["traits"]
            description += f" Personality expressed as {', '.join(traits[:2])}."
        
        return description
        
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
        
        # Extract inconsistencies and suggestions
        lines = response.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            lower_line = line.lower()
            
            if "inconsistent" in lower_line or "issue" in lower_line or "problem" in lower_line:
                current_section = "inconsistencies"
                continue
            elif "enhance" in lower_line or "suggest" in lower_line or "improve" in lower_line:
                current_section = "enhancement_suggestions"
                continue
            elif "memorable" in lower_line or "distinctive" in lower_line or "unique" in lower_line:
                current_section = "memorable_elements"
                continue
                
            if current_section and line.startswith("-"):
                assessment[current_section].append(line[1:].strip())
            elif current_section and line[0].isdigit() and ". " in line:
                point = line.split(". ", 1)[1]
                assessment[current_section].append(point.strip())
            
        return assessment
    
    def _parse_stat_block_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for NPC stat block."""
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
            
        # Try to extract skills
        skills_match = re.search(r"(?:Skills|Proficiencies)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if skills_match:
            skills_text = skills_match.group(1).strip()
            # Split by commas or bullet points
            skills = re.findall(r"(?:[-•*]\s*|^)([^,\n-•*][^,\n]*)", skills_text)
            if skills:
                stats["skills"] = [s.strip() for s in skills if s.strip()]
            else:
                skills = [s.strip() for s in skills_text.split(",")]
                stats["skills"] = [s for s in skills if s]
                
        # Try to extract equipment
        equipment_match = re.search(r"(?:Equipment|Items|Possessions)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if equipment_match:
            equipment_text = equipment_match.group(1).strip()
            # Split by commas or bullet points
            equipment = re.findall(r"(?:[-•*]\s*|^)([^,\n-•*][^,\n]*)", equipment_text)
            if equipment:
                stats["equipment"] = [e.strip() for e in equipment if e.strip()]
            else:
                equipment = [e.strip() for e in equipment_text.split(",")]
                stats["equipment"] = [e for e in equipment if e]
                
        # Try to extract features
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
        backstory = {
            "childhood": "",
            "relationships": "",
            "significant_events": "",
            "career_path": "",
            "recent_history": "",
            "secret": "",
            "full_text": response
        }
        
        # Try to extract childhood
        childhood_match = re.search(r"(?:Childhood|Early Life|Youth|Formative)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if childhood_match:
            backstory["childhood"] = childhood_match.group(1).strip()
            
        # Try to extract relationships
        relationships_match = re.search(r"(?:Relationships|Family|Connections|Key Relations)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if relationships_match:
            backstory["relationships"] = relationships_match.group(1).strip()
            
        # Try to extract significant events
        events_match = re.search(r"(?:Events|Significant|Defining|Life Events)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if events_match:
            backstory["significant_events"] = events_match.group(1).strip()
            
        # Try to extract career path
        career_match = re.search(r"(?:Career|Occupation|Profession|Training)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if career_match:
            backstory["career_path"] = career_match.group(1).strip()
            
        # Try to extract recent history
        recent_match = re.search(r"(?:Recent|Current|Present|Situation)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if recent_match:
            backstory["recent_history"] = recent_match.group(1).strip()
            
        # Try to extract secret
        secret_match = re.search(r"(?:Secret|Hidden|Unknown|Mystery)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if secret_match:
            backstory["secret"] = secret_match.group(1).strip()
            
        return backstory
    
    def _parse_connections_response(self, response: str) -> List[Dict[str, str]]:
        """Parse LLM response for NPC connections."""
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
                
            # Try to extract discovery method
            discovery_match = re.search(r"(?:Discover|Find Out|Learn|Reveal)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if discovery_match:
                hook["discovery"] = discovery_match.group(1).strip()
                
            # Try to extract potential developments
            development_match = re.search(r"(?:Development|Adventure|Unfolds|Progress|Pursue)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if development_match:
                hook["development"] = development_match.group(1).strip()
                
            # Try to extract connections
            connections_match = re.search(r"(?:Connected|Related|NPCs|Locations|Involves)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if connections_match:
                connections_text = connections_match.group(1).strip()
                connections = [conn.strip() for conn in re.split(r',|\n|;', connections_text) if conn.strip()]
                hook["connections"] = connections
                
            # Try to extract rewards
            rewards_match = re.search(r"(?:Rewards|Consequences|Results|Outcome)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if rewards_match:
                hook["rewards"] = rewards_match.group(1).strip()
                
            hooks_and_secrets.append(hook)
            
        return hooks_and_secrets

    def generate_npc_voice_pattern(self, npc_data: Dict[str, Any], 
                                detail_level: str = "standard") -> Dict[str, Any]:
        """
        Generate detailed speech patterns and voice characteristics for an NPC.
        
        Args:
            npc_data: Basic NPC data
            detail_level: Level of detail (basic, standard, extensive)
            
        Returns:
            Dict[str, Any]: Voice and speech pattern details
        """
        # Build context for LLM
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'Human')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'Commoner')}\n"
        context += f"Detail Level: {detail_level}\n"
        
        # Add personality info
        personality = npc_data.get("personality", {})
        if personality:
            if "traits" in personality:
                context += f"Personality Traits: {', '.join(personality['traits'])}\n"
        
        # Create prompt for voice generation
        prompt = self._create_prompt(
            "generate npc voice pattern",
            context + "\n"
            "Create detailed speech patterns and voice characteristics for this NPC.\n"
            "Include:\n"
            "1. Voice quality (pitch, tone, volume, clarity)\n"
            "2. Speech patterns (fast/slow, linguistic quirks, favorite phrases)\n"
            "3. Vocabulary level and word choice tendencies\n"
            "4. Accent or dialect characteristics\n"
            "5. Non-verbal communication habits\n"
            "6. How emotions affect their speech\n\n"
            "Make the voice pattern distinctive enough to help the DM roleplay this character consistently."
        )
        
        try:
            # Generate voice pattern with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            voice_data = self._parse_voice_response(response)
            
            return {
                "success": True,
                "voice_pattern": voice_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate voice pattern: {str(e)}"
            }

    def generate_npc_beliefs(self, npc_data: Dict[str, Any],
                        cultural_context: str = None,
                        belief_focus: str = "general") -> Dict[str, Any]:
        """
        Generate detailed cultural and religious beliefs for an NPC.
        
        Args:
            npc_data: Basic NPC data
            cultural_context: Optional cultural background information
            belief_focus: Focus area for beliefs (religious, political, cultural, general)
            
        Returns:
            Dict[str, Any]: Beliefs and value system details
        """
        # Build context for LLM
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'Human')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'Commoner')}\n"
        context += f"Belief Focus: {belief_focus}\n"
        
        if cultural_context:
            context += f"Cultural Context: {cultural_context}\n"
            
        # Add ideals if available
        personality = npc_data.get("personality", {})
        if personality and "ideals" in personality:
            context += f"Ideals: {personality['ideals']}\n"
        
        # Create prompt for beliefs generation
        prompt = self._create_prompt(
            "generate npc beliefs",
            context + "\n"
            "Create a detailed belief system for this NPC that shapes their worldview and decisions.\n"
            "Include:\n"
            "1. Religious beliefs and practices (deities, rituals, level of devotion)\n"
            "2. Cultural values and traditions they uphold\n"
            "3. Political views and stance on authority\n"
            "4. Superstitions or folk beliefs they follow\n"
            "5. Ethical framework and moral boundaries\n"
            "6. How these beliefs manifest in daily behaviors\n\n"
            f"Focus especially on their {belief_focus} beliefs while creating a coherent worldview."
        )
        
        try:
            # Generate beliefs with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            beliefs_data = self._parse_beliefs_response(response)
            
            return {
                "success": True,
                "beliefs": beliefs_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate beliefs: {str(e)}"
            }

    def generate_npc_quirks(self, npc_data: Dict[str, Any],
                        quirk_count: int = 3) -> Dict[str, Any]:
        """
        Generate memorable quirks, habits, and mannerisms for an NPC.
        
        Args:
            npc_data: Basic NPC data
            quirk_count: Number of quirks to generate
            
        Returns:
            Dict[str, Any]: Unique quirks and habits
        """
        # Build context for LLM
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'Human')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'Commoner')}\n"
        context += f"Number of Quirks: {quirk_count}\n"
        
        # Add personality info
        personality = npc_data.get("personality", {})
        if personality and "traits" in personality:
            context += f"Personality Traits: {', '.join(personality['traits'])}\n"
            
        if "flaws" in personality:
            context += f"Flaws: {personality['flaws']}\n"
        
        # Create prompt for quirk generation
        prompt = self._create_prompt(
            "generate npc quirks",
            context + "\n"
            f"Create {quirk_count} memorable quirks, habits, or mannerisms for this NPC that make them distinctive.\n"
            "For each quirk, provide:\n"
            "1. A brief name or title for the quirk\n"
            "2. Detailed description of how it manifests\n"
            "3. The underlying reason or origin of this behavior\n"
            "4. How it affects interactions with others\n"
            "5. Circumstances when it becomes more or less pronounced\n\n"
            "Make these quirks distinctive enough that players would remember and recognize this NPC by them."
        )
        
        try:
            # Generate quirks with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            quirks_data = self._parse_quirks_response(response)
            
            return {
                "success": True,
                "quirks": quirks_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate quirks: {str(e)}"
            }

    def generate_npc_art_description(self, npc_data: Dict[str, Any],
                                art_style: str = "fantasy",
                                detail_level: str = "high") -> Dict[str, Any]:
        """
        Generate detailed visual description for AI art generation of the NPC.
        
        Args:
            npc_data: Basic NPC data
            art_style: Desired art style
            detail_level: Level of detail in description
            
        Returns:
            Dict[str, Any]: Art prompt and visual details
        """
        # Build context for LLM
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'Human')}\n"
        context += f"Gender: {npc_data.get('gender', 'Unknown')}\n"
        context += f"Age: {npc_data.get('age', 'Adult')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'Commoner')}\n"
        context += f"Art Style: {art_style}\n"
        context += f"Detail Level: {detail_level}\n"
        
        if "appearance" in npc_data:
            context += f"Existing Appearance: {npc_data['appearance']}\n"
            
        if "distinctive_features" in npc_data:
            context += f"Distinctive Features: {npc_data['distinctive_features']}\n"
        
        # Create prompt for art description
        prompt = self._create_prompt(
            "generate npc art description",
            context + "\n"
            f"Create a detailed visual description of this NPC suitable for AI art generation in {art_style} style.\n"
            "Include:\n"
            "1. Face details (eyes, expression, facial structure, hair)\n"
            "2. Body composition and posture\n"
            "3. Clothing, accessories, and equipment\n"
            "4. Color palette and lighting suggestions\n"
            "5. Background elements or setting context\n"
            "6. Mood and atmosphere\n\n"
            "Format this as a cohesive prompt that could be directly input into an AI art generator."
        )
        
        try:
            # Generate art description with LLM
            response = self.llm_service.generate(prompt)
            
            # Extract the core prompt and details
            art_data = {
                "complete_prompt": response.strip(),
                "character_description": "",
                "visual_elements": [],
                "style_notes": ""
            }
            
            # Try to extract character description
            char_match = re.search(r"(?:Character|NPC|Subject)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if char_match:
                art_data["character_description"] = char_match.group(1).strip()
                
            # Try to extract visual elements
            visual_match = re.search(r"(?:Visual|Elements|Details|Include)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if visual_match:
                visual_text = visual_match.group(1).strip()
                elements = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", visual_text, re.MULTILINE)
                if elements:
                    art_data["visual_elements"] = [e.strip() for e in elements if e.strip()]
                else:
                    art_data["visual_elements"] = [v.strip() for v in visual_text.split(",") if v.strip()]
                    
            # Try to extract style notes
            style_match = re.search(r"(?:Style|Aesthetic|Mood|Atmosphere)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if style_match:
                art_data["style_notes"] = style_match.group(1).strip()
            
            return {
                "success": True,
                "art_description": art_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate art description: {str(e)}"
            }

    def generate_npc_magic_abilities(self, npc_data: Dict[str, Any],
                                magic_level: str = "moderate",
                                magic_source: str = None) -> Dict[str, Any]:
        """
        Generate magic abilities or special powers for an NPC.
        
        Args:
            npc_data: Basic NPC data
            magic_level: Level of magical ability (minor, moderate, major)
            magic_source: Source of magic (arcane, divine, natural, etc.)
            
        Returns:
            Dict[str, Any]: Magic abilities and special powers
        """
        # Build context for LLM
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'Human')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'Commoner')}\n"
        context += f"Magic Level: {magic_level}\n"
        
        if magic_source:
            context += f"Magic Source: {magic_source}\n"
            
        # Add stats if available
        if "stats" in npc_data:
            stats = npc_data["stats"]
            if "ability_scores" in stats:
                intelligence = stats["ability_scores"].get("intelligence", 10)
                wisdom = stats["ability_scores"].get("wisdom", 10)
                charisma = stats["ability_scores"].get("charisma", 10)
                context += f"Intelligence: {intelligence}, Wisdom: {wisdom}, Charisma: {charisma}\n"
        
        # Create prompt for magic abilities
        prompt = self._create_prompt(
            "generate npc magic abilities",
            context + "\n"
            f"Create {magic_level}-level magical abilities or special powers for this NPC.\n"
            "Include:\n"
            "1. Source and nature of their magical power\n"
            "2. 3-5 specific spells or magical abilities they possess\n"
            "3. Limitations or costs of using their magic\n"
            "4. Visual and sensory effects when they use magic\n"
            "5. How they typically apply magic in daily life\n"
            "6. Any magical items or focus tools they use\n\n"
            "Make these abilities appropriate to their background and personality."
        )
        
        try:
            # Generate magic abilities with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            magic_data = self._parse_magic_response(response)
            
            return {
                "success": True,
                "magic_abilities": magic_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate magic abilities: {str(e)}"
            }

    def generate_reaction_table(self, npc_data: Dict[str, Any],
                            situation_types: List[str] = None) -> Dict[str, Any]:
        """
        Generate a reaction table for how an NPC responds to different situations.
        
        Args:
            npc_data: Basic NPC data
            situation_types: Types of situations to generate reactions for
            
        Returns:
            Dict[str, Any]: Reaction table with responses to different situations
        """
        # Default situations if none provided
        if not situation_types:
            situation_types = [
                "combat", "negotiation", "receiving gifts", 
                "being threatened", "meeting strangers"
            ]
        
        # Build context for LLM
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'Human')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'Commoner')}\n"
        context += f"Situations: {', '.join(situation_types)}\n"
        
        # Add personality info
        personality = npc_data.get("personality", {})
        if personality and "traits" in personality:
            context += f"Personality Traits: {', '.join(personality['traits'])}\n"
            
        if "flaws" in personality:
            context += f"Flaws: {personality['flaws']}\n"
        
        # Create prompt for reaction table
        prompt = self._create_prompt(
            "generate npc reaction table",
            context + "\n"
            "Create a reaction table for this NPC showing how they respond to different situations.\n"
            "For each situation type listed, provide:\n"
            "1. Initial emotional reaction\n"
            "2. Likely verbal response\n"
            "3. Physical actions or body language\n"
            "4. Decision-making process in this context\n"
            "5. Factors that might change their typical reaction\n\n"
            "Format the responses as a clear table covering each situation type."
        )
        
        try:
            # Generate reaction table with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            reaction_data = self._parse_reaction_table(response, situation_types)
            
            return {
                "success": True,
                "reaction_table": reaction_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate reaction table: {str(e)}"
            }

    def generate_personal_inventory(self, npc_data: Dict[str, Any],
                                item_count: int = 5,
                                include_valuables: bool = True) -> Dict[str, Any]:
        """
        Generate a detailed personal inventory of items the NPC carries or owns.
        
        Args:
            npc_data: Basic NPC data
            item_count: Number of items to include
            include_valuables: Whether to include valuable items
            
        Returns:
            Dict[str, Any]: Inventory with personal items and possessions
        """
        # Build context for LLM
        context = f"NPC Name: {npc_data.get('name', 'Unnamed NPC')}\n"
        context += f"Race: {npc_data.get('race', 'Human')}\n"
        context += f"Occupation: {npc_data.get('occupation', 'Commoner')}\n"
        context += f"Item Count: {item_count}\n"
        context += f"Include Valuables: {'Yes' if include_valuables else 'No'}\n"
        
        # Add background if available
        if "background" in npc_data:
            context += f"Background Summary: {npc_data['background'][:100]}...\n"
        
        # Create prompt for inventory generation
        prompt = self._create_prompt(
            "generate npc personal inventory",
            context + "\n"
            f"Create a detailed inventory of {item_count} items this NPC carries or owns.\n"
            "For each item, provide:\n"
            "1. Name and basic description\n"
            "2. Condition and appearance\n"
            "3. Origin or how they acquired it\n"
            "4. Personal significance or practical purpose\n"
            "5. How often or when they use it\n\n"
            f"{'Include some valuable items or treasures' if include_valuables else 'Focus on everyday practical items'}\n"
            "Include at least one unusual or distinctive item that reveals something about their character."
        )
        
        try:
            # Generate inventory with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            inventory_data = self._parse_inventory_response(response)
            
            return {
                "success": True,
                "personal_inventory": inventory_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate inventory: {str(e)}"
            }

    # Parser methods for new functions

    def _parse_voice_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for NPC voice patterns."""
        voice_data = {
            "voice_quality": "",
            "speech_patterns": "",
            "vocabulary": "",
            "accent": "",
            "non_verbal": "",
            "emotional_tells": "",
            "phrases": []
        }
        
        # Try to extract voice quality
        voice_match = re.search(r"(?:Voice|Tone|Pitch|Quality)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if voice_match:
            voice_data["voice_quality"] = voice_match.group(1).strip()
            
        # Try to extract speech patterns
        speech_match = re.search(r"(?:Speech|Pattern|Rhythm|Pace)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if speech_match:
            voice_data["speech_patterns"] = speech_match.group(1).strip()
            
        # Try to extract vocabulary
        vocab_match = re.search(r"(?:Vocabulary|Word Choice|Language|Diction)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if vocab_match:
            voice_data["vocabulary"] = vocab_match.group(1).strip()
            
        # Try to extract accent
        accent_match = re.search(r"(?:Accent|Dialect|Regional|Pronunciation)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if accent_match:
            voice_data["accent"] = accent_match.group(1).strip()
            
        # Try to extract non-verbal cues
        nonverbal_match = re.search(r"(?:Non-?verbal|Gesture|Body Language|Physical)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if nonverbal_match:
            voice_data["non_verbal"] = nonverbal_match.group(1).strip()
            
        # Try to extract emotional tells
        emotion_match = re.search(r"(?:Emotion|Feel|Mood|Affect)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if emotion_match:
            voice_data["emotional_tells"] = emotion_match.group(1).strip()
            
        # Try to extract favorite phrases
        phrases_match = re.search(r"(?:Phrases|Saying|Expression|Common)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if phrases_match:
            phrases_text = phrases_match.group(1).strip()
            phrases = re.findall(r"(?:[-•*]\s*|^|\n\s*|[""])([^,\n-•*""][^,\n""]*)", phrases_text)
            if phrases:
                voice_data["phrases"] = [p.strip() for p in phrases if p.strip()]
            else:
                voice_data["phrases"] = [p.strip() for p in phrases_text.split(",") if p.strip()]
        
        return voice_data

    def _parse_beliefs_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for NPC beliefs and values."""
        beliefs_data = {
            "religious_beliefs": "",
            "cultural_values": "",
            "political_views": "",
            "superstitions": [],
            "moral_code": "",
            "daily_practices": []
        }
        
        # Try to extract religious beliefs
        religious_match = re.search(r"(?:Religious|Faith|Spiritual|Divine|Deity)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if religious_match:
            beliefs_data["religious_beliefs"] = religious_match.group(1).strip()
            
        # Try to extract cultural values
        cultural_match = re.search(r"(?:Cultural|Tradition|Heritage|Custom)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if cultural_match:
            beliefs_data["cultural_values"] = cultural_match.group(1).strip()
            
        # Try to extract political views
        political_match = re.search(r"(?:Political|Authority|Government|Power|Rule)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if political_match:
            beliefs_data["political_views"] = political_match.group(1).strip()
            
        # Try to extract superstitions
        superstition_match = re.search(r"(?:Superstition|Folk|Belief|Lucky|Unlucky)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if superstition_match:
            superstition_text = superstition_match.group(1).strip()
            superstitions = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", superstition_text, re.MULTILINE)
            if superstitions:
                beliefs_data["superstitions"] = [s.strip() for s in superstitions if s.strip()]
            else:
                beliefs_data["superstitions"] = [s.strip() for s in re.split(r'\.(?=\s+[A-Z])', superstition_text) if s.strip()]
                
        # Try to extract moral code
        moral_match = re.search(r"(?:Moral|Ethic|Right|Wrong|Value)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if moral_match:
            beliefs_data["moral_code"] = moral_match.group(1).strip()
            
        # Try to extract daily practices
        practices_match = re.search(r"(?:Daily|Practice|Ritual|Habit|Behavior|Manifest)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if practices_match:
            practices_text = practices_match.group(1).strip()
            practices = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", practices_text, re.MULTILINE)
            if practices:
                beliefs_data["daily_practices"] = [p.strip() for p in practices if p.strip()]
            else:
                beliefs_data["daily_practices"] = [p.strip() for p in re.split(r'\.(?=\s+[A-Z])', practices_text) if p.strip()]
        
        return beliefs_data

    def _parse_quirks_response(self, response: str) -> List[Dict[str, str]]:
        """Parse LLM response for NPC quirks."""
        quirks = []
        
        # Look for numbered quirks or sections
        quirk_blocks = re.findall(r"(?:\d+\.)\s*([^\n]+(?:\n(?!\d+\.)[^\n]+)*)", response)
        
        if not quirk_blocks:
            # Try another pattern
            quirk_blocks = re.findall(r"(?:Quirk|Habit|Mannerism)(?:[^:]*?):\s*([^\n]+(?:\n(?!(?:Quirk|Habit|Mannerism))[^\n]+)*)", response, re.IGNORECASE)
            
        for block in quirk_blocks:
            quirk = {
                "name": f"Quirk",
                "description": block.strip(),
                "origin": "",
                "effect": "",
                "triggers": ""
            }
            
            # Try to extract name/title
            name_match = re.search(r"^([^:.\n]+)", block)
            if name_match:
                quirk["name"] = name_match.group(1).strip()
                
            # Try to extract description/manifestation
            desc_match = re.search(r"(?:Description|Manifests|Appears as|Shows up)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if desc_match:
                quirk["description"] = desc_match.group(1).strip()
                
            # Try to extract origin/reason
            origin_match = re.search(r"(?:Origin|Reason|Cause|Source|Background)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if origin_match:
                quirk["origin"] = origin_match.group(1).strip()
                
            # Try to extract effect on others
            effect_match = re.search(r"(?:Effect|Impact|Reaction|Response|Others)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if effect_match:
                quirk["effect"] = effect_match.group(1).strip()
                
            # Try to extract triggers/circumstances
            trigger_match = re.search(r"(?:Trigger|Circumstance|When|Situation|Pronounced)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if trigger_match:
                quirk["triggers"] = trigger_match.group(1).strip()
                
            quirks.append(quirk)
            
        return quirks

    def _parse_magic_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for NPC magic abilities."""
        magic_data = {
            "source": "",
            "abilities": [],
            "limitations": "",
            "visual_effects": "",
            "daily_use": "",
            "items": []
        }
        
        # Try to extract magic source
        source_match = re.search(r"(?:Source|Origin|Nature|Power)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if source_match:
            magic_data["source"] = source_match.group(1).strip()
            
        # Try to extract abilities/spells
        abilities_match = re.search(r"(?:Abilities|Spells|Powers|Magic|Can Cast|Capable)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if abilities_match:
            abilities_text = abilities_match.group(1).strip()
            abilities = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", abilities_text, re.MULTILINE)
            if abilities:
                # Process each ability
                for ability in abilities:
                    ability_data = {"name": "", "description": ""}
                    
                    # Try to split name and description
                    if ":" in ability:
                        name, desc = ability.split(":", 1)
                        ability_data["name"] = name.strip()
                        ability_data["description"] = desc.strip()
                    elif "-" in ability:
                        name, desc = ability.split("-", 1)
                        ability_data["name"] = name.strip()
                        ability_data["description"] = desc.strip()
                    elif " - " in ability:
                        name, desc = ability.split(" - ", 1)
                        ability_data["name"] = name.strip()
                        ability_data["description"] = desc.strip()
                    else:
                        ability_data["name"] = ability.strip()
                        
                    magic_data["abilities"].append(ability_data)
            else:
                # Just add text as a single ability
                magic_data["abilities"].append({
                    "name": "Magic Ability",
                    "description": abilities_text
                })
                
        # Try to extract limitations
        limits_match = re.search(r"(?:Limitation|Drawback|Cost|Weakness|Constraint)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if limits_match:
            magic_data["limitations"] = limits_match.group(1).strip()
            
        # Try to extract visual effects
        visual_match = re.search(r"(?:Visual|Effect|Appearance|Sensory|Look)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if visual_match:
            magic_data["visual_effects"] = visual_match.group(1).strip()
            
        # Try to extract daily use
        daily_match = re.search(r"(?:Daily|Use|Application|Practical|Life)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if daily_match:
            magic_data["daily_use"] = daily_match.group(1).strip()
            
        # Try to extract magical items
        items_match = re.search(r"(?:Items?|Tools?|Focus|Equipment|Implements?)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if items_match:
            items_text = items_match.group(1).strip()
            items = re.findall(r"(?:[-•*]\s*|^)([^,\n-•*][^,\n]*)", items_text)
            if items:
                magic_data["items"] = [i.strip() for i in items if i.strip()]
            else:
                magic_data["items"] = [i.strip() for i in items_text.split(",") if i.strip()]
        
        return magic_data

    def _parse_reaction_table(self, response: str, situation_types: List[str]) -> Dict[str, Dict[str, str]]:
        """Parse LLM response for NPC reaction table."""
        reaction_table = {}
        
        # Create entries for each situation type
        for situation in situation_types:
            reaction_table[situation] = {
                "emotional_reaction": "",
                "verbal_response": "",
                "physical_action": "",
                "decision_process": "",
                "modifying_factors": ""
            }
            
            # Look for sections about this situation
            situation_pattern = re.compile(rf"(?:{situation}|When {situation}|During {situation}|If {situation})(?:[^:]*?):\s*([^\n]+(?:\n(?!(?:{situation_types[0]}|{situation_types[-1]}))[^\n]+)*)", re.IGNORECASE)
            situation_match = situation_pattern.search(response)
            
            if situation_match:
                situation_block = situation_match.group(1).strip()
                
                # Try to extract components
                emotional_match = re.search(r"(?:Emotional|Feeling|Initial|React)(?:[^:]*?):\s*([^\n]+)", situation_block, re.IGNORECASE)
                if emotional_match:
                    reaction_table[situation]["emotional_reaction"] = emotional_match.group(1).strip()
                    
                verbal_match = re.search(r"(?:Verbal|Say|Speech|Words)(?:[^:]*?):\s*([^\n]+)", situation_block, re.IGNORECASE)
                if verbal_match:
                    reaction_table[situation]["verbal_response"] = verbal_match.group(1).strip()
                    
                physical_match = re.search(r"(?:Physical|Action|Body|Movement)(?:[^:]*?):\s*([^\n]+)", situation_block, re.IGNORECASE)
                if physical_match:
                    reaction_table[situation]["physical_action"] = physical_match.group(1).strip()
                    
                decision_match = re.search(r"(?:Decision|Think|Process|Consider)(?:[^:]*?):\s*([^\n]+)", situation_block, re.IGNORECASE)
                if decision_match:
                    reaction_table[situation]["decision_process"] = decision_match.group(1).strip()
                    
                factor_match = re.search(r"(?:Factors?|Change|Modify|Alter)(?:[^:]*?):\s*([^\n]+)", situation_block, re.IGNORECASE)
                if factor_match:
                    reaction_table[situation]["modifying_factors"] = factor_match.group(1).strip()
        
        return reaction_table

    def _parse_inventory_response(self, response: str) -> List[Dict[str, str]]:
        """Parse LLM response for NPC inventory."""
        inventory = []
        
        # Look for numbered items or sections
        item_blocks = re.findall(r"(?:\d+\.)\s*([^\n]+(?:\n(?!\d+\.)[^\n]+)*)", response)
        
        if not item_blocks:
            # Try another pattern
            item_blocks = re.findall(r"(?:Item|Possession|Object)(?:[^:]*?):\s*([^\n]+(?:\n(?!(?:Item|Possession|Object))[^\n]+)*)", response, re.IGNORECASE)
            
        for block in item_blocks:
            item = {
                "name": "Unknown Item",
                "description": block.strip(),
                "condition": "",
                "origin": "",
                "significance": "",
                "usage": ""
            }
            
            # Try to extract name
            name_match = re.search(r"^([^:.\n]+)", block)
            if name_match:
                item["name"] = name_match.group(1).strip()
                
            # Try to extract description
            desc_match = re.search(r"(?:Description|Appearance|Looks like)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if desc_match:
                item["description"] = desc_match.group(1).strip()
                
            # Try to extract condition
            condition_match = re.search(r"(?:Condition|State|Quality|Wear)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if condition_match:
                item["condition"] = condition_match.group(1).strip()
                
            # Try to extract origin
            origin_match = re.search(r"(?:Origin|Source|Acquired|Got it|How)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if origin_match:
                item["origin"] = origin_match.group(1).strip()
                
            # Try to extract significance
            signif_match = re.search(r"(?:Significance|Meaning|Value|Important|Purpose)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if signif_match:
                item["significance"] = signif_match.group(1).strip()
                
            # Try to extract usage
            usage_match = re.search(r"(?:Usage|Use|When|How often)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if usage_match:
                item["usage"] = usage_match.group(1).strip()
                
            inventory.append(item)
            
        return inventory