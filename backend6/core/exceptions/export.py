"""
Export and VTT Format Exceptions for the D&D Creative Content Framework.

This module defines exceptions related to character sheet export failures,
VTT platform compatibility issues, format conversion problems, and template
rendering errors. These exceptions represent business rule violations and
failure states in the export and format conversion domain.

Following Clean Architecture principles, these exceptions are:
- Infrastructure-independent (don't depend on specific VTT platforms)
- Focused on D&D export and format conversion business rules
- Designed for proper error handling and recovery strategies
- Aligned with the character sheet export and VTT integration workflow
"""

from typing import Dict, List, Optional, Any, Union
from ..enums.export_formats import ExportFormat, VTTPlatform, ExportQuality, ExportStatus
from ..enums.content_types import ContentType, ContentRarity
from ..enums.validation_types import ValidationSeverity
from .base import DnDFrameworkError, ValidationError


# ============ BASE EXPORT EXCEPTIONS ============

class ExportError(DnDFrameworkError):
    """Base exception for all export and format conversion errors."""
    
    def __init__(
        self,
        message: str,
        export_format: Optional[ExportFormat] = None,
        export_stage: Optional[str] = None,
        character_data: Optional[Dict[str, Any]] = None,
        export_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.export_format = export_format
        self.export_stage = export_stage
        self.character_data = character_data or {}
        self.export_metadata = export_metadata or {}
    
    def _generate_error_code(self) -> str:
        """Generate export-specific error code."""
        base_code = "EXP"
        format_code = self.export_format.value[:3].upper() if self.export_format else "GEN"
        timestamp_code = str(int(self.timestamp.timestamp()))[-6:]
        return f"{base_code}_{format_code}_{timestamp_code}"
    
    def get_category(self) -> str:
        """Export error category."""
        return "export"
    
    def is_retryable(self) -> bool:
        """Most export errors are retryable."""
        return True
    
    def should_fail_fast(self) -> bool:
        """Export errors don't fail fast by default."""
        return False
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.export_format:
            parts.append(f"Format: {self.export_format.value}")
        
        if self.export_stage:
            parts.append(f"Stage: {self.export_stage}")
        
        return " | ".join(parts)


class VTTExportError(ExportError):
    """Base exception for VTT platform export failures."""
    
    def __init__(
        self,
        message: str,
        vtt_platform: Optional[VTTPlatform] = None,
        platform_version: Optional[str] = None,
        compatibility_issues: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.vtt_platform = vtt_platform
        self.platform_version = platform_version
        self.compatibility_issues = compatibility_issues or []
    
    def get_category(self) -> str:
        return "vtt_export"
    
    def __str__(self) -> str:
        parts = [super().__str__()]
        
        if self.vtt_platform:
            parts.append(f"Platform: {self.vtt_platform.value}")
        
        if self.platform_version:
            parts.append(f"Version: {self.platform_version}")
        
        return " | ".join(parts)


# ============ VTT PLATFORM SPECIFIC EXCEPTIONS ============

class DNDBeyondExportError(VTTExportError):
    """Exception for D&D Beyond export failures."""
    
    def __init__(
        self,
        export_issue: str,
        dndbeyond_limitations: Optional[List[str]] = None,
        unsupported_features: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"D&D Beyond export failed: {export_issue}"
        super().__init__(
            message,
            vtt_platform=VTTPlatform.DND_BEYOND,
            **kwargs
        )
        self.export_issue = export_issue
        self.dndbeyond_limitations = dndbeyond_limitations or []
        self.unsupported_features = unsupported_features or []
    
    def get_category(self) -> str:
        return "dndbeyond_export"


class Roll20ExportError(VTTExportError):
    """Exception for Roll20 export failures."""
    
    def __init__(
        self,
        export_issue: str,
        roll20_limitations: Optional[List[str]] = None,
        macro_issues: Optional[List[str]] = None,
        sheet_template_issues: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Roll20 export failed: {export_issue}"
        super().__init__(
            message,
            vtt_platform=VTTPlatform.ROLL20,
            **kwargs
        )
        self.export_issue = export_issue
        self.roll20_limitations = roll20_limitations or []
        self.macro_issues = macro_issues or []
        self.sheet_template_issues = sheet_template_issues or []
    
    def get_category(self) -> str:
        return "roll20_export"


class FantasyGroundsExportError(VTTExportError):
    """Exception for Fantasy Grounds export failures."""
    
    def __init__(
        self,
        export_issue: str,
        fg_version: Optional[str] = None,
        ruleset_compatibility: Optional[List[str]] = None,
        module_conflicts: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Fantasy Grounds export failed: {export_issue}"
        super().__init__(
            message,
            vtt_platform=VTTPlatform.FANTASY_GROUNDS,
            platform_version=fg_version,
            **kwargs
        )
        self.export_issue = export_issue
        self.fg_version = fg_version
        self.ruleset_compatibility = ruleset_compatibility or []
        self.module_conflicts = module_conflicts or []
    
    def get_category(self) -> str:
        return "fantasy_grounds_export"


class FoundryVTTExportError(VTTExportError):
    """Exception for Foundry VTT export failures."""
    
    def __init__(
        self,
        export_issue: str,
        foundry_version: Optional[str] = None,
        system_compatibility: Optional[str] = None,
        module_dependencies: Optional[List[str]] = None,
        world_compatibility: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Foundry VTT export failed: {export_issue}"
        super().__init__(
            message,
            vtt_platform=VTTPlatform.FOUNDRY_VTT,
            platform_version=foundry_version,
            **kwargs
        )
        self.export_issue = export_issue
        self.foundry_version = foundry_version
        self.system_compatibility = system_compatibility
        self.module_dependencies = module_dependencies or []
        self.world_compatibility = world_compatibility or []
    
    def get_category(self) -> str:
        return "foundry_vtt_export"


class EncounterPlusExportError(VTTExportError):
    """Exception for Encounter+ export failures."""
    
    def __init__(
        self,
        export_issue: str,
        encounter_plus_limitations: Optional[List[str]] = None,
        compendium_issues: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Encounter+ export failed: {export_issue}"
        super().__init__(
            message,
            vtt_platform=VTTPlatform.ENCOUNTER_PLUS,
            **kwargs
        )
        self.export_issue = export_issue
        self.encounter_plus_limitations = encounter_plus_limitations or []
        self.compendium_issues = compendium_issues or []
    
    def get_category(self) -> str:
        return "encounter_plus_export"


# ============ FORMAT CONVERSION EXCEPTIONS ============

class FormatConversionError(ExportError):
    """Exception for format conversion failures."""
    
    def __init__(
        self,
        source_format: str,
        target_format: str,
        conversion_issue: str,
        data_loss: Optional[List[str]] = None,
        conversion_warnings: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Format conversion failed from {source_format} to {target_format}: {conversion_issue}"
        super().__init__(message, **kwargs)
        self.source_format = source_format
        self.target_format = target_format
        self.conversion_issue = conversion_issue
        self.data_loss = data_loss or []
        self.conversion_warnings = conversion_warnings or []
    
    def get_category(self) -> str:
        return "format_conversion"


class JSONExportError(FormatConversionError):
    """Exception for JSON format export failures."""
    
    def __init__(
        self,
        json_issue: str,
        invalid_fields: Optional[List[str]] = None,
        serialization_errors: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            source_format="character_data",
            target_format="JSON",
            conversion_issue=json_issue,
            **kwargs
        )
        self.json_issue = json_issue
        self.invalid_fields = invalid_fields or []
        self.serialization_errors = serialization_errors or []
    
    def get_category(self) -> str:
        return "json_export"


class XMLExportError(FormatConversionError):
    """Exception for XML format export failures."""
    
    def __init__(
        self,
        xml_issue: str,
        schema_violations: Optional[List[str]] = None,
        namespace_issues: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            source_format="character_data",
            target_format="XML",
            conversion_issue=xml_issue,
            **kwargs
        )
        self.xml_issue = xml_issue
        self.schema_violations = schema_violations or []
        self.namespace_issues = namespace_issues or []
    
    def get_category(self) -> str:
        return "xml_export"


class PDFExportError(FormatConversionError):
    """Exception for PDF format export failures."""
    
    def __init__(
        self,
        pdf_issue: str,
        rendering_errors: Optional[List[str]] = None,
        layout_issues: Optional[List[str]] = None,
        font_issues: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            source_format="character_data",
            target_format="PDF",
            conversion_issue=pdf_issue,
            **kwargs
        )
        self.pdf_issue = pdf_issue
        self.rendering_errors = rendering_errors or []
        self.layout_issues = layout_issues or []
        self.font_issues = font_issues or []
    
    def get_category(self) -> str:
        return "pdf_export"


class CSVExportError(FormatConversionError):
    """Exception for CSV format export failures."""
    
    def __init__(
        self,
        csv_issue: str,
        delimiter_issues: Optional[List[str]] = None,
        encoding_issues: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            source_format="character_data",
            target_format="CSV",
            conversion_issue=csv_issue,
            **kwargs
        )
        self.csv_issue = csv_issue
        self.delimiter_issues = delimiter_issues or []
        self.encoding_issues = encoding_issues or []
    
    def get_category(self) -> str:
        return "csv_export"


# ============ TEMPLATE RENDERING EXCEPTIONS ============

class TemplateRenderingError(ExportError):
    """Exception for template rendering failures."""
    
    def __init__(
        self,
        template_name: str,
        rendering_issue: str,
        template_variables: Optional[Dict[str, Any]] = None,
        missing_variables: Optional[List[str]] = None,
        template_syntax_errors: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Template rendering failed for '{template_name}': {rendering_issue}"
        super().__init__(
            message,
            export_stage="template_rendering",
            **kwargs
        )
        self.template_name = template_name
        self.rendering_issue = rendering_issue
        self.template_variables = template_variables or {}
        self.missing_variables = missing_variables or []
        self.template_syntax_errors = template_syntax_errors or []
    
    def get_category(self) -> str:
        return "template_rendering"


class TemplateMissingError(TemplateRenderingError):
    """Exception for missing template files."""
    
    def __init__(
        self,
        template_name: str,
        search_paths: Optional[List[str]] = None,
        available_templates: Optional[List[str]] = None,
        **kwargs
    ):
        rendering_issue = f"Template not found"
        if search_paths:
            rendering_issue += f" in paths: {', '.join(search_paths)}"
        
        super().__init__(
            template_name=template_name,
            rendering_issue=rendering_issue,
            **kwargs
        )
        self.search_paths = search_paths or []
        self.available_templates = available_templates or []
    
    def get_category(self) -> str:
        return "template_missing"
    
    def should_fail_fast(self) -> bool:
        """Missing templates should fail fast."""
        return True


class TemplateVariableError(TemplateRenderingError):
    """Exception for template variable processing errors."""
    
    def __init__(
        self,
        template_name: str,
        variable_name: str,
        variable_issue: str,
        expected_type: Optional[str] = None,
        actual_value: Optional[Any] = None,
        **kwargs
    ):
        rendering_issue = f"Variable '{variable_name}' error: {variable_issue}"
        if expected_type:
            rendering_issue += f" (expected: {expected_type})"
        
        super().__init__(
            template_name=template_name,
            rendering_issue=rendering_issue,
            **kwargs
        )
        self.variable_name = variable_name
        self.variable_issue = variable_issue
        self.expected_type = expected_type
        self.actual_value = actual_value
    
    def get_category(self) -> str:
        return "template_variable"


class TemplateSyntaxError(TemplateRenderingError):
    """Exception for template syntax errors."""
    
    def __init__(
        self,
        template_name: str,
        syntax_error: str,
        line_number: Optional[int] = None,
        column_number: Optional[int] = None,
        template_excerpt: Optional[str] = None,
        **kwargs
    ):
        rendering_issue = f"Syntax error: {syntax_error}"
        if line_number:
            rendering_issue += f" at line {line_number}"
            if column_number:
                rendering_issue += f", column {column_number}"
        
        super().__init__(
            template_name=template_name,
            rendering_issue=rendering_issue,
            **kwargs
        )
        self.syntax_error = syntax_error
        self.line_number = line_number
        self.column_number = column_number
        self.template_excerpt = template_excerpt
    
    def get_category(self) -> str:
        return "template_syntax"


# ============ CHARACTER SHEET EXPORT EXCEPTIONS ============

class CharacterSheetExportError(ExportError):
    """Exception for character sheet export failures."""
    
    def __init__(
        self,
        sheet_type: str,
        export_issue: str,
        character_name: Optional[str] = None,
        missing_data: Optional[List[str]] = None,
        layout_issues: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Character sheet export failed for {sheet_type}: {export_issue}"
        if character_name:
            message += f" (character: {character_name})"
        
        super().__init__(
            message,
            export_stage="character_sheet_generation",
            **kwargs
        )
        self.sheet_type = sheet_type
        self.export_issue = export_issue
        self.character_name = character_name
        self.missing_data = missing_data or []
        self.layout_issues = layout_issues or []
    
    def get_category(self) -> str:
        return "character_sheet_export"


class CharacterDataIncompleteError(CharacterSheetExportError):
    """Exception for incomplete character data during export."""
    
    def __init__(
        self,
        missing_required_fields: List[str],
        optional_missing_fields: Optional[List[str]] = None,
        data_validation_errors: Optional[List[str]] = None,
        **kwargs
    ):
        export_issue = f"Required character data missing: {', '.join(missing_required_fields)}"
        
        super().__init__(
            sheet_type="any",
            export_issue=export_issue,
            missing_data=missing_required_fields,
            **kwargs
        )
        self.missing_required_fields = missing_required_fields
        self.optional_missing_fields = optional_missing_fields or []
        self.data_validation_errors = data_validation_errors or []
    
    def get_category(self) -> str:
        return "character_data_incomplete"
    
    def should_fail_fast(self) -> bool:
        """Missing required data should fail fast."""
        return True


class CharacterSheetLayoutError(CharacterSheetExportError):
    """Exception for character sheet layout and formatting issues."""
    
    def __init__(
        self,
        layout_issue: str,
        affected_sections: Optional[List[str]] = None,
        layout_constraints: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            sheet_type="formatted",
            export_issue=f"Layout error: {layout_issue}",
            layout_issues=[layout_issue],
            **kwargs
        )
        self.layout_issue = layout_issue
        self.affected_sections = affected_sections or []
        self.layout_constraints = layout_constraints or {}
    
    def get_category(self) -> str:
        return "character_sheet_layout"


# ============ CUSTOM CONTENT EXPORT EXCEPTIONS ============

class CustomContentExportError(ExportError):
    """Exception for custom content export failures."""
    
    def __init__(
        self,
        content_name: str,
        content_type: ContentType,
        export_issue: str,
        content_limitations: Optional[List[str]] = None,
        platform_compatibility: Optional[Dict[str, bool]] = None,
        **kwargs
    ):
        message = f"Custom {content_type.value} '{content_name}' export failed: {export_issue}"
        super().__init__(
            message,
            content_type=content_type,
            **kwargs
        )
        self.content_name = content_name
        self.export_issue = export_issue
        self.content_limitations = content_limitations or []
        self.platform_compatibility = platform_compatibility or {}
    
    def get_category(self) -> str:
        return "custom_content_export"


class UnsupportedContentError(CustomContentExportError):
    """Exception for content not supported by target export format."""
    
    def __init__(
        self,
        content_name: str,
        content_type: ContentType,
        export_format: ExportFormat,
        unsupported_features: List[str],
        alternative_formats: Optional[List[ExportFormat]] = None,
        **kwargs
    ):
        export_issue = f"Content not supported by {export_format.value} format"
        if unsupported_features:
            export_issue += f" (unsupported: {', '.join(unsupported_features)})"
        
        super().__init__(
            content_name=content_name,
            content_type=content_type,
            export_issue=export_issue,
            export_format=export_format,
            **kwargs
        )
        self.unsupported_features = unsupported_features
        self.alternative_formats = alternative_formats or []
    
    def get_category(self) -> str:
        return "unsupported_content"


class ContentComplexityExportError(CustomContentExportError):
    """Exception for content too complex for target export format."""
    
    def __init__(
        self,
        content_name: str,
        content_type: ContentType,
        complexity_issue: str,
        complexity_score: Optional[float] = None,
        max_complexity: Optional[float] = None,
        simplification_suggestions: Optional[List[str]] = None,
        **kwargs
    ):
        export_issue = f"Content complexity exceeds format limits: {complexity_issue}"
        if complexity_score and max_complexity:
            export_issue += f" (score: {complexity_score:.2f}, max: {max_complexity:.2f})"
        
        super().__init__(
            content_name=content_name,
            content_type=content_type,
            export_issue=export_issue,
            **kwargs
        )
        self.complexity_issue = complexity_issue
        self.complexity_score = complexity_score
        self.max_complexity = max_complexity
        self.simplification_suggestions = simplification_suggestions or []
    
    def get_category(self) -> str:
        return "content_complexity_export"


# ============ EXPORT QUALITY AND VALIDATION EXCEPTIONS ============

class ExportQualityError(ExportError):
    """Exception for export quality validation failures."""
    
    def __init__(
        self,
        quality_issue: str,
        quality_score: Optional[float] = None,
        minimum_quality: Optional[float] = None,
        quality_metrics: Optional[Dict[str, float]] = None,
        **kwargs
    ):
        message = f"Export quality validation failed: {quality_issue}"
        if quality_score and minimum_quality:
            message += f" (score: {quality_score:.2f}, minimum: {minimum_quality:.2f})"
        
        super().__init__(
            message,
            export_stage="quality_validation",
            **kwargs
        )
        self.quality_issue = quality_issue
        self.quality_score = quality_score
        self.minimum_quality = minimum_quality
        self.quality_metrics = quality_metrics or {}
    
    def get_category(self) -> str:
        return "export_quality"


class ExportValidationError(ValidationError):
    """Exception for export data validation failures."""
    
    def __init__(
        self,
        validation_issue: str,
        export_format: Optional[ExportFormat] = None,
        validation_stage: Optional[str] = None,
        failed_validations: Optional[List[str]] = None,
        **kwargs
    ):
        message = f"Export validation failed: {validation_issue}"
        if export_format:
            message += f" for {export_format.value} format"
        
        super().__init__(
            message,
            field_name="export_data",
            **kwargs
        )
        self.validation_issue = validation_issue
        self.export_format = export_format
        self.validation_stage = validation_stage
        self.failed_validations = failed_validations or []
    
    def get_category(self) -> str:
        return "export_validation"


# ============ EXPORT PERFORMANCE AND RESOURCE EXCEPTIONS ============

class ExportTimeoutError(ExportError):
    """Exception for export operation timeouts."""
    
    def __init__(
        self,
        timeout_duration: float,
        export_stage: Optional[str] = None,
        partial_export: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Export operation timed out after {timeout_duration} seconds"
        if export_stage:
            message += f" during {export_stage}"
        
        super().__init__(
            message,
            export_stage=export_stage,
            **kwargs
        )
        self.timeout_duration = timeout_duration
        self.partial_export = partial_export or {}
    
    def get_category(self) -> str:
        return "export_timeout"
    
    def is_retryable(self) -> bool:
        """Timeout errors are retryable."""
        return True


class ExportResourceError(ExportError):
    """Exception for export resource limitations."""
    
    def __init__(
        self,
        resource_type: str,
        resource_limit: Union[int, float],
        current_usage: Union[int, float],
        resource_description: Optional[str] = None,
        **kwargs
    ):
        message = f"Export resource limit exceeded: {resource_type}"
        if resource_description:
            message += f" - {resource_description}"
        message += f" (limit: {resource_limit}, current: {current_usage})"
        
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.resource_limit = resource_limit
        self.current_usage = current_usage
        self.resource_description = resource_description
    
    def get_category(self) -> str:
        return "export_resource"
    
    def should_fail_fast(self) -> bool:
        """Resource errors might need immediate attention."""
        critical_resources = ["memory", "disk_space", "file_handle"]
        return self.resource_type in critical_resources


class ExportFileSizeError(ExportResourceError):
    """Exception for export file size limitations."""
    
    def __init__(
        self,
        file_size: int,
        max_file_size: int,
        export_format: Optional[ExportFormat] = None,
        compression_attempted: bool = False,
        **kwargs
    ):
        resource_description = f"Generated file size too large"
        if export_format:
            resource_description += f" for {export_format.value} format"
        if compression_attempted:
            resource_description += " (even with compression)"
        
        super().__init__(
            resource_type="file_size",
            resource_limit=max_file_size,
            current_usage=file_size,
            resource_description=resource_description,
            **kwargs
        )
        self.file_size = file_size
        self.max_file_size = max_file_size
        self.export_format = export_format
        self.compression_attempted = compression_attempted
    
    def get_category(self) -> str:
        return "export_file_size"


# ============ UTILITY FUNCTIONS FOR EXPORT EXCEPTION HANDLING ============

def categorize_export_error(error: Exception) -> str:
    """
    Categorize an export error for handling and routing.
    
    Args:
        error: The exception to categorize
        
    Returns:
        Error category string
    """
    if isinstance(error, VTTExportError):
        return "vtt_export"
    elif isinstance(error, FormatConversionError):
        return "format_conversion"
    elif isinstance(error, TemplateRenderingError):
        return "template_rendering"
    elif isinstance(error, CharacterSheetExportError):
        return "character_sheet_export"
    elif isinstance(error, CustomContentExportError):
        return "custom_content_export"
    elif isinstance(error, ExportQualityError):
        return "export_quality"
    elif isinstance(error, ExportTimeoutError):
        return "export_timeout"
    elif isinstance(error, ExportResourceError):
        return "export_resource"
    elif isinstance(error, ExportError):
        return "general_export"
    else:
        return "unknown"


def is_retryable_export_error(error: Exception) -> bool:
    """
    Determine if an export error is retryable.
    
    Args:
        error: The exception to check
        
    Returns:
        True if the error might succeed on retry
    """
    # Timeout and resource errors are generally retryable
    if isinstance(error, (ExportTimeoutError, ExportResourceError)):
        return True
    
    # Template variable errors might be retryable if data changes
    if isinstance(error, TemplateVariableError):
        return True
    
    # Format conversion errors might be retryable
    if isinstance(error, FormatConversionError):
        return True
    
    # VTT export errors might be retryable
    if isinstance(error, VTTExportError):
        return True
    
    # Missing templates and syntax errors are not retryable
    if isinstance(error, (TemplateMissingError, TemplateSyntaxError)):
        return False
    
    # Unsupported content errors are not retryable
    if isinstance(error, UnsupportedContentError):
        return False
    
    # Most export errors are retryable
    if isinstance(error, ExportError):
        return error.is_retryable()
    
    return False


def get_export_recovery_suggestions(error: ExportError) -> List[str]:
    """
    Generate recovery suggestions for export errors.
    
    Args:
        error: The export error to analyze
        
    Returns:
        List of recovery suggestions
    """
    suggestions = list(error.recovery_suggestions)
    
    if isinstance(error, TemplateMissingError):
        suggestions.extend([
            "Check template file paths and permissions",
            "Install required template packages",
            "Use alternative template if available"
        ])
        if error.available_templates:
            suggestions.append(f"Try available templates: {', '.join(error.available_templates[:3])}")
    
    elif isinstance(error, TemplateVariableError):
        suggestions.extend([
            f"Provide required variable: {error.variable_name}",
            "Check character data completeness",
            "Verify variable type requirements"
        ])
        if error.expected_type:
            suggestions.append(f"Ensure {error.variable_name} is of type {error.expected_type}")
    
    elif isinstance(error, CharacterDataIncompleteError):
        suggestions.extend([
            "Complete required character information",
            "Run character validation before export",
            "Use export with warnings if appropriate"
        ])
        for field in error.missing_required_fields[:3]:
            suggestions.append(f"Provide {field}")
    
    elif isinstance(error, UnsupportedContentError):
        suggestions.extend([
            "Simplify content for target format",
            "Remove unsupported features",
            "Use format-specific alternatives"
        ])
        if error.alternative_formats:
            alt_formats = [fmt.value for fmt in error.alternative_formats[:3]]
            suggestions.append(f"Try alternative formats: {', '.join(alt_formats)}")
    
    elif isinstance(error, ExportFileSizeError):
        suggestions.extend([
            "Enable compression if available",
            "Reduce image quality or size",
            "Split into multiple files",
            "Use more compact export format"
        ])
    
    elif isinstance(error, ExportTimeoutError):
        suggestions.extend([
            "Try export in smaller batches",
            "Increase timeout duration",
            "Simplify character complexity",
            "Use faster export format"
        ])
    
    elif isinstance(error, VTTExportError):
        suggestions.extend([
            f"Check {error.vtt_platform.value if error.vtt_platform else 'VTT'} compatibility",
            "Update VTT platform version",
            "Use platform-specific export options"
        ])
        if error.compatibility_issues:
            suggestions.extend([f"Address: {issue}" for issue in error.compatibility_issues[:2]])
    
    return suggestions


def get_export_format_alternatives(failed_format: ExportFormat) -> List[ExportFormat]:
    """
    Get alternative export formats when one fails.
    
    Args:
        failed_format: The format that failed
        
    Returns:
        List of alternative formats to try
    """
    alternatives = {
        ExportFormat.JSON: [ExportFormat.XML, ExportFormat.YAML],
        ExportFormat.XML: [ExportFormat.JSON, ExportFormat.YAML],
        ExportFormat.PDF: [ExportFormat.HTML, ExportFormat.DOCX],
        ExportFormat.HTML: [ExportFormat.PDF, ExportFormat.MARKDOWN],
        ExportFormat.CSV: [ExportFormat.JSON, ExportFormat.TSV],
        ExportFormat.YAML: [ExportFormat.JSON, ExportFormat.XML],
        ExportFormat.MARKDOWN: [ExportFormat.HTML, ExportFormat.TXT]
    }
    
    return alternatives.get(failed_format, [])


def create_export_error_context(
    operation: str,
    export_format: Optional[ExportFormat] = None,
    character_name: Optional[str] = None,
    export_stage: Optional[str] = None,
    progress: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create standardized error context for export operations.
    
    Args:
        operation: Name of the export operation
        export_format: Target export format
        character_name: Name of character being exported
        export_stage: Current stage of export
        progress: Export progress (0.0-1.0)
        
    Returns:
        Context dictionary for error reporting
    """
    context = {
        "operation": operation,
        "timestamp": None,  # Will be set by infrastructure layer
        "stage": export_stage,
        "progress": progress
    }
    
    if export_format:
        context["export_format"] = export_format.value
    
    if character_name:
        context["character_name"] = character_name
    
    return context


def validate_export_requirements(
    character_data: Dict[str, Any],
    export_format: ExportFormat,
    vtt_platform: Optional[VTTPlatform] = None
) -> List[str]:
    """
    Validate export requirements and return any issues found.
    
    Args:
        character_data: Character data to export
        export_format: Target export format
        vtt_platform: Target VTT platform if applicable
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    # Check required fields based on export format
    required_fields = {
        ExportFormat.JSON: ["name", "class", "level"],
        ExportFormat.PDF: ["name", "class", "level", "ability_scores"],
        ExportFormat.XML: ["name", "class", "level", "ability_scores"],
        ExportFormat.HTML: ["name", "class", "level", "ability_scores"]
    }
    
    format_requirements = required_fields.get(export_format, ["name"])
    for field in format_requirements:
        if field not in character_data or not character_data[field]:
            issues.append(f"Missing required field for {export_format.value}: {field}")
    
    # Check VTT-specific requirements
    if vtt_platform:
        vtt_requirements = {
            VTTPlatform.DND_BEYOND: ["name", "class", "species", "level", "ability_scores"],
            VTTPlatform.ROLL20: ["name", "class", "level", "ability_scores", "skills"],
            VTTPlatform.FANTASY_GROUNDS: ["name", "class", "species", "level", "ability_scores"],
            VTTPlatform.FOUNDRY_VTT: ["name", "class", "level", "ability_scores"]
        }
        
        platform_requirements = vtt_requirements.get(vtt_platform, [])
        for field in platform_requirements:
            if field not in character_data or not character_data[field]:
                issues.append(f"Missing required field for {vtt_platform.value}: {field}")
    
    return issues


# ============ MODULE METADATA ============

__version__ = '2.0.0'
__description__ = 'Export and VTT format exceptions for D&D Creative Content Framework'
__author__ = 'D&D Character Creator Backend6'

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/exceptions",
    "dependencies": ["core/enums", "core/exceptions/base"],
    "dependents": ["domain/services", "application/use_cases", "infrastructure"],
    "infrastructure_independent": True,
    "focuses_on": "D&D export and format conversion business rules"
}

# Exception statistics
EXCEPTION_STATISTICS = {
    "base_export_exceptions": 2,
    "vtt_platform_exceptions": 5,
    "format_conversion_exceptions": 5,
    "template_rendering_exceptions": 4,
    "character_sheet_exceptions": 3,
    "custom_content_exceptions": 3,
    "quality_validation_exceptions": 2,
    "performance_exceptions": 3,
    "total_exception_types": 27,
    "utility_functions": 7
}