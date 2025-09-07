"""JWT service for token generation and validation."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
from uuid import UUID

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from auth_service.core.config import settings
from auth_service.core.exceptions import AuthenticationError, TokenError


class JWTService:
    """Service for JWT token operations using RS256."""
    
    def __init__(self):
        """Initialize JWT service with RSA keys."""
        self.algorithm = "RS256"
        self.issuer = settings.JWT_ISSUER
        self.audience = settings.JWT_AUDIENCE
        
        # Token expiration times
        self.access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Load or generate RSA keys
        self._load_or_generate_keys()
        
        # Token blacklist (in production, use Redis)
        self._blacklist = set()
    
    def _load_or_generate_keys(self) -> None:
        """Load existing RSA keys or generate new ones."""
        try:
            # Try to load existing keys
            with open(settings.JWT_PRIVATE_KEY_PATH, "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            
            with open(settings.JWT_PUBLIC_KEY_PATH, "rb") as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
        except FileNotFoundError:
            # Generate new RSA key pair
            self._generate_keys()
    
    def _generate_keys(self) -> None:
        """Generate new RSA key pair."""
        # Generate private key
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Get public key
        self.public_key = self.private_key.public_key()
        
        # Save keys to files
        self._save_keys()
    
    def _save_keys(self) -> None:
        """Save RSA keys to files."""
        # Save private key
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        with open(settings.JWT_PRIVATE_KEY_PATH, "wb") as f:
            f.write(private_pem)
        
        # Save public key
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(settings.JWT_PUBLIC_KEY_PATH, "wb") as f:
            f.write(public_pem)
    
    def generate_access_token(
        self,
        user_id: UUID,
        username: str,
        roles: list[str],
        permissions: list[str],
        session_id: Optional[UUID] = None,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate an access token.
        
        Args:
            user_id: User's UUID
            username: User's username
            roles: User's roles
            permissions: User's permissions
            session_id: Optional session ID
            additional_claims: Additional JWT claims
            
        Returns:
            JWT access token string
        """
        now = datetime.now(timezone.utc)
        expire = now + self.access_token_expire
        
        payload = {
            "sub": str(user_id),  # Subject
            "username": username,
            "roles": roles,
            "permissions": permissions,
            "type": "access",
            "iat": now,
            "exp": expire,
            "nbf": now,  # Not before
            "iss": self.issuer,
            "aud": self.audience,
            "jti": str(UUID.uuid4()),  # JWT ID for tracking
        }
        
        if session_id:
            payload["session_id"] = str(session_id)
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)
    
    def generate_refresh_token(
        self,
        user_id: UUID,
        session_id: UUID,
        device_id: Optional[str] = None
    ) -> str:
        """
        Generate a refresh token.
        
        Args:
            user_id: User's UUID
            session_id: Session ID
            device_id: Optional device identifier
            
        Returns:
            JWT refresh token string
        """
        now = datetime.now(timezone.utc)
        expire = now + self.refresh_token_expire
        
        payload = {
            "sub": str(user_id),
            "session_id": str(session_id),
            "type": "refresh",
            "iat": now,
            "exp": expire,
            "nbf": now,
            "iss": self.issuer,
            "aud": self.audience,
            "jti": str(UUID.uuid4()),
        }
        
        if device_id:
            payload["device_id"] = device_id
        
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)
    
    def verify_token(
        self,
        token: str,
        token_type: str = "access",
        verify_exp: bool = True
    ) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            token_type: Expected token type (access/refresh)
            verify_exp: Whether to verify expiration
            
        Returns:
            Decoded token payload
            
        Raises:
            TokenError: If token is invalid
        """
        try:
            # Check if token is blacklisted
            if self._is_blacklisted(token):
                raise TokenError("Token has been revoked")
            
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
                options={"verify_exp": verify_exp}
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                raise TokenError(f"Invalid token type. Expected {token_type}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise TokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise TokenError(f"Invalid token: {str(e)}")
    
    def refresh_access_token(
        self,
        refresh_token: str
    ) -> Tuple[str, str]:
        """
        Generate new access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Tuple of (new_access_token, new_refresh_token)
            
        Raises:
            TokenError: If refresh token is invalid
        """
        # Verify refresh token
        payload = self.verify_token(refresh_token, token_type="refresh")
        
        # Generate new tokens
        # Note: In production, fetch user data from database
        user_id = UUID(payload["sub"])
        session_id = UUID(payload["session_id"])
        
        # This would be fetched from database
        username = "fetched_username"
        roles = ["fetched_roles"]
        permissions = ["fetched_permissions"]
        
        new_access_token = self.generate_access_token(
            user_id=user_id,
            username=username,
            roles=roles,
            permissions=permissions,
            session_id=session_id
        )
        
        new_refresh_token = self.generate_refresh_token(
            user_id=user_id,
            session_id=session_id,
            device_id=payload.get("device_id")
        )
        
        # Revoke old refresh token
        self.revoke_token(refresh_token)
        
        return new_access_token, new_refresh_token
    
    def revoke_token(self, token: str) -> None:
        """
        Revoke a token by adding it to blacklist.
        
        Args:
            token: Token to revoke
        """
        try:
            # Decode to get JTI
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False, "verify_signature": True}
            )
            jti = payload.get("jti")
            if jti:
                self._blacklist.add(jti)
        except jwt.InvalidTokenError:
            # If we can't decode it, add the whole token
            self._blacklist.add(token)
    
    def _is_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted.
        
        Args:
            token: Token to check
            
        Returns:
            True if blacklisted, False otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False, "verify_signature": True}
            )
            jti = payload.get("jti")
            return jti in self._blacklist if jti else token in self._blacklist
        except jwt.InvalidTokenError:
            return token in self._blacklist
    
    def generate_api_key_token(
        self,
        api_key_id: UUID,
        user_id: UUID,
        key_name: str,
        scopes: list[str]
    ) -> str:
        """
        Generate a token for API key authentication.
        
        Args:
            api_key_id: API key UUID
            user_id: User's UUID
            key_name: Name of the API key
            scopes: API key scopes/permissions
            
        Returns:
            JWT token for API key
        """
        # API keys don't expire via JWT (managed in database)
        payload = {
            "sub": str(user_id),
            "api_key_id": str(api_key_id),
            "key_name": key_name,
            "scopes": scopes,
            "type": "api_key",
            "iat": datetime.now(timezone.utc),
            "iss": self.issuer,
            "aud": self.audience,
        }
        
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)
    
    def get_public_key_pem(self) -> str:
        """
        Get public key in PEM format for external services.
        
        Returns:
            Public key as PEM string
        """
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
    
    def rotate_keys(self) -> None:
        """Rotate RSA keys (generate new key pair)."""
        # Save old keys for grace period
        old_public = self.public_key
        old_private = self.private_key
        
        # Generate new keys
        self._generate_keys()
        
        # In production, keep old keys for a grace period
        # to validate existing tokens
