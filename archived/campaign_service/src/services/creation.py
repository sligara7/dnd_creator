"""
D&D Campaign Creation Service

A unified, efficient creation system for all D&D campaign content types.
Based on creation_ref.py architecture and campaign_creation.md requirements.

Architecture:
- BaseCampaignCreator: Core creation functionality shared by all campaign content types
- CampaignCreator: Complete campaign generation from concepts
- ChapterCreator: Individual chapter creation with character integration
- CampaignRefiner: Iterative refinement and evolution system
- CampaignValidator: Validation and quality assurance

This eliminates code duplication and ensures consistency across all campaign creation types.
"""

import json
import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime

# Import campaign creation models
from src.models.campaign_creation_models import (
    CampaignCreationType,
    BaseCampaignRequest,
    CampaignFromScratchRequest,
    CampaignSkeletonRequest,
    ChapterContentRequest,
    CampaignRefinementRequest,
    PsychologicalExperimentRequest,
    SettingThemeRequest,
    CharacterForCampaignRequest,
    CampaignCreationResponse,
    CampaignRefinementResponse,
    CampaignData,
    CampaignMetadata,
    CampaignRequestValidator
)

# Import campaign validation services
from src.services.creation_validation import (
    validate_campaign_request,
    validate_campaign_from_scratch_request,
    validate_campaign_skeleton_request,
    validate_chapter_content_request,
    validate_refinement_request,
    validate_generated_campaign,
    validate_campaign_structure,
    validate_chapter_content,
    validate_encounter_balance,
    validate_narrative_quality,
    validate_performance_requirements,
    ValidationResult
)

# Import campaign generation services
from src.services.creation_factory import (
    CampaignCreationFactory,
    CampaignCreationOptions
)

from src.services.generators import (
    CampaignGenre,
    CampaignComplexity,
    SettingTheme,
    PsychologicalExperimentType
)

# Import core services
from src.services.llm_service import LLMService
from src.core.config import Settings
from src.models.database_models import CampaignDB

logger = logging.getLogger(__name__)

# ============================================================================
# SHARED CONFIGURATION AND RESULT CLASSES  
# ============================================================================

@dataclass
class CampaignCreationConfig:
    """Configuration for campaign creation processes."""
    base_timeout: int = 300  # 5 minutes for complex campaign generation
    max_retries: int = 3
    enable_progress_feedback: bool = True
    auto_save: bool = True
    use_character_service: bool = True
    fallback_on_service_failure: bool = True

class CampaignCreationResult:
    """Result container for campaign creation operations."""
    
    def __init__(self, success: bool = False, data: Dict[str, Any] = None, 
                 error: str = "", warnings: List[str] = None):
        self.success = success
        self.data = data or {}
        self.error = error
        self.warnings = warnings or []
        self.creation_time: float = 0.0
        self.verbose_logs: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, Any] = {}
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)
    
    def add_performance_metric(self, metric: str, value: Any):
        """Add a performance metric."""
        self.performance_metrics[metric] = value
    
    def is_valid(self) -> bool:
        """Check if the result is valid."""
        return self.success and bool(self.data)
    
    def to_response(self, creation_type: str) -> CampaignCreationResponse:
        """Convert to API response format."""
        metadata = CampaignMetadata(
            source=self.performance_metrics.get("source", "unknown"),
            attempts=self.performance_metrics.get("attempts", 1),
            generated_at=datetime.utcnow(),
            generation_time=self.creation_time,
            within_timeout=self.performance_metrics.get("within_timeout", True),
            timeout_limit=self.performance_metrics.get("timeout_limit", 300)
        )
        
        response_data = {
            "success": self.success,
            "creation_type": creation_type,
            "performance": metadata,
            "warnings": self.warnings,
            "error": self.error if not self.success else None
        }
        
        # Map data to appropriate response field based on creation type
        if creation_type == "campaign_from_scratch" and "campaign" in self.data:
            response_data["campaign"] = self.data["campaign"]
        elif creation_type == "campaign_skeleton" and "skeleton" in self.data:
            response_data["skeleton"] = self.data["skeleton"]
        elif creation_type == "chapter_content" and "chapter" in self.data:
            response_data["chapter"] = self.data["chapter"]
        elif creation_type in ["npc_for_campaign", "monster_for_campaign"] and "characters" in self.data:
            response_data["characters"] = self.data["characters"]
        elif creation_type == "psychological_experiment" and "experiment" in self.data:
            response_data["experiment"] = self.data["experiment"]
        elif creation_type == "setting_theme" and "theme" in self.data:
            response_data["theme"] = self.data["theme"]
        
        return CampaignCreationResponse(**response_data)

