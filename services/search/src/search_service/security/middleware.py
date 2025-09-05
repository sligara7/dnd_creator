from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from search_service.security.security import SecurityService, SecurityError
from search_service.security.models import SecurityContext, AccessLevel


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for handling request security"""

    def __init__(
        self,
        app: ASGIApp,
        security_service: SecurityService,
    ):
        super().__init__(app)
        self.security_service = security_service
        
        # Skip security for these paths
        self.public_paths = {
            "/health/live",
            "/health/ready",
            "/health/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        }

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Handle request security"""
        # Skip security for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)

        # Get authorization token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return Response(
                status_code=401,
                content="Authorization header missing",
                media_type="text/plain",
            )

        try:
            # Extract token
            token = auth_header.split(" ")[1]

            # Verify token and get claims
            claims = self.security_service.verify_token(token)

            # Get user roles and permissions
            roles = self.security_service.get_user_roles(claims)
            permissions = self.security_service.get_user_permissions(roles)
            access_levels = self.security_service.get_user_access_levels(claims)

            # Create security context
            context = SecurityContext(
                user_id=claims.get("sub"),
                roles=list(roles),
                permissions=list(permissions),
                access_levels=list(access_levels),
                token_expires_at=claims.get("exp"),
            )

            # Add context to request state
            request.state.security_context = context

            # Add document access filter to request state
            request.state.access_filter = self.security_service.get_document_query_filter(
                access_levels=set(access_levels)
            )

            return await call_next(request)

        except (IndexError, SecurityError) as e:
            return Response(
                status_code=401,
                content=str(e),
                media_type="text/plain",
            )
        except Exception as e:
            return Response(
                status_code=500,
                content=str(e),
                media_type="text/plain",
            )


def add_security(
    app: FastAPI,
    security_service: SecurityService,
) -> None:
    """Add security middleware to FastAPI app"""
    app.add_middleware(
        SecurityMiddleware,
        security_service=security_service,
    )
