# skill.py
# Description: Handles character skills and proficiencies.

from typing import Dict, List, Tuple, Any, Optional
import json

from backend.core.skills.abstract_skills import AbstractSkills    
from backend.core.skills.llm_skills_advisor import LLMSkillsAdvisor

class Skills(AbstractSkills):
    """Implementation of AbstractSkills for D&D 2024 edition."""
    
    def __init__(self):
        """Initialize the skills data for D&D 2024 edition."""
        self.llm_advisor = LLMSkillsAdvisor()
        
        # Skills data with their associated ability scores
        self._skills_data = {
            "acrobatics": {
                "ability": "dexterity",
                "description": "Your Acrobatics skill covers your ability to stay on your feet in tricky situations, perform gymnastic maneuvers, and flourishes.",
                "examples": ["Balance on narrow or unstable surfaces", "Land safely after falls", "Perform acrobatic stunts"]
            },
            "animal handling": {
                "ability": "wisdom",
                "description": "Animal Handling determines how well you can calm, control, or interact with animals.",
                "examples": ["Calm a domesticated animal", "Prevent a mount from getting spooked", "Intuit an animal's intentions"]
            },
            "arcana": {
                "ability": "intelligence",
                "description": "Arcana measures your ability to recall lore about spells, magic items, eldritch symbols, magical traditions, and planes of existence.",
                "examples": ["Identify magical effects and spells", "Recall knowledge about arcane traditions", "Understand magical symbols"]
            },
            "athletics": {
                "ability": "strength",
                "description": "Athletics covers difficult situations you encounter while climbing, jumping, swimming, or other physical activities.",
                "examples": ["Climb vertical surfaces", "Jump exceptional distances", "Swim against strong currents"]
            },
            "deception": {
                "ability": "charisma",
                "description": "Deception determines how well you can convincingly hide the truth, either verbally or through your actions.",
                "examples": ["Mislead someone with ambiguity", "Tell convincing lies", "Pass yourself off as someone else"]
            },
            "history": {
                "ability": "intelligence",
                "description": "History measures your ability to recall lore about historical events, legendary people, ancient kingdoms, past disputes, recent wars, and lost civilizations.",
                "examples": ["Recall information about ancient civilizations", "Remember details about major historical events", "Identify famous historical figures"]
            },
            "insight": {
                "ability": "wisdom",
                "description": "Insight helps you determine the true intentions of a creature, detect lies, and predict someone's next move.",
                "examples": ["Determine if someone is telling the truth", "Predict another's next action", "Read body language"]
            },
            "intimidation": {
                "ability": "charisma",
                "description": "Intimidation measures your ability to influence others through threats, hostile actions, and physical violence.",
                "examples": ["Extract information through threats", "Scare someone into compliance", "Project menacing presence"]
            },
            "investigation": {
                "ability": "intelligence",
                "description": "Investigation is about finding clues and making deductions based on those clues.",
                "examples": ["Search for hidden objects", "Find clues at a crime scene", "Identify patterns in evidence"]
            },
            "medicine": {
                "ability": "wisdom",
                "description": "Medicine lets you diagnose illness, stabilize dying companions, or treat wounds.",
                "examples": ["Diagnose diseases", "Stabilize a dying creature", "Identify poisons and toxins"]
            },
            "nature": {
                "ability": "intelligence",
                "description": "Nature measures your ability to recall lore about terrain, plants and animals, the weather, and natural cycles.",
                "examples": ["Identify plants and animals", "Predict weather", "Recognize dangerous natural hazards"]
            },
            "perception": {
                "ability": "wisdom",
                "description": "Perception lets you spot, hear, or otherwise detect the presence of something using your senses.",
                "examples": ["Spot hidden creatures", "Hear distant sounds", "Notice subtle details"]
            },
            "performance": {
                "ability": "charisma",
                "description": "Performance determines how well you can delight an audience with music, dance, acting, storytelling, or some other entertainment.",
                "examples": ["Play a musical instrument", "Entertain with storytelling", "Perform theatrical acts"]
            },
            "persuasion": {
                "ability": "charisma",
                "description": "Persuasion is used when you attempt to influence someone or a group of people with tact, social graces, or good nature.",
                "examples": ["Convince someone through logical argument", "Negotiate a diplomatic agreement", "Win someone's trust"]
            },
            "religion": {
                "ability": "intelligence",
                "description": "Religion measures your ability to recall lore about deities, rites and prayers, religious hierarchies, holy symbols, and the practices of secret cults.",
                "examples": ["Recall religious ceremonies", "Identify holy symbols", "Remember details about deities"]
            },
            "sleight of hand": {
                "ability": "dexterity",
                "description": "Sleight of Hand entails fast hand movements and misdirection to take or hide objects without others noticing.",
                "examples": ["Pickpocket someone", "Conceal an object", "Perform manual tricks"]
            },
            "stealth": {
                "ability": "dexterity",
                "description": "Stealth determines how well you can conceal yourself from enemies, slink past guards, slip away without being noticed, or sneak up on someone without being seen or heard.",
                "examples": ["Hide from enemies", "Move silently", "Blend into a crowd"]
            },
            "survival": {
                "ability": "wisdom",
                "description": "Survival helps you to follow tracks, hunt wild game, guide your group through frozen wastelands, identify signs of nearby creatures, or avoid natural hazards.",
                "examples": ["Track creatures", "Find food in the wilderness", "Navigate through difficult terrain"]
            }
        }
        
        # Class skill proficiencies
        self._class_skills = {
            "artificer": ["arcana", "history", "investigation", "medicine", "nature", "perception", "sleight of hand"],
            "barbarian": ["animal handling", "athletics", "intimidation", "nature", "perception", "survival"],
            "bard": ["acrobatics", "animal handling", "arcana", "athletics", "deception", "history", "insight", "intimidation", "investigation", "medicine", "nature", "perception", "performance", "persuasion", "religion", "sleight of hand", "stealth", "survival"],
            "cleric": ["history", "insight", "medicine", "persuasion", "religion"],
            "druid": ["arcana", "animal handling", "insight", "medicine", "nature", "perception", "religion", "survival"],
            "fighter": ["acrobatics", "animal handling", "athletics", "history", "insight", "intimidation", "perception", "survival"],
            "monk": ["acrobatics", "athletics", "history", "insight", "religion", "stealth"],
            "paladin": ["athletics", "insight", "intimidation", "medicine", "persuasion", "religion"],
            "ranger": ["animal handling", "athletics", "insight", "investigation", "nature", "perception", "stealth", "survival"],
            "rogue": ["acrobatics", "athletics", "deception", "insight", "intimidation", "investigation", "perception", "performance", "persuasion", "sleight of hand", "stealth"],
            "sorcerer": ["arcana", "deception", "insight", "intimidation", "persuasion", "religion"],
            "warlock": ["arcana", "deception", "history", "intimidation", "investigation", "nature", "religion"],
            "wizard": ["arcana", "history", "insight", "investigation", "medicine", "religion"]
        }
        
        # Background skill proficiencies
        self._background_skills = {
            "acolyte": ["insight", "religion"],
            "charlatan": ["deception", "sleight of hand"],
            "criminal": ["deception", "stealth"],
            "entertainer": ["acrobatics", "performance"],
            "folk hero": ["animal handling", "survival"],
            "guild artisan": ["insight", "persuasion"],
            "hermit": ["medicine", "religion"],
            "noble": ["history", "persuasion"],
            "outlander": ["athletics", "survival"],
            "sage": ["arcana", "history"],
            "sailor": ["athletics", "perception"],
            "soldier": ["athletics", "intimidation"],
            "urchin": ["sleight of hand", "stealth"]
        }
    
    def get_all_skills(self) -> List[str]:
        """
        Return a list of all available skills in D&D 2024.
        
        Returns:
            List[str]: List of all skill names
        """
        return list(self._skills_data.keys())
    
    def get_skill_details(self, skill_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a skill.
        
        Args:
            skill_name (str): Name of the skill
            
        Returns:
            Dict: Dictionary with skill details
            
        Raises:
            ValueError: If skill_name is not valid
        """
        skill_name_lower = skill_name.lower()
        
        if skill_name_lower not in self._skills_data:
            raise ValueError(f"Unknown skill: {skill_name}")
            
        return self._skills_data[skill_name_lower]
    
    def get_skill_ability_score(self, skill_name: str) -> str:
        """
        Get the ability score associated with a skill.
        
        Args:
            skill_name (str): Name of the skill
            
        Returns:
            str: The ability score name (e.g., 'dexterity')
            
        Raises:
            ValueError: If skill_name is not valid
        """
        skill_name_lower = skill_name.lower()
        
        if skill_name_lower not in self._skills_data:
            raise ValueError(f"Unknown skill: {skill_name}")
            
        return self._skills_data[skill_name_lower]["ability"]
    
    def calculate_skill_modifier(
        self, 
        skill_name: str, 
        ability_scores: Dict[str, int], 
        proficiency_bonus: int, 
        is_proficient: bool = False, 
        expertise: bool = False
    ) -> int:
        """
        Calculate modifier for a skill check.
        
        Args:
            skill_name (str): Name of the skill
            ability_scores (Dict[str, int]): Character ability scores
            proficiency_bonus (int): Character proficiency bonus
            is_proficient (bool): Whether the character is proficient in this skill
            expertise (bool): Whether the character has expertise in this skill
            
        Returns:
            int: The skill modifier
            
        Raises:
            ValueError: If skill_name is not valid
        """
        skill_name_lower = skill_name.lower()
        
        if skill_name_lower not in self._skills_data:
            raise ValueError(f"Unknown skill: {skill_name}")
        
        ability = self._skills_data[skill_name_lower]["ability"]
        
        if ability not in ability_scores:
            raise ValueError(f"Ability score {ability} not found in provided ability scores")
        
        # Calculate ability modifier: (score - 10) / 2, rounded down
        ability_modifier = (ability_scores[ability] - 10) // 2
        
        # Add proficiency if applicable
        if is_proficient:
            if expertise:
                # Expertise doubles proficiency bonus
                return ability_modifier + (proficiency_bonus * 2)
            else:
                return ability_modifier + proficiency_bonus
                
        return ability_modifier
    
    def get_class_skill_proficiencies(self, class_name: str) -> List[str]:
        """
        Get skill proficiencies available to a class.
        
        Args:
            class_name (str): Name of the character class
            
        Returns:
            List[str]: List of skills the class can be proficient in
            
        Raises:
            ValueError: If class_name is not valid
        """
        class_name_lower = class_name.lower()
        
        if class_name_lower not in self._class_skills:
            # If class is not in our standard list, ask the LLM for help
            return self.llm_advisor.get_skills_for_custom_class(class_name)
            
        return self._class_skills[class_name_lower]
    
    def get_background_skill_proficiencies(self, background: str) -> List[str]:
        """
        Get skill proficiencies from a background.
        
        Args:
            background (str): Character background
            
        Returns:
            List[str]: List of skills granted by the background
            
        Raises:
            ValueError: If background is not recognized
        """
        background_lower = background.lower()
        
        if background_lower not in self._background_skills:
            # If background is not in our standard list, ask the LLM for help
            return self.llm_advisor.get_skills_for_custom_background(background)
            
        return self._background_skills[background_lower]
    
    def get_custom_skill_recommendations(self, character_concept: str) -> List[str]:
        """
        Get skill recommendations for a character concept.
        
        Args:
            character_concept (str): Brief description of character concept
            
        Returns:
            List[str]: List of recommended skills
        """
        return self.llm_advisor.recommend_skills_for_concept(character_concept)