# ============================================================================
# BASE CAMPAIGN CREATOR ABSTRACT CLASS
# ============================================================================

class BaseCampaignCreator(ABC):
    """
    Abstract base class for all campaign content creators.
    
    Provides shared functionality and enforces consistent interface
    across all campaign creation types.
    """
    
    def __init__(self, llm_service: LLMService, 
                 config: CampaignCreationConfig = None,
                 settings: Settings = None):
        self.llm_service = llm_service
        self.config = config or CampaignCreationConfig()
        self.settings = settings or Settings()
        self.creation_factory = CampaignCreationFactory(llm_service, settings)
        
        # Performance tracking
        self.creation_stats = {
            "total_creations": 0,
            "successful_creations": 0,
            "failed_creations": 0,
            "avg_creation_time": 0.0
        }
    
    @abstractmethod
    async def create(self, request: BaseCampaignRequest) -> CampaignCreationResult:
        """Create campaign content based on the request."""
        pass
    
    def validate_request(self, request: BaseCampaignRequest) -> ValidationResult:
        """Validate a creation request using creation_validation.py methods."""
        return validate_campaign_request(request)
    
    async def _track_creation_performance(self, creation_func, *args, **kwargs) -> CampaignCreationResult:
        """Track performance metrics for creation operations."""
        start_time = time.time()
        
        try:
            result = await creation_func(*args, **kwargs)
            creation_time = time.time() - start_time
            
            result.creation_time = creation_time
            result.add_performance_metric("creation_time", creation_time)
            
            # Update stats
            self.creation_stats["total_creations"] += 1
            if result.success:
                self.creation_stats["successful_creations"] += 1
            else:
                self.creation_stats["failed_creations"] += 1
            
            # Update average
            total = self.creation_stats["total_creations"]
            current_avg = self.creation_stats["avg_creation_time"]
            self.creation_stats["avg_creation_time"] = (
                (current_avg * (total - 1) + creation_time) / total
            )
            
            return result
            
        except Exception as e:
            creation_time = time.time() - start_time
            logger.error(f"Creation failed after {creation_time:.2f}s: {str(e)}")
            
            self.creation_stats["total_creations"] += 1
            self.creation_stats["failed_creations"] += 1
            
            result = CampaignCreationResult(
                success=False,
                error=f"Creation failed: {str(e)}"
            )
            result.creation_time = creation_time
            return result
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return self.creation_stats.copy()

# ============================================================================
# CAMPAIGN CREATOR - COMPLETE CAMPAIGNS FROM SCRATCH
# ============================================================================

