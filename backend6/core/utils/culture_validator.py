"""
Simple Culture Validation for D&D Character Creation.

MINIMAL VERSION: Focused on character creation with optional cultural enhancement.
Culture validation is supportive and enhancing - never restrictive or bureaucratic.

Philosophy:
- Character creation comes first
- Culture enhances but never restricts
- Simple validation, maximum creativity
- Creative freedom is paramount
"""

from typing import Dict, List, Optional, Tuple, Any
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
# SIMPLE VALIDATION RESULT - Character Focused
# ============================================================================

@dataclass(frozen=True)
class SimpleValidationResult:
    """Simple validation result focused on character creation support."""
    
    # Essential character creation metrics
    is_usable: bool = True  # Almost always True - we support creativity
    character_ready: bool = True
    gaming_friendly: bool = True
    
    # Simple scores (0.0 to 1.0)
    name_quality: float = 0.5
    background_support: float = 0.5
    creative_potential: float = 0.5
    overall_score: float = 0.5
    
    # Helpful suggestions (never requirements)
    helpful_suggestions: List[str] = field(default_factory=list)
    creative_opportunities: List[str] = field(default_factory=list)
    gaming_tips: List[str] = field(default_factory=list)
    
    # Simple analysis
    total_names: int = 0
    background_elements: int = 0
    
    def get_character_readiness_percentage(self) -> int:
        """Get character creation readiness as percentage."""
        return int(self.overall_score * 100)
    
    def is_good_for_characters(self) -> bool:
        """Check if culture is good for character creation."""
        return self.overall_score >= 0.3  # Very low bar - we support creativity


# ============================================================================
# SIMPLE CULTURE VALIDATOR - No Bureaucracy
# ============================================================================

