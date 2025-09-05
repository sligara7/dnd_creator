from datetime import datetime
from typing import Any, Dict, List, Optional


class AuthServiceError(Exception):
    """Base exception for Auth Service errors"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()


class AuthenticationError(AuthServiceError):
    """Authentication error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details,
        )


class AuthorizationError(AuthServiceError):
    """Authorization error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details,
        )


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials error"""

    def __init__(self, username: str):
        super().__init__(
            message="Invalid credentials",
            details={"username": username},
        )


class AccountLockedError(AuthenticationError):
    """Account locked error"""

    def __init__(self, username: str, unlock_time: datetime):
        super().__init__(
            message="Account is locked",
            details={
                "username": username,
                "unlock_time": unlock_time.isoformat(),
            },
        )


class MFARequiredError(AuthenticationError):
    """MFA required error"""

    def __init__(self, mfa_token: str):
        super().__init__(
            message="MFA verification required",
            details={"mfa_token": mfa_token},
        )


class InvalidMFACodeError(AuthenticationError):
    """Invalid MFA code error"""

    def __init__(self):
        super().__init__(message="Invalid MFA code")


class InvalidTokenError(AuthenticationError):
    """Invalid token error"""

    def __init__(self, reason: str):
        super().__init__(
            message="Invalid token",
            details={"reason": reason},
        )


class TokenExpiredError(AuthenticationError):
    """Token expired error"""

    def __init__(self):
        super().__init__(message="Token has expired")


class InsufficientPermissionsError(AuthorizationError):
    """Insufficient permissions error"""

    def __init__(self, required_permissions: List[str]):
        super().__init__(
            message="Insufficient permissions",
            details={"required_permissions": required_permissions},
        )


class InvalidRoleError(AuthorizationError):
    """Invalid role error"""

    def __init__(self, role: str):
        super().__init__(
            message=f"Invalid role: {role}",
            details={"role": role},
        )


class PasswordPolicyError(AuthServiceError):
    """Password policy error"""

    def __init__(self, policy_violations: List[str]):
        super().__init__(
            message="Password does not meet policy requirements",
            error_code="PASSWORD_POLICY_ERROR",
            status_code=400,
            details={"violations": policy_violations},
        )


class APIKeyError(AuthServiceError):
    """API key error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="API_KEY_ERROR",
            status_code=401,
            details=details,
        )


class SessionError(AuthServiceError):
    """Session error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="SESSION_ERROR",
            status_code=401,
            details=details,
        )


class KeyGenerationError(AuthServiceError):
    """Key generation error"""

    def __init__(self, message: str):
        super().__init__(
            message=f"Failed to generate keys: {message}",
            error_code="KEY_GENERATION_ERROR",
            status_code=500,
        )