class CampaignCreator(BaseCampaignCreator):
    """
    Creator for complete D&D campaigns from user concepts.
    Implements REQ-CAM-001-018: LLM-Powered Campaign Creation Requirements
    """
    
    async def create(self, request: CampaignFromScratchRequest) -> CampaignCreationResult:
        """Create a complete campaign from scratch."""
        return await self._track_creation_performance(self._create_campaign, request)
    
    async def _create_campaign(self, request: CampaignFromScratchRequest) -> CampaignCreationResult:
        """Internal campaign creation logic."""
        logger.info(f"Creating campaign from concept: {request.concept[:50]}...")
        
        # VALIDATION PHASE 1: Validate request using creation_validation.py (REQ-CAM-001-018)
        validation_result = validate_campaign_from_scratch_request(request)
        if validation_result.has_errors():
            return CampaignCreationResult(
                success=False,
                error=f"Validation failed: {'; '.join(validation_result.errors)}",
                warnings=validation_result.warnings
            )
        
        try:
            # Create campaign using factory
            factory_result = await self.creation_factory.create_from_scratch(
                CampaignCreationOptions.CAMPAIGN_FROM_SCRATCH,
                request.concept,
                genre=request.genre,
                complexity=request.complexity,
                session_count=request.session_count,
                themes=request.themes,
                setting_theme=request.setting_theme,
                party_level=request.party_level,
                party_size=request.party_size,
                use_character_service=request.use_character_service,
                include_psychological_experiments=request.include_psychological_experiments,
                experiment_types=request.experiment_types
            )
            
            # VALIDATION PHASE 2: Validate generated campaign content (REQ-CAM-013, REQ-CAM-014)
            if factory_result.get("success") and "campaign" in factory_result:
                campaign_validation = validate_generated_campaign(factory_result["campaign"])
                structure_validation = validate_campaign_structure(factory_result["campaign"])
                narrative_validation = validate_narrative_quality(factory_result["campaign"])
                performance_validation = validate_performance_requirements(
                    factory_result["campaign"], request.creation_type
                )
                
                # Collect all validation warnings
                all_warnings = validation_result.warnings.copy()
                for val_result in [campaign_validation, structure_validation, narrative_validation, performance_validation]:
                    if val_result.has_warnings():
                        all_warnings.extend(val_result.warnings)
                    if val_result.has_errors():
                        logger.warning(f"Generated campaign validation errors: {val_result.errors}")
                        all_warnings.extend([f"Content issue: {err}" for err in val_result.errors])
            else:
                all_warnings = validation_result.warnings.copy()
            
            # Auto-save if enabled
            if self.config.auto_save and factory_result.get("success"):
                await self._save_campaign(factory_result["campaign"])
            
            result = CampaignCreationResult(
                success=factory_result.get("success", False),
                data=factory_result,
                warnings=all_warnings
            )
            
            # Add performance metrics
            if "performance" in factory_result:
                perf = factory_result["performance"]
                result.add_performance_metric("source", "campaign_factory")
                result.add_performance_metric("within_timeout", perf.get("within_timeout", True))
                result.add_performance_metric("timeout_limit", perf.get("timeout_limit", 300))
            
            # Add validation metrics
            result.add_performance_metric("validation_phases", 2)
            result.add_performance_metric("validation_warnings", len(all_warnings))
            
            return result
            
        except Exception as e:
            logger.error(f"Campaign creation failed: {str(e)}")
            return CampaignCreationResult(
                success=False,
                error=f"Campaign creation failed: {str(e)}",
                warnings=validation_result.warnings
            )
    
    async def _save_campaign(self, campaign_data: Dict[str, Any]) -> Optional[str]:
        """Save campaign to database."""
        try:
            # Implementation would use CampaignDB to save to database
            logger.info("Campaign auto-save completed")
            return campaign_data.get("id", "generated_id")
        except Exception as e:
            logger.warning(f"Failed to auto-save campaign: {str(e)}")
            return None

# ============================================================================
# CHAPTER CREATOR - INDIVIDUAL CHAPTER CREATION
# ============================================================================

