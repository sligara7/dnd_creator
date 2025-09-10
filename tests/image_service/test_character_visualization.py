"""
Tests for character visualization functionality.
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime
import base64
import json
from typing import Dict, Any

from image_service.models.character import (
    CharacterPortraitRequest,
    PortraitMetadata,
    CharacterClass,
    CharacterRace,
    EquipmentVisuals,
    ThemeStyle,
    PortraitSize,
    NPCType,
    MonsterType
)
from image_service.core.portrait_generator import PortraitGenerator
from image_service.services.image_service import ImageService

@pytest.fixture
def test_portrait_metadata() -> PortraitMetadata:
    """Create test portrait metadata."""
    return PortraitMetadata(
        width=512,
        height=512,
        character_id=uuid4(),
        character_name="Test Character",
        character_class=CharacterClass.FIGHTER,
        character_race=CharacterRace.HUMAN,
        equipment=EquipmentVisuals(
            armor="plate",
            weapon="longsword",
            shield=None,
            accessories=["cloak"]
        ),
        theme=ThemeStyle(
            art_style="realistic",
            color_scheme="dark",
            mood="heroic"
        )
    )

@pytest.fixture
def test_portrait_request(test_portrait_metadata: PortraitMetadata) -> CharacterPortraitRequest:
    """Create test portrait request."""
    return CharacterPortraitRequest(
        size=PortraitSize.MEDIUM,
        metadata=test_portrait_metadata,
        background_style="neutral",
        pose="standing",
        expression="neutral",
        lighting="dramatic"
    )

@pytest.fixture
def mock_portrait_data() -> bytes:
    """Generate mock portrait image data."""
    # Create a small test pattern
    data = bytearray()
    for i in range(64):
        for j in range(64):
            # Create a simple gradient pattern
            data.append((i + j) % 256)
    return bytes(data)

@pytest.mark.asyncio
class TestCharacterVisualization:
    async def test_portrait_generation(
        self,
        image_service: ImageService,
        mock_getimg_api,
        test_portrait_request: CharacterPortraitRequest,
        mock_portrait_data: bytes
    ):
        """Test basic character portrait generation."""
        # Setup mock response
        mock_getimg_api.generate_image.return_value = {
            "url": "http://mock.api/image.png",
            "data": base64.b64encode(mock_portrait_data).decode(),
            "metadata": {
                "width": 512,
                "height": 512,
                "style": "realistic",
                "prompt": "human fighter in plate armor"
            }
        }

        # Generate portrait
        image_id = await image_service.generate_character_portrait(test_portrait_request)

        # Verify generation
        assert image_id is not None
        mock_getimg_api.generate_image.assert_called_once()

        # Verify portrait was stored
        image = await image_service.get_image_metadata(image_id)
        assert image is not None
        assert image.metadata.width == 512
        assert image.metadata.height == 512
        assert test_portrait_request.metadata.character_id in image.tags.values()

    async def test_npc_visualization(
        self,
        image_service: ImageService,
        mock_getimg_api,
        test_portrait_metadata: PortraitMetadata
    ):
        """Test NPC portrait generation."""
        # Modify request for NPC
        npc_request = CharacterPortraitRequest(
            size=PortraitSize.SMALL,
            metadata=test_portrait_metadata.copy(update={
                "npc_type": NPCType.MERCHANT,
                "character_name": "Test NPC",
                "equipment": EquipmentVisuals(
                    armor="clothing",
                    weapon=None,
                    accessories=["coin_purse", "ledger"]
                )
            }),
            background_style="indoor",
            pose="sitting",
            expression="friendly",
            lighting="soft"
        )

        # Setup mock response
        mock_getimg_api.generate_image.return_value = {
            "url": "http://mock.api/npc.png",
            "data": base64.b64encode(bytes(32 * 32)).decode(),
            "metadata": {
                "width": 256,
                "height": 256,
                "style": "realistic",
                "prompt": "merchant npc"
            }
        }

        # Generate NPC portrait
        image_id = await image_service.generate_character_portrait(npc_request)
        assert image_id is not None

        # Verify NPC-specific generation
        call_args = mock_getimg_api.generate_image.call_args[1]
        assert "merchant" in call_args["prompt"].lower()
        assert call_args["style"] == npc_request.metadata.theme.art_style

    async def test_monster_image_generation(
        self,
        image_service: ImageService,
        mock_getimg_api
    ):
        """Test monster visualization."""
        monster_request = CharacterPortraitRequest(
            size=PortraitSize.LARGE,
            metadata=PortraitMetadata(
                width=1024,
                height=1024,
                character_id=uuid4(),
                character_name="Ancient Red Dragon",
                monster_type=MonsterType.DRAGON,
                theme=ThemeStyle(
                    art_style="realistic",
                    color_scheme="dark",
                    mood="threatening"
                )
            ),
            background_style="lair",
            pose="flying",
            expression="threatening",
            lighting="dark"
        )

        # Setup mock response
        mock_getimg_api.generate_image.return_value = {
            "url": "http://mock.api/dragon.png",
            "data": base64.b64encode(bytes(128 * 128)).decode(),
            "metadata": {
                "width": 1024,
                "height": 1024,
                "style": "realistic",
                "prompt": "ancient red dragon"
            }
        }

        # Generate monster image
        image_id = await image_service.generate_character_portrait(monster_request)
        assert image_id is not None

        # Verify monster-specific details
        call_args = mock_getimg_api.generate_image.call_args[1]
        assert "dragon" in call_args["prompt"].lower()
        assert call_args["width"] == 1024
        assert call_args["height"] == 1024

    async def test_equipment_visualization(
        self,
        image_service: ImageService,
        mock_getimg_api,
        test_portrait_metadata: PortraitMetadata
    ):
        """Test equipment rendering in portraits."""
        # Create request with detailed equipment
        equipment_request = CharacterPortraitRequest(
            size=PortraitSize.MEDIUM,
            metadata=test_portrait_metadata.copy(update={
                "equipment": EquipmentVisuals(
                    armor="ornate plate armor",
                    weapon="flaming longsword",
                    shield="tower shield",
                    accessories=[
                        "magical cloak",
                        "glowing amulet",
                        "enchanted boots"
                    ]
                )
            }),
            background_style="magical",
            pose="dynamic",
            expression="determined",
            lighting="magical"
        )

        # Setup mock response
        mock_getimg_api.generate_image.return_value = {
            "url": "http://mock.api/equipped.png",
            "data": base64.b64encode(bytes(64 * 64)).decode(),
            "metadata": {
                "width": 512,
                "height": 512,
                "style": "realistic",
                "prompt": "warrior with magical equipment"
            }
        }

        # Generate equipped portrait
        image_id = await image_service.generate_character_portrait(equipment_request)
        assert image_id is not None

        # Verify equipment details in prompt
        call_args = mock_getimg_api.generate_image.call_args[1]
        prompt = call_args["prompt"].lower()
        assert "plate armor" in prompt
        assert "longsword" in prompt
        assert "shield" in prompt
        assert "cloak" in prompt
        assert "amulet" in prompt
        assert "boots" in prompt

    async def test_theme_style_application(
        self,
        image_service: ImageService,
        mock_getimg_api,
        test_portrait_metadata: PortraitMetadata
    ):
        """Test theme-based visual styling."""
        # Create requests with different themes
        theme_requests = [
            CharacterPortraitRequest(
                size=PortraitSize.MEDIUM,
                metadata=test_portrait_metadata.copy(update={
                    "theme": ThemeStyle(
                        art_style=style,
                        color_scheme=scheme,
                        mood=mood
                    )
                }),
                background_style=bg_style,
                pose="standing",
                expression="neutral",
                lighting=lighting
            )
            for style, scheme, mood, bg_style, lighting in [
                ("anime", "vibrant", "heroic", "action", "dramatic"),
                ("painterly", "muted", "mysterious", "misty", "moody"),
                ("pixel_art", "retro", "adventurous", "dungeon", "torchlit"),
                ("comic", "bold", "dynamic", "city", "daylight")
            ]
        ]

        # Setup mock responses
        mock_getimg_api.generate_image.side_effect = [
            {
                "url": f"http://mock.api/theme_{i}.png",
                "data": base64.b64encode(bytes(64 * 64)).decode(),
                "metadata": {
                    "width": 512,
                    "height": 512,
                    "style": request.metadata.theme.art_style,
                    "prompt": f"character in {request.metadata.theme.art_style} style"
                }
            }
            for i, request in enumerate(theme_requests)
        ]

        # Generate and verify each themed portrait
        for request in theme_requests:
            # Generate portrait
            image_id = await image_service.generate_character_portrait(request)
            assert image_id is not None

            # Verify theme details in generation
            call_args = mock_getimg_api.generate_image.call_args[1]
            assert request.metadata.theme.art_style in call_args["style"]
            assert request.metadata.theme.mood.lower() in call_args["prompt"].lower()
            assert request.lighting in call_args["prompt"].lower()

            # Verify metadata preservation
            image = await image_service.get_image_metadata(image_id)
            assert image is not None
            assert "theme" in image.tags
            assert json.loads(image.tags["theme"])["art_style"] == request.metadata.theme.art_style

    async def test_portrait_batch_generation(
        self,
        image_service: ImageService,
        mock_getimg_api,
        test_portrait_metadata: PortraitMetadata
    ):
        """Test batch portrait generation for multiple characters."""
        # Create batch of requests
        batch_requests = [
            CharacterPortraitRequest(
                size=PortraitSize.MEDIUM,
                metadata=test_portrait_metadata.copy(update={
                    "character_id": uuid4(),
                    "character_name": f"Character {i}",
                    "character_class": class_type
                }),
                background_style="neutral",
                pose="standing",
                expression="neutral",
                lighting="dramatic"
            )
            for i, class_type in enumerate([
                CharacterClass.FIGHTER,
                CharacterClass.WIZARD,
                CharacterClass.ROGUE,
                CharacterClass.CLERIC
            ])
        ]

        # Setup mock responses
        mock_getimg_api.generate_image.side_effect = [
            {
                "url": f"http://mock.api/batch_{i}.png",
                "data": base64.b64encode(bytes(64 * 64)).decode(),
                "metadata": {
                    "width": 512,
                    "height": 512,
                    "style": "realistic",
                    "prompt": f"character portrait {i}"
                }
            }
            for i in range(len(batch_requests))
        ]

        # Generate batch of portraits
        image_ids = await image_service.generate_character_portraits(batch_requests)
        assert len(image_ids) == len(batch_requests)

        # Verify each generated portrait
        for request, image_id in zip(batch_requests, image_ids):
            image = await image_service.get_image_metadata(image_id)
            assert image is not None
            assert str(request.metadata.character_id) in image.tags.values()
            assert request.metadata.character_name in image.tags.values()
