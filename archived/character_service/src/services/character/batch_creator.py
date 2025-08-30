"""Batch creation service for NPCs and monsters."""

import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from .npc_creator import NPCCreator, NPCType
from .monster_creator import MonsterCreator, MonsterTemplate, MonsterType, MonsterSize
from .theme_manager import ThemeManager
from .cr_calculator import CRCalculator

class CreatureRole(Enum):
    """Role in an encounter or scenario."""
    BOSS = "boss"
    ELITE = "elite"
    STANDARD = "standard"
    MINION = "minion"
    SWARM = "swarm"

@dataclass
class BatchRequest:
    """Request for batch creature creation."""
    count: int
    target_cr: float
    role: CreatureRole
    theme: Optional[str] = None
    creature_type: Optional[str] = None  # Monster type or NPC role
    variation_level: str = "medium"  # "low", "medium", "high"

@dataclass
class EncounterGroup:
    """Group of related creatures for an encounter."""
    boss: Optional[Dict[str, Any]] = None
    elites: List[Dict[str, Any]] = None
    standard: List[Dict[str, Any]] = None
    minions: List[Dict[str, Any]] = None

class BatchCreator:
    """Creates batches of NPCs and monsters efficiently."""

    def __init__(self, npc_creator: NPCCreator, monster_creator: MonsterCreator,
                 theme_manager: ThemeManager, cr_calculator: CRCalculator):
        self.npc_creator = npc_creator
        self.monster_creator = monster_creator
        self.theme_manager = theme_manager
        self.cr_calculator = cr_calculator

    async def create_batch(self, request: BatchRequest) -> List[Dict[str, Any]]:
        """Create a batch of similar creatures."""
        base_creature = await self._generate_base_creature(request)
        
        # For minions/swarms, use simplified stats
        if request.role in [CreatureRole.MINION, CreatureRole.SWARM]:
            return await self._create_simplified_batch(base_creature, request)
        
        # For standard creatures, create variations
        variations = await self._create_variations(base_creature, request)
        return variations

    async def create_encounter_group(self, 
                                   boss_cr: float,
                                   minion_count: int,
                                   theme: Optional[str] = None) -> EncounterGroup:
        """Create a complete encounter group with boss and minions."""
        # Create boss with full detail
        boss_request = BatchRequest(
            count=1,
            target_cr=boss_cr,
            role=CreatureRole.BOSS,
            theme=theme,
            variation_level="high"
        )
        boss = (await self._generate_base_creature(boss_request))

        # Create elite lieutenants (CR = boss_cr - 2)
        elite_request = BatchRequest(
            count=2,
            target_cr=max(1, boss_cr - 2),
            role=CreatureRole.ELITE,
            theme=theme,
            variation_level="medium"
        )
        elites = await self.create_batch(elite_request)

        # Create minions (CR = boss_cr - 4)
        minion_request = BatchRequest(
            count=minion_count,
            target_cr=max(0.25, boss_cr - 4),
            role=CreatureRole.MINION,
            theme=theme,
            variation_level="low"
        )
        minions = await self.create_batch(minion_request)

        return EncounterGroup(
            boss=boss,
            elites=elites,
            minions=minions
        )

    async def _generate_base_creature(self, request: BatchRequest) -> Dict[str, Any]:
        """Generate base creature for variations."""
        if request.role == CreatureRole.BOSS:
            # Generate full character sheet with backstory
            return await self._generate_detailed_boss(request)
        elif request.role == CreatureRole.MINION:
            # Generate simplified stat block
            return await self._generate_simplified_creature(request)
        else:
            # Generate standard creature
            return await self._generate_standard_creature(request)

    async def _generate_detailed_boss(self, request: BatchRequest) -> Dict[str, Any]:
        """Generate a detailed boss character with full background."""
        # Determine if it should be an NPC or monster
        is_humanoid = request.creature_type and "humanoid" in request.creature_type.lower()
        
        if is_humanoid:
            # Create detailed NPC
            npc_type = NPCType(
                name="Boss",
                role="boss",
                challenge_rating=request.target_cr,
                is_recurring=True
            )
            concept = await self._generate_boss_concept(request)
            return await self.npc_creator.create_npc_from_concept(
                concept=concept,
                npc_type=npc_type,
                theme=request.theme
            )
        else:
            # Create legendary monster
            template = MonsterTemplate(
                type=self._determine_monster_type(request),
                size=MonsterSize.LARGE,
                challenge_rating=request.target_cr,
                is_legendary=True,
                is_unique=True,
                role="boss"
            )
            concept = await self._generate_boss_concept(request)
            return await self.monster_creator.create_monster_from_concept(
                concept=concept,
                template=template,
                theme=request.theme
            )

    async def _generate_simplified_creature(self, request: BatchRequest) -> Dict[str, Any]:
        """Generate simplified creature for minions/swarms."""
        # Use minimal stat block for efficiency
        if request.creature_type and "humanoid" in request.creature_type.lower():
            template = {
                "name": f"Minion {request.creature_type}",
                "type": "humanoid",
                "cr": request.target_cr,
                "hp": int(request.target_cr * 10),
                "ac": 10 + int(request.target_cr / 2),
                "attack_bonus": int(request.target_cr / 2),
                "damage": f"{max(1, int(request.target_cr))}d6",
                "speed": 30
            }
        else:
            template = {
                "name": f"Minion Creature",
                "type": request.creature_type or "monstrosity",
                "cr": request.target_cr,
                "hp": int(request.target_cr * 12),
                "ac": 12 + int(request.target_cr / 2),
                "attack_bonus": int(request.target_cr / 2),
                "damage": f"{max(1, int(request.target_cr))}d8",
                "speed": 30
            }

        # Apply theme if provided
        if request.theme:
            template = await self.theme_manager.apply_theme_to_template(
                template, request.theme
            )

        return template

    async def _generate_standard_creature(self, request: BatchRequest) -> Dict[str, Any]:
        """Generate standard creature with moderate detail."""
        if request.creature_type and "humanoid" in request.creature_type.lower():
            # Create NPC with moderate detail
            npc_type = NPCType(
                name="Standard",
                role="standard",
                challenge_rating=request.target_cr
            )
            return await self.npc_creator.create_npc_from_concept(
                concept=f"A {request.creature_type} warrior",
                npc_type=npc_type,
                theme=request.theme
            )
        else:
            # Create monster with moderate detail
            template = MonsterTemplate(
                type=self._determine_monster_type(request),
                size=MonsterSize.MEDIUM,
                challenge_rating=request.target_cr,
                is_legendary=False,
                is_unique=False,
                role="standard"
            )
            return await self.monster_creator.create_monster_from_concept(
                concept=f"A {request.creature_type or 'creature'} warrior",
                template=template,
                theme=request.theme
            )

    async def _create_simplified_batch(self, base_creature: Dict[str, Any],
                                     request: BatchRequest) -> List[Dict[str, Any]]:
        """Create batch of simplified creatures with minor variations."""
        variations = []
        
        for i in range(request.count):
            variation = base_creature.copy()
            
            # Add minor variations based on variation_level
            if request.variation_level == "medium":
                variation["hp"] = int(variation["hp"] * (0.9 + (i * 0.2 / request.count)))
                variation["name"] = f"{base_creature['name']} {chr(65 + i)}"
            elif request.variation_level == "high":
                variation["hp"] = int(variation["hp"] * (0.8 + (i * 0.4 / request.count)))
                variation["ac"] = variation["ac"] + (-1 + (i % 3))
                variation["name"] = f"{base_creature['name']} {chr(65 + i)}"
            else:  # low variation
                variation["name"] = f"{base_creature['name']} #{i+1}"
            
            variations.append(variation)
        
        return variations

    async def _create_variations(self, base_creature: Dict[str, Any],
                               request: BatchRequest) -> List[Dict[str, Any]]:
        """Create variations of a base creature."""
        variations = []
        
        # Generate variations in parallel
        tasks = [
            self._create_variation(
                base_creature,
                request,
                variation_index=i
            )
            for i in range(request.count)
        ]
        variations = await asyncio.gather(*tasks)
        
        return variations

    async def _create_variation(self, base_creature: Dict[str, Any],
                              request: BatchRequest,
                              variation_index: int) -> Dict[str, Any]:
        """Create a single variation of a base creature."""
        variation = base_creature.copy()
        
        # Apply variations based on level
        if request.variation_level == "high":
            # Significant variations in abilities and features
            variation = await self._apply_high_variation(
                variation, request, variation_index
            )
        elif request.variation_level == "medium":
            # Moderate variations in stats and equipment
            variation = await self._apply_medium_variation(
                variation, request, variation_index
            )
        else:
            # Minor variations in appearance and names
            variation = await self._apply_low_variation(
                variation, request, variation_index
            )
        
        return variation

    async def _apply_high_variation(self, creature: Dict[str, Any],
                                  request: BatchRequest,
                                  index: int) -> Dict[str, Any]:
        """Apply significant variations to creature."""
        # Vary core stats within CR bounds
        cr_mod = 0.2  # Allow 20% CR variation
        creature["hp"] = int(creature["hp"] * (0.9 + (index * cr_mod)))
        creature["ac"] = creature["ac"] + (-2 + (index % 5))
        
        # Add unique abilities
        if "special_abilities" not in creature:
            creature["special_abilities"] = []
        creature["special_abilities"].append(
            await self._generate_unique_ability(creature, request)
        )
        
        # Vary equipment if humanoid
        if creature.get("equipment"):
            creature["equipment"] = await self._vary_equipment(
                creature["equipment"], request.theme
            )
        
        return creature

    async def _apply_medium_variation(self, creature: Dict[str, Any],
                                    request: BatchRequest,
                                    index: int) -> Dict[str, Any]:
        """Apply moderate variations to creature."""
        # Vary stats slightly
        cr_mod = 0.1  # Allow 10% CR variation
        creature["hp"] = int(creature["hp"] * (0.95 + (index * cr_mod)))
        creature["ac"] = creature["ac"] + (-1 + (index % 3))
        
        # Vary equipment if humanoid
        if creature.get("equipment"):
            creature["equipment"] = await self._vary_equipment(
                creature["equipment"], request.theme
            )
        
        return creature

    async def _apply_low_variation(self, creature: Dict[str, Any],
                                 request: BatchRequest,
                                 index: int) -> Dict[str, Any]:
        """Apply minor variations to creature."""
        # Just vary names and descriptions
        creature["name"] = f"{creature['name']} {chr(65 + index)}"
        if creature.get("description"):
            creature["description"] = await self._vary_description(
                creature["description"], index
            )
        
        return creature

    async def _generate_boss_concept(self, request: BatchRequest) -> str:
        """Generate detailed concept for boss creature."""
        prompt = f"""Generate a boss character concept. Return ONLY JSON:

        TARGET CR: {request.target_cr}
        TYPE: {request.creature_type or 'any'}
        THEME: {request.theme or 'standard fantasy'}

        Generate a concept that:
        1. Is appropriate for a boss encounter
        2. Has clear motivation and goals
        3. Includes distinctive features
        4. Fits the theme and type

        Return JSON with concept details."""

        concept_data = await self.theme_manager.generate_with_llm(prompt)
        return concept_data.get("concept", f"A powerful {request.creature_type or 'creature'} leader")

    def _determine_monster_type(self, request: BatchRequest) -> MonsterType:
        """Determine appropriate monster type from request."""
        type_str = request.creature_type or "monstrosity"
        try:
            return MonsterType[type_str.upper()]
        except KeyError:
            return MonsterType.MONSTROSITY

    async def _generate_unique_ability(self, creature: Dict[str, Any],
                                     request: BatchRequest) -> Dict[str, Any]:
        """Generate a unique ability appropriate for the creature."""
        prompt = f"""Generate a unique ability for this creature. Return ONLY JSON:

        CREATURE: {creature.get('name', 'Unknown')}
        CR: {request.target_cr}
        ROLE: {request.role.value}
        THEME: {request.theme or 'standard fantasy'}

        Generate an ability that:
        1. Fits the creature's theme and role
        2. Is balanced for the CR
        3. Provides tactical options
        4. Is distinct from standard abilities

        Return JSON with ability details."""

        ability_data = await self.theme_manager.generate_with_llm(prompt)
        return ability_data

    async def _vary_equipment(self, base_equipment: List[Dict[str, Any]],
                            theme: Optional[str]) -> List[Dict[str, Any]]:
        """Create variation of equipment while maintaining theme."""
        varied = base_equipment.copy()
        
        # Modify a random piece of equipment
        if varied and len(varied) > 0:
            import random
            idx = random.randint(0, len(varied) - 1)
            item = varied[idx]
            
            if theme:
                varied[idx] = await self.theme_manager.theme_item(item, theme)
            else:
                # Add minor variation to name
                item["name"] = f"Variant {item['name']}"
        
        return varied

    async def _vary_description(self, base_description: str,
                              index: int) -> str:
        """Create variation of description."""
        # Add minor variations to appearance
        variations = [
            "taller", "shorter", "broader", "leaner", "darker", "lighter",
            "more scarred", "less scarred", "more armored", "less armored"
        ]
        variation = variations[index % len(variations)]
        
        return f"{base_description} This one is {variation} than the others."
