from enum import Enum, auto


class GenerationMethod(Enum):
    """Methods for generating content in the Creative Framework."""
    LLM = "llm"                         # Large Language Model generation
    TEMPLATE = "template"               # Template-based generation
    HYBRID = "hybrid"                   # Combination of LLM and template
    MANUAL = "manual"                   # User-created content
    PROCEDURAL = "procedural"           # Algorithm-based generation


class LLMProvider(Enum):
    """Supported LLM providers for content generation."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


class TemplateType(Enum):
    """Types of templates used in content generation."""
    SPECIES_TEMPLATE = "species_template"
    CLASS_TEMPLATE = "class_template"
    EQUIPMENT_TEMPLATE = "equipment_template"
    SPELL_TEMPLATE = "spell_template"
    FEAT_TEMPLATE = "feat_template"


class GenerationComplexity(Enum):
    """Complexity levels for content generation."""
    SIMPLE = "simple"                   # Basic generation with minimal features
    MODERATE = "moderate"               # Standard generation with balanced features
    COMPLEX = "complex"                 # Advanced generation with rich features
    MASTERWORK = "masterwork"           # Highly detailed, premium generation


class IterationMethod(Enum):
    """Methods for iterative content refinement."""
    SINGLE_PASS = "single_pass"         # Generate once, no refinement
    VALIDATION_LOOP = "validation_loop" # Refine based on validation feedback
    USER_FEEDBACK = "user_feedback"     # Refine based on user input
    AUTOMATED_REFINEMENT = "automated_refinement"  # AI-driven refinement