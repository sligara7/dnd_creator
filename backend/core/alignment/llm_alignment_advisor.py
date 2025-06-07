import logging
from typing import Dict, List, Any, Optional, Tuple

from backend.core.alignment.alignment import Alignment
from backend.core.advisor.base_advisor import BaseAdvisor

logger = logging.getLogger(__name__)

class LLMAlignmentAdvisor(Alignment, BaseAdvisor):
    """
    LLM-enhanced alignment advisor that provides nuanced, personalized
    alignment guidance using an LLM service.
    """
    
    def __init__(self, llm_service=None, data_path: str = None, cache_enabled=True):
        """
        Initialize the LLM alignment advisor.
        
        Args:
            llm_service: LLM service for alignment advice
            data_path: Optional path to alignment data files
            cache_enabled: Whether to enable response caching
        """
        # Initialize Alignment parent
        Alignment.__init__(self, data_path)
        
        # Initialize BaseAdvisor parent with an alignment-specific system prompt
        system_prompt = (
            "You are a D&D 5e (2024 rules) alignment expert. "
            "You understand the nuances of the nine alignments (Lawful Good through Chaotic Evil) "
            "and how they affect character choices and development."
        )
        BaseAdvisor.__init__(self, llm_service, system_prompt, cache_enabled)
    
    def get_all_alignments(self, suggest_for_backstory: bool = False,
                         backstory: str = None,
                         character_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Return a list of all available alignments with LLM enhancements.
        """
        # Get base alignments first
        alignments = super().get_all_alignments(False)
        
        # If not suggesting based on backstory, return standard list
        if not suggest_for_backstory or not backstory:
            return alignments
            
        try:
            # Create prompt for LLM
            prompt = self._format_prompt(
                "Suggest D&D alignments based on character backstory",
                self._build_character_context(backstory, character_data),
                [
                    "List the most fitting D&D alignments in order of relevance",
                    "For each alignment, provide a brief rationale explaining why it fits",
                    "Consider contradictions or tensions in the backstory",
                    "Note which traits suggest particular ethical or moral leanings"
                ]
            )
            
            # Get response from LLM using cached response if available
            response = self._get_llm_response(
                "alignment_suggestions", 
                prompt, 
                {"backstory": backstory[:100], "class": character_data.get("class", {}).get("name", "") if character_data else ""}
            )
            
            # Parse the response to get recommended alignments
            recommended_alignments = self._parse_alignment_recommendations(response, alignments)
            
            return recommended_alignments
            
        except Exception as e:
            logger.error(f"Error using LLM for alignment suggestions: {e}")
            # Fall back to basic implementation
            return super().get_all_alignments(suggest_for_backstory, backstory, character_data)

    def get_alignment_description(self, alignment_name: str, 
                               character_perspective: str = None) -> str:
        """
        Get a nuanced description of what an alignment means with LLM enhancement.
        """
        # Get the base description first
        base_description = super().get_alignment_description(alignment_name, None)
        
        # If no character perspective, return standard description
        if not character_perspective:
            return base_description
            
        try:
            prompt = self._format_prompt(
                f"Explain {alignment_name} from a character's perspective",
                f"Alignment: {alignment_name}\nStandard Description: {base_description}\n\nCharacter Perspective: {character_perspective}",
                [
                    "How this character would uniquely interpret this alignment",
                    "How their background affects their view of this alignment",
                    "Any tension between their worldview and the alignment's tenets",
                    "Practical examples of how they might express this alignment"
                ]
            )
            
            # Get LLM response with caching
            response = self._get_llm_response(
                "alignment_perspective", 
                prompt, 
                {"alignment": alignment_name, "perspective": character_perspective[:100]}
            )
            
            # Return the enhanced description
            return response if response else base_description
            
        except Exception as e:
            logger.error(f"Error using LLM for alignment description: {e}")
            # Fall back to basic implementation
            return super().get_alignment_description(alignment_name, character_perspective)

    def validate_alignment(self, alignment: str, 
                        explain_conflicts: bool = False,
                        character_data: Dict[str, Any] = None) -> Tuple[bool, Optional[str]]:
        """
        Check if an alignment is valid with LLM-enhanced conflict explanation.
        """
        # Validate using base method
        is_valid, base_explanation = super().validate_alignment(alignment, False)
        
        # If not valid or not explaining conflicts, return base result
        if not is_valid or not explain_conflicts or not character_data:
            return (is_valid, base_explanation)
            
        try:
            # Create prompt using base advisor method
            prompt = self._format_prompt(
                f"Analyze {alignment} alignment conflicts",
                self._build_alignment_conflict_context(alignment, character_data),
                [
                    "Identify contradictions between alignment and character elements",
                    "Point out where character elements reinforce this alignment",
                    "Suggest ways to resolve any tensions through roleplay",
                    "Note how these conflicts might create interesting character depth"
                ]
            )
            
            # Get response from LLM using the base advisor's method
            response = self._get_llm_response(
                "alignment_conflicts", 
                prompt, 
                {"alignment": alignment, "class": character_data.get("class", {}).get("name", "")}
            )
            
            # Return the enhanced explanation
            return (is_valid, response if response else base_explanation)
            
        except Exception as e:
            logger.error(f"Error using LLM for alignment conflict explanation: {e}")
            # Fall back to basic implementation
            return super().validate_alignment(alignment, explain_conflicts, character_data)

    def get_alignment_roleplay_suggestions(self, alignment: str,
                                        character_class: str = None,
                                        background: str = None,
                                        key_traits: List[str] = None) -> List[str]:
        """
        Provide LLM-enhanced roleplay guidance based on alignment and character elements.
        """
        # Get base suggestions first
        base_suggestions = super().get_alignment_roleplay_suggestions(alignment, character_class, background, key_traits)
        
        # If no character specifics, return base suggestions
        if not character_class and not background and not key_traits:
            return base_suggestions
            
        try:
            # Build character context
            context = f"Alignment: {alignment}"
            if character_class:
                context += f"\nClass: {character_class}"
            if background:
                context += f"\nBackground: {background}"
            if key_traits:
                context += f"\nKey Traits: {', '.join(key_traits)}"
            
            # Create prompt using base advisor method
            prompt = self._format_prompt(
                f"Roleplay suggestions for {alignment} character",
                context,
                [
                    "5-7 specific roleplay suggestions for this character",
                    "Examples of dialogue or behavior that reflect the alignment",
                    "Unique ways this character might express their alignment",
                    "How their class abilities and background relate to their moral stance"
                ]
            )
            
            # Get response from LLM using the base advisor's method
            response = self._get_llm_response(
                "roleplay_suggestions", 
                prompt, 
                {"alignment": alignment, "class": character_class or "", "background": background or ""}
            )
            
            # Parse the response using base advisor's helper method
            enhanced_suggestions = self._extract_list_items(response)
            
            # Combine with base suggestions, removing duplicates
            all_suggestions = base_suggestions + [
                suggestion for suggestion in enhanced_suggestions 
                if suggestion not in base_suggestions
            ]
            
            return all_suggestions
            
        except Exception as e:
            logger.error(f"Error using LLM for roleplay suggestions: {e}")
            # Fall back to basic implementation
            return base_suggestions

    def suggest_alignment_evolution(self, character_data: Dict[str, Any], 
                                 narrative_events: List[str]) -> Dict[str, Any]:
        """
        Suggest how character alignment might evolve based on narrative events.
        """
        current_alignment = character_data.get("alignment", "True Neutral")
        
        try:
            # Build context for prompt
            context = self._build_character_summary(character_data)
            context += "\n\nRecent significant events in the character's journey:\n"
            for i, event in enumerate(narrative_events, 1):
                context += f"{i}. {event}\n"
            
            # Create prompt using base advisor method
            prompt = self._format_prompt(
                "Analyze potential alignment evolution",
                context,
                [
                    "How these events might challenge or reinforce the character's alignment",
                    "Potential alignment shifts that might occur (if any)",
                    "Internal conflicts the character might experience",
                    "How these shifts would manifest in behavior"
                ]
            )
            
            # Get response from LLM using the base advisor's method
            response = self._get_llm_response(
                "alignment_evolution", 
                prompt, 
                {"alignment": current_alignment, "events_count": len(narrative_events)}
            )
            
            # Parse the response
            evolution_data = self._extract_json(response) or {}
            
            # Ensure expected structure or use default
            if not evolution_data or not isinstance(evolution_data, dict):
                evolution_data = {
                    "possible_shifts": self._extract_alignment_shifts(response),
                    "explanation": response[:500] if response else "",
                    "narrative_impact": ""
                }
            
            return {
                "current_alignment": current_alignment,
                "possible_shifts": evolution_data.get("possible_shifts", []),
                "explanation": evolution_data.get("explanation", ""),
                "narrative_impact": evolution_data.get("narrative_impact", "")
            }
            
        except Exception as e:
            logger.error(f"Error using LLM for alignment evolution: {e}")
            # Provide a basic response
            return {
                "current_alignment": current_alignment,
                "possible_shifts": [],
                "explanation": "Could not analyze potential alignment shifts.",
                "narrative_impact": ""
            }

    def generate_moral_dilemma(self, character_data: Dict[str, Any], 
                            campaign_setting: str = None) -> Dict[str, Any]:
        """
        Generate an alignment-testing moral dilemma tailored to the character.
        """
        try:
            # Build context
            context = self._build_character_summary(character_data)
            if campaign_setting:
                context += f"\nCampaign Setting: {campaign_setting}"
            
            # Create prompt using base advisor method
            prompt = self._format_prompt(
                "Create a moral dilemma scenario",
                context,
                [
                    "A complex moral/ethical choice with no clearly correct answer",
                    "3-4 distinct possible responses to the dilemma",
                    "Alignment implications for each possible choice",
                    "How this dilemma specifically challenges the character's alignment"
                ]
            )
            
            # Get response from LLM using the base advisor's method
            response = self._get_llm_response(
                "moral_dilemma", 
                prompt, 
                {"alignment": character_data.get("alignment", ""), "setting": campaign_setting or ""}
            )
            
            # Parse the response using the base advisor's JSON extraction
            dilemma_data = self._extract_json(response)
            
            # If JSON extraction failed, use structured text parsing
            if not dilemma_data:
                dilemma_data = {
                    "scenario": self._get_scenario_from_text(response),
                    "options": self._extract_list_items(response),
                    "alignment_implications": {"raw_text": response}
                }
            
            return {
                "scenario": dilemma_data.get("scenario", ""),
                "options": dilemma_data.get("options", []),
                "alignment_implications": dilemma_data.get("alignment_implications", {}),
                "setting_context": campaign_setting
            }
            
        except Exception as e:
            logger.error(f"Error using LLM for moral dilemma generation: {e}")
            # Provide a basic response
            return {
                "scenario": "Failed to generate a moral dilemma scenario.",
                "options": [],
                "alignment_implications": {},
                "setting_context": campaign_setting
            }
    
    # Helper methods specific to alignment domain
    
    def _build_character_context(self, backstory: str, character_data: Dict[str, Any] = None) -> str:
        """Build character context from backstory and data."""
        context = f"Backstory:\n{backstory}\n\n"
        
        if character_data:
            # Add more context if available
            class_name = character_data.get("class", {}).get("name", "")
            species = character_data.get("species", {}).get("name", "")
            if class_name:
                context += f"Character Class: {class_name}\n"
            if species:
                context += f"Character Species: {species}\n"
            
            # Add personality traits if available
            personality = character_data.get("personality", {})
            traits = personality.get("traits", [])
            if traits:
                context += f"Personality Traits: {', '.join(traits)}\n"
                
        return context
    
    def _build_alignment_conflict_context(self, alignment: str, character_data: Dict[str, Any]) -> str:
        """Build context for alignment conflict analysis."""
        # Extract relevant character info
        class_name = character_data.get("class", {}).get("name", "Unknown class")
        background = character_data.get("background", {}).get("name", "Unknown background")
        personality = character_data.get("personality", {})
        traits = personality.get("traits", [])
        ideals = personality.get("ideals", [])
        
        context = (
            f"Alignment: {alignment}\n"
            f"Class: {class_name}\n"
            f"Background: {background}\n"
        )
        
        if traits:
            context += f"Personality Traits: {', '.join(traits)}\n"
        if ideals:
            context += f"Ideals: {', '.join(ideals)}\n"
            
        return context
    
    def _build_character_summary(self, character_data: Dict[str, Any]) -> str:
        """Create a summary of character data for prompts."""
        # Extract basic character info
        name = character_data.get("name", "The character")
        alignment = character_data.get("alignment", "Unknown alignment")
        class_name = character_data.get("class", {}).get("name", "Unknown class")
        background = character_data.get("background", {}).get("name", "Unknown background")
        
        return f"Character: {name}, a {alignment} {class_name} with {background} background."
    
    def _parse_alignment_recommendations(self, llm_response: str, 
                                      all_alignments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse LLM response for alignment recommendations."""
        # Try to parse as JSON first using the base advisor method
        parsed_data = self._extract_json(llm_response)
        if parsed_data and isinstance(parsed_data, list):
            result = []
            for item in parsed_data:
                alignment_name = item.get("alignment", "")
                rationale = item.get("rationale", "")
                
                # Find the matching alignment data
                for alignment_data in all_alignments:
                    if alignment_data["name"] == alignment_name:
                        new_data = alignment_data.copy()
                        new_data["llm_rationale"] = rationale
                        result.append(new_data)
                        break
            
            if result:
                return result
        
        # Fallback to text-based parsing
        result = []
        alignment_names = [alignment["name"] for alignment in all_alignments]
        
        # Create a list to track which alignments were found and their positions
        found_alignments = []
        
        for alignment in alignment_names:
            # Look for the alignment name in the response
            pos = llm_response.find(alignment)
            if pos >= 0:
                found_alignments.append((alignment, pos))
        
        # Sort by position to maintain the order from the LLM response
        found_alignments.sort(key=lambda x: x[1])
        
        # Create the ordered result
        for alignment_name, pos in found_alignments:
            # Find the full alignment data
            for alignment_data in all_alignments:
                if alignment_data["name"] == alignment_name:
                    # Add LLM rationale
                    try:
                        # Extract text after the alignment name up to next alignment or paragraph
                        start_pos = pos + len(alignment_name)
                        end_pos = min(
                            [llm_response.find(other_name, start_pos) for other_name, _ in found_alignments if other_name != alignment_name and llm_response.find(other_name, start_pos) > 0] + 
                            [llm_response.find("\n\n", start_pos), len(llm_response)]
                        )
                        
                        rationale = llm_response[start_pos:end_pos].strip(" :\n-")
                        new_data = alignment_data.copy()
                        new_data["llm_rationale"] = rationale
                    except Exception as e:
                        logger.warning(f"Error extracting rationale for {alignment_name}: {e}")
                        new_data = alignment_data.copy()
                        new_data["llm_rationale"] = "Rationale could not be extracted."
                    
                    result.append(new_data)
                    break
        
        # If we didn't find any alignments, return the original list
        if not result:
            return all_alignments
            
        return result
    
    def _extract_alignment_shifts(self, text: str) -> List[str]:
        """Extract potential alignment shifts from text."""
        standard_alignments = [
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral",
            "Lawful Evil", "Neutral Evil", "Chaotic Evil"
        ]
        
        shifts = []
        for alignment in standard_alignments:
            if alignment in text:
                # Check if it appears to be suggested as a shift
                for shift_phrase in ["shift toward", "move toward", "change to", "become", "shift to"]:
                    if f"{shift_phrase} {alignment}".lower() in text.lower():
                        shifts.append(alignment)
                        break
                        
        return shifts
    
    def _get_scenario_from_text(self, text: str) -> str:
        """Extract scenario description from text response."""
        # Look for scenario section
        for marker in ["scenario:", "dilemma:", "situation:"]:
            if marker in text.lower():
                start_pos = text.lower().find(marker) + len(marker)
                end_pos = text.find("\n\n", start_pos)
                if end_pos > 0:
                    return text[start_pos:end_pos].strip()
        
        # If no scenario marker found, use the first paragraph
        paragraphs = text.split("\n\n")
        if paragraphs:
            return paragraphs[0].strip()
            
        return text[:200].strip()  # Fallback to first 200 chars