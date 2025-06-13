# ├── services/              # NEW: Domain Services
# │   ├── __init__.py
# │   ├── validation_coordinator.py
# │   ├── content_generator.py
# │   └── balance_analyzer.py
"""
Balance analysis service for generated content.

This service analyzes the mechanical balance of generated content,
ensuring it fits within D&D's power level expectations.
"""
from typing import Dict, List, Any, Optional, Tuple
from ..entities import GeneratedContent, ContentCollection
from ..value_objects import BalanceMetrics
from ..enums import ContentType, ContentRarity
from ..exceptions import BalanceViolation

class BalanceAnalyzerService:
    """Service for analyzing content balance and power levels."""
    
    def __init__(self):
        self.balance_baselines = self._load_balance_baselines()
        self.analysis_history: List[Dict[str, Any]] = []
    
    def analyze_content_balance(self, content: GeneratedContent) -> BalanceMetrics:
        """
        Analyze the balance of a single piece of generated content.
        
        Args:
            content: The generated content to analyze
            
        Returns:
            BalanceMetrics for the content
            
        Raises:
            BalanceViolation: If content is severely imbalanced
        """
        if content.content_type == ContentType.SPECIES:
            return self._analyze_species_balance(content)
        elif content.content_type == ContentType.CHARACTER_CLASS:
            return self._analyze_class_balance(content)
        elif content.content_type == ContentType.EQUIPMENT:
            return self._analyze_equipment_balance(content)
        elif content.content_type == ContentType.SPELL:
            return self._analyze_spell_balance(content)
        elif content.content_type == ContentType.FEAT:
            return self._analyze_feat_balance(content)
        else:
            return self._create_default_balance_metrics()
    
    def analyze_collection_balance(self, collection: ContentCollection) -> Dict[str, BalanceMetrics]:
        """
        Analyze the balance of an entire content collection.
        
        Args:
            collection: The content collection to analyze
            
        Returns:
            Dictionary mapping content IDs to their balance metrics
        """
        results = {}
        
        for content_type, items in collection.content_items.items():
            for item in items:
                try:
                    balance = self.analyze_content_balance(item)
                    results[item.content_id] = balance
                except BalanceViolation as e:
                    # Log violation but continue analysis
                    results[item.content_id] = BalanceMetrics.create_failed_analysis(str(e))
        
        # Record analysis session
        self.analysis_history.append({
            "collection_id": collection.collection_id,
            "analyzed_items": len(results),
            "balance_issues": sum(1 for m in results.values() if not m.is_balanced),
            "timestamp": collection.creation_metadata.created_at
        })
        
        return results
    
    def suggest_balance_adjustments(self, content: GeneratedContent, metrics: BalanceMetrics) -> List[str]:
        """
        Suggest adjustments to improve content balance.
        
        Args:
            content: The content that needs adjustment
            metrics: Current balance metrics
            
        Returns:
            List of suggested adjustments
        """
        suggestions = []
        
        if metrics.power_level_score > 1.2:
            suggestions.append("Reduce overall power level - content may be overpowered")
            
            if content.content_type == ContentType.SPECIES:
                suggestions.extend([
                    "Consider reducing ability score increases",
                    "Limit powerful racial traits to once per long rest",
                    "Add situational restrictions to strong abilities"
                ])
            elif content.content_type == ContentType.FEAT:
                suggestions.extend([
                    "Add prerequisites to limit accessibility",
                    "Reduce numerical bonuses",
                    "Make benefits more situational"
                ])
        
        if metrics.utility_score > 1.3:
            suggestions.append("Reduce utility breadth - content provides too many benefits")
        
        if metrics.versatility_score < 0.7:
            suggestions.append("Increase versatility - content may be too narrow")
        
        if not metrics.is_balanced:
            suggestions.append("Overall balance adjustment needed - consult D&D design guidelines")
        
        return suggestions
    
    def _analyze_species_balance(self, content: GeneratedContent) -> BalanceMetrics:
        """Analyze species-specific balance factors."""
        mechanical_data = content.mechanical_data
        
        # Analyze ability score increases
        asi_total = sum(mechanical_data.get('ability_score_increases', {}).values())
        asi_score = min(asi_total / 3.0, 1.5)  # Cap at 1.5 for balance
        
        # Analyze racial traits
        traits = mechanical_data.get('traits', [])
        trait_power = sum(self._evaluate_trait_power(trait) for trait in traits)
        trait_score = min(trait_power / 2.0, 1.5)  # Baseline 2 power points
        
        # Calculate overall scores
        power_level = (asi_score + trait_score) / 2
        utility_score = len(traits) / 3.0  # Baseline 3 traits
        versatility_score = len(set(trait.get('category', 'general') for trait in traits)) / 4.0
        
        return BalanceMetrics(
            power_level_score=power_level,
            utility_score=utility_score,
            versatility_score=versatility_score,
            overall_balance_score=(power_level + utility_score + versatility_score) / 3,
            scaling_score=1.0,  # Species don't scale
            complexity_score=len(traits) / 5.0
        )
    
    def _analyze_class_balance(self, content: GeneratedContent) -> BalanceMetrics:
        """Analyze class-specific balance factors."""
        mechanical_data = content.mechanical_data
        
        # Analyze hit die
        hit_die = mechanical_data.get('hit_die', 8)
        hit_die_score = hit_die / 10.0  # d10 = 1.0 baseline
        
        # Analyze features by level
        features_by_level = mechanical_data.get('features_by_level', {})
        feature_power = sum(
            self._evaluate_class_feature_power(features, int(level))
            for level, features in features_by_level.items()
        )
        
        # Calculate scaling based on feature distribution
        scaling_score = self._calculate_class_scaling(features_by_level)
        
        power_level = (hit_die_score + feature_power / 20) / 2  # 20 levels
        utility_score = len(features_by_level) / 20.0
        versatility_score = self._calculate_class_versatility(features_by_level)
        
        return BalanceMetrics(
            power_level_score=power_level,
            utility_score=utility_score,
            versatility_score=versatility_score,
            overall_balance_score=(power_level + utility_score + versatility_score) / 3,
            scaling_score=scaling_score,
            complexity_score=feature_power / 15.0
        )
    
    def _analyze_equipment_balance(self, content: GeneratedContent) -> BalanceMetrics:
        """Analyze equipment-specific balance factors."""
        mechanical_data = content.mechanical_data
        
        # Analyze damage/AC
        damage_dice = mechanical_data.get('damage_dice', '1d4')
        ac_bonus = mechanical_data.get('ac_bonus', 0)
        
        damage_score = self._evaluate_damage_balance(damage_dice)
        ac_score = ac_bonus / 18.0  # Plate armor baseline
        
        # Analyze magical properties
        magical_properties = mechanical_data.get('magical_properties', [])
        magic_score = sum(self._evaluate_magic_property_power(prop) for prop in magical_properties)
        
        power_level = max(damage_score, ac_score) + magic_score
        utility_score = len(magical_properties) / 3.0
        versatility_score = len(set(prop.get('category', 'combat') for prop in magical_properties)) / 4.0
        
        return BalanceMetrics(
            power_level_score=power_level,
            utility_score=utility_score,
            versatility_score=versatility_score,
            overall_balance_score=(power_level + utility_score + versatility_score) / 3,
            scaling_score=1.0,  # Equipment doesn't scale
            complexity_score=len(magical_properties) / 4.0
        )
    
    def _analyze_spell_balance(self, content: GeneratedContent) -> BalanceMetrics:
        """Analyze spell-specific balance factors."""
        mechanical_data = content.mechanical_data
        
        spell_level = mechanical_data.get('level', 1)
        damage = mechanical_data.get('damage', '1d4')
        duration = mechanical_data.get('duration', 'Instantaneous')
        range_val = mechanical_data.get('range', '30 feet')
        
        # Calculate power based on spell level expectations
        expected_damage = self._get_expected_spell_damage(spell_level)
        actual_damage = self._parse_spell_damage(damage)
        
        damage_ratio = actual_damage / max(expected_damage, 1)
        duration_multiplier = self._get_duration_multiplier(duration)
        range_multiplier = self._get_range_multiplier(range_val)
        
        power_level = damage_ratio * duration_multiplier * range_multiplier / spell_level if spell_level > 0 else 1.0
        utility_score = self._calculate_spell_utility(mechanical_data)
        versatility_score = len(mechanical_data.get('effects', [])) / 3.0
        
        return BalanceMetrics(
            power_level_score=power_level,
            utility_score=utility_score,
            versatility_score=versatility_score,
            overall_balance_score=(power_level + utility_score + versatility_score) / 3,
            scaling_score=self._calculate_spell_scaling(mechanical_data),
            complexity_score=len(mechanical_data.get('components', [])) / 3.0
        )
    
    def _analyze_feat_balance(self, content: GeneratedContent) -> BalanceMetrics:
        """Analyze feat-specific balance factors."""
        mechanical_data = content.mechanical_data
        
        # Analyze benefits
        benefits = mechanical_data.get('benefits', [])
        asi_bonus = mechanical_data.get('ability_score_increase', 0)
        
        benefit_power = sum(self._evaluate_feat_benefit_power(benefit) for benefit in benefits)
        asi_power = asi_bonus / 2.0  # Half-feat baseline
        
        # Check prerequisites
        prerequisites = mechanical_data.get('prerequisites', [])
        prereq_modifier = 1.0 + (len(prerequisites) * 0.1)  # Harder prereqs allow more power
        
        power_level = (benefit_power + asi_power) * prereq_modifier
        utility_score = len(benefits) / 2.0
        versatility_score = len(set(benefit.get('category', 'general') for benefit in benefits)) / 3.0
        
        return BalanceMetrics(
            power_level_score=power_level,
            utility_score=utility_score,
            versatility_score=versatility_score,
            overall_balance_score=(power_level + utility_score + versatility_score) / 3,
            scaling_score=1.0,  # Feats don't scale
            complexity_score=len(benefits) / 3.0
        )
    
    def _load_balance_baselines(self) -> Dict[str, Any]:
        """Load baseline balance metrics for comparison."""
        return {
            'species': {
                'asi_total': 3,
                'trait_count': 3,
                'power_budget': 2.0
            },
            'class': {
                'features_per_level': 1.0,
                'power_progression': 'linear',
                'capstone_power': 3.0
            },
            'spell': {
                'damage_per_level': 1.5,
                'utility_baseline': 1.0,
                'scaling_bonus': 0.5
            },
            'feat': {
                'power_budget': 1.5,
                'asi_equivalent': 2.0,
                'utility_cap': 2.0
            }
        }
    
    def _evaluate_trait_power(self, trait: Dict[str, Any]) -> float:
        """Evaluate the power level of a racial trait."""
        # Simple trait power evaluation
        trait_type = trait.get('type', 'passive')
        frequency = trait.get('frequency', 'always')
        
        base_power = 0.5
        
        if trait_type == 'active':
            base_power = 1.0
        elif trait_type == 'combat':
            base_power = 1.5
        
        if frequency == 'once_per_long_rest':
            base_power *= 0.8
        elif frequency == 'once_per_short_rest':
            base_power *= 1.2
        
        return base_power
    
    def _evaluate_class_feature_power(self, features: List[Dict[str, Any]], level: int) -> float:
        """Evaluate power level of class features at a given level."""
        total_power = 0.0
        
        for feature in features:
            base_power = 1.0
            feature_type = feature.get('type', 'utility')
            
            if feature_type == 'combat':
                base_power = 1.5
            elif feature_type == 'spellcasting':
                base_power = 2.0
            elif feature_type == 'capstone' and level >= 18:
                base_power = 3.0
            
            total_power += base_power
        
        return total_power
    
    def _calculate_class_scaling(self, features_by_level: Dict[str, List]) -> float:
        """Calculate how well a class scales across levels."""
        if not features_by_level:
            return 0.5
        
        levels_with_features = len(features_by_level)
        expected_levels = 20
        
        return min(levels_with_features / expected_levels, 1.0)
    
    def _calculate_class_versatility(self, features_by_level: Dict[str, List]) -> float:
        """Calculate class versatility based on feature diversity."""
        all_features = []
        for features in features_by_level.values():
            all_features.extend(features)
        
        if not all_features:
            return 0.5
        
        categories = set(feature.get('category', 'general') for feature in all_features)
        return min(len(categories) / 5.0, 1.0)  # 5 categories for full versatility
    
    def _create_default_balance_metrics(self) -> BalanceMetrics:
        """Create default balance metrics for unknown content types."""
        return BalanceMetrics(
            power_level_score=1.0,
            utility_score=1.0,
            versatility_score=1.0,
            overall_balance_score=1.0,
            scaling_score=1.0,
            complexity_score=1.0
        )
    
    # Additional helper methods would be implemented here...
    def _evaluate_damage_balance(self, damage_dice: str) -> float:
        """Evaluate damage balance for weapons."""
        # Simple damage evaluation
        if 'd4' in damage_dice:
            return 0.4
        elif 'd6' in damage_dice:
            return 0.6
        elif 'd8' in damage_dice:
            return 0.8
        elif 'd10' in damage_dice:
            return 1.0
        elif 'd12' in damage_dice:
            return 1.2
        else:
            return 0.5
    
    def _evaluate_magic_property_power(self, prop: Dict[str, Any]) -> float:
        """Evaluate magical property power."""
        prop_type = prop.get('type', 'minor')
        
        if prop_type == 'minor':
            return 0.3
        elif prop_type == 'major':
            return 0.8
        elif prop_type == 'legendary':
            return 1.5
        else:
            return 0.5
    
    def _get_expected_spell_damage(self, spell_level: int) -> float:
        """Get expected damage for spell level."""
        # D&D spell damage expectations
        damage_by_level = {
            0: 1, 1: 6, 2: 9, 3: 14, 4: 18, 5: 22,
            6: 26, 7: 30, 8: 34, 9: 38
        }
        return damage_by_level.get(spell_level, 1)
    
    def _parse_spell_damage(self, damage: str) -> float:
        """Parse spell damage string to average damage."""
        # Simple damage parsing
        if 'd4' in damage:
            return 2.5
        elif 'd6' in damage:
            return 3.5
        elif 'd8' in damage:
            return 4.5
        elif 'd10' in damage:
            return 5.5
        elif 'd12' in damage:
            return 6.5
        else:
            return 1.0
    
    def _get_duration_multiplier(self, duration: str) -> float:
        """Get power multiplier based on spell duration."""
        if 'instantaneous' in duration.lower():
            return 1.0
        elif 'minute' in duration.lower():
            return 1.2
        elif 'hour' in duration.lower():
            return 1.5
        elif 'day' in duration.lower():
            return 2.0
        else:
            return 1.0
    
    def _get_range_multiplier(self, range_val: str) -> float:
        """Get power multiplier based on spell range."""
        if 'self' in range_val.lower():
            return 0.8
        elif 'touch' in range_val.lower():
            return 0.9
        elif 'feet' in range_val.lower():
            return 1.0
        else:
            return 1.0
    
    def _calculate_spell_utility(self, mechanical_data: Dict[str, Any]) -> float:
        """Calculate spell utility score."""
        effects = mechanical_data.get('effects', [])
        components = mechanical_data.get('components', [])
        
        return min((len(effects) + len(components)) / 4.0, 1.5)
    
    def _calculate_spell_scaling(self, mechanical_data: Dict[str, Any]) -> float:
        """Calculate spell scaling score."""
        if mechanical_data.get('scales_with_slot_level', False):
            return 1.2
        elif mechanical_data.get('scales_with_character_level', False):
            return 1.0
        else:
            return 0.8
    
    def _evaluate_feat_benefit_power(self, benefit: Dict[str, Any]) -> float:
        """Evaluate the power of a feat benefit."""
        benefit_type = benefit.get('type', 'passive')
        
        if benefit_type == 'combat':
            return 1.0
        elif benefit_type == 'skill':
            return 0.5
        elif benefit_type == 'utility':
            return 0.7
        elif benefit_type == 'special':
            return 1.2
        else:
            return 0.5