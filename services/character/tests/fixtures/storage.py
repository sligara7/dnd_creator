"""Storage adapter fixtures for tests."""

import pytest

from character_service.storage.storage_adapter import StorageAdapter
from tests.utils.storage_mock import MockStorageAdapter


@pytest.fixture
def storage() -> StorageAdapter:
    """Get a mock storage adapter for tests."""
    return MockStorageAdapter()