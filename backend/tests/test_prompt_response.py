import unittest
from unittest.mock import MagicMock, patch
import json

from backend.core.services.ollama_service import OllamaService

class TestPromptResponses(unittest.TestCase):
    """
    Test the system's ability to respond to character creation prompts.
    Note: This test requires manual verification of the output quality.
    """
    
    def setUp(self):
        """Set up test environment"""
        # If we want to test against the real LLM, don't mock it
        self.use_real_llm = False
        
        if not self.use_real_llm:
            # Mock the OllamaService
            self.ollama_patcher = patch('backend.core.services.ollama_service.OllamaService')
            self.mock_ollama = self.ollama_patcher.start()
            
            # Setup mock responses for different prompt types
            self.mock_ollama.return_value.generate_text.side_effect = self._mock_response_generator
            self.ollama_service = OllamaService()
        else:
            # Use real LLM for testing - note this requires Ollama to be running
            self.ollama_service = OllamaService()
    
    def tearDown(self):
        """Clean up after test"""
        if not self.use_real_llm:
            self.ollama_patcher.stop()
    
    def _mock_response_generator(self, prompt, *args, **kwargs):
        """Generate mock responses based on prompt content"""
        if "describe your new character" in prompt.lower():
            return json.dumps({
                "character_concept": {
                    "archetype": "Skilled Hunter",
                    "personality": "Quiet, observant, and self-reliant",
                    "motivations": "Seeking to protect nature from encroaching corruption",
                    "background_hooks": "Grew up in a small woodland community"
                }
            })
        elif "what is the sex of your new character" in prompt.lower():
            return json.dumps({
                "sex": "female",
                "physical_description": "Tall and athletic with weather-worn features"
            })
        elif "personality" in prompt.lower() and "backstory" in prompt.lower():
            return json.dumps({
                "personality_traits": "Prefers solitude, values self-reliance, distrusts city folk",
                "ideals": "Balance, protection, respect for nature's power",
                "bonds": "Has a deep connection to her homeland forest",
                "flaws": "Stubborn, sometimes judgmental of those who don't share her values",
                "backstory": "Aria grew up in a remote woodland settlement where she learned to hunt and track from her father..."
            })
        elif "characteristics" in prompt.lower() and "powers" in prompt.lower():
            return json.dumps({
                "suggested_class": "ranger",
                "suggested_abilities": ["Tracking", "Archery", "Wilderness Survival"],
                "suggested_spells": ["Hunter's Mark", "Speak with Animals"],
                "combat_style": "Prefers ranged combat, skilled with bow"
            })
        else:
            return "I don't understand the prompt."
    
    def test_character_description_prompt(self):
        """Test the system response to initial character description prompt"""
        prompt = "describe your new character?"
        response = self.ollama_service.generate_text(prompt)
        
        # If using mock, verify structure
        if not self.use_real_llm:
            response_data = json.loads(response)
            self.assertIn("character_concept", response_data)
            self.assertIn("archetype", response_data["character_concept"])
            self.assertIn("personality", response_data["character_concept"])
        else:
            # For real LLM, just print and require manual verification
            print(f"\n=== Response to '{prompt}' ===\n{response}\n")
    
    def test_character_sex_prompt(self):
        """Test the system response to character sex prompt"""
        prompt = "what is the sex of your new character?"
        response = self.ollama_service.generate_text(prompt)
        
        # If using mock, verify structure
        if not self.use_real_llm:
            response_data = json.loads(response)
            self.assertIn("sex", response_data)
        else:
            # For real LLM, just print and require manual verification
            print(f"\n=== Response to '{prompt}' ===\n{response}\n")
    
    def test_personality_backstory_prompt(self):
        """Test the system response to personality and backstory prompt"""
        prompt = "tell me some things about your personality_and_backstory"
        response = self.ollama_service.generate_text(prompt)
        
        # If using mock, verify structure
        if not self.use_real_llm:
            response_data = json.loads(response)
            self.assertIn("personality_traits", response_data)
            self.assertIn("backstory", response_data)
        else:
            # For real LLM, just print and require manual verification
            print(f"\n=== Response to '{prompt}' ===\n{response}\n")
    
    def test_powers_abilities_prompt(self):
        """Test the system response to powers and abilities prompt"""
        prompt = "what are some characteristics (powers, abilities, etc) that you would like your character to have?"
        response = self.ollama_service.generate_text(prompt)
        
        # If using mock, verify structure
        if not self.use_real_llm:
            response_data = json.loads(response)
            self.assertIn("suggested_class", response_data)
            self.assertIn("suggested_abilities", response_data)
        else:
            # For real LLM, just print and require manual verification
            print(f"\n=== Response to '{prompt}' ===\n{response}\n")