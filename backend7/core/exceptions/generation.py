"""
Essential D&D Generation Exception Types

Streamlined generation-related exception handling following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from typing import Optional, Dict, Any, List
from .base import DnDCharacterCreatorError

# ============ CONTENT GENERATION EXCEPTIONS ============

class GenerationFailureError(DnDCharacterCreatorError):
    """Content generation process failures."""
    
    def __init__(self, content_type: str, generation_stage: str, failure_reason: str, **kwargs):
        message = f"Generation failed for {content_type} at {generation_stage}: {failure_reason}"
        details = {
            "content_type": content_type,
            "generation_stage": generation_stage,
            "failure_reason": failure_reason,
            **kwargs
        }
        super().__init__(message, details)
        self.content_type = content_type
        self.generation_stage = generation_stage
        self.failure_reason = failure_reason

class CreativityConstraintError(DnDCharacterCreatorError):
    """Creativity level constraints preventing generation."""
    
    def __init__(self, creativity_level: str, requested_content: str, constraint: str, **kwargs):
        message = f"Creativity constraint: {creativity_level} level cannot generate {requested_content} - {constraint}"
        details = {
            "creativity_level": creativity_level,
            "requested_content": requested_content,
            "constraint": constraint,
            **kwargs
        }
        super().__init__(message, details)
        self.creativity_level = creativity_level
        self.requested_content = requested_content
        self.constraint = constraint

class InsufficientDataError(DnDCharacterCreatorError):
    """Insufficient source data for generation."""
    
    def __init__(self, data_type: str, required_amount: int, available_amount: int, **kwargs):
        message = f"Insufficient {data_type} data: need {required_amount}, have {available_amount}"
        details = {
            "data_type": data_type,
            "required_amount": required_amount,
            "available_amount": available_amount,
            **kwargs
        }
        super().__init__(message, details)
        self.data_type = data_type
        self.required_amount = required_amount
        self.available_amount = available_amount

# ============ TEMPLATE GENERATION EXCEPTIONS ============

class TemplateProcessingError(DnDCharacterCreatorError):
    """Template processing failures during generation."""
    
    def __init__(self, template_type: str, processing_error: str, **kwargs):
        message = f"Template processing error for {template_type}: {processing_error}"
        details = {
            "template_type": template_type,
            "processing_error": processing_error,
            **kwargs
        }
        super().__init__(message, details)
        self.template_type = template_type
        self.processing_error = processing_error

class VariableSubstitutionError(DnDCharacterCreatorError):
    """Variable substitution failures in templates."""
    
    def __init__(self, variable_name: str, template_context: str, substitution_error: str, **kwargs):
        message = f"Variable substitution failed for '{variable_name}' in {template_context}: {substitution_error}"
        details = {
            "variable_name": variable_name,
            "template_context": template_context,
            "substitution_error": substitution_error,
            **kwargs
        }
        super().__init__(message, details)
        self.variable_name = variable_name
        self.template_context = template_context

# ============ NAME GENERATION EXCEPTIONS ============

class NameGenerationError(DnDCharacterCreatorError):
    """Character name generation failures."""
    
    def __init__(self, name_type: str, race: str, generation_error: str, **kwargs):
        message = f"Name generation failed for {name_type} {race} name: {generation_error}"
        details = {
            "name_type": name_type,
            "race": race,
            "generation_error": generation_error,
            **kwargs
        }
        super().__init__(message, details)
        self.name_type = name_type
        self.race = race
        self.generation_error = generation_error

class NameConflictError(DnDCharacterCreatorError):
    """Generated name conflicts with existing names."""
    
    def __init__(self, generated_name: str, conflict_source: str, **kwargs):
        message = f"Name conflict: '{generated_name}' conflicts with {conflict_source}"
        details = {
            "generated_name": generated_name,
            "conflict_source": conflict_source,
            **kwargs
        }
        super().__init__(message, details)
        self.generated_name = generated_name
        self.conflict_source = conflict_source

# ============ BACKSTORY GENERATION EXCEPTIONS ============

class BackstoryGenerationError(DnDCharacterCreatorError):
    """Character backstory generation failures."""
    
    def __init__(self, backstory_element: str, generation_context: str, error_detail: str, **kwargs):
        message = f"Backstory generation failed for {backstory_element} in {generation_context}: {error_detail}"
        details = {
            "backstory_element": backstory_element,
            "generation_context": generation_context,
            "error_detail": error_detail,
            **kwargs
        }
        super().__init__(message, details)
        self.backstory_element = backstory_element
        self.generation_context = generation_context

class InconsistentBackstoryError(DnDCharacterCreatorError):
    """Generated backstory elements are inconsistent."""
    
    def __init__(self, inconsistent_elements: List[str], consistency_issue: str, **kwargs):
        elements_str = ", ".join(inconsistent_elements)
        message = f"Backstory inconsistency in {elements_str}: {consistency_issue}"
        details = {
            "inconsistent_elements": inconsistent_elements,
            "consistency_issue": consistency_issue,
            **kwargs
        }
        super().__init__(message, details)
        self.inconsistent_elements = inconsistent_elements
        self.consistency_issue = consistency_issue

# ============ RANDOM GENERATION EXCEPTIONS ============

class RandomSeedError(DnDCharacterCreatorError):
    """Random seed or generation algorithm failures."""
    
    def __init__(self, seed_value: Any, algorithm: str, seed_error: str, **kwargs):
        message = f"Random seed error: {algorithm} failed with seed {seed_value} - {seed_error}"
        details = {
            "seed_value": seed_value,
            "algorithm": algorithm,
            "seed_error": seed_error,
            **kwargs
        }
        super().__init__(message, details)
        self.seed_value = seed_value
        self.algorithm = algorithm

# ============ UTILITY FUNCTIONS ============

def create_generation_failure(content_type: str, stage: str, reason: str) -> GenerationFailureError:
    """Factory function for generation failure errors."""
    return GenerationFailureError(content_type, stage, reason)

def create_creativity_constraint(level: str, content: str, constraint: str) -> CreativityConstraintError:
    """Factory function for creativity constraint errors."""
    return CreativityConstraintError(level, content, constraint)

def create_insufficient_data_error(data_type: str, required: int, available: int) -> InsufficientDataError:
    """Factory function for insufficient data errors."""
    return InsufficientDataError(data_type, required, available)

def is_retryable_generation_error(error: DnDCharacterCreatorError) -> bool:
    """Check if generation error can be retried with different parameters."""
    retryable_types = [
        GenerationFailureError,
        NameGenerationError,
        NameConflictError,
        BackstoryGenerationError,
        RandomSeedError
    ]
    return any(isinstance(error, error_type) for error_type in retryable_types)

def requires_manual_intervention(error: DnDCharacterCreatorError) -> bool:
    """Check if generation error requires manual user input."""
    manual_types = [
        CreativityConstraintError,
        InsufficientDataError,
        InconsistentBackstoryError,
        TemplateProcessingError
    ]
    return any(isinstance(error, error_type) for error_type in manual_types)

def get_generation_error_severity(error: DnDCharacterCreatorError) -> str:
    """Get generation error severity level."""
    severity_map = {
        GenerationFailureError: "error",
        CreativityConstraintError: "warning",
        InsufficientDataError: "error",
        TemplateProcessingError: "error",
        VariableSubstitutionError: "warning",
        NameGenerationError: "warning",
        NameConflictError: "info",
        BackstoryGenerationError: "warning",
        InconsistentBackstoryError: "warning",
        RandomSeedError: "error"
    }
    return severity_map.get(type(error), "warning")

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Content generation exceptions
    'GenerationFailureError',
    'CreativityConstraintError',
    'InsufficientDataError',
    
    # Template generation exceptions
    'TemplateProcessingError',
    'VariableSubstitutionError',
    
    # Name generation exceptions
    'NameGenerationError',
    'NameConflictError',
    
    # Backstory generation exceptions
    'BackstoryGenerationError',
    'InconsistentBackstoryError',
    
    # Random generation exceptions
    'RandomSeedError',
    
    # Utility functions
    'create_generation_failure',
    'create_creativity_constraint',
    'create_insufficient_data_error',
    'is_retryable_generation_error',
    'requires_manual_intervention',
    'get_generation_error_severity',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D generation exception handling'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/exceptions",
    "focus": "generation_error_handling_only",
    "line_target": 150,
    "dependencies": ["base"],
    "philosophy": "crude_functional_inspired_simple_generation_exceptions"
}