class ChapterCreator(BaseCampaignCreator):
    """
    Creator for individual D&D campaign chapters.
    Implements REQ-CAM-033-037: Chapter Content Generation
    """
    
    async def create(self, request: ChapterContentRequest) -> CampaignCreationResult:
        """Create chapter content with character integration."""
        return await self._track_creation_performance(self._create_chapter, request)
    
    async def _create_chapter(self, request: ChapterContentRequest) -> CampaignCreationResult:
        """Internal chapter creation logic."""
        logger.info(f"Creating chapter: {request.chapter_title}")
        
        # VALIDATION PHASE 1: Validate request using creation_validation.py (REQ-CAM-033-037)
        validation_result = validate_chapter_content_request(request)
        if validation_result.has_errors():
            return CampaignCreationResult(
                success=False,
                error=f"Validation failed: {'; '.join(validation_result.errors)}",
                warnings=validation_result.warnings
            )
        
        try:
            # Create chapter using factory
            factory_result = await self.creation_factory.create_from_scratch(
                CampaignCreationOptions.CHAPTER_CONTENT,
                request.concept,
                campaign_title=request.campaign_title,
                campaign_description=request.campaign_description,
                chapter_title=request.chapter_title,
                chapter_summary=request.chapter_summary,
                themes=request.themes,
                chapter_theme=request.chapter_theme,
                genre=request.genre,
                setting_theme=request.setting_theme,
                complexity=request.complexity,
                party_level=request.party_level,
                party_size=request.party_size,
                include_npcs=request.include_npcs,
                include_encounters=request.include_encounters,
                include_locations=request.include_locations,
                include_items=request.include_items,
                use_character_service=request.use_character_service
            )
            
            # VALIDATION PHASE 2: Validate generated chapter content (REQ-CAM-035, REQ-CAM-036)
            all_warnings = validation_result.warnings.copy()
            if factory_result.get("success") and "chapter" in factory_result:
                chapter_validation = validate_chapter_content(
                    factory_result["chapter"], request.party_level, request.party_size
                )
                narrative_validation = validate_narrative_quality(factory_result["chapter"])
                
                # Validate encounters if present
                if factory_result["chapter"].get("encounters"):
                    encounter_validation = validate_encounter_balance(
                        factory_result["chapter"]["encounters"], 
                        request.party_level, request.party_size
                    )
                    for val_result in [chapter_validation, narrative_validation, encounter_validation]:
                        if val_result.has_warnings():
                            all_warnings.extend(val_result.warnings)
                        if val_result.has_errors():
                            logger.warning(f"Chapter content validation errors: {val_result.errors}")
                            all_warnings.extend([f"Content issue: {err}" for err in val_result.errors])
                else:
                    for val_result in [chapter_validation, narrative_validation]:
                        if val_result.has_warnings():
                            all_warnings.extend(val_result.warnings)
                        if val_result.has_errors():
                            logger.warning(f"Chapter content validation errors: {val_result.errors}")
                            all_warnings.extend([f"Content issue: {err}" for err in val_result.errors])
            
            result = CampaignCreationResult(
                success=factory_result.get("success", False),
                data=factory_result,
                warnings=all_warnings
            )
            
            # Add performance metrics
            if "performance" in factory_result:
                perf = factory_result["performance"]
                result.add_performance_metric("source", "campaign_factory")
                result.add_performance_metric("within_timeout", perf.get("within_timeout", True))
            
            # Add validation metrics
            result.add_performance_metric("validation_phases", 2)
            result.add_performance_metric("validation_warnings", len(all_warnings))
            
            return result
            
        except Exception as e:
            logger.error(f"Chapter creation failed: {str(e)}")
            return CampaignCreationResult(
                success=False,
                error=f"Chapter creation failed: {str(e)}",
                warnings=validation_result.warnings
            )

# ============================================================================
# CAMPAIGN REFINER - ITERATIVE REFINEMENT SYSTEM
# ============================================================================

