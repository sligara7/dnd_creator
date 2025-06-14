"""
Interactive Conversation State Enums for the D&D Creative Content Framework.

This module defines state enums for managing interactive character creation
conversations, supporting the conversational workflow that guides users through
the complete character creation process from initial concept to final export.

Following Clean Architecture principles, these enums are:
- Infrastructure-independent (no framework-specific dependencies)
- Focused on D&D character creation conversation flow
- Used by domain entities and application use cases
- Support state transition validation and workflow management
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple


# ============ CONVERSATION WORKFLOW STATES ============

class ConversationState(Enum):
    """
    Main conversation states for interactive character creation workflow.
    
    Represents the primary phases of the character creation conversation,
    from initial greeting through final export and completion.
    """
    
    # Initial states
    GREETING = "greeting"                    # Welcome message, explain process
    CONCEPT_GATHERING = "concept_gathering"  # Collect initial character concept
    CONCEPT_CLARIFICATION = "concept_clarification"  # Clarify ambiguous concepts
    
    # Generation states
    GENERATING_OPTIONS = "generating_options"  # Creating character options
    PRESENTING_OPTIONS = "presenting_options"  # Showing generated options
    AWAITING_SELECTION = "awaiting_selection"  # Waiting for user choice
    
    # Refinement states
    GATHERING_FEEDBACK = "gathering_feedback"  # Collecting user feedback
    PROCESSING_CHANGES = "processing_changes"  # Applying user modifications
    VALIDATING_CHANGES = "validating_changes"  # Checking modification validity
    
    # Progression states
    PLANNING_PROGRESSION = "planning_progression"  # Level 1-20 progression planning
    REVIEWING_PROGRESSION = "reviewing_progression"  # User review of progression
    ADJUSTING_PROGRESSION = "adjusting_progression"  # Modifying progression plan
    
    # Finalization states
    FINAL_REVIEW = "final_review"            # Complete character review
    PREPARING_EXPORT = "preparing_export"    # Preparing for export
    SELECTING_FORMATS = "selecting_formats"  # Choosing export formats
    EXPORTING = "exporting"                  # Generating exports
    
    # Terminal states
    COMPLETED = "completed"                  # Successfully completed
    CANCELLED = "cancelled"                  # User cancelled
    ERROR = "error"                         # Error occurred
    TIMEOUT = "timeout"                     # Session timed out


class ConversationSubState(Enum):
    """
    Sub-states within main conversation states for detailed workflow tracking.
    
    Provides granular state tracking within major conversation phases,
    enabling precise workflow management and error recovery.
    """
    
    # Concept gathering sub-states
    COLLECTING_BASIC_CONCEPT = "collecting_basic_concept"
    COLLECTING_BACKSTORY = "collecting_backstory"
    COLLECTING_PREFERENCES = "collecting_preferences"
    ANALYZING_CONCEPT = "analyzing_concept"
    
    # Generation sub-states
    GENERATING_SPECIES = "generating_species"
    GENERATING_CLASS = "generating_class"
    GENERATING_BACKGROUND = "generating_background"
    GENERATING_STATS = "generating_stats"
    GENERATING_EQUIPMENT = "generating_equipment"
    GENERATING_SPELLS = "generating_spells"
    GENERATING_FEATURES = "generating_features"
    
    # Validation sub-states
    VALIDATING_RULES = "validating_rules"
    VALIDATING_BALANCE = "validating_balance"
    VALIDATING_THEME = "validating_theme"
    CHECKING_COMPLETENESS = "checking_completeness"
    
    # Refinement sub-states
    MODIFYING_ABILITIES = "modifying_abilities"
    MODIFYING_SKILLS = "modifying_skills"
    MODIFYING_EQUIPMENT = "modifying_equipment"
    MODIFYING_SPELLS = "modifying_spells"
    MODIFYING_BACKSTORY = "modifying_backstory"
    
    # Progression sub-states
    PLANNING_EARLY_LEVELS = "planning_early_levels"      # Levels 1-5
    PLANNING_MID_LEVELS = "planning_mid_levels"          # Levels 6-10
    PLANNING_HIGH_LEVELS = "planning_high_levels"        # Levels 11-15
    PLANNING_EPIC_LEVELS = "planning_epic_levels"        # Levels 16-20
    REVIEWING_MULTICLASS = "reviewing_multiclass"        # Multiclass options
    PLANNING_FEAT_SELECTION = "planning_feat_selection"  # ASI vs Feat choices
    
    # Export sub-states
    PREPARING_CHARACTER_SHEET = "preparing_character_sheet"
    PREPARING_VTT_FORMATS = "preparing_vtt_formats"
    PREPARING_PDF_SUMMARY = "preparing_pdf_summary"
    VALIDATING_EXPORTS = "validating_exports"


class ConversationPhase(Enum):
    """
    High-level conversation phases for workflow organization.
    
    Groups related conversation states into logical phases for
    progress tracking and user experience optimization.
    """
    
    INITIALIZATION = "initialization"        # Setup and concept gathering
    GENERATION = "generation"               # Character option generation
    ITERATION = "iteration"                 # Feedback and refinement
    PROGRESSION = "progression"             # Level progression planning
    FINALIZATION = "finalization"           # Review and export
    COMPLETION = "completion"               # Final states


class UserInteractionType(Enum):
    """
    Types of user interactions during conversations.
    
    Categorizes user input types to determine appropriate
    processing and response strategies.
    """
    
    # Input types
    TEXT_INPUT = "text_input"               # Free-form text description
    SELECTION = "selection"                 # Choice from options
    CONFIRMATION = "confirmation"           # Yes/no response
    RATING = "rating"                      # Numeric rating/preference
    UPLOAD = "upload"                      # File upload (image, document)
    
    # Action types
    REQUEST_OPTIONS = "request_options"     # Ask for more options
    REQUEST_EXPLANATION = "request_explanation"  # Ask for clarification
    REQUEST_MODIFICATION = "request_modification"  # Request changes
    REQUEST_RESTART = "request_restart"     # Start over
    REQUEST_HELP = "request_help"          # Ask for help
    
    # Navigation types
    NEXT_STEP = "next_step"                # Proceed to next step
    PREVIOUS_STEP = "previous_step"        # Go back to previous step
    JUMP_TO_SECTION = "jump_to_section"    # Jump to specific section
    SAVE_AND_EXIT = "save_and_exit"        # Save progress and exit
    CANCEL = "cancel"                      # Cancel conversation


class ConversationTrigger(Enum):
    """
    Events that trigger conversation state transitions.
    
    Defines the conditions and events that cause the conversation
    to move between different states in the workflow.
    """
    
    # User-initiated triggers
    USER_INPUT_RECEIVED = "user_input_received"
    USER_SELECTION_MADE = "user_selection_made"
    USER_CONFIRMATION = "user_confirmation"
    USER_REJECTION = "user_rejection"
    USER_MODIFICATION_REQUEST = "user_modification_request"
    USER_RESTART_REQUEST = "user_restart_request"
    USER_CANCEL_REQUEST = "user_cancel_request"
    
    # System-initiated triggers
    GENERATION_COMPLETED = "generation_completed"
    VALIDATION_PASSED = "validation_passed"
    VALIDATION_FAILED = "validation_failed"
    EXPORT_READY = "export_ready"
    ERROR_OCCURRED = "error_occurred"
    
    # Time-based triggers
    TIMEOUT_WARNING = "timeout_warning"
    SESSION_TIMEOUT = "session_timeout"
    INACTIVITY_DETECTED = "inactivity_detected"
    
    # Progress triggers
    PHASE_COMPLETED = "phase_completed"
    MILESTONE_REACHED = "milestone_reached"
    REQUIREMENTS_MET = "requirements_met"


class ConversationContext(Enum):
    """
    Context information that affects conversation flow.
    
    Defines contextual factors that influence how the conversation
    proceeds and what options are available to the user.
    """
    
    # User experience level
    BEGINNER_USER = "beginner_user"         # New to D&D
    INTERMEDIATE_USER = "intermediate_user" # Some D&D experience
    EXPERT_USER = "expert_user"            # Experienced D&D player
    DM_USER = "dm_user"                    # Dungeon Master
    
    # Creation preferences
    QUICK_CREATION = "quick_creation"       # Fast, minimal interaction
    DETAILED_CREATION = "detailed_creation" # Comprehensive, interactive
    COLLABORATIVE_CREATION = "collaborative_creation"  # Back-and-forth refinement
    
    # Character complexity
    SIMPLE_CHARACTER = "simple_character"   # Basic, straightforward build
    COMPLEX_CHARACTER = "complex_character" # Multiclass, custom content
    OPTIMIZED_CHARACTER = "optimized_character"  # Min-max focused
    THEMATIC_CHARACTER = "thematic_character"    # Story-focused
    
    # Session constraints
    TIME_LIMITED = "time_limited"           # User has limited time
    FULL_SESSION = "full_session"          # No time pressure
    RETURN_SESSION = "return_session"      # Continuing previous session


class ResponseTone(Enum):
    """
    Tone and style for AI responses during conversations.
    
    Defines the communication style the AI should use based on
    user preferences and conversation context.
    """
    
    FRIENDLY = "friendly"                   # Warm, encouraging
    PROFESSIONAL = "professional"          # Clear, business-like
    CASUAL = "casual"                      # Relaxed, informal
    ENTHUSIASTIC = "enthusiastic"         # Excited, energetic
    EDUCATIONAL = "educational"            # Informative, teaching
    CONCISE = "concise"                    # Brief, to-the-point
    DETAILED = "detailed"                  # Comprehensive explanations


class ConversationPriority(Enum):
    """
    Priority levels for conversation processing and response.
    
    Determines resource allocation and response time targets
    for different types of conversations and users.
    """
    
    LOW = "low"                            # Standard processing
    NORMAL = "normal"                      # Default priority
    HIGH = "high"                          # Faster processing
    URGENT = "urgent"                      # Immediate attention
    PREMIUM = "premium"                    # Premium user priority


# ============ STATE TRANSITION DEFINITIONS ============

# Valid state transitions mapping
VALID_TRANSITIONS: Dict[ConversationState, Set[ConversationState]] = {
    ConversationState.GREETING: {
        ConversationState.CONCEPT_GATHERING,
        ConversationState.CANCELLED,
        ConversationState.ERROR
    },
    ConversationState.CONCEPT_GATHERING: {
        ConversationState.CONCEPT_CLARIFICATION,
        ConversationState.GENERATING_OPTIONS,
        ConversationState.CANCELLED,
        ConversationState.ERROR,
        ConversationState.TIMEOUT
    },
    ConversationState.CONCEPT_CLARIFICATION: {
        ConversationState.CONCEPT_GATHERING,
        ConversationState.GENERATING_OPTIONS,
        ConversationState.CANCELLED,
        ConversationState.ERROR
    },
    ConversationState.GENERATING_OPTIONS: {
        ConversationState.PRESENTING_OPTIONS,
        ConversationState.ERROR,
        ConversationState.CANCELLED
    },
    ConversationState.PRESENTING_OPTIONS: {
        ConversationState.AWAITING_SELECTION,
        ConversationState.GENERATING_OPTIONS,  # Generate more options
        ConversationState.CONCEPT_GATHERING,   # Start over
        ConversationState.CANCELLED,
        ConversationState.ERROR
    },
    ConversationState.AWAITING_SELECTION: {
        ConversationState.GATHERING_FEEDBACK,
        ConversationState.PLANNING_PROGRESSION,
        ConversationState.GENERATING_OPTIONS,  # Request new options
        ConversationState.CANCELLED,
        ConversationState.ERROR,
        ConversationState.TIMEOUT
    },
    ConversationState.GATHERING_FEEDBACK: {
        ConversationState.PROCESSING_CHANGES,
        ConversationState.PLANNING_PROGRESSION,  # No changes needed
        ConversationState.AWAITING_SELECTION,    # Go back
        ConversationState.CANCELLED,
        ConversationState.ERROR
    },
    ConversationState.PROCESSING_CHANGES: {
        ConversationState.VALIDATING_CHANGES,
        ConversationState.ERROR
    },
    ConversationState.VALIDATING_CHANGES: {
        ConversationState.PRESENTING_OPTIONS,   # Show updated options
        ConversationState.GATHERING_FEEDBACK,   # Validation failed
        ConversationState.PLANNING_PROGRESSION, # Changes valid
        ConversationState.ERROR
    },
    ConversationState.PLANNING_PROGRESSION: {
        ConversationState.REVIEWING_PROGRESSION,
        ConversationState.ERROR
    },
    ConversationState.REVIEWING_PROGRESSION: {
        ConversationState.ADJUSTING_PROGRESSION,
        ConversationState.FINAL_REVIEW,         # Progression approved
        ConversationState.PLANNING_PROGRESSION, # Start over
        ConversationState.CANCELLED,
        ConversationState.ERROR
    },
    ConversationState.ADJUSTING_PROGRESSION: {
        ConversationState.PLANNING_PROGRESSION,
        ConversationState.REVIEWING_PROGRESSION,
        ConversationState.ERROR
    },
    ConversationState.FINAL_REVIEW: {
        ConversationState.PREPARING_EXPORT,
        ConversationState.GATHERING_FEEDBACK,   # Make changes
        ConversationState.REVIEWING_PROGRESSION, # Change progression
        ConversationState.CANCELLED,
        ConversationState.ERROR
    },
    ConversationState.PREPARING_EXPORT: {
        ConversationState.SELECTING_FORMATS,
        ConversationState.ERROR
    },
    ConversationState.SELECTING_FORMATS: {
        ConversationState.EXPORTING,
        ConversationState.PREPARING_EXPORT,     # Change formats
        ConversationState.CANCELLED,
        ConversationState.ERROR
    },
    ConversationState.EXPORTING: {
        ConversationState.COMPLETED,
        ConversationState.ERROR
    },
    ConversationState.COMPLETED: set(),        # Terminal state
    ConversationState.CANCELLED: set(),        # Terminal state
    ConversationState.ERROR: {
        ConversationState.GREETING,             # Restart
        ConversationState.CANCELLED            # Give up
    },
    ConversationState.TIMEOUT: {
        ConversationState.GREETING,             # Resume/restart
        ConversationState.CANCELLED            # End session
    }
}

# Phase groupings for states
STATE_PHASES: Dict[ConversationState, ConversationPhase] = {
    ConversationState.GREETING: ConversationPhase.INITIALIZATION,
    ConversationState.CONCEPT_GATHERING: ConversationPhase.INITIALIZATION,
    ConversationState.CONCEPT_CLARIFICATION: ConversationPhase.INITIALIZATION,
    
    ConversationState.GENERATING_OPTIONS: ConversationPhase.GENERATION,
    ConversationState.PRESENTING_OPTIONS: ConversationPhase.GENERATION,
    ConversationState.AWAITING_SELECTION: ConversationPhase.GENERATION,
    
    ConversationState.GATHERING_FEEDBACK: ConversationPhase.ITERATION,
    ConversationState.PROCESSING_CHANGES: ConversationPhase.ITERATION,
    ConversationState.VALIDATING_CHANGES: ConversationPhase.ITERATION,
    
    ConversationState.PLANNING_PROGRESSION: ConversationPhase.PROGRESSION,
    ConversationState.REVIEWING_PROGRESSION: ConversationPhase.PROGRESSION,
    ConversationState.ADJUSTING_PROGRESSION: ConversationPhase.PROGRESSION,
    
    ConversationState.FINAL_REVIEW: ConversationPhase.FINALIZATION,
    ConversationState.PREPARING_EXPORT: ConversationPhase.FINALIZATION,
    ConversationState.SELECTING_FORMATS: ConversationPhase.FINALIZATION,
    ConversationState.EXPORTING: ConversationPhase.FINALIZATION,
    
    ConversationState.COMPLETED: ConversationPhase.COMPLETION,
    ConversationState.CANCELLED: ConversationPhase.COMPLETION,
    ConversationState.ERROR: ConversationPhase.COMPLETION,
    ConversationState.TIMEOUT: ConversationPhase.COMPLETION,
}

# Expected user interactions for each state
STATE_INTERACTIONS: Dict[ConversationState, Set[UserInteractionType]] = {
    ConversationState.GREETING: {
        UserInteractionType.TEXT_INPUT,
        UserInteractionType.CONFIRMATION,
        UserInteractionType.CANCEL
    },
    ConversationState.CONCEPT_GATHERING: {
        UserInteractionType.TEXT_INPUT,
        UserInteractionType.UPLOAD,
        UserInteractionType.REQUEST_HELP,
        UserInteractionType.CANCEL
    },
    ConversationState.CONCEPT_CLARIFICATION: {
        UserInteractionType.TEXT_INPUT,
        UserInteractionType.SELECTION,
        UserInteractionType.CONFIRMATION,
        UserInteractionType.PREVIOUS_STEP
    },
    ConversationState.PRESENTING_OPTIONS: {
        UserInteractionType.SELECTION,
        UserInteractionType.REQUEST_OPTIONS,
        UserInteractionType.REQUEST_EXPLANATION,
        UserInteractionType.REQUEST_RESTART
    },
    ConversationState.AWAITING_SELECTION: {
        UserInteractionType.SELECTION,
        UserInteractionType.CONFIRMATION,
        UserInteractionType.REQUEST_MODIFICATION,
        UserInteractionType.PREVIOUS_STEP
    },
    ConversationState.GATHERING_FEEDBACK: {
        UserInteractionType.TEXT_INPUT,
        UserInteractionType.RATING,
        UserInteractionType.REQUEST_MODIFICATION,
        UserInteractionType.NEXT_STEP
    },
    ConversationState.REVIEWING_PROGRESSION: {
        UserInteractionType.CONFIRMATION,
        UserInteractionType.REQUEST_MODIFICATION,
        UserInteractionType.REQUEST_EXPLANATION,
        UserInteractionType.PREVIOUS_STEP
    },
    ConversationState.FINAL_REVIEW: {
        UserInteractionType.CONFIRMATION,
        UserInteractionType.REQUEST_MODIFICATION,
        UserInteractionType.JUMP_TO_SECTION,
        UserInteractionType.NEXT_STEP
    },
    ConversationState.SELECTING_FORMATS: {
        UserInteractionType.SELECTION,
        UserInteractionType.CONFIRMATION,
        UserInteractionType.REQUEST_HELP
    }
}

# Timeout durations for each state (in minutes)
STATE_TIMEOUTS: Dict[ConversationState, int] = {
    ConversationState.GREETING: 10,
    ConversationState.CONCEPT_GATHERING: 15,
    ConversationState.CONCEPT_CLARIFICATION: 10,
    ConversationState.PRESENTING_OPTIONS: 20,
    ConversationState.AWAITING_SELECTION: 15,
    ConversationState.GATHERING_FEEDBACK: 20,
    ConversationState.REVIEWING_PROGRESSION: 25,
    ConversationState.FINAL_REVIEW: 30,
    ConversationState.SELECTING_FORMATS: 10,
    # No timeouts for processing states
    ConversationState.GENERATING_OPTIONS: 0,
    ConversationState.PROCESSING_CHANGES: 0,
    ConversationState.VALIDATING_CHANGES: 0,
    ConversationState.PLANNING_PROGRESSION: 0,
    ConversationState.ADJUSTING_PROGRESSION: 0,
    ConversationState.PREPARING_EXPORT: 0,
    ConversationState.EXPORTING: 0,
}


# ============ UTILITY FUNCTIONS ============

def is_valid_transition(from_state: ConversationState, to_state: ConversationState) -> bool:
    """
    Check if a state transition is valid.
    
    Args:
        from_state: Current conversation state
        to_state: Target conversation state
        
    Returns:
        True if transition is valid, False otherwise
    """
    return to_state in VALID_TRANSITIONS.get(from_state, set())


def get_valid_transitions(state: ConversationState) -> Set[ConversationState]:
    """
    Get all valid transitions from a given state.
    
    Args:
        state: Current conversation state
        
    Returns:
        Set of valid target states
    """
    return VALID_TRANSITIONS.get(state, set())


def get_conversation_phase(state: ConversationState) -> ConversationPhase:
    """
    Get the conversation phase for a given state.
    
    Args:
        state: Conversation state
        
    Returns:
        The conversation phase containing this state
    """
    return STATE_PHASES.get(state, ConversationPhase.COMPLETION)


def get_expected_interactions(state: ConversationState) -> Set[UserInteractionType]:
    """
    Get expected user interaction types for a conversation state.
    
    Args:
        state: Current conversation state
        
    Returns:
        Set of expected interaction types
    """
    return STATE_INTERACTIONS.get(state, set())


def get_state_timeout(state: ConversationState) -> Optional[int]:
    """
    Get timeout duration for a conversation state.
    
    Args:
        state: Conversation state
        
    Returns:
        Timeout in minutes, or None if no timeout
    """
    timeout = STATE_TIMEOUTS.get(state, 0)
    return timeout if timeout > 0 else None


def is_terminal_state(state: ConversationState) -> bool:
    """
    Check if a conversation state is terminal (no valid transitions).
    
    Args:
        state: Conversation state to check
        
    Returns:
        True if state is terminal
    """
    return len(VALID_TRANSITIONS.get(state, set())) == 0


def is_processing_state(state: ConversationState) -> bool:
    """
    Check if a conversation state is a processing state (system-driven).
    
    Args:
        state: Conversation state to check
        
    Returns:
        True if state involves system processing
    """
    processing_states = {
        ConversationState.GENERATING_OPTIONS,
        ConversationState.PROCESSING_CHANGES,
        ConversationState.VALIDATING_CHANGES,
        ConversationState.PLANNING_PROGRESSION,
        ConversationState.ADJUSTING_PROGRESSION,
        ConversationState.PREPARING_EXPORT,
        ConversationState.EXPORTING
    }
    return state in processing_states


def is_user_input_state(state: ConversationState) -> bool:
    """
    Check if a conversation state expects user input.
    
    Args:
        state: Conversation state to check
        
    Returns:
        True if state expects user input
    """
    return not is_processing_state(state) and not is_terminal_state(state)


def get_states_in_phase(phase: ConversationPhase) -> List[ConversationState]:
    """
    Get all conversation states in a given phase.
    
    Args:
        phase: Conversation phase
        
    Returns:
        List of states in the phase
    """
    return [state for state, state_phase in STATE_PHASES.items() if state_phase == phase]


def calculate_progress_percentage(current_state: ConversationState) -> float:
    """
    Calculate conversation progress as a percentage.
    
    Args:
        current_state: Current conversation state
        
    Returns:
        Progress percentage (0.0 to 100.0)
    """
    phase = get_conversation_phase(current_state)
    
    # Base progress by phase
    phase_progress = {
        ConversationPhase.INITIALIZATION: 0.0,
        ConversationPhase.GENERATION: 20.0,
        ConversationPhase.ITERATION: 40.0,
        ConversationPhase.PROGRESSION: 60.0,
        ConversationPhase.FINALIZATION: 80.0,
        ConversationPhase.COMPLETION: 100.0
    }
    
    base_progress = phase_progress.get(phase, 0.0)
    
    # Add fine-grained progress within phase
    phase_states = get_states_in_phase(phase)
    if len(phase_states) > 1 and current_state in phase_states:
        state_index = phase_states.index(current_state)
        phase_step = 20.0 / len(phase_states)  # Each phase is 20% of total
        base_progress += (state_index * phase_step)
    
    return min(100.0, base_progress)


def get_next_recommended_state(
    current_state: ConversationState,
    trigger: ConversationTrigger,
    context: Optional[ConversationContext] = None
) -> Optional[ConversationState]:
    """
    Get recommended next state based on current state, trigger, and context.
    
    Args:
        current_state: Current conversation state
        trigger: Event that occurred
        context: Optional conversation context
        
    Returns:
        Recommended next state, or None if no clear recommendation
    """
    valid_transitions = get_valid_transitions(current_state)
    
    if not valid_transitions:
        return None
    
    # Handle common triggers
    if trigger == ConversationTrigger.USER_CANCEL_REQUEST:
        return ConversationState.CANCELLED
    
    if trigger == ConversationTrigger.ERROR_OCCURRED:
        return ConversationState.ERROR
    
    if trigger == ConversationTrigger.SESSION_TIMEOUT:
        return ConversationState.TIMEOUT
    
    # State-specific recommendations
    recommendations = {
        (ConversationState.GREETING, ConversationTrigger.USER_INPUT_RECEIVED): 
            ConversationState.CONCEPT_GATHERING,
        
        (ConversationState.CONCEPT_GATHERING, ConversationTrigger.USER_INPUT_RECEIVED): 
            ConversationState.GENERATING_OPTIONS,
        
        (ConversationState.GENERATING_OPTIONS, ConversationTrigger.GENERATION_COMPLETED): 
            ConversationState.PRESENTING_OPTIONS,
        
        (ConversationState.PRESENTING_OPTIONS, ConversationTrigger.USER_SELECTION_MADE): 
            ConversationState.AWAITING_SELECTION,
        
        (ConversationState.AWAITING_SELECTION, ConversationTrigger.USER_CONFIRMATION): 
            ConversationState.PLANNING_PROGRESSION,
        
        (ConversationState.AWAITING_SELECTION, ConversationTrigger.USER_MODIFICATION_REQUEST): 
            ConversationState.GATHERING_FEEDBACK,
        
        (ConversationState.GATHERING_FEEDBACK, ConversationTrigger.USER_INPUT_RECEIVED): 
            ConversationState.PROCESSING_CHANGES,
        
        (ConversationState.PROCESSING_CHANGES, ConversationTrigger.GENERATION_COMPLETED): 
            ConversationState.VALIDATING_CHANGES,
        
        (ConversationState.VALIDATING_CHANGES, ConversationTrigger.VALIDATION_PASSED): 
            ConversationState.PLANNING_PROGRESSION,
        
        (ConversationState.PLANNING_PROGRESSION, ConversationTrigger.GENERATION_COMPLETED): 
            ConversationState.REVIEWING_PROGRESSION,
        
        (ConversationState.REVIEWING_PROGRESSION, ConversationTrigger.USER_CONFIRMATION): 
            ConversationState.FINAL_REVIEW,
        
        (ConversationState.FINAL_REVIEW, ConversationTrigger.USER_CONFIRMATION): 
            ConversationState.PREPARING_EXPORT,
        
        (ConversationState.PREPARING_EXPORT, ConversationTrigger.EXPORT_READY): 
            ConversationState.SELECTING_FORMATS,
        
        (ConversationState.SELECTING_FORMATS, ConversationTrigger.USER_SELECTION_MADE): 
            ConversationState.EXPORTING,
        
        (ConversationState.EXPORTING, ConversationTrigger.GENERATION_COMPLETED): 
            ConversationState.COMPLETED,
    }
    
    recommended = recommendations.get((current_state, trigger))
    
    # Verify recommendation is valid
    if recommended and recommended in valid_transitions:
        return recommended
    
    return None


# ============ CONVERSATION STATE METADATA ============

# State descriptions for UI and logging
STATE_DESCRIPTIONS: Dict[ConversationState, str] = {
    ConversationState.GREETING: "Welcoming user and explaining the character creation process",
    ConversationState.CONCEPT_GATHERING: "Collecting initial character concept and preferences",
    ConversationState.CONCEPT_CLARIFICATION: "Clarifying ambiguous or incomplete concept details",
    ConversationState.GENERATING_OPTIONS: "Generating character options based on concept",
    ConversationState.PRESENTING_OPTIONS: "Presenting generated character options to user",
    ConversationState.AWAITING_SELECTION: "Waiting for user to select preferred character option",
    ConversationState.GATHERING_FEEDBACK: "Collecting user feedback for character refinement",
    ConversationState.PROCESSING_CHANGES: "Processing user-requested character modifications",
    ConversationState.VALIDATING_CHANGES: "Validating modified character for rule compliance",
    ConversationState.PLANNING_PROGRESSION: "Planning character progression from levels 1-20",
    ConversationState.REVIEWING_PROGRESSION: "User reviewing planned character progression",
    ConversationState.ADJUSTING_PROGRESSION: "Modifying character progression based on feedback",
    ConversationState.FINAL_REVIEW: "Final review of complete character before export",
    ConversationState.PREPARING_EXPORT: "Preparing character data for export formats",
    ConversationState.SELECTING_FORMATS: "User selecting desired export formats",
    ConversationState.EXPORTING: "Generating character exports in selected formats",
    ConversationState.COMPLETED: "Character creation successfully completed",
    ConversationState.CANCELLED: "Character creation cancelled by user",
    ConversationState.ERROR: "Error occurred during character creation",
    ConversationState.TIMEOUT: "Session timed out due to user inactivity"
}

# User-friendly state names
STATE_DISPLAY_NAMES: Dict[ConversationState, str] = {
    ConversationState.GREETING: "Getting Started",
    ConversationState.CONCEPT_GATHERING: "Describing Your Character",
    ConversationState.CONCEPT_CLARIFICATION: "Clarifying Details",
    ConversationState.GENERATING_OPTIONS: "Creating Options",
    ConversationState.PRESENTING_OPTIONS: "Character Options",
    ConversationState.AWAITING_SELECTION: "Choose Your Character",
    ConversationState.GATHERING_FEEDBACK: "Refining Your Character",
    ConversationState.PROCESSING_CHANGES: "Making Changes",
    ConversationState.VALIDATING_CHANGES: "Checking Changes",
    ConversationState.PLANNING_PROGRESSION: "Planning Levels 1-20",
    ConversationState.REVIEWING_PROGRESSION: "Review Progression",
    ConversationState.ADJUSTING_PROGRESSION: "Adjusting Progression",
    ConversationState.FINAL_REVIEW: "Final Review",
    ConversationState.PREPARING_EXPORT: "Preparing Export",
    ConversationState.SELECTING_FORMATS: "Export Options",
    ConversationState.EXPORTING: "Creating Files",
    ConversationState.COMPLETED: "Complete!",
    ConversationState.CANCELLED: "Cancelled",
    ConversationState.ERROR: "Error",
    ConversationState.TIMEOUT: "Session Expired"
}


# ============ MODULE METADATA ============

__version__ = '2.0.0'
__description__ = 'Interactive conversation state enums for D&D Creative Content Framework'
__author__ = 'D&D Character Creator Backend6'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/enums",
    "dependencies": [],
    "dependents": ["domain/entities", "application/use_cases", "infrastructure"],
    "infrastructure_independent": True,
    "focuses_on": "D&D character creation conversation workflow states"
}

# State statistics
STATE_STATISTICS = {
    "total_states": len(ConversationState),
    "processing_states": len([s for s in ConversationState if is_processing_state(s)]),
    "user_input_states": len([s for s in ConversationState if is_user_input_state(s)]),
    "terminal_states": len([s for s in ConversationState if is_terminal_state(s)]),
    "phases": len(ConversationPhase),
    "interaction_types": len(UserInteractionType),
    "triggers": len(ConversationTrigger),
    "contexts": len(ConversationContext)
}