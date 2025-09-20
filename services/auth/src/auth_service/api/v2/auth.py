"""Authentication API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr


from auth_service.core.database import get_db
from auth_service.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    TokenError,
    ValidationError
)
from auth_service.services.authentication import AuthenticationService
from auth_service.services.authorization import AuthorizationService


router = APIRouter(prefix="/api/v2/auth", tags=["Authentication"])


# Request/Response Models
class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str
    device_id: Optional[str] = None


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 900  # 15 minutes


class RefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class ValidationRequest(BaseModel):
    """Token validation request."""
    token: str
    permissions: Optional[list[str]] = None
    roles: Optional[list[str]] = None


class ValidationResponse(BaseModel):
    """Token validation response."""
    valid: bool
    user_id: Optional[str] = None
    username: Optional[str] = None
    permissions: Optional[list[str]] = None
    roles: Optional[list[str]] = None


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation."""
    reset_token: str
    new_password: str


# Helper functions
def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Get user agent from request."""
    return request.headers.get("User-Agent", "unknown")


# API Endpoints
@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
) -> LoginResponse:
    """
    Authenticate user and create session.
    
    Args:
        request: Login credentials
        req: FastAPI request object
        db: Database session
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthenticationService(db)
    
    try:
        access_token, refresh_token, session = await auth_service.login(
            username=request.username,
            password=request.password,
            ip_address=get_client_ip(req),
            user_agent=get_user_agent(req),
            device_id=request.device_id
        )
        
        await db.commit()
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/logout")
async def logout(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Logout user and invalidate session.
    
    Args:
        authorization: Authorization header with bearer token
        db: Database session
        
    Returns:
        Success response
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    access_token = authorization.replace("Bearer ", "")
    auth_service = AuthenticationService(db)
    
    try:
        success = await auth_service.logout(access_token)
        await db.commit()
        
        if success:
            return JSONResponse(
                content={"message": "Logged out successfully"},
                status_code=status.HTTP_200_OK
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logout failed"
            )
            
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    request: RefreshRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Refresh access and refresh tokens.
    
    Args:
        request: Refresh token
        req: FastAPI request object
        db: Database session
        
    Returns:
        New access and refresh tokens
        
    Raises:
        HTTPException: If refresh fails
    """
    auth_service = AuthenticationService(db)
    
    try:
        access_token, refresh_token = await auth_service.refresh_tokens(
            refresh_token=request.refresh_token,
            ip_address=get_client_ip(req)
        )
        
        await db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/validate", response_model=ValidationResponse)
async def validate_token(
    request: ValidationRequest,
    db: AsyncSession = Depends(get_db)
) -> ValidationResponse:
    """
    Validate access token and check permissions.
    
    Args:
        request: Token and optional permission/role requirements
        db: Database session
        
    Returns:
        Validation result with user info
        
    Raises:
        HTTPException: If validation fails
    """
    auth_service = AuthenticationService(db)
    
    try:
        payload = await auth_service.validate_token(
            token=request.token,
            required_permissions=request.permissions,
            required_roles=request.roles
        )
        
        await db.commit()
        
        return ValidationResponse(
            valid=True,
            user_id=payload.get("sub"),
            username=payload.get("username"),
            permissions=payload.get("permissions"),
            roles=payload.get("roles")
        )
        
    except (TokenError, AuthorizationError) as e:
        return ValidationResponse(
            valid=False
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Validation failed"
        )


@router.post("/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Request password reset.
    
    Args:
        request: Email address
        req: FastAPI request object
        db: Database session
        
    Returns:
        Success response (always returns success for security)
    """
    auth_service = AuthenticationService(db)
    
    try:
        reset_token = await auth_service.initiate_password_reset(
            email=request.email,
            ip_address=get_client_ip(req)
        )
        
        await db.commit()
        
        # In production, send email with reset token
        # For now, just return success
        
        return JSONResponse(
            content={"message": "If the email exists, a reset link has been sent"},
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        await db.rollback()
        # Always return success for security
        return JSONResponse(
            content={"message": "If the email exists, a reset link has been sent"},
            status_code=status.HTTP_200_OK
        )


@router.post("/password-reset-confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    req: Request,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    """
    Confirm password reset with token.
    
    Args:
        request: Reset token and new password
        req: FastAPI request object
        db: Database session
        
    Returns:
        Success response
        
    Raises:
        HTTPException: If reset fails
    """
    auth_service = AuthenticationService(db)
    
    try:
        success = await auth_service.reset_password(
            reset_token=request.reset_token,
            new_password=request.new_password,
            ip_address=get_client_ip(req)
        )
        
        await db.commit()
        
        if success:
            return JSONResponse(
                content={"message": "Password reset successfully"},
                status_code=status.HTTP_200_OK
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset failed"
            )
            
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.get("/public-key")
async def get_public_key() -> JSONResponse:
    """
    Get JWT public key for external services.
    
    Returns:
        Public key in PEM format
    """
    from auth_service.security.jwt_service import JWTService
    
    jwt_service = JWTService()
    public_key = jwt_service.get_public_key_pem()
    
    return JSONResponse(
        content={"public_key": public_key},
        status_code=status.HTTP_200_OK
    )


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    """
    Health check endpoint.
    
    Args:
        db: Database session
        
    Returns:
        Health status
    """
    try:
        # Check database connection
        await db.execute("SELECT 1")
        
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "auth-service",
                "version": "2.0.0"
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "unhealthy",
                "service": "auth-service",
                "error": str(e)
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
