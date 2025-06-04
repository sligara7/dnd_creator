import re
import json
from typing import Dict, List, Any, Optional, Union, Tuple

from backend.core.services.ollama_service import OllamaService

class LLMPersonalityAdvisor:
    """
    LLM-powered advisor for D&D character personality development and backstory generation.
    Uses Ollama/Llama 3 to enhance character creation with AI-generated content.
    """

    def __init__(self):
        """Initialize the LLM advisor with Ollama service and prompt templates"""
        self.ollama_service = OllamaService()
        
        # System message for D&D personality generation
        self.system_message = (
            "You are a D&D 5e (2024 Edition) expert assistant helping create compelling and "
            "rule-consistent character personalities and backstories. Provide creative but "
            "setting-appropriate responses."
        )

    def generate_options_for_background(self, background: str, include_custom_options: bool = False) -> Dict[str, List[str]]:
        """
        Generate personality options for a specific background.
        
        Args:
            background (str): The character background (e.g., 'hermit', 'noble')
            include_custom_options (bool): Whether to include unique AI-generated options
            
        Returns:
            dict: Dictionary with traits, ideals, bonds, and flaws lists
        """
        # Standard D&D options based on background
        standard_options = self._get_standard_options(background)
        
        if not include_custom_options:
            return standard_options
        
        # Generate unique personality traits using LLM
        prompt = f"Create three unique personality traits, three ideals, three bonds, and three flaws for a character with the {background} background that go beyond standard D&D options but remain appropriate for the setting. Format your response as clean JSON with the keys 'traits', 'ideals', 'bonds', and 'flaws'."
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            # Extract JSON from response
            custom_options = self._extract_json(response)
            # Merge standard and custom options
            result = {
                "traits": standard_options["traits"] + custom_options.get("traits", []),
                "ideals": standard_options["ideals"] + custom_options.get("ideals", []),
                "bonds": standard_options["bonds"] + custom_options.get("bonds", []),
                "flaws": standard_options["flaws"] + custom_options.get("flaws", [])
            }
            return result
        except (json.JSONDecodeError, AttributeError):
            # Fallback to standard options if JSON parsing fails
            return standard_options

    def generate_coherent_personality(self, theme: Optional[str] = None) -> Dict[str, str]:
        """
        Generate a psychologically coherent personality profile.
        
        Args:
            theme (str, optional): Central character theme (e.g., 'redemption seeker')
            
        Returns:
            dict: Coherent personality traits, ideals, bonds, and flaws
        """
        theme_text = f"with a central theme of '{theme}'" if theme else ""
        
        prompt = f"Generate a psychologically coherent D&D character personality profile {theme_text} where traits, ideals, bonds, and flaws naturally complement and reinforce each other. Return as JSON with keys 'trait', 'ideal', 'bond', and 'flaw'."
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            return self._extract_json(response)
        except (json.JSONDecodeError, AttributeError):
            # Fallback if JSON extraction fails
            return {
                "trait": "I analyze every situation before acting.",
                "ideal": "Logic. Rational thinking is the key to solving problems.",
                "bond": "I seek knowledge that was lost to time.",
                "flaw": "I overthink simple problems and miss obvious solutions."
            }

    def create_backstory(
        self, 
        character_data: Dict[str, Any], 
        backstory_length: str = "medium", 
        tone: str = "neutral", 
        key_elements_to_include: Optional[List[str]] = None
    ) -> str:
        """
        Create an AI-generated backstory for a character.
        
        Args:
            character_data (dict): Character information (species, class, background, etc.)
            backstory_length (str): Length preference ('short', 'medium', 'long')
            tone (str): Emotional tone (e.g., 'heroic', 'tragic', 'bittersweet')
            key_elements_to_include (list, optional): Specific elements to include
            
        Returns:
            str: Generated character backstory
        """
        # Set word count based on length preference
        word_counts = {"short": 150, "medium": 300, "long": 600}
        word_count = word_counts.get(backstory_length.lower(), 300)
        
        # Extract character elements
        species = character_data.get("species", "humanoid")
        character_class = character_data.get("class", "adventurer")
        background = character_data.get("background", "wanderer")
        
        elements_text = ""
        if key_elements_to_include:
            elements_text = f" Include these key elements: {', '.join(key_elements_to_include)}."
        
        prompt = (
            f"Write a {word_count}-word backstory for a {species} {character_class} "
            f"with the {background} background. The tone should be {tone}.{elements_text}"
        )
        
        # Add personality traits if available
        if "personality" in character_data:
            p = character_data["personality"]
            prompt += f"\n\nIncorporate these personality elements:"
            if "trait" in p: prompt += f"\nTrait: {p['trait']}"
            if "ideal" in p: prompt += f"\nIdeal: {p['ideal']}"
            if "bond" in p: prompt += f"\nBond: {p['bond']}"
            if "flaw" in p: prompt += f"\nFlaw: {p['flaw']}"
            
        prompt += "\n\nThe backstory should explain their motivations, formative experiences, and how they acquired their abilities."
        
        # Add alignment guidance if available
        if "alignment" in character_data:
            prompt += f"\n\nThe character's alignment is {character_data['alignment']}. The backstory should reflect this alignment through their actions and values."
            
        return self.ollama_service.generate_text(prompt, self.system_message)

    def validate_backstory_against_rules(
        self, 
        backstory: str, 
        setting_name: str = "Generic Fantasy", 
        check_for_consistency: bool = True,
        suggest_improvements: bool = False
    ) -> Dict[str, Any]:
        """
        Validate backstory for rule consistency and setting compatibility.
        
        Args:
            backstory (str): The character backstory to validate
            setting_name (str): D&D setting name
            check_for_consistency (bool): Whether to check for internal consistency
            suggest_improvements (bool): Whether to include improvement suggestions
            
        Returns:
            dict: Validation results including is_valid and reason
        """
        consistency_text = " Check for internal consistency and character coherence." if check_for_consistency else ""
        improvements_text = " Suggest specific improvements to address any issues found." if suggest_improvements else ""
        
        prompt = (
            f"Review this character backstory for a D&D character in the {setting_name} setting:\n\n"
            f"{backstory}\n\n"
            f"Evaluate if it contains any elements that contradict D&D 5e (2024) rules, lore, or setting.{consistency_text}{improvements_text} "
            f"Return a JSON object with 'is_valid' (boolean), 'reason' (string explaining any issues or 'Backstory is valid'), "
            f"and 'suggestions' (array of improvement suggestions, empty if none)."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            result = self._extract_json(response)
            return {
                "is_valid": result.get("is_valid", True),
                "reason": result.get("reason", "Backstory is valid"),
                "suggestions": result.get("suggestions", [])
            }
        except (json.JSONDecodeError, AttributeError):
            # Default response if JSON extraction fails
            return {
                "is_valid": True,
                "reason": "Backstory validation completed",
                "suggestions": []
            }

    def extract_backstory_hooks(
        self, 
        backstory: str,
        hook_count: int = 3,
        hook_types: List[str] = None,
        detail_level: str = "summary"
    ) -> List[Dict[str, str]]:
        """
        Extract narrative hooks from a character backstory.
        
        Args:
            backstory (str): The character backstory
            hook_count (int): Number of hooks to extract
            hook_types (list): Types of hooks to extract (ally, enemy, mystery, goal)
            detail_level (str): Level of detail ('summary', 'detailed')
            
        Returns:
            list: List of hook dictionaries with type and description
        """
        if hook_types is None:
            hook_types = ['ally', 'enemy', 'mystery', 'goal']
        
        hook_types_str = ", ".join(hook_types)
        detail_instruction = "brief summary of" if detail_level == "summary" else "detailed description of"
        
        prompt = (
            f"From this character backstory:\n\n{backstory}\n\n"
            f"Extract {hook_count} narrative elements that could become personal quests or campaign ties. "
            f"For each element, identify the hook type ({hook_types_str}) and provide a {detail_instruction} "
            f"how it could be developed into an adventure. Format as JSON array with objects containing 'type' and 'description'."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            result = self._extract_json(response)
            if isinstance(result, list):
                return result[:hook_count]
            else:
                return result.get("hooks", [])[:hook_count]
        except (json.JSONDecodeError, AttributeError):
            # Default response if JSON extraction fails
            return [{"type": "mystery", "description": "Unresolved element from character's past"}]
    
    def generate_personality_evolution(
        self, 
        original_personality: Dict[str, str], 
        significant_events: List[str]
    ) -> Dict[str, str]:
        """
        Generate how a character's personality might evolve after significant events.
        
        Args:
            original_personality (dict): Original personality traits
            significant_events (list): List of significant events that impacted character
            
        Returns:
            dict: Updated personality traits reflecting character growth
        """
        events_text = "\n".join([f"- {event}" for event in significant_events])
        
        prompt = (
            f"A D&D character with the following personality traits has experienced significant events:\n\n"
            f"Original Personality:\n"
            f"- Trait: {original_personality.get('trait', 'Unknown')}\n"
            f"- Ideal: {original_personality.get('ideal', 'Unknown')}\n"
            f"- Bond: {original_personality.get('bond', 'Unknown')}\n"
            f"- Flaw: {original_personality.get('flaw', 'Unknown')}\n\n"
            f"Significant Events:\n{events_text}\n\n"
            f"How would these events change the character's personality traits? Return JSON with updated 'trait', 'ideal', 'bond', and 'flaw'."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            result = self._extract_json(response)
            # Ensure all original keys are preserved if new ones aren't generated
            for key in original_personality:
                if key not in result:
                    result[key] = original_personality[key]
            return result
        except (json.JSONDecodeError, AttributeError):
            return original_personality
    
    def create_connected_npc(
        self, 
        character_backstory: str, 
        npc_role: str = "ally",
        relationship_strength: str = "strong"
    ) -> Dict[str, Any]:
        """
        Create an NPC with meaningful connections to a character's backstory.
        
        Args:
            character_backstory (str): Player character's backstory
            npc_role (str): Role of NPC (ally, rival, mentor, etc.)
            relationship_strength (str): How strong the connection is
            
        Returns:
            dict: NPC details including name, description, connection, and plot hooks
        """
        prompt = (
            f"Based on this character backstory:\n\n{character_backstory}\n\n"
            f"Create a detailed NPC who has a {relationship_strength} connection to the character "
            f"and serves as a {npc_role}. Return a JSON object with 'name', 'species', 'description', "
            f"'connection' (how they know the character), 'personality', and 'plot_hooks' (array of "
            f"potential storylines involving this NPC)."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            return self._extract_json(response)
        except (json.JSONDecodeError, AttributeError):
            # Default response if JSON extraction fails
            return {
                "name": "Unknown NPC",
                "species": "Human",
                "description": "A mysterious figure from the character's past",
                "connection": "They share a history",
                "personality": "Reserved but loyal",
                "plot_hooks": ["The NPC requires assistance with a personal quest"]
            }

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        # Find JSON pattern in response
        json_match = re.search(r'```json(.*?)```', text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1).strip()
        else:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0).strip()
            else:
                json_text = text
        
        # Clean up potential markdown and whitespace
        json_text = re.sub(r'^\s*```.*\n', '', json_text)
        json_text = re.sub(r'\n\s*```\s*$', '', json_text)
        
        return json.loads(json_text)
    
    def _get_standard_options(self, background: str) -> Dict[str, List[str]]:
        """Get standard D&D personality options for a background"""
        # This would ideally be loaded from a database or file
        # Simplified example for demonstration
        standard_options = {
            "acolyte": {
                "traits": ["I quote sacred texts", "I find guidance in prayer"],
                "ideals": ["Tradition", "Faith", "Charity"],
                "bonds": ["I would die for my temple", "My mentor is everything to me"],
                "flaws": ["I judge others harshly", "I trust religious authority blindly"]
            },
            "criminal": {
                "traits": ["I always have a plan", "I'm suspicious of everyone"],
                "ideals": ["Freedom", "Greed", "People"],
                "bonds": ["I'm loyal to my crew", "I have a debt to repay"],
                "flaws": ["I can't resist a con", "I run from authority"]
            },
            "hermit": {
                "traits": ["I speak rarely but precisely", "I connect everything to a grand theory"],
                "ideals": ["Greater Good", "Self-Knowledge", "Solitude"],
                "bonds": ["My isolation holds a powerful secret", "My writings contain important insights"],
                "flaws": ["I'm oblivious to etiquette", "I distrust strangers"]
            },
            # Default for unknown backgrounds
            "default": {
                "traits": ["I'm always optimistic", "I carefully plan everything"],
                "ideals": ["Balance", "Aspiration", "Redemption"],
                "bonds": ["I protect those who cannot protect themselves", "I seek to restore what was lost"],
                "flaws": ["I have a weakness I'm ashamed of", "I trust too easily"]
            }
        }
        
        return standard_options.get(background.lower(), standard_options["default"])