# Central character state manager that:
# - Maintains complete character state
# - Broadcasts changes to interested components
# - Coordinates validation across domains
# - Preserves history for iterative refinement

import logging
import uuid
from typing import Dict, Any, List, Callable, Optional, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ChangeEvent:
    """Event representing a change to character data"""
    component: str  # e.g., "class", "background", "race"
    field: str      # e.g., "name", "abilities", "proficiencies" 
    old_value: Any  # Previous value
    new_value: Any  # New value
    character_id: str
    timestamp: float = field(default_factory=lambda: import time; return time.time())

class CharacterContextService:
    """
    Central service that maintains the complete state of characters being created/edited
    and coordinates interactions between different character creation components.
    """
    
    def __init__(self):
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.change_listeners: Dict[str, List[Callable[[ChangeEvent], None]]] = {
            "all": []  # Listeners for all events
        }
        self.validation_services: Dict[str, Any] = {}
    
    def create_character(self, initial_data: Dict[str, Any] = None) -> str:
        """
        Create a new character entry with a unique ID.
        
        Args:
            initial_data: Optional initial character data
            
        Returns:
            character_id: Unique identifier for the new character
        """
        character_id = str(uuid.uuid4())
        self.characters[character_id] = {
            "id": character_id,
            "created_at": import time; time.time(),
            "modified_at": import time; time.time(),
            "creation_stage": "initial",
            "validation_status": {},
            # Default empty structures for character components
            "name": "",
            "race": {},
            "class": {},
            "background": {},
            "abilities": {},
            "skills": {},
            "equipment": [],
            "spells": [],
            "features": [],
            "character_options": {},
            # Add any other necessary defaults
        }
        
        # Apply initial data if provided
        if initial_data:
            self.update_character(character_id, initial_data)
            
        return character_id
    
    def get_character(self, character_id: str) -> Dict[str, Any]:
        """Get the full character data by ID."""
        if character_id not in self.characters:
            raise ValueError(f"No character found with ID: {character_id}")
        return self.characters[character_id].copy()
    
    def update_character(self, character_id: str, updates: Dict[str, Any], 
                       component: str = None) -> Dict[str, Any]:
        """
        Update character data with new values.
        
        Args:
            character_id: Character identifier
            updates: Dictionary of updates to apply
            component: Optional component name for tracking changes (e.g., "class", "race")
            
        Returns:
            Updated character data
        """
        if character_id not in self.characters:
            raise ValueError(f"No character found with ID: {character_id}")
            
        character = self.characters[character_id]
        
        # Track changes to notify listeners
        changes = []
        
        # Apply updates and track changes
        for key, new_value in updates.items():
            old_value = character.get(key)
            if old_value != new_value:
                character[key] = new_value
                changes.append(ChangeEvent(
                    component=component or "general",
                    field=key,
                    old_value=old_value,
                    new_value=new_value,
                    character_id=character_id
                ))
        
        # Update modification time
        character["modified_at"] = import time; time.time()
        
        # Notify listeners about changes
        self._notify_listeners(changes)
        
        # Run validations if appropriate
        self._validate_character_updates(character_id, changes)
        
        return character.copy()
    
    def get_component(self, character_id: str, component: str) -> Any:
        """
        Get a specific component of a character.
        
        Args:
            character_id: Character identifier
            component: Component name (e.g., "class", "background")
            
        Returns:
            Component data
        """
        if character_id not in self.characters:
            raise ValueError(f"No character found with ID: {character_id}")
            
        character = self.characters[character_id]
        return character.get(component)
    
    def update_component(self, character_id: str, component: str, 
                       data: Any) -> Dict[str, Any]:
        """
        Update a specific component of a character.
        
        Args:
            character_id: Character identifier
            component: Component name (e.g., "class", "background")
            data: New component data
            
        Returns:
            Updated character data
        """
        if character_id not in self.characters:
            raise ValueError(f"No character found with ID: {character_id}")
            
        character = self.characters[character_id]
        old_value = character.get(component)
        
        # Create update dictionary
        updates = {component: data}
        
        return self.update_character(character_id, updates, component)
    
    def register_listener(self, callback: Callable[[ChangeEvent], None], 
                        components: List[str] = None) -> None:
        """
        Register a callback to be notified of character changes.
        
        Args:
            callback: Function to call when changes occur
            components: List of components to listen for (None for all)
        """
        if not components:
            self.change_listeners["all"].append(callback)
        else:
            for component in components:
                if component not in self.change_listeners:
                    self.change_listeners[component] = []
                self.change_listeners[component].append(callback)
    
    def register_validation_service(self, component: str, service: Any) -> None:
        """
        Register a validation service for a specific component.
        
        Args:
            component: Component name the service validates
            service: Validation service instance
        """
        self.validation_services[component] = service
    
    def validate_character(self, character_id: str, 
                         components: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Validate a character across multiple components.
        
        Args:
            character_id: Character identifier
            components: Components to validate (None for all)
            
        Returns:
            Dictionary mapping component names to lists of issues
        """
        if character_id not in self.characters:
            raise ValueError(f"No character found with ID: {character_id}")
            
        character = self.characters[character_id]
        validation_results = {}
        
        # Determine which components to validate
        to_validate = components or list(self.validation_services.keys())
        
        # Run validation for each component
        for component in to_validate:
            if component in self.validation_services:
                service = self.validation_services[component]
                component_data = character.get(component)
                
                try:
                    # Assume each validation service has a validate method
                    is_valid, issues = service.validate(component_data)
                    validation_results[component] = issues
                except Exception as e:
                    logger.error(f"Error validating {component}: {e}")
                    validation_results[component] = [{
                        "component": component,
                        "issue": f"Validation error: {str(e)}",
                        "severity": "error"
                    }]
        
        # Store validation results in character data
        character["validation_status"] = validation_results
        
        return validation_results
    
    def calculate_derived_values(self, character_id: str) -> Dict[str, Any]:
        """
        Calculate and update derived values based on current character state.
        E.g., ability modifiers, skill bonuses, etc.
        
        Args:
            character_id: Character identifier
            
        Returns:
            Dictionary of calculated derived values
        """
        if character_id not in self.characters:
            raise ValueError(f"No character found with ID: {character_id}")
            
        character = self.characters[character_id]
        derived = {}
        
        # Calculate ability modifiers
        abilities = character.get("abilities", {})
        ability_modifiers = {}
        for ability, score in abilities.items():
            ability_modifiers[ability] = (score - 10) // 2
        
        derived["ability_modifiers"] = ability_modifiers
        
        # Calculate proficiency bonus based on level
        character_level = self._calculate_character_level(character)
        derived["proficiency_bonus"] = 2 + ((character_level - 1) // 4)
        
        # Calculate skill bonuses
        skill_bonuses = self._calculate_skill_bonuses(character, derived["ability_modifiers"], 
                                                    derived["proficiency_bonus"])
        derived["skill_bonuses"] = skill_bonuses
        
        # Calculate saving throw bonuses
        saving_throw_bonuses = self._calculate_saving_throw_bonuses(character, 
                                                                 derived["ability_modifiers"],
                                                                 derived["proficiency_bonus"])
        derived["saving_throw_bonuses"] = saving_throw_bonuses
        
        # Update derived values in character data
        character["derived_values"] = derived
        
        return derived
    
    def detect_conflicts(self, character_id: str) -> List[Dict[str, Any]]:
        """
        Detect conflicts between different components of a character.
        E.g., incompatible choices, exceeding limits, etc.
        
        Args:
            character_id: Character identifier
            
        Returns:
            List of conflict issues
        """
        if character_id not in self.characters:
            raise ValueError(f"No character found with ID: {character_id}")
            
        character = self.characters[character_id]
        conflicts = []
        
        # Example conflict detection - duplicate proficiencies
        all_proficiencies = self._gather_all_proficiencies(character)
        duplicate_proficiencies = self._find_duplicate_proficiencies(all_proficiencies)
        
        for duplicate in duplicate_proficiencies:
            conflicts.append({
                "type": "duplicate_proficiency",
                "item": duplicate["proficiency"],
                "sources": duplicate["sources"],
                "severity": "warning",
                "message": f"Duplicate proficiency in {', '.join(duplicate['sources'])}"
            })
        
        # More conflict detection logic would go here...
        
        return conflicts
    
    def suggest_options(self, character_id: str, context: str) -> List[Dict[str, Any]]:
        """
        Suggest options for a character based on current state and context.
        E.g., recommend spells, feats, equipment based on class/background.
        
        Args:
            character_id: Character identifier
            context: Context for suggestions (e.g., "spells", "feats")
            
        Returns:
            List of suggestions
        """
        if character_id not in self.characters:
            raise ValueError(f"No character found with ID: {character_id}")
            
        character = self.characters[character_id]
        suggestions = []
        
        # Different suggestion logic based on context
        if context == "spells":
            suggestions = self._suggest_spells(character)
        elif context == "feats":
            suggestions = self._suggest_feats(character)
        elif context == "equipment":
            suggestions = self._suggest_equipment(character)
        
        return suggestions
    
    # ----- PRIVATE HELPER METHODS -----
    
    def _notify_listeners(self, changes: List[ChangeEvent]) -> None:
        """Notify registered listeners about changes."""
        for change in changes:
            # Notify general listeners
            for listener in self.change_listeners["all"]:
                try:
                    listener(change)
                except Exception as e:
                    logger.error(f"Error in change listener: {e}")
            
            # Notify component-specific listeners
            component = change.component
            if component in self.change_listeners:
                for listener in self.change_listeners[component]:
                    try:
                        listener(change)
                    except Exception as e:
                        logger.error(f"Error in {component} change listener: {e}")
    
    def _validate_character_updates(self, character_id: str, 
                                 changes: List[ChangeEvent]) -> None:
        """Validate character updates based on changes."""
        # Extract unique components that changed
        changed_components = set(change.component for change in changes)
        
        # Only validate affected components
        self.validate_character(character_id, list(changed_components))
    
    def _calculate_character_level(self, character: Dict[str, Any]) -> int:
        """Calculate total character level."""
        # This would need to handle multiclassing properly
        class_data = character.get("class", {})
        if isinstance(class_data, dict):
            return class_data.get("level", 1)
        return 1
    
    def _calculate_skill_bonuses(self, character: Dict[str, Any], 
                              ability_modifiers: Dict[str, int],
                              proficiency_bonus: int) -> Dict[str, int]:
        """Calculate skill bonuses based on abilities and proficiencies."""
        # Mapping of skills to their associated abilities
        skill_abilities = {
            "acrobatics": "dexterity",
            "animal_handling": "wisdom",
            "arcana": "intelligence",
            # Add all other skills...
        }
        
        skill_proficiencies = self._gather_skill_proficiencies(character)
        skill_bonuses = {}
        
        for skill, ability in skill_abilities.items():
            ability_mod = ability_modifiers.get(ability, 0)
            is_proficient = skill in skill_proficiencies
            expertise = skill in skill_proficiencies.get("expertise", [])
            
            if expertise:
                bonus = ability_mod + (proficiency_bonus * 2)
            elif is_proficient:
                bonus = ability_mod + proficiency_bonus
            else:
                bonus = ability_mod
                
            skill_bonuses[skill] = bonus
            
        return skill_bonuses
    
    def _calculate_saving_throw_bonuses(self, character: Dict[str, Any],
                                     ability_modifiers: Dict[str, int],
                                     proficiency_bonus: int) -> Dict[str, int]:
        """Calculate saving throw bonuses."""
        saving_throw_proficiencies = self._gather_saving_throw_proficiencies(character)
        saving_throw_bonuses = {}
        
        for ability, modifier in ability_modifiers.items():
            if ability in saving_throw_proficiencies:
                saving_throw_bonuses[ability] = modifier + proficiency_bonus
            else:
                saving_throw_bonuses[ability] = modifier
                
        return saving_throw_bonuses
    
    def _gather_all_proficiencies(self, character: Dict[str, Any]) -> Dict[str, List[str]]:
        """Gather all proficiencies from different sources."""
        proficiencies = {
            "skills": [],
            "weapons": [],
            "armor": [],
            "tools": [],
            "languages": [],
            "saving_throws": [],
            "sources": {}  # Track where each proficiency comes from
        }
        
        # Add proficiencies from race
        race = character.get("race", {})
        for category in ["skills", "weapons", "armor", "tools", "languages"]:
            race_profs = race.get(f"{category}_proficiencies", [])
            for prof in race_profs:
                proficiencies[category].append(prof)
                if prof not in proficiencies["sources"]:
                    proficiencies["sources"][prof] = []
                proficiencies["sources"][prof].append("race")
        
        # Add proficiencies from class
        class_data = character.get("class", {})
        for category in ["skills", "weapons", "armor", "tools"]:
            class_profs = class_data.get(f"{category}_proficiencies", [])
            for prof in class_profs:
                proficiencies[category].append(prof)
                if prof not in proficiencies["sources"]:
                    proficiencies["sources"][prof] = []
                proficiencies["sources"][prof].append("class")
        
        # Add saving throws from class
        saving_throws = class_data.get("saving_throw_proficiencies", [])
        for save in saving_throws:
            proficiencies["saving_throws"].append(save)
            if save not in proficiencies["sources"]:
                proficiencies["sources"][save] = []
            proficiencies["sources"][save].append("class")
        
        # Add proficiencies from background
        background = character.get("background", {})
        for category in ["skills", "tools", "languages"]:
            bg_profs = background.get(f"{category}", [])
            for prof in bg_profs:
                proficiencies[category].append(prof)
                if prof not in proficiencies["sources"]:
                    proficiencies["sources"][prof] = []
                proficiencies["sources"][prof].append("background")
        
        return proficiencies
    
    def _find_duplicate_proficiencies(self, proficiencies: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Find duplicate proficiencies across different sources."""
        duplicates = []
        sources = proficiencies.get("sources", {})
        
        for prof, source_list in sources.items():
            if len(source_list) > 1:
                duplicates.append({
                    "proficiency": prof,
                    "sources": source_list
                })
                
        return duplicates
    
    def _gather_skill_proficiencies(self, character: Dict[str, Any]) -> Dict[str, List[str]]:
        """Gather skill proficiencies from all sources."""
        result = {
            "proficient": [],
            "expertise": []
        }
        
        # From race
        race = character.get("race", {})
        race_skills = race.get("skill_proficiencies", [])
        result["proficient"].extend(race_skills)
        
        # From class
        class_data = character.get("class", {})
        class_skills = class_data.get("skill_proficiencies", [])
        result["proficient"].extend(class_skills)
        
        # From background
        background = character.get("background", {})
        bg_skills = background.get("skills", [])
        result["proficient"].extend(bg_skills)
        
        # From features (expertise)
        features = character.get("features", [])
        for feature in features:
            if feature.get("name", "").lower() == "expertise":
                expertise_skills = feature.get("skills", [])
                result["expertise"].extend(expertise_skills)
        
        return result
    
    def _gather_saving_throw_proficiencies(self, character: Dict[str, Any]) -> List[str]:
        """Gather saving throw proficiencies."""
        saving_throws = []
        
        # From class
        class_data = character.get("class", {})
        class_saves = class_data.get("saving_throw_proficiencies", [])
        saving_throws.extend(class_saves)
        
        # From features
        features = character.get("features", [])
        for feature in features:
            if feature.get("type", "") == "saving_throw_proficiency":
                feat_saves = feature.get("abilities", [])
                saving_throws.extend(feat_saves)
        
        return saving_throws
    
    def _suggest_spells(self, character: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest spells based on character class, level, and ability scores."""
        # This would need to be implemented based on spell data
        return []
    
    def _suggest_feats(self, character: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest feats based on character build."""
        # This would need to be implemented based on feat data
        return []
    
    def _suggest_equipment(self, character: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest equipment based on character class and background."""
        # This would need to be implemented based on equipment data
        return []