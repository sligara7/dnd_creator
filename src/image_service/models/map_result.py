"""
Map generation result models.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, DateTime, String, Integer, LargeBinary, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from shared.db import Base

class MapImage(Base):
    """Map image model."""
    __tablename__ = "map_images"

    id = Column(PGUUID, primary_key=True, default=uuid4)
    campaign_id = Column(PGUUID, nullable=True)
    encounter_id = Column(PGUUID, nullable=True)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    format = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)
    grid_metadata = Column(JSON, nullable=True)
    map_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def terrain_data(self) -> Optional[Dict[str, Any]]:
        """Get terrain data from metadata."""
        return self.map_metadata.get("terrain_data") if self.map_metadata else None

    @property
    def character_positions(self) -> List[Dict[str, Any]]:
        """Get character position data from metadata."""
        return self.map_metadata.get("character_positions", []) if self.map_metadata else []

    @property
    def spell_overlays(self) -> List[Dict[str, Any]]:
        """Get spell effect overlay data from metadata."""
        return self.map_metadata.get("spell_overlays", []) if self.map_metadata else []

    @property
    def points_of_interest(self) -> List[Dict[str, Any]]:
        """Get points of interest data from metadata."""
        return self.map_metadata.get("points_of_interest", []) if self.map_metadata else []

    @property
    def party_positions(self) -> List[Dict[str, Any]]:
        """Get party position data from metadata."""
        return self.map_metadata.get("party_positions", []) if self.map_metadata else []

    @property
    def region_data(self) -> Dict[str, Any]:
        """Get region data from metadata."""
        return self.map_metadata.get("region_data", {}) if self.map_metadata else {}

    @property
    def political_borders(self) -> List[Dict[str, Any]]:
        """Get political border data from metadata."""
        return self.map_metadata.get("political_borders", []) if self.map_metadata else []
