"""Dependency injection package."""
from character_service.di.container import setup_di, setup_test_di

__all__ = [
    "setup_di",
    "setup_test_di",
]
