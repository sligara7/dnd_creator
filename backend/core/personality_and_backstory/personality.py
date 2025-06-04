# personality.py
# Description: Handles character traits, ideals, bonds, and flaws.

from typing import Dict, List, Tuple, Any
import random

from backend.core.ollama_service import OllamaService
from backend.core.personality_and_backstory.llm_personality_advisor import LLMPersonalityAdvisor
from backend.core.personality_and_backstory.abstract_personality import AbstractPersonality


class Personality(AbstractPersonality):
    """
    Implementation of AbstractPersonality for handling character personality 
    and backstory in D&D 2024.
    """
    
    def __init__(self):
        """Initialize services required for personality generation"""
        self.ollama_service = OllamaService()
        self.personality_advisor = LLMPersonalityAdvisor()
        
        # Common personality traits by background - simplified example
        self._background_options = {
            "acolyte": {
                "traits": ["I quote sacred texts", "I find guidance in prayer"],
                "ideals": ["Tradition", "Faith", "Charity"],
                "bonds": ["I would die for my temple", "My mentor is everything to me"],
                "flaws": ["I judge others harshly", "I trust religious authority blindly"]
            },
            "criminal": {
                "traits": ["I always have a plan", "I'm suspicious of everyone"],
                "ideals": ["Freedom", "Greed", "People"],
                "bonds": ["I'm loyal to my crew", "I have a debt to repay"],
                "flaws": ["I can't resist a con", "I run from authority"]
            },
            # Additional backgrounds would be added here
        }
    
    def get_personality_options(self, background: str) -> Dict[str, List[str]]:
        """
        Get personality options based on background
        
        Args:
            background (str): The character's background
            
        Returns:
            dict: Dictionary containing traits, ideals, bonds, and flaws options
        """
        if background.lower() in self._background_options:
            return self._background_options[background.lower()]
        
        # If background isn't found, generate options using the LLM
        return self.personality_advisor.generate_options_for_background(background)
    
    def generate_random_personality(self) -> Dict[str, str]:
        """
        Generate random personality traits
        
        Returns:
            dict: Randomly generated personality traits, ideals, bonds, and flaws
        """
        # Select a random background for base options
        background = random.choice(list(self._background_options.keys()))
        options = self._background_options[background]
        
        # Choose one option randomly from each category
        return {
            "trait": random.choice(options["traits"]),
            "ideal": random.choice(options["ideals"]),
            "bond": random.choice(options["bonds"]),
            "flaw": random.choice(options["flaws"]),
            "background": background
        }
    
    def generate_ai_backstory(self, character_data: Dict[str, Any]) -> str:
        """
        Use LLM to generate character backstory
        
        Args:
            character_data (dict): Character information including class, race, background
            
        Returns:
            str: Generated backstory
        """
        # Extract key data for backstory generation
        prompt = self._format_backstory_prompt(character_data)
        
        # Generate backstory using Ollama service
        return self.ollama_service.generate_text(
            prompt=prompt, 
            system_message="Create a compelling D&D character backstory that aligns with the 2024 edition rules."
        )
    
    def validate_backstory(self, backstory: str) -> Tuple[bool, str]:
        """
        Check backstory for rule compliance
        
        Args:
            backstory (str): The character backstory
            
        Returns:
            tuple: (is_valid, reason_if_invalid)
        """
        # Define validation criteria
        max_length = 2000
        forbidden_terms = ["modern", "gun", "technology", "internet", "computer"]
        
        # Check length
        if len(backstory) > max_length:
            return False, f"Backstory exceeds maximum length of {max_length} characters"
        
        # Check for anachronistic or forbidden terms
        for term in forbidden_terms:
            if term.lower() in backstory.lower():
                return False, f"Backstory contains anachronistic term: '{term}'"
        
        # Use LLM to check for deeper rule compliance
        validation_result = self.personality_advisor.validate_backstory_against_rules(backstory)
        if not validation_result["is_valid"]:
            return False, validation_result["reason"]
        
        return True, "Backstory is valid"
    
    def get_backstory_hooks(self, backstory: str) -> List[str]:
        """
        Extract potential story hooks from backstory
        
        Args:
            backstory (str): The character backstory
            
        Returns:
            list: List of potential story hooks
        """
        # Use LLM to extract story hooks
        result = self.ollama_service.generate_text(
            prompt=f"Extract 3-5 story hooks from this character backstory: {backstory}",
            system_message="You are a helpful DM assistant. Extract specific plot hooks, unresolved conflicts, or character goals that could be used in a D&D campaign."
        )
        
        # Process result to get a clean list of hooks
        hooks = []
        for line in result.split("\n"):
            line = line.strip()
            if line and (line.startswith("-") or line.startswith("•") or len(hooks) < 5):
                # Clean up the line
                hook = line.lstrip("-•").strip()
                if hook and len(hook) > 10:  # Ensure it's substantive
                    hooks.append(hook)
        
        return hooks
    
    def _format_backstory_prompt(self, character_data: Dict[str, Any]) -> str:
        """Helper method to format the backstory prompt based on character data"""
        prompt = f"Create a character backstory for a {character_data.get('species', 'humanoid')} " \
                 f"{character_data.get('class', 'adventurer')} with the " \
                 f"{character_data.get('background', 'wanderer')} background.\n\n"
                 
        # Add personality traits if available
        if "personality" in character_data:
            p = character_data["personality"]
            prompt += f"Traits: {p.get('trait', '')}\n"
            prompt += f"Ideals: {p.get('ideal', '')}\n"
            prompt += f"Bonds: {p.get('bond', '')}\n"
            prompt += f"Flaws: {p.get('flaw', '')}\n\n"
            
        prompt += "The backstory should explain their motivations, past experiences, " \
                  "and how they acquired their abilities. Include at least one unresolved " \
                  "conflict and a connection to the world."
            
        return prompt