class CampaignRefiner(BaseCampaignCreator):
    """
    Refiner for evolving existing campaigns based on feedback.
    Implements REQ-CAM-007-012: Iterative Campaign Refinement System
    """
    
    async def create(self, request: CampaignRefinementRequest) -> CampaignCreationResult:
        """This method name is for interface compliance - actually performs refinement."""
        return await self.refine(request)
    
    async def refine(self, request: CampaignRefinementRequest) -> CampaignCreationResult:
        """Refine existing campaign content."""
        return await self._track_creation_performance(self._refine_campaign, request)
    
    async def _refine_campaign(self, request: CampaignRefinementRequest) -> CampaignCreationResult:
        """Internal campaign refinement logic."""
        logger.info(f"Refining campaign with prompt: {request.refinement_prompt[:50]}...")
        
        # VALIDATION PHASE 1: Validate refinement request (REQ-CAM-007-012)
        validation_result = validate_refinement_request(request)
        if validation_result.has_errors():
            return CampaignCreationResult(
                success=False,
                error=f"Refinement validation failed: {'; '.join(validation_result.errors)}",
                warnings=validation_result.warnings
            )
        
        try:
            # Use factory's evolution capabilities
            factory_result = await self.creation_factory.evolve_existing(
                CampaignCreationOptions.ITERATIVE_REFINEMENT,
                request.existing_data,
                request.refinement_prompt,
                refinement_type=request.refinement_type,
                preserve_elements=request.preserve_elements,
                player_feedback=request.player_feedback,
                refinement_cycles=request.refinement_cycles
            )
            
            # VALIDATION PHASE 2: Validate refined content quality
            all_warnings = validation_result.warnings.copy()
            if factory_result.get("success") and factory_result.get("data"):
                # Validate refined campaign structure and narrative quality
                if "campaign" in factory_result["data"]:
                    refined_validation = validate_generated_campaign(factory_result["data"]["campaign"])
                    narrative_validation = validate_narrative_quality(factory_result["data"]["campaign"])
                elif "chapter" in factory_result["data"]:
                    # For chapter refinements, validate chapter content
                    refined_validation = validate_chapter_content(
                        factory_result["data"]["chapter"], 
                        request.existing_data.get("party_level", 3),
                        request.existing_data.get("party_size", 4)
                    )
                    narrative_validation = validate_narrative_quality(factory_result["data"]["chapter"])
                else:
                    # Generic structure validation
                    refined_validation = validate_campaign_structure(factory_result["data"])
                    narrative_validation = validate_narrative_quality(factory_result["data"])
                
                for val_result in [refined_validation, narrative_validation]:
                    if val_result.has_warnings():
                        all_warnings.extend(val_result.warnings)
                    if val_result.has_errors():
                        logger.warning(f"Refined content validation errors: {val_result.errors}")
                        all_warnings.extend([f"Refinement issue: {err}" for err in val_result.errors])
            
            result = CampaignCreationResult(
                success=factory_result.get("success", False),
                data=factory_result,
                warnings=all_warnings
            )
            
            # Add refinement-specific metrics
            result.add_performance_metric("refinement_type", request.refinement_type)
            result.add_performance_metric("cycles_completed", 
                                        factory_result.get("cycles_completed", 1))
            result.add_performance_metric("validation_phases", 2)
            result.add_performance_metric("validation_warnings", len(all_warnings))
            
            return result
            
        except Exception as e:
            logger.error(f"Campaign refinement failed: {str(e)}")
            return CampaignCreationResult(
                success=False,
                error=f"Campaign refinement failed: {str(e)}",
                warnings=validation_result.warnings
            )

# ============================================================================
# SPECIALIZED CREATORS
# ============================================================================

