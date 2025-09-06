"""Service for campaign generation and content creation."""

from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.api.factory import (CampaignGenerationRequest,
                              CampaignGenerationResponse,
                              CampaignRefinementRequest,
                              CampaignRefinementResponse,
                              NPCGenerationRequest, NPCGenerationResponse,
                              LocationGenerationRequest,
                              LocationGenerationResponse,
                              MapGenerationRequest, MapGenerationResponse)
from ..models.theme import Theme


class CampaignFactory:
    """Factory service for campaign and content generation."""

    def __init__(
        self,
        db: AsyncSession,
        llm_service=None,
        theme_service=None,
        world_effect_service=None,
    ):
        """Initialize the campaign factory.

        Args:
            db: Database session
            llm_service: LLM service for content generation
            theme_service: Theme service for theme application
            world_effect_service: World effect service for environmental changes
        """
        self.db = db
        self.llm_service = llm_service
        self.theme_service = theme_service
        self.world_effect_service = world_effect_service

    async def generate_campaign(
        self, request: CampaignGenerationRequest
    ) -> CampaignGenerationResponse:
        """Generate a new campaign.

        Args:
            request: Campaign generation parameters

        Returns:
            Generated campaign details
        """
        try:
            # Get themes if specified
            themes = []
            if request.theme_ids:
                themes = [
                    await self.theme_service.get_theme(theme_id)
                    for theme_id in request.theme_ids
                ]
                themes = [t for t in themes if t]  # Filter out None values

            # Generate campaign structure based on complexity and length
            structure = await self._generate_campaign_structure(
                request.complexity,
                request.length,
                request.campaign_type,
                themes,
            )

            # Generate initial content
            content = await self._generate_campaign_content(
                structure,
                request.level_range,
                request.player_count,
                themes,
                request.parameters,
            )

            # Create campaign in database
            campaign = await self._create_campaign(
                request, structure, content
            )

            # Apply themes if specified
            if themes:
                campaign = await self._apply_themes_to_campaign(
                    campaign, themes
                )

            return CampaignGenerationResponse(
                campaign_id=campaign.id,
                status="success",
                message="Campaign generated successfully",
                details={
                    "structure": structure,
                    "applied_themes": [t.name for t in themes],
                },
                generated_content=content,
            )

        except Exception as e:
            return CampaignGenerationResponse(
                campaign_id=UUID(int=0),  # Dummy UUID
                status="error",
                message=str(e),
            )

    async def refine_campaign(
        self, request: CampaignRefinementRequest
    ) -> CampaignRefinementResponse:
        """Refine an existing campaign.

        Args:
            request: Campaign refinement parameters

        Returns:
            Refinement results
        """
        try:
            # Get current campaign state
            campaign = await self._get_campaign(request.campaign_id)
            if not campaign:
                raise ValueError("Campaign not found")

            changes = []
            preserved = request.preserve or []

            # Apply refinements based on type
            if request.refinement_type == "theme":
                changes = await self._refine_campaign_theme(
                    campaign,
                    request.adjustments,
                    preserved,
                )
            elif request.refinement_type == "content":
                changes = await self._refine_campaign_content(
                    campaign,
                    request.adjustments,
                    preserved,
                )
            elif request.refinement_type == "structure":
                changes = await self._refine_campaign_structure(
                    campaign,
                    request.adjustments,
                    preserved,
                )
            else:
                raise ValueError(f"Unknown refinement type: {request.refinement_type}")

            return CampaignRefinementResponse(
                campaign_id=campaign.id,
                status="success",
                message="Campaign refined successfully",
                changes=changes,
                preserved=preserved,
            )

        except Exception as e:
            return CampaignRefinementResponse(
                campaign_id=request.campaign_id,
                status="error",
                message=str(e),
                changes=[],
                preserved=[],
            )

    async def generate_npc(
        self, request: NPCGenerationRequest
    ) -> NPCGenerationResponse:
        """Generate a new NPC for a campaign.

        Args:
            request: NPC generation parameters

        Returns:
            Generated NPC details
        """
        try:
            # Get campaign context
            campaign = await self._get_campaign(request.campaign_id)
            if not campaign:
                raise ValueError("Campaign not found")

            # Get theme if specified
            theme = None
            if request.theme_id:
                theme = await self.theme_service.get_theme(request.theme_id)

            # Generate NPC data
            npc_data = await self._generate_npc_data(
                campaign,
                request.npc_type,
                request.role,
                theme,
                request.parameters,
            )

            # Generate relationships if specified
            relationships = []
            if request.relationships:
                relationships = await self._generate_npc_relationships(
                    npc_data,
                    request.relationships,
                    campaign,
                )

            # Create NPC in database
            npc = await self._create_npc(
                campaign,
                npc_data,
                relationships,
            )

            return NPCGenerationResponse(
                npc_id=npc.id,
                status="success",
                message="NPC generated successfully",
                npc_data=npc_data,
                relationships=relationships,
                theme_elements=npc_data.get("theme_elements"),
            )

        except Exception as e:
            return NPCGenerationResponse(
                npc_id=UUID(int=0),  # Dummy UUID
                status="error",
                message=str(e),
                npc_data={},
                relationships=[],
            )

    async def generate_location(
        self, request: LocationGenerationRequest
    ) -> LocationGenerationResponse:
        """Generate a new location for a campaign.

        Args:
            request: Location generation parameters

        Returns:
            Generated location details
        """
        try:
            # Get campaign context
            campaign = await self._get_campaign(request.campaign_id)
            if not campaign:
                raise ValueError("Campaign not found")

            # Get theme if specified
            theme = None
            if request.theme_id:
                theme = await self.theme_service.get_theme(request.theme_id)

            # Generate location data
            location_data = await self._generate_location_data(
                campaign,
                request.location_type,
                request.importance,
                theme,
                request.parameters,
            )

            # Generate connections if specified
            connections = []
            if request.connections:
                connections = await self._generate_location_connections(
                    location_data,
                    request.connections,
                    campaign,
                )

            # Create location in database
            location = await self._create_location(
                campaign,
                location_data,
                connections,
            )

            # Generate world effects if appropriate
            if theme:
                await self._generate_location_effects(location, theme)

            return LocationGenerationResponse(
                location_id=location.id,
                status="success",
                message="Location generated successfully",
                location_data=location_data,
                connections=connections,
                theme_elements=location_data.get("theme_elements"),
            )

        except Exception as e:
            return LocationGenerationResponse(
                location_id=UUID(int=0),  # Dummy UUID
                status="error",
                message=str(e),
                location_data={},
                connections=[],
            )

    async def generate_map(
        self, request: MapGenerationRequest
    ) -> MapGenerationResponse:
        """Generate a new map for a campaign.

        Args:
            request: Map generation parameters

        Returns:
            Generated map details
        """
        try:
            # Get campaign context
            campaign = await self._get_campaign(request.campaign_id)
            if not campaign:
                raise ValueError("Campaign not found")

            # Get location if specified
            location = None
            if request.location_id:
                location = await self._get_location(request.location_id)

            # Get theme if specified
            theme = None
            if request.theme_id:
                theme = await self.theme_service.get_theme(request.theme_id)

            # Generate map data
            map_data = await self._generate_map_data(
                campaign,
                request.map_type,
                request.scale,
                location,
                theme,
                request.parameters,
            )

            # Generate map image using external service
            image_url = await self._generate_map_image(map_data)

            # Create map in database
            map_obj = await self._create_map(
                campaign,
                map_data,
                image_url,
            )

            return MapGenerationResponse(
                map_id=map_obj.id,
                status="success",
                message="Map generated successfully",
                map_data=map_data,
                image_url=image_url,
                features=map_data.get("features", []),
                theme_elements=map_data.get("theme_elements"),
            )

        except Exception as e:
            return MapGenerationResponse(
                map_id=UUID(int=0),  # Dummy UUID
                status="error",
                message=str(e),
                map_data={},
                image_url="",
                features=[],
            )

    async def _generate_campaign_structure(
        self,
        complexity: str,
        length: str,
        campaign_type: str,
        themes: List[Theme],
    ) -> Dict:
        """Generate campaign structure based on parameters."""
        if not self.llm_service:
            raise ValueError("LLM service required for campaign generation")

        prompt = self._build_structure_prompt(
            complexity, length, campaign_type, themes
        )
        result = await self.llm_service.generate_content(prompt)

        return self._parse_structure_response(result)

    async def _generate_campaign_content(
        self,
        structure: Dict,
        level_range: Dict,
        player_count: Dict,
        themes: List[Theme],
        parameters: Optional[Dict],
    ) -> Dict:
        """Generate initial campaign content."""
        if not self.llm_service:
            raise ValueError("LLM service required for content generation")

        prompt = self._build_content_prompt(
            structure, level_range, player_count, themes, parameters
        )
        result = await self.llm_service.generate_content(prompt)

        return self._parse_content_response(result)

    def _build_structure_prompt(
        self,
        complexity: str,
        length: str,
        campaign_type: str,
        themes: List[Theme],
    ) -> str:
        """Build prompt for campaign structure generation."""
        theme_text = "\n".join(
            f"- {t.name}: {t.description}" for t in themes
        ) if themes else "No specific themes"

        return f"""Generate a D&D campaign structure with:
Complexity: {complexity}
Length: {length}
Type: {campaign_type}
Themes:
{theme_text}

The structure should include:
1. Overall narrative arc
2. Chapter breakdown
3. Major plot points
4. Key NPCs and locations
5. Theme integration points

Return in JSON format with:
- narrative_arc
- chapters
- plot_points
- key_npcs
- key_locations
- theme_elements

Format each chapter as:
{{
    "title": "Chapter title",
    "summary": "Brief summary",
    "objectives": ["list", "of", "objectives"],
    "key_elements": {{
        "npcs": ["list of NPCs"],
        "locations": ["list of locations"],
        "items": ["list of items"]
    }}
}}"""

    def _build_content_prompt(
        self,
        structure: Dict,
        level_range: Dict,
        player_count: Dict,
        themes: List[Theme],
        parameters: Optional[Dict],
    ) -> str:
        """Build prompt for campaign content generation."""
        theme_text = "\n".join(
            f"- {t.name}: {t.description}" for t in themes
        ) if themes else "No specific themes"

        param_text = "\n".join(
            f"- {k}: {v}" for k, v in (parameters or {}).items()
        ) if parameters else "No additional parameters"

        return f"""Generate detailed content for a D&D campaign with:
Level Range: {level_range['min']} to {level_range['max']}
Player Count: {player_count['min']} to {player_count['max']}
Themes:
{theme_text}

Parameters:
{param_text}

Based on structure:
{structure}

Generate detailed content for:
1. Chapter narratives
2. NPC details and motivations
3. Location descriptions
4. Key items and artifacts
5. Plot hooks and transitions
6. Theme manifestations

Return in JSON format with:
- chapters
- npcs
- locations
- items
- plot_hooks
- theme_elements"""

    def _parse_structure_response(self, response: Dict) -> Dict:
        """Parse LLM response for campaign structure."""
        # Implementation would validate and process LLM response
        return response

    def _parse_content_response(self, response: Dict) -> Dict:
        """Parse LLM response for campaign content."""
        # Implementation would validate and process LLM response
        return response

    async def _create_campaign(
        self,
        request: CampaignGenerationRequest,
        structure: Dict,
        content: Dict,
    ) -> object:
        """Create campaign in database."""
        # Implementation would create campaign using models/repositories
        pass

    async def _apply_themes_to_campaign(
        self,
        campaign: object,
        themes: List[Theme],
    ) -> object:
        """Apply themes to campaign content."""
        # Implementation would use theme service to apply themes
        pass

    async def _get_campaign(self, campaign_id: UUID) -> Optional[object]:
        """Get campaign from database."""
        # Implementation would retrieve campaign using models/repositories
        pass

    async def _get_location(self, location_id: UUID) -> Optional[object]:
        """Get location from database."""
        # Implementation would retrieve location using models/repositories
        pass

    async def _refine_campaign_theme(
        self,
        campaign: object,
        adjustments: Dict,
        preserved: List[str],
    ) -> List[Dict]:
        """Refine campaign theme elements."""
        # Implementation would use theme service to refine themes
        pass

    async def _refine_campaign_content(
        self,
        campaign: object,
        adjustments: Dict,
        preserved: List[str],
    ) -> List[Dict]:
        """Refine campaign content."""
        # Implementation would use LLM to refine content
        pass

    async def _refine_campaign_structure(
        self,
        campaign: object,
        adjustments: Dict,
        preserved: List[str],
    ) -> List[Dict]:
        """Refine campaign structure."""
        # Implementation would use LLM to refine structure
        pass

    async def _generate_npc_data(
        self,
        campaign: object,
        npc_type: str,
        role: Optional[str],
        theme: Optional[Theme],
        parameters: Optional[Dict],
    ) -> Dict:
        """Generate NPC data."""
        # Implementation would use LLM to generate NPC
        pass

    async def _generate_npc_relationships(
        self,
        npc_data: Dict,
        relationships: List[Dict],
        campaign: object,
    ) -> List[Dict]:
        """Generate NPC relationships."""
        # Implementation would generate relationships
        pass

    async def _create_npc(
        self,
        campaign: object,
        npc_data: Dict,
        relationships: List[Dict],
    ) -> object:
        """Create NPC in database."""
        # Implementation would create NPC using models/repositories
        pass

    async def _generate_location_data(
        self,
        campaign: object,
        location_type: str,
        importance: str,
        theme: Optional[Theme],
        parameters: Optional[Dict],
    ) -> Dict:
        """Generate location data."""
        # Implementation would use LLM to generate location
        pass

    async def _generate_location_connections(
        self,
        location_data: Dict,
        connections: List[Dict],
        campaign: object,
    ) -> List[Dict]:
        """Generate location connections."""
        # Implementation would generate connections
        pass

    async def _create_location(
        self,
        campaign: object,
        location_data: Dict,
        connections: List[Dict],
    ) -> object:
        """Create location in database."""
        # Implementation would create location using models/repositories
        pass

    async def _generate_location_effects(
        self,
        location: object,
        theme: Theme,
    ) -> None:
        """Generate and apply world effects to location."""
        # Implementation would use world effect service
        pass

    async def _generate_map_data(
        self,
        campaign: object,
        map_type: str,
        scale: str,
        location: Optional[object],
        theme: Optional[Theme],
        parameters: Optional[Dict],
    ) -> Dict:
        """Generate map data."""
        # Implementation would use LLM to generate map data
        pass

    async def _generate_map_image(self, map_data: Dict) -> str:
        """Generate map image using external service."""
        # Implementation would use image service to generate map
        pass

    async def _create_map(
        self,
        campaign: object,
        map_data: Dict,
        image_url: str,
    ) -> object:
        """Create map in database."""
        # Implementation would create map using models/repositories
        pass
