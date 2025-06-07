"""
LLM Creature Advisor Module

Provides AI-powered assistance for single creature creation and enhancement using LLM integration.
This module enhances the core creature functionality with thematic suggestions and balance assessment.
"""

from typing import Dict, List, Any, Optional, Union
import json
import datetime
import re
from pathlib import Path

from backend.core.advisor.base_advisor import BaseAdvisor
from backend.core.ability_scores.ability_scores import AbilityScores
from backend.core.creature.abstract_creature import AbstractCreature

import logging
logger = logging.getLogger(__name__)

class LLMCreatureAdvisor(BaseAdvisor):
    """
    Provides AI-powered assistance for D&D creature creation and enhancement.
    
    This class integrates with Language Learning Models (LLMs) to provide creative
    and mechanical assistance for individual monster creation, focusing on thematic
    coherence, balance assessment, and flavor enhancement.
    """

    def __init__(self, llm_service=None, data_path: str = None, cache_enabled=True):
        """
        Initialize the LLM creature advisor.
        
        Args:
            llm_service: LLM service client for generating responses
            data_path: Optional path to creature data
            cache_enabled: Whether to enable response caching
        """
        # Initialize base advisor with creature-specific system prompt
        system_prompt = "You are a D&D 5e (2024 rules) creature design expert specializing in balanced monsters with compelling ecology and behavior."
        super().__init__(llm_service, system_prompt, cache_enabled)
            
        # Set up paths and data - specific to creature advisor
        self.data_path = Path(data_path) if data_path else Path("backend/data/creatures")
        self.ability_scores = AbilityScores()
        self._load_reference_data()

    def _load_reference_data(self):
        """Load reference data for creature creation."""
        try:
            # Load CR calculation reference
            cr_path = self.data_path / "challenge_ratings.json"
            if cr_path.exists():
                with open(cr_path, "r") as f:
                    self.cr_data = json.load(f)
            else:
                self.cr_data = {}
                
            # Load environment data
            env_path = self.data_path / "environments.json"
            if env_path.exists():
                with open(env_path, "r") as f:
                    self.environment_data = json.load(f)
            else:
                self.environment_data = {}
                
            # Load creature type data
            type_path = self.data_path / "creature_types.json"
            if type_path.exists():
                with open(type_path, "r") as f:
                    self.creature_type_data = json.load(f)
            else:
                self.creature_type_data = {}
                
        except Exception as e:
            logger.error(f"Error loading reference data: {e}")
            self.cr_data = {}
            self.environment_data = {}
            self.creature_type_data = {}

    def create_creature(self, ecology_description: str, party_level: int = None, 
                        campaign_theme: str = None) -> Dict[str, Any]:
        """
        Generate a thematically coherent creature based on environment and campaign needs.
        
        Args:
            ecology_description: Description of the ecological niche and requirements
            party_level: Optional target party level for appropriate challenge
            campaign_theme: Optional campaign theme for thematic consistency
            
        Returns:
            Dict[str, Any]: Suggested creature data
        """
        # Build context for LLM
        context = f"Ecological Context: {ecology_description}\n"
        
        if party_level:
            context += f"Target Party Level: {party_level}\n"
            context += f"Approximate CR Range: {max(1, party_level-2)} to {party_level+1}\n"
            
        if campaign_theme:
            context += f"Campaign Theme: {campaign_theme}\n"
            
        # Create prompt using base advisor's format_prompt method
        prompt = self._format_prompt(
            "Generate a thematic creature",
            context,
            [
                "Creature name and type (beast, monstrosity, etc.)",
                "Size and general appearance", 
                "Key abilities and traits that make it interesting",
                "Attack options that reflect its nature",
                "Brief ecological role and behavior",
                "Challenge rating suggestion and reasoning"
            ]
        )
        
        try:
            # Generate creature concept with LLM using base advisor's method
            response = self._get_llm_response(
                "creature_create", 
                prompt, 
                {"ecology": ecology_description[:50], "party_level": party_level}
            )
            
            # Parse the response into structured creature data
            creature_data = self._parse_creature_response(response)
            
            # Add metadata
            creature_data["metadata"] = {
                "generated_at": datetime.datetime.now().isoformat(),
                "ecology_description": ecology_description,
                "generation_method": "llm_assisted"
            }
            
            return {
                "success": True,
                "creature_concept": creature_data,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Failed to generate creature concept: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate creature concept: {str(e)}"
            }

    def validate_creature(self, creature_data: Dict[str, Any], 
                         include_balance_feedback: bool = True) -> Dict[str, Any]:
        """
        Validate creature and provide balance assessments with thematic suggestions.
        
        Args:
            creature_data: Creature data to validate
            include_balance_feedback: Whether to include detailed balance feedback
            
        Returns:
            Dict[str, Any]: Validation results with suggestions
        """
        # Mechanical validation first (standard checks)
        standard_validation = self._validate_creature_mechanics(creature_data)
        
        # If not requesting balance feedback or validation failed critically, return basic results
        if not include_balance_feedback or not standard_validation.get("is_valid", False):
            return standard_validation
            
        # Create context for balance assessment
        creature_type = creature_data.get("type", "unknown")
        creature_cr = creature_data.get("challenge_rating", "unknown")
        
        context = f"Creature: {creature_data.get('name', 'Unnamed creature')}\n"
        context += f"Type: {creature_type}\n"
        context += f"CR: {creature_cr}\n"
        context += f"HP: {creature_data.get('hit_points', 0)}\n"
        context += f"AC: {creature_data.get('armor_class', 10)}\n"
        
        # Add abilities/attacks info
        abilities = creature_data.get("abilities", [])
        attacks = creature_data.get("attacks", [])
        
        if abilities:
            context += "Abilities:\n"
            for ability in abilities:
                context += f"- {ability.get('name')}: {ability.get('description', '')}\n"
                
        if attacks:
            context += "Attacks:\n"
            for attack in attacks:
                context += f"- {attack.get('name')}: {attack.get('damage', 'N/A')} damage\n"
                
        # Use base advisor's format_prompt method
        prompt = self._format_prompt(
            "Assess creature balance",
            context,
            [
                "Overall balance assessment (underpowered, balanced, or overpowered)",
                "Specific mechanics that may need adjustment",
                "Thematic suggestions to maintain the concept while improving balance",
                "Synergies between abilities that might cause balance issues"
            ]
        )
        
        try:
            # Generate balance assessment using base advisor's method
            response = self._get_llm_response(
                "creature_validate", 
                prompt, 
                {"creature": creature_data.get("name", "unknown"), "cr": creature_cr}
            )
            
            # Parse the assessment
            assessment = self._parse_balance_assessment(response)
            
            # Combine with standard validation
            standard_validation["balance_assessment"] = assessment
            standard_validation["has_balance_feedback"] = True
            
            return standard_validation
        except Exception as e:
            logger.error(f"Error during balance assessment: {e}")
            standard_validation["balance_assessment"] = {"error": str(e)}
            standard_validation["has_balance_feedback"] = False
            return standard_validation

    def calculate_challenge_rating(self, creature_stats: Dict[str, Any],
                                 party_composition: List[Dict[str, Any]] = None,
                                 include_tactical_analysis: bool = False) -> Dict[str, Any]:
        """
        Calculate challenge rating and explain tactical implications for a specific party.
        
        Args:
            creature_stats: Creature statistics
            party_composition: Optional list of party member dictionaries
            include_tactical_analysis: Whether to include tactical analysis
            
        Returns:
            Dict[str, Any]: CR calculation with tactical implications
        """
        # Calculate base CR using standard formula
        base_cr = self._calculate_base_cr(creature_stats)
        
        # If not requesting tactical analysis or no party provided, return basic result
        if not include_tactical_analysis or not party_composition:
            return {
                "challenge_rating": base_cr,
                "has_tactical_analysis": False
            }
            
        # Create context for tactical analysis
        context = f"Creature: {creature_stats.get('name', 'Unnamed creature')}\n"
        context += f"Calculated CR: {base_cr}\n"
        context += f"HP: {creature_stats.get('hit_points', 0)}\n"
        context += f"AC: {creature_stats.get('armor_class', 10)}\n"
        
        # Add key abilities/resistances
        if "damage_resistances" in creature_stats:
            context += f"Resistances: {', '.join(creature_stats['damage_resistances'])}\n"
        if "damage_immunities" in creature_stats:
            context += f"Immunities: {', '.join(creature_stats['damage_immunities'])}\n"
        
        # Add party composition info
        context += "\nParty Composition:\n"
        for i, member in enumerate(party_composition, 1):
            context += f"Member {i}: Level {member.get('level', '?')} {member.get('class', '?')}\n"
            
        prompt = self._format_prompt(
            "Analyze tactical implications",
            context,
            [
                "Overall encounter difficulty (easy, medium, hard, deadly)",
                "Tactical advantages the creature has against this party",
                "Tactical advantages the party has against this creature",
                "Suggested tactics for the creature to maximize effectiveness",
                "Key party members who might struggle or excel"
            ]
        )
        
        try:
            # Generate tactical analysis using base advisor's method
            response = self._get_llm_response(
                "creature_tactics", 
                prompt, 
                {"creature": creature_stats.get("name", "unknown"), "party_size": len(party_composition)}
            )
            
            # Parse the analysis
            tactical_analysis = self._parse_tactical_analysis(response)
            
            return {
                "challenge_rating": base_cr,
                "tactical_analysis": tactical_analysis,
                "has_tactical_analysis": True
            }
        except Exception as e:
            logger.error(f"Error during tactical analysis: {e}")
            return {
                "challenge_rating": base_cr,
                "tactical_analysis": {"error": str(e)},
                "has_tactical_analysis": False
            }

    def calculate_hit_points(self, hit_dice: str, constitution: int,
                           resistances: List[str] = None,
                           include_physical_description: bool = False) -> Dict[str, Any]:
        """
        Calculate hit points and suggest narrative descriptions of the creature's physical resilience.
        
        Args:
            hit_dice: Hit dice expression (e.g., "3d8+6")
            constitution: Constitution score
            resistances: Optional list of damage resistances
            include_physical_description: Whether to include physical description
            
        Returns:
            Dict[str, Any]: HP calculation with physical description
        """
        # Calculate average hit points
        hit_points = self._calculate_average_hp(hit_dice, constitution)
            
        # Basic result
        result = {
            "hit_points": hit_points,
            "hit_dice": hit_dice,
            "constitution_modifier": self.ability_scores.calculate_modifier(constitution)
        }
        
        # If not requesting physical description, return basic result
        if not include_physical_description:
            result["has_physical_description"] = False
            return result
            
        # Create context for physical description
        context = f"Hit Points: {hit_points}\n"
        context += f"Hit Dice: {hit_dice}\n"
        context += f"Constitution: {constitution}\n"
        
        if resistances:
            context += f"Resistances: {', '.join(resistances)}\n"
            
        prompt = self._format_prompt(
            "Describe physical resilience",
            context,
            [
                "Evocative physical description that conveys toughness",
                "How body structure reflects durability",
                "Physical characteristics that explain damage resistances (if any)",
                "Visual details that help players understand the creature's toughness"
            ]
        )
        
        try:
            # Generate physical description using base advisor's method
            response = self._get_llm_response(
                "creature_resilience", 
                prompt, 
                {"hit_points": hit_points, "constitution": constitution}
            )
            
            result["physical_description"] = response.strip()
            result["has_physical_description"] = True
            
            return result
        except Exception as e:
            logger.error(f"Error generating physical description: {e}")
            result["physical_description"] = f"Error generating description: {str(e)}"
            result["has_physical_description"] = False
            return result

    def generate_attack_options(self, creature_type: str, cr: Union[str, float, int],
                              thematic_elements: List[str] = None,
                              distinctive_feature: str = None) -> Dict[str, Any]:
        """
        Generate unique and thematic attacks beyond standard options.
        
        Args:
            creature_type: Type of creature
            cr: Challenge rating
            thematic_elements: Optional list of thematic elements to incorporate
            distinctive_feature: Optional distinctive feature to base attacks on
            
        Returns:
            Dict[str, Any]: Generated attack options
        """
        # Get standard attacks first
        standard_attacks = self._generate_standard_attacks(creature_type, cr)
        
        # If no thematic elements or distinctive feature, return standard attacks
        if not thematic_elements and not distinctive_feature:
            return {
                "attacks": standard_attacks,
                "has_thematic_attacks": False
            }
            
        # Create context for thematic attacks
        context = f"Creature Type: {creature_type}\n"
        context += f"Challenge Rating: {cr}\n"
        
        if thematic_elements:
            context += f"Thematic Elements: {', '.join(thematic_elements)}\n"
            
        if distinctive_feature:
            context += f"Distinctive Feature: {distinctive_feature}\n"
            
        # Include basic attack expectations
        if float(cr) < 5:
            context += "Attack Expectation: 1-2 attacks with moderate damage\n"
        elif float(cr) < 10:
            context += "Attack Expectation: 2-3 attacks with significant damage or effects\n"
        else:
            context += "Attack Expectation: Multiple attacks with significant damage and special effects\n"
            
        prompt = self._format_prompt(
            "Create thematic attacks",
            context,
            [
                "Name of each attack",
                "Attack type (melee, ranged, area)",
                "Attack bonus or save DC",
                "Damage amount and type",
                "Special effects or conditions",
                "Brief flavor description",
                "At least one signature ability unique to this creature"
            ]
        )
        
        try:
            # Generate thematic attacks using base advisor's method
            response = self._get_llm_response(
                "creature_attacks", 
                prompt, 
                {"creature_type": creature_type, "cr": str(cr)}
            )
            
            # Parse the attacks
            thematic_attacks = self._parse_attack_response(response)
            
            # Combine standard and thematic attacks
            combined_attacks = thematic_attacks
            
            # Add any standard attacks that don't overlap with thematic ones
            thematic_names = {attack["name"].lower() for attack in thematic_attacks}
            for attack in standard_attacks:
                if attack["name"].lower() not in thematic_names:
                    combined_attacks.append(attack)
            
            return {
                "attacks": combined_attacks,
                "has_thematic_attacks": True
            }
        except Exception as e:
            logger.error(f"Error generating thematic attacks: {e}")
            return {
                "attacks": standard_attacks,
                "thematic_error": str(e),
                "has_thematic_attacks": False
            }

    def get_available_traits(self, creature_type: str, environment: str,
                           behavioral_focus: str = None,
                           adaptation_level: str = None) -> Dict[str, Any]:
        """
        Develop environmentally-appropriate traits and behaviors for creatures.
        
        Args:
            creature_type: Type of creature
            environment: Environmental context
            behavioral_focus: Optional focus area for behaviors (e.g., "hunting", "defense")
            adaptation_level: Optional adaptation level ("mild", "moderate", "extreme")
            
        Returns:
            Dict[str, Any]: Environmental traits and behaviors
        """
        # Get standard traits first
        standard_traits = self._get_standard_traits(creature_type, environment)
        
        # If no behavioral focus or adaptation level, return standard traits
        if not behavioral_focus and not adaptation_level:
            return {
                "traits": standard_traits,
                "has_environmental_traits": False
            }
            
        # Default adaptation level if not provided
        if not adaptation_level:
            adaptation_level = "moderate"
            
        # Create context for environmental traits
        context = f"Creature Type: {creature_type}\n"
        context += f"Environment: {environment}\n"
        
        if behavioral_focus:
            context += f"Behavioral Focus: {behavioral_focus}\n"
            
        context += f"Adaptation Level: {adaptation_level}\n"
            
        prompt = self._format_prompt(
            "Generate environmental traits",
            context,
            [
                "Name of each trait",
                "Mechanical effect in game terms",
                "Brief description of how it manifests",
                "Ecological reasoning behind the adaptation",
                "How the trait provides unique advantages in the environment"
            ]
        )
        
        try:
            # Generate environmental traits using base advisor's method
            response = self._get_llm_response(
                "creature_traits", 
                prompt, 
                {
                    "creature_type": creature_type, 
                    "environment": environment,
                    "focus": behavioral_focus or "general"
                }
            )
            
            # Parse the traits
            environmental_traits = self._parse_traits_response(response)
            
            # Combine standard and environmental traits
            combined_traits = environmental_traits
            
            # Add any standard traits that don't overlap with environmental ones
            environmental_names = {trait["name"].lower() for trait in environmental_traits}
            for trait in standard_traits:
                if trait["name"].lower() not in environmental_names:
                    combined_traits.append(trait)
            
            return {
                "traits": combined_traits,
                "has_environmental_traits": True
            }
        except Exception as e:
            logger.error(f"Error generating environmental traits: {e}")
            return {
                "traits": standard_traits,
                "environmental_error": str(e),
                "has_environmental_traits": False
            }

    def generate_creature_illustration_prompt(self, creature_data: Dict[str, Any],
                                           style: str = "realistic") -> Dict[str, Any]:
        """
        Create a prompt for generating creature illustrations with image generation models.
        
        Args:
            creature_data: Creature data
            style: Desired art style
            
        Returns:
            Dict[str, Any]: Illustration prompt and details
        """
        # Create context for illustration
        context = f"Creature: {creature_data.get('name', 'Unnamed creature')}\n"
        context += f"Type: {creature_data.get('type', 'unknown')}\n"
        context += f"Size: {creature_data.get('size', 'medium')}\n\n"
        
        # Add physical description if available
        if "description" in creature_data:
            context += f"Description: {creature_data['description']}\n\n"
            
        # Add distinctive features
        features = []
        if "traits" in creature_data:
            for trait in creature_data["traits"]:
                if "description" in trait:
                    features.append(trait["description"])
                    
        if features:
            context += "Distinctive Features:\n"
            for feature in features[:3]:  # Limit to top 3 features
                context += f"- {feature}\n"
                
        context += f"\nDesired Art Style: {style}\n"
            
        prompt = self._format_prompt(
            "Generate illustration prompt",
            context,
            [
                "Detailed physical description and anatomy",
                "Color scheme and textures",
                "Pose and action",
                "Environmental elements and background",
                "Lighting and mood",
                "Artistic style specifications suitable for image generation"
            ]
        )
        
        try:
            # Generate illustration prompt using base advisor's method
            response = self._get_llm_response(
                "creature_illustration", 
                prompt, 
                {"creature": creature_data.get("name", "unknown"), "style": style}
            )
            
            return {
                "success": True,
                "illustration_prompt": response.strip(),
                "style": style
            }
        except Exception as e:
            logger.error(f"Error generating illustration prompt: {e}")
            return {
                "success": False,
                "error": f"Failed to generate illustration prompt: {str(e)}"
            }

    def suggest_creature_tactics(self, creature_data: Dict[str, Any],
                               environment: str = None) -> Dict[str, Any]:
        """
        Suggest tactics and behavior for a creature in combat.
        
        Args:
            creature_data: Creature data
            environment: Optional environment context
            
        Returns:
            Dict[str, Any]: Tactical suggestions
        """
        # Get intelligence from creature data or default to 10
        intelligence = creature_data.get("ability_scores", {}).get("intelligence", 10)
            
        # Create context for tactics
        context = f"Creature: {creature_data.get('name', 'Unnamed creature')}\n"
        context += f"Type: {creature_data.get('type', 'unknown')}\n"
        context += f"CR: {creature_data.get('challenge_rating', 'unknown')}\n"
        context += f"Intelligence: {intelligence}\n\n"
        
        # Add abilities and attacks
        abilities = creature_data.get("abilities", [])
        attacks = creature_data.get("attacks", [])
        
        if abilities:
            context += "Abilities:\n"
            for ability in abilities:
                context += f"- {ability.get('name')}: {ability.get('description', '')}\n"
                
        if attacks:
            context += "\nAttacks:\n"
            for attack in attacks:
                context += f"- {attack.get('name')}: {attack.get('description', '')}\n"
                
        if environment:
            context += f"\nEnvironment: {environment}\n"
            
        prompt = self._format_prompt(
            "Suggest creature tactics",
            context,
            [
                "Opening moves and initial approach",
                "Primary targets and priorities",
                "Effective use of abilities and attacks",
                "Environmental tactics and positioning",
                "Retreat conditions and self-preservation",
                "Group tactics if applicable"
            ]
        )
        
        try:
            # Generate tactical suggestions using base advisor's method
            response = self._get_llm_response(
                "creature_combat_tactics", 
                prompt, 
                {
                    "creature": creature_data.get("name", "unknown"),
                    "intelligence": intelligence,
                    "environment": environment or "any"
                }
            )
            
            # Parse the tactics
            tactics = self._parse_tactics_response(response)
            
            return {
                "success": True,
                "tactics": tactics
            }
        except Exception as e:
            logger.error(f"Error suggesting combat tactics: {e}")
            return {
                "success": False,
                "error": f"Failed to suggest tactics: {str(e)}"
            }

    # Domain-specific helper methods - keeping these as is for creature functionality

    def _validate_creature_mechanics(self, creature_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform basic mechanical validation of creature stats."""
        errors = []
        warnings = []
        
        # Check for required fields
        required_fields = ["name", "type", "size", "hit_points", "armor_class"]
        for field in required_fields:
            if field not in creature_data:
                errors.append(f"Missing required field: {field}")
        
        # Check CR is appropriate (simplified)
        cr = creature_data.get("challenge_rating", 0)
        hp = creature_data.get("hit_points", 0)
        
        if hp > 0 and cr > 0:
            expected_hp_min = cr * 10
            expected_hp_max = cr * 30
            
            if hp < expected_hp_min:
                warnings.append(f"HP ({hp}) may be too low for CR {cr}. Expected at least {expected_hp_min}.")
            elif hp > expected_hp_max:
                warnings.append(f"HP ({hp}) may be too high for CR {cr}. Expected at most {expected_hp_max}.")
        
        return {
            "is_valid": len(errors) == 0,
            "validation_errors": errors,
            "validation_warnings": warnings
        }
        
    def _calculate_base_cr(self, creature_stats: Dict[str, Any]) -> float:
        """Calculate base challenge rating using standard formula."""
        # This is a simplified calculation
        hp = creature_stats.get("hit_points", 0)
        ac = creature_stats.get("armor_class", 10)
        
        # Defensive CR based on HP and AC
        if hp <= 6:
            def_cr = 0
        elif hp <= 35:
            def_cr = 1/8
        elif hp <= 49:
            def_cr = 1/4
        elif hp <= 70:
            def_cr = 1/2
        elif hp <= 85:
            def_cr = 1
        else:
            def_cr = 1 + ((hp - 85) // 15)
            
        # AC adjustment
        ac_diff = ac - 13
        if ac_diff != 0:
            def_cr_adjustment = ac_diff // 2
            def_cr = max(0, def_cr + def_cr_adjustment)
        
        # Placeholder for offensive CR (would be more complex in reality)
        off_cr = creature_stats.get("challenge_rating", def_cr)
        
        # Average the two
        return (def_cr + off_cr) / 2
        
    def _calculate_average_hp(self, hit_dice: str, constitution: int) -> int:
        """Calculate average hit points from hit dice and constitution."""
        # Extract number of dice, die type, and bonus
        match = re.match(r"(\d+)d(\d+)([+-]\d+)?", hit_dice)
        if not match:
            return 10
            
        num_dice = int(match.group(1))
        die_type = int(match.group(2))
        bonus_str = match.group(3) or "+0"
        bonus = int(bonus_str)
        
        # Calculate average roll for each die
        avg_per_die = (die_type + 1) / 2
        
        # Calculate total average
        return int(num_dice * avg_per_die) + bonus
        
    def _generate_standard_attacks(self, creature_type: str, cr: Union[str, float, int]) -> List[Dict[str, Any]]:
        """Generate standard attacks based on creature type and CR."""
        attacks = []
        cr_value = float(cr)
        
        # Convert to numeric CR
        if isinstance(cr, str) and "/" in cr:
            num, den = cr.split("/")
            cr_value = float(num) / float(den)
        
        # Basic attack based on creature type
        if creature_type == "beast":
            attacks.append({
                "name": "Bite",
                "type": "melee",
                "attack_bonus": max(2, int(2 + cr_value)),
                "damage": f"{1 + min(3, int(cr_value))}d6+{max(2, int(cr_value))}",
                "damage_type": "piercing"
            })
        elif creature_type == "monstrosity":
            attacks.append({
                "name": "Claw",
                "type": "melee",
                "attack_bonus": max(3, int(3 + cr_value)),
                "damage": f"{1 + min(2, int(cr_value))}d8+{max(2, int(cr_value))}",
                "damage_type": "slashing"
            })
        elif creature_type == "dragon":
            attacks.append({
                "name": "Bite",
                "type": "melee",
                "attack_bonus": max(4, int(4 + cr_value)),
                "damage": f"{2 + min(2, int(cr_value))}d10+{max(3, int(cr_value))}",
                "damage_type": "piercing"
            })
        else:
            # Generic attack
            attacks.append({
                "name": "Strike",
                "type": "melee",
                "attack_bonus": max(3, int(3 + cr_value/2)),
                "damage": f"{1 + min(2, int(cr_value/2))}d6+{max(2, int(cr_value/2))}",
                "damage_type": "bludgeoning"
            })
        
        return attacks
        
    def _get_standard_traits(self, creature_type: str, environment: str) -> List[Dict[str, Any]]:
        """Get standard traits based on creature type and environment."""
        traits = []
        
        # Type-based traits
        if creature_type == "beast":
            traits.append({
                "name": "Keen Senses",
                "description": "The creature has advantage on Wisdom (Perception) checks that rely on smell."
            })
        elif creature_type == "undead":
            traits.append({
                "name": "Undead Nature",
                "description": "The creature doesn't require air, food, drink, or sleep."
            })
        elif creature_type == "construct":
            traits.append({
                "name": "Constructed Nature",
                "description": "The creature doesn't require air, food, drink, or sleep, and is immune to disease."
            })
        
        # Environment-based traits
        if environment == "aquatic":
            traits.append({
                "name": "Amphibious",
                "description": "The creature can breathe both air and water."
            })
        elif environment == "underground":
            traits.append({
                "name": "Darkvision",
                "description": "The creature can see in darkness within 60 feet as if it were dim light."
            })
        elif environment == "desert":
            traits.append({
                "name": "Desert Camouflage",
                "description": "The creature has advantage on Dexterity (Stealth) checks made to hide in desert terrain."
            })
        
        return traits

    # Parser methods for LLM responses - keeping these for creature-specific parsing
    
    def _parse_creature_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for creature generation."""
        creature_data = {
            "name": "Unknown Creature",
            "type": "beast",
            "size": "medium",
            "abilities": [],
            "attacks": [],
            "traits": [],
            "challenge_rating": 1
        }
        
        # Try to use BaseAdvisor's JSON extraction first
        extracted_json = self._extract_json(response)
        if extracted_json:
            return {**creature_data, **extracted_json}
        
        # Otherwise fall back to regex parsing
        # Try to extract creature name
        name_match = re.search(r"(?:Creature name|Name):\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            creature_data["name"] = name_match.group(1).strip()
            
        # Try to extract creature type
        type_match = re.search(r"(?:Creature type|Type):\s*([^\n]+)", response, re.IGNORECASE)
        if type_match:
            creature_data["type"] = type_match.group(1).strip().lower()
            
        # Try to extract size
        size_match = re.search(r"(?:Size):\s*([^\n]+)", response, re.IGNORECASE)
        if size_match:
            creature_data["size"] = size_match.group(1).strip().lower()
            
        # Try to extract CR
        cr_match = re.search(r"(?:Challenge Rating|CR):\s*(\d+(?:/\d+)?)", response, re.IGNORECASE)
        if cr_match:
            cr_str = cr_match.group(1)
            if "/" in cr_str:  # Handle fractions like 1/4
                num, den = cr_str.split("/")
                creature_data["challenge_rating"] = float(num) / float(den)
            else:
                creature_data["challenge_rating"] = float(cr_str)
                
        # Extract description if present
        desc_match = re.search(r"(?:Description|Appearance):\s*([^\n]+(?:\n[^\n]+)*)", response, re.IGNORECASE)
        if desc_match:
            creature_data["description"] = desc_match.group(1).strip()
            
        # Try to find abilities/traits
        ability_blocks = re.findall(r"(?:Ability|Trait):\s*([^\n]+)(?:\n(?:[^\n]+))*", response, re.IGNORECASE)
        for block in ability_blocks:
            ability = {"name": "Unknown Ability"}
            
            # Try to extract ability name and description
            ability_lines = block.strip().split("\n")
            if ability_lines:
                name_line = ability_lines[0]
                name_parts = name_line.split(":", 1)
                if len(name_parts) > 1:
                    ability["name"] = name_parts[1].strip()
                else:
                    ability["name"] = name_line.strip()
                    
                if len(ability_lines) > 1:
                    ability["description"] = "\n".join(ability_lines[1:]).strip()
                    
            creature_data["abilities"].append(ability)
            
        # Try to find attacks
        attack_blocks = re.findall(r"(?:Attack):\s*([^\n]+)(?:\n(?:[^\n]+))*", response, re.IGNORECASE)
        for block in attack_blocks:
            attack = {"name": "Unknown Attack"}
            
            # Extract attack name and description similar to abilities
            attack_lines = block.strip().split("\n")
            if attack_lines:
                name_line = attack_lines[0]
                name_parts = name_line.split(":", 1)
                if len(name_parts) > 1:
                    attack["name"] = name_parts[1].strip()
                else:
                    attack["name"] = name_line.strip()
                    
                if len(attack_lines) > 1:
                    attack["description"] = "\n".join(attack_lines[1:]).strip()
                    
                # Try to extract damage if mentioned
                damage_match = re.search(r"(\d+d\d+(?:\s*[+]\s*\d+)?)\s+(\w+)\s+damage", 
                                        "\n".join(attack_lines), re.IGNORECASE)
                if damage_match:
                    attack["damage"] = damage_match.group(1).strip()
                    attack["damage_type"] = damage_match.group(2).strip().lower()
                    
            creature_data["attacks"].append(attack)
        
        return creature_data
    
    def _parse_balance_assessment(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for balance assessment."""
        assessment = {
            "overall_balance": "unknown",
            "issues": [],
            "suggestions": []
        }
        
        # Try BaseAdvisor's JSON extraction first
        extracted_json = self._extract_json(response)
        if extracted_json:
            return {**assessment, **extracted_json}
            
        # Try to determine overall balance rating
        if "underpowered" in response.lower():
            assessment["overall_balance"] = "underpowered"
        elif "overpowered" in response.lower():
            assessment["overall_balance"] = "overpowered"
        else:
            assessment["overall_balance"] = "balanced"
            
        # Extract issues and suggestions - use BaseAdvisor's extract_list_items method
        issues = self._extract_list_items(response, ["issue", "problem", "concern"])
        suggestions = self._extract_list_items(response, ["suggest", "recommend", "adjustment"])
        
        if issues:
            assessment["issues"] = issues
        
        if suggestions:
            assessment["suggestions"] = suggestions
        
        return assessment
    
    def _parse_tactical_analysis(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for tactical analysis."""
        analysis = {
            "difficulty_assessment": "unknown",
            "creature_advantages": [],
            "party_advantages": [],
            "tactical_suggestions": []
        }
        
        # Try BaseAdvisor's JSON extraction first
        extracted_json = self._extract_json(response)
        if extracted_json:
            return {**analysis, **extracted_json}
            
        # Try to determine difficulty assessment
        if "easy" in response.lower():
            analysis["difficulty_assessment"] = "easy"
        elif "medium" in response.lower():
            analysis["difficulty_assessment"] = "medium"
        elif "hard" in response.lower():
            analysis["difficulty_assessment"] = "hard"
        elif "deadly" in response.lower():
            analysis["difficulty_assessment"] = "deadly"
            
        # Extract different sections using BaseAdvisor's extract_list_items method
        creature_advantages = self._extract_list_items(response, ["creature advantage", "tactical advantage"])
        party_advantages = self._extract_list_items(response, ["party advantage"])
        tactical_suggestions = self._extract_list_items(response, ["tactic", "suggest", "recommend"])
        
        if creature_advantages:
            analysis["creature_advantages"] = creature_advantages
        
        if party_advantages:
            analysis["party_advantages"] = party_advantages
            
        if tactical_suggestions:
            analysis["tactical_suggestions"] = tactical_suggestions
                
        return analysis
    
    def _parse_attack_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for thematic attacks."""
        attacks = []
        
        # Try BaseAdvisor's JSON extraction first
        extracted_json = self._extract_json(response)
        if extracted_json and isinstance(extracted_json, list):
            return extracted_json
        
        # Look for attack blocks
        attack_blocks = re.findall(r"(?:Attack|Ability):\s*([^\n]+)(?:\n(?:[^\n]+))*", response, re.IGNORECASE)
        if not attack_blocks:
            # Try another pattern for numbered attacks
            attack_blocks = re.findall(r"\d+\.\s+([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", response)
        
        for block in attack_blocks:
            attack = {"name": "Unknown Attack"}
            
            # Try to extract attack name
            name_match = re.search(r"^([^:\.]+)", block)
            if name_match:
                attack["name"] = name_match.group(1).strip()
                
            # Try to extract attack type
            type_match = re.search(r"(?:Type|Attack Type):\s*([^\n]+)", block, re.IGNORECASE)
            if type_match:
                attack["type"] = type_match.group(1).strip().lower()
                
            # Try to extract attack bonus
            bonus_match = re.search(r"(?:Attack Bonus|To Hit):\s*([+]\d+)", block, re.IGNORECASE)
            if bonus_match:
                attack["attack_bonus"] = int(bonus_match.group(1).replace("+", ""))
                
            # Try to extract damage
            damage_match = re.search(r"(?:Damage|Damage Roll):\s*([^\n]+)", block, re.IGNORECASE)
            if damage_match:
                damage_text = damage_match.group(1).strip()
                attack["damage"] = damage_text
                
                # Try to extract damage type
                damage_type_match = re.search(r"(\d+d\d+(?:\s*[+]\s*\d+)?)\s+(\w+)", damage_text)
                if damage_type_match:
                    attack["damage_type"] = damage_type_match.group(2).lower()
                
            # Try to extract effect
            effect_match = re.search(r"(?:Effect|Special):\s*([^\n]+)", block, re.IGNORECASE)
            if effect_match:
                attack["effect"] = effect_match.group(1).strip()
                
            # Try to extract description
            desc_match = re.search(r"(?:Description|Flavor):\s*([^\n]+)", block, re.IGNORECASE)
            if desc_match:
                attack["description"] = desc_match.group(1).strip()
                
            attacks.append(attack)
            
        return attacks
    
    def _parse_traits_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for environmental traits."""
        traits = []
        
        # Try BaseAdvisor's JSON extraction first
        extracted_json = self._extract_json(response)
        if extracted_json and isinstance(extracted_json, list):
            return extracted_json
        
        # Look for trait blocks
        trait_blocks = re.findall(r"(?:Trait|Ability|Adaptation):\s*([^\n]+)(?:\n(?:[^\n]+))*", response, re.IGNORECASE)
        if not trait_blocks:
            # Try another pattern for numbered traits
            trait_blocks = re.findall(r"\d+\.\s+([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", response)
        
        for block in trait_blocks:
            trait = {"name": "Unknown Trait"}
            
            # Try to extract trait name
            name_match = re.search(r"^([^:\.]+)", block)
            if name_match:
                trait["name"] = name_match.group(1).strip()
                
            # Try to extract mechanical effect
            effect_match = re.search(r"(?:Effect|Mechanical Effect|Game Mechanics):\s*([^\n]+)", block, re.IGNORECASE)
            if effect_match:
                trait["effect"] = effect_match.group(1).strip()
                
            # Try to extract description
            desc_match = re.search(r"(?:Description|Manifestation):\s*([^\n]+)", block, re.IGNORECASE)
            if desc_match:
                trait["description"] = desc_match.group(1).strip()
            
            # Try to extract ecological reasoning
            reason_match = re.search(r"(?:Reasoning|Ecological Reasoning|Adaptation Reason):\s*([^\n]+)", block, re.IGNORECASE)
            if reason_match:
                trait["reasoning"] = reason_match.group(1).strip()
                
            traits.append(trait)
            
        return traits
                
    def _parse_tactics_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for creature tactics."""
        tactics = {
            "opening_moves": "",
            "priority_targets": "",
            "ability_usage": "",
            "positioning": "",
            "retreat_conditions": "",
            "full_description": response
        }
        
        # Try BaseAdvisor's JSON extraction first
        extracted_json = self._extract_json(response)
        if extracted_json:
            return {**tactics, **extracted_json}
        
        # Use BaseAdvisor's extract section method if available (added as helper)
        sections = {
            "opening_moves": ["Opening", "Initial", "First"],
            "priority_targets": ["Target", "Priority"],
            "ability_usage": ["Abilities", "Special", "Ability Usage"],
            "positioning": ["Position", "Environmental", "Terrain"],
            "retreat_conditions": ["Retreat", "Withdrawal", "Flee"]
        }
        
        for key, terms in sections.items():
            for term in terms:
                pattern = rf"(?:{term})(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)"
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    tactics[key] = match.group(1).strip()
                    break
        
        return tactics