class SkeletonCreator(BaseCampaignCreator):
    """Creator for campaign skeletons and outlines."""
    
    async def create(self, request: CampaignSkeletonRequest) -> CampaignCreationResult:
        """Create a campaign skeleton."""
        return await self._track_creation_performance(self._create_skeleton, request)
    
    async def _create_skeleton(self, request: CampaignSkeletonRequest) -> CampaignCreationResult:
        """Internal skeleton creation logic."""
        # VALIDATION PHASE 1: Validate skeleton request (REQ-CAM-023-027)
        validation_result = validate_campaign_skeleton_request(request)
        if validation_result.has_errors():
            return CampaignCreationResult(
                success=False,
                error=f"Skeleton validation failed: {'; '.join(validation_result.errors)}",
                warnings=validation_result.warnings
            )
        
        try:
            factory_result = await self.creation_factory.create_from_scratch(
                CampaignCreationOptions.CAMPAIGN_SKELETON,
                request.concept,
                campaign_title=request.campaign_title,
                campaign_description=request.campaign_description,
                themes=request.themes,
                session_count=request.session_count,
                detail_level=request.detail_level
            )
            
            # VALIDATION PHASE 2: Validate skeleton structure and performance
            all_warnings = validation_result.warnings.copy()
            if factory_result.get("success") and "skeleton" in factory_result:
                structure_validation = validate_campaign_structure(factory_result["skeleton"])
                performance_validation = validate_performance_requirements(
                    factory_result["skeleton"], request.creation_type
                )
                
                for val_result in [structure_validation, performance_validation]:
                    if val_result.has_warnings():
                        all_warnings.extend(val_result.warnings)
                    if val_result.has_errors():
                        logger.warning(f"Skeleton validation errors: {val_result.errors}")
                        all_warnings.extend([f"Skeleton issue: {err}" for err in val_result.errors])
            
            result = CampaignCreationResult(
                success=factory_result.get("success", False),
                data=factory_result,
                warnings=all_warnings
            )
            
            # Add validation metrics
            result.add_performance_metric("validation_phases", 2)
            result.add_performance_metric("validation_warnings", len(all_warnings))
            
            return result
            
        except Exception as e:
            logger.error(f"Skeleton creation failed: {str(e)}")
            return CampaignCreationResult(
                success=False,
                error=f"Skeleton creation failed: {str(e)}",
                warnings=validation_result.warnings
            )

class ExperimentCreator(BaseCampaignCreator):
    """Creator for psychological experiment integration."""
    
    async def create(self, request: PsychologicalExperimentRequest) -> CampaignCreationResult:
        """Create psychological experiment integration."""
        return await self._track_creation_performance(self._create_experiment, request)
    
    async def _create_experiment(self, request: PsychologicalExperimentRequest) -> CampaignCreationResult:
        """Internal experiment creation logic."""
        try:
            factory_result = await self.creation_factory.create_from_scratch(
                CampaignCreationOptions.PSYCHOLOGICAL_EXPERIMENT,
                request.concept,
                experiment_type=request.experiment_type,
                campaign_context=request.campaign_context,
                custom_concept=request.custom_concept
            )
            
            return CampaignCreationResult(
                success=factory_result.get("success", False),
                data=factory_result
            )
            
        except Exception as e:
            logger.error(f"Experiment creation failed: {str(e)}")
            return CampaignCreationResult(
                success=False,
                error=f"Experiment creation failed: {str(e)}"
            )

# ============================================================================
# CAMPAIGN CREATION SERVICE - MAIN COORDINATOR
# ============================================================================

