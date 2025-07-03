"""
Basic test to verify the modular backend structure works correctly.
"""
import sys
import pytest
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_import_structure():
    """Test that all core modules can be imported successfully."""
    # Test core imports
    from src.core.config import Settings
    from src.core.enums import CreationOptions
    
    # Test model imports
    from src.models.character_models import CharacterCore
    from src.models.database_models import CharacterDB
    
    # Test service imports
    from src.services.creation_factory import CreationFactory
    
    # Basic instantiation tests
    settings = Settings()
    assert settings.api_title == "D&D Character Creator API"
    
    # Test enum access
    assert hasattr(CreationOptions, 'CHARACTER')


def test_app_initialization():
    """Test that the FastAPI app can be imported and initialized."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from app import app
    assert app is not None
    assert app.title == "D&D Character Creator API"


if __name__ == "__main__":
    pytest.main([__file__])
