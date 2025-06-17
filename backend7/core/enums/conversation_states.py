"""
Essential Conversation State Enums

Streamlined conversation state management following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from enum import Enum, auto

# ============ CHARACTER CREATION CONVERSATION STATES ============

class CreationState(Enum):
    """Character creation conversation flow states."""
    START = auto()
    RACE_SELECTION = auto()
    CLASS_SELECTION = auto()
    ABILITY_SCORES = auto()
    BACKGROUND = auto()
    EQUIPMENT = auto()
    FINALIZATION = auto()
    COMPLETE = auto()

class InputState(Enum):
    """User input expectation states."""
    WAITING_CHOICE = auto()
    WAITING_TEXT = auto()
    WAITING_NUMBER = auto()
    WAITING_CONFIRMATION = auto()
    PROCESSING = auto()

class ValidationState(Enum):
    """Input validation states."""
    VALID = auto()
    INVALID = auto()
    INCOMPLETE = auto()
    REQUIRES_CLARIFICATION = auto()

# ============ CONVERSATION FLOW CONTROL ============

class FlowDirection(Enum):
    """Conversation flow direction."""
    FORWARD = auto()
    BACKWARD = auto()
    RESTART = auto()
    JUMP = auto()

class UserIntent(Enum):
    """User intention classification."""
    CREATE_CHARACTER = auto()
    MODIFY_CHARACTER = auto()
    GET_HELP = auto()
    GO_BACK = auto()
    START_OVER = auto()
    QUIT = auto()

class ResponseType(Enum):
    """System response classifications."""
    QUESTION = auto()
    CONFIRMATION = auto()
    ERROR = auto()
    HELP = auto()
    SUMMARY = auto()
    COMPLETION = auto()

# ============ CHARACTER MODIFICATION STATES ============

class ModificationState(Enum):
    """Character modification conversation states."""
    SELECT_ELEMENT = auto()
    MODIFY_RACE = auto()
    MODIFY_CLASS = auto()
    MODIFY_ABILITIES = auto()
    MODIFY_BACKGROUND = auto()
    MODIFY_EQUIPMENT = auto()
    CONFIRM_CHANGES = auto()

class EditMode(Enum):
    """Editing mode classifications."""
    REPLACE = auto()
    ADD = auto()
    REMOVE = auto()
    ADJUST = auto()

# ============ ERROR AND HELP STATES ============

class ErrorLevel(Enum):
    """Error severity levels."""
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

class HelpContext(Enum):
    """Help system contexts."""
    GENERAL = auto()
    RACE_HELP = auto()
    CLASS_HELP = auto()
    ABILITIES_HELP = auto()
    RULES_HELP = auto()

# ============ STATE TRANSITIONS ============

CREATION_FLOW = {
    CreationState.START: CreationState.RACE_SELECTION,
    CreationState.RACE_SELECTION: CreationState.CLASS_SELECTION,
    CreationState.CLASS_SELECTION: CreationState.ABILITY_SCORES,
    CreationState.ABILITY_SCORES: CreationState.BACKGROUND,
    CreationState.BACKGROUND: CreationState.EQUIPMENT,
    CreationState.EQUIPMENT: CreationState.FINALIZATION,
    CreationState.FINALIZATION: CreationState.COMPLETE,
}

VALID_BACK_STATES = {
    CreationState.CLASS_SELECTION: CreationState.RACE_SELECTION,
    CreationState.ABILITY_SCORES: CreationState.CLASS_SELECTION,
    CreationState.BACKGROUND: CreationState.ABILITY_SCORES,
    CreationState.EQUIPMENT: CreationState.BACKGROUND,
    CreationState.FINALIZATION: CreationState.EQUIPMENT,
}

# ============ UTILITY FUNCTIONS ============

def get_next_state(current_state: CreationState) -> CreationState:
    """Get the next state in character creation flow."""
    return CREATION_FLOW.get(current_state, CreationState.COMPLETE)

def get_previous_state(current_state: CreationState) -> CreationState:
    """Get the previous state in character creation flow."""
    return VALID_BACK_STATES.get(current_state, CreationState.START)

def can_go_back(current_state: CreationState) -> bool:
    """Check if user can go back from current state."""
    return current_state in VALID_BACK_STATES

def is_creation_complete(state: CreationState) -> bool:
    """Check if character creation is complete."""
    return state == CreationState.COMPLETE

def requires_user_input(input_state: InputState) -> bool:
    """Check if state requires user input."""
    return input_state in [
        InputState.WAITING_CHOICE,
        InputState.WAITING_TEXT,
        InputState.WAITING_NUMBER,
        InputState.WAITING_CONFIRMATION
    ]

def is_error_state(validation_state: ValidationState) -> bool:
    """Check if validation state indicates an error."""
    return validation_state in [
        ValidationState.INVALID,
        ValidationState.INCOMPLETE,
        ValidationState.REQUIRES_CLARIFICATION
    ]

def get_help_for_state(creation_state: CreationState) -> HelpContext:
    """Get appropriate help context for creation state."""
    help_mapping = {
        CreationState.RACE_SELECTION: HelpContext.RACE_HELP,
        CreationState.CLASS_SELECTION: HelpContext.CLASS_HELP,
        CreationState.ABILITY_SCORES: HelpContext.ABILITIES_HELP,
    }
    return help_mapping.get(creation_state, HelpContext.GENERAL)

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core states
    'CreationState',
    'InputState',
    'ValidationState',
    
    # Flow control
    'FlowDirection',
    'UserIntent',
    'ResponseType',
    
    # Modification
    'ModificationState',
    'EditMode',
    
    # Error handling
    'ErrorLevel',
    'HelpContext',
    
    # Flow mappings
    'CREATION_FLOW',
    'VALID_BACK_STATES',
    
    # Utility functions
    'get_next_state',
    'get_previous_state',
    'can_go_back',
    'is_creation_complete',
    'requires_user_input',
    'is_error_state',
    'get_help_for_state',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential conversation state enumerations'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/enums",
    "focus": "conversation_flow_only",
    "line_target": 150,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_state_management"
}