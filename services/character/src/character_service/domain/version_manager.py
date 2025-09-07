"""Stub for VersionManager to allow tests to run."""

class VersionManager:
    def __init__(self):
        pass

    async def apply_changes(self, character_id, state_data, base_version=None):
        # Dummy implementation for testing
        class DummyVersion:
            version = 1
        return DummyVersion(), False

    async def create_version(self, character, parent_version=None):
        class DummyVersion:
            version = 1
        return DummyVersion()
