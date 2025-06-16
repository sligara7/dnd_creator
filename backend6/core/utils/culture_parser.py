"""
Simple Culture Parser for D&D Character Creation.

MINIMAL VERSION: Focused on character creation with optional cultural enhancement.
Culture features are simple suggestions that enhance but never restrict creativity.

Philosophy:
- Character creation comes first
- Culture enhances but never restricts
- Simple parsing, maximum utility
- Creative freedom is paramount
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

# ============================================================================
# MINIMAL IMPORTS - Only what we need for character creation
# ============================================================================

# Optional culture support - graceful fallback if not available
try:
    from ..enums.culture_types import CultureAuthenticityLevel
    CULTURE_SUPPORT = True
except ImportError:
    class CultureAuthenticityLevel:
        CREATIVE = "creative"
        GAMING = "gaming"
    CULTURE_SUPPORT = False

from ..exceptions.culture import CultureError


# ============================================================================
# SIMPLE PARSING RESULT - Character Focused
# ============================================================================

@dataclass(frozen=True)
class SimpleCultureResult:
    """Simple culture parsing result focused on character creation."""
    
    # Essential character creation data
    culture_name: str = "Unique Culture"
    description: str = "A unique culture for character backgrounds"
    
    # Character names (most important)
    male_names: List[str] = field(default_factory=list)
    female_names: List[str] = field(default_factory=list)
    unisex_names: List[str] = field(default_factory=list)
    family_names: List[str] = field(default_factory=list)
    
    # Optional character support
    personality_traits: List[str] = field(default_factory=list)
    background_hooks: List[str] = field(default_factory=list)
    cultural_values: List[str] = field(default_factory=list)
    
    # Gaming utility
    gaming_notes: List[str] = field(default_factory=list)
    pronunciation_tips: List[str] = field(default_factory=list)
    
    # Simple metadata
    character_ready: bool = True
    gaming_friendly: bool = True
    
    def get_all_names(self) -> List[str]:
        """Get all names for character creation."""
        return (self.male_names + self.female_names + 
                self.unisex_names + self.family_names)
    
    def get_character_inspiration(self) -> Dict[str, List[str]]:
        """Get character creation inspiration."""
        return {
            'personality_traits': self.personality_traits,
            'background_hooks': self.background_hooks,
            'cultural_values': self.cultural_values
        }


# ============================================================================
# SIMPLE CULTURE PARSER - No Overwhelming Complexity
# ============================================================================

class SimpleCultureParser:
    """Simple culture parser focused on character creation."""
    
    @staticmethod
    def parse_for_character_creation(response_text: str) -> SimpleCultureResult:
        """
        Parse LLM response for character creation.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            SimpleCultureResult ready for character creation
        """
        if not response_text or not response_text.strip():
            return SimpleCultureParser._create_fallback_culture("Empty response")
        
        try:
            # Extract basic culture info
            culture_name = SimpleCultureParser._extract_culture_name(response_text)
            description = SimpleCultureParser._extract_description(response_text)
            
            # Extract character names (most important)
            names = SimpleCultureParser._extract_character_names(response_text)
            
            # Extract optional character support
            traits = SimpleCultureParser._extract_personality_traits(response_text)
            hooks = SimpleCultureParser._extract_background_hooks(response_text)
            values = SimpleCultureParser._extract_cultural_values(response_text)
            
            # Extract gaming utility
            gaming_notes = SimpleCultureParser._extract_gaming_notes(response_text)
            pronunciation = SimpleCultureParser._extract_pronunciation_tips(response_text, names)
            
            return SimpleCultureResult(
                culture_name=culture_name,
                description=description,
                male_names=names.get('male', []),
                female_names=names.get('female', []),
                unisex_names=names.get('unisex', []),
                family_names=names.get('family', []),
                personality_traits=traits,
                background_hooks=hooks,
                cultural_values=values,
                gaming_notes=gaming_notes,
                pronunciation_tips=pronunciation,
                character_ready=True,
                gaming_friendly=True
            )
            
        except Exception as e:
            # Always return something usable for character creation
            return SimpleCultureParser._create_fallback_culture(f"Parsing error: {str(e)}")
    
    @staticmethod
    def extract_names_only(response_text: str) -> Dict[str, List[str]]:
        """
        Extract just the names for quick character creation.
        
        Args:
            response_text: Text containing names
            
        Returns:
            Dictionary of categorized names
        """
        return SimpleCultureParser._extract_character_names(response_text)
    
    @staticmethod
    def validate_for_character_use(culture_result: SimpleCultureResult) -> Tuple[bool, List[str]]:
        """
        Simple validation - always supportive, never restrictive.
        
        Args:
            culture_result: Culture result to validate
            
        Returns:
            (is_usable, helpful_suggestions) - always returns True
        """
        suggestions = []
        
        # Check names (most important)
        total_names = len(culture_result.get_all_names())
        if total_names == 0:
            suggestions.append("Consider adding some character names for players to choose from")
        elif total_names < 5:
            suggestions.append("Adding more name options would give players better variety")
        
        # Check background support
        if not culture_result.background_hooks:
            suggestions.append("Character background hooks help players create backstories")
        
        # Always usable - suggestions are just helpful
        if not suggestions:
            suggestions.append("Culture looks great for character creation!")
        
        return True, suggestions  # Always True - we support creativity
    
    # ============================================================================
    # SIMPLE EXTRACTION METHODS - No Complexity
    # ============================================================================
    
    @staticmethod
    def _extract_culture_name(text: str) -> str:
        """Extract culture name from text."""
        # Look for common patterns
        patterns = [
            r'(?:culture|people|folk|tribe|clan).*?called\s+([A-Z][A-Za-z\s]+)',
            r'([A-Z][A-Za-z\s]+)\s+(?:culture|people|folk|tribe|clan)',
            r'(?:the\s+)?([A-Z][A-Za-z\s]{3,20})\s+are\s+known',
            r'^([A-Z][A-Za-z\s]{3,20}):',  # Starting with name:
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and len(name) < 30:
                    return name.title()
        
        # Fallback
        return "Unique Culture"
    
    @staticmethod
    def _extract_description(text: str) -> str:
        """Extract simple description from text."""
        # Look for descriptive sentences
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 20 and len(sentence) < 200 and 
                any(word in sentence.lower() for word in ['culture', 'people', 'known', 'famous'])):
                return sentence + "."
        
        # Fallback
        return "A unique culture perfect for character backgrounds."
    
    @staticmethod
    def _extract_character_names(text: str) -> Dict[str, List[str]]:
        """Extract character names from text."""
        names = {'male': [], 'female': [], 'unisex': [], 'family': []}
        
        # Look for explicit name categories
        male_patterns = [
            r'male\s+names?[:\s]+([^.!?\n]+)',
            r'men[:\s]+([^.!?\n]+)',
            r'male[:\s]+([^.!?\n]+)',
        ]
        
        female_patterns = [
            r'female\s+names?[:\s]+([^.!?\n]+)',
            r'women[:\s]+([^.!?\n]+)',
            r'female[:\s]+([^.!?\n]+)',
        ]
        
        family_patterns = [
            r'family\s+names?[:\s]+([^.!?\n]+)',
            r'surnames?[:\s]+([^.!?\n]+)',
            r'last\s+names?[:\s]+([^.!?\n]+)',
        ]
        
        # Extract by category
        for pattern in male_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                names['male'].extend(SimpleCultureParser._parse_name_list(match.group(1)))
        
        for pattern in female_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                names['female'].extend(SimpleCultureParser._parse_name_list(match.group(1)))
        
        for pattern in family_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                names['family'].extend(SimpleCultureParser._parse_name_list(match.group(1)))
        
        # Look for general names if categories not found
        if not any(names.values()):
            general_names = SimpleCultureParser._extract_general_names(text)
            names['unisex'] = general_names
        
        # Clean up names
        for category in names:
            names[category] = SimpleCultureParser._clean_names(names[category])
        
        return names
    
    @staticmethod
    def _parse_name_list(name_text: str) -> List[str]:
        """Parse a list of names from text."""
        # Split by common separators
        names = re.split(r'[,;|\n]+', name_text)
        
        cleaned_names = []
        for name in names:
            # Clean up each name
            name = re.sub(r'[^\w\s\'-]', '', name).strip()
            if name and len(name) > 1 and len(name) < 25:
                cleaned_names.append(name.title())
        
        return cleaned_names
    
    @staticmethod
    def _extract_general_names(text: str) -> List[str]:
        """Extract names from general text."""
        # Look for capitalized words that might be names
        potential_names = re.findall(r'\b[A-Z][a-z]{2,15}\b', text)
        
        # Filter out common words
        common_words = {
            'The', 'This', 'That', 'They', 'There', 'Then', 'When', 'Where',
            'What', 'Who', 'Why', 'How', 'And', 'But', 'Or', 'So', 'Culture',
            'People', 'Folk', 'Tribe', 'Clan', 'Character', 'Name'
        }
        
        names = [name for name in potential_names if name not in common_words]
        
        # Remove duplicates
        seen = set()
        unique_names = []
        for name in names:
            if name not in seen:
                seen.add(name)
                unique_names.append(name)
        
        return unique_names[:10]  # Keep it reasonable
    
    @staticmethod
    def _clean_names(names: List[str]) -> List[str]:
        """Clean up name list."""
        cleaned = []
        for name in names:
            if name and len(name) > 1 and len(name) < 25:
                # Remove extra whitespace and weird characters
                clean_name = re.sub(r'\s+', ' ', name.strip())
                if clean_name:
                    cleaned.append(clean_name)
        
        return cleaned[:8]  # Keep reasonable number
    
    @staticmethod
    def _extract_personality_traits(text: str) -> List[str]:
        """Extract personality traits from text."""
        traits = []
        
        # Look for trait patterns
        trait_patterns = [
            r'(?:personality|traits?|characteristics?)[:\s]+([^.!?\n]{10,100})',
            r'(?:they are|known for being)\s+([^.!?\n]{10,100})',
            r'(?:values?|beliefs?)[:\s]+([^.!?\n]{10,100})',
        ]
        
        for pattern in trait_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Split into individual traits
                individual_traits = re.split(r'[,;]+', match)
                for trait in individual_traits:
                    trait = trait.strip()
                    if len(trait) > 5 and len(trait) < 100:
                        traits.append(trait.capitalize())
        
        return traits[:5]  # Keep it simple
    
    @staticmethod
    def _extract_background_hooks(text: str) -> List[str]:
        """Extract background hooks from text."""
        hooks = []
        
        # Look for story elements
        hook_patterns = [
            r'(?:background|story|history)[:\s]+([^.!?\n]{15,150})',
            r'(?:known for|famous for)\s+([^.!?\n]{15,150})',
            r'(?:tradition|custom)[:\s]+([^.!?\n]{15,150})',
        ]
        
        for pattern in hook_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                hook = match.strip()
                if len(hook) > 10 and len(hook) < 150:
                    hooks.append(hook.capitalize())
        
        # Add generic hooks if none found
        if not hooks:
            culture_name = SimpleCultureParser._extract_culture_name(text)
            hooks = [
                f"A member of the {culture_name} seeking adventure",
                f"Someone who left the {culture_name} to prove themselves",
                f"A keeper of {culture_name} traditions"
            ]
        
        return hooks[:4]  # Keep it reasonable
    
    @staticmethod
    def _extract_cultural_values(text: str) -> List[str]:
        """Extract cultural values from text."""
        values = []
        
        # Look for value patterns
        value_patterns = [
            r'(?:values?|beliefs?|principles?)[:\s]+([^.!?\n]{10,100})',
            r'(?:important|sacred|honored)\s+([^.!?\n]{10,100})',
        ]
        
        for pattern in value_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.strip()
                if len(value) > 5 and len(value) < 100:
                    values.append(value.capitalize())
        
        # Add generic values if none found
        if not values:
            values = [
                "Honor and loyalty",
                "Respect for traditions",
                "Community over individual"
            ]
        
        return values[:4]  # Keep it simple
    
    @staticmethod
    def _extract_gaming_notes(text: str) -> List[str]:
        """Extract gaming utility notes."""
        notes = []
        
        # Look for gaming-related content
        if any(word in text.lower() for word in ['gaming', 'table', 'session', 'campaign']):
            notes.append("Designed for gaming table use")
        
        if any(word in text.lower() for word in ['pronounce', 'pronunciation', 'easy']):
            notes.append("Names chosen for easy pronunciation")
        
        if any(word in text.lower() for word in ['character', 'player', 'roleplay']):
            notes.append("Great for character creation and roleplay")
        
        # Default gaming notes
        if not notes:
            notes = [
                "Perfect for character backgrounds",
                "Names are gaming-table friendly"
            ]
        
        return notes[:3]  # Keep it simple
    
    @staticmethod
    def _extract_pronunciation_tips(text: str, names: Dict[str, List[str]]) -> List[str]:
        """Extract pronunciation tips."""
        tips = []
        
        # Check for difficult names
        all_names = []
        for name_list in names.values():
            all_names.extend(name_list)
        
        difficult_patterns = ['sch', 'tch', 'pht', "'", 'x', 'z']
        difficult_names = []
        
        for name in all_names:
            if any(pattern in name.lower() for pattern in difficult_patterns):
                difficult_names.append(name)
        
        if difficult_names:
            tips.append(f"Some names may need practice: {', '.join(difficult_names[:3])}")
        
        # General pronunciation tips
        if any(len(name) > 8 for name in all_names):
            tips.append("Longer names can be shortened for table use")
        
        if not tips:
            tips.append("All names designed for easy gaming table use")
        
        return tips[:2]  # Keep it simple
    
    @staticmethod
    def _create_fallback_culture(reason: str) -> SimpleCultureResult:
        """Create fallback culture when parsing fails."""
        return SimpleCultureResult(
            culture_name="Creative Culture",
            description="A unique culture perfect for character creation",
            male_names=['Aeron', 'Brix', 'Cael', 'Dain'],
            female_names=['Aria', 'Bryn', 'Echo', 'Faye'],
            unisex_names=['Ash', 'Sage', 'Sky', 'Vale'],
            family_names=['Brightblade', 'Stormwind', 'Goldleaf'],
            personality_traits=[
                "Values creativity and freedom",
                "Adapts to new situations",
                "Loyal to friends and family"
            ],
            background_hooks=[
                "A creative individual seeking their place in the world",
                "Someone who brings unique perspectives to any group"
            ],
            cultural_values=[
                "Creative expression is valued",
                "Everyone deserves respect and freedom"
            ],
            gaming_notes=[
                f"Created as fallback: {reason}",
                "Perfect for any character concept"
            ],
            pronunciation_tips=["All names chosen for easy pronunciation"],
            character_ready=True,
            gaming_friendly=True
        )


# ============================================================================
# UTILITY FUNCTIONS - Simple and Helpful
# ============================================================================

def parse_culture_response(response_text: str) -> SimpleCultureResult:
    """
    Parse LLM response for character creation.
    
    Args:
        response_text: Raw LLM response
        
    Returns:
        SimpleCultureResult ready for character creation
    """
    return SimpleCultureParser.parse_for_character_creation(response_text)


def extract_character_names(response_text: str) -> Dict[str, List[str]]:
    """
    Extract character names from response.
    
    Args:
        response_text: Text containing names
        
    Returns:
        Dictionary of categorized names
    """
    return SimpleCultureParser.extract_names_only(response_text)


def validate_culture_for_characters(culture: SimpleCultureResult) -> Tuple[bool, List[str]]:
    """
    Validate culture for character creation use.
    
    Args:
        culture: Culture to validate
        
    Returns:
        (is_usable, suggestions) - always True with helpful suggestions
    """
    return SimpleCultureParser.validate_for_character_use(culture)


def get_quick_character_names(culture: SimpleCultureResult, count: int = 5) -> List[str]:
    """
    Get names for quick character creation.
    
    Args:
        culture: Culture to get names from
        count: Number of names to return
        
    Returns:
        List of names for character creation
    """
    all_names = culture.get_all_names()
    return all_names[:count] if len(all_names) >= count else all_names


def is_culture_ready_for_characters(culture: SimpleCultureResult) -> bool:
    """
    Check if culture is ready for character creation.
    
    Args:
        culture: Culture to check
        
    Returns:
        True if ready (always True - we support creativity)
    """
    return culture.character_ready


# ============================================================================
# EXPORTS - Keep it Simple
# ============================================================================

__all__ = [
    # Core classes
    "SimpleCultureResult",
    "SimpleCultureParser",
    
    # Utility functions
    "parse_culture_response",
    "extract_character_names",
    "validate_culture_for_characters",
    "get_quick_character_names",
    "is_culture_ready_for_characters"
]

# ============================================================================
# MODULE INFO
# ============================================================================

__version__ = "1.0.0"
__description__ = "Simple Culture Parser for D&D Character Creation - Culture Enhances, Never Restricts"