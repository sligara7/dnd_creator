"""
Content generation exceptions for the D&D Creative Content Framework.

This module defines exceptions related to content generation failures,
LLM errors, template processing issues, and generation workflow problems.
"""

from typing import Dict, List, Optional, Any
from ..enums.generation_methods import GenerationMethod, LLMProvider
from ..enums.content_types import ContentType


class GenerationError(Exception):
    """Base exception for all content generation errors."""
    
    def __init__(
        self,
        message: str,
        content_type: Optional[ContentType] = None,
        generation_method: Optional[GenerationMethod] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.content_type = content_type
        self.generation_method = generation_method
        self.context = context or {}
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.content_type:
            parts.append(f"Content Type: {self.content_type.value}")
        
        if self.generation_method:
            parts.append(f"Generation Method: {self.generation_method.value}")
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        
        return " | ".join(parts)


class LLMError(GenerationError):
    """Exception for LLM-related generation failures."""
    
    def __init__(
        self,
        message: str,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        response_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.provider = provider
        self.model = model
        self.response_data = response_data or {}


class LLMTimeoutError(LLMError):
    """Exception for LLM request timeouts."""
    
    def __init__(
        self,
        timeout_duration: float,
        provider: Optional[LLMProvider] = None,
        **kwargs
    ):
        message = f"LLM request timed out after {timeout_duration} seconds"
        super().__init__(message, provider=provider, **kwargs)
        self.timeout_duration = timeout_duration


class LLMRateLimitError(LLMError):
    """Exception for LLM rate limit violations."""
    
    def __init__(
        self,
        retry_after: Optional[int] = None,
        provider: Optional[LLMProvider] = None,
        **kwargs
    ):
        message = "LLM API rate limit exceeded"
        if retry_after:
            message += f" (retry after {retry_after} seconds)"
        
        super().__init__(message, provider=provider, **kwargs)
        self.retry_after = retry_after


class LLMQuotaExceededError(LLMError):
    """Exception for LLM quota/usage limit violations."""
    
    def __init__(
        self,
        quota_type: str = "requests",
        provider: Optional[LLMProvider] = None,
        **kwargs
    ):
        message = f"LLM {quota_type} quota exceeded"
        super().__init__(message, provider=provider, **kwargs)
        self.quota_type = quota_type


class LLMResponseError(LLMError):
    """Exception for invalid or malformed LLM responses."""
    
    def __init__(
        self,
        message: str,
        response_content: Optional[str] = None,
        expected_format: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.response_content = response_content
        self.expected_format = expected_format


class TemplateError(GenerationError):
    """Exception for template processing failures."""
    
    def __init__(
        self,
        message: str,
        template_name: Optional[str] = None,
        template_variables: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.template_name = template_name
        self.template_variables = template_variables or {}


class TemplateMissingError(TemplateError):
    """Exception for missing template files or definitions."""
    
    def __init__(
        self,
        template_name: str,
        search_paths: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Template '{template_name}' not found"
        if search_paths:
            message += f" in paths: {', '.join(search_paths)}"
        
        super().__init__(message, template_name=template_name, **kwargs)
        self.search_paths = search_paths or []


class TemplateVariableError(TemplateError):
    """Exception for missing or invalid template variables."""
    
    def __init__(
        self,
        variable_name: str,
        template_name: Optional[str] = None,
        required_type: Optional[str] = None,
        actual_value: Optional[Any] = None,
        **kwargs
    ):
        message = f"Template variable '{variable_name}' is invalid"
        if required_type:
            message += f" (expected {required_type}"
            if actual_value is not None:
                message += f", got {type(actual_value).__name__}: {actual_value}"
            message += ")"
        
        super().__init__(message, template_name=template_name, **kwargs)
        self.variable_name = variable_name
        self.required_type = required_type
        self.actual_value = actual_value


class ContentGenerationTimeoutError(GenerationError):
    """Exception for content generation timeouts."""
    
    def __init__(
        self,
        timeout_duration: float,
        generation_stage: Optional[str] = None,
        **kwargs
    ):
        message = f"Content generation timed out after {timeout_duration} seconds"
        if generation_stage:
            message += f" during {generation_stage} stage"
        
        super().__init__(message, **kwargs)
        self.timeout_duration = timeout_duration
        self.generation_stage = generation_stage


class ContentGenerationLimitError(GenerationError):
    """Exception for exceeding generation limits or quotas."""
    
    def __init__(
        self,
        limit_type: str,
        current_count: int,
        limit_value: int,
        **kwargs
    ):
        message = f"{limit_type} limit exceeded: {current_count}/{limit_value}"
        super().__init__(message, **kwargs)
        self.limit_type = limit_type
        self.current_count = current_count
        self.limit_value = limit_value


class IterationLimitError(GenerationError):
    """Exception for exceeding maximum generation iterations."""
    
    def __init__(
        self,
        max_iterations: int,
        current_iteration: int,
        failure_reason: Optional[str] = None,
        **kwargs
    ):
        message = f"Generation failed after {current_iteration}/{max_iterations} iterations"
        if failure_reason:
            message += f": {failure_reason}"
        
        super().__init__(message, **kwargs)
        self.max_iterations = max_iterations
        self.current_iteration = current_iteration
        self.failure_reason = failure_reason


class ContentDependencyError(GenerationError):
    """Exception for missing or invalid content dependencies."""
    
    def __init__(
        self,
        dependency_type: str,
        dependency_id: Optional[str] = None,
        required_for: Optional[str] = None,
        **kwargs
    ):
        message = f"Missing {dependency_type} dependency"
        if dependency_id:
            message += f": {dependency_id}"
        if required_for:
            message += f" (required for {required_for})"
        
        super().__init__(message, **kwargs)
        self.dependency_type = dependency_type
        self.dependency_id = dependency_id
        self.required_for = required_for


class ContentFormatError(GenerationError):
    """Exception for invalid content format or structure."""
    
    def __init__(
        self,
        message: str,
        expected_format: Optional[str] = None,
        actual_content: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.expected_format = expected_format
        self.actual_content = actual_content


class ContentParsingError(GenerationError):
    """Exception for errors parsing generated content."""
    
    def __init__(
        self,
        message: str,
        raw_content: Optional[str] = None,
        parser_type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.raw_content = raw_content
        self.parser_type = parser_type


class GenerationConfigError(GenerationError):
    """Exception for invalid generation configuration."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        valid_options: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.config_value = config_value
        self.valid_options = valid_options or []


class ProviderUnavailableError(GenerationError):
    """Exception for unavailable generation providers."""
    
    def __init__(
        self,
        provider: str,
        reason: Optional[str] = None,
        alternative_providers: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Generation provider '{provider}' is unavailable"
        if reason:
            message += f": {reason}"
        
        super().__init__(message, **kwargs)
        self.provider = provider
        self.reason = reason
        self.alternative_providers = alternative_providers or []


class ContentPostProcessingError(GenerationError):
    """Exception for errors during content post-processing."""
    
    def __init__(
        self,
        message: str,
        processing_stage: Optional[str] = None,
        original_content: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.processing_stage = processing_stage
        self.original_content = original_content


class GenerationRetryExhaustedError(GenerationError):
    """Exception for exhausted retry attempts."""
    
    def __init__(
        self,
        max_retries: int,
        last_error: Optional[Exception] = None,
        retry_history: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Generation failed after {max_retries} retry attempts"
        if last_error:
            message += f". Last error: {str(last_error)}"
        
        super().__init__(message, **kwargs)
        self.max_retries = max_retries
        self.last_error = last_error
        self.retry_history = retry_history or []


# === UTILITY FUNCTIONS ===

def categorize_generation_error(error: Exception) -> str:
    """
    Categorize a generation error for logging and handling.
    
    Args:
        error: The exception to categorize
        
    Returns:
        Error category string
    """
    if isinstance(error, LLMError):
        return "llm_error"
    elif isinstance(error, TemplateError):
        return "template_error"
    elif isinstance(error, ContentGenerationTimeoutError):
        return "timeout_error"
    elif isinstance(error, ContentGenerationLimitError):
        return "limit_error"
    elif isinstance(error, ContentDependencyError):
        return "dependency_error"
    elif isinstance(error, ContentFormatError):
        return "format_error"
    elif isinstance(error, GenerationConfigError):
        return "config_error"
    elif isinstance(error, ProviderUnavailableError):
        return "provider_error"
    elif isinstance(error, GenerationError):
        return "generation_error"
    else:
        return "unknown_error"


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if a generation error is retryable.
    
    Args:
        error: The exception to check
        
    Returns:
        True if the error is retryable
    """
    # Network/timeout errors are generally retryable
    if isinstance(error, (LLMTimeoutError, LLMRateLimitError, ContentGenerationTimeoutError)):
        return True
    
    # Provider unavailable might be temporary
    if isinstance(error, ProviderUnavailableError):
        return True
    
    # Format errors might be fixed with a retry
    if isinstance(error, (ContentFormatError, ContentParsingError)):
        return True
    
    # Config errors and quota errors are not retryable
    if isinstance(error, (GenerationConfigError, LLMQuotaExceededError)):
        return False
    
    # Template errors are not retryable
    if isinstance(error, TemplateError):
        return False
    
    # Default to not retryable for safety
    return False


def get_retry_delay(error: Exception) -> Optional[float]:
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
    
    if isinstance(error, ContentGenerationTimeoutError):
        return 5.0  # Longer delay for generation timeout
    
    if isinstance(error, ProviderUnavailableError):
        return 10.0  # Longer delay for provider issues
    
    if is_retryable_error(error):
        return 1.0  # Default retry delay
    
    return None