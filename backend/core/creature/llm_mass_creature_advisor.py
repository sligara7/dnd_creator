"""
LLM Mass Creature Advisor Module

Uses LLM to make suggestions on amounts and types of creatures to face (combat) a party of adventurers.
Provides intelligent encounter composition based on party composition, environment, and desired difficulty.
Works in conjunction with LLMCreatureAdvisor for detailed individual creature creation.
"""

import json
import datetime
import re
import random
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

from backend.core.advisor.base_advisor import BaseAdvisor
from backend.core.creature.llm_creature_advisor import LLMCreatureAdvisor

import logging
logger = logging.getLogger(__name__)

class LLMMassCreatureAdvisor(BaseAdvisor):
    """
    Provides AI-powered assistance for creating groups of creatures to challenge an adventuring party.
    
    This class integrates with Language Learning Models (LLMs) to suggest appropriate
    combinations and quantities of creatures based on party composition, desired challenge level,
    and environmental context. It works alongside LLMCreatureAdvisor which focuses on 
    individual creature creation.
    """
    
    def __init__(self, llm_service=None, data_path: str = None, cache_enabled=True):
        """
        Initialize the LLM mass creature advisor.
        
        Args:
            llm_service: LLM service client for generating responses
            data_path: Optional path to encounter data
            cache_enabled: Whether to enable response caching
        """
        # Initialize base advisor with encounter-specific system prompt
        system_prompt = "You are a D&D 5e (2024 rules) encounter design expert specializing in balanced and thematic creature groups."
        super().__init__(llm_service, system_prompt, cache_enabled)
        
        # Set up paths and data - specific to mass creature advisor
        self.data_path = Path(data_path) if data_path else Path("backend/data/encounters")
        self.creature_advisor = LLMCreatureAdvisor(llm_service, data_path, cache_enabled)
        self._load_encounter_data()
    
    def _load_encounter_data(self):
        """Load reference data for encounter creation."""
        try:
            # Load challenge rating tables
            cr_path = self.data_path / "challenge_ratings.json"
            if cr_path.exists():
                with open(cr_path, "r") as f:
                    self.cr_data = json.load(f)
            else:
                self.cr_data = {}
                
            # Load encounter templates
            templates_path = self.data_path / "encounter_templates.json"
            if templates_path.exists():
                with open(templates_path, "r") as f:
                    self.encounter_templates = json.load(f)
            else:
                self.encounter_templates = {}
                
        except Exception as e:
            logger.error(f"Error loading encounter data: {e}")
            self.cr_data = {}
            self.encounter_templates = {}

    def suggest_encounter_composition(self, party_data: List[Dict[str, Any]], 
                                    difficulty: str = "medium",
                                    environment: str = None,
                                    theme: str = None) -> Dict[str, Any]:
        """
        Suggest a balanced encounter composition for a given party.
        
        Args:
            party_data: List of party member data 
            difficulty: Desired difficulty (easy, medium, hard, deadly)
            environment: Optional environmental context
            theme: Optional thematic focus
            
        Returns:
            Dict[str, Any]: Suggested encounter composition
        """
        # Calculate party level and size
        party_size = len(party_data)
        avg_level = sum(member.get("level", 1) for member in party_data) / max(1, party_size)
        
        # Build context for LLM
        context = f"Party Composition: {party_size} members, average level {avg_level:.1f}\n"
        context += f"Party Details:\n"
        
        for i, member in enumerate(party_data, 1):
            context += f"- Member {i}: Level {member.get('level', 1)} {member.get('class', 'Unknown')}\n"
            
        context += f"\nDesired Difficulty: {difficulty}\n"
        
        if environment:
            context += f"Environment: {environment}\n"
            
        if theme:
            context += f"Thematic Focus: {theme}\n"
            
        # Create prompt using base advisor's format_prompt method
        prompt = self._format_prompt(
            "Suggest a balanced encounter composition",
            context,
            [
                "Creature types and quantities that would make a balanced encounter",
                "Approximate challenge rating for the encounter",
                "Tactical relationships between the suggested creatures",
                "Environmental features that could enhance the encounter",
                "Reasoning for why this composition suits the party's capabilities"
            ]
        )
        
        try:
            # Generate encounter composition with LLM using base advisor's method
            response = self._get_llm_response(
                "encounter_composition", 
                prompt, 
                {"party_size": party_size, "avg_level": avg_level, "difficulty": difficulty}
            )
            
            # Parse the response into structured encounter data
            encounter_data = self._parse_encounter_composition(response)
            
            # Add metadata
            encounter_data["metadata"] = {
                "generated_at": datetime.datetime.now().isoformat(),
                "difficulty": difficulty,
                "environment": environment,
                "theme": theme,
                "party_size": party_size,
                "avg_party_level": avg_level
            }
            
            return {
                "success": True,
                "encounter": encounter_data,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to generate encounter composition: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate encounter composition: {str(e)}"
            }
            
    def create_themed_encounter(self, theme: str, party_level: int, 
                              party_size: int = 4,
                              environment: str = None,
                              difficulty: str = "medium") -> Dict[str, Any]:
        """
        Create a thematic encounter based on a specific theme or concept.
        
        Args:
            theme: Thematic focus for the encounter
            party_level: Average party level
            party_size: Number of party members
            environment: Optional environmental context
            difficulty: Desired difficulty level
            
        Returns:
            Dict[str, Any]: Themed encounter details
        """
        # Build context for LLM
        context = f"Thematic Focus: {theme}\n"
        context += f"Party: {party_size} members at level {party_level}\n"
        context += f"Difficulty Target: {difficulty}\n"
        
        if environment:
            context += f"Environment: {environment}\n"
            
        # Create prompt using base advisor's format_prompt method
        prompt = self._format_prompt(
            "Create a themed encounter",
            context,
            [
                "Narrative setup for the encounter",
                "Creature composition and quantities",
                "Environmental features that enhance the theme",
                "Tactical considerations for the encounter",
                "Treasure or rewards that fit the theme"
            ]
        )
        
        try:
            # Generate themed encounter with LLM using base advisor's method
            response = self._get_llm_response(
                "themed_encounter", 
                prompt, 
                {"theme": theme, "party_level": party_level, "difficulty": difficulty}
            )
            
            # Parse the response into structured encounter data
            encounter_data = self._parse_themed_encounter(response)
            
            # Add metadata
            encounter_data["metadata"] = {
                "generated_at": datetime.datetime.now().isoformat(),
                "theme": theme,
                "party_level": party_level,
                "party_size": party_size,
                "difficulty": difficulty,
                "environment": environment
            }
            
            return {
                "success": True,
                "encounter": encounter_data,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to generate themed encounter: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate themed encounter: {str(e)}"
            }
    
    def balance_encounter(self, encounter_data: Dict[str, Any], 
                        target_difficulty: str = None,
                        party_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Balance an existing encounter for a specific party or difficulty.
        
        Args:
            encounter_data: Existing encounter data
            target_difficulty: Optional new difficulty target
            party_data: Optional party data for custom balancing
            
        Returns:
            Dict[str, Any]: Balanced encounter data
        """
        # Extract current encounter details
        creatures = encounter_data.get("creatures", [])
        current_difficulty = encounter_data.get("difficulty", "medium")
        
        # Set target difficulty if not provided
        if not target_difficulty:
            target_difficulty = current_difficulty
            
        # Build context for LLM
        context = f"Current Encounter: {len(creatures)} creatures\n"
        context += f"Current Composition:\n"
        
        for creature in creatures:
            context += f"- {creature.get('quantity', 1)} x {creature.get('name', 'Unknown')} (CR {creature.get('cr', '?')})\n"
            
        context += f"\nCurrent Difficulty: {current_difficulty}\n"
        context += f"Target Difficulty: {target_difficulty}\n"
        
        if party_data:
            party_size = len(party_data)
            avg_level = sum(member.get("level", 1) for member in party_data) / max(1, party_size)
            context += f"Party: {party_size} members, average level {avg_level:.1f}\n"
            
        # Create prompt using base advisor's format_prompt method
        prompt = self._format_prompt(
            "Balance this encounter",
            context,
            [
                "Suggested modifications to creature quantities",
                "Potential creature substitutions",
                "Tactical adjustments to increase or decrease difficulty",
                "Environmental factors that could aid balancing",
                "Analysis of why these changes will achieve the target difficulty"
            ]
        )
        
        try:
            # Generate balance suggestions with LLM using base advisor's method
            response = self._get_llm_response(
                "balance_encounter", 
                prompt, 
                {
                    "current_difficulty": current_difficulty,
                    "target_difficulty": target_difficulty
                }
            )
            
            # Parse the response into structured balance data
            balance_data = self._parse_balance_suggestions(response)
            
            # Combine with original encounter data
            balanced_encounter = encounter_data.copy()
            balanced_encounter["creatures"] = balance_data.get("modified_creatures", creatures)
            balanced_encounter["difficulty"] = target_difficulty
            balanced_encounter["balance_suggestions"] = balance_data.get("suggestions", [])
            
            return {
                "success": True,
                "original_encounter": encounter_data,
                "balanced_encounter": balanced_encounter,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to balance encounter: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to balance encounter: {str(e)}"
            }
    
    # Parser methods for LLM responses - specific to encounter data
    
    def _parse_encounter_composition(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for encounter composition."""
        encounter_data = {
            "creatures": [],
            "environment_features": [],
            "difficulty": "medium",
            "cr": "unknown"
        }
        
        # Try to use BaseAdvisor's JSON extraction first
        extracted_json = self._extract_json(response)
        if extracted_json:
            return {**encounter_data, **extracted_json}
        
        # Otherwise fall back to regex parsing
        # Extract creature composition suggestions
        creature_blocks = re.findall(r"(?:Creature|Monster|Enemy):\s*([^\n]+)(?:\n(?:[^\n]+))*", response, re.IGNORECASE)
        for block in creature_blocks:
            creature = {"name": "Unknown Creature", "quantity": 1, "cr": "?"}
            
            # Try to extract creature name and quantity
            name_quantity_match = re.search(r"(\d+)\s*x\s*([^\n(]+)", block, re.IGNORECASE)
            if name_quantity_match:
                creature["quantity"] = int(name_quantity_match.group(1))
                creature["name"] = name_quantity_match.group(2).strip()
            else:
                name_match = re.search(r"^([^\n(]+)", block)
                if name_match:
                    creature["name"] = name_match.group(1).strip()
            
            # Try to extract CR
            cr_match = re.search(r"(?:CR|Challenge Rating):\s*(\d+(?:/\d+)?)", block, re.IGNORECASE)
            if cr_match:
                creature["cr"] = cr_match.group(1)
                
            encounter_data["creatures"].append(creature)
            
        # Try to extract CR
        cr_match = re.search(r"(?:CR|Challenge Rating):\s*(\d+(?:/\d+)?)", response, re.IGNORECASE)
        if cr_match:
            encounter_data["cr"] = cr_match.group(1)
            
        # Try to extract difficulty
        difficulty_match = re.search(r"(?:Difficulty):\s*(easy|medium|hard|deadly)", response, re.IGNORECASE)
        if difficulty_match:
            encounter_data["difficulty"] = difficulty_match.group(1).lower()
            
        # Extract environment features
        env_blocks = re.findall(r"(?:Environment|Feature):\s*([^\n]+)", response, re.IGNORECASE)
        encounter_data["environment_features"] = [feature.strip() for feature in env_blocks]
        
        return encounter_data
    
    def _parse_themed_encounter(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for themed encounters."""
        encounter_data = {
            "creatures": [],
            "narrative": "",
            "environment_features": [],
            "rewards": []
        }
        
        # Try to use BaseAdvisor's JSON extraction first
        extracted_json = self._extract_json(response)
        if extracted_json:
            return {**encounter_data, **extracted_json}
        
        # Extract narrative setup
        narrative_match = re.search(r"(?:Narrative|Setup):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if narrative_match:
            encounter_data["narrative"] = narrative_match.group(1).strip()
        
        # Extract creatures (similar to encounter composition)
        creature_blocks = re.findall(r"(?:Creature|Monster|Enemy):\s*([^\n]+)(?:\n(?:[^\n]+))*", response, re.IGNORECASE)
        for block in creature_blocks:
            creature = {"name": "Unknown Creature", "quantity": 1, "cr": "?"}
            
            # Try to extract creature name and quantity
            name_quantity_match = re.search(r"(\d+)\s*x\s*([^\n(]+)", block, re.IGNORECASE)
            if name_quantity_match:
                creature["quantity"] = int(name_quantity_match.group(1))
                creature["name"] = name_quantity_match.group(2).strip()
            else:
                name_match = re.search(r"^([^\n(]+)", block)
                if name_match:
                    creature["name"] = name_match.group(1).strip()
                    
            encounter_data["creatures"].append(creature)
        
        # Extract features
        feature_blocks = re.findall(r"(?:Feature|Environmental Feature):\s*([^\n]+)", response, re.IGNORECASE)
        encounter_data["environment_features"] = [feature.strip() for feature in feature_blocks]
        
        # Extract rewards
        reward_blocks = re.findall(r"(?:Reward|Treasure|Loot):\s*([^\n]+)", response, re.IGNORECASE)
        encounter_data["rewards"] = [reward.strip() for reward in reward_blocks]
        
        return encounter_data
        
    def _parse_balance_suggestions(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for encounter balance suggestions."""
        balance_data = {
            "modified_creatures": [],
            "suggestions": [],
            "tactical_adjustments": []
        }
        
        # Try to use BaseAdvisor's JSON extraction first
        extracted_json = self._extract_json(response)
        if extracted_json:
            return {**balance_data, **extracted_json}
        
        # Extract modified creature composition
        creature_blocks = re.findall(r"(?:Creature|Monster|Enemy)(?:[^:]*?):\s*([^\n]+)(?:\n(?:[^\n]+))*", response, re.IGNORECASE)
        for block in creature_blocks:
            creature = {"name": "Unknown Creature", "quantity": 1, "cr": "?"}
            
            # Try to extract creature name and quantity
            name_quantity_match = re.search(r"(\d+)\s*x\s*([^\n(]+)", block, re.IGNORECASE)
            if name_quantity_match:
                creature["quantity"] = int(name_quantity_match.group(1))
                creature["name"] = name_quantity_match.group(2).strip()
            else:
                name_match = re.search(r"^([^\n(]+)", block)
                if name_match:
                    creature["name"] = name_match.group(1).strip()
            
            balance_data["modified_creatures"].append(creature)
            
        # Extract suggestions
        suggestion_blocks = re.findall(r"(?:Suggestion|Modification|Adjustment):\s*([^\n]+)", response, re.IGNORECASE)
        balance_data["suggestions"] = [suggestion.strip() for suggestion in suggestion_blocks]
        
        # Extract tactical adjustments
        tactical_blocks = re.findall(r"(?:Tactical|Strategy|Tactic):\s*([^\n]+)", response, re.IGNORECASE)
        balance_data["tactical_adjustments"] = [tactic.strip() for tactic in tactical_blocks]
        
        return balance_data