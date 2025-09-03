"""Service for managing session notes and feedback."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session

from ..core.ai import AIClient
from ..core.logging import get_logger
from ..models.session_notes import SessionNote, SessionCharacterRecord
from ..api.schemas.session_notes import (
    CreateSessionNoteRequest,
    UpdateSessionNoteRequest,
    ProcessNoteFeedbackRequest,
)
from .campaign_factory import CampaignFactory
from .version_control import VersionControlService

logger = get_logger(__name__)


class SessionService:
    """Service for managing session notes and feedback."""

    def __init__(
        self,
        db: Session,
        ai_client: AIClient,
        campaign_factory: CampaignFactory,
        version_control: VersionControlService,
        message_hub_client,
    ):
        """Initialize with required dependencies."""
        self.db = db
        self.ai_client = ai_client
        self.campaign_factory = campaign_factory
        self.version_control = version_control
        self.message_hub = message_hub_client

    async def create_note(self, request: CreateSessionNoteRequest) -> SessionNote:
        """Create a new session note."""
        try:
            # Validate campaign exists
            campaign = await self.campaign_factory.get_campaign(request.campaign_id)
            if not campaign:
                raise ValueError("Campaign not found")

            # Validate chapter if provided
            if request.chapter_id:
                chapter = await self.campaign_factory.get_chapter(request.chapter_id)
                if not chapter:
                    raise ValueError("Chapter not found")
                if chapter.campaign_id != request.campaign_id:
                    raise ValueError("Chapter does not belong to campaign")

            # Extract character references from narrative
            characters = await self._extract_character_references(
                request.narrative,
                request.character_interactions
            )

            # Create note
            note = SessionNote(
                campaign_id=request.campaign_id,
                chapter_id=request.chapter_id,
                session_number=request.session_number,
                title=request.title,
                narrative=request.narrative,
                dm_id=request.dm_id,
                players_present=request.players_present,
                objectives_completed=request.objectives_completed,
                significant_events=[e.dict() for e in request.significant_events],
                character_interactions=[i.dict() for i in request.character_interactions],
                plot_decisions=[d.dict() for d in request.plot_decisions],
                metadata=request.metadata
            )
            self.db.add(note)

            # Create character records
            for char_data in characters:
                record = SessionCharacterRecord(
                    session_note_id=note.id,
                    character_id=char_data["id"],
                    character_type=char_data["type"],
                    interactions=char_data["interactions"],
                    significant_actions=char_data["actions"],
                    traits_demonstrated=char_data["traits"]
                )
                self.db.add(record)

            self.db.commit()

            # Publish event
            await self.message_hub.publish(
                "campaign.session_note.created",
                {
                    "campaign_id": str(request.campaign_id),
                    "note_id": str(note.id),
                    "characters": [c["id"] for c in characters]
                }
            )

            return note

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create session note", error=str(e))
            raise ValueError(f"Failed to create session note: {e}")

    async def get_note(self, note_id: UUID) -> Optional[SessionNote]:
        """Get a specific session note."""
        return self.db.query(SessionNote).get(note_id)

    async def list_notes(
        self,
        campaign_id: UUID,
        chapter_id: Optional[UUID] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[SessionNote]:
        """List session notes with optional filters."""
        query = self.db.query(SessionNote).filter(
            SessionNote.campaign_id == campaign_id
        )

        if chapter_id:
            query = query.filter(SessionNote.chapter_id == chapter_id)

        if status:
            query = query.filter(SessionNote.feedback_status == status)

        return query.order_by(
            SessionNote.session_number.desc()
        ).offset(offset).limit(limit).all()

    async def update_note(
        self,
        note_id: UUID,
        request: UpdateSessionNoteRequest
    ) -> SessionNote:
        """Update a session note."""
        try:
            note = self.db.query(SessionNote).get(note_id)
            if not note:
                raise ValueError("Session note not found")

            # Update fields
            updates = request.dict(exclude_unset=True)
            for field, value in updates.items():
                if hasattr(note, field):
                    setattr(note, field, value)

            # Extract new character references if narrative updated
            if request.narrative:
                characters = await self._extract_character_references(
                    request.narrative,
                    request.character_interactions
                )
                # Update character records
                for record in note.character_records:
                    self.db.delete(record)
                
                for char_data in characters:
                    record = SessionCharacterRecord(
                        session_note_id=note.id,
                        character_id=char_data["id"],
                        character_type=char_data["type"],
                        interactions=char_data["interactions"],
                        significant_actions=char_data["actions"],
                        traits_demonstrated=char_data["traits"]
                    )
                    self.db.add(record)

            self.db.commit()

            # Publish event
            await self.message_hub.publish(
                "campaign.session_note.updated",
                {
                    "campaign_id": str(note.campaign_id),
                    "note_id": str(note.id),
                    "fields_updated": list(updates.keys())
                }
            )

            return note

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to update session note", error=str(e))
            raise ValueError(f"Failed to update session note: {e}")

    async def delete_note(self, note_id: UUID) -> None:
        """Delete a session note."""
        try:
            note = self.db.query(SessionNote).get(note_id)
            if not note:
                raise ValueError("Session note not found")

            self.db.delete(note)
            self.db.commit()

            # Publish event
            await self.message_hub.publish(
                "campaign.session_note.deleted",
                {
                    "campaign_id": str(note.campaign_id),
                    "note_id": str(note.id)
                }
            )

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to delete session note", error=str(e))
            raise ValueError(f"Failed to delete session note: {e}")

    async def process_feedback(
        self,
        note_id: UUID,
        request: ProcessNoteFeedbackRequest
    ) -> Dict:
        """Process feedback from session note."""
        try:
            note = self.db.query(SessionNote).get(note_id)
            if not note:
                raise ValueError("Session note not found")

            result = {
                "campaign": None,
                "characters": [],
                "npcs": [],
                "notes": []
            }

            # Process campaign feedback
            if request.apply_to_campaign:
                campaign_feedback = await self._process_campaign_feedback(
                    note,
                    request.custom_rules
                )
                result["campaign"] = campaign_feedback
                result["notes"].append("Applied campaign feedback")

            # Process character feedback
            if request.apply_to_characters or request.apply_to_npcs:
                char_updates = await self._process_character_feedback(
                    note,
                    request.custom_rules
                )
                
                for update in char_updates:
                    if update["type"] == "player" and request.apply_to_characters:
                        result["characters"].append(update)
                    elif update["type"] == "npc" and request.apply_to_npcs:
                        result["npcs"].append(update)

                result["notes"].append(
                    f"Applied feedback for {len(char_updates)} characters"
                )

            # Update note status
            note.feedback_status = "processed"
            note.feedback_processed_at = datetime.utcnow()
            self.db.commit()

            # Publish event
            await self.message_hub.publish(
                "campaign.session_note.feedback_processed",
                {
                    "campaign_id": str(note.campaign_id),
                    "note_id": str(note.id),
                    "updates": {
                        "campaign": bool(result["campaign"]),
                        "characters": len(result["characters"]),
                        "npcs": len(result["npcs"])
                    }
                }
            )

            return result

        except Exception as e:
            self.db.rollback()
            logger.error("Failed to process feedback", error=str(e))
            raise ValueError(f"Failed to process feedback: {e}")

    async def get_character_history(
        self,
        note_id: UUID,
        character_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Get character's session history."""
        try:
            # Get base note for campaign context
            note = self.db.query(SessionNote).get(note_id)
            if not note:
                raise ValueError("Session note not found")

            # Get character records
            records = self.db.query(SessionCharacterRecord).filter(
                and_(
                    SessionCharacterRecord.character_id == character_id,
                    SessionNote.campaign_id == note.campaign_id
                )
            ).join(
                SessionNote
            ).order_by(
                SessionNote.session_number.desc()
            ).limit(limit).all()

            return [{
                "session_number": r.session_note.session_number,
                "interactions": r.interactions,
                "significant_actions": r.significant_actions,
                "rewards_earned": r.rewards_earned,
                "consequences": r.consequences,
                "traits_demonstrated": r.traits_demonstrated
            } for r in records]

        except Exception as e:
            logger.error("Failed to get character history", error=str(e))
            raise ValueError(f"Failed to get character history: {e}")

    async def _extract_character_references(
        self,
        narrative: str,
        interactions: List[Dict]
    ) -> List[Dict]:
        """Extract and validate character references from text."""
        try:
            # Use AI to extract character references
            refs = await self.ai_client.extract_character_references({
                "text": narrative,
                "interactions": interactions
            })

            # Validate character IDs with character service
            valid_refs = await self.message_hub.request(
                "character.validate_refs",
                {
                    "references": refs
                }
            )

            return valid_refs["characters"]

        except Exception as e:
            logger.error("Failed to extract character references", error=str(e))
            return []

    async def _process_campaign_feedback(
        self,
        note: SessionNote,
        custom_rules: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Process feedback for campaign updates."""
        try:
            # Get campaign context
            campaign = await self.campaign_factory.get_campaign(note.campaign_id)

            # Generate campaign feedback
            feedback = await self.ai_client.generate_campaign_feedback({
                "campaign": campaign.dict(),
                "session_note": note.dict(),
                "custom_rules": custom_rules
            })

            if not feedback:
                return None

            # Apply feedback through campaign factory
            update_result = await self.campaign_factory.apply_feedback(
                note.campaign_id,
                feedback
            )

            return update_result

        except Exception as e:
            logger.error("Failed to process campaign feedback", error=str(e))
            return None

    async def _process_character_feedback(
        self,
        note: SessionNote,
        custom_rules: Optional[Dict] = None
    ) -> List[Dict]:
        """Process character feedback for updates."""
        try:
            updates = []

            for record in note.character_records:
                # Generate character feedback
                feedback = await self.ai_client.generate_character_feedback({
                    "character_id": record.character_id,
                    "character_type": record.character_type,
                    "session_data": record.dict(),
                    "custom_rules": custom_rules
                })

                if not feedback:
                    continue

                # Send feedback to character service
                update_result = await self.message_hub.request(
                    "character.apply_feedback",
                    {
                        "character_id": record.character_id,
                        "feedback": feedback
                    }
                )

                if update_result:
                    updates.append({
                        "id": record.character_id,
                        "type": record.character_type,
                        "updates": update_result["updates"]
                    })

            return updates

        except Exception as e:
            logger.error("Failed to process character feedback", error=str(e))
            return []

    async def generate_scene_setter(
        self,
        campaign_id: UUID,
        chapter_id: Optional[UUID] = None,
        encounter_id: Optional[str] = None,
        custom_rules: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate a narrative scene setter for DMs to use during game sessions.

        This provides DMs with rich narrative descriptions and important details about:
        - The current state of the campaign world
        - Chapter-specific context and plot points
        - Encounter details like enemies, NPCs, and environment
        - Puzzles, clues, and other interactive elements
        - Key information needed to run the session effectively
        """
        try:
            # Get campaign context
            campaign = await self.campaign_factory.get_campaign(campaign_id)
            if not campaign:
                raise ValueError("Campaign not found")

            context = {
                "campaign": campaign.dict(),
                "chapter": None,
                "encounter": None,
                "custom_rules": custom_rules
            }

            if chapter_id:
                chapter = await self.campaign_factory.get_chapter(chapter_id)
                if not chapter:
                    raise ValueError("Chapter not found")
                context["chapter"] = chapter.dict()

            if encounter_id:
                # Get encounter details if specified
                encounter = await self.campaign_factory.get_encounter(encounter_id)
                if not encounter:
                    raise ValueError("Encounter not found")
                context["encounter"] = encounter.dict()

            # Generate scene description using AI
            scene_setter = await self.ai_client.generate_scene_description(context)

            if not scene_setter:
                raise ValueError("Failed to generate scene description")

            return {
                "narrative": scene_setter["narrative"],
                "dm_notes": scene_setter["dm_notes"],
                "encounter_details": scene_setter.get("encounter_details"),
                "interactive_elements": scene_setter.get("interactive_elements"),
                "npc_details": scene_setter.get("npc_details"),
                "recommended_music": scene_setter.get("recommended_music")
            }

        except Exception as e:
            logger.error("Failed to generate scene setter", error=str(e))
            raise ValueError(f"Failed to generate scene setter: {e}")

async def _generate_map_prompt(
        self,
        location: Dict[str, Any],
        map_type: str,
        style_params: Optional[Dict] = None
    ) -> str:
        """Generate a detailed prompt for the image service to create a map."""
        try:
            prompt_context = {
                "location": location,
                "map_type": map_type,
                "style": style_params or {}
            }

            # Use AI to generate detailed prompt
            prompt_data = await self.ai_client.generate_map_prompt(prompt_context)
            return prompt_data["prompt"]

        except Exception as e:
            logger.error("Failed to generate map prompt", error=str(e))
            raise ValueError(f"Failed to generate map prompt: {e}")

    async def _generate_character_prompt(
        self,
        context: Dict[str, Any],
        character_type: str,
        requirements: Dict[str, Any]
    ) -> str:
        """Generate a detailed prompt for the character service."""
        try:
            prompt_context = {
                "campaign_context": context,
                "character_type": character_type,
                "requirements": requirements
            }

            # Use AI to generate detailed prompt
            prompt_data = await self.ai_client.generate_character_prompt(prompt_context)
            return prompt_data["prompt"]

        except Exception as e:
            logger.error("Failed to generate character prompt", error=str(e))
            raise ValueError(f"Failed to generate character prompt: {e}")

    async def _request_map_generation(
        self,
        location_id: UUID,
        map_type: str,
        prompt: str,
        style_params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Request map generation from image service."""
        try:
            # Send request to image service
            response = await self.message_hub.request(
                "image.generate_map",
                {
                    "prompt": prompt,
                    "style_params": style_params,
                    "metadata": {
                        "location_id": str(location_id),
                        "map_type": map_type
                    }
                }
            )

            if not response or "image_id" not in response:
                raise ValueError("Failed to generate map")

            return response

        except Exception as e:
            logger.error("Failed to request map generation", error=str(e))
            raise ValueError(f"Failed to generate map: {e}")

    async def _request_character_generation(
        self,
        character_type: str,
        prompt: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Request character generation from character service."""
        try:
            # Send request to character service
            response = await self.message_hub.request(
                "character.generate",
                {
                    "type": character_type,
                    "prompt": prompt,
                    "requirements": requirements
                }
            )

            if not response or "character_id" not in response:
                raise ValueError("Failed to generate character")

            return response

        except Exception as e:
            logger.error("Failed to request character generation", error=str(e))
            raise ValueError(f"Failed to generate character: {e}")

    async def _process_location_updates(
        self,
        updates: List[Dict],
        campaign_id: UUID
    ) -> List[Dict]:
        """Process location updates and generate/update maps as needed."""
        try:
            processed_updates = []

            for update in updates:
                location_id = update.get("location_id")
                map_types = update.get("required_maps", [])

                if not location_id:
                    # Create new location
                    location = MapLocation(
                        campaign_id=campaign_id,
                        name=update["name"],
                        location_type=update["type"],
                        description=update.get("description"),
                        coordinates=update.get("coordinates"),
                        metadata=update.get("metadata", {})
                    )
                    self.db.add(location)
                    await self.db.flush()
                    location_id = location.id

                for map_type in map_types:
                    # Check if map exists
                    existing_map = await self.db.query(LocationMap).filter(
                        LocationMap.location_id == location_id,
                        LocationMap.map_type == map_type["type"],
                        LocationMap.is_current == True
                    ).first()

                    if not existing_map or map_type.get("force_update"):
                        # Generate new map
                        prompt = await self._generate_map_prompt(
                            update,
                            map_type["type"],
                            map_type.get("style_params")
                        )

                        map_data = await self._request_map_generation(
                            location_id,
                            map_type["type"],
                            prompt,
                            map_type.get("style_params")
                        )

                        if existing_map:
                            existing_map.is_current = False

                        new_map = LocationMap(
                            location_id=location_id,
                            image_id=map_data["image_id"],
                            map_type=map_type["type"],
                            prompt=prompt,
                            style_params=map_type.get("style_params"),
                            version=(existing_map.version + 1 if existing_map else 1),
                            metadata=map_data.get("metadata", {})
                        )
                        self.db.add(new_map)

                processed_updates.append({
                    "location_id": str(location_id),
                    "maps_generated": map_types
                })

            return processed_updates

        except Exception as e:
            logger.error("Failed to process location updates", error=str(e))
            raise ValueError(f"Failed to process location updates: {e}")

    async def _process_character_requirements(
        self,
        requirements: List[Dict],
        context: Dict[str, Any]
    ) -> List[Dict]:
        """Process character requirements and request generation as needed."""
        try:
            generated_characters = []

            for req in requirements:
                char_type = req["type"]
                count = req.get("count", 1)

                for _ in range(count):
                    # Generate detailed prompt
                    prompt = await self._generate_character_prompt(
                        context,
                        char_type,
                        req
                    )

                    # Request character generation
                    char_data = await self._request_character_generation(
                        char_type,
                        prompt,
                        req
                    )

                    generated_characters.append({
                        "type": char_type,
                        "character_id": char_data["character_id"],
                        "details": char_data.get("details", {})
                    })

            return generated_characters

        except Exception as e:
            logger.error("Failed to process character requirements", error=str(e))
            raise ValueError(f"Failed to process character requirements: {e}")

    async def update_campaign_from_notes(
        self,
        note_id: UUID,
        update_type: str = "comprehensive",
        custom_rules: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Update campaign and chapter based on session notes using LLM analysis.

        Args:
            note_id: ID of the session note to process
            update_type: Type of update to perform
                - 'comprehensive': Full update of campaign and chapter
                - 'campaign-only': Update only campaign-level elements
                - 'chapter-only': Update only chapter-level elements
            custom_rules: Optional custom rules for the update process
        """
        try:
            # Get session note
            note = await self.get_note(note_id)
            if not note:
                raise ValueError("Session note not found")

            # Get campaign and chapter context
            campaign = await self.campaign_factory.get_campaign(note.campaign_id)
            chapter = None
            if note.chapter_id:
                chapter = await self.campaign_factory.get_chapter(note.chapter_id)

            # Prepare context for LLM
            context = {
                "session_note": note.dict(),
                "campaign": campaign.dict(),
                "chapter": chapter.dict() if chapter else None,
                "update_type": update_type,
                "custom_rules": custom_rules
            }

            # Generate updates using AI
            updates = await self.ai_client.generate_campaign_updates(context)

            if not updates:
                raise ValueError("Failed to generate updates")

            result = {
                "campaign_updates": [],
                "chapter_updates": [],
                "world_state_changes": [],
                "quest_updates": [],
                "notes": []
            }

            # Apply campaign updates if requested
            if update_type in ["comprehensive", "campaign-only"]:
                campaign_result = await self.campaign_factory.apply_updates(
                    note.campaign_id,
                    updates["campaign_updates"]
                )
                result["campaign_updates"] = campaign_result["updates"]
                result["world_state_changes"] = campaign_result["world_changes"]
                result["notes"].append("Applied campaign updates")

            # Apply chapter updates if requested
            if update_type in ["comprehensive", "chapter-only"] and chapter:
                chapter_result = await self.campaign_factory.apply_chapter_updates(
                    note.chapter_id,
                    updates["chapter_updates"]
                )
                result["chapter_updates"] = chapter_result["updates"]
                result["quest_updates"] = chapter_result["quest_changes"]
                result["notes"].append("Applied chapter updates")

            # Mark note as processed
            note.feedback_status = "processed"
            note.feedback_processed_at = datetime.utcnow()
            await self.db.commit()

            # Publish event
            await self.message_hub.publish(
                "campaign.updates.applied",
                {
                    "campaign_id": str(note.campaign_id),
                    "note_id": str(note.id),
                    "update_type": update_type,
                    "changes": {
                        "campaign": len(result["campaign_updates"]),
                        "chapter": len(result["chapter_updates"]),
                        "world": len(result["world_state_changes"]),
                        "quests": len(result["quest_updates"])
                    }
                }
            )

            return result

        except Exception as e:
            logger.error("Failed to update from notes", error=str(e))
            raise ValueError(f"Failed to update from notes: {e}")
