"""Service for handling plane transitions and effects."""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.orm import Session

from ..core.logging import get_logger
from ..models.planes import (
    Plane,
    PlaneTransition,
    EntityPlaneManifestation
)
from .campaign_factory import CampaignFactory
from ..core.messaging import MessageHandlers

logger = get_logger(__name__)


class PlaneService:
    """Service for managing planes and transitions."""

    def __init__(
        self,
        db: Session,
        campaign_factory: CampaignFactory,
        message_handlers: MessageHandlers,
    ):
        self.db = db
        self.campaign_factory = campaign_factory
        self.messages = message_handlers

    async def get_plane(self, plane_id: UUID) -> Optional[Plane]:
        """Get a plane by ID."""
        return self.db.query(Plane).get(plane_id)

    async def list_campaign_planes(
        self,
        campaign_id: UUID
    ) -> List[Plane]:
        """List all planes available in a campaign."""
        campaign = await self.campaign_factory.get_campaign(campaign_id)
        return campaign.planes if campaign else []

    async def create_plane_transition(
        self,
        campaign_id: UUID,
        source_plane_id: UUID,
        target_plane_id: UUID,
        transition_type: str,
        affected_entities: List[Dict[str, Any]],
        trigger_conditions: Dict[str, Any],
        effects: Dict[str, Any],
        chapter_id: Optional[UUID] = None,
        duration: Optional[Dict[str, Any]] = None,
    ) -> PlaneTransition:
        """Create a new plane transition."""
        try:
            # Validate planes exist
            source_plane = await self.get_plane(source_plane_id)
            target_plane = await self.get_plane(target_plane_id)
            if not source_plane or not target_plane:
                raise ValueError("Invalid plane IDs")

            # Create transition
            transition = PlaneTransition(
                campaign_id=campaign_id,
                chapter_id=chapter_id,
                source_plane_id=source_plane_id,
                target_plane_id=target_plane_id,
                transition_type=transition_type,
                trigger_conditions=trigger_conditions,
                effects=effects,
                duration=duration,
                affected_entities=affected_entities
            )
            self.db.add(transition)
            await self.db.commit()

            # Process affected entities
            await self._process_transition_entities(
                transition,
                source_plane,
                target_plane
            )

            return transition

        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create plane transition", error=str(e))
            raise ValueError(f"Failed to create plane transition: {e}")

    async def _process_transition_entities(
        self,
        transition: PlaneTransition,
        source_plane: Plane,
        target_plane: Plane
    ) -> None:
        """Process entities affected by a plane transition."""
        try:
            for entity in transition.affected_entities:
                # Request re-planing from character service
                if entity["type"] in ["character", "npc", "monster"]:
                    await self.messages.character.replane_character(
                        entity["id"],
                        source_plane.dict(),
                        target_plane.dict(),
                        transition.effects
                    )

                # Create manifestation record
                manifestation = EntityPlaneManifestation(
                    entity_id=entity["id"],
                    entity_type=entity["type"],
                    plane_id=transition.target_plane_id,
                    manifestation_type=entity.get("manifestation", "default"),
                    attributes=entity.get("attributes", {}),
                    abilities=entity.get("abilities", {}),
                    restrictions=entity.get("restrictions", {}),
                    special_effects=entity.get("special_effects", {})
                )
                self.db.add(manifestation)

            await self.db.commit()

        except Exception as e:
            logger.error("Failed to process transition entities", error=str(e))
            raise

    async def get_entity_manifestation(
        self,
        entity_id: str,
        plane_id: UUID
    ) -> Optional[EntityPlaneManifestation]:
        """Get how an entity manifests in a specific plane."""
        return self.db.query(EntityPlaneManifestation).filter(
            EntityPlaneManifestation.entity_id == entity_id,
            EntityPlaneManifestation.plane_id == plane_id
        ).first()

    async def update_entity_manifestation(
        self,
        entity_id: str,
        plane_id: UUID,
        updates: Dict[str, Any]
    ) -> EntityPlaneManifestation:
        """Update an entity's manifestation in a plane."""
        try:
            manifestation = await self.get_entity_manifestation(
                entity_id,
                plane_id
            )
            if not manifestation:
                raise ValueError("Manifestation not found")

            # Update fields
            for field, value in updates.items():
                if hasattr(manifestation, field):
                    setattr(manifestation, field, value)

            manifestation.updated_at = datetime.utcnow()
            await self.db.commit()

            return manifestation

        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to update manifestation", error=str(e))
            raise ValueError(f"Failed to update manifestation: {e}")

    async def get_plane_map(
        self,
        location_id: UUID,
        plane_id: UUID,
        style_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get a plane-specific map for a location."""
        try:
            plane = await self.get_plane(plane_id)
            if not plane:
                raise ValueError("Plane not found")

            # Check for existing map
            existing_map = self.db.query(LocationMap).filter(
                LocationMap.location_id == location_id,
                LocationMap.metadata["plane_id"].astext == str(plane_id),
                LocationMap.is_current.is_(True)
            ).first()

            if existing_map:
                return await self.messages.image.get_map_by_id(
                    existing_map.image_id
                )

            # Generate new plane map
            location = self.db.query(MapLocation).get(location_id)
            if not location:
                raise ValueError("Location not found")

            # Generate map prompt
            prompt = await self._generate_plane_map_prompt(
                location,
                plane,
                style_params
            )

            # Request map generation
            map_data = await self.messages.image.generate_plane_map(
                prompt,
                plane.dict(),
                style_params or {},
                {
                    "location_id": str(location_id),
                    "plane_id": str(plane_id),
                    "map_type": "plane_specific"
                }
            )

            # Create map record
            new_map = LocationMap(
                location_id=location_id,
                image_id=map_data["image_id"],
                map_type="plane_specific",
                prompt=prompt,
                style_params=style_params,
                metadata={
                    "plane_id": str(plane_id),
                    "plane_type": plane.type
                }
            )
            self.db.add(new_map)
            await self.db.commit()

            return map_data

        except Exception as e:
            logger.error("Failed to get plane map", error=str(e))
            raise ValueError(f"Failed to get plane map: {e}")

    async def _generate_plane_map_prompt(
        self,
        location: MapLocation,
        plane: Plane,
        style_params: Optional[Dict[str, Any]]
    ) -> str:
        """Generate a prompt for plane-specific map creation."""
        try:
            context = {
                "location": location.dict(),
                "plane": plane.dict(),
                "style": style_params or {}
            }

            # Use AI to generate detailed prompt
            prompt_data = await self.ai_client.generate_plane_map_prompt(context)
            return prompt_data["prompt"]

        except Exception as e:
            logger.error("Failed to generate plane map prompt", error=str(e))
            raise ValueError(f"Failed to generate plane map prompt: {e}")

    async def list_active_transitions(
        self,
        campaign_id: UUID,
        entity_id: Optional[str] = None
    ) -> List[PlaneTransition]:
        """List active plane transitions."""
        query = self.db.query(PlaneTransition).filter(
            PlaneTransition.campaign_id == campaign_id
        )

        if entity_id:
            query = query.filter(
                PlaneTransition.affected_entities.contains([{"id": entity_id}])
            )

        return query.order_by(PlaneTransition.created_at.desc()).all()

    async def complete_transition(
        self,
        transition_id: UUID
    ) -> None:
        """Mark a plane transition as completed."""
        try:
            transition = self.db.query(PlaneTransition).get(transition_id)
            if not transition:
                raise ValueError("Transition not found")

            # Remove temporary transition record for temporary transitions
            if transition.transition_type == "temporary":
                self.db.delete(transition)
            
            await self.db.commit()

            # Publish completion event
            await self.message_hub.publish(
                "campaign.plane_transition_completed",
                {
                    "transition_id": str(transition_id),
                    "affected_entities": transition.affected_entities,
                    "type": transition.transition_type
                }
            )

        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to complete transition", error=str(e))
            raise ValueError(f"Failed to complete transition: {e}")
