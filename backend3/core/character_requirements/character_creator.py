import json
import ollama
import re
from typing import Dict, Any, List

from backend3.core.character_requirements.character_sheet import CharacterSheet, ProficiencyLevel

class SimpleCharacterCreator:
    """A simplified character creator using Ollama/Llama3 LLM."""
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        """
        Initialize the character creator.
        
        Args:
            ollama_host: URL for the Ollama API server
        """
        self.character = CharacterSheet()
        self.conversation_history = []
        self.model = "llama3"
        
        # Initialize the Ollama client
        self.ollama_client = ollama.Client(host=ollama_host)
        
        # Verify model availability
        self._ensure_model_available()
        
        self.system_prompt = """
        You are a D&D character creation assistant. Create characters based on user descriptions.
        Always format your response as JSON with these fields:
        {
          "name": "Character Name",
          "species": "Species",
          "classes": {"Class Name": Level},
          "background": "Background",
          "alignment": ["Ethical", "Moral"],
          "ability_scores": {
            "strength": X, "dexterity": X, "constitution": X, 
            "intelligence": X, "wisdom": X, "charisma": X
          },
          "skill_proficiencies": ["Skill1", "Skill2"],
          "saving_throw_proficiencies": ["Ability1", "Ability2"],
          "personality_traits": ["Trait1", "Trait2"],
          "ideals": ["Ideal1"],
          "bonds": ["Bond1"],
          "flaws": ["Flaw1"],
          "armor": "Armor Type",
          "weapons": [{"name": "Weapon", "type": "simple/martial", "properties": ["property1"]}],
          "equipment": ["Item1", "Item2"],
          "backstory": "Brief character backstory"
        }
        
        If character is a spellcaster, include:
        {
          "spellcasting_ability": "ability",
          "spells_known": {
            "0": ["Cantrip1", "Cantrip2"],
            "1": ["1st Level Spell1", "1st Level Spell2"]
          }
        }
        
        Format your JSON properly with no extra text before or after.
        """

    def _ensure_model_available(self) -> None:
        """Verify that the required model is available, attempt to pull if not."""
        try:
            # List available models
            models = self.ollama_client.list()
            
            # Check if our model is in the list
            model_exists = any(model['name'] == self.model for model in models['models']) if 'models' in models else False
            
            if not model_exists:
                print(f"Model {self.model} not found. Attempting to pull...")
                self.ollama_client.pull(self.model)
                print(f"Successfully pulled {self.model}")
                
        except Exception as e:
            print(f"Warning: Could not verify model availability: {e}")
            print("Character creation may fail if the model is not available.")

    def call_llm(self, prompt: str) -> str:
        """Call the Ollama LLM with the given prompt."""
        try:
            response = self.ollama_client.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    *self.conversation_history,
                    {'role': 'user', 'content': prompt}
                ]
            )
            
            # Add to conversation history
            self.conversation_history.append({'role': 'user', 'content': prompt})
            self.conversation_history.append({'role': 'assistant', 'content': response['message']['content']})
            
            return response['message']['content']
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "{}"
    
    def extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response."""
        try:
            # Try to find JSON content using regex
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
            if json_match:
                json_content = json_match.group(1)
            else:
                # Try to find JSON between curly braces
                json_match = re.search(r'({[\s\S]*?})', text)
                if json_match:
                    json_content = json_match.group(1)
                else:
                    json_content = text
                    
            # Parse the JSON
            data = json.loads(json_content)
            return data
        except json.JSONDecodeError:
            print("Could not parse JSON from LLM response")
            print("Response was:", text)
            return {}
    
    def populate_character(self, character_data: Dict[str, Any]) -> None:
        """Populate character sheet with data from the LLM response."""
        try:
            # Basic identity
            if "name" in character_data:
                self.character.set_name(character_data["name"])
            
            if "species" in character_data:
                self.character.set_species(character_data["species"])
            
            # Classes and levels
            for class_name, level in character_data.get("classes", {}).items():
                self.character.set_class_level(class_name, level)
                
                # Set subclass if provided
                subclasses = character_data.get("subclasses", {})
                if subclasses and class_name in subclasses:
                    self.character.set_subclass(class_name, subclasses[class_name])
            
            # Background and alignment
            if "background" in character_data:
                self.character.set_background(character_data["background"])
            
            if "alignment" in character_data and len(character_data["alignment"]) == 2:
                self.character.set_alignment(character_data["alignment"][0], character_data["alignment"][1])
            
            # Ability scores
            for ability, score in character_data.get("ability_scores", {}).items():
                self.character.set_base_ability_score(ability, int(score))
            
            # Proficiencies
            for skill in character_data.get("skill_proficiencies", []):
                self.character.set_skill_proficiency(skill, ProficiencyLevel.PROFICIENT)
            
            for ability in character_data.get("saving_throw_proficiencies", []):
                self.character.set_saving_throw_proficiency(ability, ProficiencyLevel.PROFICIENT)
            
            # Equipment
            if "armor" in character_data:
                self.character.equip_armor(character_data["armor"])
            
            if character_data.get("shield", False):
                self.character.equip_shield()
            
            for weapon in character_data.get("weapons", []):
                self.character.add_weapon(weapon)
            
            for item in character_data.get("equipment", []):
                self.character.add_equipment({"name": item, "quantity": 1})
            
            # Spellcasting
            if "spellcasting_ability" in character_data:
                self.character.set_spellcasting_ability(character_data["spellcasting_ability"])
                
                for level_str, spells in character_data.get("spells_known", {}).items():
                    level = int(level_str)
                    for spell in spells:
                        self.character.add_spell_known(level, spell)
            
            # Personality
            for trait in character_data.get("personality_traits", []):
                self.character.add_personality_trait(trait)
            
            for ideal in character_data.get("ideals", []):
                self.character.add_ideal(ideal)
            
            for bond in character_data.get("bonds", []):
                self.character.add_bond(bond)
            
            for flaw in character_data.get("flaws", []):
                self.character.add_flaw(flaw)
            
            # Backstory
            if "backstory" in character_data:
                self.character.set_backstory(character_data["backstory"])
                
            # Calculate all derived stats
            self.character.calculate_all_derived_stats()
            
        except Exception as e:
            print(f"Error populating character: {e}")
    
    def create_character(self, description: str) -> Dict[str, Any]:
        """Create a character based on a description."""
        prompt = f"Create a D&D character based on this description: {description}"
        response = self.call_llm(prompt)
        character_data = self.extract_json(response)
        self.populate_character(character_data)
        return self.character.get_character_summary()
    
    def refine_character(self, feedback: str) -> Dict[str, Any]:
        """Refine the character based on feedback."""
        prompt = f"""
        Current character: 
        {json.dumps(self.character.get_character_summary(), indent=2)}
        
        Please modify this character based on the following feedback: {feedback}
        Provide changes in proper JSON format.
        """
        response = self.call_llm(prompt)
        changes = self.extract_json(response)
        self.populate_character(changes)
        return self.character.get_character_summary()
    
    def run_interactive_session(self) -> None:
        """Run an interactive character creation session."""
        print("Welcome to the D&D Character Creator!")
        print("What type of character would you like to create?")
        description = input("> ")
        
        # Create initial character
        try:
            summary = self.create_character(description)
            print("\nHere's your character:\n")
            print(json.dumps(summary, indent=2))
            
            # Refinement loop
            while True:
                print("\nWhat would you like to adjust? (or type 'done' to finish)")
                feedback = input("> ")
                
                if feedback.lower() == 'done':
                    break
                
                summary = self.refine_character(feedback)
                print("\nUpdated character:\n")
                print(json.dumps(summary, indent=2))
            
            # Save final character
            print("\nFinal Character Sheet:\n")
            print(self.character.get_character_summary_json())
            
        except Exception as e:
            print(f"An error occurred: {e}")
            
    def test_connection(self) -> bool:
        """Test the connection to the Ollama service."""
        try:
            response = self.ollama_client.generate(
                model=self.model,
                prompt="Hello, are you working properly?"
            )
            print(f"Connection test successful: {response['response'][:50]}...")
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

# Main entry point
if __name__ == "__main__":
    creator = SimpleCharacterCreator()
    creator.test_connection()
    creator.run_interactive_session()