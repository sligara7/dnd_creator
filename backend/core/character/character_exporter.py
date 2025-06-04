# import abstract_character_class as needed
# character_exporter.py
# Purpose: Exports character data to various formats, including PDF character sheets and digital formats.

# Suggested Methods:

# export_to_pdf(self, character_data, template='standard') - Export to PDF format
# export_to_json(self, character_data) - Export to JSON format for digital tools
# export_to_markdown(self, character_data) - Export to readable Markdown format
# export_to_dndbeyond_format(self, character_data) - Export to D&D Beyond compatible format
# generate_character_portrait(self, character_data, style=None) - Generate character portrait
# generate_character_summary(self, character_data, detail_level='standard') - Generate text summary
# create_printable_spell_cards(self, character_data) - Create printable spell cards
# create_printable_equipment_cards(self, character_data) - Create equipment cards
# llm_character_advisor.py
# Purpose: Provides AI-powered assistance for character creation and development using LLM integration.

# Each of these modules will work together under the coordination of the main Character class to provide a comprehensive, AI-enhanced character creation and management system for D&D 2024.

"""
Character Exporter Module

Exports character data to various formats, primarily focusing on JSON output.
Provides minimal functionality needed for character data export and sharing.
"""

from typing import Dict, Any, Optional
import json
import os
from pathlib import Path
import datetime

try:
    from backend.core.character.abstract_character import AbstractCharacterClass
except ImportError:
    # Fallback for development
    AbstractCharacterClass = object


class CharacterExporter(AbstractCharacterClass):
    """
    Handles exporting character data to different formats.
    
    This minimal implementation focuses on JSON export functionality to ensure
    characters can be properly serialized, stored, and shared between systems.
    """

    def __init__(self, export_directory: str = None):
        """
        Initialize the character exporter.
        
        Args:
            export_directory: Optional directory for exported files
        """
        # Set default export directory if none provided
        if export_directory:
            self.export_directory = Path(export_directory)
        else:
            self.export_directory = Path("exports")
            
        # Create the directory if it doesn't exist
        os.makedirs(self.export_directory, exist_ok=True)
    
    def export_to_json(self, character_data: Dict[str, Any], 
                    filepath: str = None) -> Dict[str, Any]:
        """
        Export character data to JSON format.
        
        Args:
            character_data: Character data dictionary
            filepath: Optional specific filepath for the JSON output
            
        Returns:
            Dict[str, Any]: Result with status and file path
        """
        # Validate character data
        if not character_data or not isinstance(character_data, dict):
            return {
                "success": False,
                "error": "Invalid character data provided",
                "filepath": None
            }
        
        # Create sanitized version for export
        export_data = self._prepare_character_for_export(character_data)
        
        # Generate filename if not provided
        if not filepath:
            char_name = export_data.get("name", "unnamed_character")
            # Sanitize character name for filename
            char_name = "".join(c for c in char_name if c.isalnum() or c in [' ', '_']).strip()
            char_name = char_name.replace(' ', '_').lower()
            
            # Add timestamp to ensure uniqueness
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{char_name}_{timestamp}.json"
            filepath = self.export_directory / filename
        
        try:
            # Write the character data to JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "message": f"Character exported successfully to {filepath}",
                "filepath": str(filepath)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to export character: {str(e)}",
                "filepath": None
            }
    
    def _prepare_character_for_export(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare character data for export, cleaning up any transient or internal fields.
        
        Args:
            character_data: Raw character data
            
        Returns:
            Dict[str, Any]: Cleaned character data ready for export
        """
        # Create a deep copy to avoid modifying the original
        export_data = json.loads(json.dumps(character_data))
        
        # Add export metadata
        export_data["_export_metadata"] = {
            "export_date": datetime.datetime.now().isoformat(),
            "exporter_version": "1.0.0",
            "format": "dnd_character_json"
        }
        
        # Remove any internal fields that shouldn't be exported
        fields_to_remove = [
            "validation_issues",  # Remove validation issues
            "_temp",              # Remove any temporary data
            "_cache"              # Remove any cached data
        ]
        
        for field in fields_to_remove:
            if field in export_data:
                del export_data[field]
        
        return export_data