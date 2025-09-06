"""Test magic item service."""
import uuid
import pytest
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from character_service.core.exceptions import (
    ValidationError,
    ResourceExhaustedError,
    StateError,
)
from character_service.services.magic_items import MagicItemService
from character_service.domain.inventory import (
    MagicItem,
    ItemEffect,
    AttunementState,
    EffectType,
    DurationType,
    ActivationType,
)


@pytest.fixture
async def magic_item_service(test_session: AsyncSession) -> MagicItemService:
    """Create a magic item service."""
    return MagicItemService(test_session)


@pytest.fixture
async def test_character():
    """Create test character data."""
    return {"id": uuid.uuid4()}


@pytest.fixture
async def test_magic_item(test_session, test_character):
    """Create test magic item data."""
    # Create magic item
    magic_item = MagicItem(
        character_id=test_character["id"],
        name="Staff of Healing",
        description="A magical staff that heals wounds",
        requires_attunement=True,
        max_charges=10,
        charges=10,
        recharge_type="dawn",
        recharge_amount=1,
        restrictions="Must be a spellcaster",
    )
    test_session.add(magic_item)

    # Create effects
    effects = [
        ItemEffect(
            item_id=magic_item.id,
            name="Cure Wounds",
            description="Heals target for 2d8+2",
            effect_type=EffectType.HEALING,
            duration_type=DurationType.INSTANTANEOUS,
            activation_type=ActivationType.ACTION,
            activation_cost="1 charge",
            saving_throw="None",
            metadata={"range": "touch"},
        ),
        ItemEffect(
            item_id=magic_item.id,
            name="Lesser Restoration",
            description="Removes one condition",
            effect_type=EffectType.HEALING,
            duration_type=DurationType.INSTANTANEOUS,
            activation_type=ActivationType.ACTION,
            activation_cost="2 charges",
            saving_throw="None",
            metadata={"range": "touch"},
        ),
    ]
    test_session.add_all(effects)
    await test_session.flush()

    magic_item.effects = effects
    return magic_item


async def test_get_magic_items(
    magic_item_service: MagicItemService,
    test_character,
    test_magic_item,
):
    """Test getting magic items."""
    # Get all items
    items = await magic_item_service.get_character_magic_items(
        character_id=test_character["id"],
    )
    assert len(items) == 1
    assert items[0].name == "Staff of Healing"
    assert len(items[0].effects) == 2


async def test_attunement_process(
    magic_item_service: MagicItemService,
    test_character,
    test_magic_item,
):
    """Test item attunement process."""
    # Begin attunement
    item = await magic_item_service.begin_attunement(
        character_id=test_character["id"],
        item_id=test_magic_item.id,
    )
    assert item.attunement_state == AttunementState.ATTUNING
    assert item.attunement_date is not None

    # Too early to complete
    with pytest.raises(StateError):
        await magic_item_service.complete_attunement(
            character_id=test_character["id"],
            item_id=test_magic_item.id,
        )

    # Simulate time passing
    item.attunement_date = datetime.utcnow().replace(
        hour=item.attunement_date.hour - 2,
    )

    # Complete attunement
    item = await magic_item_service.complete_attunement(
        character_id=test_character["id"],
        item_id=test_magic_item.id,
    )
    assert item.attunement_state == AttunementState.ATTUNED


async def test_charges(
    magic_item_service: MagicItemService,
    test_character,
    test_magic_item,
):
    """Test charge management."""
    # Use charges
    item = await magic_item_service.use_charges(
        character_id=test_character["id"],
        item_id=test_magic_item.id,
        charges=2,
    )
    assert item.charges == 8

    # Try to use too many charges
    with pytest.raises(StateError):
        await magic_item_service.use_charges(
            character_id=test_character["id"],
            item_id=test_magic_item.id,
            charges=10,
        )

    # Recharge item
    item = await magic_item_service.recharge_item(
        character_id=test_character["id"],
        item_id=test_magic_item.id,
        recharge_type="dawn",
    )
    assert item.charges == item.max_charges
    assert item.last_recharged is not None


async def test_attunement_limit(
    test_session,
    magic_item_service: MagicItemService,
    test_character,
):
    """Test attunement slot limit."""
    # Create max attuned items
    for i in range(3):
        item = MagicItem(
            character_id=test_character["id"],
            name=f"Item {i}",
            description="A magical item",
            requires_attunement=True,
            attunement_state=AttunementState.ATTUNED,
        )
        test_session.add(item)

    # Create one more item
    extra_item = MagicItem(
        character_id=test_character["id"],
        name="Extra Item",
        description="Another magical item",
        requires_attunement=True,
    )
    test_session.add(extra_item)
    await test_session.flush()

    # Try to attune beyond limit
    with pytest.raises(ResourceExhaustedError):
        await magic_item_service.begin_attunement(
            character_id=test_character["id"],
            item_id=extra_item.id,
        )


async def test_break_attunement(
    magic_item_service: MagicItemService,
    test_character,
    test_magic_item,
):
    """Test breaking attunement."""
    # Begin and complete attunement
    item = await magic_item_service.begin_attunement(
        character_id=test_character["id"],
        item_id=test_magic_item.id,
    )
    item.attunement_date = datetime.utcnow().replace(hour=item.attunement_date.hour - 2)
    item = await magic_item_service.complete_attunement(
        character_id=test_character["id"],
        item_id=test_magic_item.id,
    )

    # Break attunement
    item = await magic_item_service.break_attunement(
        character_id=test_character["id"],
        item_id=test_magic_item.id,
    )
    assert item.attunement_state == AttunementState.BROKEN
    assert item.attunement_date is None


async def test_daily_recharge_limit(
    magic_item_service: MagicItemService,
    test_character,
    test_magic_item,
):
    """Test daily recharge limit."""
    # Use charges
    item = await magic_item_service.use_charges(
        character_id=test_character["id"],
        item_id=test_magic_item.id,
        charges=5,
    )

    # Recharge item
    item = await magic_item_service.recharge_item(
        character_id=test_character["id"],
        item_id=test_magic_item.id,
        recharge_type="daily",
    )

    # Try to recharge again
    with pytest.raises(StateError):
        await magic_item_service.recharge_item(
            character_id=test_character["id"],
            item_id=test_magic_item.id,
            recharge_type="daily",
        )
