"""
Migration script to populate the unified item catalog with official D&D 5e content.
This script converts all traditional D&D data from dnd_data.py into UUID-based entries
in the UnifiedItem table.
"""

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.services.dnd_data import (
    DND_SPELL_DATABASE, DND_WEAPON_DATABASE, DND_ARMOR_DATABASE, 
    DND_TOOLS_DATABASE, DND_ADVENTURING_GEAR_DATABASE
)
from src.models.database_models import UnifiedItem, CharacterDB

logger = logging.getLogger(__name__)

class UnifiedCatalogMigration:
    """Handles migration of traditional D&D content to unified UUID catalog."""
    
    def __init__(self, db: CharacterDB):
        self.db = db
        self.spell_school_mapping = {
            "abjuration": "Abjuration",
            "conjuration": "Conjuration", 
            "divination": "Divination",
            "enchantment": "Enchantment",
            "evocation": "Evocation",
            "illusion": "Illusion",
            "necromancy": "Necromancy",
            "transmutation": "Transmutation"
        }

    def migrate_all_official_content(self, session) -> Dict[str, int]:
        """Migrate all official D&D content to unified catalog."""
        results = {
            "spells": 0,
            "weapons": 0,
            "armor": 0,
            "equipment": 0,
            "tools": 0,
            "errors": 0
        }
        try:
            # Clear existing official content to avoid duplicates
            self._clear_existing_official_content(session)
            # Migrate each content type
            results["spells"] = self._migrate_spells(session)
            results["weapons"] = self._migrate_weapons(session)
            results["armor"] = self._migrate_armor(session)
            results["equipment"] = self._migrate_equipment(session)
            results["tools"] = self._migrate_tools(session)
            session.commit()
            logger.info(f"Migration completed successfully: {results}")
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            results["errors"] += 1
        return results
    
    def _clear_existing_official_content(self, session: Session):
        """Remove existing official content to prevent duplicates."""
        deleted = session.query(UnifiedItem).filter(
            UnifiedItem.source_type == "official"
        ).delete()
        logger.info(f"Cleared {deleted} existing official items")
    
    def _migrate_spells(self, session: Session) -> int:
        """Migrate all spells from DND_SPELL_DATABASE."""
        count = 0
        
        for level_key, schools in DND_SPELL_DATABASE.items():
            spell_level = 0 if level_key == "cantrips" else int(level_key.split("_")[1])
            
            for school, spell_names in schools.items():
                for spell_name in spell_names:
                    try:
                        # Get detailed spell data
                        spell_data = self._get_spell_details(spell_name, spell_level, school)
                        
                        # Create unified item
                        item = UnifiedItem(
                            id=uuid.uuid4(),
                            name=spell_name,
                            item_type="spell",
                            item_subtype=f"level_{spell_level}",
                            source_type="official",
                            content_data=spell_data,
                            short_description=spell_data.get("description", "")[:500],
                            spell_level=spell_level,
                            spell_school=self.spell_school_mapping.get(school, school.title()),
                            class_restrictions=spell_data.get("classes", []),
                            source_book="Player's Handbook 2024",
                            is_public=True,
                            created_at=datetime.now(timezone.utc)
                        )
                        
                        session.add(item)
                        count += 1
                        
                    except Exception as e:
                        logger.error(f"Failed to migrate spell {spell_name}: {e}")
        
        return count
    
    def _migrate_weapons(self, session: Session) -> int:
        """Migrate all weapons from DND_WEAPON_DATABASE."""
        count = 0
        
        for category, weapons in DND_WEAPON_DATABASE.items():
            for weapon_name, weapon_data in weapons.items():
                try:
                    # Determine weapon subtype
                    subtype = self._get_weapon_subtype(category, weapon_data)
                    
                    # Create unified item
                    item = UnifiedItem(
                        id=uuid.uuid4(),
                        name=weapon_name,
                        item_type="weapon",
                        item_subtype=subtype,
                        source_type="official",
                        content_data=weapon_data,
                        short_description=f"{category.replace('_', ' ').title()} weapon",
                        value_gp=self._parse_cost_to_gp(weapon_data.get("cost", "0 gp")),
                        weight_lbs=self._parse_weight_to_lbs(weapon_data.get("weight", 1)),
                        source_book="Player's Handbook 2024",
                        is_public=True,
                        created_at=datetime.now(timezone.utc)
                    )
                    
                    session.add(item)
                    count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to migrate weapon {weapon_name}: {e}")
        
        return count
    
    def _migrate_armor(self, session: Session) -> int:
        """Migrate all armor from DND_ARMOR_DATABASE."""
        count = 0
        
        for category, armor_items in DND_ARMOR_DATABASE.items():
            for armor_name, armor_data in armor_items.items():
                try:
                    # Create unified item
                    item = UnifiedItem(
                        id=uuid.uuid4(),
                        name=armor_name,
                        item_type="armor",
                        item_subtype=category,
                        source_type="official",
                        content_data=armor_data,
                        short_description=f"{category.replace('_', ' ').title()} armor",
                        value_gp=self._parse_cost_to_gp(armor_data.get("cost", "0 gp")),
                        weight_lbs=self._parse_weight_to_lbs(armor_data.get("weight", 1)),
                        source_book="Player's Handbook 2024",
                        is_public=True,
                        created_at=datetime.now(timezone.utc)
                    )
                    
                    session.add(item)
                    count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to migrate armor {armor_name}: {e}")
        
        return count
    
    def _migrate_equipment(self, session: Session) -> int:
        """Migrate all equipment from DND_ADVENTURING_GEAR_DATABASE."""
        count = 0
        for category, items in DND_ADVENTURING_GEAR_DATABASE.items():
            for item_name, item_data in items.items():
                try:
                    # Create unified item
                    item = UnifiedItem(
                        id=uuid.uuid4(),
                        name=item_name,
                        item_type="equipment",
                        item_subtype=category,
                        source_type="official",
                        content_data=item_data,
                        short_description=f"{category.replace('_', ' ').title()} equipment",
                        value_gp=self._parse_cost_to_gp(item_data.get("cost", "0 gp")),
                        weight_lbs=self._parse_weight_to_lbs(item_data.get("weight", 1)),
                        source_book="Player's Handbook 2024",
                        is_public=True,
                        created_at=datetime.now(timezone.utc)
                    )
                    session.add(item)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to migrate equipment {item_name}: {e}")
        return count
    
    def _migrate_tools(self, session: Session) -> int:
        """Migrate all tools from DND_TOOLS_DATABASE."""
        count = 0
        
        for category, tools in DND_TOOLS_DATABASE.items():
            for tool_name, tool_data in tools.items():
                try:
                    # Create unified item
                    item = UnifiedItem(
                        id=uuid.uuid4(),
                        name=tool_name,
                        item_type="tool",
                        item_subtype=category,
                        source_type="official",
                        content_data=tool_data,
                        short_description=f"{category.replace('_', ' ').title()} tool",
                        value_gp=self._parse_cost_to_gp(tool_data.get("cost", "0 gp")),
                        weight_lbs=self._parse_weight_to_lbs(tool_data.get("weight", 1)),
                        source_book="Player's Handbook 2024",
                        is_public=True,
                        created_at=datetime.now(timezone.utc)
                    )
                    
                    session.add(item)
                    count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to migrate tool {tool_name}: {e}")
        
        return count
    
    def _get_spell_details(self, spell_name: str, level: int, school: str) -> Dict[str, Any]:
        """Get detailed spell information."""
        # This would normally pull from a comprehensive spell database
        # For now, we'll create basic structure with what we know
        return {
            "name": spell_name,
            "level": level,
            "school": school.title(),
            "description": f"A {school} spell of level {level}",
            "casting_time": "1 action",
            "range": "60 feet" if level > 0 else "30 feet",
            "components": ["V", "S"],
            "duration": "Instantaneous",
            "classes": self._get_spell_classes(spell_name, level, school)
        }
    
    def _get_spell_classes(self, spell_name: str, level: int, school: str) -> List[str]:
        """Determine which classes can use this spell."""
        # Basic heuristics - in a real implementation, this would be data-driven
        classes = []
        
        if school in ["evocation", "conjuration", "transmutation"]:
            classes.extend(["wizard", "sorcerer"])
        if school in ["divination", "enchantment", "illusion"]:
            classes.extend(["wizard", "bard"])
        if school in ["necromancy"]:
            classes.extend(["wizard", "warlock"])
        if school in ["abjuration"]:
            classes.extend(["wizard", "cleric"])
        
        # Divine spells
        if any(word in spell_name.lower() for word in ["cure", "heal", "bless", "sacred", "divine"]):
            classes.extend(["cleric", "paladin"])
        
        # Nature spells
        if any(word in spell_name.lower() for word in ["animal", "plant", "nature", "druid"]):
            classes.append("druid")
        
        return list(set(classes))  # Remove duplicates
    
    def _get_weapon_subtype(self, category: str, weapon_data: Dict[str, Any]) -> str:
        """Determine weapon subtype based on category and properties."""
        if "simple" in category.lower():
            return "simple_weapon"
        elif "martial" in category.lower():
            return "martial_weapon"
        else:
            return category
    
    def _parse_cost_to_gp(self, cost_value) -> int:
        """Parse cost value (string, int, or float) to gold pieces."""
        if not cost_value or cost_value == "-":
            return 0
        
        # Handle numeric values directly (int or float)
        if isinstance(cost_value, (int, float)):
            return int(cost_value)
        
        # Handle string values
        if isinstance(cost_value, str):
            cost_str = cost_value.lower().strip()
            
            try:
                if "gp" in cost_str:
                    return int(cost_str.replace("gp", "").replace(",", "").strip())
                elif "sp" in cost_str:
                    return int(int(cost_str.replace("sp", "").strip()) / 10)
                elif "cp" in cost_str:
                    return int(int(cost_str.replace("cp", "").strip()) / 100)
                else:
                    # Try to parse as plain number
                    return int(cost_str.replace(",", ""))
            except:
                return 0
        
        # Fallback for any other type
        try:
            return int(cost_value)
        except:
            return 0

    def _parse_weight_to_lbs(self, weight_value) -> float:
        """Parse weight value (string, int, or float) to pounds."""
        if not weight_value:
            return 0.0
        
        # Handle numeric values directly (int or float)
        if isinstance(weight_value, (int, float)):
            return float(weight_value)
        
        # Handle string values
        if isinstance(weight_value, str):
            weight_str = weight_value.lower().strip()
            
            try:
                # Remove common weight suffixes
                weight_str = weight_str.replace(" lb", "").replace("s", "").replace("lbs", "")
                weight_str = weight_str.replace("pounds", "").replace("pound", "")
                weight_str = weight_str.strip()
                
                # Parse the numeric value
                return float(weight_str)
            except:
                return 0.0
        
        # Fallback for any other type
        try:
            return float(weight_value)
        except:
            return 0.0


def run_migration(db: CharacterDB, session) -> Dict[str, int]:
    """Run the unified catalog migration."""
    migration = UnifiedCatalogMigration(db)
    return migration.migrate_all_official_content(session)


if __name__ == "__main__":
    import sys
    import os
    # Add the backend directory to the path
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_path)

    from src.core.config import settings
    from src.models.database_models import init_database

    logging.basicConfig(level=logging.INFO)

    # Initialize database connection (must be done before using SessionLocal)
    database_url = settings.effective_database_url
    init_database(database_url)

    # Now import SessionLocal after init_database
    from src.models.database_models import SessionLocal

    db = CharacterDB()
    session = SessionLocal()
    try:
        migration = UnifiedCatalogMigration(db)
        results = migration.migrate_all_official_content(session)
        print(f"Migration results: {results}")
    finally:
        session.close()
