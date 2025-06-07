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

    def adapt_fictional_character(
        self,
        character_name: str,
        source_media: str,
        adaptation_approach: str = "faithful"
    ) -> Dict[str, Any]:
        """
        Adapt a character from fiction/pop culture to D&D while preserving their essence.
        
        Args:
            character_name: Name of the fictional character (e.g., "Thor", "Wonder Woman")
            source_media: Source of the character (e.g., "Marvel Comics", "Game of Thrones")
            adaptation_approach: How closely to follow the original ("faithful", "inspired", "reimagined")
            
        Returns:
            Dict containing personality traits, backstory elements, and character hooks
        """
        approach_instructions = {
            "faithful": "Create a faithfully accurate adaptation that closely follows the source material.",
            "inspired": "Create an adaptation inspired by the character but with some D&D-specific modifications.",
            "reimagined": "Reimagine the character within D&D while keeping their core essence and themes."
        }
        
        instruction = approach_instructions.get(adaptation_approach.lower(), approach_instructions["inspired"])
        
        prompt = (
            f"Adapt {character_name} from {source_media} to a D&D character. {instruction}\n\n"
            f"Include the following in your JSON response:\n"
            f"- 'character_class': Recommended D&D class(es) and subclass(es)\n"
            f"- 'species': Appropriate D&D species/race\n" 
            f"- 'background': Suitable background\n"
            f"- 'personality': Object with trait, ideal, bond, and flaw\n"
            f"- 'abilities': Any special abilities that translate to D&D mechanics\n"
            f"- 'backstory': Brief backstory adapted to a D&D setting\n"
            f"- 'connections': Important relationships from source material translated to D&D\n"
            f"- 'iconic_elements': Key narrative elements to preserve from original character\n"
            f"- 'suggested_homebrew': Any custom elements needed to truly capture the character"
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            return self._extract_json(response)
        except (json.JSONDecodeError, AttributeError):
            # Fallback if JSON parsing fails
            return {
                "character_class": f"Based on {character_name}'s abilities, a suitable class would be determined",
                "species": "Human (or equivalent)",
                "background": "Custom",
                "personality": {
                    "trait": f"Embodies the classic traits of {character_name}",
                    "ideal": "Upholds their iconic principles",
                    "bond": f"Connected to the important elements of {character_name}'s story",
                    "flaw": "Has the characteristic weaknesses from their source material"
                },
                "backstory": f"Adaptation of {character_name}'s origin story in a fantasy setting",
                "connections": ["Major relationships adapted to D&D context"],
                "iconic_elements": ["Signature themes and motifs"]
            }

    def create_family_dynamics(
        self,
        character_data: Dict[str, Any],
        relationship_focus: List[str] = None,  # e.g., ["sibling rivalry", "parental approval"]
        family_complexity: str = "moderate",
        include_npcs: bool = True
    ) -> Dict[str, Any]:
        """
        Generate complex family relationships and dynamics for a character.
        Perfect for creating Thor/Loki type sibling relationships or complex family trees.
        
        Args:
            character_data: Base character information
            relationship_focus: Specific relationship dynamics to focus on
            family_complexity: How complex the family structure should be ("simple", "moderate", "complex")
            include_npcs: Whether to generate detailed NPC stats for family members
            
        Returns:
            Dict containing family tree, key relationships, and family history
        """
        # Set default relationship focus if none provided
        if relationship_focus is None:
            relationship_focus = ["sibling relationship", "parental influence"]
        
        # Extract relevant character info
        species = character_data.get("species", "humanoid")
        background = character_data.get("background", "")
        
        # Build complexity-based instructions
        complexity_instructions = {
            "simple": "Create a small, straightforward family with 3-4 key members",
            "moderate": "Create a medium-sized family with 5-7 members and moderate complexity",
            "complex": "Create an expansive, complex family structure with multiple branches, 8+ members, and intricate relationships"
        }
        
        complexity_text = complexity_instructions.get(family_complexity.lower(), complexity_instructions["moderate"])
        relationship_text = "Focus on these specific relationship dynamics: " + ", ".join(relationship_focus)
        
        npc_instruction = ""
        if include_npcs:
            npc_instruction = "Include detailed NPC information for key family members (personality, motivations, stats)."
        
        prompt = (
            f"Create a family structure and dynamic for a {species} character with {background} background.\n\n"
            f"{complexity_text}. {relationship_text}.\n\n"
            f"Generate a complex and narratively rich family history that could drive character development. "
            f"{npc_instruction}\n\n"
            f"Include the following in your JSON response:\n"
            f"- 'family_structure': Array of family members with relationships to character\n"
            f"- 'key_dynamics': Object mapping relationship types to their dynamic descriptions\n"
            f"- 'family_history': Significant events in family history\n"
            f"- 'secrets': Array of family secrets that could be revealed during gameplay\n"
            f"- 'influence': How family has shaped character's personality and motivations\n"
            f"- 'current_status': Current standing with each family member\n"
            f"- 'plot_hooks': Array of potential storylines involving family members"
        )
        
        if include_npcs:
            prompt += f"\n- 'npcs': Array of detailed NPC data for family members"
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            result = self._extract_json(response)
            # Ensure NPC data is included if requested but missing
            if include_npcs and "npcs" not in result:
                result["npcs"] = self._generate_family_npcs(result.get("family_structure", []))
            return result
        except (json.JSONDecodeError, AttributeError):
            # Fallback
            basic_family = {
                "family_structure": [
                    {"relation": "father", "name": "Unnamed", "status": "alive"},
                    {"relation": "mother", "name": "Unnamed", "status": "alive"},
                ],
                "key_dynamics": {"parental": "Supportive but distant"},
                "family_history": "A family with traditional values and modest background.",
                "secrets": ["A hidden past that connects to the character's future"],
                "influence": "Family values shaped the character's core beliefs.",
                "current_status": "Occasional contact but living separate lives",
                "plot_hooks": ["A family member needs help with a personal problem"]
            }
            
            if include_npcs:
                basic_family["npcs"] = self._generate_family_npcs(basic_family["family_structure"])
                
            return basic_family

    def _generate_family_npcs(self, family_structure: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Helper method to generate NPCs for family members when needed"""
        npcs = []
        for member in family_structure:
            npcs.append({
                "name": member.get("name", "Unnamed Family Member"),
                "relation": member.get("relation", "relative"),
                "personality": "Unique personality traits would be generated here",
                "goals": ["Primary motivations would be listed here"],
                "stats": "Basic NPC stats would be generated here"
            })
        return npcs

    def generate_inner_conflicts(
        self,
        character_data: Dict[str, Any],
        conflict_count: int = 2,
        conflict_depth: str = "profound"
    ) -> List[Dict[str, Any]]:
        """
        Create psychologically rich inner conflicts and moral dilemmas for the character.
        
        Args:
            character_data: Character information
            conflict_count: Number of inner conflicts to generate
            conflict_depth: Depth of conflicts ("mild", "significant", "profound")
            
        Returns:
            List of conflict objects with descriptions and roleplaying suggestions
        """
        # Extract character details
        personality = character_data.get("personality", {})
        background = character_data.get("background", "")
        character_class = character_data.get("class", "")
        
        # Adjust depth instructions
        depth_instructions = {
            "mild": "Create everyday ethical quandaries that cause minor internal tension",
            "significant": "Create meaningful moral dilemmas that challenge core beliefs",
            "profound": "Create deep philosophical conflicts that question fundamental identity and values"
        }
        
        depth_text = depth_instructions.get(conflict_depth.lower(), depth_instructions["significant"])
        
        prompt = (
            f"Generate {conflict_count} inner conflicts/moral dilemmas for a {character_class} with "
            f"a {background} background and these personality elements:\n"
            f"- Trait: {personality.get('trait', 'Unspecified')}\n"
            f"- Ideal: {personality.get('ideal', 'Unspecified')}\n"
            f"- Bond: {personality.get('bond', 'Unspecified')}\n"
            f"- Flaw: {personality.get('flaw', 'Unspecified')}\n\n"
            f"{depth_text}\n\n"
            f"For each conflict, include in a JSON array:\n"
            f"- 'name': Short name for the conflict\n"
            f"- 'description': Detailed explanation of the inner conflict\n"
            f"- 'manifestation': How this conflict manifests in behavior and decision-making\n"
            f"- 'opposing_values': The two (or more) competing values/beliefs causing tension\n"
            f"- 'triggers': Situations that intensify this conflict\n"
            f"- 'roleplaying_suggestions': How to portray this conflict during gameplay\n"
            f"- 'resolution_paths': Possible ways this conflict might be resolved"
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            result = self._extract_json(response)
            if isinstance(result, list):
                return result[:conflict_count]
            else:
                return result.get("conflicts", [])[:conflict_count]
        except (json.JSONDecodeError, AttributeError):
            # Fallback - generate basic conflicts
            return [
                {
                    "name": "Duty vs. Desire",
                    "description": "The character is torn between responsibilities and personal wants",
                    "manifestation": "Hesitation when making decisions between self-interest and obligations",
                    "opposing_values": ["Duty", "Personal freedom"],
                    "triggers": ["Being asked to sacrifice personal goals for others"],
                    "roleplaying_suggestions": "Show reluctance when asked to put duties first",
                    "resolution_paths": ["Finding a balance", "Choosing one path definitively"]
                },
                {
                    "name": "Faith vs. Experience",
                    "description": "The character's beliefs are challenged by lived experiences",
                    "manifestation": "Questioning long-held beliefs when evidence contradicts them",
                    "opposing_values": ["Faith in traditions", "Trust in personal experience"],
                    "triggers": ["Witnessing events that contradict beliefs"],
                    "roleplaying_suggestions": "Express doubt and confusion when beliefs are challenged",
                    "resolution_paths": ["Evolving beliefs", "Doubling down on faith", "Finding synthesis"]
                }
            ][:conflict_count]

    def adapt_character_across_genres(
        self,
        character_concept: str,
        origin_genre: str,  # e.g., "superhero", "sci-fi", "mythology"
        target_genre: str = "fantasy",
        retain_elements: List[str] = None  # e.g., ["powers", "relationships", "motivations"]
    ) -> Dict[str, Any]:
        """
        Adapt a character concept from one genre to another while preserving core elements.
        
        Args:
            character_concept: Brief character description
            origin_genre: Original genre of the character
            target_genre: Target genre for adaptation
            retain_elements: Which elements to preserve in the adaptation
            
        Returns:
            Dict with adapted character concept, personality, and background
        """
        if retain_elements is None:
            retain_elements = ["powers", "personality", "relationships", "core themes"]
        
        retain_text = "Specifically retain these elements: " + ", ".join(retain_elements)
        
        prompt = (
            f"Adapt this character concept from {origin_genre} genre to {target_genre} genre:\n\n"
            f"CHARACTER CONCEPT: {character_concept}\n\n"
            f"{retain_text}\n\n"
            f"Create a complete adaptation that preserves the character's essence while making them "
            f"fit naturally into the new genre. Return a JSON object with:\n"
            f"- 'adapted_concept': Brief high-level adapted character concept\n"
            f"- 'original_elements': Key elements from original character/genre\n"
            f"- 'transformed_elements': How each element transforms in new genre\n"
            f"- 'personality': Object with trait, ideal, bond, flaw\n"
            f"- 'abilities': Main capabilities and how they manifest in new genre\n"
            f"- 'background': Character history adapted to new genre\n"
            f"- 'character_hooks': Storylines that would work in new genre\n"
            f"- 'worldbuilding': Suggestions for world elements that support this character"
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            return self._extract_json(response)
        except (json.JSONDecodeError, AttributeError):
            # Fallback adaptation
            return {
                "adapted_concept": f"A {target_genre} version of '{character_concept}'",
                "original_elements": retain_elements,
                "transformed_elements": {element: f"{element.capitalize()} adapted to {target_genre}" for element in retain_elements},
                "personality": {
                    "trait": "Maintains core personality from original concept",
                    "ideal": "Primary motivation transformed to fit new genre",
                    "bond": "Key relationship adapted to new setting",
                    "flaw": "Central character flaw retained in new context"
                },
                "abilities": ["Abilities would be genre-appropriate versions of original powers"],
                "background": f"Origin story reimagined for {target_genre} setting",
                "character_hooks": ["Character arcs adapted to new genre conventions"]
            }

    def create_custom_culture(
        self,
        culture_concept: str,
        detail_level: str = "detailed",
        aspects_to_include: List[str] = None  # e.g., ["values", "traditions", "religion", "art"]
    ) -> Dict[str, Any]:
        """
        Create a detailed culture/society for characters with non-standard backgrounds.
        
        Args:
            culture_concept: Brief description of desired culture
            detail_level: How detailed the culture should be
            aspects_to_include: Cultural aspects to focus on
            
        Returns:
            Dict containing cultural details that can be referenced in character backstory
        """
        if aspects_to_include is None:
            aspects_to_include = ["values", "traditions", "religion", "social structure", "aesthetics"]
        
        # Determine detail level instructions
        detail_instructions = {
            "brief": "Provide a concise overview of essential cultural elements",
            "moderate": "Create a balanced description with moderate detail on key aspects",
            "detailed": "Develop an in-depth cultural profile with rich details on all aspects",
            "comprehensive": "Create an exhaustive cultural framework with intricate details on all aspects"
        }
        
        detail_text = detail_instructions.get(detail_level.lower(), detail_instructions["detailed"])
        aspects_text = "Focus on these cultural aspects: " + ", ".join(aspects_to_include)
        
        prompt = (
            f"Create a unique and fully realized culture based on this concept:\n\n"
            f"CULTURE CONCEPT: {culture_concept}\n\n"
            f"{detail_text}\n{aspects_text}\n\n"
            f"Design a culture that could serve as background for D&D characters but isn't restricted "
            f"to standard fantasy tropes. Make it feel authentic, internally consistent, and rich with "
            f"roleplaying potential. Return your response as a JSON object with these keys:\n"
            f"- 'name': Name of the culture\n"
            f"- 'overview': Brief high-level description\n"
            f"- 'values': Core values and beliefs\n"
            f"- 'social_structure': How society is organized\n"
            f"- 'traditions': Important customs and practices\n"
            f"- 'religion': Spiritual beliefs and practices\n"
            f"- 'aesthetics': Visual style, art, architecture, clothing\n"
            f"- 'language': Distinctive linguistic features\n"
            f"- 'coming_of_age': Rites of passage\n"
            f"- 'taboos': Forbidden actions or beliefs\n"
            f"- 'relations': How they interact with other cultures\n"
            f"- 'character_traits': Common personality traits of members\n"
            f"- 'roleplaying_tips': How to portray a character from this culture"
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            result = self._extract_json(response)
            # Ensure all requested aspects are present
            for aspect in aspects_to_include:
                if aspect not in result and aspect in ["values", "traditions", "religion", "social_structure", "aesthetics"]:
                    result[aspect] = f"The {aspect} of this culture would be developed here"
            return result
        except (json.JSONDecodeError, AttributeError):
            # Fallback culture
            return {
                "name": f"The {culture_concept.split()[0].title()} Culture",
                "overview": f"A culture based on {culture_concept}",
                "values": "Core cultural values would be detailed here",
                "social_structure": "Social hierarchy would be described here",
                "traditions": "Key traditions would be outlined here",
                "religion": "Religious practices would be explained here",
                "aesthetics": "Cultural aesthetic would be described here",
                "character_traits": ["Typical personality traits would be listed"]
            }

    def design_character_arc(
        self,
        starting_personality: Dict[str, Any],
        arc_type: str = "redemption",  # e.g., "redemption", "fall", "discovery"
        arc_length: str = "campaign",  # e.g., "session", "adventure", "campaign"
        key_milestones: int = 3
    ) -> Dict[str, Any]:
        """
        Design a character development arc with key growth moments and personality evolution.
        
        Args:
            starting_personality: Starting personality traits
            arc_type: Type of character arc
            arc_length: Expected duration of the arc
            key_milestones: Number of key milestones in the arc
            
        Returns:
            Dict with arc description, milestones, and evolved personality
        """
        # Extract personality elements
        trait = starting_personality.get("trait", "Unspecified trait")
        ideal = starting_personality.get("ideal", "Unspecified ideal")
        bond = starting_personality.get("bond", "Unspecified bond")
        flaw = starting_personality.get("flaw", "Unspecified flaw")
        
        # Common character arc types
        arc_descriptions = {
            "redemption": "Character journey from moral failing to atonement and virtue",
            "fall": "Character descent from virtue to moral corruption",
            "discovery": "Character journey of self-discovery and identity formation",
            "growth": "Character development through overcoming challenges and gaining wisdom",
            "tragedy": "Character decline through fatal flaws despite positive intentions",
            "coming_of_age": "Character transition from immaturity to greater responsibility",
            "transformation": "Character undergoes fundamental change in nature or identity"
        }
        
        arc_desc = arc_descriptions.get(arc_type.lower(), f"Custom {arc_type} character development")
        arc_length_text = arc_length.lower()
        
        prompt = (
            f"Design a {arc_type} character arc over a {arc_length_text}-length story with {key_milestones} key milestones.\n\n"
            f"Starting personality:\n"
            f"- Trait: {trait}\n"
            f"- Ideal: {ideal}\n"
            f"- Bond: {bond}\n"
            f"- Flaw: {flaw}\n\n"
            f"Create a compelling character development path that transforms these traits in a way that feels "
            f"earned and meaningful. For each milestone, describe the event, its impact, and how the character "
            f"changes. Show how personality evolves at each stage.\n\n"
            f"Return a JSON object with:\n"
            f"- 'arc_description': Overview of the character arc\n"
            f"- 'starting_point': Initial character state\n"
            f"- 'milestones': Array of {key_milestones} milestone objects with 'event', 'impact', and 'character_state'\n"
            f"- 'climax': The turning point of the arc\n"
            f"- 'resolution': Final state and outcome\n"
            f"- 'evolved_personality': Object showing final trait, ideal, bond, and flaw\n"
            f"- 'roleplay_opportunities': Suggestions for playing out this arc"
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            result = self._extract_json(response)
            
            # Ensure milestones match requested count
            if "milestones" in result and len(result["milestones"]) != key_milestones:
                # Trim excess or add generic milestones
                if len(result["milestones"]) > key_milestones:
                    result["milestones"] = result["milestones"][:key_milestones]
                else:
                    for i in range(len(result["milestones"]), key_milestones):
                        result["milestones"].append({
                            "event": f"Milestone {i+1}",
                            "impact": "Character faces a significant challenge",
                            "character_state": "Character grows in response to challenge"
                        })
                        
            return result
        except (json.JSONDecodeError, AttributeError):
            # Fallback arc
            milestones = []
            for i in range(key_milestones):
                milestones.append({
                    "event": f"Milestone {i+1}",
                    "impact": f"Character experiences a significant event related to {arc_type}",
                    "character_state": "Character's perspective shifts in response"
                })
                
            return {
                "arc_description": arc_desc,
                "starting_point": "Character begins with initial personality traits",
                "milestones": milestones,
                "climax": f"Character faces defining moment in their {arc_type} arc",
                "resolution": "Character completes their transformation",
                "evolved_personality": {
                    "trait": "Evolution of original trait",
                    "ideal": "Evolution of original ideal",
                    "bond": "Evolution of original bond",
                    "flaw": "Evolution of original flaw"
                },
                "roleplay_opportunities": [
                    "Key moments to roleplay during this character arc"
                ]
            }

    def integrate_iconic_abilities(
        self,
        abilities: List[str],
        personality_impact: str = "significant",
        narrative_focus: str = "balanced"  # "power-focused", "balanced", "character-focused"
    ) -> Dict[str, Any]:
        """
        Integrate iconic abilities/powers into personality traits and backstory.
        Perfect for adapting characters like Thor with distinctive powers.
        
        Args:
            abilities: List of special abilities/powers
            personality_impact: How much the abilities influence personality
            narrative_focus: Balance between power emphasis and character development
            
        Returns:
            Dict with personality traits influenced by abilities and backstory hooks
        """
        abilities_text = "\n".join([f"- {ability}" for ability in abilities])
        impact_levels = {
            "minimal": "Abilities have little effect on personality",
            "moderate": "Abilities somewhat shape personality and worldview",
            "significant": "Abilities strongly influence character identity and behavior",
            "defining": "Abilities completely define who the character is and how they see the world"
        }
        
        focus_types = {
            "power-focused": "Emphasize how these abilities make the character special and powerful",
            "balanced": "Balance between power fantasy and character development",
            "character-focused": "Focus on the psychological and social impacts of these abilities"
        }
        
        impact_text = impact_levels.get(personality_impact.lower(), impact_levels["significant"])
        focus_text = focus_types.get(narrative_focus.lower(), focus_types["balanced"])
        
        prompt = (
            f"Integrate these special abilities into a character's personality and backstory:\n\n"
            f"ABILITIES:\n{abilities_text}\n\n"
            f"GUIDANCE:\n- {impact_text}\n- {focus_text}\n\n"
            f"Show how these powers would realistically shape someone's identity, worldview, "
            f"relationships, and behavior. Create a psychologically believable integration of "
            f"these abilities into a D&D character. Return a JSON object with:\n"
            f"- 'personality_traits': How abilities shape character traits\n"
            f"- 'abilities_origin': How character acquired these abilities\n"
            f"- 'worldview': How abilities influence character's perspective\n"
            f"- 'relationships': How abilities affect interactions with others\n"
            f"- 'psychological_effects': Mental/emotional impacts of having these abilities\n"
            f"- 'narrative_hooks': Storylines that arise from these abilities\n"
            f"- 'roleplay_suggestions': How to portray a character with these abilities\n"
            f"- 'character_growth': How abilities create opportunities for development"
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            return self._extract_json(response)
        except (json.JSONDecodeError, AttributeError):
            # Fallback integration
            return {
                "personality_traits": ["Character traits influenced by abilities"],
                "abilities_origin": "How the character acquired these powers",
                "worldview": "How having these abilities shapes the character's perspective",
                "relationships": "How these abilities affect interactions with others",
                "psychological_effects": "Mental and emotional impacts of having these abilities",
                "narrative_hooks": ["Story opportunities created by these abilities"],
                "roleplay_suggestions": ["Ideas for portraying these abilities in-game"],
                "character_growth": "Development path related to mastering these abilities"
            }

    def generate_philosophical_outlook(
        self,
        character_data: Dict[str, Any],
        depth: str = "moderate",  # "simple", "moderate", "complex"
        influences: List[str] = None  # e.g., ["military training", "religious upbringing"]
    ) -> Dict[str, str]:
        """
        Generate a character's philosophical outlook or worldview.
        
        Args:
            character_data: Character information
            depth: Depth of philosophical development
            influences: Factors that influenced the character's worldview
            
        Returns:
            Dict containing philosophical principles, views on key concepts, and quotes
        """
        # Set default influences if none provided
        if influences is None:
            influences = []
            if "background" in character_data:
                influences.append(f"{character_data['background']} background")
            if "class" in character_data:
                influences.append(f"{character_data['class']} training")
        
        # Extract character elements
        background = character_data.get("background", "")
        character_class = character_data.get("class", "")
        alignment = character_data.get("alignment", "")
        personality = character_data.get("personality", {})
        
        # Determine depth of philosophical exploration
        depth_levels = {
            "simple": "Create a straightforward worldview with clear principles",
            "moderate": "Develop a nuanced philosophy with some complexity and internal tensions",
            "complex": "Craft a sophisticated philosophical framework with depth, nuance, and potential contradictions"
        }
        
        depth_instruction = depth_levels.get(depth.lower(), depth_levels["moderate"])
        influences_text = ""
        if influences:
            influences_text = "These factors influenced the worldview: " + ", ".join(influences)
        
        prompt = (
            f"Create a philosophical worldview for a {character_class} character with a {background} background "
            f"and {alignment} alignment.\n\n"
            f"Personality elements:\n"
            f"- Trait: {personality.get('trait', 'Not specified')}\n"
            f"- Ideal: {personality.get('ideal', 'Not specified')}\n"
            f"- Bond: {personality.get('bond', 'Not specified')}\n"
            f"- Flaw: {personality.get('flaw', 'Not specified')}\n\n"
            f"{depth_instruction}. {influences_text}\n\n"
            f"Return a JSON object with:\n"
            f"- 'core_philosophy': Central worldview in one sentence\n"
            f"- 'principles': Array of guiding philosophical principles\n"
            f"- 'perspective': Object with views on concepts like duty, honor, truth, etc.\n"
            f"- 'moral_framework': How the character distinguishes right from wrong\n"
            f"- 'influences': Factors that shaped this philosophy\n"
            f"- 'contradictions': Internal tensions or inconsistencies\n"
            f"- 'quotes': Array of quotes that express this philosophy\n"
            f"- 'growth_potential': How this worldview might evolve"
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            return self._extract_json(response)
        except (json.JSONDecodeError, AttributeError):
            # Fallback philosophy
            return {
                "core_philosophy": "A philosophical outlook based on character background and class",
                "principles": ["Primary philosophical principles would be listed here"],
                "perspective": {
                    "duty": "Character's view on duty and obligation",
                    "honor": "Character's concept of honor",
                    "truth": "Character's relationship with truth"
                },
                "moral_framework": "Character's approach to ethical decisions",
                "influences": influences,
                "contradictions": "Internal philosophical tensions",
                "quotes": ["Characteristic quotes would appear here"],
                "growth_potential": "How this philosophy might evolve over time"
            }

    def create_multiverse_variants(
        self,
        base_character: Dict[str, Any],
        variant_count: int = 2,
        divergence_point: str = None  # A specific event that caused timeline divergence
    ) -> List[Dict[str, Any]]:
        """
        Create multiverse variants of a character (what-if scenarios).
        Perfect for exploring alternate versions like Thor variants.
        
        Args:
            base_character: The original character data
            variant_count: Number of variants to create
            divergence_point: Event where timeline split (or None for random)
            
        Returns:
            List of character variants with altered personalities and backstories
        """
        # Extract character elements
        name = base_character.get("name", "Character")
        species = base_character.get("species", "humanoid")
        character_class = base_character.get("class", "")
        background = base_character.get("background", "")
        personality = base_character.get("personality", {})
        backstory = base_character.get("backstory", "Character has a history")
        
        # Prepare divergence point text
        divergence_text = ""
        if divergence_point:
            divergence_text = f"All variants diverge from the base timeline at this specific event: {divergence_point}"
        else:
            divergence_text = "Create different divergence points for each variant that would significantly alter the character's development"
        
        prompt = (
            f"Create {variant_count} multiverse variants of this character:\n\n"
            f"BASE CHARACTER:\n"
            f"- Name: {name}\n"
            f"- Species: {species}\n"
            f"- Class: {character_class}\n"
            f"- Background: {background}\n"
            f"- Trait: {personality.get('trait', 'Not specified')}\n"
            f"- Ideal: {personality.get('ideal', 'Not specified')}\n"
            f"- Bond: {personality.get('bond', 'Not specified')}\n"
            f"- Flaw: {personality.get('flaw', 'Not specified')}\n"
            f"- Backstory Summary: {backstory[:200]}...\n\n"
            f"{divergence_text}\n\n"
            f"Make each variant distinctly different while maintaining core character essence. "
            f"These should feel like multiverse versions that took different paths. "
            f"Return a JSON array of variant objects, each containing:\n"
            f"- 'variant_name': Name for this variant (can include title/epithet)\n"
            f"- 'divergence_point': What changed in their timeline\n"
            f"- 'class': Class of this variant (can differ from original)\n"
            f"- 'appearance': How this variant looks\n"
            f"- 'personality': Object with trait, ideal, bond, flaw\n"
            f"- 'key_differences': Major differences from base character\n"
            f"- 'abilities': Special abilities of this variant\n"
            f"- 'backstory': Brief backstory of this variant's life\n"
            f"- 'potential_role': How this variant might appear in a campaign"
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            result = self._extract_json(response)
            if isinstance(result, list):
                return result[:variant_count]
            else:
                return result.get("variants", [])[:variant_count]
        except (json.JSONDecodeError, AttributeError):
            # Fallback variants
            variants = []
            variant_types = ["heroic", "villainous", "tragic", "comic"]
            
            for i in range(min(variant_count, len(variant_types))):
                variant_type = variant_types[i]
                variants.append({
                    "variant_name": f"{name} the {variant_type.capitalize()}",
                    "divergence_point": f"A key moment where character took a {variant_type} turn",
                    "class": character_class,
                    "appearance": f"Appearance reflecting {variant_type} nature",
                    "personality": {
                        "trait": f"Trait adapted to {variant_type} version",
                        "ideal": f"Ideal adapted to {variant_type} version",
                        "bond": f"Bond adapted to {variant_type} version",
                        "flaw": f"Flaw adapted to {variant_type} version"
                    },
                    "key_differences": [f"How this {variant_type} variant differs from the base character"],
                    "abilities": [f"Abilities reflecting {variant_type} development"],
                    "backstory": f"Brief backstory for {variant_type} variant",
                    "potential_role": f"How this {variant_type} variant might appear in a campaign"
                })
                
            return variants