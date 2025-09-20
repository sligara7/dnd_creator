"""Service dependencies."""
from typing import Optional

from fastapi import Depends, Request

from character_service.di.container import setup_di
from character_service.domain.messages import MessagePublisher
from character_service.services.interfaces import (
    CharacterService,
    InventoryService,
    JournalService
)
from character_service.services.theme_service import ThemeService


_container = None


def get_container(request: Request = None):
    """Get DI container singleton."""
    global _container
    if not _container:
        _container = setup_di()
    return _container


def get_message_publisher(container=Depends(get_container)) -> MessagePublisher:
    """Get message publisher dependency."""
    return container.resolve(MessagePublisher)


def get_character_service(container=Depends(get_container)) -> CharacterService:
    """Get character service dependency."""
    return container.resolve(CharacterService)


def get_inventory_service(container=Depends(get_container)) -> InventoryService:
    """Get inventory service dependency."""
    return container.resolve(InventoryService)


def get_journal_service(container=Depends(get_container)) -> JournalService:
    """Get journal service dependency."""
    return container.resolve(JournalService)


def get_theme_service(container=Depends(get_container)) -> ThemeService:
    """Get theme service dependency."""
    return container.resolve(ThemeService)
