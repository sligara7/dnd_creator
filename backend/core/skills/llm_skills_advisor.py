# Customizing Skills System with Llama 3/Ollama Integration
# Each function in skills.py can be enhanced through LLM interactions to provide a personalized skill system experience:

from typing import Dict, List, Any, Optional, Tuple
import json
import re

from backend.core.services.ollama_service import OllamaService

class LLMSkillsAdvisor:
    """
    LLM-powered advisor for enhancing the D&D skills system with personalized recommendations
    and contextual information using Ollama/Llama 3.
    """
    
    def __init__(self):
        """Initialize the LLM skills advisor with Ollama service"""
        self.ollama_service = OllamaService()
        
        # System message for D&D skills assistance
        self.system_message = (
            "You are a D&D 5e (2024 Edition) expert assistant specializing in character skills. "
            "Provide rule-consistent, creative, and personalized advice about skills. "
            "Keep responses concise but informative."
        )
        
        # Standard D&D skills for validation
        self.standard_skills = [
            "acrobatics", "animal handling", "arcana", "athletics", 
            "deception", "history", "insight", "intimidation", 
            "investigation", "medicine", "nature", "perception", 
            "performance", "persuasion", "religion", "sleight of hand", 
            "stealth", "survival"
        ]
    
    def recommend_skills_for_concept(
        self, 
        character_concept: str, 
        backstory: str = "", 
        limit: int = 5
    ) -> List[str]:
        """
        Recommend skills that would align with a character concept and backstory.
        
        Args:
            character_concept (str): Brief description of character concept
            backstory (str, optional): Character backstory if available
            limit (int): Maximum number of skills to recommend
            
        Returns:
            List[str]: List of recommended skills
        """
        backstory_text = f"\nBackstory: {backstory}" if backstory else ""
        
        prompt = (
            f"Based on this D&D character concept: '{character_concept}'{backstory_text}, "
            f"recommend the {limit} most important skills they should focus on. "
            f"Return only a comma-separated list of official D&D 5e (2024) skills, no explanations."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        # Extract skills and validate against standard skills
        skills = [s.strip().lower() for s in response.split(',')]
        validated_skills = [s for s in skills if s in self.standard_skills]
        
        # If we got fewer than requested, take the first 'limit' skills
        return validated_skills[:limit]
    
    def suggest_creative_uses(self, skill_name: str, scenario_type: str = "all") -> List[str]:
        """
        Suggest creative and unconventional ways to use a skill.
        
        Args:
            skill_name (str): Name of the skill
            scenario_type (str): Type of scenario - "social", "exploration", "combat", or "all"
            
        Returns:
            List[str]: List of creative uses
        """
        scenario_text = f"in {scenario_type} scenarios" if scenario_type != "all" else "across different scenarios"
        
        prompt = (
            f"Suggest 3-5 creative and unconventional ways to use the {skill_name} skill {scenario_text} "
            f"in D&D 5e (2024). Focus on applications that players might not immediately consider "
            f"but would be acceptable by most DMs. List each use in a brief sentence."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        # Process the response to extract individual uses
        uses = []
        for line in response.split('\n'):
            # Remove numbering/bullets and clean up
            clean_line = re.sub(r'^\s*[\d\-\*\•]+\.?\s*', '', line).strip()
            if clean_line and len(clean_line) > 10:  # Ensure it's a meaningful suggestion
                uses.append(clean_line)
        
        return uses
    
    def suggest_variant_ability_checks(self, skill_name: str) -> Dict[str, str]:
        """
        Explain when a DM might call for alternative ability checks with a skill.
        
        Args:
            skill_name (str): Name of the skill
            
        Returns:
            Dict[str, str]: Dictionary of ability scores and their usage scenarios
        """
        prompt = (
            f"While {skill_name} typically uses its standard ability score in D&D 5e (2024), "
            f"a DM might call for alternative ability checks in certain situations. "
            f"List 3 different ability scores and a specific scenario where each might be used "
            f"with the {skill_name} skill. Format as JSON with ability names as keys and scenarios as values."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        # Try to extract JSON from the response
        try:
            # Find JSON pattern in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            # Simple extraction if JSON parsing fails
            variants = {}
            ability_pattern = r'([A-Za-z]+).*?:(.*?)(?=\n[A-Za-z]+|\Z)'
            matches = re.finditer(ability_pattern, response, re.DOTALL)
            
            for match in matches:
                ability = match.group(1).strip().lower()
                scenario = match.group(2).strip()
                variants[ability] = scenario
                
            return variants
        except:
            # Fallback response
            return {
                "strength": f"Using {skill_name} in a physically demanding situation",
                "intelligence": f"Applying academic knowledge to {skill_name}",
                "charisma": f"Using {skill_name} to influence others"
            }
    
    def provide_capability_context(self, skill_name: str, modifier: int) -> str:
        """
        Provide context for what a modifier represents in terms of capability.
        
        Args:
            skill_name (str): Name of the skill
            modifier (int): The skill modifier
            
        Returns:
            str: Description of capability level
        """
        prompt = (
            f"In D&D 5e (2024), what does a {modifier:+d} modifier in the {skill_name} skill "
            f"represent in terms of practical capability? Compare this to average people, "
            f"professionals, and masters of the craft. Provide a brief, single paragraph description."
        )
        
        return self.ollama_service.generate_text(prompt, self.system_message)
    
    def recommend_class_skills(self, class_name: str, character_concept: str = None) -> List[str]:
        """
        Recommend skill proficiencies from a class that fit a character concept.
        
        Args:
            class_name (str): The character class
            character_concept (str, optional): Description of character concept
            
        Returns:
            List[str]: Recommended skill proficiencies
        """
        concept_text = f" who is {character_concept}" if character_concept else ""
        
        prompt = (
            f"For a {class_name}{concept_text} in D&D 5e (2024), which skill proficiencies "
            f"from the {class_name} class list would be most fitting? List only official "
            f"skill names as a comma-separated list."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        # Extract skills
        skills = [s.strip().lower() for s in response.split(',')]
        return [s for s in skills if s in self.standard_skills]
    
    def get_skills_for_custom_class(self, class_name: str) -> List[str]:
        """
        Get skill proficiency options for a custom or unofficial class.
        
        Args:
            class_name (str): Name of the custom class
            
        Returns:
            List[str]: List of skill proficiency options
        """
        prompt = (
            f"For a custom D&D 5e (2024) class called {class_name}, what would be the "
            f"most thematically appropriate skill proficiency options? Consider the name "
            f"and likely playstyle. List 6-8 official D&D skills as a comma-separated list."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        # Extract and validate skills
        skills = [s.strip().lower() for s in response.split(',')]
        return [s for s in skills if s in self.standard_skills]
    
    def get_skills_for_custom_background(self, background: str) -> List[str]:
        """
        Get skill proficiencies for a custom or unofficial background.
        
        Args:
            background (str): Name of the custom background
            
        Returns:
            List[str]: List of skill proficiencies
        """
        prompt = (
            f"For a custom D&D 5e (2024) background called {background}, what two skill "
            f"proficiencies would be most appropriate? Consider the background name and "
            f"likely character experiences. List exactly 2 official D&D skills."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        # Extract and validate skills
        skills = [s.strip().lower() for s in response.split(',')]
        valid_skills = [s for s in skills if s in self.standard_skills]
        
        # If we don't have exactly 2 skills, provide safe defaults based on the background name
        if len(valid_skills) != 2:
            return ["insight", "persuasion"]  # Generic fallback skills
        
        return valid_skills
    
    def explain_background_skills(self, background: str, skills: List[str]) -> Dict[str, str]:
        """
        Provide narrative reasons for why someone with a background would have these skills.
        
        Args:
            background (str): Character background
            skills (List[str]): List of skills from that background
            
        Returns:
            Dict[str, str]: Dictionary mapping skills to narrative explanations
        """
        skills_text = ", ".join(skills)
        
        prompt = (
            f"For someone with the {background} background in D&D 5e (2024), explain why they would "
            f"have developed proficiency specifically in these skills: {skills_text}. "
            f"What experiences in their past would have cultivated each skill? "
            f"Provide a brief explanation for each skill separately, focusing on narrative elements."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        # Parse the response into individual skill explanations
        explanations = {}
        current_skill = None
        current_explanation = []
        
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with a skill name
            skill_match = False
            for skill in skills:
                if re.match(rf'^{skill}', line.lower(), re.IGNORECASE):
                    # Save previous skill explanation if any
                    if current_skill and current_explanation:
                        explanations[current_skill] = ' '.join(current_explanation)
                    
                    # Start new skill
                    current_skill = skill
                    current_explanation = [re.sub(rf'^{skill}[:\-]*\s*', '', line, flags=re.IGNORECASE)]
                    skill_match = True
                    break
            
            if not skill_match and current_skill:
                current_explanation.append(line)
        
        # Add the last skill explanation
        if current_skill and current_explanation:
            explanations[current_skill] = ' '.join(current_explanation)
        
        # If parsing failed, create simple explanations
        if not explanations:
            return {skill: f"Their experience as a {background} helped develop this skill." for skill in skills}
        
        return explanations
    
    def generate_skill_story(self, skill_name: str, character_data: Dict[str, Any]) -> str:
        """
        Generate a brief narrative about how a character developed a particular skill.
        
        Args:
            skill_name (str): The skill name
            character_data (Dict): Character information including background, class, etc.
            
        Returns:
            str: A brief narrative about skill development
        """
        class_name = character_data.get("class", "adventurer")
        background = character_data.get("background", "wanderer")
        species = character_data.get("species", "humanoid")
        
        prompt = (
            f"Write a brief, engaging paragraph about how a {species} {class_name} with the "
            f"{background} background developed their {skill_name} skill. Include a formative "
            f"experience that shaped their approach to using this skill."
        )
        
        return self.ollama_service.generate_text(prompt, self.system_message)
    
    def suggest_skill_difficulty_checks(self, skill_name: str, context: str) -> Dict[str, int]:
        """
        Suggest appropriate DC ranges for different skill applications.
        
        Args:
            skill_name (str): The skill name
            context (str): The situation context
            
        Returns:
            Dict[str, int]: Dictionary mapping difficulty levels to DC values
        """
        prompt = (
            f"For a D&D 5e (2024) {skill_name} check in this situation: '{context}', "
            f"suggest appropriate DC values for Easy, Medium, Hard, and Very Hard difficulties. "
            f"Explain what might be accomplished at each DC. Format as JSON with difficulty names as keys."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                # Convert string DCs to integers if needed
                for key in result:
                    if isinstance(result[key], str) and result[key].isdigit():
                        result[key] = int(result[key])
                return result
        except:
            pass
        
        # Fallback standard DCs
        return {
            "Easy": 10,
            "Medium": 15, 
            "Hard": 20,
            "Very Hard": 25
        }
    
    def suggest_skill_synergies(self, primary_skill: str, scenario: str = None) -> List[Dict[str, str]]:
        """
        Suggest skills that could synergize with a primary skill.
        
        Args:
            primary_skill (str): The main skill
            scenario (str, optional): Optional scenario for context
            
        Returns:
            List[Dict[str, str]]: List of synergy dictionaries with skill and description
        """
        scenario_text = f" in this scenario: '{scenario}'" if scenario else ""
        
        prompt = (
            f"Suggest 3 D&D 5e (2024) skills that could synergize well with the {primary_skill} skill{scenario_text}. "
            f"For each skill, explain how they could work together for special outcomes. "
            f"Format as JSON array with objects containing 'skill' and 'synergy' fields."
        )
        
        response = self.ollama_service.generate_text(prompt, self.system_message)
        
        try:
            # Look for JSON array in the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except:
            pass
        
        # Fallback - extract skills manually
        synergies = []
        lines = response.split('\n')
        current_skill = None
        current_synergy = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            skill_match = False
            for skill in self.standard_skills:
                if re.match(rf'^{skill}', line.lower(), re.IGNORECASE):
                    # Save previous synergy if any
                    if current_skill and current_synergy:
                        synergies.append({
                            "skill": current_skill,
                            "synergy": ' '.join(current_synergy)
                        })
                    
                    # Start new skill
                    current_skill = skill
                    current_synergy = [re.sub(rf'^{skill}[:\-]*\s*', '', line, flags=re.IGNORECASE)]
                    skill_match = True
                    break
                    
            if not skill_match and current_skill:
                current_synergy.append(line)
        
        # Add the last synergy
        if current_skill and current_synergy:
            synergies.append({
                "skill": current_skill,
                "synergy": ' '.join(current_synergy)
            })
        
        # If parsing failed, return basic synergies
        if not synergies:
            similar_skills = [s for s in self.standard_skills if s != primary_skill][:3]
            synergies = [{"skill": s, "synergy": f"Can be combined with {primary_skill} for enhanced outcomes."} 
                         for s in similar_skills]
        
        return synergies[:3]  # Limit to 3 synergies