# alignment.py
# Description: Handles character alignment options and their implications.

# must adhere to abstract_alignment.py interface for alignment management in D&D 2024.

from typing import List, Dict, Any, Optional, Tuple
import json
from pathlib import Path

try:
    from backend.core.alignment.abstract_alignment import AbstractAlignment
    from backend.core.ollama_service import OllamaService
except ImportError:
    # Fallback for development
    AbstractAlignment = object
    class OllamaService:
        def __init__(self): pass
        def generate_response(self, prompt): return "LLM service not available"

from backend.core.alignment.llm_alignment_advisor import LLMAlignmentAdvisor

class Alignment(AbstractAlignment):
    """
    Base class for handling character alignment options and their implications in D&D.
    Provides methods to retrieve and validate alignments and get alignment descriptions.
    """

    def __init__(self, data_path: str = None):
        """
        Initialize the Alignment handler.
        
        Args:
            data_path: Optional path to alignment data files
        """
        self.data_path = Path(data_path) if data_path else Path("backend/data/rules")
        self._load_alignment_data()
        
        # Standard D&D alignments
        self.standard_alignments = [
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral",
            "Lawful Evil", "Neutral Evil", "Chaotic Evil",
            "Unaligned"  # For creatures without moral capacity
        ]
        
    def _load_alignment_data(self):
        """Load alignment data from JSON files."""
        try:
            alignment_path = self.data_path / "alignments.json"
            if alignment_path.exists():
                with open(alignment_path, "r") as f:
                    self.alignment_data = json.load(f)
            else:
                # Default alignment data if file doesn't exist
                self.alignment_data = self._default_alignment_data()
                
        except Exception as e:
            print(f"Error loading alignment data: {e}")
            self.alignment_data = self._default_alignment_data()
            
    def _default_alignment_data(self) -> Dict[str, Dict[str, str]]:
        """Create default alignment data structure."""
        return {
            "Lawful Good": {
                "description": "Creatures that act as good people are expected or required to act. They combine a commitment to oppose evil with the discipline to fight relentlessly.",
                "examples": "Gold dragons, paladins",
                "roleplay_suggestions": [
                    "Values honor and compassion equally",
                    "Believes in justice tempered with mercy",
                    "Follows rules but places moral good above blind obedience"
                ]
            },
            "Neutral Good": {
                "description": "Creatures that do the best they can to help others according to their needs. Many celestials are neutral good.",
                "examples": "Celestials, many rangers",
                "roleplay_suggestions": [
                    "Does good for goodness' sake without concern for rules",
                    "Helps others regardless of laws or traditions",
                    "Values flexibility in approach while maintaining moral standards"
                ]
            },
            "Chaotic Good": {
                "description": "Creatures that act as their conscience directs, with little regard for what others expect. Copper dragons and many elves are chaotic good.",
                "examples": "Copper dragons, many elves",
                "roleplay_suggestions": [
                    "Values personal freedom and the freedom of others",
                    "Rebels against authority that restricts liberty",
                    "Believes kindness cannot be legislated"
                ]
            },
            "Lawful Neutral": {
                "description": "Creatures that act in accordance with law, tradition, or personal codes. Many monks and wizards are lawful neutral.",
                "examples": "Monks, certain wizards",
                "roleplay_suggestions": [
                    "Values consistency and order above all",
                    "Believes in systems and structures as necessary for society",
                    "Follows rules regardless of outcome"
                ]
            },
            "True Neutral": {
                "description": "Creatures most neutral in ethical and moral concerns, often by choice. Druids often strive for this neutrality.",
                "examples": "Many druids, typical animals",
                "roleplay_suggestions": [
                    "Maintains balance between extremes",
                    "Avoids taking sides in conflicts of ideology",
                    "Considers the big picture beyond good and evil"
                ]
            },
            "Chaotic Neutral": {
                "description": "Creatures that follow their whims, valuing their freedom. Many rogues and bards are chaotic neutral.",
                "examples": "Many rogues, bards",
                "roleplay_suggestions": [
                    "Values personal freedom above all else",
                    "Acts on instinct rather than planning",
                    "Dislikes being tied down by obligations"
                ]
            },
            "Lawful Evil": {
                "description": "Creatures that methodically take what they want, within the limits of a code of tradition, loyalty, or order.",
                "examples": "Devils, hobgoblins",
                "roleplay_suggestions": [
                    "Uses systems and laws to their advantage",
                    "Keeps their word but finds loopholes",
                    "Values order as a means to power"
                ]
            },
            "Neutral Evil": {
                "description": "Creatures that do whatever they can get away with, without compassion or qualms.",
                "examples": "Yugoloths, drow",
                "roleplay_suggestions": [
                    "Acts in self-interest without moral restraint",
                    "Shows no loyalty beyond what's immediately useful",
                    "Pragmatic about achieving goals regardless of who gets hurt"
                ]
            },
            "Chaotic Evil": {
                "description": "Creatures that act with arbitrary violence, spurred by their greed, hatred, or bloodlust.",
                "examples": "Demons, orcs",
                "roleplay_suggestions": [
                    "Revels in destruction and discord",
                    "Unpredictable and impulsive in pursuing desires",
                    "Rejects any constraints on behavior"
                ]
            },
            "Unaligned": {
                "description": "Creatures without the capacity for ethical or moral reasoning. Many animals and magical beasts are unaligned.",
                "examples": "Animals, constructs",
                "roleplay_suggestions": [
                    "Acts on instinct rather than moral reasoning",
                    "Not evil or good, simply exists",
                    "Follows nature without moral consideration"
                ]
            }
        }

    def get_all_alignments(self, suggest_for_backstory: bool = False,
                         backstory: str = None,
                         character_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Return a list of all available alignments.
        
        Args:
            suggest_for_backstory: If True, recommend alignments based on character backstory
            backstory: Character backstory text
            character_data: Optional character data for more context
            
        Returns:
            List[Dict[str, Any]]: List of alignment data dictionaries
        """
        # Basic implementation returns all alignments
        alignments = []
        
        for alignment_name in self.standard_alignments:
            alignment_info = {
                "name": alignment_name,
                "description": self.get_alignment_description(alignment_name)
            }
            
            # Add roleplay suggestions
            if alignment_name in self.alignment_data:
                if "roleplay_suggestions" in self.alignment_data[alignment_name]:
                    alignment_info["roleplay_suggestions"] = self.alignment_data[alignment_name]["roleplay_suggestions"]
                if "examples" in self.alignment_data[alignment_name]:
                    alignment_info["examples"] = self.alignment_data[alignment_name]["examples"]
            
            alignments.append(alignment_info)
        
        # If not suggesting based on backstory, return all
        if not suggest_for_backstory or not backstory:
            return alignments
        
        # Simplified recommendation logic (a real implementation would be more sophisticated)
        recommended_alignments = []
        lower_backstory = backstory.lower()
        
        # Very simple keyword matching
        for alignment in alignments:
            score = 0
            name = alignment["name"].lower()
            
            # Simple keyword matching
            if "honor" in lower_backstory and "lawful" in name:
                score += 1
            if "compassion" in lower_backstory and "good" in name:
                score += 1
            if "freedom" in lower_backstory and "chaotic" in name:
                score += 1
            if "balance" in lower_backstory and "neutral" in name:
                score += 1
            if "selfish" in lower_backstory and "evil" in name:
                score += 1
                
            alignment["relevance"] = score
            recommended_alignments.append(alignment)
        
        # Sort by relevance
        return sorted(recommended_alignments, key=lambda x: x.get("relevance", 0), reverse=True)

    def get_alignment_description(self, alignment_name: str, 
                               character_perspective: str = None) -> str:
        """
        Get a description of what an alignment means.
        
        Args:
            alignment_name: Name of the alignment
            character_perspective: Optional character perspective to contextualize the description
            
        Returns:
            str: Description of the alignment
        """
        # Basic implementation returns standard description
        if alignment_name in self.alignment_data:
            base_description = self.alignment_data[alignment_name].get("description", "No description available.")
        else:
            return "Unknown alignment."
            
        # If no character perspective provided, return standard description
        if not character_perspective:
            return base_description
            
        # A real implementation would use more sophisticated context analysis
        # This is a simple example of how perspective might modify the description
        if "Lawful" in alignment_name and "rebel" in character_perspective.lower():
            return f"{base_description} From your rebellious perspective, this might feel constraining, but remember that even rebellion often follows its own codes and principles."
            
        if "Chaotic" in alignment_name and "order" in character_perspective.lower():
            return f"{base_description} From your orderly perspective, this might seem disruptive, but such freedom often brings innovation and breaks harmful traditions."
            
        # Default to adding a simple contextual note
        return f"{base_description} From your perspective as {character_perspective}, this alignment represents a particular approach to morality and ethics that may align with or challenge your worldview."

    def validate_alignment(self, alignment: str, 
                        explain_conflicts: bool = False,
                        character_data: Dict[str, Any] = None) -> Tuple[bool, Optional[str]]:
        """
        Check if an alignment is valid.
        
        Args:
            alignment: Alignment to validate
            explain_conflicts: If True, provide explanation for invalid alignments
            character_data: Optional character data to check for conflicts
            
        Returns:
            Tuple[bool, Optional[str]]: Tuple containing validity and optional explanation
        """
        # Basic validation just checks if it's a standard alignment
        is_valid = alignment in self.standard_alignments
        
        if not is_valid and not explain_conflicts:
            return (False, None)
        
        if not is_valid:
            return (False, f"'{alignment}' is not a valid alignment. Valid alignments are: {', '.join(self.standard_alignments)}.")
        
        # If no character data or not requesting explanation, return valid without explanation
        if not explain_conflicts or not character_data:
            return (True, None)
        
        # Check for potential conflicts with character data
        conflicts = []
        
        # Example conflict detection - class conflicts
        character_class = character_data.get("class", {}).get("name", "").lower()
        if character_class == "paladin" and "evil" in alignment.lower():
            conflicts.append("Paladins traditionally follow good alignments, so an evil paladin may face challenges.")
            
        # Background conflicts
        background = character_data.get("background", {}).get("name", "").lower()
        if background == "criminal" and "lawful" in alignment.lower():
            conflicts.append("A criminal background may conflict with a lawful alignment unless there's a compelling reason for the shift.")
        
        # Personality conflicts
        personality = character_data.get("personality", {})
        traits = personality.get("traits", [])
        
        for trait in traits:
            if "honest" in trait.lower() and "evil" in alignment.lower():
                conflicts.append("An honest personality trait may conflict with an evil alignment.")
            if "rebellious" in trait.lower() and "lawful" in alignment.lower():
                conflicts.append("A rebellious personality trait may conflict with a lawful alignment.")
        
        if conflicts:
            return (True, "Potential character conflicts: " + " ".join(conflicts))
        
        return (True, "Alignment is valid and consistent with character data.")

    def get_alignment_roleplay_suggestions(self, alignment: str,
                                        character_class: str = None,
                                        background: str = None,
                                        key_traits: List[str] = None) -> List[str]:
        """
        Provide roleplay guidance based on alignment.
        
        Args:
            alignment: Character alignment
            character_class: Optional character class for tailored suggestions
            background: Optional character background for tailored suggestions
            key_traits: Optional list of character traits for further tailoring
            
        Returns:
            List[str]: List of roleplay suggestions
        """
        # Default suggestions from alignment data
        if alignment in self.alignment_data and "roleplay_suggestions" in self.alignment_data[alignment]:
            suggestions = self.alignment_data[alignment]["roleplay_suggestions"].copy()
        else:
            suggestions = ["No specific roleplay suggestions available for this alignment."]
            
        # Basic implementation without character specifics
        if not character_class and not background and not key_traits:
            return suggestions
            
        # Add class-specific suggestions
        if character_class:
            class_suggestions = self._get_class_alignment_suggestions(alignment, character_class)
            suggestions.extend(class_suggestions)
            
        # Add background-specific suggestions
        if background:
            bg_suggestions = self._get_background_alignment_suggestions(alignment, background)
            suggestions.extend(bg_suggestions)
            
        # Incorporate key traits if provided
        if key_traits:
            trait_suggestions = self._get_trait_alignment_suggestions(alignment, key_traits)
            suggestions.extend(trait_suggestions)
            
        return suggestions

    def _get_class_alignment_suggestions(self, alignment: str, character_class: str) -> List[str]:
        """Get class-specific alignment roleplay suggestions."""
        class_lower = character_class.lower()
        alignment_lower = alignment.lower()
        suggestions = []
        
        # These are example mappings - a real implementation would have more extensive options
        if "paladin" in class_lower:
            if "lawful good" in alignment_lower:
                suggestions.append("Embody your oath through acts of mercy and justice that inspire others.")
            elif "good" in alignment_lower:
                suggestions.append("Focus on the spirit of your oath rather than exact wording.")
            elif "evil" in alignment_lower:
                suggestions.append("Consider how your oath can be twisted to serve your own ends while technically fulfilling it.")
                
        elif "rogue" in class_lower:
            if "lawful" in alignment_lower:
                suggestions.append("Use your skills within the bounds of law, perhaps as an investigator or sanctioned agent.")
            elif "chaotic" in alignment_lower:
                suggestions.append("Your flexible morality lets you adapt to circumstances that others find constraining.")
            elif "good" in alignment_lower:
                suggestions.append("Target those who abuse power and wealth, becoming a champion of the downtrodden.")
                
        elif "wizard" in class_lower:
            if "lawful" in alignment_lower:
                suggestions.append("Your study of magic follows strict methodologies and ethical guidelines.")
            elif "chaotic" in alignment_lower:
                suggestions.append("Your magical research pushes boundaries that others fear to approach.")
            elif "evil" in alignment_lower:
                suggestions.append("Knowledge is power, and you see no reason to limit your studies by others' moral concerns.")
                
        return suggestions

    def _get_background_alignment_suggestions(self, alignment: str, background: str) -> List[str]:
        """Get background-specific alignment roleplay suggestions."""
        bg_lower = background.lower()
        alignment_lower = alignment.lower()
        suggestions = []
        
        # These are example mappings
        if "criminal" in bg_lower:
            if "lawful" in alignment_lower:
                suggestions.append("You've reformed and now use your knowledge of criminal methods to uphold the law.")
            elif "good" in alignment_lower:
                suggestions.append("You may break unjust laws to help those in need, like a fantasy Robin Hood.")
                
        elif "noble" in bg_lower:
            if "lawful" in alignment_lower:
                suggestions.append("You believe your privilege comes with responsibility to uphold social order.")
            elif "chaotic" in alignment_lower:
                suggestions.append("You reject the constraints of your upbringing, using your privilege to challenge tradition.")
            elif "evil" in alignment_lower:
                suggestions.append("You believe your noble birth entitles you to power over others.")
                
        elif "soldier" in bg_lower:
            if "lawful" in alignment_lower:
                suggestions.append("The discipline of military life has shaped your approach to all problems.")
            elif "chaotic" in alignment_lower:
                suggestions.append("Your experiences in war showed you the futility of blind obedience.")
                
        return suggestions

    def _get_trait_alignment_suggestions(self, alignment: str, traits: List[str]) -> List[str]:
        """Get trait-specific alignment roleplay suggestions."""
        alignment_lower = alignment.lower()
        suggestions = []
        
        # Process each trait
        for trait in traits:
            trait_lower = trait.lower()
            
            if "ambitious" in trait_lower:
                if "good" in alignment_lower:
                    suggestions.append("Your ambition is tempered by consideration for how your actions affect others.")
                elif "evil" in alignment_lower:
                    suggestions.append("Your ambition drives you to seek power regardless of who gets hurt.")
                    
            elif "cautious" in trait_lower:
                if "lawful" in alignment_lower:
                    suggestions.append("Your caution manifests as careful adherence to established procedures.")
                elif "chaotic" in alignment_lower:
                    suggestions.append("Your caution makes you skeptical of authorities and established systems.")
                    
            elif "generous" in trait_lower:
                if "good" in alignment_lower:
                    suggestions.append("Your generosity comes from genuine compassion for others.")
                elif "evil" in alignment_lower:
                    suggestions.append("Your generosity is calculated to create obligations and dependencies.")
                    
        return suggestions

