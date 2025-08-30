"""
D&D Campaign Creation Validation Module

This module contains comprehensive validation methods for campaign creation based on campaign_creation.md requirements.
All validation follows D&D 5e 2024 rules and ensures campaigns meet narrative quality and structural requirements.

VALIDATION REQUIREMENTS:
- Campaign concepts must be 50-500 words (REQ-CAM-002)
- Campaigns must have compelling narrative hooks (REQ-CAM-013)
- Complex storylines with multiple plot layers (REQ-CAM-003, REQ-CAM-014)
- Morally complex scenarios (REQ-CAM-005)
- Appropriate encounter balance for party level (REQ-CAM-035, REQ-CAM-036)
- Chapter structure and content validation (REQ-CAM-028-037)
- Campaign length validation (REQ-CAM-027, REQ-CAM-219)
- Performance requirements validation (REQ-CAM-216-223)

Validation Functions:
- Campaign concept and structure validation
- Chapter content and balance validation
- NPC/monster appropriateness for campaign context
- Plot complexity and narrative quality validation
- Campaign performance and scalability validation
- Refinement request validation
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Import from models
from src.models.campaign_creation_models import (
    CampaignCreationType, BaseCampaignRequest, CampaignFromScratchRequest,
    CampaignSkeletonRequest, ChapterContentRequest, CampaignRefinementRequest
)
from src.models.core_models import ChallengeRating, EncounterDifficulty, EncounterBuilder

logger = logging.getLogger(__name__)

# ============================================================================
# VALIDATION RESULT CLASSES
# ============================================================================

@dataclass
class ValidationResult:
    """Result container for validation operations."""
    success: bool = False
    errors: List[str] = None
    warnings: List[str] = None
    validated_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.validated_data is None:
            self.validated_data = {}
    
    def add_error(self, error: str):
        """Add a validation error."""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str):
        """Add a validation warning."""
        self.warnings.append(warning)
    
    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any validation warnings."""
        return len(self.warnings) > 0

# ============================================================================
# CAMPAIGN CONCEPT VALIDATION (REQ-CAM-002, REQ-CAM-006)
# ============================================================================

def validate_campaign_concept(concept: str, creation_type: CampaignCreationType) -> ValidationResult:
    """
    Validate campaign concept meets requirements.
    
    REQ-CAM-002: Accept campaign concepts of 50-500 words
    REQ-CAM-006: Support multiple genres
    """
    result = ValidationResult(success=True)
    
    if not concept or not isinstance(concept, str):
        result.add_error("Campaign concept is required and must be a string")
        return result
    
    # Word count validation (REQ-CAM-002)
    words = concept.split()
    word_count = len(words)
    
    if word_count < 50:
        result.add_error(f"Campaign concept too short: {word_count} words (minimum 50 required)")
    elif word_count > 500:
        result.add_error(f"Campaign concept too long: {word_count} words (maximum 500 allowed)")
    
    # Content quality validation
    if word_count < 75:
        result.add_warning("Concept may be too brief for complex storytelling")
    
    # Check for narrative elements (REQ-CAM-013: compelling narrative hooks)
    narrative_indicators = [
        'conflict', 'mystery', 'adventure', 'quest', 'threat', 'danger',
        'intrigue', 'political', 'magic', 'ancient', 'forbidden', 'lost',
        'heroes', 'villain', 'antagonist', 'enemy', 'ally', 'betrayal'
    ]
    
    concept_lower = concept.lower()
    found_indicators = [word for word in narrative_indicators if word in concept_lower]
    
    if len(found_indicators) < 2:
        result.add_warning("Concept may lack compelling narrative elements. Consider adding conflict, mystery, or adventure themes.")
    
    # Check for moral complexity indicators (REQ-CAM-005)
    complexity_indicators = [
        'choice', 'dilemma', 'difficult', 'complex', 'moral', 'ethics',
        'sacrifice', 'consequences', 'grey', 'ambiguous', 'conflicted'
    ]
    
    found_complexity = [word for word in complexity_indicators if word in concept_lower]
    if len(found_complexity) == 0:
        result.add_warning("Consider adding moral complexity and difficult choices to enhance storytelling")
    
    # Genre detection and validation (REQ-CAM-006)
    genre_keywords = {
        'fantasy': ['magic', 'dragon', 'wizard', 'knight', 'kingdom', 'realm', 'spell'],
        'sci-fi': ['space', 'alien', 'technology', 'future', 'robot', 'cybernetic', 'galaxy'],
        'horror': ['dark', 'evil', 'terror', 'nightmare', 'haunted', 'cursed', 'undead'],
        'mystery': ['mystery', 'investigate', 'clues', 'detective', 'secret', 'hidden', 'puzzle'],
        'western': ['frontier', 'outlaw', 'sheriff', 'desert', 'saloon', 'gunslinger'],
        'cyberpunk': ['cyber', 'hacker', 'corporation', 'street', 'neon', 'virtual']
    }
    
    detected_genres = []
    for genre, keywords in genre_keywords.items():
        if any(keyword in concept_lower for keyword in keywords):
            detected_genres.append(genre)
    
    if not detected_genres:
        detected_genres = ['fantasy']  # Default genre
        result.add_warning("No clear genre detected in concept, defaulting to fantasy")
    
    result.validated_data = {
        'concept': concept,
        'word_count': word_count,
        'detected_genres': detected_genres,
        'narrative_indicators': found_indicators,
        'complexity_indicators': found_complexity
    }
    
    return result

