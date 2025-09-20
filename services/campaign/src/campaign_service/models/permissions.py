"""Campaign permission models."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from campaign_service.services.permissions import PermissionType
from campaign_service.models.base import Base


class CampaignPermission(Base):
    """Campaign permission model."""
    __tablename__ = "campaign_permissions"
    __table_args__ = (
        UniqueConstraint(
            "campaign_id",
            "user_id",
            "permission_type",
            name="uix_campaign_permission",
        ),
    )
    
    # Model fields
    campaign_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    permission_type = Column(
        Enum(PermissionType),
        nullable=False,
    )
    granted_by = Column(
        PGUUID(as_uuid=True),
        nullable=False,
    )
    granted_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )