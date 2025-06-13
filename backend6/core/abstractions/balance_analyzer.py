"""
Balance Analyzer Interface - Domain Service Boundary.

Defines the contract for analyzing and validating the power level and balance
of generated D&D content. This ensures all custom content meets appropriate
power standards for its type and level.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..enums.balance_levels import BalanceLevel, BalanceCategory, PowerBenchmark
from ..enums.content_types import ContentType
from ..enums.game_mechanics import PowerTier


class BalanceResult:
    """Result of balance analysis."""
    
    def __init__(self, 
                 balance_level: BalanceLevel,
                 power_score: float,
                 category_scores: Dict[BalanceCategory, float],
                 recommendations: List[str],
                 issues: List[str] = None):
        self.balance_level = balance_level
        self.power_score = power_score
        self.category_scores = category_scores
        self.recommendations = recommendations
        self.issues = issues or []
    
    @property
    def is_balanced(self) -> bool:
        """Check if content is considered balanced."""
        return self.balance_level.is_acceptable
    
    @property
    def needs_adjustment(self) -> bool:
        """Check if content needs balance adjustment."""
        return self.balance_level.requires_adjustment


class IBalanceAnalyzer(ABC):
    """
    Domain service interface for analyzing content balance and power levels.
    
    This service ensures all generated content maintains appropriate power
    levels and follows D&D balance guidelines.
    """
    
    @abstractmethod
    def analyze_content_balance(self,
                              content_data: Dict[str, Any],
                              content_type: ContentType,
                              benchmark: PowerBenchmark = PowerBenchmark.CORE_CLASSES) -> BalanceResult:
        """
        Analyze overall balance of content.
        
        Args:
            content_data: Content to analyze
            content_type: Type of content
            benchmark: Comparison benchmark
            
        Returns:
            Complete balance analysis result
        """
        pass
    
    @abstractmethod
    def analyze_combat_power(self,
                           content_data: Dict[str, Any],
                           content_type: ContentType,
                           character_level: int) -> float:
        """
        Analyze combat effectiveness of content.
        
        Args:
            content_data: Content to analyze
            content_type: Type of content
            character_level: Character level context
            
        Returns:
            Combat power score (0.0 to 2.0, 1.0 = balanced)
        """
        pass
    
    @abstractmethod
    def analyze_utility_value(self,
                            content_data: Dict[str, Any],
                            content_type: ContentType) -> float:
        """
        Analyze out-of-combat utility value.
        
        Args:
            content_data: Content to analyze
            content_type: Type of content
            
        Returns:
            Utility value score (0.0 to 2.0, 1.0 = balanced)
        """
        pass
    
    @abstractmethod
    def analyze_power_scaling(self,
                            content_data: Dict[str, Any],
                            level_range: tuple[int, int]) -> Dict[int, float]:
        """
        Analyze how content power scales across levels.
        
        Args:
            content_data: Content to analyze
            level_range: Level range to analyze
            
        Returns:
            Dictionary mapping levels to power scores
        """
        pass
    
    @abstractmethod
    def compare_to_benchmark(self,
                           content_data: Dict[str, Any],
                           content_type: ContentType,
                           benchmark_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Compare content to benchmark items.
        
        Args:
            content_data: Content to compare
            content_type: Type of content
            benchmark_items: Official content for comparison
            
        Returns:
            Comparison scores for each benchmark item
        """
        pass
    
    @abstractmethod
    def get_balance_recommendations(self,
                                  balance_result: BalanceResult,
                                  content_type: ContentType) -> List[str]:
        """
        Get specific recommendations for improving balance.
        
        Args:
            balance_result: Current balance analysis
            content_type: Type of content
            
        Returns:
            List of actionable balance recommendations
        """
        pass
    
    @abstractmethod
    def validate_power_tier_appropriateness(self,
                                          content_data: Dict[str, Any],
                                          power_tier: PowerTier,
                                          content_type: ContentType) -> bool:
        """
        Validate content is appropriate for its power tier.
        
        Args:
            content_data: Content to validate
            power_tier: Expected power tier
            content_type: Type of content
            
        Returns:
            True if appropriate for tier
        """
        pass
    
    @abstractmethod
    def auto_balance_content(self,
                           content_data: Dict[str, Any],
                           target_balance: BalanceLevel,
                           content_type: ContentType) -> Dict[str, Any]:
        """
        Automatically adjust content to target balance level.
        
        Args:
            content_data: Content to balance
            target_balance: Target balance level
            content_type: Type of content
            
        Returns:
            Balanced content data
        """
        pass