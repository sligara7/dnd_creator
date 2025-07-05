"""
D&D Campaign Content Coordinator

This module provides high-level coordination for complex campaign generation
workflows that involve multiple creation types and dependencies.

Handles orchestration of:
- Campaign creation with chapters, NPCs, and encounters
- Multi-chapter campaign generation
- Campaign skeleton expansion into full content
- Cross-chapter consistency and narrative flow
- Batch campaign content creation
- Campaign validation and quality assurance
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from src.models.campaign_creation_models import (
    CampaignCreationType, CampaignFromScratchRequest, CampaignSkeletonRequest,
    ChapterContentRequest, CampaignRefinementRequest, CampaignCreationResponse
)
from src.services.creation import CampaignCreationService, CampaignCreationConfig
from src.services.creation_validation import (
    validate_campaign_structure, validate_narrative_quality,
    validate_chapter_content, validate_encounter_balance
)
from src.services.llm_service import LLMService
from src.core.config import Settings

logger = logging.getLogger(__name__)

# ============================================================================
# CAMPAIGN COORDINATION REQUEST MODELS
# ============================================================================

@dataclass
class CampaignWorkflowRequest:
    """Request for complex campaign generation workflows."""
    workflow_type: str  # "full_campaign", "skeleton_expansion", "multi_chapter"
    primary_params: Dict[str, Any]
    chapters_needed: int = 8
    auto_generate_npcs: bool = True
    auto_generate_encounters: bool = True
    auto_generate_items: bool = True
    consistency_checks: bool = True
    narrative_flow_validation: bool = True

@dataclass
class ChapterGenerationBatch:
    """Batch request for generating multiple chapters."""
    campaign_id: str
    campaign_context: Dict[str, Any]
    chapter_outlines: List[Dict[str, Any]]
    party_level_progression: List[int]
    thematic_consistency: bool = True

# ============================================================================
# CAMPAIGN CONTENT COORDINATOR
# ============================================================================

class CampaignContentCoordinator:
    """
    Coordinates complex campaign generation workflows.
    
    Handles cases where creating a campaign requires orchestrating multiple
    creation types with dependencies and consistency requirements.
    """
    
    def __init__(self, llm_service: LLMService, 
                 config: CampaignCreationConfig = None,
                 settings: Settings = None):
        self.llm_service = llm_service
        self.config = config or CampaignCreationConfig()
        self.settings = settings or Settings()
        
        # Initialize the campaign creation service
        self.campaign_service = CampaignCreationService(llm_service, config, settings)
        
        # Workflow tracking
        self.workflow_stats = {
            "total_workflows": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "avg_workflow_time": 0.0
        }
        
        logger.info("CampaignContentCoordinator initialized")
    
    # ========================================================================
    # FULL CAMPAIGN GENERATION WORKFLOWS
    # ========================================================================
    
    async def generate_complete_campaign_workflow(self, 
                                                 concept: str,
                                                 **campaign_params) -> Dict[str, Any]:
        """
        Generate a complete campaign with all content types.
        
        Workflow:
        1. Create campaign skeleton
        2. Generate all chapters with content
        3. Create NPCs, encounters, and items for each chapter
        4. Validate narrative consistency across all content
        5. Apply final quality assurance
        """
        start_time = datetime.utcnow()
        workflow_id = f"campaign_workflow_{int(start_time.timestamp())}"
        
        logger.info(f"Starting complete campaign workflow {workflow_id}")
        
        result = {
            "workflow_id": workflow_id,
            "workflow_type": "complete_campaign",
            "start_time": start_time.isoformat(),
            "campaign": None,
            "chapters": [],
            "npcs": [],
            "encounters": [],
            "items": [],
            "validation_results": [],
            "warnings": [],
            "success": False
        }
        
        try:
            # Step 1: Create campaign foundation
            campaign_request = CampaignFromScratchRequest(
                creation_type=CampaignCreationType.CAMPAIGN_FROM_SCRATCH,
                concept=concept,
                **campaign_params
            )
            
            campaign_response = await self.campaign_service.create_content(campaign_request)
            if not campaign_response.success:
                result["error"] = f"Campaign creation failed: {campaign_response.error}"
                return result
            
            result["campaign"] = campaign_response.campaign
            result["warnings"].extend(campaign_response.warnings or [])
            
            # Step 2: Generate campaign skeleton
            skeleton_request = CampaignSkeletonRequest(
                creation_type=CampaignCreationType.CAMPAIGN_SKELETON,
                concept=concept,
                campaign_title=campaign_response.campaign.get("title", "Generated Campaign"),
                campaign_description=campaign_response.campaign.get("description", ""),
                session_count=campaign_params.get("session_count", 10)
            )
            
            skeleton_response = await self.campaign_service.create_content(skeleton_request)
            if skeleton_response.success:
                result["skeleton"] = skeleton_response.skeleton
                result["warnings"].extend(skeleton_response.warnings or [])
            
            # Step 3: Generate chapters with full content
            chapters_result = await self._generate_all_chapters(
                campaign_response.campaign,
                skeleton_response.skeleton if skeleton_response.success else None,
                campaign_params
            )
            
            result["chapters"] = chapters_result["chapters"]
            result["npcs"].extend(chapters_result["npcs"])
            result["encounters"].extend(chapters_result["encounters"])
            result["items"].extend(chapters_result["items"])
            result["warnings"].extend(chapters_result["warnings"])
            
            # Step 4: Validate campaign consistency
            consistency_result = await self._validate_campaign_consistency(result)
            result["validation_results"].append(consistency_result)
            result["warnings"].extend(consistency_result.get("warnings", []))
            
            # Step 5: Final success determination
            result["success"] = True
            result["end_time"] = datetime.utcnow().isoformat()
            
            self.workflow_stats["successful_workflows"] += 1
            logger.info(f"Campaign workflow {workflow_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Campaign workflow {workflow_id} failed: {str(e)}")
            result["error"] = str(e)
            result["end_time"] = datetime.utcnow().isoformat()
            self.workflow_stats["failed_workflows"] += 1
        
        finally:
            self.workflow_stats["total_workflows"] += 1
            workflow_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Update average workflow time
            total = self.workflow_stats["total_workflows"]
            current_avg = self.workflow_stats["avg_workflow_time"]
            self.workflow_stats["avg_workflow_time"] = (
                (current_avg * (total - 1) + workflow_time) / total
            )
        
        return result
    
    async def expand_skeleton_to_full_campaign(self, 
                                              skeleton_data: Dict[str, Any],
                                              expansion_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expand a campaign skeleton into a full campaign with all content.
        
        Takes an existing skeleton and generates detailed chapters, NPCs, etc.
        """
        logger.info("Expanding campaign skeleton to full campaign")
        
        result = {
            "workflow_type": "skeleton_expansion",
            "original_skeleton": skeleton_data,
            "expanded_content": {},
            "success": False
        }
        
        try:
            # Extract chapter outlines from skeleton
            chapter_outlines = self._extract_chapter_outlines_from_skeleton(skeleton_data)
            
            # Generate detailed content for each chapter
            expanded_chapters = []
            for i, outline in enumerate(chapter_outlines):
                chapter_request = ChapterContentRequest(
                    creation_type=CampaignCreationType.CHAPTER_CONTENT,
                    concept=outline.get("concept", outline.get("summary", "")),
                    campaign_title=skeleton_data.get("title", "Campaign"),
                    campaign_description=skeleton_data.get("description", ""),
                    chapter_title=outline.get("title", f"Chapter {i+1}"),
                    chapter_summary=outline.get("summary", ""),
                    party_level=expansion_params.get("party_level", 1 + i//2),  # Level progression
                    party_size=expansion_params.get("party_size", 4),
                    **expansion_params
                )
                
                chapter_response = await self.campaign_service.create_content(chapter_request)
                if chapter_response.success:
                    expanded_chapters.append(chapter_response.chapter)
            
            result["expanded_content"]["chapters"] = expanded_chapters
            result["success"] = True
            
        except Exception as e:
            logger.error(f"Skeleton expansion failed: {str(e)}")
            result["error"] = str(e)
        
        return result
    
    # ========================================================================
    # BATCH CHAPTER GENERATION
    # ========================================================================
    
    async def batch_generate_chapters(self, batch_request: ChapterGenerationBatch) -> Dict[str, Any]:
        """
        Generate multiple chapters in a coordinated batch with consistency checks.
        """
        logger.info(f"Batch generating {len(batch_request.chapter_outlines)} chapters")
        
        result = {
            "workflow_type": "batch_chapters",
            "campaign_id": batch_request.campaign_id,
            "chapters_requested": len(batch_request.chapter_outlines),
            "chapters_generated": [],
            "consistency_checks": [],
            "warnings": [],
            "success": False
        }
        
        try:
            generated_chapters = []
            
            for i, outline in enumerate(batch_request.chapter_outlines):
                # Determine party level for this chapter
                party_level = (batch_request.party_level_progression[i] 
                             if i < len(batch_request.party_level_progression) 
                             else batch_request.party_level_progression[-1])
                
                chapter_request = ChapterContentRequest(
                    creation_type=CampaignCreationType.CHAPTER_CONTENT,
                    concept=outline.get("concept", outline.get("summary", "")),
                    campaign_title=batch_request.campaign_context.get("title", "Campaign"),
                    campaign_description=batch_request.campaign_context.get("description", ""),
                    chapter_title=outline.get("title", f"Chapter {i+1}"),
                    chapter_summary=outline.get("summary", ""),
                    party_level=party_level,
                    party_size=4,  # Default party size
                    themes=batch_request.campaign_context.get("themes", [])
                )
                
                chapter_response = await self.campaign_service.create_content(chapter_request)
                
                if chapter_response.success:
                    generated_chapters.append({
                        "chapter_index": i,
                        "chapter_data": chapter_response.chapter,
                        "warnings": chapter_response.warnings or []
                    })
                    result["warnings"].extend(chapter_response.warnings or [])
                else:
                    logger.warning(f"Chapter {i+1} generation failed: {chapter_response.error}")
                    result["warnings"].append(f"Chapter {i+1} failed: {chapter_response.error}")
            
            result["chapters_generated"] = generated_chapters
            
            # Perform thematic consistency checks if requested
            if batch_request.thematic_consistency:
                consistency_result = await self._validate_chapter_consistency(generated_chapters)
                result["consistency_checks"].append(consistency_result)
                result["warnings"].extend(consistency_result.get("warnings", []))
            
            result["success"] = len(generated_chapters) > 0
            
        except Exception as e:
            logger.error(f"Batch chapter generation failed: {str(e)}")
            result["error"] = str(e)
        
        return result
    
    # ========================================================================
    # CONTENT REFINEMENT WORKFLOWS
    # ========================================================================
    
    async def refine_campaign_narrative_flow(self, 
                                           campaign_data: Dict[str, Any],
                                           refinement_focus: str = "narrative_consistency") -> Dict[str, Any]:
        """
        Refine a campaign to improve narrative flow and consistency.
        """
        logger.info("Refining campaign narrative flow")
        
        refinement_request = CampaignRefinementRequest(
            creation_type=CampaignCreationType.ITERATIVE_REFINEMENT,
            existing_data=campaign_data,
            refinement_prompt=f"Improve the {refinement_focus} of this campaign, ensuring smooth narrative flow between chapters and consistent character development.",
            refinement_type="narrative_enhancement",
            preserve_elements=["main_plot", "character_names", "major_locations"]
        )
        
        try:
            refinement_response = await self.campaign_service.refine_content(refinement_request)
            return {
                "success": refinement_response.success,
                "refined_campaign": refinement_response.campaign if refinement_response.success else None,
                "refinement_details": {
                    "focus": refinement_focus,
                    "cycles_completed": getattr(refinement_response, 'cycles_completed', 1),
                    "evolution_type": refinement_response.evolution_type
                },
                "warnings": refinement_response.warnings or [],
                "error": refinement_response.error
            }
        except Exception as e:
            logger.error(f"Campaign refinement failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # VALIDATION AND CONSISTENCY HELPERS
    # ========================================================================
    
    async def _generate_all_chapters(self, 
                                   campaign_data: Dict[str, Any],
                                   skeleton_data: Optional[Dict[str, Any]],
                                   campaign_params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all chapters for a campaign with coordinated content."""
        result = {
            "chapters": [],
            "npcs": [],
            "encounters": [],
            "items": [],
            "warnings": []
        }
        
        # Determine number of chapters
        session_count = campaign_params.get("session_count", 10)
        chapter_count = min(session_count, 12)  # Max 12 chapters
        
        # Generate each chapter
        for i in range(chapter_count):
            chapter_title = f"Chapter {i+1}: {self._generate_chapter_title(i, campaign_data)}"
            party_level = max(1, 1 + (i * 2))  # Level progression
            
            chapter_request = ChapterContentRequest(
                creation_type=CampaignCreationType.CHAPTER_CONTENT,
                concept=f"Chapter {i+1} of {campaign_data.get('title', 'the campaign')}",
                campaign_title=campaign_data.get("title", "Generated Campaign"),
                campaign_description=campaign_data.get("description", ""),
                chapter_title=chapter_title,
                chapter_summary=f"Chapter {i+1} summary to be generated",
                party_level=party_level,
                party_size=campaign_params.get("party_size", 4),
                themes=campaign_data.get("themes", []),
                include_npcs=True,
                include_encounters=True,
                include_items=True
            )
            
            try:
                chapter_response = await self.campaign_service.create_content(chapter_request)
                if chapter_response.success:
                    chapter_data = chapter_response.chapter
                    result["chapters"].append(chapter_data)
                    
                    # Extract NPCs, encounters, items from chapter
                    if "npcs" in chapter_data:
                        result["npcs"].extend(chapter_data["npcs"])
                    if "encounters" in chapter_data:
                        result["encounters"].extend(chapter_data["encounters"])
                    if "items" in chapter_data:
                        result["items"].extend(chapter_data["items"])
                    
                    result["warnings"].extend(chapter_response.warnings or [])
                else:
                    result["warnings"].append(f"Chapter {i+1} generation failed: {chapter_response.error}")
                    
            except Exception as e:
                logger.warning(f"Chapter {i+1} generation error: {str(e)}")
                result["warnings"].append(f"Chapter {i+1} error: {str(e)}")
        
        return result
    
    async def _validate_campaign_consistency(self, campaign_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate consistency across all campaign content."""
        validation_result = {
            "validation_type": "campaign_consistency",
            "checks_performed": [],
            "warnings": [],
            "errors": [],
            "overall_score": 0
        }
        
        try:
            # Validate campaign structure
            if campaign_result.get("campaign"):
                structure_validation = validate_campaign_structure(campaign_result["campaign"])
                validation_result["checks_performed"].append("campaign_structure")
                if structure_validation.has_warnings():
                    validation_result["warnings"].extend(structure_validation.warnings)
                if structure_validation.has_errors():
                    validation_result["errors"].extend(structure_validation.errors)
            
            # Validate narrative quality across chapters
            if campaign_result.get("chapters"):
                narrative_validation = validate_narrative_quality({
                    "chapters": campaign_result["chapters"]
                })
                validation_result["checks_performed"].append("narrative_quality")
                if narrative_validation.has_warnings():
                    validation_result["warnings"].extend(narrative_validation.warnings)
                if narrative_validation.has_errors():
                    validation_result["errors"].extend(narrative_validation.errors)
            
            # Validate encounter balance across all chapters
            all_encounters = campaign_result.get("encounters", [])
            if all_encounters:
                encounter_validation = validate_encounter_balance(all_encounters, 5, 4)  # Mid-level average
                validation_result["checks_performed"].append("encounter_balance")
                if encounter_validation.has_warnings():
                    validation_result["warnings"].extend(encounter_validation.warnings)
                if encounter_validation.has_errors():
                    validation_result["errors"].extend(encounter_validation.errors)
            
            # Calculate overall quality score
            total_checks = len(validation_result["checks_performed"])
            error_penalty = len(validation_result["errors"]) * 20
            warning_penalty = len(validation_result["warnings"]) * 5
            validation_result["overall_score"] = max(0, 100 - error_penalty - warning_penalty)
            
        except Exception as e:
            logger.error(f"Campaign consistency validation failed: {str(e)}")
            validation_result["errors"].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    async def _validate_chapter_consistency(self, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate consistency between multiple chapters."""
        return {
            "validation_type": "chapter_consistency",
            "chapters_checked": len(chapters),
            "warnings": [],
            "consistency_score": 85  # Placeholder
        }
    
    def _extract_chapter_outlines_from_skeleton(self, skeleton_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract chapter outlines from skeleton data."""
        if "chapters" in skeleton_data:
            return skeleton_data["chapters"]
        
        # Generate basic outlines if not present
        return [
            {"title": f"Chapter {i+1}", "summary": f"Chapter {i+1} content"}
            for i in range(8)  # Default 8 chapters
        ]
    
    def _generate_chapter_title(self, chapter_index: int, campaign_data: Dict[str, Any]) -> str:
        """Generate an appropriate title for a chapter."""
        chapter_titles = [
            "The Call to Adventure",
            "First Steps", 
            "Rising Challenges",
            "The Plot Thickens",
            "Major Conflict",
            "Turning Point",
            "Final Preparations",
            "Climactic Battle",
            "Resolution",
            "New Beginnings"
        ]
        
        if chapter_index < len(chapter_titles):
            return chapter_titles[chapter_index]
        else:
            return f"Chapter {chapter_index + 1}"
    
    # ========================================================================
    # COORDINATOR STATUS AND STATISTICS
    # ========================================================================
    
    def get_coordinator_status(self) -> Dict[str, Any]:
        """Get status and statistics for the campaign coordinator."""
        return {
            "service": "CampaignContentCoordinator",
            "status": "operational",
            "workflow_stats": self.workflow_stats,
            "campaign_service_status": self.campaign_service.get_service_status(),
            "supported_workflows": [
                "complete_campaign",
                "skeleton_expansion", 
                "batch_chapters",
                "narrative_refinement"
            ]
        }

# ============================================================================
# COORDINATOR FACTORY AND EXPORTS
# ============================================================================

def create_campaign_coordinator(llm_service: LLMService,
                               config: CampaignCreationConfig = None,
                               settings: Settings = None) -> CampaignContentCoordinator:
    """Factory function to create a campaign content coordinator."""
    return CampaignContentCoordinator(llm_service, config, settings)

__all__ = [
    'CampaignContentCoordinator',
    'CampaignWorkflowRequest',
    'ChapterGenerationBatch',
    'create_campaign_coordinator'
]
