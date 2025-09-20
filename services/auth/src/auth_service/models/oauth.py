"""API models for external identity providers."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ProviderType(str, Enum):
    """Supported identity provider types."""
    
    OIDC = "oidc"
    OAUTH2 = "oauth2"
    SAML = "saml"


class OAuthConfig(BaseModel):
    """OAuth2/OIDC provider configuration."""
    
    provider_id: str = Field(..., description="Provider identifier")
    display_name: str = Field(..., description="Provider display name")
    provider_type: ProviderType = Field(..., description="Provider type")
    authorization_url: HttpUrl = Field(..., description="OAuth2 authorization URL")
    token_url: HttpUrl = Field(..., description="OAuth2 token URL")
    userinfo_url: Optional[HttpUrl] = Field(None, description="OIDC userinfo URL")
    jwks_url: Optional[HttpUrl] = Field(None, description="OIDC JWKS URL")
    client_id: str = Field(..., description="OAuth2 client ID")
    scopes: List[str] = Field(default_factory=list, description="Required scopes")
    is_enabled: bool = Field(default=True, description="Provider is enabled")
    is_deleted: bool = Field(default=False, description="Provider is deleted")
    deleted_at: Optional[datetime] = Field(None, description="Deletion timestamp")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OAuthConfigCreate(BaseModel):
    """OAuth2/OIDC provider creation model."""
    
    provider_id: str = Field(..., description="Provider identifier")
    display_name: str = Field(..., description="Provider display name")
    provider_type: ProviderType = Field(..., description="Provider type")
    authorization_url: HttpUrl = Field(..., description="OAuth2 authorization URL")
    token_url: HttpUrl = Field(..., description="OAuth2 token URL")
    userinfo_url: Optional[HttpUrl] = Field(None, description="OIDC userinfo URL")
    jwks_url: Optional[HttpUrl] = Field(None, description="OIDC JWKS URL")
    client_id: str = Field(..., description="OAuth2 client ID")
    client_secret: str = Field(..., description="OAuth2 client secret")
    scopes: List[str] = Field(default_factory=list, description="Required scopes")


class OAuthConfigUpdate(BaseModel):
    """OAuth2/OIDC provider update model."""
    
    display_name: Optional[str] = None
    authorization_url: Optional[HttpUrl] = None
    token_url: Optional[HttpUrl] = None
    userinfo_url: Optional[HttpUrl] = None
    jwks_url: Optional[HttpUrl] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    scopes: Optional[List[str]] = None
    is_enabled: Optional[bool] = None


class ProviderLoginResponse(BaseModel):
    """OAuth2/OIDC login response."""
    
    access_token: str = Field(..., description="Auth service access token")
    refresh_token: str = Field(..., description="Auth service refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(default=900, description="Token lifetime in seconds")
    provider_id: str = Field(..., description="Identity provider ID")
    provider_user_id: str = Field(..., description="Provider's user ID")
    email: Optional[str] = Field(None, description="User email from provider")
    provider_access_token: Optional[str] = Field(None, description="Provider's access token")


class ProviderAccount(BaseModel):
    """External provider account link."""
    
    id: UUID = Field(..., description="Account link ID")
    user_id: UUID = Field(..., description="Auth service user ID")
    provider_id: str = Field(..., description="Identity provider ID")
    provider_user_id: str = Field(..., description="Provider's user ID")
    provider_username: Optional[str] = Field(None, description="Provider's username")
    provider_email: Optional[str] = Field(None, description="Provider's email")
    metadata: Dict = Field(default_factory=dict, description="Provider metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)