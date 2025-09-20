"""Storage models for external identity providers."""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    String,
    Table,
    UniqueConstraint,
    func,
    text
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from auth_service.models.oauth import ProviderType
from auth_service.storage.base import Base, gen_uuid


# OAuth2/OIDC providers
oauth_providers = Table(
    "oauth_providers",
    Base.metadata,
    Column("id", UUID, primary_key=True, default=gen_uuid),
    Column("provider_id", String, nullable=False, unique=True),
    Column("display_name", String, nullable=False),
    Column("provider_type", SQLEnum(ProviderType), nullable=False),
    Column("authorization_url", String, nullable=False),
    Column("token_url", String, nullable=False),
    Column("userinfo_url", String),
    Column("jwks_url", String),
    Column("client_id", String, nullable=False),
    Column("client_secret_hash", String, nullable=False),
    Column("scopes", String),
    Column("is_enabled", Boolean, nullable=False, default=True),
    Column("is_deleted", Boolean, nullable=False, default=False),
    Column("deleted_at", DateTime),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column("updated_at", DateTime, nullable=False, server_default=func.now(),
           onupdate=func.now()),
    
    Index("idx_oauth_providers_id", "id"),
    Index("idx_oauth_providers_provider_id", "provider_id"),
    Index("idx_oauth_providers_enabled", "is_enabled"),
)


# External account links
provider_accounts = Table(
    "provider_accounts",
    Base.metadata,
    Column("id", UUID, primary_key=True, default=gen_uuid),
    Column("user_id", UUID, ForeignKey("users.id"), nullable=False),
    Column("provider_id", String, ForeignKey("oauth_providers.provider_id"),
           nullable=False),
    Column("provider_user_id", String, nullable=False),
    Column("provider_username", String),
    Column("provider_email", String),
    Column("metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    Column("created_at", DateTime, nullable=False, server_default=func.now()),
    Column("updated_at", DateTime, nullable=False, server_default=func.now(),
           onupdate=func.now()),
    
    UniqueConstraint("provider_id", "provider_user_id",
                    name="uq_provider_accounts_provider_user"),
    Index("idx_provider_accounts_user_id", "user_id"),
    Index("idx_provider_accounts_provider", "provider_id"),
)