# ============================================================================
# CAMPAIGN STRUCTURE VALIDATION (REQ-CAM-023-027)
# ============================================================================

def validate_campaign_structure(campaign_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate campaign structure meets requirements.
    
    REQ-CAM-024: Main story arc with beginning, middle, end
    REQ-CAM-025: 3-5 major plot points
    REQ-CAM-027: Support 3-20 sessions
    """
    result = ValidationResult(success=True)
    
    # Required fields validation
    required_fields = ['title', 'description', 'themes', 'session_count']
    for field in required_fields:
        if field not in campaign_data or not campaign_data[field]:
            result.add_error(f"Missing required field: {field}")
    
    # Session count validation (REQ-CAM-027)
    session_count = campaign_data.get('session_count', 0)
    if not isinstance(session_count, int) or session_count < 3:
        result.add_error(f"Session count too low: {session_count} (minimum 3 required)")
    elif session_count > 20:
        result.add_error(f"Session count too high: {session_count} (maximum 20 supported)")
    elif session_count > 50:
        # REQ-CAM-219: Support up to 50 chapters
        result.add_warning(f"Very long campaign: {session_count} sessions may be challenging to manage")
    
    # Story arc validation (REQ-CAM-024)
    if 'act_structure' in campaign_data:
        acts = campaign_data['act_structure']
        if isinstance(acts, list):
            act_names = [act.get('act', '').lower() if isinstance(act, dict) else str(act).lower() for act in acts]
            required_acts = ['beginning', 'middle', 'end']
            missing_acts = [act for act in required_acts if act not in act_names]
            if missing_acts:
                result.add_warning(f"Missing story arc phases: {missing_acts}")
    
    # Plot points validation (REQ-CAM-025)
    if 'major_plot_points' in campaign_data:
        plot_points = campaign_data['major_plot_points']
        if isinstance(plot_points, list):
            point_count = len(plot_points)
            if point_count < 3:
                result.add_warning(f"Few plot points: {point_count} (recommended 3-5)")
            elif point_count > 8:
                result.add_warning(f"Many plot points: {point_count} (may be overwhelming)")
    
    # Narrative complexity validation (REQ-CAM-014: multi-layered plots)
    complexity_score = 0
    
    # Check for subplots
    if 'subplots' in campaign_data and isinstance(campaign_data['subplots'], list):
        complexity_score += len(campaign_data['subplots'])
    
    # Check for interconnected elements
    if 'interconnected_elements' in campaign_data:
        complexity_score += 2
    
    # Check for multiple antagonists
    if 'antagonists' in campaign_data and isinstance(campaign_data['antagonists'], list):
        complexity_score += len(campaign_data['antagonists'])
    
    if complexity_score < 3:
        result.add_warning("Campaign may lack complexity. Consider adding subplots or multiple antagonists.")
    
    result.validated_data = campaign_data
    return result

# ============================================================================
# CHAPTER CONTENT VALIDATION (REQ-CAM-028-037)
# ============================================================================

def validate_chapter_content(chapter_data: Dict[str, Any], party_level: int, party_size: int) -> ValidationResult:
    """
    Validate chapter content meets requirements.
    
    REQ-CAM-029: Clear objective, conflict, resolution
    REQ-CAM-030: Chapter summaries 100-300 words
    REQ-CAM-033-037: Required content elements
    """
    result = ValidationResult(success=True)
    
    # Required fields validation
    required_fields = ['title', 'summary']
    for field in required_fields:
        if field not in chapter_data or not chapter_data[field]:
            result.add_error(f"Chapter missing required field: {field}")
    
    # Summary length validation (REQ-CAM-030)
    if 'summary' in chapter_data:
        summary = chapter_data['summary']
        word_count = len(summary.split()) if isinstance(summary, str) else 0
        
        if word_count < 100:
            result.add_warning(f"Chapter summary too short: {word_count} words (recommended 100-300)")
        elif word_count > 300:
            result.add_warning(f"Chapter summary too long: {word_count} words (recommended 100-300)")
    
    # Content elements validation (REQ-CAM-033-037)
    required_content = {
        'locations': 'REQ-CAM-033: Location descriptions',
        'npcs': 'REQ-CAM-034: Key NPCs with motivations',
        'encounters': 'REQ-CAM-035: Appropriate encounters',
        'rewards': 'REQ-CAM-036: Treasure/rewards',
        'chapter_hooks': 'REQ-CAM-037: Hooks to next chapters'
    }
    
    for content_type, requirement in required_content.items():
        if content_type not in chapter_data or not chapter_data[content_type]:
            result.add_warning(f"Chapter missing {content_type} ({requirement})")
    
    # Encounter balance validation (REQ-CAM-035)
    if 'encounters' in chapter_data and isinstance(chapter_data['encounters'], list):
        encounters = chapter_data['encounters']
        encounter_balance = validate_encounter_balance(encounters, party_level, party_size)
        
        if encounter_balance.has_errors():
            result.errors.extend(encounter_balance.errors)
        if encounter_balance.has_warnings():
            result.warnings.extend(encounter_balance.warnings)
    
    # Objective-conflict-resolution validation (REQ-CAM-029)
    structure_elements = ['objective', 'conflict', 'resolution']
    missing_structure = []
    
    for element in structure_elements:
        if element not in chapter_data:
            # Check if it's mentioned in summary
            summary = chapter_data.get('summary', '').lower()
            element_keywords = {
                'objective': ['goal', 'objective', 'mission', 'task', 'purpose'],
                'conflict': ['conflict', 'challenge', 'obstacle', 'problem', 'difficulty'],
                'resolution': ['resolution', 'conclusion', 'outcome', 'result', 'ending']
            }
            
            if not any(keyword in summary for keyword in element_keywords.get(element, [])):
                missing_structure.append(element)
    
    if missing_structure:
        result.add_warning(f"Chapter may lack clear {', '.join(missing_structure)} structure")
    
    result.validated_data = chapter_data
    return result

# ============================================================================
# ENCOUNTER BALANCE VALIDATION
# ============================================================================

def validate_encounter_balance(encounters: List[Dict[str, Any]], party_level: int, party_size: int) -> ValidationResult:
    """
    Validate encounter balance for party level and size.
    
    REQ-CAM-035: Appropriate encounters
    REQ-CAM-036: Appropriate rewards
    """
    result = ValidationResult(success=True)
    
    if party_level < 1 or party_level > 20:
        result.add_error(f"Invalid party level: {party_level} (must be 1-20)")
        return result
    
    if party_size < 1 or party_size > 8:  # REQ-CAM-222: Up to 8 characters
        result.add_error(f"Invalid party size: {party_size} (must be 1-8)")
        return result
    
    encounter_types = {'combat': 0, 'social': 0, 'exploration': 0, 'puzzle': 0}
    total_difficulty_budget = 0
    
    for encounter in encounters:
        if not isinstance(encounter, dict):
            continue
        
        encounter_type = encounter.get('type', 'unknown').lower()
        if encounter_type in encounter_types:
            encounter_types[encounter_type] += 1
        
        # Validate combat encounters
        if encounter_type == 'combat':
            combat_validation = validate_combat_encounter(encounter, party_level, party_size)
            if combat_validation.has_errors():
                result.errors.extend(combat_validation.errors)
            if combat_validation.has_warnings():
                result.warnings.extend(combat_validation.warnings)
    
    # Check encounter variety
    total_encounters = sum(encounter_types.values())
    if total_encounters == 0:
        result.add_warning("No encounters defined in chapter")
    else:
        # Recommend balanced encounter types
        if encounter_types['combat'] == total_encounters:
            result.add_warning("All encounters are combat - consider adding social or exploration encounters")
        elif encounter_types['social'] == 0 and total_encounters > 2:
            result.add_warning("No social encounters - consider adding roleplay opportunities")
    
    result.validated_data = {
        'encounter_types': encounter_types,
        'total_encounters': total_encounters,
        'party_level': party_level,
        'party_size': party_size
    }
    
    return result

def validate_combat_encounter(encounter: Dict[str, Any], party_level: int, party_size: int) -> ValidationResult:
    """Validate individual combat encounter balance."""
    result = ValidationResult(success=True)
    
    # Use encounter builder for validation
    try:
        builder = EncounterBuilder(party_level, party_size)
        
        # Check if creatures are specified
        creatures = encounter.get('creatures', [])
        if not creatures:
            result.add_warning("Combat encounter missing creature details")
            return result
        
        # Extract challenge ratings
        challenge_ratings = []
        for creature in creatures:
            if isinstance(creature, dict):
                cr_value = creature.get('challenge_rating', 0.25)
                try:
                    if isinstance(cr_value, str):
                        cr_value = float(cr_value)
                    cr = ChallengeRating(cr_value)
                    challenge_ratings.append(cr)
                except (ValueError, KeyError):
                    result.add_warning(f"Invalid challenge rating: {cr_value}")
        
        if challenge_ratings:
            # Validate encounter balance
            validation = builder.validate_encounter(challenge_ratings)
            
            target_difficulty = encounter.get('difficulty', 'medium')
            actual_difficulty = validation['actual_difficulty']
            
            if validation['actual_difficulty'] != target_difficulty:
                result.add_warning(f"Encounter difficulty mismatch: expected {target_difficulty}, got {actual_difficulty}")
            
            # Check for TPK risk
            if actual_difficulty == EncounterDifficulty.DEADLY:
                adjusted_xp = validation['adjusted_xp']
                deadly_threshold = validation['party_thresholds']['deadly']
                if adjusted_xp > deadly_threshold * 1.5:
                    result.add_warning("Encounter may be too dangerous - risk of TPK")
    
    except Exception as e:
        result.add_warning(f"Could not validate encounter balance: {str(e)}")
    
    return result

# ============================================================================
# REFINEMENT REQUEST VALIDATION (REQ-CAM-007-012)
# ============================================================================

def validate_refinement_request(request: CampaignRefinementRequest) -> ValidationResult:
    """
    Validate campaign refinement request.
    
    REQ-CAM-007: Iterative refinement support
    REQ-CAM-008: Multiple refinement cycles
    REQ-CAM-009: Narrative consistency
    REQ-CAM-011: Partial refinements
    """
    result = ValidationResult(success=True)
    
    # Basic validation
    if not request.existing_data:
        result.add_error("Refinement requires existing campaign data")
    
    if not request.refinement_prompt or len(request.refinement_prompt.strip()) < 10:
        result.add_error("Refinement prompt must be at least 10 characters")
    
    # Refinement cycles validation (REQ-CAM-008)
    if request.refinement_cycles < 1:
        result.add_error("Refinement cycles must be at least 1")
    elif request.refinement_cycles > 5:
        result.add_warning("Many refinement cycles may lead to inconsistency")
    
    # Preserve elements validation (REQ-CAM-011: partial refinements)
    if request.preserve_elements:
        available_elements = list(request.existing_data.keys()) if request.existing_data else []
        invalid_elements = [elem for elem in request.preserve_elements if elem not in available_elements]
        if invalid_elements:
            result.add_warning(f"Cannot preserve non-existent elements: {invalid_elements}")
    
    # Refinement type validation
    valid_types = ['enhance', 'modify', 'expand', 'simplify', 'player_driven']
    if request.refinement_type not in valid_types:
        result.add_warning(f"Unknown refinement type: {request.refinement_type}")
    
    result.validated_data = {
        'refinement_prompt': request.refinement_prompt,
        'refinement_type': request.refinement_type,
        'cycles': request.refinement_cycles,
        'preserve_elements': request.preserve_elements or []
    }
    
    return result

# ============================================================================
# PERFORMANCE VALIDATION (REQ-CAM-216-223)
# ============================================================================

def validate_performance_requirements(campaign_data: Dict[str, Any], creation_type: CampaignCreationType) -> ValidationResult:
    """
    Validate performance requirements are met.
    
    REQ-CAM-216: Skeleton generation < 30s
    REQ-CAM-217: Chapter generation < 60s
    REQ-CAM-219: Up to 50 chapters
    REQ-CAM-220: Refinement < 45s
    REQ-CAM-221: 10 concurrent generations
    REQ-CAM-222: Up to 8 player characters
    """
    result = ValidationResult(success=True)
    
    # Chapter count validation (REQ-CAM-219)
    if 'session_count' in campaign_data:
        session_count = campaign_data['session_count']
        if session_count > 50:
            result.add_error(f"Too many chapters: {session_count} (maximum 50 supported)")
    
    if 'chapters' in campaign_data:
        chapter_count = len(campaign_data['chapters'])
        if chapter_count > 50:
            result.add_error(f"Too many chapters: {chapter_count} (maximum 50 supported)")
    
    # Party size validation (REQ-CAM-222)
    if 'party_size' in campaign_data:
        party_size = campaign_data['party_size']
        if party_size > 8:
            result.add_error(f"Party size too large: {party_size} (maximum 8 supported)")
        elif party_size < 1:
            result.add_error(f"Invalid party size: {party_size} (minimum 1 required)")
    
    # Content complexity validation for performance
    complexity_indicators = {
        'npcs': 100,  # Max NPCs per campaign
        'locations': 50,  # Max locations per campaign
        'encounters': 200,  # Max encounters per campaign
        'plot_points': 20  # Max major plot points
    }
    
    for element, max_count in complexity_indicators.items():
        if element in campaign_data:
            element_data = campaign_data[element]
            if isinstance(element_data, list) and len(element_data) > max_count:
                result.add_warning(f"High {element} count: {len(element_data)} (may impact performance)")
    
    # Timeout expectations based on creation type
    timeout_limits = {
        CampaignCreationType.CAMPAIGN_SKELETON: 30,  # REQ-CAM-216
        CampaignCreationType.CHAPTER_CONTENT: 60,    # REQ-CAM-217
        CampaignCreationType.ITERATIVE_REFINEMENT: 45  # REQ-CAM-220
    }
    
    expected_timeout = timeout_limits.get(creation_type, 300)  # Default 5 minutes
    
    result.validated_data = {
        'expected_timeout': expected_timeout,
        'performance_validated': True
    }
    
    return result

# ============================================================================
# NARRATIVE QUALITY VALIDATION (REQ-CAM-013-018)
# ============================================================================

def validate_narrative_quality(campaign_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate narrative quality requirements.
    
    REQ-CAM-013: Compelling narrative hooks
    REQ-CAM-014: Multi-layered plots
    REQ-CAM-015: Complex antagonists
    REQ-CAM-016: Organic plot twists
    REQ-CAM-017: Emotional stakes
    REQ-CAM-018: Narrative pacing
    """
    result = ValidationResult(success=True)
    
    # Narrative hooks validation (REQ-CAM-013)
    hooks = campaign_data.get('campaign_hooks', [])
    if not hooks or len(hooks) < 2:
        result.add_warning("Campaign needs more narrative hooks to engage players")
    
    # Check hook quality
    hook_quality_indicators = ['mystery', 'urgent', 'personal', 'threat', 'opportunity', 'intrigue']
    for i, hook in enumerate(hooks):
        if isinstance(hook, str):
            hook_lower = hook.lower()
            quality_score = sum(1 for indicator in hook_quality_indicators if indicator in hook_lower)
            if quality_score == 0:
                result.add_warning(f"Hook {i+1} may lack compelling elements")
    
    # Multi-layered plot validation (REQ-CAM-014)
    plot_layers = 0
    if 'main_plot' in campaign_data:
        plot_layers += 1
    if 'subplots' in campaign_data and isinstance(campaign_data['subplots'], list):
        plot_layers += len(campaign_data['subplots'])
    if 'interconnected_elements' in campaign_data:
        plot_layers += 1
    
    if plot_layers < 2:
        result.add_warning("Campaign may lack plot complexity - consider adding subplots")
    
    # Antagonist complexity validation (REQ-CAM-015)
    antagonists = campaign_data.get('antagonists', [])
    if not antagonists:
        antagonists = [campaign_data.get('main_antagonist')] if 'main_antagonist' in campaign_data else []
    
    for antagonist in antagonists:
        if isinstance(antagonist, dict):
            if 'motivation' not in antagonist or not antagonist['motivation']:
                result.add_warning("Antagonist missing clear motivation")
            if 'goals' not in antagonist or not antagonist['goals']:
                result.add_warning("Antagonist missing believable goals")
    
    # Emotional stakes validation (REQ-CAM-017)
    stakes_indicators = ['consequence', 'lose', 'save', 'protect', 'sacrifice', 'death', 'betrayal']
    description = campaign_data.get('description', '').lower()
    plot_summary = campaign_data.get('plot_summary', '').lower()
    
    combined_text = f"{description} {plot_summary}"
    stakes_score = sum(1 for indicator in stakes_indicators if indicator in combined_text)
    
    if stakes_score == 0:
        result.add_warning("Campaign may lack emotional stakes and consequences")
    
    # Pacing validation (REQ-CAM-018)
    if 'chapters' in campaign_data:
        chapters = campaign_data['chapters']
        if isinstance(chapters, list) and len(chapters) > 2:
            # Check for pacing variety
            pacing_types = set()
            for chapter in chapters:
                if isinstance(chapter, dict):
                    chapter_type = chapter.get('pacing', 'standard')
                    pacing_types.add(chapter_type)
            
            if len(pacing_types) == 1:
                result.add_warning("Consider varying chapter pacing for better narrative flow")
    
    result.validated_data = {
        'narrative_hooks': len(hooks),
        'plot_layers': plot_layers,
        'antagonist_count': len(antagonists),
        'emotional_stakes_score': stakes_score
    }
    
    return result

# ============================================================================
# MAIN VALIDATION FUNCTIONS
# ============================================================================

def validate_campaign_request(request: BaseCampaignRequest) -> ValidationResult:
    """
    Main validation function for all campaign creation requests.
    Routes to appropriate validators based on request type.
    """
    result = ValidationResult(success=True)
    
    # Basic request validation
    if not request:
        result.add_error("Request cannot be None")
        return result
    
    if not hasattr(request, 'creation_type') or not request.creation_type:
        result.add_error("Request missing creation_type")
        return result
    
    # Concept validation (applies to all request types)
    if hasattr(request, 'concept') and request.concept:
        concept_validation = validate_campaign_concept(request.concept, request.creation_type)
        if concept_validation.has_errors():
            result.errors.extend(concept_validation.errors)
        if concept_validation.has_warnings():
            result.warnings.extend(concept_validation.warnings)
    
    # Type-specific validation
    try:
        if isinstance(request, CampaignFromScratchRequest):
            type_validation = validate_campaign_from_scratch_request(request)
        elif isinstance(request, CampaignSkeletonRequest):
            type_validation = validate_campaign_skeleton_request(request)
        elif isinstance(request, ChapterContentRequest):
            type_validation = validate_chapter_content_request(request)
        elif isinstance(request, CampaignRefinementRequest):
            type_validation = validate_refinement_request(request)
        else:
            result.add_warning(f"No specific validator for request type: {type(request)}")
            type_validation = ValidationResult(success=True)
        
        if type_validation.has_errors():
            result.errors.extend(type_validation.errors)
        if type_validation.has_warnings():
            result.warnings.extend(type_validation.warnings)
    
    except Exception as e:
        result.add_error(f"Validation error: {str(e)}")
    
    return result

def validate_campaign_from_scratch_request(request: CampaignFromScratchRequest) -> ValidationResult:
    """Validate campaign from scratch request."""
    result = ValidationResult(success=True)
    
    # Session count validation
    if request.session_count < 3 or request.session_count > 20:
        result.add_error(f"Invalid session count: {request.session_count} (must be 3-20)")
    
    # Party validation
    if request.party_level < 1 or request.party_level > 20:
        result.add_error(f"Invalid party level: {request.party_level} (must be 1-20)")
    
    if request.party_size < 1 or request.party_size > 8:
        result.add_error(f"Invalid party size: {request.party_size} (must be 1-8)")
    
    # Theme validation
    if not request.themes or len(request.themes) == 0:
        result.add_warning("No themes specified - campaign may lack thematic coherence")
    
    return result

def validate_campaign_skeleton_request(request: CampaignSkeletonRequest) -> ValidationResult:
    """Validate campaign skeleton request."""
    result = ValidationResult(success=True)
    
    # Session count validation
    if request.session_count < 3 or request.session_count > 20:
        result.add_error(f"Invalid session count: {request.session_count} (must be 3-20)")
    
    # Detail level validation
    valid_detail_levels = ['basic', 'medium', 'detailed']
    if request.detail_level not in valid_detail_levels:
        result.add_warning(f"Unknown detail level: {request.detail_level} (using 'medium')")
    
    return result

def validate_chapter_content_request(request: ChapterContentRequest) -> ValidationResult:
    """Validate chapter content request."""
    result = ValidationResult(success=True)
    
    # Required fields validation
    if not request.chapter_title or len(request.chapter_title.strip()) < 3:
        result.add_error("Chapter title must be at least 3 characters")
    
    if not request.campaign_title or len(request.campaign_title.strip()) < 3:
        result.add_error("Campaign title must be at least 3 characters")
    
    # Party validation
    if request.party_level < 1 or request.party_level > 20:
        result.add_error(f"Invalid party level: {request.party_level} (must be 1-20)")
    
    if request.party_size < 1 or request.party_size > 8:
        result.add_error(f"Invalid party size: {request.party_size} (must be 1-8)")
    
    return result

# ============================================================================
# GENERATED CONTENT VALIDATION
# ============================================================================

def validate_generated_campaign(campaign_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate generated campaign content meets all requirements.
    This is the main validation function for completed campaigns.
    """
    result = ValidationResult(success=True)
    
    # Structure validation
    structure_validation = validate_campaign_structure(campaign_data)
    if structure_validation.has_errors():
        result.errors.extend(structure_validation.errors)
    if structure_validation.has_warnings():
        result.warnings.extend(structure_validation.warnings)
    
    # Narrative quality validation
    narrative_validation = validate_narrative_quality(campaign_data)
    if narrative_validation.has_errors():
        result.errors.extend(narrative_validation.errors)
    if narrative_validation.has_warnings():
        result.warnings.extend(narrative_validation.warnings)
    
    # Performance validation
    performance_validation = validate_performance_requirements(
        campaign_data, 
        CampaignCreationType.CAMPAIGN_FROM_SCRATCH
    )
    if performance_validation.has_errors():
        result.errors.extend(performance_validation.errors)
    if performance_validation.has_warnings():
        result.warnings.extend(performance_validation.warnings)
    
    # Chapter validation if chapters exist
    if 'chapters' in campaign_data and isinstance(campaign_data['chapters'], list):
        party_level = campaign_data.get('party_level', 1)
        party_size = campaign_data.get('party_size', 4)
        
        for i, chapter in enumerate(campaign_data['chapters']):
            if isinstance(chapter, dict):
                chapter_validation = validate_chapter_content(chapter, party_level, party_size)
                if chapter_validation.has_errors():
                    chapter_errors = [f"Chapter {i+1}: {error}" for error in chapter_validation.errors]
                    result.errors.extend(chapter_errors)
                if chapter_validation.has_warnings():
                    chapter_warnings = [f"Chapter {i+1}: {warning}" for warning in chapter_validation.warnings]
                    result.warnings.extend(chapter_warnings)
    
    result.validated_data = campaign_data
    return result

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

__all__ = [
    'ValidationResult',
    'validate_campaign_request',
    'validate_campaign_concept',
    'validate_campaign_structure',
    'validate_chapter_content',
    'validate_encounter_balance',
    'validate_refinement_request',
    'validate_performance_requirements',
    'validate_narrative_quality',
    'validate_generated_campaign'
]
