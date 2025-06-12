from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from ..enums.content_types import ContentType, ContentSource
from ..enums.generation_methods import GenerationComplexity
from ..enums.validation_types import RuleCompliance


@dataclass(frozen=True)
class GenerationConstraints:
    """
    Value object defining rules and boundaries for content generation.
    
    This ensures all generated content follows D&D rules and meets
    campaign-specific requirements in the Creative Content Framework.
    """
    
    # === POWER LEVEL CONSTRAINTS ===
    power_level: str = "standard"  # "low", "standard", "high", "epic"
    complexity_level: GenerationComplexity = GenerationComplexity.MODERATE
    
    # === RULE COMPLIANCE ===
    rule_compliance: RuleCompliance = RuleCompliance.STRICT
    allowed_sources: Set[ContentSource] = field(default_factory=lambda: {ContentSource.CORE_RULES, ContentSource.GENERATED})
    
    # === CONTENT RESTRICTIONS ===
    forbidden_elements: List[str] = field(default_factory=list)
    required_elements: List[str] = field(default_factory=list)
    forbidden_themes: List[str] = field(default_factory=list)
    required_themes: List[str] = field(default_factory=list)
    
    # === MECHANICAL LIMITS ===
    mechanical_limits: Dict[str, Any] = field(default_factory=dict)
    balance_thresholds: Dict[str, float] = field(default_factory=dict)
    
    # === LEVEL CONSTRAINTS ===
    min_level: int = 1
    max_level: int = 20
    target_level: Optional[int] = None
    
    # === CAMPAIGN CONSTRAINTS ===
    campaign_setting: Optional[str] = None
    setting_restrictions: List[str] = field(default_factory=list)
    tone_requirements: List[str] = field(default_factory=list)
    
    # === CONTENT TYPE SPECIFIC ===
    content_type_limits: Dict[ContentType, Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate constraints on creation."""
        if self.min_level < 1 or self.min_level > 20:
            raise ValueError("min_level must be between 1 and 20")
        if self.max_level < 1 or self.max_level > 20:
            raise ValueError("max_level must be between 1 and 20")
        if self.min_level > self.max_level:
            raise ValueError("min_level cannot be greater than max_level")
        
        valid_power_levels = {"low", "standard", "high", "epic"}
        if self.power_level not in valid_power_levels:
            raise ValueError(f"Invalid power level: {self.power_level}")
    
    @property
    def is_restrictive(self) -> bool:
        """Check if constraints are highly restrictive."""
        restriction_count = (
            len(self.forbidden_elements) +
            len(self.forbidden_themes) +
            len(self.setting_restrictions) +
            len(self.mechanical_limits)
        )
        return restriction_count > 10
    
    @property
    def allows_homebrew(self) -> bool:
        """Check if homebrew content is allowed."""
        return ContentSource.CUSTOM in self.allowed_sources or ContentSource.GENERATED in self.allowed_sources
    
    @property
    def level_range_span(self) -> int:
        """Get the span of the level range."""
        return self.max_level - self.min_level + 1
    
    def is_element_forbidden(self, element: str) -> bool:
        """Check if a specific element is forbidden."""
        element_lower = element.lower()
        return any(forbidden.lower() in element_lower for forbidden in self.forbidden_elements)
    
    def is_theme_forbidden(self, theme: str) -> bool:
        """Check if a specific theme is forbidden."""
        theme_lower = theme.lower()
        return any(forbidden.lower() in theme_lower for forbidden in self.forbidden_themes)
    
    def is_element_required(self, element: str) -> bool:
        """Check if a specific element is required."""
        element_lower = element.lower()
        return any(required.lower() in element_lower for required in self.required_elements)
    
    def is_theme_required(self, theme: str) -> bool:
        """Check if a specific theme is required."""
        theme_lower = theme.lower()
        return any(required.lower() in theme_lower for required in self.required_themes)
    
    def get_mechanical_limit(self, limit_type: str, default: Any = None) -> Any:
        """Get a specific mechanical limit."""
        return self.mechanical_limits.get(limit_type, default)
    
    def get_balance_threshold(self, threshold_type: str, default: float = 0.5) -> float:
        """Get a specific balance threshold."""
        return self.balance_thresholds.get(threshold_type, default)
    
    def get_content_type_limit(self, content_type: ContentType, limit_name: str, default: Any = None) -> Any:
        """Get a limit specific to a content type."""
        type_limits = self.content_type_limits.get(content_type, {})
        return type_limits.get(limit_name, default)
    
    def validate_against_content(self, content_data: Dict[str, Any], content_type: ContentType) -> List[str]:
        """Validate content against these constraints."""
        violations = []
        
        # Check forbidden elements
        content_str = str(content_data).lower()
        for forbidden in self.forbidden_elements:
            if forbidden.lower() in content_str:
                violations.append(f"Content contains forbidden element: {forbidden}")
        
        # Check forbidden themes
        for forbidden_theme in self.forbidden_themes:
            if forbidden_theme.lower() in content_str:
                violations.append(f"Content contains forbidden theme: {forbidden_theme}")
        
        # Check required elements
        for required in self.required_elements:
            if required.lower() not in content_str:
                violations.append(f"Content missing required element: {required}")
        
        # Check mechanical limits
        for limit_type, limit_value in self.mechanical_limits.items():
            if limit_type in content_data:
                content_value = content_data[limit_type]
                if isinstance(limit_value, (int, float)) and isinstance(content_value, (int, float)):
                    if content_value > limit_value:
                        violations.append(f"{limit_type} ({content_value}) exceeds limit ({limit_value})")
        
        # Check content-type specific limits
        type_limits = self.content_type_limits.get(content_type, {})
        for limit_name, limit_value in type_limits.items():
            if limit_name in content_data:
                content_value = content_data[limit_name]
                if isinstance(limit_value, (int, float)) and isinstance(content_value, (int, float)):
                    if content_value > limit_value:
                        violations.append(f"{content_type.value} {limit_name} ({content_value}) exceeds limit ({limit_value})")
        
        return violations
    
    def create_relaxed_version(self) -> 'GenerationConstraints':
        """Create a more permissive version of these constraints."""
        return GenerationConstraints(
            power_level=self.power_level,
            complexity_level=self.complexity_level,
            rule_compliance=RuleCompliance.HOMEBREW,  # More permissive
            allowed_sources=self.allowed_sources | {ContentSource.CUSTOM},  # Add custom content
            forbidden_elements=self.forbidden_elements[:len(self.forbidden_elements)//2],  # Reduce restrictions
            required_elements=self.required_elements,  # Keep requirements
            forbidden_themes=self.forbidden_themes[:len(self.forbidden_themes)//2],  # Reduce restrictions
            required_themes=self.required_themes,  # Keep requirements
            mechanical_limits={k: v * 1.2 for k, v in self.mechanical_limits.items()},  # Increase limits
            balance_thresholds=self.balance_thresholds,
            min_level=self.min_level,
            max_level=self.max_level,
            target_level=self.target_level,
            campaign_setting=self.campaign_setting,
            setting_restrictions=self.setting_restrictions[:len(self.setting_restrictions)//2],  # Reduce restrictions
            tone_requirements=self.tone_requirements,
            content_type_limits=self.content_type_limits
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "power_level": self.power_level,
            "complexity_level": self.complexity_level.value,
            "rule_compliance": self.rule_compliance.value,
            "allowed_sources": [source.value for source in self.allowed_sources],
            "forbidden_elements": self.forbidden_elements,
            "required_elements": self.required_elements,
            "forbidden_themes": self.forbidden_themes,
            "required_themes": self.required_themes,
            "mechanical_limits": self.mechanical_limits,
            "balance_thresholds": self.balance_thresholds,
            "min_level": self.min_level,
            "max_level": self.max_level,
            "target_level": self.target_level,
            "campaign_setting": self.campaign_setting,
            "setting_restrictions": self.setting_restrictions,
            "tone_requirements": self.tone_requirements,
            "content_type_limits": {
                content_type.value: limits 
                for content_type, limits in self.content_type_limits.items()
            }
        }