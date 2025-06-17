"""
Essential D&D Workflow Exception Types

Streamlined workflow-related exception handling following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from typing import Optional, Dict, Any, List
from .base import DnDCharacterCreatorError

# ============ CHARACTER CREATION WORKFLOW EXCEPTIONS ============

class WorkflowStateError(DnDCharacterCreatorError):
    """Invalid workflow state transitions or operations."""
    
    def __init__(self, current_state: str, attempted_operation: str, state_error: str, **kwargs):
        message = f"Workflow state error: cannot {attempted_operation} from {current_state} - {state_error}"
        details = {
            "current_state": current_state,
            "attempted_operation": attempted_operation,
            "state_error": state_error,
            **kwargs
        }
        super().__init__(message, details)
        self.current_state = current_state
        self.attempted_operation = attempted_operation

class InvalidTransitionError(DnDCharacterCreatorError):
    """Invalid transitions between workflow states."""
    
    def __init__(self, from_state: str, to_state: str, transition_reason: str, **kwargs):
        message = f"Invalid transition: {from_state} -> {to_state} - {transition_reason}"
        details = {
            "from_state": from_state,
            "to_state": to_state,
            "transition_reason": transition_reason,
            **kwargs
        }
        super().__init__(message, details)
        self.from_state = from_state
        self.to_state = to_state

class WorkflowInterruptionError(DnDCharacterCreatorError):
    """Workflow interruption due to errors or user actions."""
    
    def __init__(self, interrupted_stage: str, interruption_cause: str, **kwargs):
        message = f"Workflow interrupted at {interrupted_stage}: {interruption_cause}"
        details = {
            "interrupted_stage": interrupted_stage,
            "interruption_cause": interruption_cause,
            **kwargs
        }
        super().__init__(message, details)
        self.interrupted_stage = interrupted_stage
        self.interruption_cause = interruption_cause

# ============ STEP VALIDATION EXCEPTIONS ============

class StepValidationError(DnDCharacterCreatorError):
    """Step-specific validation failures in workflow."""
    
    def __init__(self, step_name: str, validation_failures: List[str], **kwargs):
        failures_str = ", ".join(validation_failures)
        message = f"Step validation failed for {step_name}: {failures_str}"
        details = {
            "step_name": step_name,
            "validation_failures": validation_failures,
            **kwargs
        }
        super().__init__(message, details)
        self.step_name = step_name
        self.validation_failures = validation_failures

class IncompleteStepError(DnDCharacterCreatorError):
    """Required workflow step not completed."""
    
    def __init__(self, step_name: str, missing_requirements: List[str], **kwargs):
        requirements_str = ", ".join(missing_requirements)
        message = f"Step incomplete: {step_name} missing {requirements_str}"
        details = {
            "step_name": step_name,
            "missing_requirements": missing_requirements,
            **kwargs
        }
        super().__init__(message, details)
        self.step_name = step_name
        self.missing_requirements = missing_requirements

class PrerequisiteError(DnDCharacterCreatorError):
    """Step prerequisites not met."""
    
    def __init__(self, step_name: str, unmet_prerequisites: List[str], **kwargs):
        prereqs_str = ", ".join(unmet_prerequisites)
        message = f"Prerequisites not met for {step_name}: {prereqs_str}"
        details = {
            "step_name": step_name,
            "unmet_prerequisites": unmet_prerequisites,
            **kwargs
        }
        super().__init__(message, details)
        self.step_name = step_name
        self.unmet_prerequisites = unmet_prerequisites

# ============ USER INPUT EXCEPTIONS ============

class UserInputError(DnDCharacterCreatorError):
    """Invalid or missing user input in workflow."""
    
    def __init__(self, input_field: str, input_error: str, expected_format: str = None, **kwargs):
        message = f"User input error for {input_field}: {input_error}"
        if expected_format:
            message += f" (expected: {expected_format})"
        details = {
            "input_field": input_field,
            "input_error": input_error,
            "expected_format": expected_format,
            **kwargs
        }
        super().__init__(message, details)
        self.input_field = input_field
        self.input_error = input_error
        self.expected_format = expected_format

class TimeoutError(DnDCharacterCreatorError):
    """Workflow timeout due to user inactivity or system limits."""
    
    def __init__(self, timeout_stage: str, timeout_duration: int, **kwargs):
        message = f"Workflow timeout at {timeout_stage} after {timeout_duration} seconds"
        details = {
            "timeout_stage": timeout_stage,
            "timeout_duration": timeout_duration,
            **kwargs
        }
        super().__init__(message, details)
        self.timeout_stage = timeout_stage
        self.timeout_duration = timeout_duration

# ============ COMPLETION EXCEPTIONS ============

class WorkflowCompletionError(DnDCharacterCreatorError):
    """Workflow completion failures."""
    
    def __init__(self, completion_stage: str, completion_error: str, **kwargs):
        message = f"Workflow completion failed at {completion_stage}: {completion_error}"
        details = {
            "completion_stage": completion_stage,
            "completion_error": completion_error,
            **kwargs
        }
        super().__init__(message, details)
        self.completion_stage = completion_stage
        self.completion_error = completion_error

class FinalValidationError(DnDCharacterCreatorError):
    """Final character validation failures before completion."""
    
    def __init__(self, validation_errors: List[str], **kwargs):
        errors_str = ", ".join(validation_errors)
        message = f"Final validation failed: {errors_str}"
        details = {
            "validation_errors": validation_errors,
            **kwargs
        }
        super().__init__(message, details)
        self.validation_errors = validation_errors

# ============ UTILITY FUNCTIONS ============

def create_workflow_state_error(state: str, operation: str, error: str) -> WorkflowStateError:
    """Factory function for workflow state errors."""
    return WorkflowStateError(state, operation, error)

def create_invalid_transition_error(from_state: str, to_state: str, reason: str) -> InvalidTransitionError:
    """Factory function for invalid transition errors."""
    return InvalidTransitionError(from_state, to_state, reason)

def create_step_validation_error(step: str, failures: List[str]) -> StepValidationError:
    """Factory function for step validation errors."""
    return StepValidationError(step, failures)

def is_recoverable_workflow_error(error: DnDCharacterCreatorError) -> bool:
    """Check if workflow error is recoverable with user action."""
    recoverable_types = [
        StepValidationError,
        IncompleteStepError,
        UserInputError,
        PrerequisiteError
    ]
    return any(isinstance(error, error_type) for error_type in recoverable_types)

def requires_workflow_restart(error: DnDCharacterCreatorError) -> bool:
    """Check if error requires restarting the workflow."""
    restart_types = [
        WorkflowCompletionError,
        FinalValidationError,
        TimeoutError
    ]
    return any(isinstance(error, error_type) for error_type in restart_types)

def can_continue_workflow(error: DnDCharacterCreatorError) -> bool:
    """Check if workflow can continue after error resolution."""
    continuable_types = [
        StepValidationError,
        UserInputError,
        IncompleteStepError
    ]
    return any(isinstance(error, error_type) for error_type in continuable_types)

def get_workflow_error_severity(error: DnDCharacterCreatorError) -> str:
    """Get workflow error severity level."""
    severity_map = {
        WorkflowStateError: "error",
        InvalidTransitionError: "error",
        WorkflowInterruptionError: "warning",
        StepValidationError: "warning",
        IncompleteStepError: "warning",
        PrerequisiteError: "error",
        UserInputError: "info",
        TimeoutError: "warning",
        WorkflowCompletionError: "error",
        FinalValidationError: "error"
    }
    return severity_map.get(type(error), "warning")

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Character creation workflow exceptions
    'WorkflowStateError',
    'InvalidTransitionError',
    'WorkflowInterruptionError',
    
    # Step validation exceptions
    'StepValidationError',
    'IncompleteStepError',
    'PrerequisiteError',
    
    # User input exceptions
    'UserInputError',
    'TimeoutError',
    
    # Completion exceptions
    'WorkflowCompletionError',
    'FinalValidationError',
    
    # Utility functions
    'create_workflow_state_error',
    'create_invalid_transition_error',
    'create_step_validation_error',
    'is_recoverable_workflow_error',
    'requires_workflow_restart',
    'can_continue_workflow',
    'get_workflow_error_severity',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D workflow exception handling'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/exceptions",
    "focus": "workflow_error_handling_only",
    "line_target": 150,
    "dependencies": ["base"],
    "philosophy": "crude_functional_inspired_simple_workflow_exceptions"
}