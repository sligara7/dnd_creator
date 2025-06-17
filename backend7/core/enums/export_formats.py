"""
Essential Export Format Enums

Streamlined export format classifications following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from enum import Enum, auto

# ============ EXPORT FORMAT TYPES ============

class ExportFormat(Enum):
    """Character export format options."""
    JSON = "json"
    PDF = "pdf"
    HTML = "html"
    TEXT = "txt"
    CSV = "csv"
    XML = "xml"

class OutputTarget(Enum):
    """Export output target destinations."""
    FILE = auto()           # Save to file
    SCREEN = auto()         # Display on screen
    PRINT = auto()          # Print-ready format
    WEB = auto()            # Web sharing
    API = auto()            # API response

class CompressionLevel(Enum):
    """Export compression options."""
    NONE = auto()           # No compression
    LOW = auto()            # Minimal compression
    STANDARD = auto()       # Default compression
    HIGH = auto()           # Maximum compression

# ============ CONTENT DETAIL LEVELS ============

class DetailLevel(Enum):
    """Export content detail levels."""
    MINIMAL = auto()        # Core stats only
    STANDARD = auto()       # Standard character sheet
    DETAILED = auto()       # Full character details
    COMPLETE = auto()       # Everything including notes

class IncludeOptions(Enum):
    """Optional content inclusion flags."""
    BACKSTORY = auto()
    EQUIPMENT = auto()
    SPELLS = auto()
    NOTES = auto()
    ARTWORK = auto()
    STATISTICS = auto()

# ============ FORMAT-SPECIFIC OPTIONS ============

class PDFLayout(Enum):
    """PDF-specific layout options."""
    CHARACTER_SHEET = auto()    # Standard D&D sheet
    COMPACT = auto()            # Condensed format
    DETAILED = auto()           # Extended sheet
    CUSTOM = auto()             # User-defined layout

class HTMLTheme(Enum):
    """HTML export theme options."""
    CLASSIC = auto()            # Traditional styling
    MODERN = auto()             # Contemporary design
    MINIMAL = auto()            # Clean, simple
    DARK = auto()               # Dark theme

class TextFormat(Enum):
    """Text export formatting options."""
    PLAIN = auto()              # Simple text
    FORMATTED = auto()          # Structured text
    MARKDOWN = auto()           # Markdown format
    TABULATED = auto()          # Table format

# ============ EXPORT CONFIGURATIONS ============

EXPORT_PRESETS = {
    "quick_reference": {
        "format": ExportFormat.TEXT,
        "target": OutputTarget.SCREEN,
        "detail": DetailLevel.MINIMAL,
        "includes": [IncludeOptions.EQUIPMENT],
        "compression": CompressionLevel.NONE
    },
    "character_sheet": {
        "format": ExportFormat.PDF,
        "target": OutputTarget.PRINT,
        "detail": DetailLevel.STANDARD,
        "includes": [IncludeOptions.EQUIPMENT, IncludeOptions.SPELLS],
        "compression": CompressionLevel.STANDARD,
        "pdf_layout": PDFLayout.CHARACTER_SHEET
    },
    "web_sharing": {
        "format": ExportFormat.HTML,
        "target": OutputTarget.WEB,
        "detail": DetailLevel.DETAILED,
        "includes": [IncludeOptions.BACKSTORY, IncludeOptions.EQUIPMENT, IncludeOptions.SPELLS],
        "compression": CompressionLevel.LOW,
        "html_theme": HTMLTheme.MODERN
    },
    "data_backup": {
        "format": ExportFormat.JSON,
        "target": OutputTarget.FILE,
        "detail": DetailLevel.COMPLETE,
        "includes": list(IncludeOptions),
        "compression": CompressionLevel.HIGH
    }
}

FORMAT_EXTENSIONS = {
    ExportFormat.JSON: ".json",
    ExportFormat.PDF: ".pdf",
    ExportFormat.HTML: ".html",
    ExportFormat.TEXT: ".txt",
    ExportFormat.CSV: ".csv",
    ExportFormat.XML: ".xml"
}

# ============ UTILITY FUNCTIONS ============

def get_export_preset(preset_name: str) -> dict:
    """Get export configuration preset."""
    return EXPORT_PRESETS.get(preset_name, EXPORT_PRESETS["character_sheet"])

def get_file_extension(format_type: ExportFormat) -> str:
    """Get file extension for export format."""
    return FORMAT_EXTENSIONS.get(format_type, ".txt")

def supports_compression(format_type: ExportFormat) -> bool:
    """Check if format supports compression."""
    return format_type in [ExportFormat.JSON, ExportFormat.XML, ExportFormat.HTML]

def is_binary_format(format_type: ExportFormat) -> bool:
    """Check if export format produces binary output."""
    return format_type == ExportFormat.PDF

def requires_styling(format_type: ExportFormat) -> bool:
    """Check if format supports visual styling."""
    return format_type in [ExportFormat.PDF, ExportFormat.HTML]

def is_structured_data(format_type: ExportFormat) -> bool:
    """Check if format uses structured data."""
    return format_type in [ExportFormat.JSON, ExportFormat.XML, ExportFormat.CSV]

def get_mime_type(format_type: ExportFormat) -> str:
    """Get MIME type for export format."""
    mime_types = {
        ExportFormat.JSON: "application/json",
        ExportFormat.PDF: "application/pdf",
        ExportFormat.HTML: "text/html",
        ExportFormat.TEXT: "text/plain",
        ExportFormat.CSV: "text/csv",
        ExportFormat.XML: "application/xml"
    }
    return mime_types.get(format_type, "text/plain")

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core format types
    'ExportFormat',
    'OutputTarget',
    'CompressionLevel',
    
    # Content options
    'DetailLevel',
    'IncludeOptions',
    
    # Format-specific options
    'PDFLayout',
    'HTMLTheme',
    'TextFormat',
    
    # Configuration
    'EXPORT_PRESETS',
    'FORMAT_EXTENSIONS',
    
    # Utility functions
    'get_export_preset',
    'get_file_extension',
    'supports_compression',
    'is_binary_format',
    'requires_styling',
    'is_structured_data',
    'get_mime_type',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential export format enumerations'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/enums",
    "focus": "export_format_classification_only",
    "line_target": 150,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_essential_enums"
}