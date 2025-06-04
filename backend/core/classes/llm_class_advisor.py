from backend.core.ollama_service import OllamaService

class LLMClassAdvisor:
    """Service for generating custom character classes using LLM"""
    
    def __init__(self, llm_service=None):
        """Initialize with optional custom LLM service"""
        self.llm_service = llm_service or OllamaService()
    
    def _create_prompt(self, task, context):
        """Create a well-structured prompt for the LLM."""
        system_context = "You are a D&D 5e (2024 rules) game designer specializing in balanced class creation."
        instructions = f"Based on the following information, {task}. Focus on game balance and D&D 5e design principles."
        
        prompt = f"{system_context}\n\n{instructions}\n\nInformation: {context}"
        return prompt
    
    def _extract_json(self, response):
        """Extract JSON from LLM response."""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return None
    
    def generate_class_concept(self, concept_description: str) -> Dict[str, Any]:
        """Generate a high-level class concept based on a description."""
        prompt = self._create_prompt(
            "create a D&D character class concept",
            f"Concept: {concept_description}\n\n"
            f"Generate a high-level concept for this class including: name, brief description, "
            f"playstyle summary, primary abilities, and a unique class mechanic. Return as JSON."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            concept_data = self._extract_json(response)
            if concept_data:
                return concept_data
        except Exception as e:
            print(f"Error generating class concept: {e}")
        
        # Fallback
        return {
            "name": concept_description.split()[0].capitalize() + "master",
            "description": f"A class based on the concept: {concept_description}",
            "playstyle": "Balanced between combat and utility abilities",
            "primary_abilities": ["Dexterity", "Wisdom"],
            "unique_mechanic": "Adaptability in various situations"
        }
    
    def generate_complete_class(self, concept: str = None, partial_data: Dict[str, Any] = None) -> CustomClass:
        """Generate a complete custom class with all required attributes."""
        if not concept and not partial_data:
            raise ValueError("Must provide either concept or partial_data")
        
        if partial_data:
            context = f"Partial class data: {json.dumps(partial_data)}\n\n"
            context += "Fill in all missing attributes to create a complete, balanced class."
            task = "complete this partial class definition"
        else:
            context = f"Class concept: {concept}\n\n"
            context += "Create a complete, balanced character class based on this concept."
            task = "create a complete custom character class"
        
        prompt = self._create_prompt(
            task,
            context + "\n\n"
            "Include the following attributes in your JSON response:\n"
            "- name: The class name\n"
            "- description: Class description\n"
            "- hit_die: Hit die size (6, 8, 10, or 12)\n"
            "- primary_ability: Array of primary abilities\n"
            "- saving_throw_proficiencies: Array of saving throw proficiencies (max 2)\n"
            "- armor_proficiencies: Array of armor proficiencies\n"
            "- weapon_proficiencies: Array of weapon proficiencies\n"
            "- skill_proficiencies: Object with 'choose' (number) and 'from' (array of skills)\n"
            "- tool_proficiencies: Array of tool proficiencies\n"
            "- starting_equipment: Object with equipment options\n"
            "- class_features: Object mapping levels (1-20) to arrays of features\n"
            "- spellcasting_type: 'none', 'full', 'half', 'third', 'pact', or 'unique'\n"
            "- spellcasting_ability: Ability used for spellcasting (if applicable)\n"
            "- class_resources: Object describing class-specific resources\n"
            "- multiclass_requirements: Object mapping abilities to minimum scores\n"
            "- flavor_text: Object with flavor elements"
        )
        
        try:
            response = self.llm_service.generate(prompt)
            class_data = self._extract_json(response)
            
            if class_data:
                # Convert spellcasting type string to enum
                if "spellcasting_type" in class_data:
                    try:
                        class_data["spellcasting_type"] = SpellcastingType(class_data["spellcasting_type"])
                    except ValueError:
                        class_data["spellcasting_type"] = SpellcastingType.NONE
                
                # Create the custom class
                return CustomClass(**class_data)
        except Exception as e:
            print(f"Error generating complete class: {e}")
        
        # Fallback if LLM fails
        name = (partial_data or {}).get("name", f"Custom{concept.split()[0].title()}") if concept else "CustomClass"
        return CustomClass(
            name=name,
            description=concept or "Custom character class"
        )
    
    def generate_class_feature(self, class_name: str, level: int, 
                             feature_concept: str) -> Dict[str, Any]:
        """Generate a class feature for a specific level."""
        prompt = self._create_prompt(
            "create a balanced class feature",
            f"Class: {class_name}\nLevel: {level}\nConcept: {feature_concept}\n\n"
            f"Create a balanced and thematic class feature appropriate for this level. "
            f"It should fit the class theme and be comparable in power to official classes. "
            f"Return as JSON with 'name', 'description', 'mechanics', 'limitations' (e.g., uses per day)."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            feature_data = self._extract_json(response)
            
            if feature_data:
                return feature_data
        except Exception as e:
            print(f"Error generating class feature: {e}")
        
        # Fallback
        return {
            "name": f"{feature_concept.split()[0].title()} Technique",
            "description": f"A technique based on {feature_concept}.",
            "mechanics": "You can use an action to activate this ability.",
            "limitations": "You can use this feature a number of times equal to your proficiency bonus per long rest."
        }
    
    def generate_subclass(self, base_class_name: str, 
                        subclass_concept: str) -> Dict[str, Any]:
        """Generate a subclass for a base class."""
        prompt = self._create_prompt(
            "create a character subclass",
            f"Base Class: {base_class_name}\nSubclass Concept: {subclass_concept}\n\n"
            f"Create a balanced and thematic subclass that specializes the base class according to the concept. "
            f"Include features at the appropriate levels for subclasses of this type. "
            f"Return as JSON with 'name', 'description', and 'features' (mapping levels to feature arrays)."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            subclass_data = self._extract_json(response)
            
            if subclass_data:
                return subclass_data
        except Exception as e:
            print(f"Error generating subclass: {e}")
        
        # Fallback
        return {
            "name": f"{subclass_concept.split()[0].title()} {base_class_name}",
            "description": f"A {base_class_name} that specializes in {subclass_concept}.",
            "features": {
                3: [{"name": "Specialization Feature", "description": f"You gain abilities related to {subclass_concept}."}]
            }
        }
    
    def balance_class(self, custom_class: CustomClass) -> CustomClass:
        """Balance a custom class to ensure it follows D&D design principles."""
        prompt = self._create_prompt(
            "balance this custom class",
            f"Class definition: {json.dumps(custom_class.to_dict())}\n\n"
            f"Review this class for balance issues according to D&D 5e (2024) design principles.\n"
            f"Check for:\n"
            f"1. Appropriate power level compared to official classes\n"
            f"2. Expected number of features per level\n"
            f"3. Balanced saving throw proficiencies (usually one strong, one weak)\n"
            f"4. Appropriate hit die size\n"
            f"5. Resource scaling that matches class power\n\n"
            f"Return the balanced version as JSON with the same structure."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            balanced_data = self._extract_json(response)
            
            if balanced_data:
                # Convert spellcasting type string to enum if needed
                if "spellcasting_type" in balanced_data:
                    try:
                        balanced_data["spellcasting_type"] = SpellcastingType(balanced_data["spellcasting_type"])
                    except ValueError:
                        balanced_data["spellcasting_type"] = custom_class.spellcasting_type
                
                # Create balanced class
                return CustomClass(**balanced_data)
        except Exception as e:
            print(f"Error balancing class: {e}")
        
        # Return original if balancing fails
        return custom_class
    
    def generate_starting_equipment(self, class_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate starting equipment options for a class."""
        prompt = self._create_prompt(
            "create starting equipment options",
            f"Class: {json.dumps(class_data)}\n\n"
            f"Create balanced and thematic starting equipment options for this class. "
            f"Consider the class's proficiencies, playstyle, and typical role in an adventuring party. "
            f"Return as JSON with 'options' array containing different equipment packages."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            equipment_data = self._extract_json(response)
            
            if equipment_data:
                return equipment_data
        except Exception as e:
            print(f"Error generating starting equipment: {e}")
        
        # Fallback
        return {
            "options": [
                {"items": ["A simple weapon", "Explorer's Pack", "10 darts"]},
                {"items": ["A martial weapon", "Dungeoneer's Pack", "Shield"]}
            ]
        }
    
    def suggest_multiclass_combinations(self, class_name: str) -> List[Dict[str, Any]]:
        """Suggest effective multiclass combinations for a class."""
        prompt = self._create_prompt(
            "suggest multiclass combinations",
            f"Class: {class_name}\n\n"
            f"Suggest 3-5 effective multiclass combinations with this class. "
            f"For each, explain why the combination works well, what levels to take in each class, "
            f"and what synergies to look for. Return as JSON array with objects containing "
            f"'classes', 'synergy', 'level_split', and 'build_focus' keys."
        )
        
        try:
            response = self.llm_service.generate(prompt)
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            print(f"Error generating multiclass suggestions: {e}")
        
        # Fallback
        return [
            {
                "classes": f"{class_name}/Fighter",
                "synergy": "Adds combat durability and fighting styles",
                "level_split": f"{class_name} X/Fighter 2",
                "build_focus": "Combat enhancement"
            },
            {
                "classes": f"{class_name}/Rogue",
                "synergy": "Adds skills and sneak attack",
                "level_split": f"{class_name} X/Rogue 3",
                "build_focus": "Skill utility and damage"
            }
        ]

