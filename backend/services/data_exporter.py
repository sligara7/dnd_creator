"""
Data Exporter Service

A general-purpose service for exporting game entity data to various formats.
Supports characters, NPCs, creatures, and other game elements.
"""

from typing import Dict, Any, Optional, Literal
import json
import os
from pathlib import Path
import datetime


class DataExporter:
    """
    Service for exporting game entity data to different formats.
    
    This service provides functionality to export any type of game entity
    (characters, NPCs, creatures) to various formats for storage, sharing,
    and interoperability between systems.
    """

    def __init__(self, export_directory: str = None):
        """
        Initialize the data exporter.
        
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
    
    def export_to_json(self, 
                      data: Dict[str, Any], 
                      entity_type: str = "entity",
                      filepath: str = None) -> Dict[str, Any]:
        """
        Export entity data to JSON format.
        
        Args:
            data: Entity data dictionary to export
            entity_type: Type of entity (character, npc, creature, etc.)
            filepath: Optional specific filepath for the JSON output
            
        Returns:
            Dict[str, Any]: Result with status and file path
        """
        # Validate data
        if not data or not isinstance(data, dict):
            return {
                "success": False,
                "error": "Invalid data provided",
                "filepath": None
            }
        
        # Create sanitized version for export
        export_data = self._prepare_data_for_export(data, entity_type)
        
        # Generate filename if not provided
        if not filepath:
            entity_name = export_data.get("name", f"unnamed_{entity_type}")
            # Sanitize name for filename
            entity_name = "".join(c for c in entity_name if c.isalnum() or c in [' ', '_']).strip()
            entity_name = entity_name.replace(' ', '_').lower()
            
            # Add timestamp to ensure uniqueness
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{entity_type}_{entity_name}_{timestamp}.json"
            filepath = self.export_directory / filename
        
        try:
            # Write the data to JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "message": f"{entity_type.capitalize()} exported successfully to {filepath}",
                "filepath": str(filepath)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to export {entity_type}: {str(e)}",
                "filepath": None
            }
    
    def export_data(self,
                   data: Dict[str, Any],
                   entity_type: str = "entity",
                   format: Literal["json", "pdf", "markdown"] = "json",
                   filepath: str = None) -> Dict[str, Any]:
        """
        Export data in the specified format.
        
        Args:
            data: Entity data dictionary to export
            entity_type: Type of entity (character, npc, creature, etc.)
            format: Format to export data in
            filepath: Optional specific filepath for the output
            
        Returns:
            Dict[str, Any]: Result with status and file path
        """
        if format.lower() == "json":
            return self.export_to_json(data, entity_type, filepath)
        elif format.lower() == "pdf":
            # PDF export would be implemented here
            return self._export_to_pdf(data, entity_type, filepath)
        elif format.lower() == "markdown":
            # Markdown export would be implemented here
            return self._export_to_markdown(data, entity_type, filepath)
        else:
            return {
                "success": False,
                "error": f"Unsupported export format: {format}",
                "filepath": None
            }
    
    def _prepare_data_for_export(self, data: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """
        Prepare data for export, cleaning up any transient or internal fields.
        
        Args:
            data: Raw entity data
            entity_type: Type of entity being exported
            
        Returns:
            Dict[str, Any]: Cleaned data ready for export
        """
        # Create a deep copy to avoid modifying the original
        export_data = json.loads(json.dumps(data))
        
        # Add export metadata
        export_data["_export_metadata"] = {
            "export_date": datetime.datetime.now().isoformat(),
            "exporter_version": "1.0.0",
            "format": f"dnd_{entity_type}_json",
            "entity_type": entity_type
        }
        
        # Remove any internal fields that shouldn't be exported
        fields_to_remove = [
            "validation_issues",  # Remove validation issues
            "_temp",              # Remove any temporary data
            "_cache",             # Remove any cached data
            "_internal",          # Remove any internal data
            "llm_advisor"         # Remove LLM advisor instances
        ]
        
        for field in fields_to_remove:
            if field in export_data:
                del export_data[field]
        
        return export_data

    def _export_to_pdf(self, data: Dict[str, Any], entity_type: str, filepath: str = None) -> Dict[str, Any]:
        """
        Export data to PDF format (placeholder for future implementation).
        
        Args:
            data: Entity data dictionary
            entity_type: Type of entity being exported
            filepath: Optional specific filepath for the PDF output
            
        Returns:
            Dict[str, Any]: Result with status and file path
        """
        # This would be implemented with a PDF library like reportlab or weasyprint
        return {
            "success": False,
            "error": "PDF export not yet implemented",
            "filepath": None
        }
        
    def _export_to_markdown(self, data: Dict[str, Any], entity_type: str, filepath: str = None) -> Dict[str, Any]:
        """
        Export data to Markdown format.
        
        Args:
            data: Entity data dictionary
            entity_type: Type of entity being exported
            filepath: Optional specific filepath for the markdown output
            
        Returns:
            Dict[str, Any]: Result with status and file path
        """
        # Generate filename if not provided
        if not filepath:
            entity_name = data.get("name", f"unnamed_{entity_type}")
            # Sanitize name for filename
            entity_name = "".join(c for c in entity_name if c.isalnum() or c in [' ', '_']).strip()
            entity_name = entity_name.replace(' ', '_').lower()
            
            # Add timestamp to ensure uniqueness
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{entity_type}_{entity_name}_{timestamp}.md"
            filepath = self.export_directory / filename
            
        try:
            # Create basic markdown content
            md_content = f"# {data.get('name', 'Unnamed ' + entity_type.capitalize())}\n\n"
            
            # Add description if available
            if "description" in data:
                md_content += f"{data['description']}\n\n"
            
            # Add basic attributes
            md_content += "## Basic Information\n\n"
            
            # Handle different entity types
            if entity_type == "character":
                md_content += self._character_to_markdown(data)
            elif entity_type == "npc":
                md_content += self._npc_to_markdown(data)
            elif entity_type == "creature":
                md_content += self._creature_to_markdown(data)
            else:
                # Generic approach for other entity types
                for key, value in data.items():
                    if key.startswith("_") or isinstance(value, dict):
                        continue
                    if isinstance(value, list):
                        md_content += f"**{key.replace('_', ' ').title()}**: {', '.join(str(v) for v in value)}\n\n"
                    else:
                        md_content += f"**{key.replace('_', ' ').title()}**: {value}\n\n"
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
                
            return {
                "success": True,
                "message": f"{entity_type.capitalize()} exported successfully to {filepath}",
                "filepath": str(filepath)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to export {entity_type} to markdown: {str(e)}",
                "filepath": None
            }
            
    def _character_to_markdown(self, data: Dict[str, Any]) -> str:
        """
        Convert character data to markdown format.
        
        Args:
            data: Character data dictionary
            
        Returns:
            str: Markdown representation of character
        """
        md_content = ""
        
        # Basic character info
        char_class = data.get("class", "Unknown")
        if isinstance(char_class, dict):
            char_class = char_class.get("name", "Unknown")
            
        level = data.get("level", 1)
        species = data.get("species", "Unknown")
        if isinstance(species, dict):
            species = species.get("name", "Unknown")
            
        md_content += f"**Class**: {char_class}\n"
        md_content += f"**Level**: {level}\n"
        md_content += f"**Species**: {species}\n"
        
        # Ability scores
        if "ability_scores" in data:
            md_content += "\n## Ability Scores\n\n"
            for ability, score in data["ability_scores"].items():
                modifier = (score - 10) // 2
                md_content += f"**{ability.capitalize()}**: {score} ({modifier:+d})\n"
                
        # Other sections would be added based on character data structure
                
        return md_content
        
    def _npc_to_markdown(self, data: Dict[str, Any]) -> str:
        """
        Convert NPC data to markdown format.
        
        Args:
            data: NPC data dictionary
            
        Returns:
            str: Markdown representation of NPC
        """
        md_content = ""
        
        # Basic NPC info
        md_content += f"**Role**: {data.get('role', 'Unknown')}\n"
        md_content += f"**CR**: {data.get('challenge_rating', 'Unknown')}\n"
        
        # Personality
        if "personality" in data:
            md_content += "\n## Personality\n\n"
            for trait, desc in data["personality"].items():
                md_content += f"**{trait.capitalize()}**: {desc}\n"
        
        # Motivations
        if "motivations" in data:
            md_content += "\n## Motivations\n\n"
            if isinstance(data["motivations"], list):
                for motivation in data["motivations"]:
                    md_content += f"- {motivation}\n"
            else:
                md_content += data["motivations"] + "\n"
                
        return md_content
        
    def _creature_to_markdown(self, data: Dict[str, Any]) -> str:
        """
        Convert creature data to markdown format.
        
        Args:
            data: Creature data dictionary
            
        Returns:
            str: Markdown representation of creature
        """
        md_content = ""
        
        # Basic creature info
        md_content += f"**Type**: {data.get('type', 'Unknown')}\n"
        md_content += f"**CR**: {data.get('challenge_rating', 'Unknown')}\n"
        md_content += f"**Size**: {data.get('size', 'Medium')}\n"
        
        # Stats
        if "hit_points" in data:
            md_content += f"**HP**: {data['hit_points']}\n"
        if "armor_class" in data:
            md_content += f"**AC**: {data['armor_class']}\n"
            
        # Abilities
        if "abilities" in data:
            md_content += "\n## Abilities\n\n"
            for ability in data["abilities"]:
                md_content += f"**{ability['name']}**: {ability['description']}\n\n"
                
        return md_content


# For backward compatibility - this will be deprecated
class CharacterExporter(DataExporter):
    """
    Legacy class for character exports. Replaced by DataExporter.
    Will be removed in a future release.
    """
    
    def __init__(self, export_directory: str = None):
        """Initialize with character-specific defaults"""
        super().__init__(export_directory)
        
    def export_character_to_json(self, character_data: Dict[str, Any], filepath: str = None) -> Dict[str, Any]:
        """Legacy method that calls the new export_to_json with character entity type"""
        return self.export_to_json(character_data, "character", filepath)