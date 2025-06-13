"""
Content Generation Exceptions for the D&D Creative Content Framework.

This module defines exceptions related to content generation failures,
LLM errors, template processing issues, and generation workflow problems.
These exceptions represent business rule violations and failure states
in the creative content generation domain.

Following Clean Architecture principles, these exceptions are:
- Infrastructure-independent (don't depend on specific LLM providers)
- Focused on D&D content generation business rules
- Designed for proper error handling and recovery strategies
- Aligned with the interactive character creation workflow
"""

from typing import Dict, List, Optional, Any, Union
from ..enums.creativity_levels import CreativityLevel, GenerationMethod, ContentComplexity
from ..enums.content_types import ContentType, ThemeCategory
from ..enums.balance_levels import BalanceLevel
from ..enums.progression_types import ProgressionType


# ============ BASE GENERATION EXCEPTIONS ============

class GenerationError(Exception):
    """Base exception for all content generation errors."""
    
    def __init__(
        self,
        message: str,
        content_type: Optional[ContentType] = None,
        generation_method: Optional[GenerationMethod] = None,
        creativity_level: Optional[CreativityLevel] = None,
        context: Optional[Dict[str, Any]] = None,
        recovery_suggestions: Optional[List[str]] = None
    ):
        super().__init__(message)
        self.content_type = content_type
        self.generation_method = generation_method
        self.creativity_level = creativity_level
        self.context = context or {}
        self.recovery_suggestions = recovery_suggestions or []
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.content_type:
            parts.append(f"Content: {self.content_type.value}")
        
        if self.generation_method:
            parts.append(f"Method: {self.generation_method.value}")
        
        if self.creativity_level:
            parts.append(f"Creativity: {self.creativity_level.value}")
        
        if self.recovery_suggestions:
            parts.append(f"Suggestions: {'; '.join(self.recovery_suggestions[:2])}")
        
        return " | ".join(parts)

    def add_context(self, key: str, value: Any) -> None:
        """Add contextual information to the exception."""
        self.context[key] = value

    def add_recovery_suggestion(self, suggestion: str) -> None:
        """Add a recovery suggestion to the exception."""
        if suggestion not in self.recovery_suggestions:
            self.recovery_suggestions.append(suggestion)


