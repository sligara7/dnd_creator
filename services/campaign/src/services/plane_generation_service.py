"""Service for generating custom planes of existence using LLM."""
from typing import Dict, List, Optional, Any
from uuid import UUID

from ..core.ai import AIClient
from ..core.logging import get_logger
from ..models.planes import Plane
from .plane_service import PlaneService

logger = get_logger(__name__)


class PlaneGenerationService:
    """Service for generating custom planes using LLM."""

    def __init__(
        self,
        ai_client: AIClient,
        plane_service: PlaneService,
    ):
        self.ai_client = ai_client
        self.plane_service = plane_service

    async def generate_plane(
        self,
        concept: str,
        requirements: Optional[Dict[str, Any]] = None,
        existing_planes: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate a complete plane of existence from a concept."""
        try:
            # Build generation context
            context = {
                "concept": concept,
                "requirements": requirements or {},
                "existing_planes": existing_planes or []
            }

            # Generate base plane description
            base_plane = await self._generate_base_plane(context)

            # Generate detailed rules
            rules = await self._generate_plane_rules(base_plane, context)

            # Generate consistency validations
            validations = await self._validate_plane_consistency(
                base_plane,
                rules,
                context
            )

            if not validations["is_valid"]:
                raise ValueError(
                    f"Generated plane is not consistent: {validations['issues']}"
                )

            # Generate complete plane definition
            plane_definition = {
                "name": base_plane["name"],
                "type": base_plane["type"],
                "description": base_plane["description"],
                "physics_rules": rules["physics"],
                "magic_rules": rules["magic"],
                "base_effects": rules["effects"],
                "transition_rules": rules["transitions"],
                "metadata": {
                    "concept": concept,
                    "theme": base_plane["theme"],
                    "validations": validations["checks"],
                    "generation_context": context
                }
            }

            return plane_definition

        except Exception as e:
            logger.error("Failed to generate plane", error=str(e))
            raise ValueError(f"Failed to generate plane: {e}")

    async def _generate_base_plane(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate base plane concept and description."""
        try:
            prompt = f"""Generate a detailed D&D plane of existence based on this concept:
            {context['concept']}

            Include:
            1. Name and type of plane
            2. Detailed description
            3. Overall theme and atmosphere
            4. Key distinguishing features
            5. Fundamental nature of reality
            6. Basic assumptions about existence

            If there are specific requirements, incorporate them:
            {context.get('requirements', {})}

            Consider existing planes for consistency:
            {context.get('existing_planes', [])}

            Format as structured data with name, type, description, theme, and features.
            """

            response = await self.ai_client.generate_plane_concept({"prompt": prompt})
            return response["plane_concept"]

        except Exception as e:
            logger.error("Failed to generate base plane", error=str(e))
            raise

    async def _generate_plane_rules(
        self,
        base_plane: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed rules for the plane."""
        try:
            prompt = f"""Generate comprehensive rules for this plane of existence:

            Plane Concept:
            {base_plane}

            Generate detailed rules for:
            1. Physics and Natural Laws:
               - Space and time
               - Matter and energy
               - Fundamental forces
               - Environmental conditions

            2. Magic System:
               - How magic functions
               - Unique spell effects
               - Power sources
               - Limitations and enhancements

            3. Base Effects on Entities:
               - Impact on living beings
               - Effect on items and equipment
               - Mental/physical/spiritual changes
               - Special abilities or restrictions

            4. Transition Rules:
               - Entry and exit conditions
               - Transformation effects
               - Compatibility with other planes
               - Travel mechanics

            Consider any specific requirements:
            {context.get('requirements', {})}

            Format as structured data with physics_rules, magic_rules, effects, and transitions.
            """

            response = await self.ai_client.generate_plane_rules({
                "prompt": prompt,
                "base_plane": base_plane
            })
            return response["plane_rules"]

        except Exception as e:
            logger.error("Failed to generate plane rules", error=str(e))
            raise

    async def _validate_plane_consistency(
        self,
        base_plane: Dict[str, Any],
        rules: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate internal consistency of generated plane."""
        try:
            prompt = f"""Validate the consistency of this plane of existence:

            Base Plane:
            {base_plane}

            Rules:
            {rules}

            Check for:
            1. Internal Consistency:
               - Are physics rules self-consistent?
               - Do magic rules align with physics?
               - Are effects logical within the system?

            2. Playability:
               - Can characters meaningfully interact?
               - Are there clear ways to navigate?
               - Do abilities and restrictions balance?

            3. Integration:
               - Can it connect with other planes?
               - Does it fit the campaign context?
               - Are transitions logical?

            4. Balance:
               - Are powers/limitations balanced?
               - Is survival possible?
               - Are there meaningful challenges?

            Context:
            {context}

            Format response as structured data with is_valid flag, checks performed, and any issues found.
            """

            response = await self.ai_client.validate_plane_consistency({
                "prompt": prompt,
                "plane_data": {
                    "base": base_plane,
                    "rules": rules,
                    "context": context
                }
            })
            return response["validation_results"]

        except Exception as e:
            logger.error("Failed to validate plane consistency", error=str(e))
            raise

    async def generate_transition_mapping(
        self,
        source_plane: Dict[str, Any],
        target_plane: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate rules for transitioning between two planes."""
        try:
            prompt = f"""Generate transition rules between these planes:

            Source Plane:
            {source_plane}

            Target Plane:
            {target_plane}

            Define:
            1. Transformation Rules:
               - Entity changes
               - Equipment adaptations
               - Power/ability modifications
               - State transformations

            2. Transition Mechanics:
               - How transition occurs
               - Duration and stages
               - Required conditions
               - Possible complications

            3. Compatibility Layer:
               - How systems interact
               - Shared elements
               - Conflicting elements
               - Resolution mechanics

            Format as structured data with transformation_rules, mechanics, and compatibility.
            """

            response = await self.ai_client.generate_transition_mapping({
                "prompt": prompt,
                "source_plane": source_plane,
                "target_plane": target_plane
            })
            return response["transition_mapping"]

        except Exception as e:
            logger.error("Failed to generate transition mapping", error=str(e))
            raise

    async def generate_plane_content(
        self,
        plane_id: UUID,
        content_type: str,
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate plane-specific content (locations, creatures, items, etc)."""
        try:
            plane = await self.plane_service.get_plane(plane_id)
            if not plane:
                raise ValueError("Plane not found")

            prompt = f"""Generate {content_type} for this plane:

            Plane:
            {plane.dict()}

            Requirements:
            {requirements or {}}

            Generate complete definition including:
            1. Base properties
            2. Plane-specific manifestation
            3. Special abilities/effects
            4. Interaction rules
            5. Balance considerations

            Format as structured data appropriate for the content type.
            """

            response = await self.ai_client.generate_plane_content({
                "prompt": prompt,
                "plane": plane.dict(),
                "content_type": content_type,
                "requirements": requirements
            })
            return response["content"]

        except Exception as e:
            logger.error(
                "Failed to generate plane content",
                content_type=content_type,
                error=str(e)
            )
            raise

    async def adapt_entity_to_plane(
        self,
        entity: Dict[str, Any],
        target_plane: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate rules for adapting an entity to a plane."""
        try:
            prompt = f"""Adapt this entity to the target plane:

            Entity:
            {entity}

            Target Plane:
            {target_plane}

            Generate:
            1. Form Adaptation:
               - Physical/spiritual form
               - Attribute modifications
               - Ability changes
               - New limitations/powers

            2. Equipment Adaptation:
               - How items manifest
               - Functional changes
               - Power scaling
               - New properties

            3. Interaction Rules:
               - How to interact with plane
               - Special abilities
               - Restrictions
               - Movement/action rules

            Format as structured data with form, equipment, and interaction rules.
            """

            response = await self.ai_client.adapt_entity_to_plane({
                "prompt": prompt,
                "entity": entity,
                "plane": target_plane
            })
            return response["adaptation_rules"]

        except Exception as e:
            logger.error("Failed to adapt entity to plane", error=str(e))
            raise
