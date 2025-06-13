import os
import json
from typing import Optional, List
from datetime import datetime
from pathlib import Path

from ...core.entities.character import Character
from ...core.utils.character_utils import CharacterSerializer

class CharacterStorage:
    """Infrastructure service for character file operations."""
    
    def __init__(self, base_path: str = "characters"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def save_character(self, character: Character, 
                      filename: Optional[str] = None) -> str:
        """Save character to file."""
        if not filename:
            # Generate filename from character name and timestamp
            safe_name = "".join(c for c in character.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{timestamp}.json"
        
        filepath = self.base_path / filename
        CharacterSerializer.to_file(character, str(filepath))
        
        return str(filepath)
    
    def load_character(self, filename: str) -> Character:
        """Load character from file."""
        filepath = self.base_path / filename
        return CharacterSerializer.from_file(str(filepath))
    
    def list_saved_characters(self) -> List[Dict[str, Any]]:
        """List all saved character files."""
        characters = []
        
        for filepath in self.base_path.glob("*.json"):
            try:
                # Load minimal character data for listing
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                characters.append({
                    "filename": filepath.name,
                    "name": data.get("name", "Unknown"),
                    "level": data.get("total_level", 1),
                    "species": data.get("species", "Unknown"),
                    "primary_class": data.get("primary_class", "Unknown"),
                    "created_at": data.get("created_at", "Unknown"),
                    "file_size": filepath.stat().st_size
                })
            except Exception as e:
                # Skip corrupted files
                continue
        
        return sorted(characters, key=lambda x: x["created_at"], reverse=True)
    
    def delete_character(self, filename: str) -> bool:
        """Delete a character file."""
        try:
            filepath = self.base_path / filename
            filepath.unlink()
            return True
        except Exception:
            return False
    
    def backup_characters(self, backup_path: str) -> List[str]:
        """Create backup of all character files."""
        backup_dir = Path(backup_path)
        backup_dir.mkdir(exist_ok=True)
        
        backed_up_files = []
        for filepath in self.base_path.glob("*.json"):
            backup_file = backup_dir / filepath.name
            backup_file.write_text(filepath.read_text())
            backed_up_files.append(str(backup_file))
        
        return backed_up_files