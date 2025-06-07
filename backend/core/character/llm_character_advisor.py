"""
LLM Character Advisor Module

Provides AI-powered assistance for character creation and development using LLM integration.
Offers methods to generate character concepts, backstories, and optimization suggestions.
"""

from typing import Dict, List, Any, Optional, Union, Callable
import json
import datetime
import logging
from enum import Enum
from pathlib import Path

try:
    from backend.core.character.abstract_character import AbstractCharacterClass
except ImportError:
    # Fallback for development
    AbstractCharacterClass = object

logger = logging.getLogger(__name__)

class CharacterAspect(Enum):
    """Enum for different character aspects to generate or modify"""
    CONCEPT = "concept"
    BACKSTORY = "backstory"
    OPTIMIZATION = "optimization"
    NARRATIVE = "narrative"
    MECHANICS = "mechanics"
    DEVELOPMENT = "development"
    ROLEPLAYING = "roleplaying"
    VISUALS = "visuals"
    RESOLUTION = "resolution"
    ADAPTATION = "adaptation"
    CUSTOM = "custom"


class LLMCharacterAdvisor(AbstractCharacterClass):
    """
    Provides AI-powered assistance for D&D character creation and development.
    
    This class integrates with Language Learning Models (LLMs) to provide creative 
    and mechanical assistance for character creation, backstory development,
    optimization, and roleplaying guidance.
    """

    def __init__(self, llm_service, rules_data_path: str = None):
        """
        Initialize the LLM character advisor.
        
        Args:
            llm_service: LLM service client for generating responses
            rules_data_path: Optional path to D&D rules data
        """
        self.llm_service = llm_service
        
        # Set up rules data
        self.rules_data_path = Path(rules_data_path) if rules_data_path else Path("backend/data/rules")
        self._load_rules_data()
        
    def _load_rules_data(self):
        """Load rules data from JSON files."""
        self.rules_data = {}
        data_files = {
            "class_data": "classes.json",
            "species_data": "species.json", 
            "background_data": "backgrounds.json",
            "spell_data": "spells.json",
            "feat_data": "feats.json",
            "equipment_data": "equipment.json"
        }
        
        for data_key, filename in data_files.items():
            try:
                with open(self.rules_data_path / filename, "r") as f:
                    self.rules_data[data_key] = json.load(f)
            except FileNotFoundError:
                logger.warning(f"Could not load {filename}. Using empty data.")
                self.rules_data[data_key] = {}

    #---------------------------------------------------------------
    # Core LLM Generation Method - This centralizes the LLM interactions
    #---------------------------------------------------------------
    
    def generate_character_content(
        self, 
        aspect: CharacterAspect,
        character_data: Dict[str, Any] = None,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate any type of character content using the LLM.
        
        Args:
            aspect: Which aspect of character to generate
            character_data: Optional character data for context
            parameters: Additional parameters for generation
            
        Returns:
            Dictionary with generated content or error
        """
        try:
            # Create context data
            context = {
                "character_data": character_data or {},
                "parameters": parameters or {},
                "aspect": aspect.value
            }
            
            # Get appropriate prompt creator and parser functions
            prompt_creator, response_parser = self._get_handler_functions(aspect)
            
            # Create prompt
            prompt = prompt_creator(context)
            
            # Get LLM response
            llm_response = self.llm_service.generate_response(prompt)
            
            # Parse response
            parsed_content = response_parser(llm_response, context)
            
            # Add metadata
            parsed_content["metadata"] = {
                "generated_at": datetime.datetime.now().isoformat(),
                "aspect": aspect.value,
                **{f"param_{k}": v for k, v in (parameters or {}).items()}
            }
            
            return {
                "success": True,
                f"{aspect.value}_content": parsed_content
            }
            
        except Exception as e:
            logger.error(f"Error generating {aspect.value}: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate {aspect.value}: {str(e)}"
            }
    
    def _get_handler_functions(self, aspect: CharacterAspect) -> tuple:
        """Get the appropriate prompt creator and response parser for an aspect."""
        handlers = {
            CharacterAspect.CONCEPT: (self._create_concept_prompt, self._parse_concept_response),
            CharacterAspect.BACKSTORY: (self._create_backstory_prompt, self._parse_backstory_response),
            CharacterAspect.OPTIMIZATION: (self._create_optimization_prompt, self._parse_optimization_response),
            CharacterAspect.NARRATIVE: (self._create_narrative_prompt, self._parse_narrative_response),
            CharacterAspect.MECHANICS: (self._create_mechanics_prompt, self._parse_mechanics_response),
            CharacterAspect.DEVELOPMENT: (self._create_development_prompt, self._parse_development_response),
            CharacterAspect.ROLEPLAYING: (self._create_roleplaying_prompt, self._parse_roleplaying_response),
            CharacterAspect.VISUALS: (self._create_visuals_prompt, self._parse_visuals_response),
            CharacterAspect.RESOLUTION: (self._create_resolution_prompt, self._parse_resolution_response),
            CharacterAspect.ADAPTATION: (self._create_adaptation_prompt, self._parse_adaptation_response),
            CharacterAspect.CUSTOM: (self._create_custom_prompt, self._parse_custom_response)
        }
        
        return handlers.get(
            aspect, 
            (lambda ctx: "Generate content", lambda resp, ctx: {"content": resp})
        )

    #---------------------------------------------------------------
    # Simplified Public Methods - These replace the original detailed methods
    #---------------------------------------------------------------
    
    def generate_character_concept(self, concept_description: str) -> Dict[str, Any]:
        """Generate a character concept based on a description."""
        return self.generate_character_content(
            CharacterAspect.CONCEPT,
            parameters={"concept_description": concept_description}
        )
    
    def generate_backstory(self, 
                        character_data: Dict[str, Any], 
                        backstory_elements: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a character backstory."""
        return self.generate_character_content(
            CharacterAspect.BACKSTORY,
            character_data=character_data,
            parameters={"elements": backstory_elements or {}}
        )
    
    def suggest_character_optimization(self, 
                                    character_data: Dict[str, Any], 
                                    optimization_goal: str = "general") -> Dict[str, Any]:
        """Suggest character optimization based on a goal."""
        return self.generate_character_content(
            CharacterAspect.OPTIMIZATION,
            character_data=character_data,
            parameters={"goal": optimization_goal}
        )
    
    def suggest_narrative_elements(self, 
                               character_data: Dict[str, Any], 
                               narrative_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Suggest narrative elements like choices, moments, or approaches."""
        return self.generate_character_content(
            CharacterAspect.NARRATIVE,
            character_data=character_data,
            parameters=narrative_context
        )
    
    def explain_mechanics(self, 
                       character_data: Dict[str, Any], 
                       question: str) -> Dict[str, Any]:
        """Explain character mechanics."""
        return self.generate_character_content(
            CharacterAspect.MECHANICS,
            character_data=character_data,
            parameters={"question": question}
        )
    
    def suggest_character_development(self, 
                                   character_data: Dict[str, Any], 
                                   development_focus: Dict[str, Any] = None) -> Dict[str, Any]:
        """Suggest character development paths."""
        return self.generate_character_content(
            CharacterAspect.DEVELOPMENT,
            character_data=character_data,
            parameters=development_focus
        )
    
    def suggest_visual_elements(self, 
                             character_data: Dict[str, Any], 
                             visual_type: str = "portrait") -> Dict[str, Any]:
        """Create prompts for visual elements like portraits or symbols."""
        return self.generate_character_content(
            CharacterAspect.VISUALS,
            character_data=character_data,
            parameters={"type": visual_type}
        )
    
    def resolve_conflicts(self, 
                       character_data: Dict[str, Any], 
                       conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve character conflicts or inconsistencies."""
        return self.generate_character_content(
            CharacterAspect.RESOLUTION,
            character_data=character_data,
            parameters={"conflicts": conflicts}
        )
    
    #---------------------------------------------------------------
    # Character Adaptation Methods - For creative freedom
    #---------------------------------------------------------------
    
    def adapt_external_character(self, 
                              character_name: str, 
                              source: str, 
                              key_traits: List[str] = None, 
                              game_style: str = "authentic") -> Dict[str, Any]:
        """Adapt a character from literature, history, or other media to D&D."""
        return self.generate_character_content(
            CharacterAspect.ADAPTATION,
            parameters={
                "name": character_name,
                "source": source,
                "traits": key_traits or [],
                "style": game_style
            }
        )
    
    def adapt_concept_or_mechanics(self, 
                               concept_type: str, 
                               description: str, 
                               reference_elements: List[str] = None,
                               power_level: str = "balanced") -> Dict[str, Any]:
        """
        Universal adaptor for custom concepts, mechanics, etc.
        This covers all custom adaptations like:
        - Translating concept to mechanics
        - Reflavoring standard abilities
        - Creating custom features
        - Incorporating cultural elements
        - Creating resource systems
        - Integrating with settings
        """
        return self.generate_character_content(
            CharacterAspect.CUSTOM,
            parameters={
                "type": concept_type,
                "description": description,
                "references": reference_elements or [],
                "power_level": power_level
            }
        )
    
    #---------------------------------------------------------------
    # Prompt Creation Methods
    #---------------------------------------------------------------
    
    def _create_concept_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for character concept generation."""
        concept_description = context["parameters"].get("concept_description", "")
        
        return self._format_prompt(
            "Create a D&D character concept",
            concept_description,
            [
                "Character class recommendation with rationale",
                "Species (race) recommendation with rationale",
                "Background recommendation with rationale",
                "Suggested ability scores priority",
                "Personality traits that fit this concept",
                "Character motivation and goals"
            ]
        )
    
    def _create_backstory_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for backstory generation."""
        character_summary = self._create_character_summary(context["character_data"])
        elements = context["parameters"].get("elements", {})
        elements_text = ", ".join(f"{k}: {v}" for k, v in elements.items())
        
        return self._format_prompt(
            "Create a character backstory",
            f"Character: {character_summary}\nBackstory elements: {elements_text}",
            [
                "Origin and early life",
                "Formative events that shaped the character",
                "How they acquired their class abilities",
                "Key relationships and connections",
                "Events that led them to their adventuring life",
                "Current goals and motivations"
            ]
        )
    
    def _create_optimization_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for optimization suggestions."""
        character_summary = self._create_character_summary(context["character_data"])
        goal = context["parameters"].get("goal", "general improvement")
        
        return self._format_prompt(
            f"Optimize this character for {goal}",
            f"Character: {character_summary}",
            [
                "Ability score adjustments",
                "Skill selection recommendations",
                "Equipment suggestions",
                "Feat recommendations (if applicable)",
                "Spell selections (if applicable)",
                "Multiclass options (if beneficial)"
            ]
        )
    
    def _create_narrative_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for narrative elements."""
        character_summary = self._create_character_summary(context["character_data"])
        
        # Handle various narrative contexts
        if "scenario" in context["parameters"]:
            narrative_type = "roleplaying scenario"
            focus = context["parameters"]["scenario"]
            items = [
                "Initial reaction",
                "Key personality traits to emphasize",
                "Dialogue examples and speech patterns",
                "Body language and mannerisms",
                "Internal thoughts vs. external actions"
            ]
        elif "situation" in context["parameters"]:
            narrative_type = "character moments"
            focus = context["parameters"]["situation"]
            items = [
                "3-4 brief narrative vignettes",
                "Dialogue that reflects their way of speaking",
                "How they display their abilities and traits",
                "What makes their approach unique"
            ]
        elif "decision_point" in context["parameters"]:
            narrative_type = "decision point"
            decision = context["parameters"]["decision_point"]
            focus = f"Decision: {decision.get('situation', '')}"
            options = "\n".join([f"- {option}" for option in decision.get("options", [])])
            focus = f"{focus}\nOptions:\n{options}"
            items = [
                "Likelihood of choosing each option",
                "Character's thought process",
                "Alignment with character traits",
                "Additional in-character options"
            ]
        else:
            narrative_type = "general narrative"
            focus = "Provide general narrative guidance for this character"
            items = [
                "Character voice and mannerisms",
                "Typical reactions to common situations",
                "Relationship dynamics",
                "Personal quirks to emphasize"
            ]
            
        return self._format_prompt(
            f"Create {narrative_type} content",
            f"Character: {character_summary}\n{focus}",
            items
        )
    
    def _create_mechanics_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for mechanics explanations."""
        character_summary = self._create_character_summary(context["character_data"])
        question = context["parameters"].get("question", "")
        
        return self._format_prompt(
            "Explain character mechanics",
            f"Character: {character_summary}\nQuestion: {question}",
            [
                "Clear explanation of the relevant rules",
                "How these mechanics apply to this character specifically",
                "Examples of how this works in play",
                "Tips for using these mechanics effectively"
            ]
        )
    
    def _create_development_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for character development."""
        character_summary = self._create_character_summary(context["character_data"])
        development_focus = context["parameters"]
        goals_text = ", ".join(f"{k}: {v}" for k, v in development_focus.items() if k != "timeframe")
        timeframe = development_focus.get("timeframe", "full character arc")
        
        return self._format_prompt(
            f"Create a character development plan ({timeframe})",
            f"Character: {character_summary}\nGoals and focus: {goals_text}",
            [
                "Short-term development milestones",
                "Medium-term growth opportunities",
                "Long-term character arc",
                "Skills and abilities to focus on developing",
                "Narrative challenges to drive growth",
                "Relationships to cultivate"
            ]
        )
    
    def _create_visuals_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for visual elements."""
        character_summary = self._create_character_summary(context["character_data"])
        visual_type = context["parameters"].get("type", "portrait")
        
        elements = [
            "Physical appearance details",
            "Clothing and armor description",
            "Weapons and equipment",
            "Pose and expression",
            "Lighting and background suggestions",
            "Artistic style recommendations"
        ]
        
        if visual_type == "symbol":
            elements = [
                "Symbolic elements representing the character",
                "Color scheme and meaning",
                "Design motifs",
                "Style and presentation",
                "How it represents the character's essence"
            ]
            
        return self._format_prompt(
            f"Create a {visual_type} prompt",
            f"Character: {character_summary}",
            elements
        )
    
    def _create_resolution_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for conflict resolution."""
        character_summary = self._create_character_summary(context["character_data"])
        conflicts = context["parameters"].get("conflicts", [])
        
        conflicts_text = "\n".join([
            f"- {conflict.get('type', 'Unknown conflict')}: {conflict.get('description', 'No description')}"
            for conflict in conflicts
        ])
        
        return self._format_prompt(
            "Resolve character conflicts",
            f"Character: {character_summary}\nConflicts:\n{conflicts_text}",
            [
                "Analysis of why each conflict exists",
                "2-3 possible resolution approaches per conflict",
                "Best recommendation for each conflict",
                "How to integrate resolutions into the character's narrative"
            ]
        )
    
    def _create_adaptation_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for external character adaptation."""
        params = context["parameters"]
        name = params.get("name", "")
        source = params.get("source", "")
        traits = params.get("traits", [])
        style = params.get("style", "authentic")
        
        traits_text = "\n".join([f"- {trait}" for trait in traits])
        
        approach_guidance = {
            "authentic": "Focus on creating a faithful adaptation that captures the essence of the original character while working within D&D mechanics. Prioritize thematic accuracy over mechanical optimization.",
            "fantastical": "Adapt the character with a focus on creating interesting and powerful game mechanics, even if it means taking creative liberties with the source material.",
            "modern": "Update the character for a modern context while preserving their core identity. Consider how their traits would manifest in today's world."
        }
        
        return self._format_prompt(
            f"Adapt {name} from {source} to D&D",
            f"Character: {name}\nSource: {source}\nKey traits:\n{traits_text}\nAdaptation style: {style}\n\nGuidance: {approach_guidance.get(style, '')}",
            [
                "Recommended class and subclass with rationale",
                "Species (race) selection with justification",
                "Background that reflects their origin",
                "Ability score distribution",
                "Key skill proficiencies",
                "Signature abilities and how they translate to D&D mechanics",
                "Equipment and items that reflect their iconic gear",
                "Personality traits to roleplay",
                "Backstory adaptation"
            ]
        )
    
    def _create_custom_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for custom concept adaptation."""
        params = context["parameters"]
        concept_type = params.get("type", "")
        description = params.get("description", "")
        references = params.get("references", [])
        power_level = params.get("power_level", "balanced")
        
        references_text = "\n".join([f"- {ref}" for ref in references]) if references else "None provided"
        
        # Customize instructions based on concept type
        if concept_type == "translate_abilities":
            title = "Translate conceptual abilities to D&D mechanics"
            items = [
                "Game mechanics that represent these abilities",
                "Required class features or spells",
                "Balance considerations and limitations",
                "How to implement within existing D&D rules",
                "Suggested level progression"
            ]
        elif concept_type == "reflavor_ability":
            title = "Reflavor standard D&D ability"
            items = [
                "New thematic description",
                "Visual effects and appearance",
                "Roleplaying opportunities",
                "Mechanical implications (if any)",
                "Integration with character concept"
            ]
        elif concept_type == "cultural_elements":
            title = "Incorporate cultural elements"
            items = [
                "Cultural equipment and attire",
                "Traditions and practices",
                "Values and beliefs",
                "Language and communication style",
                "Social structures and relationships"
            ]
        elif concept_type == "custom_feature":
            title = "Create custom character feature"
            items = [
                "Feature name and description",
                "Mechanical benefits and limitations",
                "Usage frequency and conditions",
                "Scaling with character level",
                "Balance considerations"
            ]
        elif concept_type == "resource_system":
            title = "Design custom resource system"
            items = [
                "Resource name and thematic description",
                "How resources are gained and spent",
                "Maximum capacity and limitations",
                "Special abilities enabled by resources",
                "Integration with existing D&D mechanics"
            ]
        else:
            title = f"Adapt {concept_type} concept to D&D"
            items = [
                "D&D mechanics that best represent this concept",
                "Required adjustments to make it work",
                "Balance considerations",
                "Roleplaying guidance",
                "Integration with existing rules"
            ]
            
        power_guidance = {
            "low": "Create a modest implementation that's slightly below average power level",
            "balanced": "Create a balanced implementation comparable to official D&D content",
            "high": "Create a powerful implementation that's slightly above average",
            "exceptional": "Create a uniquely powerful implementation for high-powered campaigns"
        }
        
        return self._format_prompt(
            title,
            f"Concept: {description}\nReference elements:\n{references_text}\nPower level: {power_level} - {power_guidance.get(power_level, '')}",
            items
        )
    
    #---------------------------------------------------------------
    # Response Parsing Methods
    #---------------------------------------------------------------
    
    def _parse_concept_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response for character concept."""
        return self._extract_structured_data(response, default_structure={
            "class": {"suggestion": "Unknown", "rationale": ""},
            "species": {"suggestion": "Unknown", "rationale": ""},
            "background": {"suggestion": "Unknown", "rationale": ""},
            "ability_scores": {"priority": []},
            "personality": {"traits": [], "motivation": ""}
        })
    
    def _parse_backstory_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response for backstory."""
        return self._extract_structured_data(response, default_structure={
            "origin": "",
            "formative_events": [],
            "connections": [],
            "abilities_source": "",
            "adventuring_catalyst": "",
            "goals": []
        })
    
    def _parse_optimization_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response for optimization suggestions."""
        return self._extract_structured_data(response, default_structure={
            "ability_scores": [],
            "skills": [],
            "equipment": [],
            "feats": [],
            "spells": [],
            "multiclass": [],
            "general_advice": ""
        })
    
    def _parse_narrative_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response for narrative elements."""
        if "scenario" in context["parameters"]:
            default_structure = {
                "initial_reaction": "",
                "key_traits": [],
                "dialogue_examples": [],
                "mannerisms": "",
                "internal_vs_external": ""
            }
        elif "situation" in context["parameters"]:
            default_structure = {
                "vignettes": [
                    {"title": "Moment 1", "content": ""},
                    {"title": "Moment 2", "content": ""}
                ]
            }
        elif "decision_point" in context["parameters"]:
            default_structure = {
                "options": [
                    {"option": "", "likelihood": "", "rationale": ""}
                ],
                "additional_options": []
            }
        else:
            default_structure = {
                "voice": "",
                "reactions": {},
                "relationships": {},
                "quirks": []
            }
            
        return self._extract_structured_data(response, default_structure)
    
    def _parse_mechanics_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response for mechanics explanations."""
        return self._extract_structured_data(response, default_structure={
            "rules_explanation": "",
            "character_specific_context": "",
            "examples": [],
            "tips": []
        })
    
    def _parse_development_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response for development suggestions."""
        return self._extract_structured_data(response, default_structure={
            "short_term": [],
            "medium_term": [],
            "long_term": [],
            "abilities_focus": [],
            "narrative_challenges": [],
            "relationships": []
        })
    
    def _parse_visuals_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response for visual elements."""
        visual_type = context["parameters"].get("type", "portrait")
        
        if visual_type == "symbol":
            default_structure = {
                "symbols": [],
                "colors": {},
                "motifs": [],
                "style": "",
                "meaning": ""
            }
        else:
            default_structure = {
                "physical_description": "",
                "clothing_and_equipment": "",
                "pose_and_expression": "",
                "lighting_and_background": "",
                "artistic_style": "",
                "complete_prompt": ""
            }
            
        return self._extract_structured_data(response, default_structure)
    
    def _parse_resolution_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response for conflict resolutions."""
        return self._extract_structured_data(response, default_structure={
            "resolutions": [
                {
                    "conflict_type": "",
                    "analysis": "",
                    "options": [],
                    "recommendation": "",
                    "integration": ""
                }
            ]
        })
    
    def _parse_adaptation_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response for character adaptation."""
        return self._extract_structured_data(response, default_structure={
            "class": {"name": "", "subclass": "", "rationale": ""},
            "species": {"name": "", "rationale": ""},
            "background": {"name": "", "rationale": ""},
            "ability_scores": {},
            "skills": [],
            "signature_abilities": [],
            "equipment": [],
            "personality": [],
            "backstory": ""
        })
    
    def _parse_custom_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response for custom concept adaptation."""
        concept_type = context["parameters"].get("type", "")
        
        # Different default structures based on concept type
        if concept_type == "translate_abilities":
            default_structure = {
                "mechanics": [],
                "features": [],
                "balance": {},
                "implementation": "",
                "progression": {}
            }
        elif concept_type == "reflavor_ability":
            default_structure = {
                "new_description": "",
                "visual_effects": "",
                "roleplaying": [],
                "mechanics": {},
                "integration": ""
            }
        elif concept_type == "custom_feature":
            default_structure = {
                "name": "",
                "description": "",
                "mechanics": {},
                "limitations": "",
                "scaling": {}
            }
        elif concept_type == "resource_system":
            default_structure = {
                "name": "",
                "description": "",
                "acquisition": "",
                "expenditure": "",
                "limitations": "",
                "abilities": []
            }
        else:
            default_structure = {
                "mechanics": {},
                "adjustments": [],
                "balance": {},
                "roleplaying": "",
                "integration": ""
            }
            
        return self._extract_structured_data(response, default_structure)
    
    #---------------------------------------------------------------
    # Helper Methods
    #---------------------------------------------------------------
    
    def _format_prompt(self, title: str, context: str, elements: List[str]) -> str:
        """Format a standard prompt with consistent structure."""
        elements_text = "\n".join([f"- {element}" for element in elements])
        
        return (
            f"# {title}\n\n"
            f"{context}\n\n"
            f"Include the following elements:\n{elements_text}\n\n"
            "Format your response as structured data that can be parsed into a JSON object."
        )
    
    def _create_character_summary(self, character_data: Dict[str, Any]) -> str:
        """Create a brief character summary for context in prompts."""
        # Handle case where character data is empty
        if not character_data:
            return "New character under development"
            
        name = character_data.get("name", "Unnamed character")
        
        # Extract basic character info using safe gets with defaults
        species = self._safe_get(character_data, ["species", "name"], "Unknown species")
        class_name = self._safe_get(character_data, ["class", "name"], "Unknown class")
        level = self._safe_get(character_data, ["class", "level"], 1)
        background = self._safe_get(character_data, ["background", "name"], "Unknown background")
        
        # Collect personality traits if available
        personality_parts = []
        personality = character_data.get("personality", {})
        
        for trait_type in ["traits", "ideals", "bonds", "flaws"]:
            traits = personality.get(trait_type, [])
            if traits and len(traits) > 0:
                trait_name = trait_type.rstrip('s').capitalize() # Remove plural 's' if present
                personality_parts.append(f"{trait_name}: {traits[0]}")
        
        personality_text = f" ({'; '.join(personality_parts)})" if personality_parts else ""
        
        # Add ability scores if available
        ability_text = ""
        if "ability_scores" in character_data:
            scores = character_data["ability_scores"]
            if scores:
                top_abilities = sorted(
                    [(k.capitalize(), v) for k, v in scores.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:2]
                ability_text = f" Top abilities: {top_abilities[0][0]} ({top_abilities[0][1]}), {top_abilities[1][0]} ({top_abilities[1][1]})."
        
        return f"{name}, level {level} {species} {class_name} with {background} background{personality_text}.{ability_text}"
    
    def _safe_get(self, data_dict: Dict[str, Any], key_path: List[str], default: Any = None) -> Any:
        """Safely get a nested value from a dictionary."""
        current = data_dict
        for key in key_path:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current
    
    def _extract_structured_data(self, response: str, default_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from LLM response with fallback to default structure."""
        # First try to extract JSON directly
        try:
            # Look for JSON patterns
            import re
            import json
            
            # Try to match JSON inside the response
            json_pattern = r'```(?:json)?\s*({[\s\S]*?}|[[\s\S]*?])\s*```|({[\s\S]*}|[[\s\S]*])'
            matches = re.search(json_pattern, response)
            
            if matches:
                json_str = matches.group(1) or matches.group(2)
                parsed_data = json.loads(json_str)
                
                # Ensure all expected keys are present
                for key, default_value in default_structure.items():
                    if key not in parsed_data:
                        parsed_data[key] = default_value
                        
                return parsed_data
        except Exception as e:
            logger.warning(f"Failed to parse JSON from response: {str(e)}")
        
        # If JSON parsing fails, try to extract structured data based on headings
        try:
            # Simple extraction based on common patterns in the response
            result = default_structure.copy()
            result["full_response"] = response
            
            return result
        except Exception as e:
            logger.error(f"Failed to extract structured data: {str(e)}")
            
            # Return default structure with full response
            result = default_structure.copy()
            result["full_response"] = response
            return result