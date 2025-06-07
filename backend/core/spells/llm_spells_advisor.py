import re
import json
from typing import List, Dict, Any, Optional, Union
from backend.core.ollama_service import OllamaService

class LLMSpellsAdvisor:
    """
    Provides AI-enhanced spell recommendations and creative spell insights
    based on character concept, background, personality, and playstyle.
    """
    
    def __init__(self, llm_service=None, cache_enabled=True):
        """
        Initialize the LLM Spells Advisor.
        
        Args:
            llm_service: Custom LLM service. Uses OllamaService if None.
            cache_enabled: Whether to cache LLM responses for common queries.
        """
        self.llm_service = llm_service if llm_service else OllamaService()
        self.cache_enabled = cache_enabled
        self.response_cache = {}
        
    def suggest_thematic_spells(self, 
                              character_data: Dict[str, Any], 
                              spell_level_range: Union[str, List[int]] = "all",
                              count: int = 5) -> Dict[str, Any]:
        """
        Suggest spells that resonate with the character's nature, background, and concept.
        
        Args:
            character_data: Dictionary containing character information
            spell_level_range: Range of spell levels to consider ("all", "cantrips", 
                              or list of specific levels)
            count: Number of spells to suggest
            
        Returns:
            Dictionary with suggested spells and explanation of thematic connections
        """
        # Extract relevant character information
        char_class = character_data.get("class", {}).get("name", "unknown")
        level = character_data.get("level", 1)
        personality = character_data.get("personality", {})
        traits = personality.get("traits", [])
        ideals = personality.get("ideals", "")
        bonds = personality.get("bonds", "")
        flaws = personality.get("flaws", "")
        background = character_data.get("background", {}).get("name", "")
        species = character_data.get("species", {}).get("name", "")
        
        # Build context for LLM
        context = f"Character Class: {char_class} (Level {level})\n"
        context += f"Species: {species}\n"
        context += f"Background: {background}\n"
        
        if traits:
            context += f"Personality Traits: {', '.join(traits)}\n"
        if ideals:
            context += f"Ideals: {ideals}\n"
        if bonds:
            context += f"Bonds: {bonds}\n"
        if flaws:
            context += f"Flaws: {flaws}\n"
            
        # Handle spell level range
        if spell_level_range == "cantrips":
            context += "Spell Level Range: Cantrips only\n"
        elif spell_level_range == "all":
            max_spell_level = (level + 1) // 2
            context += f"Spell Level Range: Cantrips to level {max_spell_level}\n"
        else:
            level_str = ", ".join(str(l) for l in spell_level_range)
            context += f"Spell Level Range: {level_str}\n"
            
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "thematic_spells",
            context + f"\nSuggest {count} spells that would thematically resonate with this character's nature, " +
            "background, personality, and concept. For each spell, explain how it connects to " +
            "the character's identity and how it might be flavored or customized to better fit them. " +
            f"Only include spells available to a {char_class} of this level. " +
            "Include a mix of combat, utility, and roleplay-focused spells."
        )
        
        # Get LLM response
        response = self._get_llm_response("thematic_spells", prompt, character_data)
        
        # Parse the response
        spell_suggestions = self._parse_spell_suggestions(response)
        
        return {
            "suggestions": spell_suggestions,
            "raw_response": response
        }
        
    def get_creative_spell_uses(self, 
                              spell_name: str,
                              character_data: Optional[Dict[str, Any]] = None,
                              count: int = 5) -> Dict[str, Any]:
        """
        Provide creative examples of how a spell could be used beyond its obvious applications.
        
        Args:
            spell_name: Name of the spell
            character_data: Optional character data to personalize suggestions
            count: Number of creative uses to suggest
            
        Returns:
            Dictionary with creative uses and explanations
        """
        # Build context for LLM
        context = f"Spell: {spell_name}\n"
        
        if character_data:
            char_class = character_data.get("class", {}).get("name", "unknown")
            background = character_data.get("background", {}).get("name", "")
            context += f"Character Class: {char_class}\n"
            context += f"Background: {background}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "creative_uses",
            context + f"\nSuggest {count} creative ways to use {spell_name} beyond its " +
            "obvious applications. Focus on unexpected utility, creative problem-solving, " +
            "social situations, exploration challenges, and unusual combat tactics. " +
            "Explain how each use works within the spell's actual mechanics and rules, " +
            "without changing the fundamental nature of the spell."
        )
        
        # Get LLM response
        response = self._get_llm_response("creative_uses", prompt, {"spell_name": spell_name})
        
        # Parse the response
        creative_uses = self._parse_creative_uses(response)
        
        return {
            "creative_uses": creative_uses,
            "raw_response": response
        }
    
    def recommend_class_spells(self, 
                             class_name: str, 
                             level: int, 
                             character_background: Optional[str] = None,
                             playstyle: Optional[str] = None,
                             species: Optional[str] = None,
                             focus_areas: Optional[List[str]] = None,
                             count: int = 8) -> Dict[str, Any]:
        """
        Recommend spells for a class, considering background, playstyle, and species.
        
        Args:
            class_name: Character class
            level: Character level
            character_background: Character's background
            playstyle: Desired playstyle (e.g., "controller", "blaster", "support")
            species: Character's species
            focus_areas: Areas to focus on (e.g., ["combat", "social", "utility"])
            count: Number of spells to recommend
            
        Returns:
            Dictionary with recommended spells and explanations
        """
        # Build context for LLM
        context = f"Character Class: {class_name} (Level {level})\n"
        
        if character_background:
            context += f"Background: {character_background}\n"
            
        if species:
            context += f"Species: {species}\n"
            
        if playstyle:
            context += f"Playstyle Focus: {playstyle}\n"
            
        if focus_areas:
            context += f"Focus Areas: {', '.join(focus_areas)}\n"
            
        # Calculate maximum spell level
        max_spell_level = min((level + 1) // 2, 9)
        context += f"Available Spell Levels: Cantrips to level {max_spell_level}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "class_spells",
            context + f"\nRecommend {count} spells for a {class_name} of level {level} " +
            f"{'with a background as a ' + character_background if character_background else ''} " +
            f"{'who focuses on ' + playstyle if playstyle else ''}. " +
            "Include a balanced mix of spells across available levels. " +
            "For each spell, explain why it would be particularly effective or thematic " +
            "for this character concept and how it aligns with their background and focus. " +
            f"{'Focus especially on spells useful for: ' + ', '.join(focus_areas) if focus_areas else ''}"
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "class_spells", 
            prompt, 
            {"class": class_name, "level": level, "background": character_background}
        )
        
        # Parse the response
        spell_recommendations = self._parse_spell_recommendations(response)
        
        return {
            "recommendations": spell_recommendations,
            "raw_response": response
        }
    
    def explain_spell_save_dc_implications(self, 
                                         dc: int, 
                                         character_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Explain the tactical implications of a character's spell save DC.
        
        Args:
            dc: Spell save DC value
            character_data: Optional character data
            
        Returns:
            Dictionary with tactical implications and explanations
        """
        # Build context for LLM
        context = f"Spell Save DC: {dc}\n"
        
        if character_data:
            char_class = character_data.get("class", {}).get("name", "unknown")
            level = character_data.get("level", 1)
            context += f"Character Class: {char_class} (Level {level})\n"
            
            # If we have information about their spell list, include it
            if "known_spells" in character_data:
                save_spells = [spell for spell in character_data.get("known_spells", []) 
                              if "saving throw" in spell.get("description", "").lower()]
                if save_spells:
                    context += "Sample save spells known: "
                    context += ", ".join(spell.get("name", "") for spell in save_spells[:5])
                    context += "\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "dc_implications",
            context + f"\nExplain the tactical implications of having a spell save DC of {dc}. " +
            "Include analysis of:\n" +
            "1. How effective this DC is against different types of creatures and their typical saving throw bonuses\n" +
            "2. Which saving throws tend to be weaker for different enemy types\n" +
            "3. Strategic considerations for spell selection based on this DC\n" +
            "4. How this DC compares to what's typical for this level\n" +
            "5. Tactical advice for maximizing the impact of spells requiring saving throws"
        )
        
        # Get LLM response
        response = self._get_llm_response("dc_implications", prompt, {"dc": dc})
        
        # Parse the response
        implications = self._parse_tactical_implications(response)
        
        return {
            "implications": implications,
            "raw_response": response
        }
    
    def compare_spell_attacks_vs_saves(self, 
                                     attack_bonus: int, 
                                     save_dc: int,
                                     character_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compare the advantages of spell attacks vs. saving throw spells with the given modifiers.
        
        Args:
            attack_bonus: Spell attack bonus
            save_dc: Spell save DC
            character_data: Optional character data
            
        Returns:
            Dictionary with comparison analysis and recommendations
        """
        # Build context for LLM
        context = f"Spell Attack Bonus: +{attack_bonus}\n"
        context += f"Spell Save DC: {save_dc}\n"
        
        if character_data:
            char_class = character_data.get("class", {}).get("name", "unknown")
            level = character_data.get("level", 1)
            context += f"Character Class: {char_class} (Level {level})\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "attack_vs_save",
            context + f"\nCompare the advantages and disadvantages of spells requiring attack rolls " +
            f"(with a +{attack_bonus} bonus) versus spells requiring saving throws (with a DC of {save_dc}). " +
            "Include analysis of:\n" +
            "1. Mathematical probability comparisons against different enemy types\n" +
            "2. Tactical situations where attack spells are superior\n" +
            "3. Situations where saving throw spells are better choices\n" +
            "4. How advantage/disadvantage affects these calculations\n" +
            "5. Specific enemy types that are particularly vulnerable to one approach or the other\n" +
            "6. Recommendations for balancing attack and save spells in a character's repertoire"
        )
        
        # Get LLM response
        response = self._get_llm_response("attack_vs_save", prompt, {"attack": attack_bonus, "dc": save_dc})
        
        # Parse the response
        comparison = self._parse_comparison_analysis(response)
        
        return {
            "comparison": comparison,
            "raw_response": response
        }
    
    def suggest_prepared_spells(self, 
                              class_name: str, 
                              level: int, 
                              ability_score: int,
                              adventure_context: Optional[str] = None,
                              known_spells: Optional[List[str]] = None,
                              party_composition: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Suggest an optimal balance of prepared spells for an upcoming adventure.
        
        Args:
            class_name: Character class
            level: Character level
            ability_score: Spellcasting ability score
            adventure_context: Description of upcoming adventure/environment
            known_spells: List of all spells the character knows
            party_composition: List of other party members' classes
            
        Returns:
            Dictionary with prepared spell recommendations and explanation
        """
        # Calculate prepared spells limit
        modifier = (ability_score - 10) // 2
        prepared_limit = modifier + level
        
        # Build context for LLM
        context = f"Character Class: {class_name} (Level {level})\n"
        context += f"Prepared Spell Limit: {prepared_limit} spells\n"
        
        if adventure_context:
            context += f"Adventure Context: {adventure_context}\n"
            
        if known_spells:
            context += f"Known Spells: {', '.join(known_spells)}\n"
            
        if party_composition:
            context += f"Party Composition: {', '.join(party_composition)}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "prepared_spells",
            context + f"\nSuggest an optimal selection of {prepared_limit} prepared spells " +
            f"for a {class_name} of level {level} " +
            f"{'for an adventure in ' + adventure_context if adventure_context else ''}. " +
            "Include a balanced mix of:\n" +
            "1. Combat spells (offense, defense, control)\n" +
            "2. Utility/exploration spells\n" +
            "3. Social interaction spells\n" +
            "4. Emergency/contingency options\n\n" +
            f"{'Consider the party composition: ' + ', '.join(party_composition) if party_composition else ''}\n" +
            "Explain the rationale behind each choice and how they work together as a cohesive loadout."
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "prepared_spells", 
            prompt, 
            {
                "class": class_name, 
                "level": level, 
                "limit": prepared_limit, 
                "context": adventure_context
            }
        )
        
        # Parse the response
        prepared_recommendations = self._parse_prepared_recommendations(response)
        
        return {
            "prepared_spells": prepared_recommendations,
            "raw_response": response
        }

    def customize_spell_appearance(self, 
                                 spell_name: str, 
                                 character_concept: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create personalized visual and thematic elements for a spell based on character concept.
        
        Args:
            spell_name: Name of the spell to customize
            character_concept: Dictionary with character concept details
            
        Returns:
            Dictionary with customization suggestions
        """
        # Extract relevant character information
        char_class = character_concept.get("class", {}).get("name", "unknown")
        background = character_concept.get("background", {}).get("name", "")
        species = character_concept.get("species", {}).get("name", "")
        
        # Additional character details that might influence spell appearance
        themes = character_concept.get("themes", [])
        elements = character_concept.get("elements", [])
        colors = character_concept.get("colors", [])
        personality = character_concept.get("personality", {})
        
        # Build context for LLM
        context = f"Spell to Customize: {spell_name}\n"
        context += f"Character Class: {char_class}\n"
        context += f"Species: {species}\n"
        context += f"Background: {background}\n"
        
        if themes:
            context += f"Character Themes: {', '.join(themes)}\n"
            
        if elements:
            context += f"Preferred Elements: {', '.join(elements)}\n"
            
        if colors:
            context += f"Character Colors: {', '.join(colors)}\n"
            
        if personality:
            traits = personality.get("traits", [])
            if traits:
                context += f"Personality Traits: {', '.join(traits)}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "customize_appearance",
            context + f"\nCreate a personalized thematic customization for the {spell_name} spell " +
            f"that reflects this {species} {char_class}'s identity, background, and aesthetic. " +
            "Include:\n" +
            "1. Visual appearance changes (colors, elements, motifs)\n" +
            "2. Sensory details (sounds, smells, tactile sensations)\n" +
            "3. Thematic connections to the character's background and personality\n" +
            "4. Verbal and somatic component customizations\n" +
            "5. Suggestions for how the spell's effect might look unique to this caster\n\n" +
            "Note that these changes are purely cosmetic and do not alter the mechanical function of the spell."
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "customize_appearance", 
            prompt, 
            {"spell": spell_name, "class": char_class}
        )
        
        # Parse the response
        customization = self._parse_spell_customization(response)
        
        return {
            "customization": customization,
            "raw_response": response
        }
        
    def create_spell_combinations(self, 
                                spell_list: List[str],
                                character_data: Optional[Dict[str, Any]] = None,
                                combo_count: int = 3) -> Dict[str, Any]:
        """
        Suggest creative combinations of spells for tactical advantage.
        
        Args:
            spell_list: List of spells available to combine
            character_data: Optional character data
            combo_count: Number of combinations to suggest
            
        Returns:
            Dictionary with spell combination suggestions
        """
        # Build context for LLM
        context = f"Available Spells: {', '.join(spell_list)}\n"
        context += f"Number of Combinations Requested: {combo_count}\n"
        
        if character_data:
            char_class = character_data.get("class", {}).get("name", "unknown")
            level = character_data.get("level", 1)
            context += f"Character Class: {char_class} (Level {level})\n"
            
            if "party" in character_data:
                context += "Party Members: "
                context += ", ".join(f"{m.get('name', 'Unknown')} ({m.get('class', 'Unknown')})" 
                                   for m in character_data.get("party", []))
                context += "\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "spell_combinations",
            context + f"\nSuggest {combo_count} creative and effective combinations using " +
            "the listed spells. For each combination:\n" +
            "1. Identify 2-3 spells that work especially well together\n" +
            "2. Explain how they mechanically interact and complement each other\n" +
            "3. Describe the tactical advantage gained from this combination\n" +
            "4. Suggest a specific scenario where this combo would be particularly effective\n" +
            "5. Note any timing, positioning, or preparation requirements\n\n" +
            "Focus on combinations that are rules-compliant and don't require questionable interpretations."
        )
        
        # Get LLM response
        response = self._get_llm_response("spell_combinations", prompt, {"spells": spell_list})
        
        # Parse the response
        combinations = self._parse_spell_combinations(response)
        
        return {
            "combinations": combinations,
            "raw_response": response
        }
        
    def suggest_signature_spell(self, 
                              character_data: Dict[str, Any],
                              spell_level: Optional[int] = None) -> Dict[str, Any]:
        """
        Suggest and customize a signature spell that defines the character's spellcasting style.
        
        Args:
            character_data: Character information
            spell_level: Optional specific spell level to consider
            
        Returns:
            Dictionary with signature spell suggestion and customization
        """
        # Extract relevant character information
        char_class = character_data.get("class", {}).get("name", "unknown")
        level = character_data.get("level", 1)
        personality = character_data.get("personality", {})
        background = character_data.get("background", {}).get("name", "")
        species = character_data.get("species", {}).get("name", "")
        
        # Build context for LLM
        context = f"Character Class: {char_class} (Level {level})\n"
        context += f"Species: {species}\n"
        context += f"Background: {background}\n"
        
        if personality:
            traits = personality.get("traits", [])
            ideals = personality.get("ideals", "")
            if traits:
                context += f"Personality Traits: {', '.join(traits)}\n"
            if ideals:
                context += f"Ideals: {ideals}\n"
                
        if spell_level is not None:
            context += f"Spell Level: {spell_level}\n"
        else:
            max_level = min((level + 1) // 2, 9)
            context += f"Available Spell Levels: Up to level {max_level}\n"
            
        # Add additional character elements if available
        for key in ["fighting_style", "subclass", "magical_approach"]:
            if key in character_data:
                context += f"{key.replace('_', ' ').title()}: {character_data[key]}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "signature_spell",
            context + "\nSuggest a signature spell that would define this character's magical identity " +
            "and spellcasting style. This should be a spell that reflects their personality, " +
            "background, and approach to magic.\n\n" +
            "Provide:\n" +
            "1. The name of an appropriate spell from the character's class spell list\n" +
            "2. Why this spell perfectly encapsulates the character's identity and magical style\n" +
            "3. A personalized description of how the spell appears when this character casts it\n" +
            "4. Creative ways the character might use this spell beyond its standard applications\n" +
            "5. How the character might have developed a special connection to this particular spell\n" +
            "6. A unique name the character might use for their personalized version of this spell"
        )
        
        # Get LLM response
        response = self._get_llm_response("signature_spell", prompt, character_data)
        
        # Parse the response
        signature_spell = self._parse_signature_spell(response)
        
        return {
            "signature_spell": signature_spell,
            "raw_response": response
        }
    
    def generate_ritual_casting_flavor(self, 
                                     spell_name: str,
                                     character_data: Dict[str, Any],
                                     ritual_duration_minutes: int = 10) -> Dict[str, Any]:
        """
        Generate detailed flavor for how a character performs ritual casting.
        
        Args:
            spell_name: The ritual spell being cast
            character_data: Character information
            ritual_duration_minutes: Duration of the ritual in minutes
            
        Returns:
            Dictionary with ritual casting details and flavor
        """
        # Extract relevant character information
        char_class = character_data.get("class", {}).get("name", "unknown")
        background = character_data.get("background", {}).get("name", "")
        species = character_data.get("species", {}).get("name", "")
        
        # Build context for LLM
        context = f"Ritual Spell: {spell_name}\n"
        context += f"Character Class: {char_class}\n"
        context += f"Species: {species}\n"
        context += f"Background: {background}\n"
        context += f"Ritual Duration: {ritual_duration_minutes} minutes\n"
        
        # Add any relevant items the character might use
        items = []
        if "equipment" in character_data:
            items = [item for item in character_data.get("equipment", []) 
                    if any(keyword in item.lower() for keyword in 
                          ["component", "focus", "holy", "book", "tome", "incense", "herb"])]
            
        if items:
            context += f"Relevant Items: {', '.join(items)}\n"
            
        # Add any religious or philosophical affiliations
        if "religion" in character_data:
            context += f"Religious Affiliation: {character_data['religion']}\n"
            
        if "philosophy" in character_data:
            context += f"Philosophical Approach: {character_data['philosophy']}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "ritual_casting",
            context + f"\nDescribe in rich detail how this {species} {char_class} performs " +
            f"the {ritual_duration_minutes}-minute ritual to cast {spell_name}. Include:\n\n" +
            "1. The physical components and preparations required\n" +
            "2. Gestures, movements, and body positioning during the ritual\n" +
            "3. Words, chants, or incantations spoken\n" +
            "4. How the character's background and training influence their ritual style\n" +
            "5. Sensory details (sights, sounds, smells, etc.) that accompany the ritual\n" +
            "6. How the magical energy builds and manifests throughout the duration\n" +
            "7. What happens in the final moments as the spell takes effect\n\n" +
            "Make this description uniquely suited to this character's identity and magical style."
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "ritual_casting", 
            prompt, 
            {"spell": spell_name, "class": char_class}
        )
        
        # Parse the response
        ritual_description = self._parse_ritual_description(response)
        
        return {
            "ritual_description": ritual_description,
            "raw_response": response
        }

    def explain_multiclass_spell_synergies(self, 
                                         classes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Explain spell synergies and strategies for multiclass spellcasters.
        
        Args:
            classes: List of class information dictionaries with names and levels
            
        Returns:
            Dictionary with multiclass spellcasting analysis
        """
        # Build context for LLM
        class_descriptions = [f"{c['name']} (Level {c['level']})" for c in classes]
        context = f"Multiclass Combination: {', '.join(class_descriptions)}\n"
        
        # Calculate spellcasting level for each class
        spellcasting_classes = [c for c in classes if c['name'].lower() in 
                              ["wizard", "sorcerer", "cleric", "druid", "bard", 
                               "warlock", "paladin", "ranger", "artificer"]]
        
        if spellcasting_classes:
            context += "Spellcasting Classes:\n"
            for c in spellcasting_classes:
                if c['name'].lower() in ["paladin", "ranger"]:
                    caster_level = c['level'] // 2
                elif c['name'].lower() == "artificer":
                    caster_level = (c['level'] + 1) // 2
                else:
                    caster_level = c['level']
                context += f"- {c['name']}: Caster level {caster_level}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "multiclass_synergy",
            context + "\nAnalyze the spell synergies and optimal spellcasting strategies for this " +
            "multiclass combination. Include:\n\n" +
            "1. How spell slots are calculated and shared between classes\n" +
            "2. Which spells are known/prepared from each class\n" +
            "3. Recommended spell selection strategy to maximize synergy\n" +
            "4. Unique spell combinations enabled by this multiclass build\n" +
            "5. Potential limitations and how to work around them\n" +
            "6. Spellcasting focus considerations\n" +
            "7. Overall magical theme or style that emerges from this combination\n\n" +
            "Be specific about rules interactions and provide practical advice."
        )
        
        # Get LLM response
        response = self._get_llm_response("multiclass_synergy", prompt, {"classes": classes})
        
        # Parse the response
        synergy_analysis = self._parse_multiclass_analysis(response)
        
        return {
            "synergy_analysis": synergy_analysis,
            "raw_response": response
        }

    # Helper methods
    def _create_prompt(self, prompt_type: str, context: str) -> str:
        """Create a well-formatted prompt for the LLM based on prompt type."""
        base_prompts = {
            "thematic_spells": "You are an expert D&D 5e spellcasting advisor focused on character-driven spell selection.",
            "creative_uses": "You are an imaginative D&D 5e magic consultant who helps players use spells in creative ways.",
            "class_spells": "You are a knowledgeable D&D 5e spellcasting mentor who provides optimal spell recommendations.",
            "dc_implications": "You are a tactical D&D 5e advisor specializing in spell mechanics and probabilities.",
            "attack_vs_save": "You are a mathematical D&D 5e analyst who compares different spellcasting approaches.",
            "prepared_spells": "You are a strategic D&D 5e spell loadout consultant who optimizes spell preparation.",
            "customize_appearance": "You are an artistic D&D 5e spell designer who creates unique magical aesthetics.",
            "spell_combinations": "You are a creative D&D 5e magical synergy expert who finds powerful spell combinations.",
            "signature_spell": "You are a character-focused D&D 5e magical stylist who develops distinctive spellcasting identities.",
            "ritual_casting": "You are a descriptive D&D 5e magical ritualist who brings spellcasting processes to life.",
            "multiclass_synergy": "You are a D&D 5e multiclass specialist who optimizes complex spellcasting combinations."
        }
        
        # Default prompt type if not found
        if prompt_type not in base_prompts:
            prompt_type = "thematic_spells"
            
        full_prompt = f"{base_prompts[prompt_type]}\n\n{context}\n\n"
        full_prompt += "Format your response in a clear, organized way with headings and sections. "
        full_prompt += "Ensure all recommendations are accurate to D&D 5e rules."
        
        return full_prompt
    
    def _get_llm_response(self, query_type: str, prompt: str, key_data: Dict[str, Any]) -> str:
        """Get response from LLM, using cache if enabled and available."""
        if not self.cache_enabled:
            return self.llm_service.generate(prompt)
        
        # Create a cache key based on query type and key data
        cache_key = f"{query_type}_{json.dumps(key_data, sort_keys=True)}"
        
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]
            
        # Generate new response and cache it
        response = self.llm_service.generate(prompt)
        self.response_cache[cache_key] = response
        return response
    
    def _parse_spell_suggestions(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for spell suggestions."""
        suggestions = []
        
        # Look for numbered spell sections
        spell_blocks = re.findall(r"(?:\d+\.|\*|\-)\s*([^\n]+(?:\n(?!(?:\d+\.|\*|\-))[^\n]+)*)", response)
        
        if not spell_blocks:
            # Try another approach - look for spell names followed by descriptions
            spell_blocks = re.findall(r"(?:^|\n)([A-Z][^:\n]+)(?::|(?:\n(?!\d+\.|[A-Z][^:\n]+:)))", response)
        
        for block in spell_blocks:
            spell = {"name": "", "level": "", "connection": "", "flavor": ""}
            
            # Try to extract spell name
            name_match = re.search(r"^([^(:.\n]+)", block.strip())
            if name_match:
                spell["name"] = name_match.group(1).strip()
            
            # Try to extract spell level
            level_match = re.search(r"(?:Level|lvl|Spell Level)[^:]*?:\s*(\d|cantrip)", block.lower())
            if level_match:
                spell["level"] = level_match.group(1)
            elif "cantrip" in block.lower():
                spell["level"] = "cantrip"
                
            # Try to extract character connection
            connection_match = re.search(r"(?:Connection|Theme|Resonance|Aligns|Fits)[^:]*?:\s*([^\n]+)", block, re.IGNORECASE)
            if connection_match:
                spell["connection"] = connection_match.group(1).strip()
            else:
                # Look for sentences mentioning connection or why
                connection_matches = re.findall(r"(?:This (?:spell )?(?:connects|relates|aligns|fits|works)|This (?:fits|aligns|connects|relates)|Because)[^.!?]*[.!?]", block)
                if connection_matches:
                    spell["connection"] = " ".join(connection_matches)
            
            # Try to extract flavor customization
            flavor_match = re.search(r"(?:Flavor|Customization|Appearance|Manifest)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if flavor_match:
                spell["flavor"] = flavor_match.group(1).strip()
                
            if spell["name"]:
                suggestions.append(spell)
        
        return suggestions
    
    def _parse_creative_uses(self, response: str) -> List[Dict[str, str]]:
        """Parse LLM response for creative spell uses."""
        uses = []
        
        # Look for numbered uses
        use_blocks = re.findall(r"(?:\d+\.|\*|\-)\s*([^\n]+(?:\n(?!(?:\d+\.|\*|\-))[^\n]+)*)", response)
        
        for block in use_blocks:
            use = {"title": "", "description": block.strip(), "mechanics": ""}
            
            # Try to extract title
            title_match = re.search(r"^([^:.\n]+)", block)
            if title_match:
                use["title"] = title_match.group(1).strip()
                
            # Try to extract mechanics explanation
            mechanics_match = re.search(r"(?:Mechanic|Rules|How it works|RAW)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if mechanics_match:
                use["mechanics"] = mechanics_match.group(1).strip()
                
            uses.append(use)
            
        return uses
    
    def _parse_spell_recommendations(self, response: str) -> Dict[str, List[Dict[str, str]]]:
        """Parse LLM response for spell recommendations by level."""
        recommendations = {"cantrips": [], "level_1": [], "level_2": [], "level_3": [], 
                          "level_4": [], "level_5": [], "level_6": [], "level_7": [], 
                          "level_8": [], "level_9": []}
        
        # Look for spell blocks
        spell_blocks = re.findall(r"(?:\d+\.|\*|\-)\s*([^\n]+(?:\n(?!(?:\d+\.|\*|\-))[^\n]+)*)", response)
        
        for block in spell_blocks:
            spell = {"name": "", "reason": block.strip()}
            
            # Try to extract spell name
            name_match = re.search(r"^([^(:.\n]+)", block.strip())
            if name_match:
                spell["name"] = name_match.group(1).strip()
                
            # Try to determine spell level
            level_key = "level_1"  # Default
            
            level_match = re.search(r"(?:Level|lvl)[^:]*?:\s*(\d|cantrip)", block.lower())
            if level_match:
                level = level_match.group(1)
                if level == "cantrip":
                    level_key = "cantrips"
                else:
                    level_key = f"level_{level}"
            elif "cantrip" in block.lower():
                level_key = "cantrips"
            else:
                # Try to infer from context
                for i in range(9, 0, -1):
                    if f"level {i}" in block.lower() or f"{i}th level" in block.lower() or f"{i}st level" in block.lower() or f"{i}nd level" in block.lower() or f"{i}rd level" in block.lower():
                        level_key = f"level_{i}"
                        break
            
            # Add to appropriate level list
            if spell["name"]:
                recommendations[level_key].append(spell)
                
        return recommendations
    
    def _parse_tactical_implications(self, response: str) -> Dict[str, str]:
        """Parse LLM response for spell save DC tactical implications."""
        implications = {
            "effectiveness": "",
            "enemy_types": "",
            "spell_selection": "",
            "level_comparison": "",
            "tactical_advice": ""
        }
        
        # Try to extract effectiveness
        effect_match = re.search(r"(?:Effectiveness|Effectivity|Overall Power)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if effect_match:
            implications["effectiveness"] = effect_match.group(1).strip()
            
        # Try to extract enemy types
        enemy_match = re.search(r"(?:Enemy Types|Creature Types|Against Different|Saving Throws)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if enemy_match:
            implications["enemy_types"] = enemy_match.group(1).strip()
            
        # Try to extract spell selection advice
        spell_match = re.search(r"(?:Spell Selection|Choosing Spells|Strategic|Strategy)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if spell_match:
            implications["spell_selection"] = spell_match.group(1).strip()
            
        # Try to extract level comparison
        level_match = re.search(r"(?:Level Comparison|Compared To|Typical For|Average)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if level_match:
            implications["level_comparison"] = level_match.group(1).strip()
            
        # Try to extract tactical advice
        tactical_match = re.search(r"(?:Tactical Advice|Maximize|Tips|Recommendations)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if tactical_match:
            implications["tactical_advice"] = tactical_match.group(1).strip()
            
        return implications
    
    def _parse_comparison_analysis(self, response: str) -> Dict[str, str]:
        """Parse LLM response for attack vs save spell comparison."""
        comparison = {
            "probability_analysis": "",
            "attack_advantages": "",
            "save_advantages": "",
            "advantage_effects": "",
            "enemy_vulnerabilities": "",
            "recommendations": ""
        }
        
        # Try to extract probability analysis
        prob_match = re.search(r"(?:Probability|Mathematical|Statistics|Numbers)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if prob_match:
            comparison["probability_analysis"] = prob_match.group(1).strip()
            
        # Try to extract attack advantages
        attack_match = re.search(r"(?:Attack Advantages|When Attacks Are Better|Attack Roll Benefit)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if attack_match:
            comparison["attack_advantages"] = attack_match.group(1).strip()
            
        # Try to extract save advantages
        save_match = re.search(r"(?:Save Advantages|When Saves Are Better|Saving Throw Benefit)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if save_match:
            comparison["save_advantages"] = save_match.group(1).strip()
            
        # Try to extract advantage effects
        adv_match = re.search(r"(?:Advantage|Disadvantage|Effect of Advantage)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if adv_match:
            comparison["advantage_effects"] = adv_match.group(1).strip()
            
        # Try to extract enemy vulnerabilities
        enemy_match = re.search(r"(?:Enemy Types|Creature|Vulnerabilities|Specific Enemies)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if enemy_match:
            comparison["enemy_vulnerabilities"] = enemy_match.group(1).strip()
            
        # Try to extract recommendations
        rec_match = re.search(r"(?:Recommendations|Balance|Repertoire|Suggestions)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if rec_match:
            comparison["recommendations"] = rec_match.group(1).strip()
            
        return comparison
    
    def _parse_prepared_recommendations(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for prepared spell recommendations."""
        prepared = {
            "combat": [],
            "utility": [],
            "social": [],
            "emergency": [],
            "rationale": "",
            "spell_list": []
        }
        
        # Try to extract overall rationale
        rationale_match = re.search(r"(?:Rationale|Strategy|Approach|Overview)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if rationale_match:
            prepared["rationale"] = rationale_match.group(1).strip()
            
        # Try to find combat spells section
        combat_match = re.search(r"(?:Combat|Offensive|Battle|Fighting)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if combat_match:
            combat_text = combat_match.group(1)
            # Extract spell names from bullet points or numbered lists
            combat_spells = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^(:.\n]+)", combat_text, re.MULTILINE)
            prepared["combat"] = [spell.strip() for spell in combat_spells if spell.strip()]
            
        # Try to find utility spells section
        utility_match = re.search(r"(?:Utility|Exploration|General Use)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if utility_match:
            utility_text = utility_match.group(1)
            utility_spells = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^(:.\n]+)", utility_text, re.MULTILINE)
            prepared["utility"] = [spell.strip() for spell in utility_spells if spell.strip()]
            
        # Try to find social spells section
        social_match = re.search(r"(?:Social|Interaction|Communication)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if social_match:
            social_text = social_match.group(1)
            social_spells = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^(:.\n]+)", social_text, re.MULTILINE)
            prepared["social"] = [spell.strip() for spell in social_spells if spell.strip()]
            
        # Try to find emergency spells section
        emergency_match = re.search(r"(?:Emergency|Contingency|Situational|Defensive)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if emergency_match:
            emergency_text = emergency_match.group(1)
            emergency_spells = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^(:.\n]+)", emergency_text, re.MULTILINE)
            prepared["emergency"] = [spell.strip() for spell in emergency_spells if spell.strip()]
            
        # Create a consolidated spell list
        all_spells = prepared["combat"] + prepared["utility"] + prepared["social"] + prepared["emergency"]
        prepared["spell_list"] = list(set(all_spells))  # Remove duplicates
        
        return prepared
    
    def _parse_spell_customization(self, response: str) -> Dict[str, str]:
        """Parse LLM response for spell appearance customization."""
        customization = {
            "visual": "",
            "sensory": "",
            "thematic": "",
            "components": "",
            "effect": ""
        }
        
        # Try to extract visual appearance
        visual_match = re.search(r"(?:Visual|Appearance|Look|Colors)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if visual_match:
            customization["visual"] = visual_match.group(1).strip()
            
        # Try to extract sensory details
        sensory_match = re.search(r"(?:Sensory|Sound|Smell|Tactile|Feel)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if sensory_match:
            customization["sensory"] = sensory_match.group(1).strip()
            
        # Try to extract thematic connections
        thematic_match = re.search(r"(?:Thematic|Connection|Background|Personality)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if thematic_match:
            customization["thematic"] = thematic_match.group(1).strip()
            
        # Try to extract component customizations
        components_match = re.search(r"(?:Components?|Verbal|Somatic|Material)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if components_match:
            customization["components"] = components_match.group(1).strip()
            
        # Try to extract effect customizations
        effect_match = re.search(r"(?:Effect|Outcome|Result|Impact)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if effect_match:
            customization["effect"] = effect_match.group(1).strip()
            
        return customization
    
    def _parse_spell_combinations(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for spell combinations."""
        combinations = []
        
        # Look for numbered combinations
        combo_blocks = re.findall(r"(?:\d+\.|\*|\-)\s*([^\n]+(?:\n(?!(?:\d+\.|\*|\-))[^\n]+)*)", response)
        
        if not combo_blocks and "combination" in response.lower():
            # Try another approach - look for "Combination" headers
            combo_blocks = re.findall(r"(?:Combination|Combo)[^:]*?:\s*([^\n]+(?:\n(?!(?:Combination|Combo))[^\n]+)*)", response, re.IGNORECASE)
        
        for block in combo_blocks:
            combo = {
                "name": "",
                "spells": [],
                "interaction": "",
                "advantage": "",
                "scenario": "",
                "requirements": ""
            }
            
            # Try to extract combo name
            name_match = re.search(r"^([^:.\n]+)", block)
            if name_match:
                combo["name"] = name_match.group(1).strip()
                
            # Try to extract spells involved
            spells_match = re.search(r"(?:Spells|Includes|Involving)[^:]*?:\s*([^\n]+)", block, re.IGNORECASE)
            if spells_match:
                spells_text = spells_match.group(1)
                spells = re.findall(r"([^,+&and]+)", spells_text)
                combo["spells"] = [s.strip() for s in spells if s.strip()]
            else:
                # Extract spell names from the block
                spell_candidates = re.findall(r"(?:\b[A-Z][a-z]+ [A-Z][a-z]+\b|\b[A-Z][a-z]+\b)", block)
                if spell_candidates:
                    combo["spells"] = list(set([s for s in spell_candidates if len(s) > 3]))[:3]
                    
            # Try to extract mechanical interaction
            interaction_match = re.search(r"(?:Interaction|Mechanics|How it works)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if interaction_match:
                combo["interaction"] = interaction_match.group(1).strip()
                
            # Try to extract tactical advantage
            advantage_match = re.search(r"(?:Advantage|Benefit|Tactical|Gain|Outcome)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if advantage_match:
                combo["advantage"] = advantage_match.group(1).strip()
                
            # Try to extract scenario
            scenario_match = re.search(r"(?:Scenario|Situation|When to use|Best for)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if scenario_match:
                combo["scenario"] = scenario_match.group(1).strip()
                
            # Try to extract requirements
            req_match = re.search(r"(?:Requirements?|Timing|Positioning|Prep|Setup)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if req_match:
                combo["requirements"] = req_match.group(1).strip()
                
            combinations.append(combo)
            
        return combinations
    
    def _parse_signature_spell(self, response: str) -> Dict[str, str]:
        """Parse LLM response for signature spell details."""
        signature = {
            "spell_name": "",
            "custom_name": "",
            "rationale": "",
            "appearance": "",
            "creative_uses": [],
            "connection": ""
        }
        
        # Try to extract spell name
        name_match = re.search(r"(?:Spell|Signature Spell|Name)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            signature["spell_name"] = name_match.group(1).strip()
        else:
            # Look for spell names with typical capitalization
            spell_candidates = re.findall(r"(?<=\b)[A-Z][a-z]+(?: [A-Z][a-z]+)?(?=\b)", response)
            if spell_candidates:
                # Take the most frequently mentioned candidate that's not a common word
                from collections import Counter
                common_words = ["The", "And", "This", "That", "With", "When", "Character", "Spell"]
                candidates = [c for c in spell_candidates if c not in common_words]
                if candidates:
                    signature["spell_name"] = Counter(candidates).most_common(1)[0][0]
            
        # Try to extract custom name
        custom_match = re.search(r"(?:Custom|Unique|Personal|Own) Name[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if custom_match:
            signature["custom_name"] = custom_match.group(1).strip()
        else:
            # Look for quoted phrases that might be custom names
            custom_candidates = re.findall(r'"([^"]+)"', response)
            if custom_candidates:
                signature["custom_name"] = custom_candidates[0]
                
        # Try to extract rationale
        rationale_match = re.search(r"(?:Why|Rationale|Reason|Reflects|Identity)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if rationale_match:
            signature["rationale"] = rationale_match.group(1).strip()
            
        # Try to extract appearance
        appearance_match = re.search(r"(?:Appearance|Description|Looks|Manifests)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if appearance_match:
            signature["appearance"] = appearance_match.group(1).strip()
            
        # Try to extract creative uses
        uses_match = re.search(r"(?:Creative Uses|Applications|Beyond Standard)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if uses_match:
            uses_text = uses_match.group(1)
            uses = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", uses_text, re.MULTILINE)
            if uses:
                signature["creative_uses"] = [use.strip() for use in uses if use.strip()]
            else:
                # Split by sentences
                uses = [s.strip() for s in re.split(r'(?<=[.!?])\s+', uses_text) if s.strip()]
                signature["creative_uses"] = uses
                
        # Try to extract connection
        connection_match = re.search(r"(?:Connection|Developed|History|Story)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if connection_match:
            signature["connection"] = connection_match.group(1).strip()
            
        return signature
    
    def _parse_ritual_description(self, response: str) -> Dict[str, str]:
        """Parse LLM response for ritual casting description."""
        ritual = {
            "preparation": "",
            "gestures": "",
            "incantations": "",
            "background_influence": "",
            "sensory_details": "",
            "energy_buildup": "",
            "culmination": "",
            "overall_description": response.strip()  # Store full response as fallback
        }
        
        # Try to extract preparation components
        prep_match = re.search(r"(?:Preparation|Components|Materials|Setup|Physical)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if prep_match:
            ritual["preparation"] = prep_match.group(1).strip()
        
        # Try to extract gestures and movements
        gestures_match = re.search(r"(?:Gestures?|Movements?|Somatic|Body|Positioning)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if gestures_match:
            ritual["gestures"] = gestures_match.group(1).strip()
        
        # Try to extract verbal components
        verbal_match = re.search(r"(?:Words|Chants?|Incantations?|Verbal|Spoken)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if verbal_match:
            ritual["incantations"] = verbal_match.group(1).strip()
        
        # Try to extract background influence
        background_match = re.search(r"(?:Background|Training|Influence|Style|Tradition)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if background_match:
            ritual["background_influence"] = background_match.group(1).strip()
        
        # Try to extract sensory details
        sensory_match = re.search(r"(?:Sensory|Sights?|Sounds?|Smells?|Feels?|Details)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if sensory_match:
            ritual["sensory_details"] = sensory_match.group(1).strip()
        
        # Try to extract energy buildup
        buildup_match = re.search(r"(?:Energy|Buildup|Building|Growing|Progress|Duration)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if buildup_match:
            ritual["energy_buildup"] = buildup_match.group(1).strip()
        
        # Try to extract culmination/final moments
        final_match = re.search(r"(?:Final|Culmination|Completion|Conclusion|Effect|Takes Effect)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if final_match:
            ritual["culmination"] = final_match.group(1).strip()
        
        # If we don't find explicit sections, try to infer from paragraphs
        if not any(ritual.values()):
            paragraphs = re.split(r'\n\n+', response)
            if len(paragraphs) >= 3:
                # Assume first paragraph is preparation/setup
                ritual["preparation"] = paragraphs[0].strip()
                # Assume middle paragraphs are the process
                process_text = " ".join(paragraphs[1:-1])
                
                # Try to identify gestures vs incantations in process text
                gesture_words = ["hands", "gesture", "movement", "body", "position", "arms", "fingers"]
                verbal_words = ["chant", "word", "speak", "voice", "incant", "utter", "whisper", "intone"]
                
                for word in gesture_words:
                    if word in process_text.lower():
                        gesture_sentence = re.search(r'[^.!?]*' + word + r'[^.!?]*[.!?]', process_text.lower())
                        if gesture_sentence:
                            ritual["gestures"] = gesture_sentence.group(0).strip()
                        break
                        
                for word in verbal_words:
                    if word in process_text.lower():
                        verbal_sentence = re.search(r'[^.!?]*' + word + r'[^.!?]*[.!?]', process_text.lower())
                        if verbal_sentence:
                            ritual["incantations"] = verbal_sentence.group(0).strip()
                        break
                
                # Assume last paragraph is culmination
                ritual["culmination"] = paragraphs[-1].strip()
        
        return ritual


    def create_thematic_spell_reskin(self, 
                                concept: str,
                                source_of_power: str,
                                existing_spell_name: str,
                                character_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Reskin an existing D&D spell to fit a non-traditional character concept.
        
        Args:
            concept: The character concept (e.g., "Jedi mind warrior", "Techno-shaman")
            source_of_power: Source of magical abilities (e.g., "The Force", "Nanites", "Psionic energy")
            existing_spell_name: Name of the existing D&D spell to reskin
            character_data: Optional character data for further customization
            
        Returns:
            Dictionary with reskinned spell details
        """
        # Build context for LLM
        context = f"Character Concept: {concept}\n"
        context += f"Power Source: {source_of_power}\n"
        context += f"D&D Spell to Adapt: {existing_spell_name}\n"
        
        if character_data:
            if "personality" in character_data:
                traits = character_data.get("personality", {}).get("traits", [])
                if traits:
                    context += f"Personality Traits: {', '.join(traits)}\n"
                    
            if "background" in character_data:
                background = character_data.get("background", {}).get("name", "")
                context += f"Background: {background}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "thematic_reskin",
            context + f"\nReskin the D&D spell '{existing_spell_name}' to fit a {concept} who draws power from {source_of_power}.\n\n" +
            "Provide:\n" +
            "1. A thematic new name for the spell that fits the concept\n" +
            "2. A complete visual and sensory description of how the spell appears when cast\n" +
            "3. How the spell's components (verbal, somatic, material) are reinterpreted for this concept\n" +
            "4. How the effect and mechanics remain the same despite the new theme\n" +
            "5. The in-universe explanation for how this ability works within the character's conceptual framework\n" +
            "6. Any cultural or philosophical aspects associated with this power in the character's tradition\n\n" +
            "Keep all mechanical aspects of the spell identical while completely transforming its thematic presentation."
        )
        
        # Get LLM response
        response = self._get_llm_response("thematic_reskin", prompt, 
                                        {"concept": concept, "spell": existing_spell_name})
        
        # Parse the response
        reskin_data = self._parse_reskin_response(response)
        
        return {
            "reskinned_spell": reskin_data,
            "raw_response": response
        }

    def generate_custom_power_source(self,
                                concept: str,
                                inspiration_media: Optional[List[str]] = None,
                                cultural_elements: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a detailed non-traditional power source for spellcasting.
        
        Args:
            concept: Brief description of the character concept
            inspiration_media: Optional list of media inspirations (movies, books, games)
            cultural_elements: Optional cultural or mythological elements to incorporate
            
        Returns:
            Dictionary with custom power source details
        """
        # Build context for LLM
        context = f"Character Concept: {concept}\n"
        
        if inspiration_media:
            context += f"Media Inspirations: {', '.join(inspiration_media)}\n"
            
        if cultural_elements:
            context += f"Cultural Elements: {', '.join(cultural_elements)}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "power_source",
            context + "\nCreate a detailed non-traditional power source for this character concept " +
            "that can explain their spellcasting abilities in D&D while fitting their unique theme.\n\n" +
            "Include:\n" +
            "1. Name and basic nature of the power source\n" +
            "2. Origin and history of this power in the universe\n" +
            "3. How the character connects to and channels this power\n" +
            "4. Visual and sensory manifestations when the power is used\n" +
            "5. Limitations, costs, or risks associated with using this power\n" +
            "6. How different spell schools or effects map to different aspects of this power\n" +
            "7. Philosophical or ethical principles associated with the power\n" +
            "8. How the power source can explain traditional D&D mechanics (spell slots, preparation, etc.)\n\n" +
            "Make this power source feel coherent, unique, and rich with storytelling potential."
        )
        
        # Get LLM response
        response = self._get_llm_response("power_source", prompt, {"concept": concept})
        
        # Parse the response
        power_source = self._parse_power_source(response)
        
        return {
            "power_source": power_source,
            "raw_response": response
        }

    def translate_fictional_abilities(self,
                                    character_reference: str,
                                    fictional_powers: List[str],
                                    dnd_level: int = 5) -> Dict[str, Any]:
        """
        Translate specific abilities from fiction into equivalent D&D spells and mechanics.
        
        Args:
            character_reference: Name of character or power system to reference (e.g., "Jedi", "Avatar bending")
            fictional_powers: List of specific powers to translate (e.g., ["mind trick", "force push"])
            dnd_level: Target D&D character level to use as reference point
            
        Returns:
            Dictionary with D&D spell and mechanic equivalents
        """
        # Build context for LLM
        context = f"Reference Character/System: {character_reference}\n"
        context += f"Powers to Translate: {', '.join(fictional_powers)}\n"
        context += f"Target D&D Level: {dnd_level}\n"
        
        # Calculate appropriate spell levels based on character level
        max_spell_level = min((dnd_level + 1) // 2, 9)
        context += f"Available Spell Levels: Cantrips to level {max_spell_level}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "translate_powers",
            context + f"\nTranslate these {character_reference} powers into equivalent D&D spells and mechanics " +
            "that could create similar effects while fitting within the D&D rules framework.\n\n" +
            "For each power, provide:\n" +
            "1. The closest equivalent D&D spell(s) or class feature(s)\n" +
            "2. Any modifications needed to better match the fictional power\n" +
            "3. Alternative options if the main suggestion isn't perfect\n" +
            "4. Suggested spell level or how to access this ability in D&D\n" +
            "5. How to describe the power when using it to maintain the original flavor\n" +
            "6. Creative ways to combine existing D&D mechanics to simulate this power\n\n" +
            "Focus on RAW options when possible, but suggest reasonable homebrew adjustments if needed."
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "translate_powers", 
            prompt, 
            {"reference": character_reference, "powers": fictional_powers}
        )
        
        # Parse the response
        translations = self._parse_power_translations(response)
        
        return {
            "power_translations": translations,
            "raw_response": response
        }

    def design_custom_focus_item(self,
                            concept: str,
                            item_type: str,
                            power_source: Optional[str] = None,
                            character_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Design a custom spellcasting focus item for non-traditional caster concepts.
        
        Args:
            concept: Character concept (e.g., "Jedi mind warrior", "Technomancer")
            item_type: Type of focus item (e.g., "weapon", "wearable", "crystal", "device")
            power_source: Optional source of character's power
            character_data: Optional character information
            
        Returns:
            Dictionary with custom focus item details
        """
        # Build context for LLM
        context = f"Character Concept: {concept}\n"
        context += f"Focus Item Type: {item_type}\n"
        
        if power_source:
            context += f"Power Source: {power_source}\n"
            
        if character_data:
            background = character_data.get("background", {}).get("name", "")
            if background:
                context += f"Background: {background}\n"
                
            personality = character_data.get("personality", {})
            if "traits" in personality:
                traits = personality.get("traits", [])
                context += f"Personality Traits: {', '.join(traits)}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "custom_focus",
            context + f"\nDesign a unique spellcasting focus item for this {concept} character " +
            "that serves as both a mechanically valid focus for D&D and thematically fits their concept.\n\n" +
            "Include:\n" +
            "1. Name and detailed physical description of the item\n" +
            "2. Materials and craftsmanship details\n" +
            "3. History and significance to the character\n" +
            "4. How it channels or connects to their power source\n" +
            "5. Visual and sensory effects when used to cast spells\n" +
            "6. Any special attunement or connection requirements\n" +
            "7. How it might evolve or be upgraded as the character advances\n" +
            "8. Any minor magical properties or features (that don't affect game balance)\n\n" +
            "Make this focus item distinctive, personal, and central to the character's identity."
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "custom_focus", 
            prompt, 
            {"concept": concept, "item_type": item_type}
        )
        
        # Parse the response
        focus_item = self._parse_focus_item(response)
        
        return {
            "focus_item": focus_item,
            "raw_response": response
        }

    def create_custom_spell_progression(self,
                                    concept: str,
                                    character_level: int,
                                    primary_class: str,
                                    concept_elements: List[str],
                                    playstyle_preference: str) -> Dict[str, Any]:
        """
        Create a custom spell learning progression that fits a non-traditional concept.
        
        Args:
            concept: Character concept (e.g., "Jedi mind warrior")
            character_level: Current or target character level
            primary_class: Base D&D class being used
            concept_elements: Key elements of the concept to emphasize
            playstyle_preference: Preferred playstyle (e.g., "control", "damage", "utility")
            
        Returns:
            Dictionary with spell progression roadmap
        """
        # Build context for LLM
        context = f"Character Concept: {concept}\n"
        context += f"Target Level: {character_level}\n"
        context += f"Base D&D Class: {primary_class}\n"
        context += f"Key Concept Elements: {', '.join(concept_elements)}\n"
        context += f"Playstyle Preference: {playstyle_preference}\n"
        
        # Calculate spell level availability by character level
        max_spell_level = min((character_level + 1) // 2, 9)
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "spell_progression",
            context + f"\nCreate a custom spell learning progression for a {concept} built using the " +
            f"{primary_class} class that thematically evolves to level {character_level}.\n\n" +
            "Include:\n" +
            "1. A level-by-level progression showing which spells to select at each level\n" +
            "2. How each spell choice reinforces the character concept\n" +
            "3. Thematic relationships between the spells that show character development\n" +
            "4. Key power milestones that define the character's growing abilities\n" +
            "5. Alternative spell choices that could fit different expressions of this concept\n" +
            "6. Suggested multiclass levels or feats that enhance the concept (if appropriate)\n" +
            "7. How the mechanical spell choices tell a story about the character's growth\n\n" +
            "Ensure all suggestions are rules-legal while prioritizing theme and concept."
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "spell_progression",
            prompt,
            {"concept": concept, "class": primary_class, "level": character_level}
        )
        
        # Parse the response
        progression = self._parse_spell_progression(response)
        
        return {
            "spell_progression": progression,
            "raw_response": response
        }

    def suggest_concept_appropriate_limitations(self,
                                            concept: str,
                                            power_source: str,
                                            character_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Suggest thematic limitations, costs, or drawbacks for spellcasting that enhance roleplaying.
        
        Args:
            concept: Character concept
            power_source: Source of magical abilities
            character_data: Optional character information
            
        Returns:
            Dictionary with thematic limitations and roleplaying hooks
        """
        # Build context for LLM
        context = f"Character Concept: {concept}\n"
        context += f"Power Source: {power_source}\n"
        
        if character_data:
            background = character_data.get("background", {}).get("name", "")
            if background:
                context += f"Background: {background}\n"
                
            flaws = character_data.get("personality", {}).get("flaws", "")
            if flaws:
                context += f"Character Flaws: {flaws}\n"
                
            bonds = character_data.get("personality", {}).get("bonds", "")
            if bonds:
                context += f"Character Bonds: {bonds}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "thematic_limitations",
            context + f"\nCreate thematic limitations, costs, or drawbacks for a {concept}'s powers that " +
            "enhance roleplaying and add depth to the character without overly restricting gameplay.\n\n" +
            "Include:\n" +
            "1. Philosophical or ethical codes that guide or restrict power usage\n" +
            "2. Physical, mental, or spiritual costs of channeling the power source\n" +
            "3. Environmental or situational factors that enhance or diminish abilities\n" +
            "4. Rituals or practices required to maintain connection to the power source\n" +
            "5. Personal challenges or temptations related to using these powers\n" +
            "6. Story hooks related to the consequences of using these abilities\n" +
            "7. How these limitations can be incorporated into D&D mechanics in balanced ways\n\n" +
            "Make these limitations meaningful and character-defining rather than purely restrictive."
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "thematic_limitations",
            prompt,
            {"concept": concept, "power_source": power_source}
        )
        
        # Parse the response
        limitations = self._parse_thematic_limitations(response)
        
        return {
            "thematic_limitations": limitations,
            "raw_response": response
        }

    def generate_nonstandard_components(self,
                                    concept: str,
                                    component_type: str = "all",
                                    spell_tradition: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate non-standard thematic replacements for spell components that fit a character concept.
        
        This method creates thematic alternatives to traditional verbal, somatic, and material
        components that align with the character's unique concept or power source while
        maintaining game balance.
        
        Args:
            concept: Character concept (e.g., "Jedi mind warrior", "Technomancer")
            component_type: Type of components to generate ("verbal", "somatic", "material", "all")
            spell_tradition: Optional specific tradition or approach to magic
                
        Returns:
            Dictionary with thematic component replacements organized by component type
        
        Example:
            >>> advisor = LLMSpellsAdvisor()
            >>> components = advisor.generate_nonstandard_components("Star Wars Jedi")
            >>> print(components["component_replacements"]["verbal"]["general"])
            "Quiet, focused phrases that channel the Force, often in a calm, centered tone..."
        """
        # Validate component_type
        if component_type not in ["verbal", "somatic", "material", "all"]:
            component_type = "all"
            
        # Build context for LLM
        context = [
            f"Character Concept: {concept}",
            f"Component Type: {component_type}"
        ]
        
        if spell_tradition:
            context.append(f"Magical Tradition: {spell_tradition}")
        
        # Build a structured prompt to improve response format consistency
        prompt_parts = [
            "\n".join(context),
            f"Create thematic replacements for standard D&D spell components that would fit a {concept}.",
            "Format your response with clear section headers and bullet points for each component type.",
        ]
        
        # Add specific instructions based on component type
        component_prompts = {
            "verbal": [
                "# VERBAL COMPONENTS",
                "What sounds, phrases, or vocalizations replace traditional magical incantations?",
                "- Provide examples for different spell types (offensive, defensive, utility)",
                "- Explain their cultural or traditional significance",
                "- Describe how they sound and feel when spoken"
            ],
            "somatic": [
                "# SOMATIC COMPONENTS",
                "What movements, gestures, or physical actions replace traditional magical gestures?",
                "- Describe how these movements connect to the character's power source",
                "- Provide variations for different spell schools or effects",
                "- Explain how subtle casting might work with these gestures"
            ],
            "material": [
                "# MATERIAL COMPONENTS",
                "What objects, substances, or elements serve as material components?",
                "- Provide thematic substitutes for common material components",
                "- Explain how these materials connect to the character's power source",
                "- Describe what might serve as a spellcasting focus"
            ]
        }
        
        # Add relevant component sections based on requested type
        if component_type == "all":
            for section in component_prompts.values():
                prompt_parts.extend(section)
        else:
            prompt_parts.extend(component_prompts[component_type])
        
        # Add final instructions for cohesive system
        prompt_parts.append("\nProvide a cohesive system that maintains game balance while completely transforming the presentation of spellcasting to match this concept.")
        
        # Create the full prompt
        prompt = self._create_prompt(
            "nonstandard_components",
            "\n\n".join(prompt_parts)
        )
        
        try:
            # Get LLM response
            response = self._get_llm_response(
                "nonstandard_components",
                prompt,
                {"concept": concept, "component_type": component_type}
            )
            
            # Parse the response
            components = self._parse_component_replacements(response, component_type)
            
            # Ensure all requested component types have at least empty dictionaries
            if component_type == "all":
                for comp_type in ["verbal", "somatic", "material"]:
                    if comp_type not in components:
                        components[comp_type] = {}
            elif component_type not in components:
                components[component_type] = {}
                
            return {
                "component_replacements": components,
                "raw_response": response
            }
        except Exception as e:
            logger.error(f"Error generating nonstandard components: {e}")
            
            # Create fallback components based on concept
            fallback = {}
            concept_words = concept.split()
            base_word = concept_words[0] if concept_words else "unique"
            
            if component_type in ["verbal", "all"]:
                fallback["verbal"] = {
                    "general": f"Phrases that invoke {base_word} energy, spoken with determination and focus."
                }
            
            if component_type in ["somatic", "all"]:
                fallback["somatic"] = {
                    "general": f"Flowing movements reminiscent of {concept} traditions, using hands to direct energy."
                }
                
            if component_type in ["material", "all"]:
                fallback["material"] = {
                    "general": f"Small objects or symbols connected to the {concept} theme, such as crystals or emblems."
                }
                
            if component_type != "all":
                return {
                    "component_replacements": fallback.get(component_type, {}),
                    "raw_response": f"Error generating components: {str(e)}"
                }
                
            return {
                "component_replacements": fallback,
                "raw_response": f"Error generating components: {str(e)}"
            }

    def create_spellcasting_style_guide(self,
                                    concept: str,
                                    aesthetic_keywords: List[str],
                                    character_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a comprehensive style guide for a character's unique spellcasting aesthetic.
        
        Args:
            concept: Character concept
            aesthetic_keywords: List of aesthetic elements or keywords
            character_data: Optional character information
            
        Returns:
            Dictionary with spellcasting style guide
        """
        # Build context for LLM
        context = f"Character Concept: {concept}\n"
        context += f"Aesthetic Keywords: {', '.join(aesthetic_keywords)}\n"
        
        if character_data:
            char_class = character_data.get("class", {}).get("name", "unknown")
            context += f"Base Class: {char_class}\n"
            
            species = character_data.get("species", {}).get("name", "")
            if species:
                context += f"Species: {species}\n"
                
            background = character_data.get("background", {}).get("name", "")
            if background:
                context += f"Background: {background}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "style_guide",
            context + f"\nCreate a comprehensive style guide for how a {concept}'s magical abilities look, " +
            "sound, and feel when used. This guide should help maintain a consistent and unique " +
            "aesthetic across all spellcasting descriptions.\n\n" +
            "Include:\n" +
            "1. Core visual elements that appear in most or all spells\n" +
            "2. Color palette and how different colors might represent different spell types\n" +
            "3. Recurring symbols, motifs, or patterns in spell manifestations\n" +
            "4. Characteristic sounds, scents, or tactile sensations accompanying spells\n" +
            "5. How the aesthetic varies between different spell schools\n" +
            "6. How the aesthetic varies between casual, combat, and ritual casting\n" +
            "7. How the spellcasting style reflects the character's personality and history\n" +
            "8. Suggestions for describing low-level vs. high-level spell effects\n\n" +
            "Make this style guide specific enough to create a distinct identity but flexible enough to apply to various spells."
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "style_guide",
            prompt,
            {"concept": concept, "aesthetics": aesthetic_keywords}
        )
        
        # Parse the response
        style_guide = self._parse_style_guide(response)
        
        return {
            "spellcasting_style": style_guide,
            "raw_response": response
        }

    # Parser methods for the new functions

    def _parse_reskin_response(self, response: str) -> Dict[str, str]:
        """Parse LLM response for spell reskin details."""
        reskin = {
            "new_name": "",
            "description": "",
            "components": "",
            "mechanics": "",
            "explanation": "",
            "cultural_aspects": ""
        }
        
        # Try to extract new name
        name_match = re.search(r"(?:Name|New Name|Title)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            reskin["new_name"] = name_match.group(1).strip()
        
        # Try to extract description
        desc_match = re.search(r"(?:Description|Appearance|Visual|Sensory)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if desc_match:
            reskin["description"] = desc_match.group(1).strip()
        
        # Try to extract components
        comp_match = re.search(r"(?:Components|Verbal|Somatic|Material)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if comp_match:
            reskin["components"] = comp_match.group(1).strip()
        
        # Try to extract mechanics
        mech_match = re.search(r"(?:Mechanics|Effect|Function|Mechanical)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if mech_match:
            reskin["mechanics"] = mech_match.group(1).strip()
        
        # Try to extract explanation
        expl_match = re.search(r"(?:Explanation|How It Works|Framework|Theory)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if expl_match:
            reskin["explanation"] = expl_match.group(1).strip()
        
        # Try to extract cultural aspects
        cult_match = re.search(r"(?:Cultural|Philosophical|Tradition|Aspects)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if cult_match:
            reskin["cultural_aspects"] = cult_match.group(1).strip()
        
        return reskin

    def _parse_power_source(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for custom power source details."""
        power_source = {
            "name": "",
            "nature": "",
            "origin": "",
            "connection": "",
            "manifestation": "",
            "limitations": "",
            "spell_mappings": {},
            "philosophy": "",
            "mechanics_explanation": ""
        }
        
        # Try to extract name and nature
        name_match = re.search(r"(?:Name|Power Source|Nature)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            power_source["name"] = name_match.group(1).strip()
            
        # Try to extract basic nature if not in name
        nature_match = re.search(r"(?:Basic Nature|Type|Form)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if nature_match:
            power_source["nature"] = nature_match.group(1).strip()
            
        # Try to extract origin
        origin_match = re.search(r"(?:Origin|History|Source|Background)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if origin_match:
            power_source["origin"] = origin_match.group(1).strip()
            
        # Try to extract connection
        conn_match = re.search(r"(?:Connection|Channel|Access|Link)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if conn_match:
            power_source["connection"] = conn_match.group(1).strip()
            
        # Try to extract manifestation
        manif_match = re.search(r"(?:Manifestation|Visual|Sensory|Appearance)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if manif_match:
            power_source["manifestation"] = manif_match.group(1).strip()
            
        # Try to extract limitations
        limit_match = re.search(r"(?:Limitation|Cost|Risk|Drawback)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if limit_match:
            power_source["limitations"] = limit_match.group(1).strip()
            
        # Try to extract spell mappings
        map_match = re.search(r"(?:Mapping|School|Different Spell|Aspect)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if map_match:
            mapping_text = map_match.group(1).strip()
            
            # Try to find school-specific mappings
            school_matches = re.findall(r"(?:Abjuration|Conjuration|Divination|Enchantment|Evocation|Illusion|Necromancy|Transmutation)[^:]*?:\s*([^\n]+)", mapping_text, re.IGNORECASE)
            
            if school_matches:
                schools = ["abjuration", "conjuration", "divination", "enchantment", 
                        "evocation", "illusion", "necromancy", "transmutation"]
                
                for i, school in enumerate(schools):
                    if i < len(school_matches):
                        power_source["spell_mappings"][school] = school_matches[i]
            else:
                power_source["spell_mappings"]["general"] = mapping_text
                
        # Try to extract philosophy
        phil_match = re.search(r"(?:Philosophy|Ethics|Principles|Belief)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if phil_match:
            power_source["philosophy"] = phil_match.group(1).strip()
            
        # Try to extract mechanics explanation
        mech_match = re.search(r"(?:Mechanics|Game System|D&D Mechanics|Spell Slots|Preparation)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if mech_match:
            power_source["mechanics_explanation"] = mech_match.group(1).strip()
            
        return power_source

    def _parse_power_translations(self, response: str) -> List[Dict[str, str]]:
        """Parse LLM response for fictional power translations."""
        translations = []
        
        # Look for sections about individual powers
        # First try to find numbered powers
        power_blocks = re.findall(r"(?:\d+\.|\*)\s*([^\n]+(?:\n(?!(?:\d+\.|\*))[^\n]+)*)", response)
        
        if not power_blocks:
            # Try another approach - look for power names as headers
            power_blocks = re.findall(r"(?:^|\n)([A-Z][^:\n]+)(?::|(?:\n(?!\d+\.|[A-Z][^:\n]+:)))", response)
        
        for block in power_blocks:
            translation = {
                "power_name": "",
                "dnd_equivalent": "",
                "modifications": "",
                "alternatives": "",
                "suggested_level": "",
                "description": "",
                "creative_combinations": ""
            }
            
            # Try to extract power name
            name_match = re.search(r"^([^(:.\n]+)", block.strip())
            if name_match:
                translation["power_name"] = name_match.group(1).strip()
                
            # Try to extract D&D equivalent
            equiv_match = re.search(r"(?:Equivalent|D&D Spell|Similar to|Closest match)[^:]*?:\s*([^\n]+)", block, re.IGNORECASE)
            if equiv_match:
                translation["dnd_equivalent"] = equiv_match.group(1).strip()
                
            # Try to extract modifications
            mod_match = re.search(r"(?:Modification|Adjustment|Change|Tweak)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if mod_match:
                translation["modifications"] = mod_match.group(1).strip()
                
            # Try to extract alternatives
            alt_match = re.search(r"(?:Alternative|Other Option|Another Choice|If Not)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if alt_match:
                translation["alternatives"] = alt_match.group(1).strip()
                
            # Try to extract suggested level
            level_match = re.search(r"(?:Level|Suggested Level|Spell Level|Access)[^:]*?:\s*([^\n]+)", block, re.IGNORECASE)
            if level_match:
                translation["suggested_level"] = level_match.group(1).strip()
                
            # Try to extract description
            desc_match = re.search(r"(?:Description|Flavor|How to Describe|Presentation)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if desc_match:
                translation["description"] = desc_match.group(1).strip()
                
            # Try to extract creative combinations
            comb_match = re.search(r"(?:Creative|Combination|Simulate|Together)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if comb_match:
                translation["creative_combinations"] = comb_match.group(1).strip()
                
            translations.append(translation)
        
        return translations

    def _parse_focus_item(self, response: str) -> Dict[str, str]:
        """Parse LLM response for custom focus item details."""
        focus_item = {
            "name": "",
            "description": "",
            "materials": "",
            "history": "",
            "channeling": "",
            "effects": "",
            "attunement": "",
            "evolution": "",
            "properties": ""
        }
        
        # Try to extract name
        name_match = re.search(r"(?:Name|Title|Focus Name)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            focus_item["name"] = name_match.group(1).strip()
            
        # Try to extract description
        desc_match = re.search(r"(?:Description|Appearance|Physical|Looks)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if desc_match:
            focus_item["description"] = desc_match.group(1).strip()
            
        # Try to extract materials
        mat_match = re.search(r"(?:Material|Construction|Craftsmanship|Made of)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if mat_match:
            focus_item["materials"] = mat_match.group(1).strip()
            
        # Try to extract history
        hist_match = re.search(r"(?:History|Significance|Background|Origin)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if hist_match:
            focus_item["history"] = hist_match.group(1).strip()
            
        # Try to extract channeling
        chan_match = re.search(r"(?:Channel|Connection|Power|How it works)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if chan_match:
            focus_item["channeling"] = chan_match.group(1).strip()
            
        # Try to extract effects
        eff_match = re.search(r"(?:Effects?|Visual|Sensory|Manifest)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if eff_match:
            focus_item["effects"] = eff_match.group(1).strip()
            
        # Try to extract attunement
        att_match = re.search(r"(?:Attunement|Connection|Bonding|Requirements?)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if att_match:
            focus_item["attunement"] = att_match.group(1).strip()
            
        # Try to extract evolution
        evo_match = re.search(r"(?:Evolution|Growth|Advancement|Upgrade)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if evo_match:
            focus_item["evolution"] = evo_match.group(1).strip()
            
        # Try to extract properties
        prop_match = re.search(r"(?:Properties|Features|Abilities|Magic)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if prop_match:
            focus_item["properties"] = prop_match.group(1).strip()
            
        return focus_item

    def _parse_spell_progression(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for spell progression roadmap."""
        progression = {
            "overview": "",
            "by_level": {},
            "milestones": [],
            "alternatives": {},
            "multiclass_feats": "",
            "character_arc": ""
        }
        
        # Try to extract overview
        overview_match = re.search(r"(?:Overview|Introduction|Summary)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if overview_match:
            progression["overview"] = overview_match.group(1).strip()
            
        # Try to extract level-by-level progression
        # Look for patterns like "Level X", "Xth Level", "X:", or "X -" followed by spell descriptions
        level_pattern = re.compile(r"(?:Level (\d+)|(\d+)(?:st|nd|rd|th) Level|^(\d+)[:\-])[^\n]*(?:\n(?!(?:Level \d+|\d+(?:st|nd|rd|th) Level|\d+[:\-]|$))[^\n]+)*", re.MULTILINE)
        level_matches = level_pattern.finditer(response)
        
        for match in level_matches:
            level_num = match.group(1) or match.group(2) or match.group(3)
            if level_num:
                level_text = match.group(0).strip()
                
                # Remove the level header
                level_content = re.sub(r"^(?:Level \d+|\d+(?:st|nd|rd|th) Level|\d+[:\-])[^\n]*\n", "", level_text, 1).strip()
                
                # Extract spell choices
                spells = []
                spell_matches = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^(:.\n]+)", level_content, re.MULTILINE)
                if spell_matches:
                    spells = [spell.strip() for spell in spell_matches if spell.strip()]
                    
                # Extract rationale if present
                rationale = ""
                rationale_match = re.search(r"(?:Rationale|Reason|Why|Because)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", level_content, re.IGNORECASE)
                if rationale_match:
                    rationale = rationale_match.group(1).strip()
                    
                progression["by_level"][level_num] = {
                    "spells": spells,
                    "rationale": rationale or level_content,
                    "full_text": level_text
                }
        
        # Try to extract milestones
        milestone_match = re.search(r"(?:Milestone|Key Power|Important Level|Defining)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if milestone_match:
            milestone_text = milestone_match.group(1).strip()
            
            # Try to find bullet points or numbered list items
            milestone_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", milestone_text, re.MULTILINE)
            if milestone_items:
                progression["milestones"] = [item.strip() for item in milestone_items if item.strip()]
            else:
                # Just use the paragraph
                progression["milestones"] = [milestone_text]
                
        # Try to extract alternatives
        alt_match = re.search(r"(?:Alternative|Other Options|Different Approach|Variant)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if alt_match:
            alt_text = alt_match.group(1).strip()
            
            # Try to find alternative spell options by level
            alt_level_matches = re.findall(r"(?:Level (\d+)|(\d+)(?:st|nd|rd|th) Level)[^:]*?:\s*([^\n]+)", alt_text)
            if alt_level_matches:
                for match in alt_level_matches:
                    level_num = match[0] or match[1]
                    spells_text = match[2].strip()
                    spells = [s.strip() for s in re.split(r',|\bor\b|\binstead of\b', spells_text) if s.strip()]
                    progression["alternatives"][level_num] = spells
            else:
                progression["alternatives"]["general"] = alt_text
                
        # Try to extract multiclass/feat suggestions
        multi_match = re.search(r"(?:Multiclass|Feats?|Additional Options)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if multi_match:
            progression["multiclass_feats"] = multi_match.group(1).strip()
            
        # Try to extract character arc
        arc_match = re.search(r"(?:Character Arc|Story|Development|Growth)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if arc_match:
            progression["character_arc"] = arc_match.group(1).strip()
            
        return progression

    def _parse_thematic_limitations(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for thematic limitations and drawbacks."""
        limitations = {
            "codes": [],
            "costs": [],
            "factors": [],
            "rituals": [],
            "challenges": [],
            "story_hooks": [],
            "mechanics": ""
        }
        
        # Try to extract codes
        code_match = re.search(r"(?:Code|Ethics?|Philosophy|Principles?)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if code_match:
            code_text = code_match.group(1).strip()
            
            # Try to find bullet points or numbered items
            code_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", code_text, re.MULTILINE)
            if code_items:
                limitations["codes"] = [item.strip() for item in code_items if item.strip()]
            else:
                # Split by periods for sentence-based items
                code_items = [s.strip() for s in re.split(r'(?<=[.!?])\s+', code_text) if s.strip()]
                limitations["codes"] = code_items
                
        # Try to extract costs
        cost_match = re.search(r"(?:Cost|Price|Toll|Exhaustion)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if cost_match:
            cost_text = cost_match.group(1).strip()
            
            # Try to find bullet points or numbered items
            cost_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", cost_text, re.MULTILINE)
            if cost_items:
                limitations["costs"] = [item.strip() for item in cost_items if item.strip()]
            else:
                # Split by periods for sentence-based items
                cost_items = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cost_text) if s.strip()]
                limitations["costs"] = cost_items
                
        # Try to extract environmental factors
        factor_match = re.search(r"(?:Factors?|Environment|Situation|Condition)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if factor_match:
            factor_text = factor_match.group(1).strip()
            
            # Try to find bullet points or numbered items
            factor_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", factor_text, re.MULTILINE)
            if factor_items:
                limitations["factors"] = [item.strip() for item in factor_items if item.strip()]
            else:
                # Split by periods for sentence-based items
                factor_items = [s.strip() for s in re.split(r'(?<=[.!?])\s+', factor_text) if s.strip()]
                limitations["factors"] = factor_items
                
        # Try to extract rituals
        ritual_match = re.search(r"(?:Ritual|Practice|Maintenance|Required)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if ritual_match:
            ritual_text = ritual_match.group(1).strip()
            
            # Try to find bullet points or numbered items
            ritual_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", ritual_text, re.MULTILINE)
            if ritual_items:
                limitations["rituals"] = [item.strip() for item in ritual_items if item.strip()]
            else:
                # Split by periods for sentence-based items
                ritual_items = [s.strip() for s in re.split(r'(?<=[.!?])\s+', ritual_text) if s.strip()]
                limitations["rituals"] = ritual_items
                
        # Try to extract challenges
        challenge_match = re.search(r"(?:Challenge|Temptation|Personal|Internal)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if challenge_match:
            challenge_text = challenge_match.group(1).strip()
            
            # Try to find bullet points or numbered items
            challenge_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", challenge_text, re.MULTILINE)
            if challenge_items:
                limitations["challenges"] = [item.strip() for item in challenge_items if item.strip()]
            else:
                # Split by periods for sentence-based items
                challenge_items = [s.strip() for s in re.split(r'(?<=[.!?])\s+', challenge_text) if s.strip()]
                limitations["challenges"] = challenge_items
                
        # Try to extract story hooks
        hook_match = re.search(r"(?:Story|Hook|Plot|Adventure)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if hook_match:
            hook_text = hook_match.group(1).strip()
            
            # Try to find bullet points or numbered items
            hook_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", hook_text, re.MULTILINE)
            if hook_items:
                limitations["story_hooks"] = [item.strip() for item in hook_items if item.strip()]
            else:
                # Split by periods for sentence-based items
                hook_items = [s.strip() for s in re.split(r'(?<=[.!?])\s+', hook_text) if s.strip()]
                limitations["story_hooks"] = hook_items
                
        # Try to extract mechanics
        mech_match = re.search(r"(?:Mechanics|Game|Rules|System)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if mech_match:
            limitations["mechanics"] = mech_match.group(1).strip()
            
        return limitations

    def _parse_component_replacements(self, response: str, component_type: str) -> Dict[str, Any]:
        """Parse LLM response for component replacements."""
        components = {
            "verbal": {},
            "somatic": {},
            "material": {}
        }
        
        if component_type in ["verbal", "all"]:
            # Try to extract verbal component details
            verbal_match = re.search(r"(?:Verbal|Voice|Sound|Words|Phrase)[^:]*?(?:Component)?[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z|\d+\.)", response, re.IGNORECASE)
            if verbal_match:
                verbal_text = verbal_match.group(1).strip()
                
                # Try to extract examples by spell type
                components["verbal"]["general"] = verbal_text
                
                # Look for specific examples by spell type
                for spell_type in ["offensive", "defensive", "utility", "healing", "control", "illusion"]:
                    type_match = re.search(rf"(?:{spell_type})[^:]*?:\s*([^\n]+)", verbal_text, re.IGNORECASE)
                    if type_match:
                        components["verbal"][spell_type] = type_match.group(1).strip()
                        
                # Try to extract cultural significance
                cultural_match = re.search(r"(?:Cultural|Significance|Meaning|Tradition)[^:]*?:\s*([^\n]+)", verbal_text, re.IGNORECASE)
                if cultural_match:
                    components["verbal"]["cultural_significance"] = cultural_match.group(1).strip()
        
        if component_type in ["somatic", "all"]:
            # Try to extract somatic component details
            somatic_match = re.search(r"(?:Somatic|Gesture|Movement|Motion|Physical)[^:]*?(?:Component)?[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z|\d+\.)", response, re.IGNORECASE)
            if somatic_match:
                somatic_text = somatic_match.group(1).strip()
                
                # Set general somatic description
                components["somatic"]["general"] = somatic_text
                
                # Look for connection to power source
                connection_match = re.search(r"(?:Connection|Power source|Link|Channel)[^:]*?:\s*([^\n]+)", somatic_text, re.IGNORECASE)
                if connection_match:
                    components["somatic"]["power_connection"] = connection_match.group(1).strip()
                    
                # Look for variations by school
                for school in ["abjuration", "conjuration", "divination", "enchantment", "evocation", "illusion", "necromancy", "transmutation"]:
                    school_match = re.search(rf"(?:{school})[^:]*?:\s*([^\n]+)", somatic_text, re.IGNORECASE)
                    if school_match:
                        components["somatic"][school] = school_match.group(1).strip()
        
        if component_type in ["material", "all"]:
            # Try to extract material component details
            material_match = re.search(r"(?:Material|Object|Substance|Element|Physical)[^:]*?(?:Component)?[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z|\d+\.)", response, re.IGNORECASE)
            if material_match:
                material_text = material_match.group(1).strip()
                
                # Set general material description
                components["material"]["general"] = material_text
                
                # Try to extract specific substitutes
                substitutes_match = re.search(r"(?:Substitutes|Replacements|Instead of|Alternative)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", material_text, re.IGNORECASE)
                if substitutes_match:
                    sub_text = substitutes_match.group(1).strip()
                    components["material"]["substitutes"] = sub_text
                    
                # Try to extract connection explanation
                power_match = re.search(r"(?:Connection|Link|Related to|How they connect)[^:]*?:\s*([^\n]+)", material_text, re.IGNORECASE)
                if power_match:
                    components["material"]["power_connection"] = power_match.group(1).strip()
        
        return components

    def _parse_style_guide(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for spellcasting style guide."""
        style_guide = {
            "core_elements": [],
            "color_palette": "",
            "motifs": [],
            "sensory_aspects": {},
            "school_variations": {},
            "casting_styles": {},
            "personality_reflection": "",
            "level_scaling": {}
        }
        
        # Try to extract core elements
        core_match = re.search(r"(?:Core|Elements?|Visual|Foundation)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if core_match:
            core_text = core_match.group(1).strip()
            
            # Try to find bullet points or numbered items
            core_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", core_text, re.MULTILINE)
            if core_items:
                style_guide["core_elements"] = [item.strip() for item in core_items if item.strip()]
            else:
                # Split by periods for sentence-based items
                style_guide["core_elements"] = [s.strip() for s in re.split(r'(?<=[.!?])\s+', core_text) if s.strip()]
        
        # Try to extract color palette
        color_match = re.search(r"(?:Color|Palette|Hue|Shade)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if color_match:
            style_guide["color_palette"] = color_match.group(1).strip()
            
        # Try to extract motifs
        motif_match = re.search(r"(?:Motifs?|Symbols?|Patterns?|Recurring)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if motif_match:
            motif_text = motif_match.group(1).strip()
            
            # Try to find bullet points or numbered items
            motif_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", motif_text, re.MULTILINE)
            if motif_items:
                style_guide["motifs"] = [item.strip() for item in motif_items if item.strip()]
            else:
                # Split by periods for sentence-based items
                style_guide["motifs"] = [s.strip() for s in re.split(r'(?<=[.!?])\s+', motif_text) if s.strip()]
        
        # Try to extract sensory aspects
        sensory_match = re.search(r"(?:Sensory|Sound|Smell|Touch|Feel|Sensation)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if sensory_match:
            sensory_text = sensory_match.group(1).strip()
            
            # Look for specific sensory aspects
            for sense in ["sound", "scent", "touch", "taste"]:
                sense_match = re.search(rf"(?:{sense})[^:]*?:\s*([^\n]+)", sensory_text, re.IGNORECASE)
                if sense_match:
                    style_guide["sensory_aspects"][sense] = sense_match.group(1).strip()
            
            # If no specific senses found, use the whole text
            if not style_guide["sensory_aspects"]:
                style_guide["sensory_aspects"]["general"] = sensory_text
        
        # Try to extract school variations
        school_match = re.search(r"(?:School|Different School|Varies by School)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if school_match:
            school_text = school_match.group(1).strip()
            
            # Look for specific schools
            for school in ["abjuration", "conjuration", "divination", "enchantment", "evocation", "illusion", "necromancy", "transmutation"]:
                sch_match = re.search(rf"(?:{school})[^:]*?:\s*([^\n]+)", school_text, re.IGNORECASE)
                if sch_match:
                    style_guide["school_variations"][school] = sch_match.group(1).strip()
        
        # Try to extract casting styles
        cast_match = re.search(r"(?:Casting|Combat|Casual|Ritual|Style|Different situations)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if cast_match:
            cast_text = cast_match.group(1).strip()
            
            # Look for specific casting contexts
            for context in ["combat", "casual", "ritual"]:
                ctx_match = re.search(rf"(?:{context})[^:]*?:\s*([^\n]+)", cast_text, re.IGNORECASE)
                if ctx_match:
                    style_guide["casting_styles"][context] = ctx_match.group(1).strip()
        
        # Try to extract personality reflection
        pers_match = re.search(r"(?:Personality|Reflects|Character|History|Identity)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if pers_match:
            style_guide["personality_reflection"] = pers_match.group(1).strip()
        
        # Try to extract level scaling
        level_match = re.search(r"(?:Level|Scaling|Low-level|High-level|Power level)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if level_match:
            level_text = level_match.group(1).strip()
            
            # Look for specific level ranges
            for level in ["low", "medium", "high"]:
                lvl_match = re.search(rf"(?:{level})[^:]*?level[^:]*?:\s*([^\n]+)", level_text, re.IGNORECASE)
                if lvl_match:
                    style_guide["level_scaling"][level] = lvl_match.group(1).strip()
            
            # If no specific levels found, use the whole text
            if not style_guide["level_scaling"]:
                style_guide["level_scaling"]["general"] = level_text
        
        return style_guide
    
    ########################
    def clear_cache(self) -> None:
        """Clear the LLM response cache."""
        self.response_cache = {}
        
    def export_cache(self, filepath: str) -> bool:
        """
        Export the current cache to a JSON file.
        
        Args:
            filepath: Path to save the cache file
            
        Returns:
            bool: True if export was successful
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.response_cache, f)
            return True
        except Exception as e:
            print(f"Failed to export cache: {str(e)}")
            return False
            
    def import_cache(self, filepath: str) -> bool:
        """
        Import a previously exported cache from a JSON file.
        
        Args:
            filepath: Path to the cache file
            
        Returns:
            bool: True if import was successful
        """
        try:
            with open(filepath, 'r') as f:
                imported_cache = json.load(f)
                if self.cache_enabled:
                    self.response_cache.update(imported_cache)
                else:
                    self.response_cache = imported_cache
                    self.cache_enabled = True
            return True
        except Exception as e:
            print(f"Failed to import cache: {str(e)}")
            return False
        
    def design_homebrew_spell(self, 
                            concept: str,
                            spell_level: int,
                            primary_effect: str,
                            character_theme: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a balanced homebrew spell that fits a character concept.
        
        Args:
            concept: Brief description of spell concept
            spell_level: Target spell level (0 for cantrip)
            primary_effect: Main effect desired (damage, control, utility, etc.)
            character_theme: Optional character details to align with
            
        Returns:
            Dictionary with homebrew spell details
        """
        # Build context for LLM
        context = f"Spell Concept: {concept}\n"
        context += f"Spell Level: {spell_level if spell_level > 0 else 'Cantrip'}\n"
        context += f"Primary Effect: {primary_effect}\n"
        
        if character_theme:
            if "class" in character_theme:
                context += f"Character Class: {character_theme['class']}\n"
            if "theme" in character_theme:
                context += f"Character Theme: {character_theme['theme']}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "homebrew_spell",
            context + "\nCreate a balanced homebrew spell for D&D 5e that fits this concept " +
            "while maintaining game balance comparable to official spells of the same level.\n\n" +
            "Include:\n" +
            "1. Name of the spell\n" +
            "2. Level, school, casting time, range, components, and duration\n" +
            "3. Complete spell description following official formatting\n" +
            "4. Classes that would have access to this spell\n" +
            "5. Design notes explaining balance considerations\n" +
            "6. Thematic description of how the spell appears when cast\n" +
            "7. Comparison to similar official spells of the same level\n\n" +
            "Ensure the spell follows 5e design principles and power curves while being creative."
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "homebrew_spell",
            prompt,
            {"concept": concept, "level": spell_level, "effect": primary_effect}
        )
        
        # Parse the response
        spell_data = self._parse_homebrew_spell(response)
        
        return {
            "homebrew_spell": spell_data,
            "raw_response": response
        }

    def _parse_homebrew_spell(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for homebrew spell details."""
        spell = {
            "name": "",
            "level": "",
            "school": "",
            "casting_time": "",
            "range": "",
            "components": {},
            "duration": "",
            "description": "",
            "classes": [],
            "design_notes": "",
            "appearance": "",
            "comparable_spells": []
        }
        
        # Try to extract name
        name_match = re.search(r"(?:^|\n)(?:Name|Spell)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            spell["name"] = name_match.group(1).strip()
            
        # Try to extract level and school
        level_match = re.search(r"(?:Level|Spell Level)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if level_match:
            level_text = level_match.group(1).strip().lower()
            if "cantrip" in level_text:
                spell["level"] = "0"
            else:
                level_digits = re.search(r"(\d+)", level_text)
                if level_digits:
                    spell["level"] = level_digits.group(1)
            
            # Try to find school in the same line
            school_match = re.search(r"(\w+)(?:\s+cantrip| level)", level_text)
            if school_match:
                spell["school"] = school_match.group(1).strip().title()
        
        # Try to extract school separately if needed
        if not spell["school"]:
            school_match = re.search(r"(?:School)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
            if school_match:
                spell["school"] = school_match.group(1).strip()
        
        # Try to extract casting time
        time_match = re.search(r"(?:Casting Time|Cast Time)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if time_match:
            spell["casting_time"] = time_match.group(1).strip()
            
        # Try to extract range
        range_match = re.search(r"(?:Range)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if range_match:
            spell["range"] = range_match.group(1).strip()
            
        # Try to extract components
        comp_match = re.search(r"(?:Components)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if comp_match:
            comp_text = comp_match.group(1).strip()
            spell["components"]["raw"] = comp_text
            
            if "V" in comp_text:
                spell["components"]["verbal"] = True
            if "S" in comp_text:
                spell["components"]["somatic"] = True
            if "M" in comp_text:
                material_match = re.search(r"M\s*\(([^)]+)\)", comp_text)
                if material_match:
                    spell["components"]["material"] = material_match.group(1).strip()
                else:
                    spell["components"]["material"] = True
                    
        # Try to extract duration
        dur_match = re.search(r"(?:Duration)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if dur_match:
            spell["duration"] = dur_match.group(1).strip()
            
        # Try to extract description - look for the largest block of text
        desc_block = ""
        description_sections = re.findall(r"(?:Description|Effect|Text)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        
        if description_sections:
            desc_block = max(description_sections, key=len)
        else:
            # Look for a paragraph that's not part of other fields
            paragraphs = re.split(r'\n\n+', response)
            for para in paragraphs:
                if not re.match(r"^(?:Name|Level|School|Casting Time|Range|Components|Duration|Classes|Design|Appearance|Comparable)[^:]*?:", para, re.IGNORECASE):
                    if len(para) > len(desc_block):
                        desc_block = para
                        
        spell["description"] = desc_block.strip()
        
        # Try to extract classes
        class_match = re.search(r"(?:Classes|Available to)[^:]*?:\s*([^\n]+)", response, re.IGNORECASE)
        if class_match:
            classes_text = class_match.group(1).strip()
            spell["classes"] = [c.strip() for c in re.split(r',|and', classes_text) if c.strip()]
            
        # Try to extract design notes
        design_match = re.search(r"(?:Design|Balance|Notes|Considerations)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if design_match:
            spell["design_notes"] = design_match.group(1).strip()
            
        # Try to extract appearance
        appear_match = re.search(r"(?:Appearance|Visual|Thematic|Aesthetics)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if appear_match:
            spell["appearance"] = appear_match.group(1).strip()
            
        # Try to extract comparable spells
        comp_match = re.search(r"(?:Comparable|Similar|Comparison)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if comp_match:
            comp_text = comp_match.group(1).strip()
            spell["comparable_spells"] = [s.strip() for s in re.split(r',|and', comp_text) if s.strip() and not s.strip().lower() in ["spells", "to", "with"]]
            
        return spell

    def analyze_character_spells(self,
                            character_data: Dict[str, Any],
                            analysis_focus: str = "balance") -> Dict[str, Any]:
        """
        Analyze an existing character's spell selection and provide insights.
        
        Args:
            character_data: Character data including spell selections
            analysis_focus: Type of analysis ("balance", "theme", "optimization", "roleplay")
            
        Returns:
            Dictionary with analysis results
        """
        # Extract relevant character information
        char_class = character_data.get("class", {}).get("name", "unknown")
        level = character_data.get("level", 1)
        spells = character_data.get("spells", [])
        
        # Build context for LLM
        context = f"Character Class: {char_class} (Level {level})\n"
        context += f"Analysis Focus: {analysis_focus}\n"
        
        if spells:
            context += "Current Spell Selection:\n"
            # Group by level
            spell_by_level = {}
            for spell in spells:
                spell_level = spell.get("level", 0)
                if spell_level not in spell_by_level:
                    spell_by_level[spell_level] = []
                spell_by_level[spell_level].append(spell.get("name", "Unknown Spell"))
                
            for level, spell_list in sorted(spell_by_level.items()):
                level_name = "Cantrips" if level == 0 else f"Level {level}"
                context += f"{level_name}: {', '.join(spell_list)}\n"
        
        # Create prompt for the LLM
        if analysis_focus == "balance":
            prompt_focus = ("Analyze the balance of this character's spell selection across different categories:\n"
                        "1. Combat vs. utility vs. social spells\n"
                        "2. Single-target vs. multi-target effects\n"
                        "3. Coverage of different damage types\n"
                        "4. Defensive and control options\n"
                        "5. Identify any gaps or redundancies in the selection")
        elif analysis_focus == "theme":
            prompt_focus = ("Analyze how well the character's spell selection forms a coherent thematic identity:\n"
                        "1. What theme(s) emerge from these spell choices?\n"
                        "2. How these spells might reflect the character's personality and background\n"
                        "3. Suggest ways to enhance thematic consistency\n"
                        "4. Identify spells that might not fit the apparent themes")
        elif analysis_focus == "optimization":
            prompt_focus = ("Analyze the mechanical effectiveness of this spell selection:\n"
                        "1. Evaluate the overall power level and efficiency\n"
                        "2. Identify suboptimal choices and suggest alternatives\n"
                        "3. Recommend synergies to exploit with this selection\n"
                        "4. Suggest optimal spell usage tactics")
        else:  # roleplay
            prompt_focus = ("Analyze the roleplaying potential of this spell selection:\n"
                        "1. How these spells could reflect character personality and development\n"
                        "2. Creative non-combat uses for these spells\n"
                        "3. Story hooks suggested by these magical affinities\n"
                        "4. How these spells could influence character relationships and interactions")
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "spell_analysis",
            context + "\n" + prompt_focus + "\n\n" +
            "Provide specific observations, constructive feedback, and actionable recommendations."
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "spell_analysis",
            prompt,
            {"class": char_class, "level": level, "focus": analysis_focus}
        )
        
        # Parse the response
        analysis = self._parse_spell_analysis(response, analysis_focus)
        
        return {
            "analysis": analysis,
            "raw_response": response
        }

    def _parse_spell_analysis(self, response: str, analysis_focus: str) -> Dict[str, Any]:
        """Parse LLM response for spell analysis."""
        analysis = {
            "summary": "",
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "insights": {}
        }
        
        # Try to extract summary
        summary_match = re.search(r"(?:Summary|Overview|Analysis)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if summary_match:
            analysis["summary"] = summary_match.group(1).strip()
        
        # Try to extract strengths
        strengths_match = re.search(r"(?:Strengths|Positives|What Works|Strong Points)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if strengths_match:
            strengths_text = strengths_match.group(1).strip()
            # Look for bullet points or numbered items
            strength_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", strengths_text, re.MULTILINE)
            if strength_items:
                analysis["strengths"] = [item.strip() for item in strength_items if item.strip()]
            else:
                # Split by sentences
                analysis["strengths"] = [s.strip() for s in re.split(r'(?<=[.!?])\s+', strengths_text) if s.strip()]
        
        # Try to extract weaknesses
        weaknesses_match = re.search(r"(?:Weaknesses|Gaps|Limitations|Concerns|Areas for Improvement)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if weaknesses_match:
            weaknesses_text = weaknesses_match.group(1).strip()
            # Look for bullet points or numbered items
            weakness_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", weaknesses_text, re.MULTILINE)
            if weakness_items:
                analysis["weaknesses"] = [item.strip() for item in weakness_items if item.strip()]
            else:
                # Split by sentences
                analysis["weaknesses"] = [s.strip() for s in re.split(r'(?<=[.!?])\s+', weaknesses_text) if s.strip()]
        
        # Try to extract recommendations
        rec_match = re.search(r"(?:Recommendations|Suggestions|Advice|What to Change)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if rec_match:
            rec_text = rec_match.group(1).strip()
            # Look for bullet points or numbered items
            rec_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", rec_text, re.MULTILINE)
            if rec_items:
                analysis["recommendations"] = [item.strip() for item in rec_items if item.strip()]
            else:
                # Split by sentences
                analysis["recommendations"] = [s.strip() for s in re.split(r'(?<=[.!?])\s+', rec_text) if s.strip()]
        
        # Extract focus-specific insights
        if analysis_focus == "balance":
            combat_match = re.search(r"(?:Combat|Battle|Offensive)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if combat_match:
                analysis["insights"]["combat"] = combat_match.group(1).strip()
                
            utility_match = re.search(r"(?:Utility|Exploration|Non-combat)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if utility_match:
                analysis["insights"]["utility"] = utility_match.group(1).strip()
                
            damage_match = re.search(r"(?:Damage Types|Elements|Damage Coverage)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if damage_match:
                analysis["insights"]["damage_coverage"] = damage_match.group(1).strip()
                
        elif analysis_focus == "theme":
            theme_match = re.search(r"(?:Themes?|Identity|Concept)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if theme_match:
                analysis["insights"]["identified_themes"] = theme_match.group(1).strip()
                
            consistency_match = re.search(r"(?:Consistency|Coherence|Alignment)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if consistency_match:
                analysis["insights"]["thematic_consistency"] = consistency_match.group(1).strip()
                
        elif analysis_focus == "optimization":
            power_match = re.search(r"(?:Power Level|Effectiveness|Efficiency)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if power_match:
                analysis["insights"]["power_assessment"] = power_match.group(1).strip()
                
            synergy_match = re.search(r"(?:Synerg|Combination|Interaction)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if synergy_match:
                analysis["insights"]["synergies"] = synergy_match.group(1).strip()
                
            tactic_match = re.search(r"(?:Tactics|Usage|Strategy|Approach)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if tactic_match:
                analysis["insights"]["tactical_advice"] = tactic_match.group(1).strip()
                
        else:  # roleplay
            personality_match = re.search(r"(?:Personality|Character|Identity|Reflection)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if personality_match:
                analysis["insights"]["character_reflection"] = personality_match.group(1).strip()
                
            story_match = re.search(r"(?:Story|Narrative|Hooks|Plot)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if story_match:
                analysis["insights"]["story_potential"] = story_match.group(1).strip()
                
            creative_match = re.search(r"(?:Creative Uses|Non-combat|Alternative)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if creative_match:
                analysis["insights"]["creative_applications"] = creative_match.group(1).strip()
        
        return analysis

    def explain_spell_mechanics(self,
                            topic: str,
                            detail_level: str = "standard",
                            context_for_character: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Provide educational explanations about spell mechanics, schools, or concepts.
        
        Args:
            topic: Spell mechanic or concept to explain
            detail_level: Level of detail ("basic", "standard", "advanced")
            context_for_character: Optional character data to personalize explanation
            
        Returns:
            Dictionary with educational explanation
        """
        # Build context for LLM
        context = f"Topic: {topic}\n"
        context += f"Detail Level: {detail_level}\n"
        
        if context_for_character:
            char_class = context_for_character.get("class", {}).get("name", "unknown")
            level = context_for_character.get("level", 1)
            context += f"Character Context: Level {level} {char_class}\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "spell_education",
            context + f"\nProvide a clear explanation of {topic} as it relates to D&D 5e spellcasting " +
            f"at a {detail_level} level of detail." +
            (f" Personalize the explanation for a {level} level {char_class}." if context_for_character else "") + "\n\n" +
            "Include:\n" +
            "1. Core mechanics and how they work within the rules\n" +
            "2. Common misconceptions or rules confusions\n" +
            "3. Practical examples of these mechanics in play\n" +
            "4. Strategic implications for spellcasters\n" +
            "5. Any relevant rules citations or page references\n\n" +
            "Make the explanation accessible and immediately useful at the table."
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "spell_education",
            prompt,
            {"topic": topic, "detail_level": detail_level}
        )
        
        # Parse the response
        explanation = self._parse_educational_content(response)
        
        return {
            "explanation": explanation,
            "raw_response": response
        }

    def _parse_educational_content(self, response: str) -> Dict[str, str]:
        """Parse LLM response for educational content."""
        education = {
            "summary": "",
            "core_mechanics": "",
            "misconceptions": "",
            "examples": "",
            "strategic_implications": "",
            "rules_references": ""
        }
        
        # Try to extract summary or overview
        summary_match = re.search(r"(?:^|\n\n)(?:Summary|Overview|Introduction)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if summary_match:
            education["summary"] = summary_match.group(1).strip()
        else:
            # Use first paragraph as summary
            first_para = re.search(r"^([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response)
            if first_para:
                education["summary"] = first_para.group(1).strip()
        
        # Try to extract core mechanics
        mech_match = re.search(r"(?:Core Mechanics|How It Works|Rules|Mechanics)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if mech_match:
            education["core_mechanics"] = mech_match.group(1).strip()
        
        # Try to extract misconceptions
        misc_match = re.search(r"(?:Misconceptions|Common Mistakes|Confusions|Errors)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if misc_match:
            education["misconceptions"] = misc_match.group(1).strip()
        
        # Try to extract examples
        example_match = re.search(r"(?:Examples|For Example|In Practice|Practical)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if example_match:
            education["examples"] = example_match.group(1).strip()
        
        # Try to extract strategic implications
        strat_match = re.search(r"(?:Strategic|Strategy|Implications|Applications)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if strat_match:
            education["strategic_implications"] = strat_match.group(1).strip()
        
        # Try to extract rules references
        ref_match = re.search(r"(?:References|Citations|Page|Rules As Written|RAW)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if ref_match:
            education["rules_references"] = ref_match.group(1).strip()
        
        return education

    def optimize_party_spell_coverage(self,
                                    party_data: List[Dict[str, Any]],
                                    upcoming_challenges: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Optimize spell selection across a party to maximize coverage and synergy.
        
        Args:
            party_data: List of character data dictionaries for party members
            upcoming_challenges: Optional list of anticipated challenges
            
        Returns:
            Dictionary with party optimization recommendations
        """
        # Build context for LLM
        context = "Party Composition:\n"
        
        spellcasters = []
        for i, character in enumerate(party_data):
            char_class = character.get("class", {}).get("name", "Unknown")
            level = character.get("level", 1)
            name = character.get("name", f"Character {i+1}")
            
            context += f"- {name}: Level {level} {char_class}\n"
            
            # Check if this is a spellcaster
            if char_class.lower() in ["wizard", "sorcerer", "cleric", "druid", "warlock", 
                                    "bard", "paladin", "ranger", "artificer"]:
                spells = character.get("spells", [])
                spell_names = [s.get("name", "Unknown Spell") for s in spells]
                context += f"  Spells: {', '.join(spell_names[:5])}"
                if len(spell_names) > 5:
                    context += f" and {len(spell_names) - 5} more"
                context += "\n"
                spellcasters.append(character)
        
        if upcoming_challenges:
            context += "\nUpcoming Challenges: " + ", ".join(upcoming_challenges) + "\n"
        
        # Create prompt for the LLM
        prompt = self._create_prompt(
            "party_optimization",
            context + "\nAnalyze this party's spell coverage and recommend optimizations to " +
            "ensure they have balanced magical capabilities across different situations.\n\n" +
            "Include:\n" +
            "1. Assessment of current spell coverage and major gaps\n" +
            "2. Recommended role for each spellcaster based on their class and current selection\n" +
            "3. Specific spell recommendations for each spellcaster to improve party coverage\n" +
            "4. Tactical advice for how these spellcasters can work together effectively\n" +
            "5. Spell combinations that would create powerful synergies between party members\n\n" +
            "Focus on practical recommendations that respect each character's class limitations."
        )
        
        # Get LLM response
        response = self._get_llm_response(
            "party_optimization",
            prompt,
            {"party_size": len(party_data), "caster_count": len(spellcasters)}
        )
        
        # Parse the response
        optimization = self._parse_party_optimization(response, [c.get("name", f"Character {i+1}") 
                                                            for i, c in enumerate(party_data)])
        
        return {
            "optimization": optimization,
            "raw_response": response
        }

    def _parse_party_optimization(self, response: str, character_names: List[str]) -> Dict[str, Any]:
        """Parse LLM response for party optimization."""
        optimization = {
            "overall_assessment": "",
            "gaps": [],
            "character_recommendations": {},
            "tactical_advice": "",
            "spell_synergies": []
        }
        
        # Try to extract overall assessment
        assessment_match = re.search(r"(?:Assessment|Overview|Analysis|Current Coverage)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if assessment_match:
            optimization["overall_assessment"] = assessment_match.group(1).strip()
        
        # Try to extract gaps
        gaps_match = re.search(r"(?:Gaps|Missing|Lacking|Weaknesses)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if gaps_match:
            gaps_text = gaps_match.group(1).strip()
            # Look for bullet points or numbered items
            gap_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", gaps_text, re.MULTILINE)
            if gap_items:
                optimization["gaps"] = [item.strip() for item in gap_items if item.strip()]
            else:
                # Split by sentences
                optimization["gaps"] = [s.strip() for s in re.split(r'(?<=[.!?])\s+', gaps_text) if s.strip()]
        
        # Try to extract character-specific recommendations
        for name in character_names:
            char_match = re.search(rf"(?:{re.escape(name)}|Character \d+)[^:]*?:\s*([^\n]+(?:\n(?!{re.escape(name)}|Character \d+)[^\n]+)*)", response, re.IGNORECASE)
            if char_match:
                char_text = char_match.group(1).strip()
                
                # Extract role if specified
                role = ""
                role_match = re.search(r"(?:Role|Focus|Specialty)[^:]*?:\s*([^\n]+)", char_text, re.IGNORECASE)
                if role_match:
                    role = role_match.group(1).strip()
                    
                # Extract spell recommendations
                recommendations = []
                rec_match = re.search(r"(?:Recommendations|Suggested Spells|Should Add|Consider)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", char_text, re.IGNORECASE)
                if rec_match:
                    rec_text = rec_match.group(1).strip()
                    # Look for specific spell names (capitalized)
                    spell_names = re.findall(r"(?:[-•*]\s*|, |[\s(]|^)([A-Z][a-z]+(?:'[a-z]+)?(?:\s[A-Z][a-z]+)*)", rec_text)
                    if spell_names:
                        recommendations = [s.strip() for s in spell_names if s.strip() and len(s) > 2]
                    
                    if not recommendations:
                        # Split by commas as fallback
                        recommendations = [s.strip() for s in re.split(r',|\band\b', rec_text) if s.strip()]
                
                optimization["character_recommendations"][name] = {
                    "suggested_role": role,
                    "recommended_spells": recommendations,
                    "full_advice": char_text
                }
        
        # Try to extract tactical advice
        tactical_match = re.search(r"(?:Tactical|Strategy|Working Together|Coordination)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if tactical_match:
            optimization["tactical_advice"] = tactical_match.group(1).strip()
        
        # Try to extract spell synergies
        synergy_match = re.search(r"(?:Synerg|Combinations|Spell Combos|Together)[^:]*?:\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if synergy_match:
            synergy_text = synergy_match.group(1).strip()
            # Look for bullet points or numbered items
            synergy_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", synergy_text, re.MULTILINE)
            if synergy_items:
                optimization["spell_synergies"] = [item.strip() for item in synergy_items if item.strip()]
            else:
                # Split by periods for sentence-based items
                optimization["spell_synergies"] = [s.strip() for s in re.split(r'(?<=[.!?])\s+', synergy_text) if s.strip()]
        
        return optimization