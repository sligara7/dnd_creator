"""
Minimal Culture Exceptions for D&D Character Creation.

SIMPLIFIED VERSION: Only essential exceptions that support character creation.
Culture features are supportive - no complex validation or restriction systems.

Philosophy:
- Character creation comes first
- Culture enhances but never restricts
- Simple exceptions for basic error handling
- Always provide fallbacks for creativity
"""

from typing import Optional, Dict, List, Any

# ============================================================================
# ESSENTIAL CULTURE EXCEPTIONS - Character Creation Focus
# ============================================================================

class CultureError(Exception):
    """Base culture exception - always provides fallback for character creation."""
    
    def __init__(self, message: str, fallback_suggestion: Optional[str] = None, 
                 culture_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.fallback_suggestion = fallback_suggestion or "Culture features are optional - continue with character creation"
        self.culture_data = culture_data or {}
    
    def get_character_creation_fallback(self) -> str:
        """Get helpful fallback message for character creation."""
        return f"{self.fallback_suggestion} (Original issue: {str(self)})"


class CultureGenerationError(CultureError):
    """Culture generation failed - provides creative alternatives."""
    
    def __init__(self, message: str, attempted_culture: Optional[str] = None):
        fallback = f"Try a different cultural inspiration or use generic fantasy names"
        if attempted_culture:
            fallback = f"'{attempted_culture}' generation failed - try generic fantasy or different inspiration"
        
        super().__init__(message, fallback)
        self.attempted_culture = attempted_culture


class CultureParsingError(CultureError):
    """Culture parsing failed - provides simple alternatives."""
    
    def __init__(self, message: str, raw_content: Optional[str] = None):
        fallback = "Use manual name entry or generic fantasy names for character creation"
        super().__init__(message, fallback)
        self.raw_content = raw_content


class CultureNotFoundError(CultureError):
    """Culture not found - provides alternatives."""
    
    def __init__(self, culture_name: str, available_cultures: Optional[List[str]] = None):
        message = f"Culture '{culture_name}' not found"
        if available_cultures:
            message += f". Available cultures: {', '.join(available_cultures[:5])}"
        
        fallback = f"Try a different culture name or use generic fantasy for character creation"
        super().__init__(message, fallback)
        self.culture_name = culture_name
        self.available_cultures = available_cultures or []


# ============================================================================
# HELPER FUNCTIONS - Always Supportive
# ============================================================================

def handle_culture_error_gracefully(error: Exception, context: str = "character creation") -> Dict[str, Any]:
    """
    Handle culture errors gracefully for character creation.
    
    Args:
        error: The error that occurred
        context: Context where error occurred
        
    Returns:
        Dictionary with error info and fallback suggestions
    """
    if isinstance(error, CultureError):
        return {
            "error_type": type(error).__name__,
            "message": str(error),
            "fallback_suggestion": error.get_character_creation_fallback(),
            "can_continue": True,
            "context": context
        }
    else:
        return {
            "error_type": "UnexpectedError",
            "message": str(error),
            "fallback_suggestion": f"Unexpected error in {context} - continue with manual character creation",
            "can_continue": True,
            "context": context
        }


def get_culture_error_fallback(error: Exception) -> str:
    """Get a helpful fallback message for any culture-related error."""
    if isinstance(error, CultureError):
        return error.get_character_creation_fallback()
    else:
        return "Culture features are optional - continue with character creation using manual input"


def should_continue_character_creation(error: Exception) -> bool:
    """Check if character creation should continue despite culture error."""
    # Always continue - culture features are supportive, not required
    return True


# ============================================================================
# EXPORTS - Keep it Simple
# ============================================================================

__all__ = [
    # Core exceptions
    "CultureError",
    "CultureGenerationError", 
    "CultureParsingError",
    "CultureNotFoundError",
    
    # Helper functions
    "handle_culture_error_gracefully",
    "get_culture_error_fallback",
    "should_continue_character_creation"
]

# ============================================================================
# MODULE INFO
# ============================================================================

__version__ = "1.0.0"
__description__ = "Minimal Culture Exceptions for D&D Character Creation - Culture Enhances, Never Restricts"