class GenerationWorkflowError(GenerationError):
    """Exception for workflow-level generation failures."""
    
    def __init__(
        self,
        workflow_stage: str,
        stage_input: Optional[Dict[str, Any]] = None,
        stage_output: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Generation workflow failed at stage: {workflow_stage}"
        super().__init__(message, **kwargs)
        self.workflow_stage = workflow_stage
        self.stage_input = stage_input or {}
        self.stage_output = stage_output or {}


# ============ LLM PROVIDER EXCEPTIONS ============

class LLMProviderError(GenerationError):
    """Base exception for LLM provider-related failures."""
    
    def __init__(
        self,
        message: str,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.provider_name = provider_name
        self.model_name = model_name
        self.request_data = request_data or {}
        self.response_data = response_data or {}


class LLMConnectionError(LLMProviderError):
    """Exception for LLM connection and communication failures."""
    
    def __init__(
        self,
        connection_issue: str,
        endpoint: Optional[str] = None,
        retry_count: int = 0,
        **kwargs
    ):
        message = f"LLM connection failed: {connection_issue}"
        if endpoint:
            message += f" (endpoint: {endpoint})"
        if retry_count > 0:
            message += f" (retry {retry_count})"
        
        super().__init__(message, **kwargs)
        self.connection_issue = connection_issue
        self.endpoint = endpoint
        self.retry_count = retry_count


class LLMTimeoutError(LLMProviderError):
    """Exception for LLM request timeouts."""
    
    def __init__(
        self,
        timeout_duration: float,
        operation_type: str = "generation",
        **kwargs
    ):
        message = f"LLM {operation_type} timed out after {timeout_duration} seconds"
        super().__init__(message, **kwargs)
        self.timeout_duration = timeout_duration
        self.operation_type = operation_type


class LLMRateLimitError(LLMProviderError):
    """Exception for LLM rate limit violations."""
    
    def __init__(
        self,
        rate_limit_type: str = "requests",
        retry_after: Optional[int] = None,
        current_usage: Optional[Dict[str, int]] = None,
        **kwargs
    ):
        message = f"LLM {rate_limit_type} rate limit exceeded"
        if retry_after:
            message += f" (retry after {retry_after}s)"
        
        super().__init__(message, **kwargs)
        self.rate_limit_type = rate_limit_type
        self.retry_after = retry_after
        self.current_usage = current_usage or {}


class LLMQuotaExceededError(LLMProviderError):
    """Exception for LLM usage quota violations."""
    
    def __init__(
        self,
        quota_type: str,
        current_usage: Optional[int] = None,
        quota_limit: Optional[int] = None,
        reset_time: Optional[str] = None,
        **kwargs
    ):
        message = f"LLM {quota_type} quota exceeded"
        if current_usage and quota_limit:
            message += f" ({current_usage}/{quota_limit})"
        if reset_time:
            message += f" (resets: {reset_time})"
        
        super().__init__(message, **kwargs)
        self.quota_type = quota_type
        self.current_usage = current_usage
        self.quota_limit = quota_limit
        self.reset_time = reset_time


class LLMResponseError(LLMProviderError):
    """Exception for invalid or malformed LLM responses."""
    
    def __init__(
        self,
        response_issue: str,
        raw_response: Optional[str] = None,
        expected_format: Optional[str] = None,
        parsing_errors: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"LLM response error: {response_issue}"
        if expected_format:
            message += f" (expected: {expected_format})"
        
        super().__init__(message, **kwargs)
        self.response_issue = response_issue
        self.raw_response = raw_response
        self.expected_format = expected_format
        self.parsing_errors = parsing_errors or []


class LLMContentFilterError(LLMProviderError):
    """Exception for LLM content filtering violations."""
    
    def __init__(
        self,
        filter_type: str,
        filtered_content: Optional[str] = None,
        filter_reason: Optional[str] = None,
        **kwargs
    ):
        message = f"LLM content filtered: {filter_type}"
        if filter_reason:
            message += f" - {filter_reason}"
        
        super().__init__(message, **kwargs)
        self.filter_type = filter_type
        self.filtered_content = filtered_content
        self.filter_reason = filter_reason


# ============ CHARACTER GENERATION EXCEPTIONS ============

class CharacterGenerationError(GenerationError):
    """Exception for character generation failures."""
    
    def __init__(
        self,
        generation_stage: str,
        character_concept: Optional[str] = None,
        partial_character: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Character generation failed at {generation_stage}"
        if character_concept:
            message += f" for concept: {character_concept}"
        
        super().__init__(
            message,
            content_type=ContentType.CHARACTER,
            **kwargs
        )
        self.generation_stage = generation_stage
        self.character_concept = character_concept
        self.partial_character = partial_character or {}


class CharacterConceptError(CharacterGenerationError):
    """Exception for character concept processing failures."""
    
    def __init__(
        self,
        concept_issue: str,
        user_input: Optional[str] = None,
        concept_analysis: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Character concept error: {concept_issue}"
        super().__init__(
            "concept_processing",
            character_concept=user_input,
            **kwargs
        )
        self.concept_issue = concept_issue
        self.user_input = user_input
        self.concept_analysis = concept_analysis or {}


class CharacterBuildError(CharacterGenerationError):
    """Exception for character build construction failures."""
    
    def __init__(
        self,
        build_issue: str,
        character_class: Optional[str] = None,
        character_species: Optional[str] = None,
        level_range: Optional[tuple] = None,
        **kwargs
    ):
        message = f"Character build error: {build_issue}"
        if character_class:
            message += f" (class: {character_class})"
        if character_species:
            message += f" (species: {character_species})"
        
        super().__init__(
            "build_construction",
            **kwargs
        )
        self.build_issue = build_issue
        self.character_class = character_class
        self.character_species = character_species
        self.level_range = level_range


class CharacterProgressionError(CharacterGenerationError):
    """Exception for character progression generation failures."""
    
    def __init__(
        self,
        progression_issue: str,
        progression_type: Optional[ProgressionType] = None,
        current_level: Optional[int] = None,
        target_level: Optional[int] = None,
        **kwargs
    ):
        message = f"Character progression error: {progression_issue}"
        if current_level and target_level:
            message += f" (levels {current_level}-{target_level})"
        
        super().__init__(
            "progression_generation",
            **kwargs
        )
        self.progression_issue = progression_issue
        self.progression_type = progression_type
        self.current_level = current_level
        self.target_level = target_level


# ============ CONTENT GENERATION EXCEPTIONS ============

class CustomContentError(GenerationError):
    """Exception for custom content generation failures."""
    
    def __init__(
        self,
        content_name: str,
        generation_issue: str,
        content_requirements: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Custom content '{content_name}' generation failed: {generation_issue}"
        super().__init__(message, **kwargs)
        self.content_name = content_name
        self.generation_issue = generation_issue
        self.content_requirements = content_requirements or {}


class ContentBalanceError(CustomContentError):
    """Exception for content balance failures during generation."""
    
    def __init__(
        self,
        content_name: str,
        balance_issue: str,
        power_level: Optional[float] = None,
        balance_target: Optional[BalanceLevel] = None,
        **kwargs
    ):
        message = f"Content '{content_name}' balance error: {balance_issue}"
        if power_level:
            message += f" (power: {power_level:.2f})"
        
        super().__init__(content_name, balance_issue, **kwargs)
        self.balance_issue = balance_issue
        self.power_level = power_level
        self.balance_target = balance_target


class ContentThemeError(CustomContentError):
    """Exception for content theme consistency failures."""
    
    def __init__(
        self,
        content_name: str,
        theme_issue: str,
        requested_themes: Optional[List[ThemeCategory]] = None,
        conflicting_themes: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Content '{content_name}' theme error: {theme_issue}"
        super().__init__(content_name, theme_issue, **kwargs)
        self.theme_issue = theme_issue
        self.requested_themes = requested_themes or []
        self.conflicting_themes = conflicting_themes or []


class ContentComplexityError(CustomContentError):
    """Exception for content complexity management failures."""
    
    def __init__(
        self,
        content_name: str,
        complexity_issue: str,
        target_complexity: Optional[ContentComplexity] = None,
        actual_complexity: Optional[ContentComplexity] = None,
        **kwargs
    ):
        message = f"Content '{content_name}' complexity error: {complexity_issue}"
        if target_complexity and actual_complexity:
            message += f" (target: {target_complexity.value}, actual: {actual_complexity.value})"
        
        super().__init__(content_name, complexity_issue, **kwargs)
        self.complexity_issue = complexity_issue
        self.target_complexity = target_complexity
        self.actual_complexity = actual_complexity


# ============ TEMPLATE AND PROMPT EXCEPTIONS ============

class TemplateError(GenerationError):
    """Exception for template processing failures."""
    
    def __init__(
        self,
        template_name: str,
        template_issue: str,
        template_variables: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Template '{template_name}' error: {template_issue}"
        super().__init__(message, **kwargs)
        self.template_name = template_name
        self.template_issue = template_issue
        self.template_variables = template_variables or {}


class TemplateMissingError(TemplateError):
    """Exception for missing template files or definitions."""
    
    def __init__(
        self,
        template_name: str,
        template_type: str,
        search_locations: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Template '{template_name}' not found"
        if search_locations:
            message += f" in: {', '.join(search_locations)}"
        
        super().__init__(template_name, f"missing {template_type} template", **kwargs)
        self.template_type = template_type
        self.search_locations = search_locations or []


class TemplateVariableError(TemplateError):
    """Exception for template variable processing failures."""
    
    def __init__(
        self,
        template_name: str,
        variable_name: str,
        variable_issue: str,
        expected_type: Optional[str] = None,
        actual_value: Optional[Any] = None,
        **kwargs
    ):
        message = f"Template variable '{variable_name}' error: {variable_issue}"
        if expected_type:
            message += f" (expected: {expected_type})"
        
        super().__init__(template_name, message, **kwargs)
        self.variable_name = variable_name
        self.variable_issue = variable_issue
        self.expected_type = expected_type
        self.actual_value = actual_value


class PromptProcessingError(GenerationError):
    """Exception for prompt processing and formatting failures."""
    
    def __init__(
        self,
        prompt_type: str,
        processing_issue: str,
        prompt_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Prompt processing error ({prompt_type}): {processing_issue}"
        super().__init__(message, **kwargs)
        self.prompt_type = prompt_type
        self.processing_issue = processing_issue
        self.prompt_data = prompt_data or {}


# ============ GENERATION CONSTRAINT EXCEPTIONS ============

class GenerationConstraintError(GenerationError):
    """Exception for generation constraint violations."""
    
    def __init__(
        self,
        constraint_type: str,
        constraint_value: Any,
        current_value: Any,
        constraint_description: Optional[str] = None,
        **kwargs
    ):
        message = f"Generation constraint violated: {constraint_type}"
        if constraint_description:
            message += f" - {constraint_description}"
        message += f" (limit: {constraint_value}, current: {current_value})"
        
        super().__init__(message, **kwargs)
        self.constraint_type = constraint_type
        self.constraint_value = constraint_value
        self.current_value = current_value
        self.constraint_description = constraint_description


class GenerationTimeoutError(GenerationConstraintError):
    """Exception for generation timeout violations."""
    
    def __init__(
        self,
        timeout_duration: float,
        operation_name: str,
        partial_result: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            "timeout",
            timeout_duration,
            timeout_duration,
            f"{operation_name} exceeded time limit",
            **kwargs
        )
        self.timeout_duration = timeout_duration
        self.operation_name = operation_name
        self.partial_result = partial_result or {}


class GenerationLimitError(GenerationConstraintError):
    """Exception for generation limit violations."""
    
    def __init__(
        self,
        limit_type: str,
        limit_value: int,
        current_count: int,
        limit_scope: str = "session",
        **kwargs
    ):
        super().__init__(
            f"{limit_scope}_{limit_type}_limit",
            limit_value,
            current_count,
            f"{limit_type} limit exceeded for {limit_scope}",
            **kwargs
        )
        self.limit_type = limit_type
        self.limit_value = limit_value
        self.current_count = current_count
        self.limit_scope = limit_scope


class GenerationIterationError(GenerationConstraintError):
    """Exception for excessive generation iterations."""
    
    def __init__(
        self,
        max_iterations: int,
        current_iteration: int,
        failure_reason: Optional[str] = None,
        iteration_history: Optional[List[str]] = None,
        **kwargs
    ):
        reason = failure_reason or "quality threshold not met"
        super().__init__(
            "max_iterations",
            max_iterations,
            current_iteration,
            f"Generation failed after maximum iterations: {reason}",
            **kwargs
        )
        self.max_iterations = max_iterations
        self.current_iteration = current_iteration
        self.failure_reason = failure_reason
        self.iteration_history = iteration_history or []


# ============ DEPENDENCY AND INTEGRATION EXCEPTIONS ============

class GenerationDependencyError(GenerationError):
    """Exception for generation dependency failures."""
    
    def __init__(
        self,
        dependency_type: str,
        dependency_name: str,
        dependency_issue: str,
        required_for: Optional[str] = None,
        **kwargs
    ):
        message = f"Generation dependency failed: {dependency_type} '{dependency_name}' - {dependency_issue}"
        if required_for:
            message += f" (required for: {required_for})"
        
        super().__init__(message, **kwargs)
        self.dependency_type = dependency_type
        self.dependency_name = dependency_name
        self.dependency_issue = dependency_issue
        self.required_for = required_for


class GenerationProviderError(GenerationError):
    """Exception for generation provider unavailability."""
    
    def __init__(
        self,
        provider_name: str,
        provider_issue: str,
        fallback_providers: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Generation provider '{provider_name}' unavailable: {provider_issue}"
        if fallback_providers:
            message += f" (fallbacks: {', '.join(fallback_providers)})"
        
        super().__init__(message, **kwargs)
        self.provider_name = provider_name
        self.provider_issue = provider_issue
        self.fallback_providers = fallback_providers or []


class GenerationRetryExhaustedError(GenerationError):
    """Exception for exhausted generation retry attempts."""
    
    def __init__(
        self,
        operation_name: str,
        max_retries: int,
        retry_reasons: List[str],
        final_error: Optional[Exception] = None,
        **kwargs
    ):
        message = f"Generation retry exhausted for {operation_name} after {max_retries} attempts"
        if final_error:
            message += f". Final error: {str(final_error)}"
        
        super().__init__(message, **kwargs)
        self.operation_name = operation_name
        self.max_retries = max_retries
        self.retry_reasons = retry_reasons
        self.final_error = final_error


# ============ CONVERSATIONAL WORKFLOW EXCEPTIONS ============

class ConversationError(GenerationError):
    """Exception for conversation workflow failures."""
    
    def __init__(
        self,
        conversation_stage: str,
        conversation_issue: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        message = f"Conversation error at {conversation_stage}: {conversation_issue}"
        super().__init__(message, **kwargs)
        self.conversation_stage = conversation_stage
        self.conversation_issue = conversation_issue
        self.conversation_history = conversation_history or []


class UserInputError(ConversationError):
    """Exception for user input processing failures."""
    
    def __init__(
        self,
        input_issue: str,
        user_input: Optional[str] = None,
        expected_format: Optional[str] = None,
        **kwargs
    ):
        message = f"User input error: {input_issue}"
        if expected_format:
            message += f" (expected: {expected_format})"
        
        super().__init__(
            "user_input_processing",
            input_issue,
            **kwargs
        )
        self.input_issue = input_issue
        self.user_input = user_input
        self.expected_format = expected_format


class ConversationStateError(ConversationError):
    """Exception for conversation state management failures."""
    
    def __init__(
        self,
        state_issue: str,
        current_state: Optional[str] = None,
        expected_state: Optional[str] = None,
        **kwargs
    ):
        message = f"Conversation state error: {state_issue}"
        if current_state and expected_state:
            message += f" (current: {current_state}, expected: {expected_state})"
        
        super().__init__(
            "state_management",
            state_issue,
            **kwargs
        )
        self.state_issue = state_issue
        self.current_state = current_state
        self.expected_state = expected_state


# ============ UTILITY FUNCTIONS FOR EXCEPTION HANDLING ============

def categorize_generation_error(error: Exception) -> str:
    """
    Categorize a generation error for handling and routing.
    
    Args:
        error: The exception to categorize
        
    Returns:
        Error category string
    """
    if isinstance(error, LLMProviderError):
        return "llm_provider"
    elif isinstance(error, CharacterGenerationError):
        return "character_generation"
    elif isinstance(error, CustomContentError):
        return "custom_content"
    elif isinstance(error, TemplateError):
        return "template_processing"
    elif isinstance(error, GenerationConstraintError):
        return "generation_constraints"
    elif isinstance(error, GenerationDependencyError):
        return "dependency"
    elif isinstance(error, ConversationError):
        return "conversation_workflow"
    elif isinstance(error, GenerationError):
        return "general_generation"
    else:
        return "unknown"


def is_retryable_generation_error(error: Exception) -> bool:
    """
    Determine if a generation error is retryable.
    
    Args:
        error: The exception to check
        
    Returns:
        True if the error might succeed on retry
    """
    # Network and timeout errors are generally retryable
    if isinstance(error, (LLMConnectionError, LLMTimeoutError, GenerationTimeoutError)):
        return True
    
    # Rate limit errors are retryable with delay
    if isinstance(error, LLMRateLimitError):
        return True
    
    # Provider unavailable might be temporary
    if isinstance(error, GenerationProviderError):
        return True
    
    # Response format errors might succeed with different prompt
    if isinstance(error, LLMResponseError):
        return True
    
    # Configuration and quota errors are not retryable
    if isinstance(error, (LLMQuotaExceededError, TemplateVariableError)):
        return False
    
    # Content filter errors are not retryable
    if isinstance(error, LLMContentFilterError):
        return False
    
    # Retry exhausted errors are not retryable
    if isinstance(error, GenerationRetryExhaustedError):
        return False
    
    # Default to not retryable for safety
    return False


def get_retry_delay_for_error(error: Exception) -> Optional[float]:
    """
    Get recommended retry delay for a retryable error.
    
    Args:
        error: The exception to get delay for
        
    Returns:
        Delay in seconds, or None if not retryable
    """
    if isinstance(error, LLMRateLimitError) and error.retry_after:
        return float(error.retry_after)
    
    if isinstance(error, LLMTimeoutError):
        return 2.0  # Short delay for timeout
    
    if isinstance(error, GenerationTimeoutError):
        return 5.0  # Longer delay for generation timeout
    
    if isinstance(error, GenerationProviderError):
        return 10.0  # Longer delay for provider issues
    
    if isinstance(error, LLMConnectionError):
        return min(2.0 ** error.retry_count, 30.0)  # Exponential backoff
    
    if is_retryable_generation_error(error):
        return 1.0  # Default retry delay
    
    return None


def extract_recovery_suggestions(error: GenerationError) -> List[str]:
    """
    Extract actionable recovery suggestions from a generation error.
    
    Args:
        error: The generation error to analyze
        
    Returns:
        List of recovery suggestions
    """
    if hasattr(error, 'recovery_suggestions') and error.recovery_suggestions:
        return error.recovery_suggestions
    
    suggestions = []
    
    if isinstance(error, LLMRateLimitError):
        suggestions.append("Wait for rate limit reset")
        if error.retry_after:
            suggestions.append(f"Retry after {error.retry_after} seconds")
    
    elif isinstance(error, LLMQuotaExceededError):
        suggestions.append("Check API quota and billing")
        if error.reset_time:
            suggestions.append(f"Quota resets: {error.reset_time}")
    
    elif isinstance(error, CharacterConceptError):
        suggestions.append("Simplify character concept")
        suggestions.append("Provide more specific details")
        suggestions.append("Try a different creativity level")
    
    elif isinstance(error, ContentBalanceError):
        suggestions.append("Reduce power level requirements")
        suggestions.append("Accept balance warnings")
        suggestions.append("Use conservative balance mode")
    
    elif isinstance(error, GenerationProviderError):
        if error.fallback_providers:
            suggestions.extend([f"Try {provider}" for provider in error.fallback_providers])
    
    elif isinstance(error, UserInputError):
        suggestions.append("Rephrase your request")
        if error.expected_format:
            suggestions.append(f"Use format: {error.expected_format}")
    
    return suggestions


def create_generation_error_context(
    operation: str,
    inputs: Optional[Dict[str, Any]] = None,
    stage: Optional[str] = None,
    progress: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create standardized error context for generation operations.
    
    Args:
        operation: Name of the operation that failed
        inputs: Input parameters for the operation
        stage: Current stage of the operation
        progress: Progress percentage (0.0-1.0)
        
    Returns:
        Context dictionary for error reporting
    """
    context = {
        "operation": operation,
        "timestamp": None,  # Will be set by infrastructure layer
        "stage": stage,
        "progress": progress
    }
    
    if inputs:
        # Sanitize inputs (remove sensitive data)
        sanitized_inputs = {}
        for key, value in inputs.items():
            if key.lower() in ['api_key', 'token', 'password']:
                sanitized_inputs[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 1000:
                sanitized_inputs[key] = value[:1000] + "... [TRUNCATED]"
            else:
                sanitized_inputs[key] = value
        context["inputs"] = sanitized_inputs
    
    return context


def should_fail_fast(error: GenerationError) -> bool:
    """
    Determine if an error should cause immediate failure (fail-fast).
    
    Args:
        error: The generation error to assess
        
    Returns:
        True if this error should stop all processing immediately
    """
    # Critical quota issues should fail fast
    if isinstance(error, LLMQuotaExceededError):
        return True
    
    # Content filter violations should fail fast
    if isinstance(error, LLMContentFilterError):
        return True
    
    # Template missing errors should fail fast
    if isinstance(error, TemplateMissingError):
        return True
    
    # Retry exhausted should fail fast
    if isinstance(error, GenerationRetryExhaustedError):
        return True
    
    # Most other errors can be handled gracefully
    return False


# ============ MODULE METADATA ============

__version__ = '2.0.0'
__description__ = 'Content generation exceptions for D&D Creative Content Framework'
__author__ = 'D&D Character Creator Backend6'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/exceptions",
    "dependencies": ["core/enums"],
    "dependents": ["domain/services", "application/use_cases", "infrastructure"],
    "infrastructure_independent": True,
    "focuses_on": "D&D content generation business rules and failure states"
}

# Exception statistics
EXCEPTION_STATISTICS = {
    "base_exceptions": 3,
    "llm_provider_exceptions": 6,
    "character_generation_exceptions": 4,
    "content_generation_exceptions": 4,
    "template_exceptions": 3,
    "constraint_exceptions": 4,
    "dependency_exceptions": 3,
    "conversation_exceptions": 3,
    "total_exception_types": 30,
    "utility_functions": 8
}