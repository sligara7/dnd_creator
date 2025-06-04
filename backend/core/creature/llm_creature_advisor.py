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

try:
    from backend.core.ability_scores.ability_scores import AbilityScores
    from backend.core.ollama_service import OllamaService
    from backend.core.creature.abstract_creature import AbstractCreature
except ImportError:
    # Fallback for development
    class AbilityScores:
        def calculate_modifier(self, score): return (score - 10) // 2
    
    class OllamaService:
        def __init__(self): pass
        def generate(self, prompt): return "LLM service not available"
    
    AbstractCreature = object


class LLMCreatureAdvisor:
    """
    Provides AI-powered assistance for D&D creature creation and enhancement.
    
    This class integrates with Language Learning Models (LLMs) to provide creative
    and mechanical assistance for individual monster creation, focusing on thematic
    coherence, balance assessment, and flavor enhancement.
    """

    def __init__(self, llm_service=None, data_path: str = None):
        """
        Initialize the LLM creature advisor.
        
        Args:
            llm_service: LLM service client for generating responses
            data_path: Optional path to creature data
        """
        # Initialize LLM service
        self.llm_service = llm_service or OllamaService()
            
        # Set up paths and data
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
            print(f"Error loading reference data: {e}")
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
            
        # Create prompt for creature generation
        prompt = self._create_prompt(
            "generate a thematic creature",
            context + "\n"
            "Create a coherent D&D creature that fits this ecological niche and campaign needs.\n"
            "Include the following information in your response:\n"
            "- Creature name and type (beast, monstrosity, etc.)\n"
            "- Size and general appearance\n"
            "- Key abilities and traits that make it interesting\n"
            "- Attack options that reflect its nature\n"
            "- Brief ecological role and behavior\n"
            "- Challenge rating suggestion and reasoning\n\n"
            "Make sure the creature is balanced for the target party level if provided."
        )
        
        try:
            # Generate creature concept with LLM
            response = self.llm_service.generate(prompt)
            
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
            
        # Create prompt for balance assessment
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
                context += f"- {ability.get('name')}: {ability.get('description')}\n"
                
        if attacks:
            context += "Attacks:\n"
            for attack in attacks:
                context += f"- {attack.get('name')}: {attack.get('damage', 'N/A')} damage\n"
                
        prompt = self._create_prompt(
            "assess creature balance",
            context + "\n"
            "Analyze this creature for D&D 5e balance at the given CR. Provide:\n"
            "1. Assessment of overall balance (underpowered, balanced, or overpowered)\n"
            "2. Specific mechanics that may need adjustment\n"
            "3. Thematic suggestions to maintain the creature concept while improving balance\n"
            "4. Any synergies between abilities that might cause balance issues\n\n"
            "Focus on maintaining the thematic elements while achieving appropriate challenge."
        )
        
        try:
            # Generate balance assessment
            response = self.llm_service.generate(prompt)
            
            # Parse the assessment
            assessment = self._parse_balance_assessment(response)
            
            # Combine with standard validation
            standard_validation["balance_assessment"] = assessment
            standard_validation["has_balance_feedback"] = True
            
            return standard_validation
        except Exception as e:
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
            
        # Create prompt for tactical analysis
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
            
        prompt = self._create_prompt(
            "analyze tactical implications",
            context + "\n"
            "Analyze how this creature would challenge this specific party composition. Provide:\n"
            "1. Overall assessment of the encounter difficulty (easy, medium, hard, deadly)\n"
            "2. Tactical advantages the creature has against this party\n"
            "3. Tactical advantages the party has against this creature\n"
            "4. Suggested tactics for the creature to maximize effectiveness\n"
            "5. Key party members who might struggle or excel in this encounter\n\n"
            "Consider damage types, special abilities, and party composition in your analysis."
        )
        
        try:
            # Generate tactical analysis
            response = self.llm_service.generate(prompt)
            
            # Parse the analysis
            tactical_analysis = self._parse_tactical_analysis(response)
            
            return {
                "challenge_rating": base_cr,
                "tactical_analysis": tactical_analysis,
                "has_tactical_analysis": True
            }
        except Exception as e:
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
            
        # Create prompt for physical description
        context = f"Hit Points: {hit_points}\n"
        context += f"Hit Dice: {hit_dice}\n"
        context += f"Constitution: {constitution}\n"
        
        if resistances:
            context += f"Resistances: {', '.join(resistances)}\n"
            
        prompt = self._create_prompt(
            "describe physical resilience",
            context + "\n"
            "Create an evocative physical description that conveys this creature's toughness and resilience.\n"
            "Focus on how its body structure, hide, scales, or other features reflect its durability.\n"
            "If the creature has any damage resistances, describe the physical characteristics that explain these resistances.\n"
            "The description should be vivid, specific, and help players visualize why this creature is so tough."
        )
        
        try:
            # Generate physical description
            response = self.llm_service.generate(prompt)
            
            result["physical_description"] = response.strip()
            result["has_physical_description"] = True
            
            return result
        except Exception as e:
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
            
        # Create prompt for thematic attacks
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
            
        prompt = self._create_prompt(
            "create thematic attacks",
            context + "\n"
            "Create unique and thematic attacks for this creature that go beyond standard options.\n"
            "For each attack, provide:\n"
            "1. Name of the attack\n"
            "2. Attack type (melee, ranged, area)\n"
            "3. Attack bonus or save DC\n"
            "4. Damage amount and type\n"
            "5. Any special effects or conditions\n"
            "6. Brief flavor description\n\n"
            "Create at least one standard attack and one signature ability that's unique to this creature.\n"
            "Ensure the attacks are balanced for the creature's CR while remaining thematically interesting."
        )
        
        try:
            # Generate thematic attacks
            response = self.llm_service.generate(prompt)
            
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
            
        # Create prompt for environmental traits
        context = f"Creature Type: {creature_type}\n"
        context += f"Environment: {environment}\n"
        
        if behavioral_focus:
            context += f"Behavioral Focus: {behavioral_focus}\n"
            
        context += f"Adaptation Level: {adaptation_level}\n"
            
        prompt = self._create_prompt(
            "generate environmental traits",
            context + "\n"
            "Develop environmentally-appropriate traits and behaviors for this creature.\n"
            "Consider how evolution in this environment would shape the creature's:\n"
            "1. Sensory capabilities\n"
            "2. Movement and locomotion\n"
            "3. Hunting or foraging strategies\n"
            "4. Defense mechanisms\n"
            "5. Social behavior\n\n"
            "For each trait, provide:\n"
            "- Name of the trait\n"
            "- Mechanical effect in game terms\n"
            "- Brief description of how it manifests\n"
            "- Ecological reasoning behind the adaptation\n\n"
            "Create traits that are balanced but provide the creature with unique advantages in its environment."
        )
        
        try:
            # Generate environmental traits
            response = self.llm_service.generate(prompt)
            
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
            return {
                "traits": standard_traits,
                "environmental_error": str(e),
                "has_environmental_traits": False
            }

    def export_creature_statblock(self, creature_data: Dict[str, Any],
                                include_ecology: bool = False,
                                encounter_suggestions: bool = False,
                                format: str = 'pdf') -> Dict[str, Any]:
        """
        Export creature statblock with optional behavioral notes and ecology.
        
        Args:
            creature_data: Base creature data
            include_ecology: Whether to include ecology information
            encounter_suggestions: Whether to include encounter suggestions
            format: Output format ('pdf', 'json', 'markdown', etc.)
            
        Returns:
            Dict[str, Any]: Enhanced statblock data and export information
        """
        # Start with base creature data
        enhanced_data = creature_data.copy()
        
        # If requested, enhance the creature with ecology information
        if include_ecology:
            ecology_data = self._generate_ecology_description(creature_data)
            enhanced_data["ecology"] = ecology_data
        
        # Format-specific export handling
        export_result = {
            "format": format,
            "creature_id": creature_data.get("id", "unknown"),
            "export_time": datetime.datetime.now().isoformat()
        }
        
        if format.lower() == 'pdf':
            # PDF generation would happen here
            export_result["status"] = "PDF generation not implemented"
        elif format.lower() == 'json':
            export_result["data"] = enhanced_data
            export_result["status"] = "success"
        elif format.lower() == 'markdown':
            export_result["data"] = self._convert_to_markdown(enhanced_data)
            export_result["status"] = "success"
        else:
            export_result["status"] = f"Unsupported format: {format}"
            
        return {
            "enhanced_creature": enhanced_data,
            "export_result": export_result
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
        # Create prompt for illustration
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
            
        prompt = self._create_prompt(
            "generate illustration prompt",
            context + "\n"
            "Create a detailed prompt for an AI image generator to create an illustration of this creature.\n"
            "The prompt should include:\n"
            "1. Detailed physical description and anatomy\n"
            "2. Color scheme and textures\n"
            "3. Pose and action\n"
            "4. Environmental elements and background\n"
            "5. Lighting and mood\n"
            "6. Artistic style specifications\n\n"
            "The prompt should be highly detailed but focus on the most visually distinctive elements.\n"
            "Format the prompt to be effective for image generation models like Stable Diffusion or Midjourney."
        )
        
        try:
            # Generate illustration prompt
            response = self.llm_service.generate(prompt)
            
            return {
                "success": True,
                "illustration_prompt": response.strip(),
                "style": style
            }
        except Exception as e:
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
            
        # Create prompt for tactics
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
            
        prompt = self._create_prompt(
            "suggest creature tactics",
            context + "\n"
            "Suggest realistic combat tactics for this creature based on its abilities and intelligence.\n"
            "Consider:\n"
            "1. Opening moves and initial approach\n"
            "2. Primary targets and priorities\n"
            "3. Effective use of abilities and attacks\n"
            "4. Environmental tactics and positioning\n"
            "5. Retreat conditions and self-preservation\n"
            "6. Group tactics if applicable\n\n"
            f"The tactics should reflect the creature's intelligence ({intelligence}) and instincts.\n"
            "Provide tactical suggestions that a DM could implement to make this creature challenging but fair."
        )
        
        try:
            # Generate tactical suggestions
            response = self.llm_service.generate(prompt)
            
            # Parse the tactics
            tactics = self._parse_tactics_response(response)
            
            return {
                "success": True,
                "tactics": tactics
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to suggest tactics: {str(e)}"
            }

    # Helper methods

    def _create_prompt(self, task: str, content: str) -> str:
        """Create a structured prompt for the LLM."""
        return f"Task: {task}\n\n{content}"
    
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
    
    def _generate_ecology_description(self, creature_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate ecological description for a creature."""
        # Create prompt for ecology description
        context = f"Creature: {creature_data.get('name', 'Unnamed creature')}\n"
        context += f"Type: {creature_data.get('type', 'unknown')}\n"
        context += f"Size: {creature_data.get('size', 'medium')}\n"
        
        # Include abilities or traits if available
        traits = creature_data.get("traits", [])
        if traits:
            context += "\nTraits:\n"
            for trait in traits[:3]:  # Limit to top 3 traits
                context += f"- {trait.get('name', 'Unnamed trait')}\n"
        
        prompt = self._create_prompt(
            "generate ecology description",
            context + "\n"
            "Create an ecological profile for this creature, including:\n"
            "1. Habitat and preferred environment\n"
            "2. Diet and hunting/feeding patterns\n"
            "3. Social structure and behaviors\n"
            "4. Reproduction and lifecycle\n"
            "5. Interactions with other species\n\n"
            "The description should be coherent with the creature's traits and abilities."
        )
        
        try:
            # Generate ecology description
            response = self.llm_service.generate(prompt)
            
            # Extract sections
            ecology = {
                "habitat": "",
                "diet": "",
                "social": "",
                "lifecycle": "",
                "interactions": "",
                "full_text": response
            }
            
            # Try to extract habitat
            habitat_match = re.search(r"(?:Habitat|Environment):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if habitat_match:
                ecology["habitat"] = habitat_match.group(1).strip()
                
            # Try to extract diet
            diet_match = re.search(r"(?:Diet|Feeding):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if diet_match:
                ecology["diet"] = diet_match.group(1).strip()
                
            # Try to extract social behavior
            social_match = re.search(r"(?:Social|Behavior):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if social_match:
                ecology["social"] = social_match.group(1).strip()
            
            return ecology
            
        except Exception as e:
            return {
                "error": f"Failed to generate ecology: {str(e)}",
                "full_text": ""
            }
    
    def _convert_to_markdown(self, creature_data: Dict[str, Any]) -> str:
        """Convert creature data to markdown format."""
        md = f"# {creature_data.get('name', 'Unnamed Creature')}\n\n"
        md += f"*{creature_data.get('size', 'Medium')} {creature_data.get('type', 'beast')}*\n\n"
        
        md += f"**Armor Class:** {creature_data.get('armor_class', 10)}\n"
        md += f"**Hit Points:** {creature_data.get('hit_points', 0)} ({creature_data.get('hit_dice', '1d8')})\n"
        md += f"**Speed:** {creature_data.get('speed', '30 ft.')}\n\n"
        
        # Ability scores if available
        ability_scores = creature_data.get("ability_scores", {})
        if ability_scores:
            md += "| STR | DEX | CON | INT | WIS | CHA |\n"
            md += "|-----|-----|-----|-----|-----|-----|\n"
            md += f"| {ability_scores.get('strength', 10)} | {ability_scores.get('dexterity', 10)} | "
            md += f"{ability_scores.get('constitution', 10)} | {ability_scores.get('intelligence', 10)} | "
            md += f"{ability_scores.get('wisdom', 10)} | {ability_scores.get('charisma', 10)} |\n\n"
        
        # Traits
        traits = creature_data.get("traits", [])
        if traits:
            md += "## Traits\n\n"
            for trait in traits:
                md += f"***{trait.get('name', 'Unnamed Trait')}.*** {trait.get('description', '')}\n\n"
        
        # Actions
        attacks = creature_data.get("attacks", [])
        if attacks:
            md += "## Actions\n\n"
            for attack in attacks:
                md += f"***{attack.get('name', 'Unnamed Attack')}.*** {attack.get('description', '')}\n\n"
        
        # Ecology if available
        if "ecology" in creature_data:
            ecology = creature_data["ecology"]
            md += "## Ecology\n\n"
            
            if "habitat" in ecology and ecology["habitat"]:
                md += f"**Habitat:** {ecology['habitat']}\n\n"
                
            if "diet" in ecology and ecology["diet"]:
                md += f"**Diet:** {ecology['diet']}\n\n"
                
            if "social" in ecology and ecology["social"]:
                md += f"**Social Behavior:** {ecology['social']}\n\n"
        
        return md

    # Parser methods for LLM responses
    
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
        
        # Try to determine overall balance rating
        if "underpowered" in response.lower():
            assessment["overall_balance"] = "underpowered"
        elif "overpowered" in response.lower():
            assessment["overall_balance"] = "overpowered"
        else:
            assessment["overall_balance"] = "balanced"
            
        # Extract issues and suggestions
        lines = response.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            lower_line = line.lower()
            
            if "issue" in lower_line or "problem" in lower_line or "concern" in lower_line:
                current_section = "issues"
                continue
            elif "suggest" in lower_line or "recommend" in lower_line or "adjustment" in lower_line:
                current_section = "suggestions"
                continue
                
            if current_section and line.startswith("-"):
                assessment[current_section].append(line[1:].strip())
            elif current_section and line[0].isdigit() and ". " in line:
                point = line.split(". ", 1)[1]
                assessment[current_section].append(point.strip())
            
        return assessment
    
    def _parse_tactical_analysis(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for tactical analysis."""
        analysis = {
            "difficulty_assessment": "unknown",
            "creature_advantages": [],
            "party_advantages": [],
            "tactical_suggestions": []
        }
        
        # Try to determine difficulty assessment
        if "easy" in response.lower():
            analysis["difficulty_assessment"] = "easy"
        elif "medium" in response.lower():
            analysis["difficulty_assessment"] = "medium"
        elif "hard" in response.lower():
            analysis["difficulty_assessment"] = "hard"
        elif "deadly" in response.lower():
            analysis["difficulty_assessment"] = "deadly"
            
        # Extract advantages and suggestions
        lines = response.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            lower_line = line.lower()
            
            if ("creature advantage" in lower_line or 
                "tactical advantage" in lower_line and "creature" in lower_line):
                current_section = "creature_advantages"
                continue
            elif "party advantage" in lower_line:
                current_section = "party_advantages"
                continue
            elif "tactic" in lower_line and ("suggest" in lower_line or "recommend" in lower_line):
                current_section = "tactical_suggestions"
                continue
                
            if current_section and (line.startswith("-") or (line[0].isdigit() and ". " in line)):
                # Clean up the bullet point or numbering
                point = line
                if line.startswith("-"):
                    point = line[1:].strip()
                elif line[0].isdigit() and ". " in line:
                    point = line.split(". ", 1)[1].strip()
                    
                analysis[current_section].append(point)
                
        return analysis
    
    def _parse_attack_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for thematic attacks."""
        attacks = []
        
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
        
        # Try to extract opening moves
        opening_match = re.search(r"(?:Opening|Initial|First)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if opening_match:
            tactics["opening_moves"] = opening_match.group(1).strip()
            
        # Try to extract targets
        targets_match = re.search(r"(?:Target|Priority)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if targets_match:
            tactics["priority_targets"] = targets_match.group(1).strip()
            
        # Try to extract ability usage
        ability_match = re.search(r"(?:Abilities|Special|Ability Usage)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if ability_match:
            tactics["ability_usage"] = ability_match.group(1).strip()
            
        # Try to extract positioning
        position_match = re.search(r"(?:Position|Environmental|Terrain)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if position_match:
            tactics["positioning"] = position_match.group(1).strip()
            
        # Try to extract retreat conditions
        retreat_match = re.search(r"(?:Retreat|Withdrawal|Flee)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if retreat_match:
            tactics["retreat_conditions"] = retreat_match.group(1).strip()
        
        return tactics