"""D&D data service.

This service provides access to core D&D data and rules, including
spells, weapons, armor, feats, and other game content.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models.base import Status
from ..models.character import (
    Character,
    Race,
    Class,
    Background,
    Equipment,
    Weapon,
    Armor,
)
from ..models.spellcasting import (
    Spell,
    SpellcastingClass,
)
from ..models.enums import (
    WeaponType,
    ArmorType,
    SpellSchool,
    ProficiencyLevel,
)
from ..core.logging import get_logger

logger = get_logger(__name__)

class DndDataService:
    """Service providing access to core D&D data and rules."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.db = session
    
    async def get_races(
        self,
        filter_query: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get available character races.
        
        Args:
            filter_query: Optional text filter
            source: Optional source filter
            
        Returns:
            List of matching races
        """
        try:
            # Build base query
            stmt = select(Race)
            
            if filter_query:
                stmt = stmt.where(Race.name.ilike(f"%{filter_query}%"))
                
            if source:
                stmt = stmt.where(Race.source == source)
            
            result = await self.db.execute(stmt)
            races = result.scalars().all()
            
            return [race.dict() for race in races]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving races: {str(e)}")
            raise
    
    async def get_classes(
        self,
        filter_query: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get available character classes.
        
        Args:
            filter_query: Optional text filter
            source: Optional source filter
            
        Returns:
            List of matching classes
        """
        try:
            # Build base query
            stmt = select(Class)
            
            if filter_query:
                stmt = stmt.where(Class.name.ilike(f"%{filter_query}%"))
                
            if source:
                stmt = stmt.where(Class.source == source)
            
            result = await self.db.execute(stmt)
            classes = result.scalars().all()
            
            # Get spellcasting info
            spellcasting = {c.class_name: c.dict() async for c in self.get_spellcasting_classes()}
            
            # Add spellcasting info to class data
            class_data = []
            for cls in classes:
                data = cls.dict()
                if cls.name in spellcasting:
                    data["spellcasting"] = spellcasting[cls.name]
                class_data.append(data)
            
            return class_data
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving classes: {str(e)}")
            raise
    
    async def get_backgrounds(
        self,
        filter_query: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get available character backgrounds.
        
        Args:
            filter_query: Optional text filter
            source: Optional source filter
            
        Returns:
            List of matching backgrounds
        """
        try:
            # Build base query
            stmt = select(Background)
            
            if filter_query:
                stmt = stmt.where(Background.name.ilike(f"%{filter_query}%"))
                
            if source:
                stmt = stmt.where(Background.source == source)
            
            result = await self.db.execute(stmt)
            backgrounds = result.scalars().all()
            
            return [bg.dict() for bg in backgrounds]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving backgrounds: {str(e)}")
            raise
    
    async def get_equipment(
        self,
        filter_query: Optional[str] = None,
        type: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get available equipment items.
        
        Args:
            filter_query: Optional text filter
            type: Optional equipment type filter
            source: Optional source filter
            
        Returns:
            List of matching equipment
        """
        try:
            # Build base query
            stmt = select(Equipment)
            
            if filter_query:
                stmt = stmt.where(Equipment.name.ilike(f"%{filter_query}%"))
                
            if type:
                stmt = stmt.where(Equipment.type == type)
                
            if source:
                stmt = stmt.where(Equipment.source == source)
            
            result = await self.db.execute(stmt)
            equipment = result.scalars().all()
            
            return [item.dict() for item in equipment]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving equipment: {str(e)}")
            raise
    
    async def get_weapons(
        self,
        filter_query: Optional[str] = None,
        type: Optional[WeaponType] = None,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get available weapons.
        
        Args:
            filter_query: Optional text filter
            type: Optional weapon type filter
            source: Optional source filter
            
        Returns:
            List of matching weapons
        """
        try:
            # Build base query
            stmt = select(Weapon)
            
            if filter_query:
                stmt = stmt.where(Weapon.name.ilike(f"%{filter_query}%"))
                
            if type:
                stmt = stmt.where(Weapon.weapon_type == type)
                
            if source:
                stmt = stmt.where(Weapon.source == source)
            
            result = await self.db.execute(stmt)
            weapons = result.scalars().all()
            
            return [weapon.dict() for weapon in weapons]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving weapons: {str(e)}")
            raise
    
    async def get_armor(
        self,
        filter_query: Optional[str] = None,
        type: Optional[ArmorType] = None,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get available armor.
        
        Args:
            filter_query: Optional text filter
            type: Optional armor type filter
            source: Optional source filter
            
        Returns:
            List of matching armor
        """
        try:
            # Build base query
            stmt = select(Armor)
            
            if filter_query:
                stmt = stmt.where(Armor.name.ilike(f"%{filter_query}%"))
                
            if type:
                stmt = stmt.where(Armor.armor_type == type)
                
            if source:
                stmt = stmt.where(Armor.source == source)
            
            result = await self.db.execute(stmt)
            armors = result.scalars().all()
            
            return [armor.dict() for armor in armors]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving armor: {str(e)}")
            raise
    
    async def get_spells(
        self,
        filter_query: Optional[str] = None,
        level: Optional[int] = None,
        school: Optional[SpellSchool] = None,
        class_name: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get available spells.
        
        Args:
            filter_query: Optional text filter
            level: Optional spell level filter
            school: Optional spell school filter
            class_name: Optional class name filter
            source: Optional source filter
            
        Returns:
            List of matching spells
        """
        try:
            # Build base query
            stmt = select(Spell)
            
            if filter_query:
                stmt = stmt.where(Spell.name.ilike(f"%{filter_query}%"))
                
            if level is not None:
                stmt = stmt.where(Spell.level == level)
                
            if school:
                stmt = stmt.where(Spell.school == school)
                
            if class_name:
                stmt = stmt.where(Spell.classes.contains([class_name]))
                
            if source:
                stmt = stmt.where(Spell.source == source)
            
            result = await self.db.execute(stmt)
            spells = result.scalars().all()
            
            return [spell.dict() for spell in spells]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving spells: {str(e)}")
            raise
            
    async def get_spellcasting_classes(
        self,
        filter_query: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get spellcasting rules by class.
        
        Args:
            filter_query: Optional text filter
            source: Optional source filter
            
        Returns:
            List of spellcasting class configurations
        """
        try:
            # Build base query
            stmt = select(SpellcastingClass)
            
            if filter_query:
                stmt = stmt.where(SpellcastingClass.class_name.ilike(f"%{filter_query}%"))
                
            if source:
                stmt = stmt.where(SpellcastingClass.source == source)
            
            result = await self.db.execute(stmt)
            classes = result.scalars().all()
            
            return [cls.dict() for cls in classes]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving spellcasting rules: {str(e)}")
            raise
            
    async def get_appropriate_content(
        self,
        character: Character,
        content_type: str,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get content appropriate for a character.
        
        Args:
            character: Character to get content for
            content_type: Type of content to retrieve
            max_results: Maximum results to return
            
        Returns:
            List of appropriate content
        """
        try:
            content: List[Dict[str, Any]] = []
            
            if content_type == "spells":
                # Get appropriate spells based on class
                spells = []
                for class_name in character.character_classes:
                    class_spells = await self.get_spells(
                        class_name=class_name,
                        level=character.get_max_spell_level(class_name),
                    )
                    spells.extend(class_spells)
                content = spells[:max_results]
                
            elif content_type == "weapons":
                # Get weapons character is proficient with
                content = await self.get_weapons(
                    type=character.weapon_proficiencies,
                )
                content = content[:max_results]
                
            elif content_type == "armor":
                # Get armor character is proficient with
                content = await self.get_armor(
                    type=character.armor_proficiencies,
                )
                content = content[:max_results]
                
            elif content_type == "equipment":
                # Get general equipment
                content = await self.get_equipment()
                content = content[:max_results]
            
            return content
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving appropriate content: {str(e)}")
            raise
            
    async def validate_content(
        self,
        content_id: UUID,
        content_type: str,
    ) -> Dict[str, Any]:
        """Validate game content against rules.
        
        Args:
            content_id: Content to validate
            content_type: Type of content
            
        Returns:
            Validation results
        """
        try:
            # Get content
            model = self._get_model_for_content_type(content_type)
            if not model:
                raise ValueError(f"Unknown content type: {content_type}")
                
            stmt = select(model).where(model.id == content_id)
            result = await self.db.execute(stmt)
            content = result.scalar_one_or_none()
            
            if not content:
                raise ValueError(f"Content not found: {content_id}")
            
            # Validate based on type
            if content_type == "spell":
                return await self._validate_spell(content)
            elif content_type == "weapon":
                return await self._validate_weapon(content)
            elif content_type == "armor":
                return await self._validate_armor(content)
            else:
                return {"valid": True}  # Basic content needs no validation
            
        except SQLAlchemyError as e:
            logger.error(f"Database error validating content: {str(e)}")
            raise
            
    def _get_model_for_content_type(self, content_type: str) -> Optional[Any]:
        """Get the model class for a content type."""
        models = {
            "race": Race,
            "class": Class,
            "background": Background,
            "equipment": Equipment,
            "weapon": Weapon,
            "armor": Armor,
            "spell": Spell,
        }
        return models.get(content_type)
        
    async def _validate_spell(self, spell: Spell) -> Dict[str, Any]:
        """Validate spell mechanics."""
        issues = []
        warnings = []
        
        # Basic validation
        if spell.level < 0 or spell.level > 9:
            issues.append("Invalid spell level")
            
        if not spell.components:
            warnings.append("Spell has no components")
            
        if not spell.description:
            issues.append("Spell missing description")
            
        if spell.type == "cantrip" and spell.level != 0:
            issues.append("Cantrip must be level 0")
            
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }
        
    async def _validate_weapon(self, weapon: Weapon) -> Dict[str, Any]:
        """Validate weapon mechanics."""
        issues = []
        warnings = []
        
        # Basic validation
        if not weapon.damage_dice:
            issues.append("Weapon missing damage dice")
            
        if not weapon.damage_type:
            issues.append("Weapon missing damage type")
            
        if weapon.finesse and weapon.heavy:
            warnings.append("Unusual to have both finesse and heavy properties")
            
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }
        
    async def _validate_armor(self, armor: Armor) -> Dict[str, Any]:
        """Validate armor mechanics."""
        issues = []
        warnings = []
        
        # Basic validation
        if armor.base_ac < 10:
            issues.append("Armor AC too low")
            
        if armor.base_ac > 18:
            warnings.append("Unusually high armor AC")
            
        if armor.strength_requirement and armor.strength_requirement > 15:
            warnings.append("Very high strength requirement")
            
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }
