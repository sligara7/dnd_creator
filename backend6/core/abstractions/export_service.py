"""
Export Service Interface - Infrastructure Boundary.

Defines the contract for exporting character sheets to various formats
and Virtual Tabletop platforms. This abstraction keeps the domain layer
independent of specific export implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ..enums.export_formats import ExportFormat, CharacterSheetType, OutputLayout


class IExportService(ABC):
    """Interface for character sheet export functionality."""
    
    @abstractmethod
    async def export_character_sheet(self,
                                   character_data: Dict[str, Any],
                                   level: int,
                                   export_format: ExportFormat,
                                   layout: OutputLayout = OutputLayout.STANDARD) -> Dict[str, Any]:
        """Export single level character sheet."""
        pass
    
    @abstractmethod
    async def export_complete_progression(self,
                                        progression_data: Dict[int, Dict[str, Any]],
                                        export_format: ExportFormat) -> Dict[str, Any]:
        """Export complete character progression."""
        pass
    
    @abstractmethod
    async def export_to_vtt(self,
                          character_data: Dict[str, Any],
                          vtt_name: str,
                          level: int = None) -> Dict[str, Any]:
        """Export character for specific VTT platform."""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[ExportFormat]:
        """Get list of supported export formats."""
        pass
    
    @abstractmethod
    def get_supported_vtts(self) -> List[str]:
        """Get list of supported VTT platforms."""
        pass
    
    @abstractmethod
    async def save_to_file(self,
                         export_data: Dict[str, Any],
                         file_path: str,
                         export_format: ExportFormat) -> bool:
        """Save exported data to file."""
        pass