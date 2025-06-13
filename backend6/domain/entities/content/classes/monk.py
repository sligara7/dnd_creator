from typing import Dict, List, Any, Optional
from ....core.abstractions.character_class import AbstractCharacterClass, ClassFeature
from ....core.entities.character import Character

class Fighter(AbstractCharacterClass):
    """Concrete implementation of the Fighter class."""
    
    @property
    def class_name(self) -> str:
        return "Fighter"
    
    @property
    def hit_die(self) -> int:
        return 10
    
    @property
    def primary_ability(self) -> List[str]:
        return ["strength", "dexterity"]
    
    @property
    def saving_throw_proficiencies(self) -> List[str]:
        return ["strength", "constitution"]
    
    def get_class_features(self, level: int) -> List[ClassFeature]:
        """Get Fighter features for specified level."""
        features = []
        
        if level >= 1:
            features.append(ClassFeature(
                name="Fighting Style",
                description="Choose a fighting style specialty",
                level_acquired=1,
                feature_type="passive"
            ))
            features.append(ClassFeature(
                name="Second Wind",
                description="Recover hit points as a bonus action",
                level_acquired=1,
                feature_type="active",
                uses_per_rest="short"
            ))
        
        if level >= 2:
            features.append(ClassFeature(
                name="Action Surge",
                description="Take an additional action on your turn",
                level_acquired=2,
                feature_type="active",
                uses_per_rest="short"
            ))
        
        # ... more features by level
        
        return features
    
    def get_spellcasting_progression(self, level: int) -> Optional[Dict[str, Any]]:
        """Fighters don't have base spellcasting (some subclasses do)."""
        return None
    
    def validate_multiclass_prerequisites(self, character: Character) -> List[str]:
        """Validate Fighter multiclass prerequisites."""
        errors = []
        
        str_score = character.get_ability_score_value("strength")
        dex_score = character.get_ability_score_value("dexterity")
        
        if str_score < 13 and dex_score < 13:
            errors.append("Multiclass into Fighter requires Strength 13 or Dexterity 13")
        
        return errors