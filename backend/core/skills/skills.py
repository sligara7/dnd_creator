# skill.py
# Description: Handles character skills and proficiencies.

# must adhere to abstract_skills.py interface for skill management in D&D 2024.

# Methods:

# get_all_skills() - Return a list of all available skills
# get_skill_details(skill_name) - Get detailed information about a skill
# get_skill_ability_score(skill_name) - Get the ability score associated with a skill
# calculate_skill_modifier(skill_name, ability_scores, proficiency_bonus, is_proficient, expertise) - Calculate modifier for a skill check
# get_class_skill_proficiencies(class_name) - Get skill proficiencies available to a class
# get_background_skill_proficiencies(background) - Get skill proficiencies from a background

# Customizing Skills System with Llama 3/Ollama Integration
# Each function in skills.py can be enhanced through LLM interactions to provide a personalized skill system experience:

# 1. get_all_skills()
# LLM Enhancement: "Recommend skills that would align with character concept {character_concept} and backstory {backstory}"
# Implementation: Add parameter suggest_for_concept=False to return LLM-recommended skill focus areas
# Prompt Example: "Based on my character being a former sailor who now seeks knowledge about the arcane, which skills would be most important for me to focus on?"
# 2. get_skill_details(skill_name)
# LLM Enhancement: "Suggest creative and unconventional ways to use the {skill_name} skill in different scenarios"
# Implementation: Add parameter include_creative_uses=False to enhance standard skill descriptions
# Prompt Example: "Beyond the obvious applications, what are some creative ways my character could use the Persuasion skill in exploration or combat scenarios?"
# 3. get_skill_ability_score(skill_name)
# LLM Enhancement: "Explain when a DM might call for alternative ability checks with this skill"
# Implementation: Add parameter suggest_variant_checks=False to provide scenario-based ability score variations
# Prompt Example: "While Athletics typically uses Strength, in what situations might a DM reasonably ask for an Intelligence (Athletics) or Constitution (Athletics) check?"
# 4. calculate_skill_modifier(skill_name, ability_scores, proficiency_bonus, is_proficient, expertise)
# LLM Enhancement: "Provide context for what a {modifier} in {skill_name} represents in terms of capability"
# Implementation: Add parameter include_capability_context=False to explain what the numerical modifier means narratively
# Prompt Example: "My character has a +7 in Stealth. In practical terms, what does this mean about their sneaking capabilities compared to average people or skilled professionals?"
# 5. get_class_skill_proficiencies(class_name)
# LLM Enhancement: "Based on my character concept as {character_concept}, which class skill proficiencies would be most fitting?"
# Implementation: Add parameter character_concept=None for personalized skill selection guidance
# Prompt Example: "As a Ranger who was formerly a bounty hunter in urban environments, which of the available Ranger skill proficiencies would make most sense for my character?"
# 6. get_background_skill_proficiencies(background)
# LLM Enhancement: "Provide narrative reasons for why someone with background {background} would have developed these skills"
# Implementation: Add parameter include_narrative_context=False to include backstory elements explaining skill development
# Prompt Example: "Why would someone with the Sage background specifically have developed proficiency in Arcana and History? What experiences in their past would have cultivated these skills?"
# Implementation Approach
# Create an LLMSkillAdvisor class that interfaces with Ollama/Llama3
# Design context-aware prompts that incorporate character details when available
# Implement an optional "skill story" system where the LLM can generate a brief narrative about how a character developed a particular skill
# Include difficulty assessment where the LLM can explain what DC ranges would be appropriate for different skill applications
# Develop a system for the LLM to suggest skill synergies where multiple skills could work together for special outcomes
# This enhancement layer maintains the core skill system's rule compliance while providing rich, personalized guidance for players to better understand and leverage their character's skills.

from backend.core.ollama_service import OllamaService

class LLMAbilityAdvisor:
    def __init__(self, llm_service=None):
        if llm_service is None:
            self.llm_service = OllamaService()
        else:
            self.llm_service = llm_service
        self.ability_scores = AbilityScores()