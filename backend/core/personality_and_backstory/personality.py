# personality.py
# Description: Handles character traits, ideals, bonds, and flaws.

# must adhere to abstract_personality.py interface for personality and backstory management in D&D 2024.

# Methods:

# get_personality_options(background) - Get personality options based on background
# generate_random_personality() - Generate random personality traits
# generate_ai_backstory(character_data) - Use LLM to generate character backstory
# validate_backstory(backstory) - Check backstory for rule compliance
# get_backstory_hooks(backstory) - Extract potential story hooks from backstory

# Customizing Personality System with Llama 3/Ollama Integration
# Each function in personality.py can be enhanced through LLM interactions to provide a rich character personality development experience:

# 1. get_personality_options(background)
# LLM Enhancement: "Generate unique personality traits that align with background {background} but go beyond the standard options"
# Implementation: Add parameter include_custom_options=False to supplement standard options with AI-generated traits
# Prompt Example: "Create three unique personality traits for a character with the Hermit background that reflect unusual experiences during their isolation"
# 2. generate_random_personality()
# LLM Enhancement: "Create a coherent personality where traits, ideals, bonds, and flaws naturally complement each other"
# Implementation: Add parameter ensure_coherence=False to generate a psychologically consistent personality profile
# Prompt Example: "Generate a personality profile where each element (traits, ideals, bonds, flaws) reinforces a central character theme of 'redemption seeker'"
# 3. generate_ai_backstory(character_data)
# LLM Enhancement: "Create a backstory that incorporates species {species}, class {class}, background {background}, and personality elements while explaining key life events"
# Implementation: Add parameters for backstory_length, tone, and key_elements_to_include
# Prompt Example: "Write a 300-word backstory for a Halfling Rogue with the Charlatan background. The tone should be bittersweet, and include how they learned their skills, their greatest con, and why they began adventuring"
# 4. validate_backstory(backstory)
# LLM Enhancement: "Analyze backstory for internal consistency, setting compatibility, and appropriate tone"
# Implementation: Add parameters setting_name, check_for_consistency=True, suggest_improvements=False
# Prompt Example: "Review this backstory for a character in the Forgotten Realms setting. Identify any inconsistencies with the world, timeline problems, or elements that seem out of character based on their species and class"
# 5. get_backstory_hooks(backstory)
# LLM Enhancement: "Extract narrative elements from the backstory that a DM could develop into personal quests or campaign ties"
# Implementation: Add parameters hook_count=3, hook_type=['ally', 'enemy', 'mystery', 'goal'], detail_level='summary'
# Prompt Example: "From this character backstory, identify 3 elements that could become personal quests: one involving a potential ally, one involving an enemy, and one unresolved mystery. Provide a brief adventure hook for each"
# Implementation Approach
# Create an LLMPersonalityAdvisor class that interfaces with Ollama/Llama3 for all personality-related enhancements
# Store prompt templates that can be filled with character data dynamically
# Implement a system to blend standard D&D personality options with custom LLM-generated content
# Develop "backstory evolution" capability where the LLM can suggest how a character's personality might change after significant campaign events
# Include a narrative voice feature where the backstory can be written in different styles (first-person, third-person, as a diary, etc.)
# Create DM tools for generating NPCs that have meaningful connections to character backstories
# This enhancement provides deep personalization of character personalities while maintaining gameplay balance by focusing these AI enhancements on narrative elements rather than mechanical advantages.

# Backstory and Personality should be tightly coupled with alignment; for instance, if character is Chaotic Good, their backstory and personality traits should reflect that alignment. The LLM can help ensure that the character's personality, backstory, and alignment are consistent with each other.

from backend.core.ollama_service import OllamaService

class LLMAbilityAdvisor:
    def __init__(self, llm_service=None):
        if llm_service is None:
            self.llm_service = OllamaService()
        else:
            self.llm_service = llm_service
        self.ability_scores = AbilityScores()