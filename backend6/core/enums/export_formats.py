"""
Export Format Enumerations.

Defines export formats and VTT compatibility for character sheet generation
and output formatting.
"""

from enum import Enum
from typing import List


class ExportFormat(Enum):
    """Character sheet export formats."""
    JSON = "json"                       # Standard JSON format
    DND_BEYOND = "dnd_beyond"          # D&D Beyond compatible JSON
    ROLL20 = "roll20"                  # Roll20 character sheet JSON
    FOUNDRY_VTT = "foundry_vtt"        # FoundryVTT actor format
    PDF = "pdf"                        # Printable PDF character sheet
    MARKDOWN = "markdown"              # Markdown format for documentation
    
    @property
    def is_vtt_format(self) -> bool:
        """Check if this is a VTT-specific format."""
        return self in {self.DND_BEYOND, self.ROLL20, self.FOUNDRY_VTT}
    
    @property
    def supports_custom_content(self) -> bool:
        """Check if format supports custom content."""
        return self in {self.JSON, self.FOUNDRY_VTT, self.PDF, self.MARKDOWN}
    
    @property
    def file_extension(self) -> str:
        """Get file extension for this format."""
        extensions = {
            self.JSON: "json",
            self.DND_BEYOND: "json",
            self.ROLL20: "json", 
            self.FOUNDRY_VTT: "json",
            self.PDF: "pdf",
            self.MARKDOWN: "md"
        }
        return extensions[self]


class CharacterSheetType(Enum):
    """Types of character sheets to generate."""
    SINGLE_LEVEL = "single_level"       # Single level character sheet
    PROGRESSION_SUMMARY = "progression_summary"  # Multi-level summary
    COMPLETE_PROGRESSION = "complete_progression"  # All levels 1-20
    CUSTOM_CONTENT_ONLY = "custom_content_only"   # Just custom content
    MILESTONE_HIGHLIGHTS = "milestone_highlights" # Key progression points
    
    @property
    def includes_all_levels(self) -> bool:
        """Check if this type includes all character levels."""
        return self in {self.COMPLETE_PROGRESSION, self.PROGRESSION_SUMMARY}


class OutputLayout(Enum):
    """Layout options for character sheet output."""
    COMPACT = "compact"                 # Minimal space usage
    STANDARD = "standard"               # Standard D&D layout
    DETAILED = "detailed"               # Full details with descriptions
    PRINTER_FRIENDLY = "printer_friendly"  # Optimized for printing
    
    @property
    def includes_descriptions(self) -> bool:
        """Check if layout includes feature descriptions."""
        return self in {self.DETAILED, self.PRINTER_FRIENDLY}


class ContentInclusionLevel(Enum):
    """Levels of content inclusion in exports."""
    CORE_ONLY = "core_only"             # Only core D&D content
    WITH_CUSTOM = "with_custom"         # Include custom content
    CUSTOM_ONLY = "custom_only"         # Only custom content
    EVERYTHING = "everything"           # All content including variants
    
    @property
    def includes_custom_content(self) -> bool:
        """Check if inclusion level includes custom content."""
        return self in {self.WITH_CUSTOM, self.CUSTOM_ONLY, self.EVERYTHING}


def get_supported_formats_for_vtt(vtt_name: str) -> List[ExportFormat]:
    """Get supported export formats for a specific VTT."""
    vtt_formats = {
        "dnd_beyond": [ExportFormat.DND_BEYOND, ExportFormat.JSON],
        "roll20": [ExportFormat.ROLL20, ExportFormat.JSON],
        "foundry": [ExportFormat.FOUNDRY_VTT, ExportFormat.JSON],
        "fantasy_grounds": [ExportFormat.JSON],  # Generic JSON for FG
        "generic": [ExportFormat.JSON, ExportFormat.PDF, ExportFormat.MARKDOWN]
    }
    return vtt_formats.get(vtt_name.lower(), [ExportFormat.JSON])