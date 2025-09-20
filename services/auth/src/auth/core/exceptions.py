"""Auth service exceptions."""


class AuthError(Exception):
    """Base class for auth service exceptions."""


class StorageError(AuthError):
    """Error interfacing with storage service."""


class DatabaseError(AuthError):
    """Database error."""


class ValidationError(AuthError):
    """Validation error."""


class AuthenticationError(AuthError):
    """Authentication error."""


class AuthorizationError(AuthError):
    """Authorization error."""


class UserNotFoundError(AuthError):
    """User not found error."""


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials error."""


class UserLockedError(AuthenticationError):
    """User account locked error."""


class TokenExpiredError(AuthenticationError):
    """Token expired error."""


class TokenInvalidError(AuthenticationError):
    """Token invalid error."""


class SessionExpiredError(AuthenticationError):
    """Session expired error."""


class SessionInvalidError(AuthenticationError):
    """Session invalid error."""


class RoleNotFoundError(AuthError):
    """Role not found error."""


class PermissionNotFoundError(AuthError):
    """Permission not found error."""


class ApiKeyNotFoundError(AuthError):
    """API key not found error."""