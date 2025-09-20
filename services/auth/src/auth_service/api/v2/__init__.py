"""Version 2 of the Auth Service API."""

from fastapi import APIRouter

from auth_service.api.v2.auth import router as auth_router
from auth_service.api.v2.users import router as users_router
from auth_service.api.v2.roles import router as roles_router
from auth_service.api.v2.sessions import router as sessions_router
from auth_service.api.v2.permissions import router as permissions_router
from auth_service.api.v2.audit import router as audit_router
from auth_service.api.v2.providers import router as providers_router


router = APIRouter(tags=["Auth Service v2"])

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(roles_router)
router.include_router(sessions_router)
router.include_router(permissions_router)
router.include_router(audit_router)
router.include_router(providers_router)
