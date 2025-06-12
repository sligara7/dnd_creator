"""
Core content generation coordination service.

This service orchestrates content generation across all content types,
managing the creative pipeline from concept to validated content.
"""
from typing import Dict, List, Any, Optional, Union
from ..entities import CharacterConcept, GeneratedContent, ContentCollection
from ..value_objects import GenerationConstraints, ThematicElements, ContentMetadata
from ..abstractions import AbstractCharacterClass, AbstractSpecies, AbstractEquipment, AbstractSpell, AbstractFeat
from ..enums import ContentType, GenerationMethod
from ..exceptions import GenerationError, ContentGenerationTimeoutError

class ContentGeneratorService:
    """Core service for orchestrating content generation."""
    
    def __init__(self):
        self.generation_history: List[Dict[str, Any]] = []
        self.active_generators: Dict[ContentType, Any] = {}
    
    def generate_from_concept(
        self, 
        concept: CharacterConcept,
        content_types: List[ContentType],
        constraints: Optional[GenerationConstraints] = None
    ) -> ContentCollection:
        """
        Generate a complete content suite from a character concept.
        
        Args:
            concept: The character concept to generate from
            content_types: Types of content to generate
            constraints: Generation constraints and limits
            
        Returns:
            ContentCollection with all generated content
            
        Raises:
            GenerationError: If generation fails
            ContentGenerationTimeoutError: If generation times out
        """
        if not concept.background_story:
            raise GenerationError("Character concept must have background story")
        
        # Extract themes from concept
        thematic_elements = self._extract_themes_from_concept(concept)
        
        # Apply constraints
        effective_constraints = constraints or self._create_default_constraints()
        
        # Generate content collection
        collection = ContentCollection(
            collection_id=f"concept_{concept.concept_id}_{len(self.generation_history)}",
            name=f"Content for {concept.concept_name}",
            description=f"Generated content suite for {concept.concept_name}",
            content_items={},
            primary_themes=thematic_elements.primary_themes,
            creation_metadata=ContentMetadata.create_for_generation(
                created_by="content_generator",
                generation_method=GenerationMethod.CONCEPT_DRIVEN,
                source_concept=concept.concept_id
            )
        )
        
        # Generate each content type
        for content_type in content_types:
            try:
                generated_items = self._generate_content_type(
                    content_type, concept, thematic_elements, effective_constraints
                )
                if generated_items:
                    collection.content_items[content_type] = generated_items
            except Exception as e:
                # Log error but continue with other content types
                collection.creation_metadata.generation_errors.append(
                    f"Failed to generate {content_type.value}: {str(e)}"
                )
        
        # Record generation session
        self.generation_history.append({
            "concept_id": concept.concept_id,
            "content_types": [ct.value for ct in content_types],
            "collection_id": collection.collection_id,
            "success": len(collection.content_items) > 0,
            "timestamp": collection.creation_metadata.created_at
        })
        
        return collection
    
    def generate_single_content(
        self,
        content_type: ContentType,
        concept: CharacterConcept,
        constraints: Optional[GenerationConstraints] = None
    ) -> Optional[GeneratedContent]:
        """
        Generate a single piece of content.
        
        Args:
            content_type: Type of content to generate
            concept: Character concept for context
            constraints: Generation constraints
            
        Returns:
            Generated content or None if generation failed
        """
        thematic_elements = self._extract_themes_from_concept(concept)
        effective_constraints = constraints or self._create_default_constraints()
        
        items = self._generate_content_type(
            content_type, concept, thematic_elements, effective_constraints
        )
        
        return items[0] if items else None
    
    def _extract_themes_from_concept(self, concept: CharacterConcept) -> ThematicElements:
        """Extract thematic elements from character concept."""
        # This would integrate with theme analysis services
        return ThematicElements(
            primary_themes=getattr(concept, 'themes', []),
            theme_keywords=self._extract_keywords_from_background(concept.background_story),
            cultural_elements=getattr(concept, 'cultural_elements', []),
            power_level=getattr(concept, 'target_level', 1)
        )
    
    def _extract_keywords_from_background(self, background: str) -> List[str]:
        """Extract thematic keywords from background text."""
        # Simple keyword extraction - would be enhanced with NLP
        keywords = []
        theme_indicators = {
            'magic': ['magic', 'spell', 'wizard', 'sorcerer', 'arcane'],
            'nature': ['forest', 'wild', 'animal', 'druid', 'ranger'],
            'combat': ['warrior', 'fighter', 'battle', 'sword', 'armor'],
            'divine': ['god', 'temple', 'holy', 'paladin', 'cleric'],
            'stealth': ['shadow', 'thief', 'rogue', 'hidden', 'sneak']
        }
        
        background_lower = background.lower()
        for theme, indicators in theme_indicators.items():
            if any(indicator in background_lower for indicator in indicators):
                keywords.append(theme)
        
        return keywords
    
    def _generate_content_type(
        self,
        content_type: ContentType,
        concept: CharacterConcept,
        themes: ThematicElements,
        constraints: GenerationConstraints
    ) -> List[GeneratedContent]:
        """Generate content for a specific type."""
        # This would delegate to specific generators
        # For now, return placeholder content
        
        if content_type == ContentType.SPECIES:
            return self._generate_species(concept, themes, constraints)
        elif content_type == ContentType.CHARACTER_CLASS:
            return self._generate_class(concept, themes, constraints)
        elif content_type == ContentType.EQUIPMENT:
            return self._generate_equipment(concept, themes, constraints)
        elif content_type == ContentType.SPELL:
            return self._generate_spells(concept, themes, constraints)
        elif content_type == ContentType.FEAT:
            return self._generate_feats(concept, themes, constraints)
        else:
            return []
    
    def _generate_species(self, concept: CharacterConcept, themes: ThematicElements, constraints: GenerationConstraints) -> List[GeneratedContent]:
        """Generate species content."""
        # Placeholder - would integrate with species generator
        return [GeneratedContent(
            content_id=f"species_{concept.concept_id}",
            content_type=ContentType.SPECIES,
            name=f"{concept.concept_name} Heritage",
            description=f"Species inspired by {concept.background_story[:100]}...",
            mechanical_data={},
            thematic_elements=themes,
            metadata=ContentMetadata.create_for_generation("species_generator")
        )]
    
    def _generate_class(self, concept: CharacterConcept, themes: ThematicElements, constraints: GenerationConstraints) -> List[GeneratedContent]:
        """Generate class content."""
        # Placeholder - would integrate with class generator
        return [GeneratedContent(
            content_id=f"class_{concept.concept_id}",
            content_type=ContentType.CHARACTER_CLASS,
            name=f"{concept.concept_name} Path",
            description=f"Class inspired by {concept.background_story[:100]}...",
            mechanical_data={},
            thematic_elements=themes,
            metadata=ContentMetadata.create_for_generation("class_generator")
        )]
    
    def _generate_equipment(self, concept: CharacterConcept, themes: ThematicElements, constraints: GenerationConstraints) -> List[GeneratedContent]:
        """Generate equipment content."""
        # Placeholder - would integrate with equipment generator
        return [GeneratedContent(
            content_id=f"equipment_{concept.concept_id}",
            content_type=ContentType.EQUIPMENT,
            name=f"{concept.concept_name}'s Gear",
            description=f"Equipment inspired by {concept.background_story[:100]}...",
            mechanical_data={},
            thematic_elements=themes,
            metadata=ContentMetadata.create_for_generation("equipment_generator")
        )]
    
    def _generate_spells(self, concept: CharacterConcept, themes: ThematicElements, constraints: GenerationConstraints) -> List[GeneratedContent]:
        """Generate spell content."""
        # Placeholder - would integrate with spell generator
        return [GeneratedContent(
            content_id=f"spell_{concept.concept_id}",
            content_type=ContentType.SPELL,
            name=f"{concept.concept_name}'s Invocation",
            description=f"Spell inspired by {concept.background_story[:100]}...",
            mechanical_data={},
            thematic_elements=themes,
            metadata=ContentMetadata.create_for_generation("spell_generator")
        )]
    
    def _generate_feats(self, concept: CharacterConcept, themes: ThematicElements, constraints: GenerationConstraints) -> List[GeneratedContent]:
        """Generate feat content."""
        # Placeholder - would integrate with feat generator
        return [GeneratedContent(
            content_id=f"feat_{concept.concept_id}",
            content_type=ContentType.FEAT,
            name=f"{concept.concept_name}'s Mastery",
            description=f"Feat inspired by {concept.background_story[:100]}...",
            mechanical_data={},
            thematic_elements=themes,
            metadata=ContentMetadata.create_for_generation("feat_generator")
        )]
    
    def _create_default_constraints(self) -> GenerationConstraints:
        """Create default generation constraints."""
        return GenerationConstraints(
            max_complexity_score=1.0,
            required_themes=[],
            balance_thresholds={},
            generation_timeout=300,
            max_iterations=10,
            enforce_uniqueness=True
        )
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get statistics about generation history."""
        if not self.generation_history:
            return {"total_generations": 0}
        
        successful = sum(1 for session in self.generation_history if session["success"])
        content_type_counts = {}
        
        for session in self.generation_history:
            for content_type in session["content_types"]:
                content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
        
        return {
            "total_generations": len(self.generation_history),
            "successful_generations": successful,
            "success_rate": (successful / len(self.generation_history)) * 100,
            "content_type_distribution": content_type_counts,
            "most_generated_type": max(content_type_counts.items(), key=lambda x: x[1])[0] if content_type_counts else None
        }