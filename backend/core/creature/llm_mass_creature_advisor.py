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

try:
    from backend.core.creature.llm_creature_advisor import LLMCreatureAdvisor
    from backend.core.ollama_service import OllamaService
except ImportError:
    # Fallback for development
    class LLMCreatureAdvisor:
        def __init__(self, llm_service=None, data_path=None): pass
    
    class OllamaService:
        def __init__(self): pass
        def generate(self, prompt): return "LLM service not available"


class LLMMassCreatureAdvisor:
    """
    Provides AI-powered assistance for creating groups of creatures to challenge an adventuring party.
    
    This class integrates with Language Learning Models (LLMs) to suggest appropriate
    combinations and quantities of creatures based on party composition, desired challenge level,
    and environmental context. It works alongside LLMCreatureAdvisor which focuses on 
    individual creature creation.
    """

    # XP thresholds by character level
    XP_THRESHOLDS = {
        # level: [easy, medium, hard, deadly]
        1: [25, 50, 75, 100],
        2: [50, 100, 150, 200],
        3: [75, 150, 225, 400],
        4: [125, 250, 375, 500],
        5: [250, 500, 750, 1100],
        6: [300, 600, 900, 1400],
        7: [350, 750, 1100, 1700],
        8: [450, 900, 1400, 2100],
        9: [550, 1100, 1600, 2400],
        10: [600, 1200, 1900, 2800],
        11: [800, 1600, 2400, 3600],
        12: [1000, 2000, 3000, 4500],
        13: [1100, 2200, 3400, 5100],
        14: [1250, 2500, 3800, 5700],
        15: [1400, 2800, 4300, 6400],
        16: [1600, 3200, 4800, 7200],
        17: [2000, 3900, 5900, 8800],
        18: [2100, 4200, 6300, 9500],
        19: [2400, 4900, 7300, 10900],
        20: [2800, 5700, 8500, 12700]
    }

    # Encounter multipliers based on number of monsters
    ENCOUNTER_MULTIPLIERS = {
        1: 1.0,
        2: 1.5,
        3: 2.0,
        4: 2.0,
        5: 2.0,
        6: 2.0,
        7: 2.5,
        8: 2.5,
        9: 2.5,
        10: 2.5,
        11: 3.0,
        12: 3.0,
        13: 3.0,
        14: 3.0,
        15: 4.0
    }

    def __init__(self, llm_service=None, data_path: str = None, creature_advisor=None):
        """
        Initialize the LLM mass creature advisor.
        
        Args:
            llm_service: LLM service client for generating responses
            data_path: Optional path to creature data
            creature_advisor: Optional LLMCreatureAdvisor instance for individual creature creation
        """
        # Initialize LLM service
        self.llm_service = llm_service or OllamaService()
            
        # Set up paths and data
        self.data_path = Path(data_path) if data_path else Path("backend/data/creatures")
        self.creature_advisor = creature_advisor or LLMCreatureAdvisor(llm_service, data_path)
        self._load_reference_data()

    def _load_reference_data(self):
        """Load reference data for encounter creation."""
        try:
            # Load CR calculation reference
            cr_path = self.data_path / "challenge_ratings.json"
            if cr_path.exists():
                with open(cr_path, "r") as f:
                    self.cr_data = json.load(f)
            else:
                self.cr_data = {}
                
            # Load monster reference data
            monster_path = self.data_path / "monster_manual.json"
            if monster_path.exists():
                with open(monster_path, "r") as f:
                    self.monster_data = json.load(f)
            else:
                self.monster_data = {}
                
            # Load environment data
            env_path = self.data_path / "environments.json"
            if env_path.exists():
                with open(env_path, "r") as f:
                    self.environment_data = json.load(f)
            else:
                self.environment_data = {}
                
        except Exception as e:
            print(f"Error loading reference data: {e}")
            self.cr_data = {}
            self.monster_data = {}
            self.environment_data = {}

    def suggest_encounter(self, party_composition: List[Dict[str, Any]], 
                       difficulty: str = "medium",
                       environment: str = None,
                       theme: str = None) -> Dict[str, Any]:
        """
        Generate a balanced encounter for a party based on composition and difficulty.
        
        Args:
            party_composition: List of party member dictionaries with keys 'level' and 'class'
            difficulty: Desired difficulty level ('easy', 'medium', 'hard', 'deadly')
            environment: Optional environment context
            theme: Optional thematic focus
            
        Returns:
            Dict[str, Any]: Suggested encounter data
        """
        # Calculate party level and XP thresholds
        party_size = len(party_composition)
        party_levels = [member.get("level", 1) for member in party_composition]
        avg_level = sum(party_levels) / len(party_levels)
        xp_threshold = self._calculate_xp_threshold(party_levels, difficulty)
        
        # Adjust for party size
        if party_size < 3:
            xp_threshold = int(xp_threshold * 1.5)
        elif party_size > 5:
            xp_threshold = int(xp_threshold * 0.8)
            
        # Build context for LLM
        context = f"Party Composition:\n"
        for i, member in enumerate(party_composition, 1):
            context += f"- Player {i}: Level {member.get('level', 1)} {member.get('class', 'Fighter')}"
            if "race" in member:
                context += f" ({member['race']})"
            if "key_features" in member:
                context += f", Features: {', '.join(member['key_features'][:3])}"
            context += "\n"
            
        context += f"\nDifficulty: {difficulty.capitalize()}\n"
        context += f"Appropriate XP Budget: {xp_threshold} XP\n"
        
        if environment:
            context += f"Environment: {environment}\n"
            
        if theme:
            context += f"Theme: {theme}\n"
            
        # Create prompt for encounter generation
        prompt = self._create_prompt(
            "generate balanced encounter",
            context + "\n"
            "Create a balanced and thematic encounter for this party with the following information:\n"
            "1. Suggest 2-3 different encounter options with different tactical approaches\n"
            "2. For each encounter, list the specific creatures and quantities\n"
            "3. Include CR and XP values for each creature\n"
            "4. Describe the initial placement and tactics for the encounter\n"
            "5. Explain how this encounter will challenge the specific party composition\n"
            "6. Suggest adjustments that could make the encounter easier or harder\n\n"
            "Focus on creating an engaging and appropriate challenge that tests the party's capabilities."
        )
        
        try:
            # Generate encounter suggestions with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured encounter data
            encounter_options = self._parse_encounter_response(response)
            
            # Validate encounter options against XP budget
            validated_options = self._validate_encounter_options(encounter_options, xp_threshold)
            
            return {
                "success": True,
                "encounter_options": validated_options,
                "party_info": {
                    "size": party_size,
                    "average_level": round(avg_level, 1),
                    "xp_threshold": xp_threshold,
                    "difficulty": difficulty
                },
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate encounter options: {str(e)}"
            }

    def generate_encounter_sequence(self, party_composition: List[Dict[str, Any]],
                                 campaign_segment: str,
                                 num_encounters: int = 3,
                                 environment: str = None) -> Dict[str, Any]:
        """
        Generate a sequence of encounters for an adventure segment or dungeon.
        
        Args:
            party_composition: List of party member dictionaries with keys 'level' and 'class'
            campaign_segment: Description of adventure segment or dungeon section
            num_encounters: Number of encounters to generate
            environment: Optional primary environment
            
        Returns:
            Dict[str, Any]: Sequence of connected encounters
        """
        # Calculate party level ranges
        party_levels = [member.get("level", 1) for member in party_composition]
        avg_level = sum(party_levels) / len(party_levels)
        
        # Build context for LLM
        context = f"Party Composition: {len(party_composition)} characters with average level {avg_level:.1f}\n"
        context += f"Campaign Segment: {campaign_segment}\n"
        context += f"Number of Encounters: {num_encounters}\n"
        
        if environment:
            context += f"Primary Environment: {environment}\n"
            
        # Include class distribution
        class_counts = {}
        for member in party_composition:
            char_class = member.get("class", "Fighter")
            class_counts[char_class] = class_counts.get(char_class, 0) + 1
            
        context += "Party Classes: "
        context += ", ".join([f"{count} {cls}" for cls, count in class_counts.items()])
        context += "\n"
        
        # Create prompt for encounter sequence generation
        prompt = self._create_prompt(
            "generate encounter sequence",
            context + "\n"
            f"Create a sequence of {num_encounters} connected encounters that form a cohesive adventure segment.\n"
            "For each encounter:\n"
            "1. Describe the setting, context, and connection to the overall segment\n"
            "2. Provide a specific mix of creatures with quantities and CRs\n"
            "3. Include a rough difficulty assessment (easy, medium, hard, or deadly)\n"
            "4. Suggest tactical dynamics and interesting terrain or environmental factors\n"
            "5. Explain how this encounter fits into the narrative progression\n\n"
            "Structure the sequence with a narrative flow and escalating challenge, with the following pattern:\n"
            "- Initial encounters: Establish theme and introduce core threats\n"
            "- Middle encounters: Develop complexity and increase challenge\n"
            "- Final encounter: Climactic challenge that tests the party's resources\n\n"
            "Consider resource depletion across the sequence and provide suggestions for rest points if appropriate."
        )
        
        try:
            # Generate encounter sequence with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured sequence data
            encounter_sequence = self._parse_encounter_sequence(response, num_encounters)
            
            # Calculate XP values and validate sequence
            validated_sequence = self._validate_encounter_sequence(encounter_sequence, party_levels)
            
            return {
                "success": True,
                "encounter_sequence": validated_sequence,
                "campaign_segment": campaign_segment,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate encounter sequence: {str(e)}"
            }

    def suggest_creatures_for_party(self, party_composition: List[Dict[str, Any]],
                                 target_ability: str = None,
                                 challenge_level: str = "balanced") -> Dict[str, Any]:
        """
        Suggest creatures that specifically challenge certain party compositions or abilities.
        
        Args:
            party_composition: List of party member dictionaries with keys 'level' and 'class'
            target_ability: Optional specific ability to target (e.g., "spellcasting", "stealth")
            challenge_level: How challenging to make it ("easy", "balanced", "hard")
            
        Returns:
            Dict[str, Any]: Suggested creatures with targeting rationale
        """
        # Analyze party composition
        party_levels = [member.get("level", 1) for member in party_composition]
        avg_level = sum(party_levels) / len(party_levels)
        party_classes = [member.get("class", "Fighter") for member in party_composition]
        
        # Determine appropriate CR range based on party level and challenge level
        cr_min = max(1/8, avg_level / 4)
        cr_max = avg_level * 1.5
        
        if challenge_level == "easy":
            cr_max = avg_level * 0.75
        elif challenge_level == "hard":
            cr_min = avg_level / 2
            cr_max = avg_level * 2
            
        # Build context for LLM
        context = f"Party Composition: {len(party_composition)} characters with average level {avg_level:.1f}\n"
        context += f"Party Classes: {', '.join(party_classes)}\n"
        context += f"Challenge Level: {challenge_level}\n"
        context += f"Appropriate CR Range: {cr_min:.1f} to {cr_max:.1f}\n"
        
        if target_ability:
            context += f"Target Ability: {target_ability}\n"
        
        # Create prompt for targeted creature suggestions
        prompt = self._create_prompt(
            "suggest targeted creatures",
            context + "\n"
            "Recommend creatures that would specifically challenge this party's composition and abilities.\n"
            "For your recommendations, consider:\n"
            "1. Creatures that exploit weaknesses in the party lineup\n"
            "2. Creatures that can counter or resist common abilities of these classes\n"
            "3. Creatures that force the party to use alternative strategies\n\n"
            "For each suggested creature or creature group:\n"
            "- Provide name, CR, and brief description\n"
            "- Explain specifically how it challenges this party composition\n"
            "- Suggest effective quantities and combinations\n"
            "- Describe why it provides an interesting tactical challenge\n\n"
            "Focus on creating meaningful challenges rather than frustrating counters, and provide a mix of different creature types."
        )
        
        try:
            # Generate targeted creature suggestions with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured creature suggestions
            creature_suggestions = self._parse_creature_suggestions(response)
            
            return {
                "success": True,
                "targeted_suggestions": creature_suggestions,
                "party_analysis": {
                    "average_level": round(avg_level, 1),
                    "class_composition": party_classes,
                    "targeted_ability": target_ability,
                    "challenge_level": challenge_level
                },
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate targeted creature suggestions: {str(e)}"
            }

    def create_thematic_creature_groups(self, environment: str, theme: str,
                                      cr_range: Tuple[float, float] = None,
                                      group_size: int = 3) -> Dict[str, Any]:
        """
        Create thematically connected groups of creatures for an environment.
        
        Args:
            environment: Primary environment
            theme: Thematic focus for the creatures
            cr_range: Optional tuple of (min_cr, max_cr)
            group_size: Number of creature types to include in each group
            
        Returns:
            Dict[str, Any]: Thematic creature groups
        """
        # Default CR range if not specified
        if cr_range is None:
            cr_range = (1/4, 10)
            
        cr_min, cr_max = cr_range
        
        # Build context for LLM
        context = f"Environment: {environment}\n"
        context += f"Theme: {theme}\n"
        context += f"CR Range: {cr_min} to {cr_max}\n"
        context += f"Creatures Per Group: {group_size}\n"
        
        # Create prompt for thematic creature groups
        prompt = self._create_prompt(
            "create thematic creature groups",
            context + "\n"
            f"Create 3 different thematic groups of creatures that would exist together in a {environment} with a {theme} theme.\n"
            f"Each group should contain {group_size} different creature types that make sense together ecologically or organizationally.\n"
            "For each group:\n"
            "1. Provide an overall concept or relationship that connects them\n"
            "2. List each creature with name, CR, and brief description\n"
            "3. Explain how these creatures would interact or work together\n"
            "4. Describe how they fit into the environment and theme\n"
            "5. Suggest appropriate quantities for an encounter\n\n"
            "Focus on interesting combinations that make narrative and ecological sense. Include a mix of CRs within the specified range."
        )
        
        try:
            # Generate thematic creature groups with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured creature groups
            creature_groups = self._parse_thematic_groups(response)
            
            return {
                "success": True,
                "thematic_groups": creature_groups,
                "environment": environment,
                "theme": theme,
                "cr_range": cr_range,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create thematic creature groups: {str(e)}"
            }

    def balance_mixed_encounter(self, creature_selections: List[Dict[str, Any]],
                             party_levels: List[int],
                             target_difficulty: str = "medium") -> Dict[str, Any]:
        """
        Balance a mixed encounter by adjusting creature quantities to reach a target difficulty.
        
        Args:
            creature_selections: List of creatures with 'name', 'cr', and 'quantity'
            party_levels: List of party member levels
            target_difficulty: Target difficulty ('easy', 'medium', 'hard', 'deadly')
            
        Returns:
            Dict[str, Any]: Balanced encounter with adjusted quantities
        """
        # Calculate target XP threshold
        target_xp = self._calculate_xp_threshold(party_levels, target_difficulty)
        
        # Calculate current encounter XP
        current_xp = 0
        for creature in creature_selections:
            cr = creature.get("cr", 0)
            quantity = creature.get("quantity", 1)
            xp = self._get_xp_by_cr(cr) * quantity
            current_xp += xp
            
        # Apply multiplier based on total number of creatures
        total_creatures = sum(creature.get("quantity", 1) for creature in creature_selections)
        multiplier = self._get_encounter_multiplier(total_creatures)
        adjusted_current_xp = current_xp * multiplier
        
        # Check if already within 10% of target
        if abs(adjusted_current_xp - target_xp) / target_xp < 0.1:
            balance_result = {
                "status": "already_balanced",
                "original_encounter": creature_selections.copy(),
                "balanced_encounter": creature_selections,
                "original_xp": adjusted_current_xp,
                "target_xp": target_xp
            }
        else:
            # Try to balance by adjusting quantities
            balanced_creatures = self._adjust_creature_quantities(
                creature_selections, target_xp
            )
            
            # Calculate new XP
            new_xp = 0
            for creature in balanced_creatures:
                cr = creature.get("cr", 0)
                quantity = creature.get("quantity", 1)
                xp = self._get_xp_by_cr(cr) * quantity
                new_xp += xp
                
            # Apply multiplier for new total
            new_total_creatures = sum(creature.get("quantity", 1) for creature in balanced_creatures)
            new_multiplier = self._get_encounter_multiplier(new_total_creatures)
            adjusted_new_xp = new_xp * new_multiplier
            
            balance_result = {
                "status": "adjusted",
                "original_encounter": creature_selections,
                "balanced_encounter": balanced_creatures,
                "original_xp": adjusted_current_xp,
                "adjusted_xp": adjusted_new_xp,
                "target_xp": target_xp
            }
            
        # If still too far from target, suggest additional creatures
        if abs(balance_result.get("adjusted_xp", adjusted_current_xp) - target_xp) / target_xp > 0.2:
            # Get average CR of current creatures
            avg_cr = sum(creature.get("cr", 0) for creature in creature_selections) / len(creature_selections)
            
            # Build context for LLM
            context = f"Current Encounter: {', '.join([f'{c.get('quantity', 1)}x {c.get('name', 'Unknown')} (CR {c.get('cr', 0)})' for c in creature_selections])}\n"
            context += f"Current Adjusted XP: {balance_result.get('adjusted_xp', adjusted_current_xp)}\n"
            context += f"Target XP: {target_xp}\n"
            context += f"Target Difficulty: {target_difficulty}\n"
            context += f"Party Levels: {', '.join(map(str, party_levels))}\n"
            context += f"Average CR: {avg_cr:.1f}\n"
            
            # Create prompt for encounter balancing
            prompt = self._create_prompt(
                "suggest encounter balance adjustments",
                context + "\n"
                "The current encounter is not properly balanced for the target difficulty.\n"
                "Suggest specific adjustments to reach the target XP threshold while maintaining a coherent encounter:\n"
                "1. Recommend creatures to add or remove with specific quantities\n"
                "2. Consider what creatures would make thematic sense with the existing selection\n"
                "3. Prefer adjusting quantities over completely replacing creatures\n"
                "4. Aim to reach within 10% of the target XP value\n\n"
                "For each adjustment, provide a brief tactical rationale."
            )
            
            try:
                # Generate balance suggestions with LLM
                response = self.llm_service.generate(prompt)
                
                # Include suggestions in the result
                balance_result["llm_suggestions"] = response
                balance_result["has_suggestions"] = True
                
            except Exception as e:
                balance_result["suggestion_error"] = str(e)
                balance_result["has_suggestions"] = False
                
        return balance_result

    def suggest_reinforcement_waves(self, initial_encounter: List[Dict[str, Any]],
                                 party_levels: List[int],
                                 num_waves: int = 2) -> Dict[str, Any]:
        """
        Suggest reinforcement waves to extend an encounter dynamically.
        
        Args:
            initial_encounter: List of initial creatures with 'name', 'cr', and 'quantity'
            party_levels: List of party member levels
            num_waves: Number of reinforcement waves to generate
            
        Returns:
            Dict[str, Any]: Suggested reinforcement waves
        """
        # Calculate initial encounter XP
        initial_xp = 0
        for creature in initial_encounter:
            cr = creature.get("cr", 0)
            quantity = creature.get("quantity", 1)
            xp = self._get_xp_by_cr(cr) * quantity
            initial_xp += xp
            
        # Apply multiplier based on total number of creatures
        total_initial_creatures = sum(creature.get("quantity", 1) for creature in initial_encounter)
        initial_multiplier = self._get_encounter_multiplier(total_initial_creatures)
        adjusted_initial_xp = initial_xp * initial_multiplier
        
        # Calculate average party level
        avg_level = sum(party_levels) / len(party_levels)
        
        # Build context for LLM
        context = f"Initial Encounter: {', '.join([f'{c.get('quantity', 1)}x {c.get('name', 'Unknown')} (CR {c.get('cr', 0)})' for c in initial_encounter])}\n"
        context += f"Initial Encounter XP: {adjusted_initial_xp}\n"
        context += f"Party Size: {len(party_levels)}\n"
        context += f"Average Party Level: {avg_level:.1f}\n"
        context += f"Number of Reinforcement Waves: {num_waves}\n"
        
        # Extract creature types for thematic consistency
        creature_types = list(set([creature.get("type", "unknown") for creature in initial_encounter if "type" in creature]))
        if creature_types:
            context += f"Initial Creature Types: {', '.join(creature_types)}\n"
            
        # Create prompt for reinforcement waves
        prompt = self._create_prompt(
            "generate reinforcement waves",
            context + "\n"
            f"Design {num_waves} waves of reinforcements that could join this encounter to create a dynamic and escalating challenge.\n"
            "For each wave:\n"
            "1. Specify the creatures and quantities that arrive\n"
            "2. Suggest a trigger or condition for when this wave appears\n"
            "3. Describe tactical changes and positioning for the new creatures\n"
            "4. Explain how this wave escalates the challenge or changes the encounter dynamics\n\n"
            "Consider appropriate pacing and challenge escalation, with each wave building upon the tactical situation.\n"
            "Ensure the reinforcements are thematically consistent with the initial encounter."
        )
        
        try:
            # Generate reinforcement waves with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured wave data
            reinforcement_waves = self._parse_reinforcement_waves(response)
            
            # Calculate XP for each wave and total
            wave_xp_values = []
            for wave in reinforcement_waves:
                wave_xp = 0
                for creature in wave.get("creatures", []):
                    cr = creature.get("cr", 0)
                    quantity = creature.get("quantity", 1)
                    xp = self._get_xp_by_cr(cr) * quantity
                    wave_xp += xp
                
                # Apply wave multiplier
                total_wave_creatures = sum(creature.get("quantity", 1) for creature in wave.get("creatures", []))
                wave_multiplier = self._get_encounter_multiplier(total_wave_creatures)
                adjusted_wave_xp = wave_xp * wave_multiplier
                
                wave["xp_value"] = adjusted_wave_xp
                wave_xp_values.append(adjusted_wave_xp)
            
            return {
                "success": True,
                "initial_encounter": initial_encounter,
                "initial_xp": adjusted_initial_xp,
                "reinforcement_waves": reinforcement_waves,
                "wave_xp_values": wave_xp_values,
                "total_potential_xp": adjusted_initial_xp + sum(wave_xp_values),
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate reinforcement waves: {str(e)}"
            }

    def adapt_creatures_to_environment(self, creature_list: List[Dict[str, Any]], 
                                    environment: str) -> Dict[str, Any]:
        """
        Adapt a list of creature selections to better fit a specific environment.
        
        Args:
            creature_list: List of creatures with 'name', 'cr', and optionally 'quantity'
            environment: Target environment
            
        Returns:
            Dict[str, Any]: Environmentally adapted creatures
        """
        # Build context for LLM
        context = f"Creatures:\n"
        for creature in creature_list:
            name = creature.get("name", "Unknown Creature")
            cr = creature.get("cr", "?")
            quantity = creature.get("quantity", 1)
            context += f"- {quantity}x {name} (CR {cr})\n"
            
        context += f"\nTarget Environment: {environment}\n"
        
        # Create prompt for environmental adaptation
        prompt = self._create_prompt(
            "adapt creatures to environment",
            context + "\n"
            f"Adapt these creatures to better fit a {environment} environment without changing their core identity or CR.\n"
            "For each creature:\n"
            "1. Suggest environmental variants or adaptations\n"
            "2. Propose adjustments to appearance, tactics, or minor abilities\n"
            "3. Explain how these adaptations help them thrive in this environment\n"
            "4. Suggest any terrain features or lair actions that would enhance the encounter\n\n"
            "Focus on believable adaptations that enhance the narrative and tactical interest while maintaining game balance."
        )
        
        try:
            # Generate environmental adaptations with LLM
            response = self.llm_service.generate(prompt)
            
            # Create structured adaptation data
            adapted_creatures = []
            for i, creature in enumerate(creature_list):
                # Try to find adaptation for this creature in the response
                creature_name = creature.get("name", "").lower()
                adaptation_pattern = re.compile(
                    rf"(?:(?:\d+\.|\*|\-)\s*)?{re.escape(creature_name)}.*?(?:\n\n|\Z)",
                    re.IGNORECASE | re.DOTALL
                )
                
                match = adaptation_pattern.search(response)
                adaptation_text = match.group(0).strip() if match else ""
                
                adapted_creature = creature.copy()
                adapted_creature["environmental_adaptation"] = adaptation_text
                adapted_creatures.append(adapted_creature)
                
            return {
                "success": True,
                "original_creatures": creature_list,
                "adapted_creatures": adapted_creatures,
                "environment": environment,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to adapt creatures to environment: {str(e)}",
                "original_creatures": creature_list
            }

    def generate_encounter_variations(self, base_encounter: List[Dict[str, Any]],
                                   party_levels: List[int],
                                   variation_focus: str = "tactical") -> Dict[str, Any]:
        """
        Generate tactical variations of a base encounter.
        
        Args:
            base_encounter: List of base creatures with 'name', 'cr', and 'quantity'
            party_levels: List of party member levels
            variation_focus: Focus of variations ('tactical', 'thematic', 'difficulty')
            
        Returns:
            Dict[str, Any]: Encounter variations
        """
        # Calculate base encounter XP
        base_xp = 0
        for creature in base_encounter:
            cr = creature.get("cr", 0)
            quantity = creature.get("quantity", 1)
            xp = self._get_xp_by_cr(cr) * quantity
            base_xp += xp
            
        # Apply multiplier based on total number of creatures
        total_creatures = sum(creature.get("quantity", 1) for creature in base_encounter)
        multiplier = self._get_encounter_multiplier(total_creatures)
        adjusted_base_xp = base_xp * multiplier
        
        # Calculate average party level
        avg_level = sum(party_levels) / len(party_levels)
        
        # Build context for LLM
        context = f"Base Encounter: {', '.join([f'{c.get('quantity', 1)}x {c.get('name', 'Unknown')} (CR {c.get('cr', 0)})' for c in base_encounter])}\n"
        context += f"Base Encounter XP: {adjusted_base_xp}\n"
        context += f"Average Party Level: {avg_level:.1f}\n"
        context += f"Variation Focus: {variation_focus}\n"
        
        # Create prompt for encounter variations
        prompt = self._create_prompt(
            "generate encounter variations",
            context + "\n"
            "Create 3 distinct variations of this base encounter that maintain approximate challenge level but change the tactical experience.\n"
            "For each variation:\n"
            "1. Provide a name and brief concept\n"
            "2. List specific creatures and quantities (can include some from the base encounter)\n"
            "3. Describe the tactical dynamics and how they differ from the base encounter\n"
            "4. Explain how this variation changes the challenge for the party\n\n"
            f"Focus on {variation_focus} variations that create meaningfully different combat experiences while staying within 20% of the original XP value."
        )
        
        try:
            # Generate encounter variations with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured variation data
            encounter_variations = self._parse_encounter_variations(response)
            
            return {
                "success": True,
                "base_encounter": base_encounter,
                "base_xp": adjusted_base_xp,
                "encounter_variations": encounter_variations,
                "variation_focus": variation_focus,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate encounter variations: {str(e)}"
            }

    # Helper methods

    def _create_prompt(self, task: str, content: str) -> str:
        """Create a structured prompt for the LLM."""
        return f"Task: {task}\n\n{content}"
    
    def _calculate_xp_threshold(self, party_levels: List[int], difficulty: str) -> int:
        """Calculate XP threshold for a party at given difficulty."""
        difficulties = ["easy", "medium", "hard", "deadly"]
        if difficulty.lower() not in difficulties:
            difficulty = "medium"
            
        difficulty_index = difficulties.index(difficulty.lower())
        
        total_xp = 0
        for level in party_levels:
            # Cap at level 20
            capped_level = min(level, 20)
            total_xp += self.XP_THRESHOLDS.get(capped_level, [0, 0, 0, 0])[difficulty_index]
            
        return total_xp
        
    def _get_xp_by_cr(self, cr: Union[float, str]) -> int:
        """Get XP value for a given CR."""
        # Handle fractional CRs as strings
        if isinstance(cr, str) and "/" in cr:
            num, den = cr.split("/")
            cr = float(num) / float(den)
            
        # Convert to float if not already
        cr_float = float(cr)
        
        # Standard XP values by CR
        xp_by_cr = {
            0: 10,
            1/8: 25,
            1/4: 50,
            1/2: 100,
            1: 200,
            2: 450,
            3: 700,
            4: 1100,
            5: 1800,
            6: 2300,
            7: 2900,
            8: 3900,
            9: 5000,
            10: 5900,
            11: 7200,
            12: 8400,
            13: 10000,
            14: 11500,
            15: 13000,
            16: 15000,
            17: 18000,
            18: 20000,
            19: 22000,
            20: 25000,
            21: 33000,
            22: 41000,
            23: 50000,
            24: 62000,
            25: 75000,
            26: 90000,
            27: 105000,
            28: 120000,
            29: 135000,
            30: 155000
        }
        
        # Return exact match if exists
        if cr_float in xp_by_cr:
            return xp_by_cr[cr_float]
            
        # Find closest lower CR
        closest_lower_cr = max([c for c in xp_by_cr.keys() if c <= cr_float])
        return xp_by_cr[closest_lower_cr]
        
    def _get_encounter_multiplier(self, num_monsters: int) -> float:
        """Get encounter multiplier based on number of monsters."""
        if num_monsters <= 1:
            return 1.0
        elif num_monsters >= 15:
            return 4.0
        else:
            return self.ENCOUNTER_MULTIPLIERS.get(num_monsters, 4.0)
            
    def _adjust_creature_quantities(self, creatures: List[Dict[str, Any]], target_xp: int) -> List[Dict[str, Any]]:
        """Adjust creature quantities to approach target XP."""
        # Create a copy to modify
        adjusted_creatures = [creature.copy() for creature in creatures]
        
        # Calculate base XP per creature
        xp_per_creature = []
        for creature in adjusted_creatures:
            cr = creature.get("cr", 0)
            xp = self._get_xp_by_cr(cr)
            xp_per_creature.append(xp)
            
        # Try simple iterative adjustment - increase or decrease quantities
        best_adjusted = adjusted_creatures.copy()
        best_diff = float('inf')
        
        # Try up to 10 iterations to improve the balance
        for _ in range(10):
            # Calculate current XP
            current_xp = 0
            for i, creature in enumerate(adjusted_creatures):
                quantity = creature.get("quantity", 1)
                current_xp += xp_per_creature[i] * quantity
                
            # Apply multiplier
            total_creatures = sum(creature.get("quantity", 1) for creature in adjusted_creatures)
            multiplier = self._get_encounter_multiplier(total_creatures)
            adjusted_current_xp = current_xp * multiplier
            
            # Check if this is the best so far
            diff = abs(adjusted_current_xp - target_xp)
            if diff < best_diff:
                best_diff = diff
                best_adjusted = [creature.copy() for creature in adjusted_creatures]
                
            # Stop if within 10% of target
            if diff / target_xp < 0.1:
                break
                
            # Determine if we need to increase or decrease
            if adjusted_current_xp < target_xp:
                # Need more creatures - find lowest XP impact creature
                min_xp_idx = xp_per_creature.index(min(xp_per_creature))
                adjusted_creatures[min_xp_idx]["quantity"] = adjusted_creatures[min_xp_idx].get("quantity", 1) + 1
            else:
                # Need fewer creatures - find highest XP impact creature
                max_xp_idx = xp_per_creature.index(max(xp_per_creature))
                if adjusted_creatures[max_xp_idx].get("quantity", 1) > 1:
                    adjusted_creatures[max_xp_idx]["quantity"] = adjusted_creatures[max_xp_idx].get("quantity", 1) - 1
                
        return best_adjusted
        
    def _parse_encounter_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for encounter generation."""
        encounter_options = []
        
        # Look for encounter blocks
        encounter_blocks = re.findall(r"(?:Encounter|Option)(?:\s+\d+)?:([^\n]+(?:\n(?!Encounter|Option\s+\d+:)[^\n]+)*)", response, re.IGNORECASE)
        
        if not encounter_blocks:
            # Try alternative pattern
            encounter_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", response)
            
        for i, block in enumerate(encounter_blocks):
            encounter = {
                "id": i + 1,
                "name": f"Encounter Option {i + 1}",
                "creatures": [],
                "tactics": "",
                "adjustments": ""
            }
            
            # Try to extract encounter name
            name_match = re.search(r"^([^\n:]+)", block)
            if name_match:
                encounter["name"] = name_match.group(1).strip()
                
            # Try to find creatures
            creature_pattern = re.compile(r"(?:[-•*]\s*|^\d+[\.x]\s*)(\d+)?(?:\s*[x×]\s*)?([^(,]+)(?:\s*\((?:CR\s*)?([^)]+)\))?", re.MULTILINE)
            creature_matches = creature_pattern.findall(block)
            
            for match in creature_matches:
                quantity_str, name, cr_str = match
                quantity = int(quantity_str) if quantity_str else 1
                creature = {
                    "name": name.strip(),
                    "quantity": quantity
                }
                
                # Try to parse CR
                if cr_str:
                    try:
                        cr_cleaned = cr_str.strip().lower()
                        if cr_cleaned in ["1/8", "1/4", "1/2"]:
                            creature["cr"] = eval(cr_cleaned)
                        else:
                            creature["cr"] = float(cr_cleaned)
                    except:
                        creature["cr"] = 0
                        
                encounter["creatures"].append(creature)
                
            # Try to extract tactics
            tactics_match = re.search(r"(?:Tactics|Approach|Strategy)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if tactics_match:
                encounter["tactics"] = tactics_match.group(1).strip()
                
            # Try to extract adjustments
            adjust_match = re.search(r"(?:Adjust|Scaling|Difficulty)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if adjust_match:
                encounter["adjustments"] = adjust_match.group(1).strip()
                
            encounter_options.append(encounter)
            
        return encounter_options
        
    def _validate_encounter_options(self, encounter_options: List[Dict[str, Any]], target_xp: int) -> List[Dict[str, Any]]:
        """Validate encounter options and calculate XP values."""
        validated_options = []
        
        for option in encounter_options:
            # Calculate XP for this encounter option
            total_xp = 0
            for creature in option.get("creatures", []):
                cr = creature.get("cr", 0)
                quantity = creature.get("quantity", 1)
                xp = self._get_xp_by_cr(cr) * quantity
                creature["xp"] = xp
                total_xp += xp
                
            # Apply encounter multiplier
            total_creatures = sum(creature.get("quantity", 1) for creature in option.get("creatures", []))
            multiplier = self._get_encounter_multiplier(total_creatures)
            adjusted_xp = total_xp * multiplier
            
            # Add XP data
            validated_option = option.copy()
            validated_option["total_xp"] = total_xp
            validated_option["adjusted_xp"] = adjusted_xp
            validated_option["xp_multiplier"] = multiplier
            
            # Check against target
            if target_xp > 0:
                xp_ratio = adjusted_xp / target_xp
                if xp_ratio < 0.8:
                    validated_option["difficulty_assessment"] = "easier than requested"
                elif xp_ratio > 1.2:
                    validated_option["difficulty_assessment"] = "harder than requested"
                else:
                    validated_option["difficulty_assessment"] = "appropriate difficulty"
                    
                validated_option["xp_ratio"] = xp_ratio
                
            validated_options.append(validated_option)
            
        return validated_options
        
    def _parse_encounter_sequence(self, response: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse LLM response for encounter sequence."""
        encounter_sequence = []
        
        # Try to split into numbered encounters
        encounter_blocks = re.findall(r"(?:Encounter|Sequence)(?:\s+\d+)?:([^\n]+(?:\n(?!Encounter|Sequence\s+\d+:)[^\n]+)*)", response, re.IGNORECASE)
        
        if len(encounter_blocks) < expected_count:
            # Try alternative pattern with numbered list
            encounter_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", response)
            
        # If still not enough, try to split the text more generally
        if len(encounter_blocks) < expected_count:
            paragraphs = re.split(r'\n\s*\n', response)
            encounter_blocks = paragraphs[:expected_count]
            
        for i, block in enumerate(encounter_blocks):
            if i >= expected_count:
                break
                
            encounter = {
                "id": i + 1,
                "name": f"Encounter {i + 1}",
                "description": block.strip(),
                "creatures": [],
                "setting": "",
                "difficulty": "medium"
            }
            
            # Try to extract encounter name
            name_match = re.search(r"^([^\n:]+)", block)
            if name_match:
                encounter["name"] = name_match.group(1).strip()
                
            # Try to find creatures
            creature_pattern = re.compile(r"(?:[-•*]\s*|^\d+[\.x]\s*)(\d+)?(?:\s*[x×]\s*)?([^(,]+)(?:\s*\((?:CR\s*)?([^)]+)\))?", re.MULTILINE)
            creature_matches = creature_pattern.findall(block)
            
            for match in creature_matches:
                quantity_str, name, cr_str = match
                quantity = int(quantity_str) if quantity_str else 1
                creature = {
                    "name": name.strip(),
                    "quantity": quantity
                }
                
                # Try to parse CR
                if cr_str:
                    try:
                        cr_cleaned = cr_str.strip().lower()
                        if cr_cleaned in ["1/8", "1/4", "1/2"]:
                            creature["cr"] = eval(cr_cleaned)
                        else:
                            creature["cr"] = float(cr_cleaned)
                    except:
                        creature["cr"] = 0
                        
                encounter["creatures"].append(creature)
                
            # Try to extract setting
            setting_match = re.search(r"(?:Setting|Location|Scene)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if setting_match:
                encounter["setting"] = setting_match.group(1).strip()
                
            # Try to extract difficulty
            difficulty_match = re.search(r"(?:Difficulty|Challenge)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if difficulty_match:
                difficulty_text = difficulty_match.group(1).lower()
                if "easy" in difficulty_text:
                    encounter["difficulty"] = "easy"
                elif "hard" in difficulty_text:
                    encounter["difficulty"] = "hard"
                elif "deadly" in difficulty_text:
                    encounter["difficulty"] = "deadly"
                    
            encounter_sequence.append(encounter)
            
        return encounter_sequence
        
    def _validate_encounter_sequence(self, encounter_sequence: List[Dict[str, Any]], party_levels: List[int]) -> List[Dict[str, Any]]:
        """Validate encounter sequence and calculate XP values."""
        validated_sequence = []
        
        for encounter in encounter_sequence:
            # Calculate XP for this encounter
            total_xp = 0
            for creature in encounter.get("creatures", []):
                cr = creature.get("cr", 0)
                quantity = creature.get("quantity", 1)
                xp = self._get_xp_by_cr(cr) * quantity
                creature["xp"] = xp
                total_xp += xp
                
            # Apply encounter multiplier
            total_creatures = sum(creature.get("quantity", 1) for creature in encounter.get("creatures", []))
            multiplier = self._get_encounter_multiplier(total_creatures)
            adjusted_xp = total_xp * multiplier
            
            # Add XP data
            validated_encounter = encounter.copy()
            validated_encounter["total_xp"] = total_xp
            validated_encounter["adjusted_xp"] = adjusted_xp
            validated_encounter["xp_multiplier"] = multiplier
            
            # Calculate difficulty based on party levels
            easy_threshold = self._calculate_xp_threshold(party_levels, "easy")
            medium_threshold = self._calculate_xp_threshold(party_levels, "medium")
            hard_threshold = self._calculate_xp_threshold(party_levels, "hard")
            deadly_threshold = self._calculate_xp_threshold(party_levels, "deadly")
            
            if adjusted_xp < easy_threshold:
                validated_encounter["calculated_difficulty"] = "trivial"
            elif adjusted_xp < medium_threshold:
                validated_encounter["calculated_difficulty"] = "easy"
            elif adjusted_xp < hard_threshold:
                validated_encounter["calculated_difficulty"] = "medium"
            elif adjusted_xp < deadly_threshold:
                validated_encounter["calculated_difficulty"] = "hard"
            else:
                validated_encounter["calculated_difficulty"] = "deadly"
                
            validated_sequence.append(validated_encounter)
            
        return validated_sequence
        
    def _parse_creature_suggestions(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for targeted creature suggestions."""
        creature_suggestions = []
        
        # Try to find creature suggestion blocks
        suggestion_blocks = re.findall(r"(?:\d+\.\s+|[-•*]\s+)([^\n]+(?:\n(?!(?:\d+\.\s+|[-•*]\s+))[^\n]+)*)", response)
        
        if not suggestion_blocks:
            # Try another pattern
            suggestion_blocks = re.findall(r"([^\n]+\(CR [^\)]+\)[^\n]+(?:\n(?![^\n]+\(CR [^\)]+\))[^\n]+)*)", response)
            
        for block in suggestion_blocks:
            suggestion = {
                "description": block.strip(),
                "targeting_rationale": ""
            }
            
            # Try to extract creature name and CR
            name_cr_match = re.search(r"([^(]+)(?:\((?:CR\s*)?([^)]+)\))?", block)
            if name_cr_match:
                suggestion["name"] = name_cr_match.group(1).strip()
                if name_cr_match.group(2):
                    cr_str = name_cr_match.group(2).strip().lower()
                    try:
                        if cr_str in ["1/8", "1/4", "1/2"]:
                            suggestion["cr"] = eval(cr_str)
                        else:
                            suggestion["cr"] = float(cr_str)
                    except:
                        pass
                        
            # Try to extract quantities if mentioned
            quantity_match = re.search(r"(?:group of|x\s*|×\s*)(\d+)", block, re.IGNORECASE)
            if quantity_match:
                suggestion["quantity"] = int(quantity_match.group(1))
                
            # Try to extract targeting rationale
            rationale_lines = []
            for line in block.split("\n")[1:]:
                if line.strip() and not re.match(r"^[-•*]", line):
                    rationale_lines.append(line.strip())
            
            if rationale_lines:
                suggestion["targeting_rationale"] = " ".join(rationale_lines)
                
            creature_suggestions.append(suggestion)
            
        return creature_suggestions
        
    def _parse_thematic_groups(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for thematic creature groups."""
        thematic_groups = []
        
        # Try to find group blocks
        group_blocks = re.findall(r"(?:Group|Option)(?:\s+\d+)?:([^\n]+(?:\n(?!Group|Option\s+\d+:)[^\n]+)*)", response, re.IGNORECASE)
        
        if not group_blocks:
            # Try another pattern
            group_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", response)
            
        if not group_blocks:
            # Split by double newlines
            group_blocks = re.split(r'\n\s*\n', response)
            
        for i, block in enumerate(group_blocks):
            group = {
                "id": i + 1,
                "name": f"Creature Group {i + 1}",
                "concept": "",
                "creatures": []
            }
            
            # Try to extract group name
            name_match = re.search(r"^([^\n:]+)", block)
            if name_match:
                group["name"] = name_match.group(1).strip()
                
            # Try to extract concept
            concept_match = re.search(r"(?:Concept|Relationship|Connection)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if concept_match:
                group["concept"] = concept_match.group(1).strip()
                
            # Try to find creatures
            creature_pattern = re.compile(r"(?:[-•*]\s*|^\d+[\.x]\s*)(\d+)?(?:\s*[x×]\s*)?([^(,]+)(?:\s*\((?:CR\s*)?([^)]+)\))?", re.MULTILINE)
            creature_matches = creature_pattern.findall(block)
            
            for match in creature_matches:
                quantity_str, name, cr_str = match
                quantity = int(quantity_str) if quantity_str else 1
                creature = {
                    "name": name.strip(),
                    "quantity": quantity
                }
                
                # Try to parse CR
                if cr_str:
                    try:
                        cr_cleaned = cr_str.strip().lower()
                        if cr_cleaned in ["1/8", "1/4", "1/2"]:
                            creature["cr"] = eval(cr_cleaned)
                        else:
                            creature["cr"] = float(cr_cleaned)
                    except:
                        creature["cr"] = 0
                        
                group["creatures"].append(creature)
                
            # Try to extract interactions
            interactions_match = re.search(r"(?:Interactions|Synergy|Work Together)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if interactions_match:
                group["interactions"] = interactions_match.group(1).strip()
                
            thematic_groups.append(group)
            
        return thematic_groups
        
    def _parse_reinforcement_waves(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for reinforcement waves."""
        reinforcement_waves = []
        
        # Try to find wave blocks
        wave_blocks = re.findall(r"(?:Wave|Reinforcement)(?:\s+\d+)?:([^\n]+(?:\n(?!Wave|Reinforcement\s+\d+:)[^\n]+)*)", response, re.IGNORECASE)
        
        if not wave_blocks:
            # Try another pattern
            wave_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", response)
            
        for i, block in enumerate(wave_blocks):
            wave = {
                "id": i + 1,
                "name": f"Wave {i + 1}",
                "trigger": "",
                "creatures": [],
                "tactical_changes": ""
            }
            
            # Try to extract wave name
            name_match = re.search(r"^([^\n:]+)", block)
            if name_match:
                wave["name"] = name_match.group(1).strip()
                
            # Try to extract trigger
            trigger_match = re.search(r"(?:Trigger|When|Condition)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if trigger_match:
                wave["trigger"] = trigger_match.group(1).strip()
                
            # Try to find creatures
            creature_pattern = re.compile(r"(?:[-•*]\s*|^\d+[\.x]\s*)(\d+)?(?:\s*[x×]\s*)?([^(,]+)(?:\s*\((?:CR\s*)?([^)]+)\))?", re.MULTILINE)
            creature_matches = creature_pattern.findall(block)
            
            for match in creature_matches:
                quantity_str, name, cr_str = match
                quantity = int(quantity_str) if quantity_str else 1
                creature = {
                    "name": name.strip(),
                    "quantity": quantity
                }
                
                # Try to parse CR
                if cr_str:
                    try:
                        cr_cleaned = cr_str.strip().lower()
                        if cr_cleaned in ["1/8", "1/4", "1/2"]:
                            creature["cr"] = eval(cr_cleaned)
                        else:
                            creature["cr"] = float(cr_cleaned)
                    except:
                        creature["cr"] = 0
                        
                wave["creatures"].append(creature)
                
            # Try to extract tactical changes
            tactics_match = re.search(r"(?:Tactics|Changes|Positioning)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if tactics_match:
                wave["tactical_changes"] = tactics_match.group(1).strip()
                
            reinforcement_waves.append(wave)
            
        return reinforcement_waves
        
    def _parse_encounter_variations(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for encounter variations."""
        variations = []
        
        # Try to find variation blocks
        variation_blocks = re.findall(r"(?:Variation|Option)(?:\s+\d+)?:([^\n]+(?:\n(?!Variation|Option\s+\d+:)[^\n]+)*)", response, re.IGNORECASE)
        
        if not variation_blocks:
            # Try another pattern with numbered list
            variation_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", response)
            
        for i, block in enumerate(variation_blocks):
            variation = {
                "id": i + 1,
                "name": f"Variation {i + 1}",
                "concept": "",
                "creatures": [],
                "tactical_dynamics": ""
            }
            
            # Try to extract variation name
            name_match = re.search(r"^([^\n:]+)", block)
            if name_match:
                variation["name"] = name_match.group(1).strip()
                
            # Try to extract concept
            concept_match = re.search(r"(?:Concept|Approach)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if concept_match:
                variation["concept"] = concept_match.group(1).strip()
                
            # Try to find creatures
            creature_pattern = re.compile(r"(?:[-•*]\s*|^\d+[\.x]\s*)(\d+)?(?:\s*[x×]\s*)?([^(,]+)(?:\s*\((?:CR\s*)?([^)]+)\))?", re.MULTILINE)
            creature_matches = creature_pattern.findall(block)
            
            for match in creature_matches:
                quantity_str, name, cr_str = match
                quantity = int(quantity_str) if quantity_str else 1
                creature = {
                    "name": name.strip(),
                    "quantity": quantity
                }
                
                # Try to parse CR
                if cr_str:
                    try:
                        cr_cleaned = cr_str.strip().lower()
                        if cr_cleaned in ["1/8", "1/4", "1/2"]:
                            creature["cr"] = eval(cr_cleaned)
                        else:
                            creature["cr"] = float(cr_cleaned)
                    except:
                        creature["cr"] = 0
                        
                variation["creatures"].append(creature)
                
            # Try to extract tactical dynamics
            tactics_match = re.search(r"(?:Tactics|Dynamics|Challenge)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if tactics_match:
                variation["tactical_dynamics"] = tactics_match.group(1).strip()
                
            variations.append(variation)
            
        return variations

    def suggest_boss_encounter(self, party_composition: List[Dict[str, Any]], 
                            campaign_arc: str = None,
                            environment: str = None,
                            climactic_tier: str = "arc") -> Dict[str, Any]:
        """
        Generate a climactic boss encounter with appropriate minions and dynamics.
        
        Args:
            party_composition: List of party member dictionaries with keys 'level' and 'class'
            campaign_arc: Optional description of the campaign arc
            environment: Optional encounter environment
            climactic_tier: Scale of the encounter ('session', 'arc', 'campaign')
            
        Returns:
            Dict[str, Any]: Boss encounter data with minions and phases
        """
        # Calculate party level and XP thresholds
        party_levels = [member.get("level", 1) for member in party_composition]
        avg_level = sum(party_levels) / len(party_levels)
        
        # Determine appropriate XP and CR based on climactic tier
        if climactic_tier == "session":
            # Session boss - hard encounter
            xp_threshold = self._calculate_xp_threshold(party_levels, "hard")
            boss_cr_modifier = 1.0
        elif climactic_tier == "campaign":
            # Campaign boss - deadly+ encounter
            xp_threshold = self._calculate_xp_threshold(party_levels, "deadly") * 1.5
            boss_cr_modifier = 2.0
        else:
            # Default: arc boss - deadly encounter
            xp_threshold = self._calculate_xp_threshold(party_levels, "deadly")
            boss_cr_modifier = 1.5
        
        # Suggested boss CR
        boss_cr = min(30, avg_level * boss_cr_modifier)
        
        # Build context for LLM
        context = f"Party Composition: {len(party_composition)} characters with average level {avg_level:.1f}\n"
        context += f"XP Budget: {xp_threshold}\n"
        context += f"Climactic Tier: {climactic_tier}\n"
        context += f"Suggested Boss CR: {boss_cr:.1f}\n"
        
        if campaign_arc:
            context += f"Campaign Arc: {campaign_arc}\n"
            
        if environment:
            context += f"Environment: {environment}\n"
            
        # Create prompt for boss encounter
        prompt = self._create_prompt(
            "create boss encounter",
            context + "\n"
            "Design a memorable and challenging boss encounter with supporting minions:\n"
            "1. Create a primary boss creature with name, CR, and key abilities\n"
            "2. Design 1-2 phases for the boss fight with different tactics or transformations\n"
            "3. Suggest appropriate minions that complement the boss tactically\n"
            "4. Describe environmental elements or lair actions that enhance the encounter\n"
            "5. Provide tactical suggestions for running the boss encounter\n"
            "6. Include escape mechanisms or final desperation moves for the boss\n\n"
            "The encounter should be challenging but winnable, with interesting tactical decisions for the players."
        )
        
        try:
            # Generate boss encounter with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured boss encounter data
            boss_data = self._parse_boss_encounter(response)
            
            return {
                "success": True,
                "boss_encounter": boss_data,
                "climactic_tier": climactic_tier,
                "xp_threshold": xp_threshold,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate boss encounter: {str(e)}"
            }

    def create_encounter_by_environment(self, environment: str, party_levels: List[int],
                                    difficulty: str = "medium",
                                    time_of_day: str = None,
                                    weather_conditions: str = None) -> Dict[str, Any]:
        """
        Generate encounter options specifically tailored to an environment with native creatures.
        
        Args:
            environment: Target environment (forest, mountains, dungeon, etc.)
            party_levels: List of party member levels
            difficulty: Desired difficulty level
            time_of_day: Optional time of day affecting encounter
            weather_conditions: Optional weather conditions
            
        Returns:
            Dict[str, Any]: Environment-specific encounter options
        """
        # Calculate XP threshold
        xp_threshold = self._calculate_xp_threshold(party_levels, difficulty)
        avg_level = sum(party_levels) / len(party_levels)
        
        # Build context for LLM
        context = f"Environment: {environment}\n"
        context += f"Party Size: {len(party_levels)}\n"
        context += f"Average Party Level: {avg_level:.1f}\n"
        context += f"Difficulty: {difficulty}\n"
        context += f"XP Budget: {xp_threshold}\n"
        
        if time_of_day:
            context += f"Time of Day: {time_of_day}\n"
            
        if weather_conditions:
            context += f"Weather: {weather_conditions}\n"
        
        # Create prompt for environmental encounter
        prompt = self._create_prompt(
            "create environmental encounter",
            context + "\n"
            f"Design 3 distinct encounter options that showcase the {environment} environment using creatures native to this setting.\n"
            "For each encounter:\n"
            "1. Provide a name and brief concept that ties closely to the environment\n"
            "2. List specific environment-appropriate creatures with quantities and CRs\n"
            "3. Describe unique environmental features that affect the encounter\n"
            "4. Suggest how the environment itself can become part of the challenge\n"
            "5. Include terrain-specific tactics creatures would use\n\n"
            "Focus on creating encounters that couldn't take place anywhere else and that make the environment feel alive and dangerous."
        )
        
        try:
            # Generate environmental encounters with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured encounter options
            encounter_options = self._parse_encounter_response(response)
            
            # Validate encounter options against XP budget
            validated_options = self._validate_encounter_options(encounter_options, xp_threshold)
            
            return {
                "success": True,
                "environment": environment,
                "encounter_options": validated_options,
                "environmental_factors": {
                    "time_of_day": time_of_day,
                    "weather": weather_conditions
                },
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate environmental encounters: {str(e)}"
            }

    def suggest_encounter_with_terrain_features(self, party_composition: List[Dict[str, Any]],
                                            environment: str,
                                            difficulty: str = "medium",
                                            terrain_complexity: str = "moderate") -> Dict[str, Any]:
        """
        Create encounters that incorporate terrain or environmental hazards.
        
        Args:
            party_composition: List of party member dictionaries
            environment: Environment type
            difficulty: Desired encounter difficulty
            terrain_complexity: Complexity of terrain features ('simple', 'moderate', 'complex')
            
        Returns:
            Dict[str, Any]: Encounter with terrain features
        """
        # Calculate party level and XP thresholds
        party_levels = [member.get("level", 1) for member in party_composition]
        avg_level = sum(party_levels) / len(party_levels)
        
        # Difficulty can be adjusted down since terrain adds challenge
        adjusted_difficulty = difficulty
        if terrain_complexity == "complex":
            # Lower mechanical difficulty when terrain is complex
            if difficulty == "deadly":
                adjusted_difficulty = "hard"
            elif difficulty == "hard":
                adjusted_difficulty = "medium"
            elif difficulty == "medium":
                adjusted_difficulty = "easy"
        
        xp_threshold = self._calculate_xp_threshold(party_levels, adjusted_difficulty)
        
        # Build context for LLM
        context = f"Environment: {environment}\n"
        context += f"Party Size: {len(party_levels)}\n"
        context += f"Average Party Level: {avg_level:.1f}\n"
        context += f"Encounter Difficulty: {difficulty}\n"
        context += f"Terrain Complexity: {terrain_complexity}\n"
        context += f"Adjusted XP Budget: {xp_threshold}\n"
        
        # Create prompt for terrain-based encounter
        prompt = self._create_prompt(
            "create terrain-focused encounter",
            context + "\n"
            f"Design an encounter for a {environment} that heavily incorporates terrain features and environmental hazards.\n"
            "Include the following elements:\n"
            "1. A detailed map layout with key terrain features (described, not visual)\n"
            "2. 3-5 specific terrain hazards or interactive elements with mechanical effects\n"
            "3. Creatures that complement or can exploit these terrain features\n"
            "4. Tactical suggestions for how creatures use the terrain to their advantage\n"
            "5. Ways players might use or neutralize terrain features\n\n"
            f"The terrain should be {terrain_complexity} in complexity and meaningfully impact the difficulty and tactics of the encounter."
        )
        
        try:
            # Generate terrain-based encounter with LLM
            response = self.llm_service.generate(prompt)
            
            # Create structured terrain encounter data
            terrain_data = self._parse_terrain_encounter(response)
            
            # Add creatures and validate
            creatures = terrain_data.get("creatures", [])
            if creatures:
                # Calculate XP
                total_xp = 0
                for creature in creatures:
                    cr = creature.get("cr", 0)
                    quantity = creature.get("quantity", 1)
                    xp = self._get_xp_by_cr(cr) * quantity
                    creature["xp"] = xp
                    total_xp += xp
                    
                # Apply multiplier
                total_creatures = sum(creature.get("quantity", 1) for creature in creatures)
                multiplier = self._get_encounter_multiplier(total_creatures)
                adjusted_xp = total_xp * multiplier
                
                terrain_data["encounter_xp"] = {
                    "base_xp": total_xp,
                    "adjusted_xp": adjusted_xp,
                    "xp_multiplier": multiplier,
                    "target_xp": xp_threshold
                }
            
            return {
                "success": True,
                "terrain_encounter": terrain_data,
                "environment": environment,
                "terrain_complexity": terrain_complexity,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate terrain encounter: {str(e)}"
            }

    def generate_tiered_encounters(self, party_composition: List[Dict[str, Any]],
                                theme: str,
                                num_tiers: int = 3) -> Dict[str, Any]:
        """
        Create encounters with multiple tiers of enemies (fodder, elite, leaders).
        
        Args:
            party_composition: List of party member dictionaries
            theme: Thematic focus for the encounter
            num_tiers: Number of enemy tiers (usually 2-3)
            
        Returns:
            Dict[str, Any]: Tiered encounter structure
        """
        # Calculate party level and XP thresholds
        party_levels = [member.get("level", 1) for member in party_composition]
        avg_level = sum(party_levels) / len(party_levels)
        
        # Calculate total XP budget (hard encounter)
        xp_threshold = self._calculate_xp_threshold(party_levels, "hard")
        
        # Build context for LLM
        context = f"Party Size: {len(party_levels)}\n"
        context += f"Average Party Level: {avg_level:.1f}\n"
        context += f"Theme: {theme}\n"
        context += f"Number of Enemy Tiers: {num_tiers}\n"
        context += f"Total XP Budget: {xp_threshold}\n"
        
        # Create prompt for tiered encounter
        prompt = self._create_prompt(
            "create tiered encounter",
            context + "\n"
            f"Design an encounter with {num_tiers} distinct tiers of enemies following a '{theme}' theme.\n"
            "Structure the enemy composition as:\n"
            "1. Fodder/Minions: Numerous low-CR creatures to absorb resources\n"
            "2. Elite/Veterans: Mid-tier threats with specialized abilities\n"
            f"{'3. Leaders/Champions: High-CR creatures that direct or buff others' if num_tiers >= 3 else ''}\n\n"
            "For each tier, provide:\n"
            "- Specific creatures with CR and quantities\n"
            "- Role in the encounter and tactical approach\n"
            "- How they interact with other tiers\n\n"
            "Additionally, suggest initiative management techniques for handling multiple enemy types and provide tactics for how different tiers coordinate their actions."
        )
        
        try:
            # Generate tiered encounter with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured tiered encounter data
            tiered_encounter = self._parse_tiered_encounter(response, num_tiers)
            
            # Calculate XP for each tier and total
            total_xp = 0
            total_creatures = 0
            
            for tier in tiered_encounter.get("tiers", []):
                tier_xp = 0
                tier_count = 0
                
                for creature in tier.get("creatures", []):
                    cr = creature.get("cr", 0)
                    quantity = creature.get("quantity", 1)
                    xp = self._get_xp_by_cr(cr) * quantity
                    creature["xp"] = xp
                    tier_xp += xp
                    tier_count += quantity
                    
                tier["tier_xp"] = tier_xp
                tier["creature_count"] = tier_count
                total_xp += tier_xp
                total_creatures += tier_count
                
            # Apply multiplier based on total creature count
            multiplier = self._get_encounter_multiplier(total_creatures)
            adjusted_xp = total_xp * multiplier
            
            tiered_encounter["total_xp"] = total_xp
            tiered_encounter["adjusted_xp"] = adjusted_xp
            tiered_encounter["xp_multiplier"] = multiplier
            tiered_encounter["target_xp"] = xp_threshold
            
            return {
                "success": True,
                "tiered_encounter": tiered_encounter,
                "theme": theme,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate tiered encounter: {str(e)}"
            }

    def scale_encounter_for_party_size(self, encounter_data: Dict[str, Any],
                                    original_party_size: int,
                                    new_party_size: int) -> Dict[str, Any]:
        """
        Adjust an existing encounter design for a different party size.
        
        Args:
            encounter_data: Original encounter data
            original_party_size: Size of the party the encounter was designed for
            new_party_size: Target party size to scale for
            
        Returns:
            Dict[str, Any]: Scaled encounter data
        """
        # Extract creatures from encounter data
        creatures = encounter_data.get("creatures", [])
        if not creatures and "encounter_options" in encounter_data:
            # Take the first encounter option if multiple available
            creatures = encounter_data.get("encounter_options", [])[0].get("creatures", []) if encounter_data.get("encounter_options") else []
        
        if not creatures:
            return {
                "success": False,
                "error": "No creatures found in encounter data"
            }
            
        # Calculate scaling factor
        scaling_factor = new_party_size / original_party_size if original_party_size > 0 else 1.0
        
        # Create context for LLM
        context = f"Original Encounter: {', '.join([f'{c.get('quantity', 1)}x {c.get('name', 'Unknown')} (CR {c.get('cr', 0)})' for c in creatures])}\n"
        context += f"Original Party Size: {original_party_size}\n"
        context += f"New Party Size: {new_party_size}\n"
        context += f"Scaling Factor: {scaling_factor:.2f}\n"
        
        # Create prompt for encounter scaling
        prompt = self._create_prompt(
            "scale encounter for party size",
            context + "\n"
            f"Adjust this encounter to be appropriately challenging for a party of {new_party_size} players instead of {original_party_size}.\n"
            "Consider the following approaches:\n"
            "1. Adjusting the quantity of existing creatures\n"
            "2. Adding or removing creature types\n"
            "3. Substituting creatures with higher/lower CR variants\n"
            "4. Modifying creature abilities or tactics\n\n"
            "Provide a specific and concrete adjustment plan, with exact quantities and any creature substitutions."
        )
        
        try:
            # Generate scaling suggestions with LLM
            response = self.llm_service.generate(prompt)
            
            # Simple scaling approach: adjust quantities
            scaled_creatures = []
            for creature in creatures:
                scaled_creature = creature.copy()
                original_quantity = creature.get("quantity", 1)
                
                # Scale quantity based on party size difference
                new_quantity = max(1, round(original_quantity * scaling_factor))
                scaled_creature["quantity"] = new_quantity
                
                scaled_creatures.append(scaled_creature)
                
            # Calculate new XP values
            original_xp = 0
            scaled_xp = 0
            
            for i, creature in enumerate(creatures):
                cr = creature.get("cr", 0)
                original_quantity = creature.get("quantity", 1)
                scaled_quantity = scaled_creatures[i].get("quantity", 1)
                
                xp_per_creature = self._get_xp_by_cr(cr)
                original_xp += xp_per_creature * original_quantity
                scaled_xp += xp_per_creature * scaled_quantity
                
            # Apply multipliers
            original_total = sum(c.get("quantity", 1) for c in creatures)
            scaled_total = sum(c.get("quantity", 1) for c in scaled_creatures)
            
            original_multiplier = self._get_encounter_multiplier(original_total)
            scaled_multiplier = self._get_encounter_multiplier(scaled_total)
            
            adjusted_original_xp = original_xp * original_multiplier
            adjusted_scaled_xp = scaled_xp * scaled_multiplier
            
            return {
                "success": True,
                "original_encounter": creatures,
                "scaled_encounter": scaled_creatures,
                "original_party_size": original_party_size,
                "new_party_size": new_party_size,
                "original_xp": {
                    "base": original_xp,
                    "multiplier": original_multiplier,
                    "adjusted": adjusted_original_xp
                },
                "scaled_xp": {
                    "base": scaled_xp,
                    "multiplier": scaled_multiplier,
                    "adjusted": adjusted_scaled_xp
                },
                "llm_suggestions": response,
                "scaling_factor": scaling_factor
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to scale encounter: {str(e)}"
            }

    def analyze_party_strengths_weaknesses(self, party_composition: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze party composition to identify strengths and vulnerabilities for encounter design.
        
        Args:
            party_composition: List of party member dictionaries with keys 'level', 'class', and optionally 'subclass'
            
        Returns:
            Dict[str, Any]: Analysis of party strengths and weaknesses
        """
        # Build context for LLM
        context = f"Party Composition:\n"
        for i, member in enumerate(party_composition, 1):
            context += f"- Player {i}: Level {member.get('level', 1)} {member.get('class', 'Fighter')}"
            if "subclass" in member:
                context += f" ({member['subclass']})"
            if "race" in member:
                context += f", {member['race']}"
            if "key_features" in member:
                context += f", Features: {', '.join(member['key_features'][:3])}"
            context += "\n"
        
        # Create prompt for party analysis
        prompt = self._create_prompt(
            "analyze party composition",
            context + "\n"
            "Analyze this party composition to identify tactical strengths and vulnerabilities for encounter design.\n"
            "Provide insights on:\n"
            "1. Offensive capabilities (damage types, ranged vs melee, AoE, single-target)\n"
            "2. Defensive capabilities (AC ranges, saving throw strengths/weaknesses, resistances)\n"
            "3. Utility capabilities (skills, problem-solving, mobility, resource management)\n"
            "4. Gaps in party composition or capabilities\n"
            "5. Specific encounter elements that would challenge this party\n"
            "6. Specific encounter elements that this party would handle easily\n\n"
            "Focus on concrete tactical insights that could be used to create appropriately challenging encounters."
        )
        
        try:
            # Generate party analysis with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured analysis
            party_analysis = self._parse_party_analysis(response)
            
            return {
                "success": True,
                "party_analysis": party_analysis,
                "party_composition": party_composition,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to analyze party composition: {str(e)}"
            }

    def create_progressive_campaign_encounters(self, party_composition: List[Dict[str, Any]],
                                            campaign_theme: str,
                                            num_levels: int = 4,
                                            encounters_per_level: int = 3) -> Dict[str, Any]:
        """
        Generate a progression of encounters that scale with party level through a campaign.
        
        Args:
            party_composition: Current party composition
            campaign_theme: Overall theme or focus of the campaign
            num_levels: Number of level increments to plan for
            encounters_per_level: Number of encounters to generate per level increment
            
        Returns:
            Dict[str, Any]: Progressive campaign encounters
        """
        # Get current average party level
        current_levels = [member.get("level", 1) for member in party_composition]
        start_level = sum(current_levels) / len(current_levels)
        
        # Build context for LLM
        context = f"Party Composition: {len(party_composition)} characters with average level {start_level:.1f}\n"
        context += f"Campaign Theme: {campaign_theme}\n"
        context += f"Level Progression: {num_levels} level increments\n"
        context += f"Encounters Per Level: {encounters_per_level}\n"
        
        # Create prompt for progressive encounters
        prompt = self._create_prompt(
            "create campaign encounter progression",
            context + "\n"
            f"Design a progression of encounters that scale with the party from level {int(start_level)} through {int(start_level) + num_levels - 1}.\n"
            "For each level increment, create:\n"
            f"- {encounters_per_level} distinct encounter concepts appropriate for that level\n"
            "- A mix of difficulty levels (easy, medium, hard, deadly)\n"
            "- Progressive introduction of more complex monster abilities and tactics\n"
            "- Thematic development that builds on previous encounters\n\n"
            f"Structure the response by level, with {encounters_per_level} encounters per level, each with:\n"
            "1. Encounter name and environment\n"
            "2. Specific creatures with quantities and CRs\n"
            "3. Brief tactical description\n"
            "4. How this encounter advances the campaign theme\n\n"
            "Ensure a sense of progression in challenge, complexity, and narrative significance."
        )
        
        try:
            # Generate progressive encounters with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured progression data
            progression_data = self._parse_campaign_progression(response, num_levels, encounters_per_level)
            
            return {
                "success": True,
                "campaign_progression": progression_data,
                "campaign_theme": campaign_theme,
                "starting_level": int(start_level),
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate campaign progression: {str(e)}"
            }

    def suggest_complementary_creatures(self, primary_creature: Dict[str, Any],
                                    challenge_level: str = "medium",
                                    party_level: int = None) -> Dict[str, Any]:
        """
        Suggest creatures that complement a primary creature tactically.
        
        Args:
            primary_creature: Dictionary with 'name', 'cr', and optionally 'traits', 'abilities'
            challenge_level: Target challenge level
            party_level: Optional party level for appropriate CR range
            
        Returns:
            Dict[str, Any]: Complementary creature suggestions
        """
        primary_name = primary_creature.get("name", "Unknown Creature")
        primary_cr = primary_creature.get("cr", 1)
        
        # Determine CR range for companions
        if party_level:
            max_companion_cr = party_level
            min_companion_cr = max(1/8, party_level / 4)
        else:
            max_companion_cr = primary_cr * 1.2
            min_companion_cr = primary_cr * 0.25
        
        # Build context for LLM
        context = f"Primary Creature: {primary_name} (CR {primary_cr})\n"
        context += f"Challenge Level: {challenge_level}\n"
        context += f"Companion CR Range: {min_companion_cr:.1f} to {max_companion_cr:.1f}\n"
        
        if party_level:
            context += f"Party Level: {party_level}\n"
            
        # Add traits and abilities if available
        if "traits" in primary_creature:
            context += "Primary Creature Traits:\n"
            for trait in primary_creature["traits"][:3]:  # Limit to top 3 traits
                trait_name = trait.get("name", "Unnamed Trait")
                context += f"- {trait_name}\n"
                
        if "abilities" in primary_creature:
            context += "Primary Creature Abilities:\n"
            for ability in primary_creature["abilities"][:3]:  # Limit to top 3 abilities
                ability_name = ability.get("name", "Unnamed Ability")
                context += f"- {ability_name}\n"
        
        # Create prompt for complementary creatures
        prompt = self._create_prompt(
            "suggest complementary creatures",
            context + "\n"
            f"Suggest 3-5 creatures that would complement {primary_name} tactically in a combat encounter.\n"
            "For each suggested creature:\n"
            "1. Provide name, CR, and recommended quantity\n"
            "2. Explain how it specifically complements the primary creature\n"
            "3. Describe tactical synergies between their abilities\n"
            "4. Suggest positioning and coordination tactics\n\n"
            "Focus on creating interesting tactical combinations rather than just adding generic reinforcements."
        )
        
        try:
            # Generate complementary suggestions with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured suggestions
            complementary_creatures = self._parse_complementary_suggestions(response)
            
            # Calculate total CR and XP
            total_xp = self._get_xp_by_cr(primary_cr)
            total_count = 1  # Start with primary creature
            
            for creature in complementary_creatures:
                cr = creature.get("cr", 0)
                quantity = creature.get("quantity", 1)
                xp = self._get_xp_by_cr(cr) * quantity
                creature["xp"] = xp
                total_xp += xp
                total_count += quantity
                
            # Apply encounter multiplier
            multiplier = self._get_encounter_multiplier(total_count)
            adjusted_xp = total_xp * multiplier
            
            return {
                "success": True,
                "primary_creature": primary_creature,
                "complementary_creatures": complementary_creatures,
                "encounter_stats": {
                    "total_xp": total_xp,
                    "adjusted_xp": adjusted_xp,
                    "multiplier": multiplier,
                    "creature_count": total_count
                },
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to suggest complementary creatures: {str(e)}"
            }

    # Helper parser methods for the new functions

    def _parse_boss_encounter(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for boss encounter."""
        boss_data = {
            "boss": {},
            "phases": [],
            "minions": [],
            "environmental_elements": [],
            "tactics": ""
        }
        
        # Try to extract boss details
        boss_block = re.search(r"(?:Boss|Primary)(?:[^:]*?):\s*([^\n]+(?:\n(?!Phase|Minion|Environment|Tactic)[^\n]+)*)", response, re.IGNORECASE)
        if boss_block:
            boss_text = boss_block.group(1).strip()
            boss_data["boss"]["description"] = boss_text
            
            # Try to extract boss name
            name_match = re.search(r"^([^\n(,]+)", boss_text)
            if name_match:
                boss_data["boss"]["name"] = name_match.group(1).strip()
                
            # Try to extract CR
            cr_match = re.search(r"(?:CR|Challenge Rating)(?:[^:]*?):\s*(\d+(?:/\d+)?)", boss_text, re.IGNORECASE)
            if cr_match:
                cr_str = cr_match.group(1)
                try:
                    if "/" in cr_str:
                        num, den = cr_str.split("/")
                        boss_data["boss"]["cr"] = float(num) / float(den)
                    else:
                        boss_data["boss"]["cr"] = float(cr_str)
                except:
                    boss_data["boss"]["cr"] = 0
        
        # Try to extract phases
        phase_blocks = re.findall(r"(?:Phase|Stage)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Phase|Stage|Minion|Environment|Tactic)[^\n]+)*)", response, re.IGNORECASE)
        
        for i, phase_text in enumerate(phase_blocks):
            phase = {
                "id": i + 1,
                "description": phase_text.strip()
            }
            boss_data["phases"].append(phase)
        
        # Try to extract minions
        minion_blocks = re.findall(r"(?:Minion|Support|Ally)(?:[^:]*?):\s*([^\n]+(?:\n(?!Minion|Support|Ally|Phase|Environment|Tactic)[^\n]+)*)", response, re.IGNORECASE)
        
        if not minion_blocks:
            # Try to find creature blocks in the regular text
            creature_pattern = re.compile(r"(?:[-•*]\s*|^\d+[\.x]\s*)(\d+)?(?:\s*[x×]\s*)?([^(,]+)(?:\s*\((?:CR\s*)?([^)]+)\))?", re.MULTILINE)
            creature_matches = creature_pattern.findall(response)
            
            for match in creature_matches:
                quantity_str, name, cr_str = match
                quantity = int(quantity_str) if quantity_str else 1
                if name.lower() != boss_data["boss"].get("name", "").lower():  # Not the boss
                    minion = {
                        "name": name.strip(),
                        "quantity": quantity
                    }
                    
                    # Try to parse CR
                    if cr_str:
                        try:
                            cr_cleaned = cr_str.strip().lower()
                            if cr_cleaned in ["1/8", "1/4", "1/2"]:
                                minion["cr"] = eval(cr_cleaned)
                            else:
                                minion["cr"] = float(cr_cleaned)
                        except:
                            minion["cr"] = 0
                            
                    boss_data["minions"].append(minion)
        else:
            for minion_text in minion_blocks:
                # Try to find creature information
                creature_pattern = re.compile(r"(?:[-•*]\s*|^\d+[\.x]\s*)(\d+)?(?:\s*[x×]\s*)?([^(,]+)(?:\s*\((?:CR\s*)?([^)]+)\))?", re.MULTILINE)
                creature_matches = creature_pattern.findall(minion_text)
                
                for match in creature_matches:
                    quantity_str, name, cr_str = match
                    quantity = int(quantity_str) if quantity_str else 1
                    minion = {
                        "name": name.strip(),
                        "quantity": quantity,
                        "description": minion_text.strip()
                    }
                    
                    # Try to parse CR
                    if cr_str:
                        try:
                            cr_cleaned = cr_str.strip().lower()
                            if cr_cleaned in ["1/8", "1/4", "1/2"]:
                                minion["cr"] = eval(cr_cleaned)
                            else:
                                minion["cr"] = float(cr_cleaned)
                        except:
                            minion["cr"] = 0
                            
                    boss_data["minions"].append(minion)
        
        # Try to extract environmental elements
        env_block = re.search(r"(?:Environment|Lair|Arena)(?:[^:]*?):\s*([^\n]+(?:\n(?!Phase|Minion|Tactic)[^\n]+)*)", response, re.IGNORECASE)
        if env_block:
            env_text = env_block.group(1).strip()
            
            # Extract individual elements if listed
            elements = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", env_text, re.MULTILINE)
            if elements:
                for element in elements:
                    boss_data["environmental_elements"].append(element.strip())
            else:
                boss_data["environmental_elements"].append(env_text)
        
        # Try to extract tactics
        tactics_block = re.search(r"(?:Tactic|Strategy|Running)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*)", response, re.IGNORECASE)
        if tactics_block:
            boss_data["tactics"] = tactics_block.group(1).strip()
        
        return boss_data

    def _parse_terrain_encounter(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for terrain-based encounter."""
        terrain_data = {
            "map_layout": "",
            "terrain_features": [],
            "creatures": [],
            "tactical_notes": ""
        }
        
        # Try to extract map layout
        layout_block = re.search(r"(?:Map|Layout|Terrain Layout)(?:[^:]*?):\s*([^\n]+(?:\n(?!Feature|Hazard|Creature|Tactic)[^\n]+)*)", response, re.IGNORECASE)
        if layout_block:
            terrain_data["map_layout"] = layout_block.group(1).strip()
        
        # Try to extract terrain features/hazards
        feature_blocks = re.findall(r"(?:Feature|Hazard|Terrain Element)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Feature|Hazard|Terrain Element|Creature|Tactic)[^\n]+)*)", response, re.IGNORECASE)
        
        if not feature_blocks:
            # Try to find numbered or bulleted lists
            feature_blocks = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+(?:\n(?![-•*]|\d+\.)[^\n]+)*)", response, re.MULTILINE)
        
        for feature_text in feature_blocks:
            feature = {"description": feature_text.strip()}
            
            # Try to extract feature name
            name_match = re.search(r"^([^:]+)(?::|–|-)?\s", feature_text)
            if name_match:
                feature["name"] = name_match.group(1).strip()
                
            terrain_data["terrain_features"].append(feature)
        
        # Try to find creatures
        creature_pattern = re.compile(r"(?:[-•*]\s*|^\d+[\.x]\s*)(\d+)?(?:\s*[x×]\s*)?([^(,]+)(?:\s*\((?:CR\s*)?([^)]+)\))?", re.MULTILINE)
        creature_matches = creature_pattern.findall(response)
        
        for match in creature_matches:
            quantity_str, name, cr_str = match
            quantity = int(quantity_str) if quantity_str else 1
            creature = {
                "name": name.strip(),
                "quantity": quantity
            }
            
            # Try to parse CR
            if cr_str:
                try:
                    cr_cleaned = cr_str.strip().lower()
                    if cr_cleaned in ["1/8", "1/4", "1/2"]:
                        creature["cr"] = eval(cr_cleaned)
                    else:
                        creature["cr"] = float(cr_cleaned)
                except:
                    creature["cr"] = 0
                    
            terrain_data["creatures"].append(creature)
        
        # Try to extract tactical notes
        tactics_block = re.search(r"(?:Tactic|Strategy|Approach)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if tactics_block:
            terrain_data["tactical_notes"] = tactics_block.group(1).strip()
        
        return terrain_data

    def _parse_tiered_encounter(self, response: str, num_tiers: int) -> Dict[str, Any]:
        """Parse LLM response for tiered encounter."""
        tiered_data = {
            "tiers": [],
            "coordination_tactics": ""
        }
        
        # Try to find tier blocks
        tier_names = ["Fodder", "Minion", "Elite", "Veteran", "Leader", "Champion", "Boss"]
        
        for i in range(min(num_tiers, len(tier_names))):
            tier_term = tier_names[i]
            tier_block = re.search(rf"(?:{tier_term}|Tier {i+1})(?:[^:]*?):\s*([^\n]+(?:\n(?!{tier_term}|Tier \d+|Coordination|Tactic)[^\n]+)*)", response, re.IGNORECASE)
            
            if tier_block:
                tier_data = {
                    "tier_level": i + 1,
                    "tier_name": tier_term,
                    "description": tier_block.group(1).strip(),
                    "creatures": []
                }
                
                # Try to find creatures in this tier
                creature_pattern = re.compile(r"(?:[-•*]\s*|^\d+[\.x]\s*)(\d+)?(?:\s*[x×]\s*)?([^(,]+)(?:\s*\((?:CR\s*)?([^)]+)\))?", re.MULTILINE)
                creature_matches = creature_pattern.findall(tier_block.group(1))
                
                for match in creature_matches:
                    quantity_str, name, cr_str = match
                    quantity = int(quantity_str) if quantity_str else 1
                    creature = {
                        "name": name.strip(),
                        "quantity": quantity
                    }
                    
                    # Try to parse CR
                    if cr_str:
                        try:
                            cr_cleaned = cr_str.strip().lower()
                            if cr_cleaned in ["1/8", "1/4", "1/2"]:
                                creature["cr"] = eval(cr_cleaned)
                            else:
                                creature["cr"] = float(cr_cleaned)
                        except:
                            creature["cr"] = 0
                            
                    tier_data["creatures"].append(creature)
                    
                tiered_data["tiers"].append(tier_data)
        
        # If no tiers found using named approach, try to split numerically
        if not tiered_data["tiers"]:
            # Try to find numbered tiers
            numbered_tiers = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", response)
            
            for i, tier_text in enumerate(numbered_tiers[:num_tiers]):
                tier_data = {
                    "tier_level": i + 1,
                    "tier_name": f"Tier {i+1}",
                    "description": tier_text.strip(),
                    "creatures": []
                }
                
                # Try to find creatures in this tier
                creature_pattern = re.compile(r"(?:[-•*]\s*|^\d+[\.x]\s*)(\d+)?(?:\s*[x×]\s*)?([^(,]+)(?:\s*\((?:CR\s*)?([^)]+)\))?", re.MULTILINE)
                creature_matches = creature_pattern.findall(tier_text)
                
                for match in creature_matches:
                    quantity_str, name, cr_str = match
                    quantity = int(quantity_str) if quantity_str else 1
                    creature = {
                        "name": name.strip(),
                        "quantity": quantity
                    }
                    
                    # Try to parse CR
                    if cr_str:
                        try:
                            cr_cleaned = cr_str.strip().lower()
                            if cr_cleaned in ["1/8", "1/4", "1/2"]:
                                creature["cr"] = eval(cr_cleaned)
                            else:
                                creature["cr"] = float(cr_cleaned)
                        except:
                            creature["cr"] = 0
                            
                    tier_data["creatures"].append(creature)
                    
                tiered_data["tiers"].append(tier_data)
        
        # Try to extract coordination tactics
        coordination_block = re.search(r"(?:Coordination|Initiative|Management|Tactics)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if coordination_block:
            tiered_data["coordination_tactics"] = coordination_block.group(1).strip()
        
        return tiered_data

    def _parse_party_analysis(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for party analysis."""
        analysis = {
            "offensive_capabilities": "",
            "defensive_capabilities": "",
            "utility_capabilities": "",
            "gaps": [],
            "effective_challenges": [],
            "ineffective_challenges": []
        }
        
        # Try to extract offensive capabilities
        offensive_block = re.search(r"(?:Offensive|Damage|Attack)(?:[^:]*?):\s*([^\n]+(?:\n(?!Defensive|Utility|Gap)[^\n]+)*)", response, re.IGNORECASE)
        if offensive_block:
            analysis["offensive_capabilities"] = offensive_block.group(1).strip()
        
        # Try to extract defensive capabilities
        defensive_block = re.search(r"(?:Defensive|Protection|AC|HP)(?:[^:]*?):\s*([^\n]+(?:\n(?!Offensive|Utility|Gap)[^\n]+)*)", response, re.IGNORECASE)
        if defensive_block:
            analysis["defensive_capabilities"] = defensive_block.group(1).strip()
        
        # Try to extract utility capabilities
        utility_block = re.search(r"(?:Utility|Skill|Problem|Resource)(?:[^:]*?):\s*([^\n]+(?:\n(?!Offensive|Defensive|Gap)[^\n]+)*)", response, re.IGNORECASE)
        if utility_block:
            analysis["utility_capabilities"] = utility_block.group(1).strip()
        
        # Try to extract gaps
        gaps_block = re.search(r"(?:Gaps|Weaknesses|Vulnerabilities)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if gaps_block:
            gaps_text = gaps_block.group(1).strip()
            
            # Try to split into individual gaps
            gap_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", gaps_text, re.MULTILINE)
            if gap_items:
                analysis["gaps"] = [item.strip() for item in gap_items]
            else:
                analysis["gaps"] = [gaps_text]
        
        # Try to extract effective challenges
        effective_block = re.search(r"(?:Challenge|Would Challenge|Effective|Difficult)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if effective_block:
            effective_text = effective_block.group(1).strip()
            
            # Try to split into individual challenges
            challenge_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", effective_text, re.MULTILINE)
            if challenge_items:
                analysis["effective_challenges"] = [item.strip() for item in challenge_items]
            else:
                analysis["effective_challenges"] = [effective_text]
        
        # Try to extract ineffective challenges
        ineffective_block = re.search(r"(?:Handle Easily|Ineffective|Easy)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if ineffective_block:
            ineffective_text = ineffective_block.group(1).strip()
            
            # Try to split into individual items
            ineffective_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", ineffective_text, re.MULTILINE)
            if ineffective_items:
                analysis["ineffective_challenges"] = [item.strip() for item in ineffective_items]
            else:
                analysis["ineffective_challenges"] = [ineffective_text]
        
        return analysis

    def _parse_campaign_progression(self, response: str, num_levels: int, encounters_per_level: int) -> Dict[str, Any]:
        """Parse LLM response for campaign progression."""
        progression = {
            "levels": []
        }
        
        # Try to split response by level
        level_blocks = re.findall(r"(?:Level|Tier)(?:\s+\d+)(?:[^:]*?):\s*([^\n]+(?:\n(?!Level|Tier\s+\d+)[^\n]+)*)", response, re.IGNORECASE)
        
        # If not enough level blocks found, try to split the response more generally
        if len(level_blocks) < num_levels:
            paragraphs = re.split(r'\n\s*\n', response)
            level_blocks = paragraphs[:num_levels]
        
        for i, level_text in enumerate(level_blocks[:num_levels]):
            level_data = {
                "level": i + 1,
                "encounters": []
            }
            
            # Try to find encounters in this level
            encounter_blocks = re.findall(r"(?:Encounter|Option)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Encounter|Option\s+\d+)[^\n]+)*)", level_text, re.IGNORECASE)
            
            if not encounter_blocks:
                # Try another pattern with numbered list
                encounter_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", level_text)
            
            # If still not enough encounter blocks, try to split the level text
            if len(encounter_blocks) < encounters_per_level:
                parts = re.split(r'\n\s*\n', level_text)
                encounter_blocks = parts[:encounters_per_level]
            
            for j, encounter_text in enumerate(encounter_blocks[:encounters_per_level]):
                encounter = {
                    "id": j + 1,
                    "description": encounter_text.strip(),
                    "creatures": []
                }
                
                # Try to extract encounter name
                name_match = re.search(r"^([^\n:]+)", encounter_text)
                if name_match:
                    encounter["name"] = name_match.group(1).strip()
                else:
                    encounter["name"] = f"Encounter {j+1}"
                
                # Try to find creatures
                creature_pattern = re.compile(r"(?:[-•*]\s*|^\d+[\.x]\s*)(\d+)?(?:\s*[x×]\s*)?([^(,]+)(?:\s*\((?:CR\s*)?([^)]+)\))?", re.MULTILINE)
                creature_matches = creature_pattern.findall(encounter_text)
                
                for match in creature_matches:
                    quantity_str, name, cr_str = match
                    quantity = int(quantity_str) if quantity_str else 1
                    creature = {
                        "name": name.strip(),
                        "quantity": quantity
                    }
                    
                    # Try to parse CR
                    if cr_str:
                        try:
                            cr_cleaned = cr_str.strip().lower()
                            if cr_cleaned in ["1/8", "1/4", "1/2"]:
                                creature["cr"] = eval(cr_cleaned)
                            else:
                                creature["cr"] = float(cr_cleaned)
                        except:
                            creature["cr"] = 0
                            
                    encounter["creatures"].append(creature)
                
                level_data["encounters"].append(encounter)
            
            progression["levels"].append(level_data)
        
        return progression

    def _parse_complementary_suggestions(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for complementary creature suggestions."""
        complementary_creatures = []
        
        # Try to find creature suggestion blocks
        suggestion_blocks = re.findall(r"(?:\d+\.\s+|[-•*]\s+)([^\n]+(?:\n(?!(?:\d+\.\s+|[-•*]\s+))[^\n]+)*)", response)
        
        if not suggestion_blocks:
            # Try another pattern
            suggestion_blocks = re.findall(r"([^\n]+\(CR [^\)]+\)[^\n]+(?:\n(?![^\n]+\(CR [^\)]+\))[^\n]+)*)", response)
        
        for block in suggestion_blocks:
            suggestion = {
                "description": block.strip(),
                "synergy": ""
            }
            
            # Try to extract creature name and CR
            name_cr_match = re.search(r"([^(]+)(?:\((?:CR\s*)?([^)]+)\))?", block)
            if name_cr_match:
                suggestion["name"] = name_cr_match.group(1).strip()
                if name_cr_match.group(2):
                    cr_str = name_cr_match.group(2).strip().lower()
                    try:
                        if cr_str in ["1/8", "1/4", "1/2"]:
                            suggestion["cr"] = eval(cr_str)
                        else:
                            suggestion["cr"] = float(cr_str)
                    except:
                        suggestion["cr"] = 0
            
            # Try to extract quantities if mentioned
            quantity_match = re.search(r"(?:group of|x\s*|×\s*)(\d+)", block, re.IGNORECASE)
            if quantity_match:
                suggestion["quantity"] = int(quantity_match.group(1))
            else:
                # Default quantity
                suggestion["quantity"] = 2
            
            # Try to extract synergy description
            synergy_lines = []
            for line in block.split("\n")[1:]:
                if line.strip() and not re.match(r"^[-•*]", line):
                    synergy_lines.append(line.strip())
            
            if synergy_lines:
                suggestion["synergy"] = " ".join(synergy_lines)
            
            complementary_creatures.append(suggestion)
        
        return complementary_creatures
        