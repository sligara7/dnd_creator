"""Service layer for managing world effects."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.api.theme import (LocationCreate, LocationResponse,
                            WorldEffectCreate, WorldEffectResponse)
from ..models.theme import (Faction, Location, Theme, WorldEffect,
                        WorldEffectType)


class WorldEffectService:
    """Service for managing theme-driven world effects."""

    def __init__(self, db: AsyncSession, llm_service=None):
        """Initialize the world effect service.

        Args:
            db: Database session
            llm_service: Optional LLM service for content generation
        """
        self.db = db
        self.llm_service = llm_service

    async def create_world_effect(
        self, effect_data: WorldEffectCreate
    ) -> WorldEffect:
        """Create a new world effect.

        Args:
            effect_data: World effect creation data

        Returns:
            The created world effect
        """
        effect = WorldEffect(**effect_data.dict())
        self.db.add(effect)
        await self.db.flush()
        await self.db.refresh(effect)
        return effect

    async def get_world_effect(
        self, effect_id: UUID
    ) -> Optional[WorldEffect]:
        """Get a world effect by ID.

        Args:
            effect_id: World effect ID

        Returns:
            The world effect if found, None otherwise
        """
        query = select(WorldEffect).where(
            and_(
                WorldEffect.id == effect_id,
                WorldEffect.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_world_effects(
        self,
        theme_id: Optional[UUID] = None,
        effect_type: Optional[WorldEffectType] = None,
    ) -> List[WorldEffect]:
        """List world effects, optionally filtered.

        Args:
            theme_id: Optional theme ID to filter by
            effect_type: Optional effect type to filter by

        Returns:
            List of matching world effects
        """
        query = select(WorldEffect).where(WorldEffect.is_deleted == False)
        
        if theme_id:
            query = query.where(WorldEffect.theme_id == theme_id)
        if effect_type:
            query = query.where(WorldEffect.effect_type == effect_type)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_world_effect(self, effect_id: UUID) -> bool:
        """Soft delete a world effect.

        Args:
            effect_id: World effect ID

        Returns:
            True if effect was deleted, False if not found
        """
        effect = await self.get_world_effect(effect_id)
        if not effect:
            return False

        effect.is_deleted = True
        effect.deleted_at = datetime.utcnow()
        effect.updated_at = datetime.utcnow()
        
        await self.db.flush()
        return True

    async def apply_effect_to_location(
        self,
        effect_id: UUID,
        location_id: UUID,
    ) -> bool:
        """Apply a world effect to a location.

        Args:
            effect_id: World effect ID
            location_id: Location ID

        Returns:
            True if effect was applied, False if not found or not applicable
        """
        effect = await self.get_world_effect(effect_id)
        if not effect:
            return False

        location = await self._get_location(location_id)
        if not location:
            return False

        # Check if effect can be applied to this location
        if not await self._validate_effect_conditions(effect, location):
            return False

        # Apply effect parameters to location state
        location.state = await self._apply_effect_parameters(
            effect.parameters,
            location.state
        )
        location.updated_at = datetime.utcnow()
        
        # Add to affected locations relationship
        effect.affected_locations.append(location)
        
        await self.db.flush()
        return True

    async def apply_effect_to_faction(
        self,
        effect_id: UUID,
        faction_id: UUID,
    ) -> bool:
        """Apply a world effect to a faction.

        Args:
            effect_id: World effect ID
            faction_id: Faction ID

        Returns:
            True if effect was applied, False if not found or not applicable
        """
        effect = await self.get_world_effect(effect_id)
        if not effect:
            return False

        faction = await self._get_faction(faction_id)
        if not faction:
            return False

        # Check if effect can be applied to this faction
        if not await self._validate_effect_conditions(effect, faction):
            return False

        # Apply effect parameters to faction state
        faction.state = await self._apply_effect_parameters(
            effect.parameters,
            faction.state
        )
        faction.updated_at = datetime.utcnow()
        
        # Add to affected factions relationship
        effect.affected_factions.append(faction)
        
        await self.db.flush()
        return True

    async def get_active_effects(
        self,
        location_id: Optional[UUID] = None,
        faction_id: Optional[UUID] = None,
    ) -> List[WorldEffect]:
        """Get active world effects for a location or faction.

        Args:
            location_id: Optional location ID
            faction_id: Optional faction ID

        Returns:
            List of active world effects
        """
        now = datetime.utcnow()
        
        if location_id:
            # Get effects active on location
            location = await self._get_location(location_id)
            if not location:
                return []
            
            return [
                effect for effect in location.world_effects
                if (
                    not effect.is_deleted
                    and effect.created_at + timedelta(days=effect.duration) > now
                )
            ]
        
        elif faction_id:
            # Get effects active on faction
            faction = await self._get_faction(faction_id)
            if not faction:
                return []
            
            return [
                effect for effect in faction.world_effects
                if (
                    not effect.is_deleted
                    and effect.created_at + timedelta(days=effect.duration) > now
                )
            ]
        
        return []

    async def process_theme_world_effects(
        self,
        theme_id: UUID,
        campaign_id: UUID,
    ) -> List[WorldEffect]:
        """Process and generate world effects for a theme in a campaign.

        Args:
            theme_id: Theme ID
            campaign_id: Campaign ID

        Returns:
            List of created world effects
        """
        theme = await self._get_theme(theme_id)
        if not theme:
            return []

        # Get affected locations and factions
        locations = await self._get_campaign_locations(campaign_id)
        factions = await self._get_campaign_factions(campaign_id)

        created_effects = []

        # Generate world effects based on theme type
        if theme.type in ["political", "war", "intrigue"]:
            # Create faction-focused effects
            for faction in factions:
                effect = await self._generate_faction_effect(theme, faction)
                if effect:
                    created_effects.append(effect)

        if theme.type in ["wilderness", "urban", "dungeon", "planar"]:
            # Create location-focused effects
            for location in locations:
                effect = await self._generate_location_effect(theme, location)
                if effect:
                    created_effects.append(effect)

        # Use LLM for additional effect generation if available
        if self.llm_service:
            generated_effects = await self.llm_service.generate_theme_effects(
                theme=theme,
                locations=locations,
                factions=factions,
            )
            created_effects.extend(generated_effects)

        return created_effects

    async def _get_location(self, location_id: UUID) -> Optional[Location]:
        """Get a location by ID."""
        query = select(Location).where(
            and_(Location.id == location_id, Location.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_faction(self, faction_id: UUID) -> Optional[Faction]:
        """Get a faction by ID."""
        query = select(Faction).where(
            and_(Faction.id == faction_id, Faction.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_theme(self, theme_id: UUID) -> Optional[Theme]:
        """Get a theme by ID."""
        query = select(Theme).where(
            and_(Theme.id == theme_id, Theme.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_campaign_locations(
        self, campaign_id: UUID
    ) -> List[Location]:
        """Get all locations in a campaign."""
        query = select(Location).where(
            and_(
                Location.campaign_id == campaign_id,
                Location.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def _get_campaign_factions(
        self, campaign_id: UUID
    ) -> List[Faction]:
        """Get all factions in a campaign."""
        query = select(Faction).where(
            and_(
                Faction.campaign_id == campaign_id,
                Faction.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def _validate_effect_conditions(
        self,
        effect: WorldEffect,
        target: Location | Faction,
    ) -> bool:
        """Validate if an effect can be applied to a target."""
        conditions = effect.conditions

        # Check basic type compatibility
        if isinstance(target, Location):
            if effect.effect_type not in [
                WorldEffectType.ENVIRONMENT,
                WorldEffectType.CLIMATE,
                WorldEffectType.POPULATION,
            ]:
                return False
        elif isinstance(target, Faction):
            if effect.effect_type not in [
                WorldEffectType.FACTION,
                WorldEffectType.ECONOMY,
                WorldEffectType.POLITICS,
                WorldEffectType.CULTURE,
            ]:
                return False

        # Check attribute requirements
        required_attrs = conditions.get("required_attributes", {})
        for attr, value in required_attrs.items():
            if target.attributes.get(attr) != value:
                return False

        # Check state requirements
        required_state = conditions.get("required_state", {})
        for key, value in required_state.items():
            if target.state.get(key) != value:
                return False

        return True

    async def _apply_effect_parameters(
        self,
        parameters: Dict,
        current_state: Dict,
    ) -> Dict:
        """Apply effect parameters to update a state dictionary."""
        new_state = current_state.copy()

        # Apply direct state changes
        state_changes = parameters.get("state_changes", {})
        for key, value in state_changes.items():
            if isinstance(value, (int, float)) and key in new_state:
                # Handle numeric modifications
                new_state[key] += value
            else:
                # Handle direct value assignments
                new_state[key] = value

        # Apply conditional changes
        conditions = parameters.get("conditional_changes", [])
        for condition in conditions:
            if self._check_condition(condition["condition"], new_state):
                for key, value in condition["changes"].items():
                    new_state[key] = value

        return new_state

    def _check_condition(self, condition: Dict, state: Dict) -> bool:
        """Check if a condition is met in the given state."""
        operator = condition.get("operator", "equals")
        state_value = state.get(condition["key"])
        check_value = condition["value"]

        if operator == "equals":
            return state_value == check_value
        elif operator == "greater_than":
            return state_value > check_value
        elif operator == "less_than":
            return state_value < check_value
        elif operator == "contains":
            return check_value in state_value
        return False

    async def _generate_faction_effect(
        self,
        theme: Theme,
        faction: Faction,
    ) -> Optional[WorldEffect]:
        """Generate a theme-appropriate effect for a faction."""
        effect_type = WorldEffectType.FACTION
        if theme.type == "political":
            effect_type = WorldEffectType.POLITICS
        elif theme.type == "intrigue":
            effect_type = WorldEffectType.CULTURE

        # Create effect data based on theme attributes
        effect_data = WorldEffectCreate(
            theme_id=theme.id,
            name=f"{theme.name} Impact on {faction.name}",
            description=self._generate_effect_description(theme, faction),
            effect_type=effect_type,
            parameters=self._generate_faction_parameters(theme, faction),
            conditions=self._generate_faction_conditions(theme, faction),
            impact_scale=0.7,
            duration=30,  # 30 days default
        )

        return await self.create_world_effect(effect_data)

    async def _generate_location_effect(
        self,
        theme: Theme,
        location: Location,
    ) -> Optional[WorldEffect]:
        """Generate a theme-appropriate effect for a location."""
        effect_type = WorldEffectType.ENVIRONMENT
        if theme.type == "wilderness":
            effect_type = WorldEffectType.CLIMATE
        elif theme.type in ["urban", "dungeon"]:
            effect_type = WorldEffectType.POPULATION

        # Create effect data based on theme attributes
        effect_data = WorldEffectCreate(
            theme_id=theme.id,
            name=f"{theme.name} Impact on {location.name}",
            description=self._generate_effect_description(theme, location),
            effect_type=effect_type,
            parameters=self._generate_location_parameters(theme, location),
            conditions=self._generate_location_conditions(theme, location),
            impact_scale=0.6,
            duration=45,  # 45 days default
        )

        return await self.create_world_effect(effect_data)

    def _generate_effect_description(
        self,
        theme: Theme,
        target: Location | Faction,
    ) -> str:
        """Generate a description for a world effect."""
        if isinstance(target, Location):
            return (
                f"The {theme.name} theme transforms {target.name}, "
                f"manifesting as {theme.attributes.get('manifestation', 'changes')} "
                f"with {theme.intensity} intensity."
            )
        else:
            return (
                f"The {theme.name} theme influences {target.name}, "
                f"causing {theme.attributes.get('influence', 'changes')} "
                f"with {theme.intensity} intensity."
            )

    def _generate_faction_parameters(
        self, theme: Theme, faction: Faction
    ) -> Dict:
        """Generate effect parameters for a faction."""
        return {
            "state_changes": {
                "influence": 0.1 if theme.intensity == "subtle" else 0.3,
                "stability": -0.2 if theme.tone == "dark" else 0.2,
            },
            "conditional_changes": [
                {
                    "condition": {
                        "key": "power_level",
                        "operator": "greater_than",
                        "value": 0.7
                    },
                    "changes": {
                        "territory_control": 0.1,
                        "resource_access": 0.2
                    }
                }
            ]
        }

    def _generate_location_parameters(
        self, theme: Theme, location: Location
    ) -> Dict:
        """Generate effect parameters for a location."""
        return {
            "state_changes": {
                "danger_level": 0.2 if theme.tone == "dark" else -0.1,
                "resource_abundance": -0.1 if theme.intensity == "overwhelming" else 0.1,
            },
            "conditional_changes": [
                {
                    "condition": {
                        "key": "population",
                        "operator": "greater_than",
                        "value": 1000
                    },
                    "changes": {
                        "unrest": 0.2,
                        "trade": -0.1
                    }
                }
            ]
        }

    def _generate_faction_conditions(
        self, theme: Theme, faction: Faction
    ) -> Dict:
        """Generate effect conditions for a faction."""
        return {
            "required_attributes": {
                "organization_type": faction.faction_type,
                "power_level": "medium"
            },
            "required_state": {
                "is_active": True,
                "stability": 0.5
            }
        }

    def _generate_location_conditions(
        self, theme: Theme, location: Location
    ) -> Dict:
        """Generate effect conditions for a location."""
        return {
            "required_attributes": {
                "location_type": location.location_type,
                "size": "medium"
            },
            "required_state": {
                "is_accessible": True,
                "population": 100
            }
        }
