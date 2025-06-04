
class LLMAlignmentAdvisor(Alignment):
    """
    LLM-enhanced alignment advisor that provides nuanced, personalized
    alignment guidance using an LLM service.
    """
    
    def __init__(self, llm_service=None, data_path: str = None):
        """
        Initialize the LLM alignment advisor.
        
        Args:
            llm_service: LLM service for alignment advice
            data_path: Optional path to alignment data files
        """
        super().__init__(data_path)
        
        # Initialize LLM service
        if llm_service is None:
            self.llm_service = OllamaService()
        else:
            self.llm_service = llm_service

    def get_all_alignments(self, suggest_for_backstory: bool = False,
                         backstory: str = None,
                         character_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Return a list of all available alignments with LLM enhancements.
        
        Args:
            suggest_for_backstory: If True, recommend alignments based on character backstory
            backstory: Character backstory text
            character_data: Optional character data for more context
            
        Returns:
            List[Dict[str, Any]]: List of alignment data dictionaries
        """
        # Get base alignments first
        alignments = super().get_all_alignments(False)
        
        # If not suggesting based on backstory, return standard list
        if not suggest_for_backstory or not backstory:
            return alignments
            
        try:
            # Create prompt for LLM
            prompt = self._create_alignment_suggestion_prompt(backstory, character_data)
            
            # Get response from LLM
            llm_response = self.llm_service.generate_response(prompt)
            
            # Parse the response to get recommended alignments
            recommended_alignments = self._parse_alignment_recommendations(llm_response, alignments)
            
            return recommended_alignments
            
        except Exception as e:
            print(f"Error using LLM for alignment suggestions: {e}")
            # Fall back to basic implementation
            return super().get_all_alignments(suggest_for_backstory, backstory, character_data)

    def get_alignment_description(self, alignment_name: str, 
                               character_perspective: str = None) -> str:
        """
        Get a nuanced description of what an alignment means with LLM enhancement.
        
        Args:
            alignment_name: Name of the alignment
            character_perspective: Optional character perspective to contextualize the description
            
        Returns:
            str: Enhanced description of the alignment
        """
        # Get the base description first
        base_description = super().get_alignment_description(alignment_name, None)
        
        # If no character perspective, return standard description
        if not character_perspective:
            return base_description
            
        try:
            # Create prompt for LLM
            prompt = self._create_alignment_perspective_prompt(alignment_name, base_description, character_perspective)
            
            # Get response from LLM
            llm_response = self.llm_service.generate_response(prompt)
            
            # Return the enhanced description
            return llm_response if llm_response else base_description
            
        except Exception as e:
            print(f"Error using LLM for alignment description: {e}")
            # Fall back to basic implementation
            return super().get_alignment_description(alignment_name, character_perspective)

    def validate_alignment(self, alignment: str, 
                        explain_conflicts: bool = False,
                        character_data: Dict[str, Any] = None) -> Tuple[bool, Optional[str]]:
        """
        Check if an alignment is valid with LLM-enhanced conflict explanation.
        
        Args:
            alignment: Alignment to validate
            explain_conflicts: If True, provide explanation for conflicts
            character_data: Optional character data to check for conflicts
            
        Returns:
            Tuple[bool, Optional[str]]: Tuple containing validity and optional explanation
        """
        # Validate using base method
        is_valid, base_explanation = super().validate_alignment(alignment, False)
        
        # If not valid or not explaining conflicts, return base result
        if not is_valid or not explain_conflicts or not character_data:
            return (is_valid, base_explanation)
            
        try:
            # Create prompt for LLM
            prompt = self._create_alignment_conflict_prompt(alignment, character_data)
            
            # Get response from LLM
            llm_response = self.llm_service.generate_response(prompt)
            
            # Return the enhanced explanation
            return (is_valid, llm_response if llm_response else base_explanation)
            
        except Exception as e:
            print(f"Error using LLM for alignment conflict explanation: {e}")
            # Fall back to basic implementation
            return super().validate_alignment(alignment, explain_conflicts, character_data)

    def get_alignment_roleplay_suggestions(self, alignment: str,
                                        character_class: str = None,
                                        background: str = None,
                                        key_traits: List[str] = None) -> List[str]:
        """
        Provide LLM-enhanced roleplay guidance based on alignment and character elements.
        
        Args:
            alignment: Character alignment
            character_class: Optional character class for tailored suggestions
            background: Optional character background for tailored suggestions
            key_traits: Optional list of character traits for further tailoring
            
        Returns:
            List[str]: List of roleplay suggestions
        """
        # Get base suggestions first
        base_suggestions = super().get_alignment_roleplay_suggestions(alignment, character_class, background, key_traits)
        
        # If no character specifics, return base suggestions
        if not character_class and not background and not key_traits:
            return base_suggestions
            
        try:
            # Create prompt for LLM
            prompt = self._create_roleplay_suggestions_prompt(
                alignment, character_class, background, key_traits
            )
            
            # Get response from LLM
            llm_response = self.llm_service.generate_response(prompt)
            
            # Parse the response
            enhanced_suggestions = self._parse_roleplay_suggestions(llm_response)
            
            # Combine with base suggestions, removing duplicates
            all_suggestions = base_suggestions + [
                suggestion for suggestion in enhanced_suggestions 
                if suggestion not in base_suggestions
            ]
            
            return all_suggestions
            
        except Exception as e:
            print(f"Error using LLM for roleplay suggestions: {e}")
            # Fall back to basic implementation
            return base_suggestions

    def suggest_alignment_evolution(self, character_data: Dict[str, Any], 
                                 narrative_events: List[str]) -> Dict[str, Any]:
        """
        Suggest how character alignment might evolve based on narrative events.
        
        Args:
            character_data: Current character data
            narrative_events: List of significant narrative events
            
        Returns:
            Dict[str, Any]: Alignment evolution suggestions
        """
        current_alignment = character_data.get("alignment", "True Neutral")
        
        try:
            # Create prompt for LLM
            prompt = self._create_alignment_evolution_prompt(character_data, narrative_events)
            
            # Get response from LLM
            llm_response = self.llm_service.generate_response(prompt)
            
            # Parse the response
            evolution_data = self._parse_alignment_evolution(llm_response)
            
            return {
                "current_alignment": current_alignment,
                "possible_shifts": evolution_data.get("possible_shifts", []),
                "explanation": evolution_data.get("explanation", ""),
                "narrative_impact": evolution_data.get("narrative_impact", "")
            }
            
        except Exception as e:
            print(f"Error using LLM for alignment evolution: {e}")
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
        
        Args:
            character_data: Character data
            campaign_setting: Optional campaign setting for context
            
        Returns:
            Dict[str, Any]: Moral dilemma scenario with options
        """
        try:
            # Create prompt for LLM
            prompt = self._create_moral_dilemma_prompt(character_data, campaign_setting)
            
            # Get response from LLM
            llm_response = self.llm_service.generate_response(prompt)
            
            # Parse the response
            dilemma_data = self._parse_moral_dilemma(llm_response)
            
            return {
                "scenario": dilemma_data.get("scenario", ""),
                "options": dilemma_data.get("options", []),
                "alignment_implications": dilemma_data.get("alignment_implications", {}),
                "setting_context": campaign_setting
            }
            
        except Exception as e:
            print(f"Error using LLM for moral dilemma generation: {e}")
            # Provide a basic response
            return {
                "scenario": "Failed to generate a moral dilemma scenario.",
                "options": [],
                "alignment_implications": {},
                "setting_context": campaign_setting
            }

    # Helper methods for LLM prompts
    
    def _create_alignment_suggestion_prompt(self, backstory: str, character_data: Dict[str, Any] = None) -> str:
        """Create a prompt for suggesting alignments based on backstory."""
        prompt = f"Based on the following character backstory, recommend the most fitting D&D alignments (Lawful Good, Neutral Good, etc.).\n\nBackstory:\n{backstory}\n\n"
        
        if character_data:
            # Add more context if available
            class_name = character_data.get("class", {}).get("name", "")
            species = character_data.get("species", {}).get("name", "")
            if class_name:
                prompt += f"Character Class: {class_name}\n"
            if species:
                prompt += f"Character Species: {species}\n"
            
            # Add personality traits if available
            personality = character_data.get("personality", {})
            traits = personality.get("traits", [])
            if traits:
                prompt += f"Personality Traits: {', '.join(traits)}\n"
        
        prompt += "\nFor each recommended alignment, explain why it fits the character and rank them from most fitting to least fitting."
        return prompt
    
    def _create_alignment_perspective_prompt(self, alignment_name: str, base_description: str, character_perspective: str) -> str:
        """Create a prompt for contextualizing alignment description based on character perspective."""
        return (
            f"Alignment: {alignment_name}\n"
            f"Standard Description: {base_description}\n\n"
            f"Explain what the {alignment_name} alignment means from the perspective of a character who: {character_perspective}.\n\n"
            "Focus on how this character might uniquely interpret the alignment based on their background and worldview. "
            "Keep the explanation under 200 words and make it insightful and nuanced."
        )
    
    def _create_alignment_conflict_prompt(self, alignment: str, character_data: Dict[str, Any]) -> str:
        """Create a prompt for explaining potential alignment conflicts."""
        # Extract relevant character info
        class_name = character_data.get("class", {}).get("name", "Unknown class")
        background = character_data.get("background", {}).get("name", "Unknown background")
        personality = character_data.get("personality", {})
        traits = personality.get("traits", [])
        ideals = personality.get("ideals", [])
        
        prompt = (
            f"Analyze potential conflicts or synergies between the {alignment} alignment and the following character elements:\n\n"
            f"Class: {class_name}\n"
            f"Background: {background}\n"
        )
        
        if traits:
            prompt += f"Personality Traits: {', '.join(traits)}\n"
        if ideals:
            prompt += f"Ideals: {', '.join(ideals)}\n"
            
        prompt += (
            "\nIdentify any contradictions or tensions that might exist between this alignment and the character elements. "
            "Also note where the alignment reinforces certain character aspects. "
            "If there are conflicts, suggest how they might be resolved or explained through character development."
        )
            
        return prompt
    
    def _create_roleplay_suggestions_prompt(self, alignment: str,
                                        character_class: str = None,
                                        background: str = None,
                                        key_traits: List[str] = None) -> str:
        """Create a prompt for generating roleplay suggestions."""
        prompt = f"Provide specific roleplay suggestions for a {alignment} character"
        
        # Add specifics if available
        if character_class:
            prompt += f" of the {character_class} class"
        if background:
            prompt += f" with a {background} background"
        if key_traits:
            prompt += f" who has the following traits: {', '.join(key_traits)}"
            
        prompt += (
            ".\n\nProvide 5-7 specific suggestions that:\n"
            "1. Reflect the alignment's values and worldview\n"
            "2. Are tailored to the character's specific elements (class, background, traits)\n"
            "3. Could be used in practical roleplay situations\n"
            "4. Include specific examples of behaviors, decisions, or dialogue\n\n"
            "Format each suggestion as a clear, actionable statement."
        )
        
        return prompt
    
    def _create_alignment_evolution_prompt(self, character_data: Dict[str, Any], narrative_events: List[str]) -> str:
        """Create a prompt for suggesting alignment evolution."""
        current_alignment = character_data.get("alignment", "True Neutral")
        
        # Extract relevant character info
        name = character_data.get("name", "The character")
        class_name = character_data.get("class", {}).get("name", "Unknown class")
        background = character_data.get("background", {}).get("name", "Unknown background")
        
        prompt = (
            f"Character: {name}, a {class_name} with {background} background, currently {current_alignment} alignment.\n\n"
            "Recent significant events in the character's journey:\n"
        )
        
        # Add narrative events
        for i, event in enumerate(narrative_events, 1):
            prompt += f"{i}. {event}\n"
            
        prompt += (
            "\nBased on these events and the character's current alignment, analyze:\n"
            "1. How might these events challenge or reinforce the character's moral compass?\n"
            "2. What potential alignment shifts might occur (if any)?\n"
            "3. What internal conflicts might the character experience?\n"
            "4. How would these shifts manifest in the character's behavior?\n\n"
            "Provide a thoughtful analysis of possible alignment evolution with specific examples."
        )
        
        return prompt
    
    def _create_moral_dilemma_prompt(self, character_data: Dict[str, Any], campaign_setting: str = None) -> str:
        """Create a prompt for generating moral dilemmas."""
        # Extract relevant character info
        alignment = character_data.get("alignment", "True Neutral")
        class_name = character_data.get("class", {}).get("name", "Unknown class")
        
        prompt = f"Create a moral dilemma scenario for a {alignment} {class_name} character that tests their alignment values."
        
        if campaign_setting:
            prompt += f" The campaign is set in {campaign_setting}."
            
        prompt += (
            "\n\nThe scenario should:\n"
            "1. Present a complex moral or ethical choice with no clearly 'correct' answer\n"
            "2. Be relevant to the character's class abilities and alignment\n"
            "3. Include at least 3-4 distinct possible responses\n"
            "4. Explain the potential alignment implications of each choice\n"
            "5. Be specific enough to use in a D&D session\n\n"
            "Provide the scenario, options, and analysis of alignment implications for each option."
        )
        
        return prompt
    
    # Parser methods for LLM responses
    
    def _parse_alignment_recommendations(self, llm_response: str, 
                                      all_alignments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse LLM response for alignment recommendations."""
        # This is a simplified parser - a real implementation would be more sophisticated
        # For now, we'll just look for alignment names in the response
        
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
        for alignment_name, _ in found_alignments:
            # Find the full alignment data
            for alignment_data in all_alignments:
                if alignment_data["name"] == alignment_name:
                    # Add LLM rationale
                    try:
                        # Extract text after the alignment name up to next alignment or paragraph
                        start_pos = llm_response.find(alignment_name) + len(alignment_name)
                        end_pos = min(
                            [llm_response.find(other_name, start_pos) for other_name, _ in found_alignments if other_name != alignment_name and llm_response.find(other_name, start_pos) > 0] + 
                            [llm_response.find("\n\n", start_pos), len(llm_response)]
                        )
                        
                        rationale = llm_response[start_pos:end_pos].strip(" :\n-")
                        alignment_data = alignment_data.copy()
                        alignment_data["llm_rationale"] = rationale
                    except:
                        alignment_data = alignment_data.copy()
                        alignment_data["llm_rationale"] = "Rationale could not be extracted."
                    
                    result.append(alignment_data)
                    break
        
        # If we didn't find any alignments, return the original list
        if not result:
            return all_alignments
            
        return result
    
    def _parse_roleplay_suggestions(self, llm_response: str) -> List[str]:
        """Parse LLM response for roleplay suggestions."""
        # Look for numbered lists, bullet points, or paragraphs
        suggestions = []
        
        # Split by numbers at the start of lines
        number_splits = []
        for i in range(1, 10):  # Check for numbers 1-9
            number_splits.extend([line.strip() for line in llm_response.split(f"\n{i}. ") if line.strip()])
            number_splits.extend([line.strip() for line in llm_response.split(f"\n{i}) ") if line.strip()])
            
        # Split by bullet points
        bullet_splits = []
        for bullet in ["- ", "• "]:
            bullet_splits.extend([line.strip() for line in llm_response.split(f"\n{bullet}") if line.strip()])
            
        # Combine and clean up results
        all_splits = number_splits + bullet_splits
        
        if all_splits:
            # Remove the first item if it's likely a header or intro text
            if len(all_splits) > 1 and len(all_splits[0].split()) > 15:
                all_splits = all_splits[1:]
                
            # Clean up items
            for item in all_splits:
                # Remove leading numbers or bullets
                cleaned = item
                for prefix in [f"{i}. " for i in range(1, 10)] + [f"{i}) " for i in range(1, 10)] + ["- ", "• "]:
                    if cleaned.startswith(prefix):
                        cleaned = cleaned[len(prefix):]
                        
                suggestions.append(cleaned)
                
        # If no structured items found, split by newlines
        if not suggestions:
            suggestions = [line.strip() for line in llm_response.split('\n') if line.strip() and len(line.strip()) > 10]
            
        return suggestions
    
    def _parse_alignment_evolution(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response for alignment evolution data."""
        # This is a simplified parser
        result = {
            "possible_shifts": [],
            "explanation": llm_response[:500],  # Truncate for explanation
            "narrative_impact": ""
        }
        
        # Look for alignment names in the response to identify possible shifts
        standard_alignments = [
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral",
            "Lawful Evil", "Neutral Evil", "Chaotic Evil"
        ]
        
        for alignment in standard_alignments:
            if alignment in llm_response:
                # Check if it appears to be suggested as a shift
                for shift_phrase in ["shift toward", "move toward", "change to", "become", "shift to"]:
                    if f"{shift_phrase} {alignment}" in llm_response.lower():
                        result["possible_shifts"].append(alignment)
                        break
        
        # Look for narrative impact section
        impact_markers = ["narrative impact", "impact on the character", "behavioral changes"]
        for marker in impact_markers:
            if marker in llm_response.lower():
                pos = llm_response.lower().find(marker)
                result["narrative_impact"] = llm_response[pos:pos+300]  # Take a portion after the marker
                break
                
        return result
    
    def _parse_moral_dilemma(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response for moral dilemma data."""
        # This is a simplified parser
        result = {
            "scenario": "",
            "options": [],
            "alignment_implications": {}
        }
        
        # Try to find a scenario section
        scenario_markers = ["scenario:", "dilemma:", "situation:"]
        for marker in scenario_markers:
            if marker in llm_response.lower():
                pos = llm_response.lower().find(marker) + len(marker)
                end_pos = llm_response.find("\n\n", pos)
                if end_pos > 0:
                    result["scenario"] = llm_response[pos:end_pos].strip()
                    break
        
        # If no scenario found, use the first paragraph
        if not result["scenario"]:
            paragraphs = llm_response.split("\n\n")
            if paragraphs:
                result["scenario"] = paragraphs[0]
                
        # Look for options section
        options_section = ""
        options_markers = ["options:", "choices:", "possible actions:"]
        for marker in options_markers:
            if marker in llm_response.lower():
                pos = llm_response.lower().find(marker) + len(marker)
                end_pos = llm_response.find("\n\n", pos)
                options_section = llm_response[pos:end_pos if end_pos > 0 else len(llm_response)].strip()
                break
        
        # Parse options
        if options_section:
            # Try to split by numbering or bullet points
            option_splits = []
            for prefix in [r"\n\d+\. ", r"\n\d+\) ", r"\n- ", r"\n• "]:
                import re
                splits = re.split(prefix, options_section)
                if len(splits) > 1:
                    option_splits = splits[1:]  # Skip the first split which is before any marker
                    break
            
            # If we found structured options
            if option_splits:
                result["options"] = [option.strip() for option in option_splits]
            else:
                # Fallback to paragraph splits
                option_splits = options_section.split("\n")
                result["options"] = [option.strip() for option in option_splits if option.strip()]
                
        # Look for alignment implications
        implications_section = ""
        implication_markers = ["alignment implications:", "implications:", "alignment consequences:"]
        for marker in implication_markers:
            if marker in llm_response.lower():
                pos = llm_response.lower().find(marker) + len(marker)
                implications_section = llm_response[pos:].strip()
                break
        
        # Parse implications (simplified - just store the whole section)
        if implications_section:
            result["alignment_implications"] = {"text": implications_section}
                
        return result