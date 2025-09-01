"""Character model module."""
from typing import Dict, List, Optional, Any
from sqlalchemy import String, Integer, JSON, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import UUID as PyUUID, uuid4

from character_service.db.base import Base


class Character(Base):
    """Character model."""
    __tablename__ = "characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('characters.id'), nullable=True)
    theme = Column(String, nullable=False, server_default='traditional')
    species = Column(String, nullable=False)
    background = Column(String, nullable=False)
    level = Column(Integer, nullable=False, default=1)
    
    # Stored as JSON
    character_classes = Column(JSON, nullable=False)  # Dict[class_name, level]
    ability_scores = Column(JSON, nullable=False)  # Dict[ability_name, score]
    equipment = Column(JSON, nullable=False, default=list)  # List[Dict]
    spells_known = Column(JSON, nullable=False, default=list)  # List[str]
    spells_prepared = Column(JSON, nullable=False, default=list)  # List[str]
    features = Column(JSON, nullable=False, default=list)  # List[Dict]
    racial_bonuses = Column(JSON, nullable=True)  # Dict[ability_name, bonus]
    warnings = Column(JSON, nullable=True)  # List[str]

    # Computed attributes
    hit_points = Column(Integer, nullable=False)
    armor_class = Column(Integer, nullable=False)
    proficiency_bonus = Column(Integer, nullable=False)
    spell_save_dc = Column(Integer, nullable=True)
    spellcasting_ability = Column(String, nullable=True)

    # Theme relationships
    parent = relationship("Character", remote_side=[id], back_populates="children")
    children = relationship("Character", back_populates="parent")

    def get_ability_modifier(self, ability: str) -> int:
        """Calculate ability score modifier."""
        score = self.ability_scores.get(ability, 10)
        return (score - 10) // 2

    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "campaign_id": self.campaign_id,
            "parent_id": self.parent_id,
            "theme": self.theme,
            "species": self.species,
            "background": self.background,
            "level": self.level,
            "character_classes": self.character_classes,
            "ability_scores": self.ability_scores,
            "equipment": self.equipment,
            "spells_known": self.spells_known,
            "spells_prepared": self.spells_prepared,
            "features": self.features,
            "racial_bonuses": self.racial_bonuses,
            "hit_points": self.hit_points,
            "armor_class": self.armor_class,
            "proficiency_bonus": self.proficiency_bonus,
            "spell_save_dc": self.spell_save_dc,
            "spellcasting_ability": self.spellcasting_ability,
            "warnings": self.warnings
        }