class SimpleCultureValidator:
    """Simple culture validator focused on character creation support."""
    
    @staticmethod
    def validate_for_character_creation(culture_data: Dict[str, Any]) -> SimpleValidationResult:
        """
        Simple validation for character creation - always supportive.
        
        Args:
            culture_data: Dictionary containing culture information
            
        Returns:
            SimpleValidationResult with helpful suggestions (never restrictions)
        """
        if not culture_data:
            return SimpleCultureValidator._create_empty_culture_result()
        
        try:
            # Simple assessments
            name_assessment = SimpleCultureValidator._assess_names_simply(culture_data)
            background_assessment = SimpleCultureValidator._assess_background_simply(culture_data)
            creative_assessment = SimpleCultureValidator._assess_creativity_simply(culture_data)
            
            # Collect helpful suggestions (never requirements)
            suggestions = []
            opportunities = []
            gaming_tips = []
            
            # Name suggestions
            if name_assessment['total_names'] == 0:
                suggestions.append("Adding some character names would help players create characters")
                opportunities.append("Names are the most useful element for character creation")
            elif name_assessment['total_names'] < 5:
                opportunities.append("More name variety gives players better character options")
            
            if name_assessment['gaming_friendly'] < 0.5:
                gaming_tips.append("Shorter names are easier to use at gaming tables")
            
            # Background suggestions
            if background_assessment['elements_count'] == 0:
                opportunities.append("Cultural background elements help players develop character stories")
            elif background_assessment['elements_count'] < 3:
                suggestions.append("Additional cultural elements could inspire more character concepts")
            
            # Creative suggestions
            if creative_assessment['uniqueness'] < 0.3:
                opportunities.append("Unique cultural features make characters more interesting")
            
            # Calculate simple overall score
            overall_score = (
                name_assessment['quality_score'] * 0.4 +
                background_assessment['support_score'] * 0.3 +
                creative_assessment['creativity_score'] * 0.3
            )
            
            return SimpleValidationResult(
                is_usable=True,  # Always usable - we support creativity
                character_ready=name_assessment['total_names'] > 0 or background_assessment['elements_count'] > 0,
                gaming_friendly=name_assessment['gaming_friendly'] > 0.3,
                name_quality=name_assessment['quality_score'],
                background_support=background_assessment['support_score'],
                creative_potential=creative_assessment['creativity_score'],
                overall_score=overall_score,
                helpful_suggestions=suggestions,
                creative_opportunities=opportunities,
                gaming_tips=gaming_tips,
                total_names=name_assessment['total_names'],
                background_elements=background_assessment['elements_count']
            )
            
        except Exception as e:
            # Always return something usable
            return SimpleCultureValidator._create_fallback_result(str(e))
    
    @staticmethod
    def quick_character_check(culture_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Quick check if culture is ready for character creation.
        
        Args:
            culture_data: Culture to check
            
        Returns:
            (is_ready, helpful_suggestions) - always supportive
        """
        result = SimpleCultureValidator.validate_for_character_creation(culture_data)
        
        suggestions = []
        if result.total_names == 0:
            suggestions.append("Consider adding some character names")
        if result.background_elements == 0:
            suggestions.append("Cultural background elements help character development")
        if not result.gaming_friendly:
            suggestions.append("Gaming-friendly features improve table experience")
        
        if not suggestions:
            suggestions.append("Culture looks great for character creation!")
        
        return result.is_good_for_characters(), suggestions
    
    @staticmethod
    def get_character_enhancement_tips(culture_data: Dict[str, Any]) -> List[str]:
        """
        Get helpful tips for enhancing culture for character creation.
        
        Args:
            culture_data: Culture to enhance
            
        Returns:
            List of helpful enhancement tips (never requirements)
        """
        result = SimpleCultureValidator.validate_for_character_creation(culture_data)
        
        tips = []
        tips.extend(result.helpful_suggestions)
        tips.extend(result.creative_opportunities)
        tips.extend(result.gaming_tips)
        
        # Add general character creation tips
        if result.overall_score < 0.7:
            tips.extend([
                "Character names are the most important element for players",
                "Cultural traits inspire character personality development",
                "Background hooks provide ready-made character stories",
                "Gaming-friendly elements improve table experience"
            ])
        
        return tips[:6]  # Keep it simple
    
    # ============================================================================
    # SIMPLE ASSESSMENT METHODS - No Complexity
    # ============================================================================
    
    @staticmethod
    def _assess_names_simply(culture_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simple name assessment for character creation."""
        assessment = {
            'total_names': 0,
            'quality_score': 0.0,
            'gaming_friendly': 0.0,
            'variety_score': 0.0
        }
        
        # Collect all names
        name_categories = ['male_names', 'female_names', 'unisex_names', 'family_names', 'titles']
        all_names = []
        
        for category in name_categories:
            if category in culture_data and isinstance(culture_data[category], list):
                names = [name for name in culture_data[category] if name and name.strip()]
                all_names.extend(names)
        
        assessment['total_names'] = len(all_names)
        
        if all_names:
            # Simple quality assessment
            avg_length = sum(len(name) for name in all_names) / len(all_names)
            gaming_friendly_count = sum(1 for name in all_names if len(name) <= 8 and "'" not in name)
            
            assessment['quality_score'] = min(1.0, len(all_names) / 10)  # Up to 10 names = perfect
            assessment['gaming_friendly'] = gaming_friendly_count / len(all_names)
            assessment['variety_score'] = min(1.0, len(set(name[0] for name in all_names)) / 10)  # Letter variety
        
        return assessment
    
    @staticmethod
    def _assess_background_simply(culture_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simple background assessment for character creation."""
        assessment = {
            'elements_count': 0,
            'support_score': 0.0,
            'character_hooks': 0
        }
        
        # Check for character-relevant background elements
        background_elements = [
            'cultural_traits', 'values', 'traditions', 'customs', 'beliefs',
            'character_hooks', 'background_hooks', 'occupations', 'social_structure'
        ]
        
        found_elements = 0
        character_hooks = 0
        
        for element in background_elements:
            if element in culture_data and culture_data[element]:
                found_elements += 1
                if 'hook' in element:
                    character_hooks += 1
        
        assessment['elements_count'] = found_elements
        assessment['character_hooks'] = character_hooks
        assessment['support_score'] = min(1.0, found_elements / 5)  # Up to 5 elements = good support
        
        return assessment
    
    @staticmethod
    def _assess_creativity_simply(culture_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simple creativity assessment for character inspiration."""
        assessment = {
            'creativity_score': 0.0,
            'uniqueness': 0.0,
            'inspiration_potential': 0.0
        }
        
        # Check for creative/unique elements
        creative_elements = [
            'unique_features', 'mysteries', 'legends', 'arts', 'crafts',
            'philosophy', 'distinctive_traits', 'special_practices'
        ]
        
        found_creative = sum(1 for element in creative_elements if element in culture_data and culture_data[element])
        
        assessment['uniqueness'] = min(1.0, found_creative / 4)  # Up to 4 unique elements = very creative
        assessment['inspiration_potential'] = assessment['uniqueness']  # Simple correlation
        assessment['creativity_score'] = assessment['uniqueness']
        
        return assessment
    
    @staticmethod
    def _create_empty_culture_result() -> SimpleValidationResult:
        """Create result for empty culture data."""
        return SimpleValidationResult(
            is_usable=True,  # Still usable - we support creativity
            character_ready=False,
            gaming_friendly=True,
            helpful_suggestions=[
                "Adding character names would be the most helpful starting point",
                "Cultural background elements help players develop character stories"
            ],
            creative_opportunities=[
                "Any cultural content helps character creation",
                "Names are the most important element for players"
            ],
            total_names=0,
            background_elements=0
        )
    
    @staticmethod
    def _create_fallback_result(error: str) -> SimpleValidationResult:
        """Create fallback result when assessment fails."""
        return SimpleValidationResult(
            is_usable=True,  # Always usable - we support creativity
            character_ready=True,
            gaming_friendly=True,
            helpful_suggestions=[
                f"Assessment had an issue ({error[:50]}), but culture is still usable",
                "Focus on what helps character creation most"
            ],
            creative_opportunities=[
                "Any culture can inspire character creation",
                "Names and background elements are most helpful for players"
            ],
            gaming_tips=[
                "Keep names simple for gaming table use",
                "Cultural elements should inspire, not restrict"
            ]
        )


# ============================================================================
# UTILITY FUNCTIONS - Simple and Helpful
# ============================================================================

def validate_culture_for_characters(culture_data: Dict[str, Any]) -> SimpleValidationResult:
    """
    Validate culture for character creation - always supportive.
    
    Args:
        culture_data: Dictionary containing culture information
        
    Returns:
        SimpleValidationResult with helpful suggestions
    """
    return SimpleCultureValidator.validate_for_character_creation(culture_data)


def quick_culture_assessment(culture_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Quick assessment for basic culture validation.
    
    Args:
        culture_data: Dictionary containing culture information
        
    Returns:
        Dictionary with basic assessment metrics
    """
    result = SimpleCultureValidator.validate_for_character_creation(culture_data)
    
    return {
        'is_usable': result.is_usable,
        'character_ready': result.character_ready,
        'gaming_friendly': result.gaming_friendly,
        'readiness_percentage': result.get_character_readiness_percentage(),
        'total_names': result.total_names,
        'background_elements': result.background_elements,
        'top_suggestions': result.helpful_suggestions[:3],
        'creative_opportunities': result.creative_opportunities[:2]
    }


def is_culture_ready_for_characters(culture_data: Dict[str, Any]) -> bool:
    """
    Check if culture is ready for character creation.
    
    Args:
        culture_data: Culture to check
        
    Returns:
        True if ready (very low bar - we support creativity)
    """
    result = SimpleCultureValidator.validate_for_character_creation(culture_data)
    return result.is_good_for_characters()


def get_character_creation_tips(culture_data: Dict[str, Any]) -> List[str]:
    """
    Get helpful tips for character creation with this culture.
    
    Args:
        culture_data: Culture to get tips for
        
    Returns:
        List of helpful tips for character creation
    """
    return SimpleCultureValidator.get_character_enhancement_tips(culture_data)


def validate_culture_names_for_gaming(culture_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate culture names for gaming table use.
    
    Args:
        culture_data: Culture with names to validate
        
    Returns:
        (gaming_friendly, helpful_tips)
    """
    result = SimpleCultureValidator.validate_for_character_creation(culture_data)
    
    tips = []
    if result.total_names == 0:
        tips.append("Adding character names would help players most")
    elif not result.gaming_friendly:
        tips.extend([
            "Shorter names (4-8 letters) work best at gaming tables",
            "Avoid complex punctuation in names for easier use",
            "Consider nickname variants for long names"
        ])
    else:
        tips.append("Names look great for gaming table use!")
    
    return result.gaming_friendly, tips


# ============================================================================
# COMPATIBILITY FUNCTIONS - For Existing Code
# ============================================================================

# These functions provide compatibility with existing imports while keeping things simple

def validate_character_culture_enhanced(culture_data: Dict[str, Any]) -> SimpleValidationResult:
    """Compatibility function - simple validation with enhanced name."""
    return SimpleCultureValidator.validate_for_character_creation(culture_data)


def get_culture_enhancement_suggestions_enhanced(culture_data: Dict[str, Any]) -> List[str]:
    """Compatibility function - get enhancement suggestions."""
    return SimpleCultureValidator.get_character_enhancement_tips(culture_data)


# Compatibility classes (simple wrappers)
class EnhancedCreativeCultureValidator:
    """Compatibility class - wraps simple validator."""
    
    @staticmethod
    def validate_for_character_generation_enhanced(culture_data: Dict[str, Any], 
                                                  target_preset: Optional[str] = None,
                                                  enhancement_focus: Optional[List] = None) -> SimpleValidationResult:
        """Compatibility method - ignores complex parameters and focuses on character creation."""
        return SimpleCultureValidator.validate_for_character_creation(culture_data)


# Compatibility result class
EnhancedCreativeValidationResult = SimpleValidationResult


# ============================================================================
# EXPORTS - Keep it Simple
# ============================================================================

__all__ = [
    # Core classes
    "SimpleValidationResult",
    "SimpleCultureValidator",
    
    # Main functions
    "validate_culture_for_characters",
    "quick_culture_assessment", 
    "is_culture_ready_for_characters",
    "get_character_creation_tips",
    "validate_culture_names_for_gaming",
    
    # Compatibility functions
    "validate_character_culture_enhanced",
    "get_culture_enhancement_suggestions_enhanced",
    "EnhancedCreativeCultureValidator",
    "EnhancedCreativeValidationResult"
]

# ============================================================================
# MODULE INFO
# ============================================================================

__version__ = "1.0.0"
__description__ = "Simple Culture Validation for D&D Character Creation - Culture Enhances, Never Restricts"