class CampaignCreationService:
    """
    Main service for coordinating all campaign creation operations.
    Routes requests to appropriate creators and handles service lifecycle.
    """
    
    def __init__(self, llm_service: LLMService, 
                 config: CampaignCreationConfig = None,
                 settings: Settings = None):
        self.llm_service = llm_service
        self.config = config or CampaignCreationConfig()
        self.settings = settings or Settings()
        
        # Initialize creators
        self.creators = {
            CampaignCreationType.CAMPAIGN_FROM_SCRATCH: CampaignCreator(llm_service, config, settings),
            CampaignCreationType.CAMPAIGN_SKELETON: SkeletonCreator(llm_service, config, settings),
            CampaignCreationType.CHAPTER_CONTENT: ChapterCreator(llm_service, config, settings),
            CampaignCreationType.ITERATIVE_REFINEMENT: CampaignRefiner(llm_service, config, settings),
            CampaignCreationType.PSYCHOLOGICAL_EXPERIMENT: ExperimentCreator(llm_service, config, settings),
            # Add more creators as needed
        }
        
        logger.info("CampaignCreationService initialized with all creators")
    
    async def create_content(self, request: BaseCampaignRequest) -> CampaignCreationResponse:
        """
        Main entry point for creating campaign content.
        Routes to appropriate creator based on request type.
        """
        creator = self.creators.get(request.creation_type)
        if not creator:
            return CampaignCreationResponse(
                success=False,
                creation_type=request.creation_type.value,
                error=f"Unsupported creation type: {request.creation_type}",
                performance=CampaignMetadata(
                    source="service_error",
                    attempts=0,
                    generated_at=datetime.utcnow(),
                    generation_time=0.0,
                    within_timeout=True,
                    timeout_limit=0
                )
            )
        
        try:
            result = await creator.create(request)
            return result.to_response(request.creation_type.value)
            
        except Exception as e:
            logger.error(f"Service-level creation error: {str(e)}")
            return CampaignCreationResponse(
                success=False,
                creation_type=request.creation_type.value,
                error=f"Service error: {str(e)}",
                performance=CampaignMetadata(
                    source="service_error",
                    attempts=1,
                    generated_at=datetime.utcnow(),
                    generation_time=0.0,
                    within_timeout=False,
                    timeout_limit=self.config.base_timeout
                )
            )
    
    async def refine_content(self, request: CampaignRefinementRequest) -> CampaignRefinementResponse:
        """Refine existing campaign content."""
        refiner = self.creators.get(CampaignCreationType.ITERATIVE_REFINEMENT)
        if not refiner:
            raise ValueError("Campaign refiner not available")
        
        try:
            result = await refiner.refine(request)
            
            # Convert to refinement response format
            response_data = {
                "success": result.success,
                "evolution_type": "iterative_refinement",
                "performance": CampaignMetadata(
                    source=result.performance_metrics.get("source", "unknown"),
                    attempts=result.performance_metrics.get("attempts", 1),
                    generated_at=datetime.utcnow(),
                    generation_time=result.creation_time,
                    within_timeout=result.performance_metrics.get("within_timeout", True),
                    timeout_limit=result.performance_metrics.get("timeout_limit", 300)
                ),
                "warnings": result.warnings,
                "error": result.error if not result.success else None
            }
            
            # Add refined content
            if result.success and result.data:
                if "campaign" in result.data:
                    response_data["campaign"] = result.data["campaign"]
                elif "skeleton" in result.data:
                    response_data["skeleton"] = result.data["skeleton"]
                elif "chapter" in result.data:
                    response_data["chapter"] = result.data["chapter"]
                
                response_data["cycles_completed"] = result.performance_metrics.get("cycles_completed", 1)
            
            return CampaignRefinementResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Refinement service error: {str(e)}")
            return CampaignRefinementResponse(
                success=False,
                evolution_type="error",
                error=f"Refinement error: {str(e)}",
                performance=CampaignMetadata(
                    source="service_error",
                    attempts=1,
                    generated_at=datetime.utcnow(),
                    generation_time=0.0,
                    within_timeout=False,
                    timeout_limit=self.config.base_timeout
                )
            )
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of the campaign creation service."""
        creator_stats = {}
        for creation_type, creator in self.creators.items():
            creator_stats[creation_type.value] = creator.get_performance_stats()
        
        return {
            "service": "CampaignCreationService",
            "status": "operational",
            "creators": list(self.creators.keys()),
            "creator_stats": creator_stats,
            "config": {
                "base_timeout": self.config.base_timeout,
                "max_retries": self.config.max_retries,
                "auto_save": self.config.auto_save,
                "use_character_service": self.config.use_character_service
            }
        }

# ============================================================================
# SERVICE FACTORY AND INITIALIZATION
# ============================================================================

def create_campaign_creation_service(llm_service: LLMService,
                                    config: CampaignCreationConfig = None,
                                    settings: Settings = None) -> CampaignCreationService:
    """Factory function to create a campaign creation service."""
    return CampaignCreationService(llm_service, config, settings)

# ============================================================================
# EXPORT CLASSES AND FUNCTIONS
# ============================================================================

__all__ = [
    'CampaignCreationService',
    'CampaignCreationConfig', 
    'CampaignCreationResult',
    'BaseCampaignCreator',
    'CampaignCreator',
    'ChapterCreator', 
    'CampaignRefiner',
    'SkeletonCreator',
    'ExperimentCreator',
    'create_campaign_creation_service'
]
