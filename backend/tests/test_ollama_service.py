import unittest
from unittest.mock import MagicMock, patch
import pytest
import json

from backend.core.services.ollama_service import OllamaService
from backend.core.spells.llm_spells_advisor import LLMSpellsAdvisor
from backend.core.character.llm_character_advisor import LLMCharacterAdvisor
from backend.core.npc.llm_npc_advisor import LLMNPCAdvisor

class TestOllamaService(unittest.TestCase):
    """Comprehensive tests for the OllamaService"""
    
    def setUp(self):
        """Set up test environment"""
        self.requests_patcher = patch('backend.core.services.ollama_service.requests.post')
        self.mock_post = self.requests_patcher.start()
        
        # Setup mock response for generate_text
        generate_mock = MagicMock()
        generate_mock.json.return_value = {"response": "This is a test response"}
        generate_mock.raise_for_status.return_value = None
        
        # Setup mock response for chat_completion
        chat_mock = MagicMock()
        chat_mock.json.return_value = {
            "model": "llama3",
            "created_at": "2023-01-01T00:00:00Z",
            "message": {"role": "assistant", "content": "This is a chat response"},
            "done": True
        }
        chat_mock.raise_for_status.return_value = None
        
        # Set different responses based on URL
        def side_effect_func(url, **kwargs):
            if url.endswith("/api/generate"):
                return generate_mock
            elif url.endswith("/api/chat"):
                return chat_mock
            return MagicMock()
            
        self.mock_post.side_effect = side_effect_func
        
        # Create OllamaService instance
        self.service = OllamaService()
    
    def tearDown(self):
        """Clean up after test"""
        self.requests_patcher.stop()
    
    def test_generate_text(self):
        """Test the generate_text method"""
        result = self.service.generate_text("Test prompt")
        
        # Verify result
        self.assertEqual(result, "This is a test response")
        
        # Verify correct API call
        self.mock_post.assert_called_once()
        args, kwargs = self.mock_post.call_args
        self.assertEqual(args[0], "http://localhost:11434/api/generate")
        self.assertEqual(kwargs["json"]["prompt"], "Test prompt")
        self.assertEqual(kwargs["json"]["model"], "llama3")
    
    def test_generate_text_with_system_message(self):
        """Test generate_text with system message"""
        result = self.service.generate_text(
            "Test prompt", 
            system_message="You are a helpful assistant"
        )
        
        # Verify API call includes system message
        args, kwargs = self.mock_post.call_args
        self.assertIn("You are a helpful assistant", kwargs["json"]["prompt"])
    
    def test_chat_completion(self):
        """Test the chat_completion method"""
        messages = [
            {"role": "system", "content": "You are a D&D expert"},
            {"role": "user", "content": "Tell me about wizards"}
        ]
        
        result = self.service.chat_completion(messages)
        
        # Verify result
        self.assertEqual(result["message"]["content"], "This is a chat response")
        self.assertEqual(result["message"]["role"], "assistant")
        
        # Verify correct API call
        args, kwargs = self.mock_post.call_args
        self.assertEqual(args[0], "http://localhost:11434/api/chat")
        self.assertEqual(kwargs["json"]["messages"], messages)
    
    def test_error_handling(self):
        """Test error handling"""
        # Make request throw an exception
        self.mock_post.side_effect = Exception("Connection error")
        
        # Verify correct error handling
        with self.assertRaises(ConnectionError):
            self.service.generate_text("Test prompt")


# Pytest fixtures and tests
@pytest.fixture
def mock_ollama():
    """Fixture for mocking OllamaService"""
    with patch('backend.core.services.ollama_service.OllamaService') as mock:
        # Setup mock response for different LLM calls
        mock.return_value.generate_text.return_value = json.dumps({
            "spells": [
                {"name": "Fireball", "level": 3, "school": "evocation"},
                {"name": "Magic Missile", "level": 1, "school": "evocation"}
            ]
        })
        yield mock


# Advisor integration tests
def test_llm_spells_advisor(mock_ollama):
    """Test the LLM spells advisor integration"""
    advisor = LLMSpellsAdvisor()
    
    # Test spell recommendations
    spells = advisor.recommend_spells_by_personality(
        personality_traits="curious and experimental",
        class_name="wizard",
        values="discovery and knowledge"
    )
    
    # Verify the advisor returned properly formatted data
    assert isinstance(spells, list)
    assert len(spells) > 0
    assert "name" in spells[0]
    assert "level" in spells[0]
    
    # Verify OllamaService was called
    mock_ollama.return_value.generate_text.assert_called_once()


def test_llm_character_advisor(mock_ollama):
    """Test the LLM character advisor integration"""
    mock_ollama.return_value.generate_text.return_value = json.dumps({
        "class_recommendation": "wizard",
        "background_recommendation": "sage",
        "alignment_recommendation": "neutral good",
        "reasoning": "Based on your description of a knowledge-seeking character..."
    })
    
    advisor = LLMCharacterAdvisor()
    
    # Test character concept recommendations
    result = advisor.recommend_character_concept(
        "I want to play a character who seeks knowledge and magical power"
    )
    
    # Verify the advisor returned properly formatted data
    assert "class_recommendation" in result
    assert result["class_recommendation"] == "wizard"
    
    # Verify OllamaService was called correctly
    mock_ollama.return_value.generate_text.assert_called_once()


# Streaming test with pytest
@pytest.mark.asyncio
async def test_stream_generation():
    """Test streaming response generation"""
    with patch('backend.core.services.ollama_service.requests.post') as mock_post:
        # Setup mock streaming response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = [
            b'{"response":"Hello", "done":false}',
            b'{"response":" world", "done":false}',
            b'{"response":"!", "done":true}'
        ]
        mock_post.return_value.__enter__.return_value = mock_response
        
        service = OllamaService()
        
        # Collect streaming response
        result = []
        async for token in service.stream_generation("Test prompt"):
            result.append(token)
        
        # Verify streaming result
        assert result == ["Hello", " world", "!"]
        assert "".join(result) == "Hello world!"