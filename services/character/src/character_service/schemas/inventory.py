"""Inventory schemas."""
from typing import Dict, List, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime

from character_service.domain.inventory import (
    ItemLocation,
    ItemType,
    AttunementState,
    EffectType,
    DurationType,
    ActivationType,
)


class BaseInventoryItem(BaseModel):
    """Base inventory item schema."""
    name: str
    item_type: ItemType
    location: Optional[ItemLocation] = None
    container_id: Optional[UUID4] = None
    quantity: Optional[int] = 1
    weight: Optional[float] = 0.0
    value: Optional[int] = 0
    description: Optional[str] = None
    metadata: Optional[Dict] = None


class InventoryItemCreate(BaseInventoryItem):
    """Create inventory item schema."""
    pass


class InventoryItemUpdate(BaseModel):
    """Update inventory item schema."""
    quantity: int


class InventoryItemResponse(BaseInventoryItem):
    """Response inventory item schema."""
    id: UUID4
    character_id: UUID4
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        orm_mode = True


class BaseContainer(BaseModel):
    """Base container schema."""
    name: str
    capacity: float
    capacity_type: str  # "weight" or "items"
    description: Optional[str] = None
    metadata: Optional[Dict] = None


class ContainerCreate(BaseContainer):
    """Create container schema."""
    pass


class ContainerUpdate(BaseModel):
    """Update container schema."""
    name: Optional[str] = None
    capacity: Optional[float] = None
    capacity_type: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict] = None


class ContainerResponse(BaseContainer):
    """Response container schema."""
    id: UUID4
    character_id: UUID4
    contents: Optional[List[InventoryItemResponse]] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        orm_mode = True


class BaseEffect(BaseModel):
    """Base item effect schema."""
    name: str
    description: str
    effect_type: EffectType
    duration_type: DurationType
    duration_value: Optional[int] = None
    activation_type: Optional[ActivationType] = None
    activation_cost: Optional[str] = None
    saving_throw: Optional[str] = None
    metadata: Optional[Dict] = None


class EffectCreate(BaseEffect):
    """Create effect schema."""
    pass


class EffectUpdate(BaseModel):
    """Update effect schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    effect_type: Optional[EffectType] = None
    duration_type: Optional[DurationType] = None
    duration_value: Optional[int] = None
    activation_type: Optional[ActivationType] = None
    activation_cost: Optional[str] = None
    saving_throw: Optional[str] = None
    metadata: Optional[Dict] = None


class EffectResponse(BaseEffect):
    """Response effect schema."""
    id: UUID4
    item_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        orm_mode = True


class BaseMagicItem(BaseModel):
    """Base magic item schema."""
    name: str
    description: str
    requires_attunement: bool = False
    max_charges: Optional[int] = None
    charges: Optional[int] = None
    recharge_type: Optional[str] = None
    recharge_amount: Optional[int] = None
    effects: List[EffectCreate] = []
    restrictions: Optional[str] = None
    metadata: Optional[Dict] = None


class MagicItemCreate(BaseMagicItem):
    """Create magic item schema."""
    pass


class MagicItemUpdate(BaseModel):
    """Update magic item schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    requires_attunement: Optional[bool] = None
    max_charges: Optional[int] = None
    charges: Optional[int] = None
    recharge_type: Optional[str] = None
    recharge_amount: Optional[int] = None
    effects: Optional[List[EffectCreate]] = None
    restrictions: Optional[str] = None
    metadata: Optional[Dict] = None


class MagicItemResponse(BaseMagicItem):
    """Response magic item schema."""
    id: UUID4
    character_id: UUID4
    effects: List[EffectResponse]
    attunement_state: AttunementState
    attunement_date: Optional[datetime] = None
    last_recharged: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    deleted_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        orm_mode = True


class CurrencyResponse(BaseModel):
    """Currency response schema."""
    cp: int = 0
    sp: int = 0
    ep: int = 0
    gp: int = 0
    pp: int = 0
