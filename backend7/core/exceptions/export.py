"""
Essential D&D Export Exception Types

Streamlined export-related exception handling following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from typing import Optional, Dict, Any, List
from .base import DnDCharacterCreatorError

# ============ FORMAT EXCEPTIONS ============

class UnsupportedFormatError(DnDCharacterCreatorError):
    """Unsupported export format requested."""
    
    def __init__(self, requested_format: str, supported_formats: List[str], **kwargs):
        formats_str = ", ".join(supported_formats)
        message = f"Unsupported format '{requested_format}'. Supported: {formats_str}"
        details = {
            "requested_format": requested_format,
            "supported_formats": supported_formats,
            **kwargs
        }
        super().__init__(message, details)
        self.requested_format = requested_format
        self.supported_formats = supported_formats

class FormatCorruptionError(DnDCharacterCreatorError):
    """Export format corruption or generation errors."""
    
    def __init__(self, format_type: str, corruption_stage: str, **kwargs):
        message = f"Format corruption in {format_type} export at {corruption_stage} stage"
        details = {
            "format_type": format_type,
            "corruption_stage": corruption_stage,
            **kwargs
        }
        super().__init__(message, details)
        self.format_type = format_type
        self.corruption_stage = corruption_stage

# ============ CONTENT EXCEPTIONS ============

class IncompleteDataError(DnDCharacterCreatorError):
    """Character data incomplete for export."""
    
    def __init__(self, missing_fields: List[str], export_format: str, **kwargs):
        fields_str = ", ".join(missing_fields)
        message = f"Incomplete data for {export_format} export. Missing: {fields_str}"
        details = {
            "missing_fields": missing_fields,
            "export_format": export_format,
            **kwargs
        }
        super().__init__(message, details)
        self.missing_fields = missing_fields
        self.export_format = export_format

class ContentFilterError(DnDCharacterCreatorError):
    """Content filtering issues during export."""
    
    def __init__(self, filter_type: str, filtered_content: List[str], **kwargs):
        content_str = ", ".join(filtered_content)
        message = f"Content filter error ({filter_type}): filtered {content_str}"
        details = {
            "filter_type": filter_type,
            "filtered_content": filtered_content,
            **kwargs
        }
        super().__init__(message, details)
        self.filter_type = filter_type
        self.filtered_content = filtered_content

# ============ OUTPUT EXCEPTIONS ============

class OutputGenerationError(DnDCharacterCreatorError):
    """Output file generation failures."""
    
    def __init__(self, output_type: str, generation_stage: str, error_detail: str, **kwargs):
        message = f"Output generation failed for {output_type} at {generation_stage}: {error_detail}"
        details = {
            "output_type": output_type,
            "generation_stage": generation_stage,
            "error_detail": error_detail,
            **kwargs
        }
        super().__init__(message, details)
        self.output_type = output_type
        self.generation_stage = generation_stage

class FileWriteError(DnDCharacterCreatorError):
    """File system write errors during export."""
    
    def __init__(self, file_path: str, write_error: str, **kwargs):
        message = f"File write error for '{file_path}': {write_error}"
        details = {
            "file_path": file_path,
            "write_error": write_error,
            **kwargs
        }
        super().__init__(message, details)
        self.file_path = file_path
        self.write_error = write_error

# ============ TEMPLATE EXCEPTIONS ============

class TemplateError(DnDCharacterCreatorError):
    """Template processing errors."""
    
    def __init__(self, template_name: str, template_error: str, **kwargs):
        message = f"Template error in '{template_name}': {template_error}"
        details = {
            "template_name": template_name,
            "template_error": template_error,
            **kwargs
        }
        super().__init__(message, details)
        self.template_name = template_name
        self.template_error = template_error

class LayoutError(DnDCharacterCreatorError):
    """Layout rendering errors in formatted exports."""
    
    def __init__(self, layout_type: str, element: str, layout_error: str, **kwargs):
        message = f"Layout error in {layout_type} for element '{element}': {layout_error}"
        details = {
            "layout_type": layout_type,
            "element": element,
            "layout_error": layout_error,
            **kwargs
        }
        super().__init__(message, details)
        self.layout_type = layout_type
        self.element = element

# ============ COMPRESSION EXCEPTIONS ============

class CompressionError(DnDCharacterCreatorError):
    """File compression errors during export."""
    
    def __init__(self, compression_type: str, compression_error: str, **kwargs):
        message = f"Compression error ({compression_type}): {compression_error}"
        details = {
            "compression_type": compression_type,
            "compression_error": compression_error,
            **kwargs
        }
        super().__init__(message, details)
        self.compression_type = compression_type
        self.compression_error = compression_error

# ============ UTILITY FUNCTIONS ============

def create_unsupported_format_error(requested: str, supported: List[str]) -> UnsupportedFormatError:
    """Factory function for unsupported format errors."""
    return UnsupportedFormatError(requested, supported)

def create_incomplete_data_error(missing_fields: List[str], format_type: str) -> IncompleteDataError:
    """Factory function for incomplete data errors."""
    return IncompleteDataError(missing_fields, format_type)

def create_output_generation_error(output_type: str, stage: str, detail: str) -> OutputGenerationError:
    """Factory function for output generation errors."""
    return OutputGenerationError(output_type, stage, detail)

def is_recoverable_export_error(error: DnDCharacterCreatorError) -> bool:
    """Check if export error is recoverable with retry."""
    recoverable_types = [
        IncompleteDataError,
        ContentFilterError,
        FileWriteError,
        CompressionError
    ]
    return any(isinstance(error, error_type) for error_type in recoverable_types)

def requires_user_intervention(error: DnDCharacterCreatorError) -> bool:
    """Check if export error requires user intervention."""
    intervention_required = [
        UnsupportedFormatError,
        IncompleteDataError,
        TemplateError,
        LayoutError
    ]
    return any(isinstance(error, error_type) for error_type in intervention_required)

def get_export_error_severity(error: DnDCharacterCreatorError) -> str:
    """Get export error severity level."""
    severity_map = {
        UnsupportedFormatError: "error",
        FormatCorruptionError: "critical",
        IncompleteDataError: "warning",
        ContentFilterError: "info",
        OutputGenerationError: "error",
        FileWriteError: "error",
        TemplateError: "error",
        LayoutError: "warning",
        CompressionError: "warning"
    }
    return severity_map.get(type(error), "error")

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Format exceptions
    'UnsupportedFormatError',
    'FormatCorruptionError',
    
    # Content exceptions
    'IncompleteDataError',
    'ContentFilterError',
    
    # Output exceptions
    'OutputGenerationError',
    'FileWriteError',
    
    # Template exceptions
    'TemplateError',
    'LayoutError',
    
    # Compression exceptions
    'CompressionError',
    
    # Utility functions
    'create_unsupported_format_error',
    'create_incomplete_data_error',
    'create_output_generation_error',
    'is_recoverable_export_error',
    'requires_user_intervention',
    'get_export_error_severity',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D export exception handling'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/exceptions",
    "focus": "export_error_handling_only",
    "line_target": 150,
    "dependencies": ["base"],
    "philosophy": "crude_functional_inspired_simple_export_exceptions"
}