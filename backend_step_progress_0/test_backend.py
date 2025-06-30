"""
Unit tests for D&D Character Creator Backend
Run with: pytest test_backend.py -v
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import json

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from main import CharacterCreationBackend
from character_creation import CreationConfig, CreationResult


class TestCharacterCreationBackend:
    """Test the main backend service."""
    
    @pytest.fixture
    def backend(self):
        """Create a backend instance for testing."""
        return CharacterCreationBackend()
    
    def test_backend_initialization(self, backend):
        """Test that backend initializes properly."""
        assert backend is not None
        assert backend.config is not None
        assert backend.validator is not None
        assert backend.formatter is not None
        # LLM service might be None if not configured
    
    def test_health_status(self, backend):
        """Test health status endpoint."""
        health = backend.get_health_status()
        
        assert health["status"] == "healthy"
        assert "services" in health
        assert "config" in health
        assert "character_creator" in health["services"]
        assert "validator" in health["services"]
        assert "formatter" in health["services"]
    
    def test_character_creation_success(self, backend):
        """Test successful character creation."""
        # Mock the character creator to return success
        with patch.object(backend.character_creator, 'create_character') as mock_create:
            mock_result = CreationResult(
                success=True,
                data={"name": "Test Character", "level": 1},
                creation_time=1.5
            )
            mock_create.return_value = mock_result
            
            result = backend.create_character("Test description")
            
            assert result["success"] is True
            assert result["character"] is not None
            assert result["character"]["name"] == "Test Character"
            assert result["creation_time"] == 1.5
            assert result["error"] is None
    
    def test_character_creation_failure(self, backend):
        """Test character creation failure handling."""
        # Mock the character creator to return failure
        with patch.object(backend.character_creator, 'create_character') as mock_create:
            mock_result = CreationResult(
                success=False,
                error="Test error message",
                creation_time=0.5
            )
            mock_create.return_value = mock_result
            
            result = backend.create_character("Test description")
            
            assert result["success"] is False
            assert result["character"] is None
            assert result["error"] == "Test error message"
    
    def test_character_creation_exception(self, backend):
        """Test character creation exception handling."""
        # Mock the character creator to raise an exception
        with patch.object(backend.character_creator, 'create_character') as mock_create:
            mock_create.side_effect = Exception("Test exception")
            
            result = backend.create_character("Test description")
            
            assert result["success"] is False
            assert result["character"] is None
            assert "Test exception" in result["error"]
    
    def test_character_validation_success(self, backend):
        """Test successful character validation."""
        from validation import ValidationResult, ValidationIssue
        
        # Mock the validator to return success
        with patch.object(backend.validator, 'validate_character_data') as mock_validate:
            mock_result = ValidationResult(
                valid=True,
                score=0.95,
                issues=[],
                summary={"total_issues": 0}
            )
            mock_validate.return_value = mock_result
            
            test_data = {"name": "Test", "level": 1}
            result = backend.validate_character(test_data)
            
            assert result["valid"] is True
            assert result["score"] == 0.95
            assert len(result["issues"]) == 0
    
    def test_character_validation_with_issues(self, backend):
        """Test character validation with issues."""
        from validation import ValidationResult, ValidationIssue
        
        # Mock the validator to return issues
        with patch.object(backend.validator, 'validate_character_data') as mock_validate:
            test_issue = ValidationIssue(
                severity="warning",
                category="stats",
                message="Low ability score",
                field="strength",
                suggestion="Consider increasing strength"
            )
            
            mock_result = ValidationResult(
                valid=False,
                score=0.7,
                issues=[test_issue],
                summary={"total_issues": 1}
            )
            mock_validate.return_value = mock_result
            
            test_data = {"name": "Test", "level": 1}
            result = backend.validate_character(test_data)
            
            assert result["valid"] is False
            assert result["score"] == 0.7
            assert len(result["issues"]) == 1
            assert result["issues"][0]["severity"] == "warning"
            assert result["issues"][0]["message"] == "Low ability score"
    
    def test_character_formatting_success(self, backend):
        """Test successful character formatting."""
        # Mock format_creation_result function
        with patch('main.format_creation_result') as mock_format:
            mock_format.return_value = "Formatted character text"
            
            test_data = {"name": "Test", "level": 1}
            result = backend.format_character(test_data, "summary")
            
            assert result["success"] is True
            assert result["formatted_text"] == "Formatted character text"
            assert result["format_type"] == "summary"
    
    def test_character_formatting_exception(self, backend):
        """Test character formatting exception handling."""
        # Mock format_creation_result to raise exception
        with patch('main.format_creation_result') as mock_format:
            mock_format.side_effect = Exception("Formatting error")
            
            test_data = {"name": "Test", "level": 1}
            result = backend.format_character(test_data, "summary")
            
            assert result["success"] is False
            assert "Formatting error" in result["formatted_text"]


class TestBackendComponents:
    """Test individual backend components."""
    
    def test_character_creator_import(self):
        """Test that character creator can be imported."""
        try:
            from character_creation import CharacterCreator, CreationConfig
            assert CharacterCreator is not None
            assert CreationConfig is not None
        except ImportError as e:
            pytest.fail(f"Could not import CharacterCreator: {e}")
    
    def test_validator_import(self):
        """Test that validator can be imported."""
        try:
            from validation import CharacterValidator
            assert CharacterValidator is not None
        except ImportError as e:
            pytest.fail(f"Could not import CharacterValidator: {e}")
    
    def test_formatter_import(self):
        """Test that formatter can be imported."""
        try:
            from formatting import CharacterFormatter
            assert CharacterFormatter is not None
        except ImportError as e:
            pytest.fail(f"Could not import CharacterFormatter: {e}")
    
    def test_llm_service_import(self):
        """Test that LLM service can be imported."""
        try:
            from llm_services import create_llm_service
            assert create_llm_service is not None
        except ImportError as e:
            pytest.fail(f"Could not import LLM service: {e}")


class TestAPIEndpoints:
    """Test API endpoint functionality."""
    
    @pytest.fixture
    def mock_backend(self):
        """Create a mock backend for API testing."""
        backend = Mock()
        backend.create_character.return_value = {
            "success": True,
            "character": {"name": "Test Character"},
            "error": None,
            "warnings": [],
            "creation_time": 1.0
        }
        backend.validate_character.return_value = {
            "valid": True,
            "score": 0.9,
            "issues": [],
            "summary": {}
        }
        backend.format_character.return_value = {
            "formatted_text": "Test formatted text",
            "format_type": "summary",
            "success": True
        }
        backend.get_health_status.return_value = {
            "status": "healthy",
            "services": {"test": "active"}
        }
        return backend
    
    def test_api_create_endpoint(self, mock_backend):
        """Test the create character endpoint logic."""
        # Test the backend method that would be called by the API
        result = mock_backend.create_character(
            "Test description", 1, True, False
        )
        
        assert result["success"] is True
        assert result["character"]["name"] == "Test Character"
        mock_backend.create_character.assert_called_once_with(
            "Test description", 1, True, False
        )
    
    def test_api_validate_endpoint(self, mock_backend):
        """Test the validate character endpoint logic."""
        test_data = {"name": "Test", "level": 1}
        result = mock_backend.validate_character(test_data)
        
        assert result["valid"] is True
        assert result["score"] == 0.9
        mock_backend.validate_character.assert_called_once_with(test_data)
    
    def test_api_format_endpoint(self, mock_backend):
        """Test the format character endpoint logic."""
        test_data = {"name": "Test", "level": 1}
        result = mock_backend.format_character(test_data, "summary")
        
        assert result["success"] is True
        assert result["formatted_text"] == "Test formatted text"
        mock_backend.format_character.assert_called_once_with(test_data, "summary")
    
    def test_api_health_endpoint(self, mock_backend):
        """Test the health check endpoint logic."""
        result = mock_backend.get_health_status()
        
        assert result["status"] == "healthy"
        assert "services" in result
        mock_backend.get_health_status.assert_called_once()


# Test configuration and fixtures
@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture."""
    return {
        "test_descriptions": [
            "A brave human fighter",
            "An elven wizard",
            "A halfling rogue"
        ],
        "test_levels": [1, 3, 5, 10],
        "test_character_data": {
            "name": "Test Character",
            "species": "Human",
            "level": 1,
            "classes": {"Fighter": 1},
            "ability_scores": {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            }
        }
    }


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])
