"""
D&D Campaign Creation Factory

This module coordinates the creation of D&D campaigns by mapping creation types
to their required generators, validators, and backend integrations.

Acts as a single entry point for creating all campaign content with the appropriate
subsets of functionality for each creation type.

Hierarchical Design based on campaign_creation.md requirements:
- CAMPAIGN_FROM_SCRATCH: Complete campaign generation (REQ-CAM-001-018)
- CAMPAIGN_SKELETON: Campaign structure with chapters (REQ-CAM-023-037) 
- CHAPTER_CONTENT: Individual chapter generation (REQ-CAM-033-037)
- ITERATIVE_REFINEMENT: Campaign evolution and refinement (REQ-CAM-007-012)
- ADAPTIVE_CONTENT: Real-time campaign updates (REQ-CAM-055-063)
- BACKEND_INTEGRATION: NPC/Monster/Item generation (REQ-CAM-064-078)

Two Main Workflows:
1. CREATE FROM SCRATCH: Generate entirely new campaigns using LLM based on text concepts
2. EVOLVE EXISTING: Update existing campaigns using refinement prompts and player feedback

Examples:
    # Create new campaign from scratch
    factory = CampaignCreationFactory(llm_service)
    campaign = await factory.create_from_scratch(
        CampaignCreationOptions.CAMPAIGN_FROM_SCRATCH,
        "political intrigue in a steampunk city"
    )
    
    # Generate campaign skeleton
    skeleton = await factory.create_from_scratch(
        CampaignCreationOptions.CAMPAIGN_SKELETON,
        "epic fantasy quest to save the realm"
    )
    
    # Evolve existing campaign based on player feedback
    evolved = await factory.evolve_existing(
        CampaignCreationOptions.ITERATIVE_REFINEMENT,
        existing_campaign_data,
        "players prefer more social encounters and less combat"
    )
"""

from typing import Dict, Any, Optional, Type, List, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import logging
import asyncio

# Generator services - these will be created/imported as we build them
from src.services.generators import (
    CampaignGeneratorFactory,
    CampaignGenre,
    CampaignComplexity,
    SettingTheme,
    PsychologicalExperimentType
)

# LLM and database services
from src.services.llm_service import LLMService
from src.core.config import Settings

logger = logging.getLogger(__name__)

# ============================================================================
# CAMPAIGN CREATION ENUMS AND OPTIONS
# ============================================================================

class CampaignCreationOptions(str, Enum):
    """
    Campaign creation types supported by the factory.
    Based on requirements in campaign_creation.md
    """
    # Core campaign generation (REQ-CAM-001-018)
    CAMPAIGN_FROM_SCRATCH = "campaign_from_scratch"
    CAMPAIGN_SKELETON = "campaign_skeleton" 
    CHAPTER_CONTENT = "chapter_content"
    
    # Refinement and evolution (REQ-CAM-007-012, REQ-CAM-055-063)
    ITERATIVE_REFINEMENT = "iterative_refinement"
    ADAPTIVE_CONTENT = "adaptive_content"
    PLAYER_FEEDBACK_INTEGRATION = "player_feedback_integration"
    
    # Backend integration content (REQ-CAM-064-078)
    NPC_FOR_CAMPAIGN = "npc_for_campaign"
    MONSTER_FOR_CAMPAIGN = "monster_for_campaign"
    EQUIPMENT_FOR_CAMPAIGN = "equipment_for_campaign"
    
    # Specialized content (REQ-CAM-118-132, REQ-CAM-133-147)
    PSYCHOLOGICAL_EXPERIMENT = "psychological_experiment"
    SETTING_THEME = "setting_theme"
    HISTORICAL_RECREATION = "historical_recreation"
    FICTIONAL_ADAPTATION = "fictional_adaptation"

@dataclass
class CampaignCreationConfig:
    """Configuration for creating a specific type of campaign content."""
    primary_generator: str  # Generator type name
    secondary_generators: List[str]  # Additional generators needed
    backend_integrations: List[str]  # Backend services to integrate with
    performance_timeout: int  # Max seconds for generation (REQ-CAM-216-220)
    requires_llm: bool  # Whether LLM service is required
    supports_refinement: bool  # Whether this type supports iterative refinement# ============================================================================
# CAMPAIGN CREATION FACTORY - MAIN CLASS
# ============================================================================

class CampaignCreationFactory:
    """
    Factory class that coordinates the creation of D&D campaign content.
    
    Provides a unified interface for creating campaigns, chapters, NPCs, monsters,
    and other campaign elements using LLM generation and backend service integration.
    
    Implements requirements from campaign_creation.md:
    - REQ-CAM-001-018: LLM-Powered Campaign Creation
    - REQ-CAM-023-037: Chapter-Based Campaign Structure  
    - REQ-CAM-064-078: Auto-Generation via Backend Integration
    - REQ-CAM-118-132: Psychological Experiment Integration
    - REQ-CAM-133-147: Universal Setting Theme System
    - REQ-CAM-216-223: Performance and Scalability Requirements
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None, settings: Optional[Settings] = None):
        self.llm_service = llm_service
        self.settings = settings or Settings()
        self.last_verbose_logs = []  # Store verbose logs from last creation
        
        # Initialize campaign generator factory
        self.generator_factory = CampaignGeneratorFactory(llm_service, settings)
        
        # Build creation configurations
        self._configs = self._build_campaign_creation_configs()
        
        # Performance tracking (REQ-CAM-216-220)
        self.generation_stats = {
            "total_generations": 0,
            "avg_generation_time": 0.0,
            "last_generation_time": 0.0,
            "failed_generations": 0
        }
        
        logger.info("CampaignCreationFactory initialized")
        
    def _build_campaign_creation_configs(self) -> Dict[CampaignCreationOptions, CampaignCreationConfig]:
        """
        Build mapping of campaign creation types to their required components.
        Based on requirements from campaign_creation.md
        """
        return {
            # Core campaign generation (REQ-CAM-001-018)
            CampaignCreationOptions.CAMPAIGN_FROM_SCRATCH: CampaignCreationConfig(
                primary_generator="campaign",
                secondary_generators=["theme", "experiment"],
                backend_integrations=["npc", "monster", "equipment"],
                performance_timeout=60,  # REQ-CAM-217
                requires_llm=True,
                supports_refinement=True
            ),
            
            # Campaign skeleton generation (REQ-CAM-023-037)
            CampaignCreationOptions.CAMPAIGN_SKELETON: CampaignCreationConfig(
                primary_generator="skeleton",
                secondary_generators=["campaign"],
                backend_integrations=[],
                performance_timeout=30,  # REQ-CAM-216
                requires_llm=True,
                supports_refinement=True
            ),
            
            # Chapter content generation (REQ-CAM-033-037)
            CampaignCreationOptions.CHAPTER_CONTENT: CampaignCreationConfig(
                primary_generator="chapter",
                secondary_generators=["theme"],
                backend_integrations=["npc", "monster", "equipment"],
                performance_timeout=60,  # REQ-CAM-217
                requires_llm=True,
                supports_refinement=True
            ),
            
            # Refinement and evolution (REQ-CAM-007-012)
            CampaignCreationOptions.ITERATIVE_REFINEMENT: CampaignCreationConfig(
                primary_generator="adaptive",
                secondary_generators=["campaign", "skeleton", "chapter"],
                backend_integrations=[],
                performance_timeout=45,  # REQ-CAM-220
                requires_llm=True,
                supports_refinement=False  # This IS refinement
            ),
            
            # Adaptive content (REQ-CAM-055-063)
            CampaignCreationOptions.ADAPTIVE_CONTENT: CampaignCreationConfig(
                primary_generator="adaptive",
                secondary_generators=["campaign"],
                backend_integrations=["npc", "monster"],
                performance_timeout=45,
                requires_llm=True,
                supports_refinement=True
            ),
            
            # Psychological experiments (REQ-CAM-118-132)
            CampaignCreationOptions.PSYCHOLOGICAL_EXPERIMENT: CampaignCreationConfig(
                primary_generator="experiment",
                secondary_generators=[],
                backend_integrations=[],
                performance_timeout=30,
                requires_llm=True,
                supports_refinement=True
            ),
            
            # Setting themes (REQ-CAM-133-147)
            CampaignCreationOptions.SETTING_THEME: CampaignCreationConfig(
                primary_generator="theme",
                secondary_generators=[],
                backend_integrations=[],
                performance_timeout=30,
                requires_llm=True,
                supports_refinement=True
            ),
            
            # Backend integration content (REQ-CAM-064-078)
            CampaignCreationOptions.NPC_FOR_CAMPAIGN: CampaignCreationConfig(
                primary_generator="backend_npc",
                secondary_generators=["theme"],
                backend_integrations=["npc"],
                performance_timeout=30,  # REQ-CAM-218
                requires_llm=False,  # Backend handles this
                supports_refinement=False
            ),
            
            CampaignCreationOptions.MONSTER_FOR_CAMPAIGN: CampaignCreationConfig(
                primary_generator="backend_monster",
                secondary_generators=["theme"],
                backend_integrations=["monster"],
                performance_timeout=30,  # REQ-CAM-218
                requires_llm=False,  # Backend handles this
                supports_refinement=False
            ),
            
            CampaignCreationOptions.EQUIPMENT_FOR_CAMPAIGN: CampaignCreationConfig(
                primary_generator="backend_equipment",
                secondary_generators=["theme"],
                backend_integrations=["weapon", "armor", "spell", "other_item"],
                performance_timeout=30,  # REQ-CAM-218
                requires_llm=False,  # Backend handles this
                supports_refinement=False
            )
        }
    
    def get_config(self, creation_type: CampaignCreationOptions) -> CampaignCreationConfig:
        """Get configuration for a specific creation type."""
        config = self._configs.get(creation_type)
        if not config:
            raise ValueError(f"Unsupported creation type: {creation_type}")
        return config
    
    async def create_from_scratch(self, creation_type: CampaignCreationOptions, 
                                concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create new campaign content from scratch using LLM generation.
        
        Implements REQ-CAM-001-018: AI-Driven Campaign Generation from Scratch
        
        Args:
            creation_type: Type of content to create
            concept: User-provided concept (50-500 words, REQ-CAM-002)
            **kwargs: Additional parameters specific to creation type
            
        Returns:
            Dict containing the generated content and metadata
        """
        start_time = datetime.utcnow()
        
        # Validate concept length (REQ-CAM-002)
        concept_words = len(concept.split())
        if not (50 <= concept_words <= 500):
            logger.warning(f"Concept length {concept_words} words outside recommended range (50-500)")
        
        config = self.get_config(creation_type)
        
        # Validate LLM requirement
        if config.requires_llm and not self.llm_service:
            raise RuntimeError(f"LLM service required for {creation_type.value} but not available")
        
        try:
            logger.info(f"Creating {creation_type.value} from concept: {concept[:50]}...")
            
            # Route to appropriate creation method
            if creation_type == CampaignCreationOptions.CAMPAIGN_FROM_SCRATCH:
                result = await self._create_campaign_from_scratch(concept, **kwargs)
            elif creation_type == CampaignCreationOptions.CAMPAIGN_SKELETON:
                result = await self._create_campaign_skeleton(concept, **kwargs)
            elif creation_type == CampaignCreationOptions.CHAPTER_CONTENT:
                result = await self._create_chapter_content(concept, **kwargs)
            elif creation_type == CampaignCreationOptions.PSYCHOLOGICAL_EXPERIMENT:
                result = await self._create_psychological_experiment(concept, **kwargs)
            elif creation_type == CampaignCreationOptions.SETTING_THEME:
                result = await self._create_setting_theme(concept, **kwargs)
            elif creation_type in [
                CampaignCreationOptions.NPC_FOR_CAMPAIGN,
                CampaignCreationOptions.MONSTER_FOR_CAMPAIGN,
                CampaignCreationOptions.EQUIPMENT_FOR_CAMPAIGN
            ]:
                result = await self._create_backend_content(creation_type, concept, **kwargs)
            else:
                raise ValueError(f"Creation from scratch not supported for: {creation_type}")
            
            # Track performance (REQ-CAM-216-220)
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_performance_stats(generation_time)
            
            if generation_time > config.performance_timeout:
                logger.warning(f"Generation exceeded timeout: {generation_time}s > {config.performance_timeout}s")
            
            result["performance"] = {
                "generation_time": generation_time,
                "within_timeout": generation_time <= config.performance_timeout,
                "timeout_limit": config.performance_timeout
            }
            
            logger.info(f"Successfully created {creation_type.value} in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            self.generation_stats["failed_generations"] += 1
            logger.error(f"Failed to create {creation_type.value}: {str(e)}")
            raise
    
    async def evolve_existing(self, creation_type: CampaignCreationOptions, 
                            existing_data: Dict[str, Any], refinement_prompt: str,
                            **kwargs) -> Dict[str, Any]:
        """
        Evolve existing campaign content using refinement prompts and player feedback.
        
        Implements REQ-CAM-007-012: Iterative Campaign Refinement System
        
        Args:
            creation_type: Type of content to evolve
            existing_data: Current campaign content data
            refinement_prompt: Guidance for evolution
            **kwargs: Additional parameters
            
        Returns:
            Dict containing the evolved content and metadata
        """
        start_time = datetime.utcnow()
        
        config = self.get_config(creation_type)
        
        # Validate refinement support
        if not config.supports_refinement:
            raise ValueError(f"Refinement not supported for: {creation_type}")
        
        # Validate LLM requirement
        if config.requires_llm and not self.llm_service:
            raise RuntimeError(f"LLM service required for {creation_type.value} refinement but not available")
        
        try:
            logger.info(f"Evolving {creation_type.value} with refinement: {refinement_prompt[:50]}...")
            
            # Route to appropriate evolution method
            if creation_type == CampaignCreationOptions.CAMPAIGN_FROM_SCRATCH:
                result = await self._evolve_campaign(existing_data, refinement_prompt, **kwargs)
            elif creation_type == CampaignCreationOptions.CAMPAIGN_SKELETON:
                result = await self._evolve_campaign_skeleton(existing_data, refinement_prompt, **kwargs)
            elif creation_type == CampaignCreationOptions.CHAPTER_CONTENT:
                result = await self._evolve_chapter(existing_data, refinement_prompt, **kwargs)
            elif creation_type == CampaignCreationOptions.ITERATIVE_REFINEMENT:
                result = await self._refine_campaign_iteratively(existing_data, refinement_prompt, **kwargs)
            elif creation_type == CampaignCreationOptions.ADAPTIVE_CONTENT:
                result = await self._adapt_to_player_feedback(existing_data, refinement_prompt, **kwargs)
            else:
                raise ValueError(f"Evolution not supported for: {creation_type}")
            
            # Track performance (REQ-CAM-220)
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_performance_stats(generation_time)
            
            result["performance"] = {
                "evolution_time": generation_time,
                "within_timeout": generation_time <= config.performance_timeout
            }
            
            logger.info(f"Successfully evolved {creation_type.value} in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            self.generation_stats["failed_generations"] += 1
            logger.error(f"Failed to evolve {creation_type.value}: {str(e)}")
            raise
            
    
    def _update_performance_stats(self, generation_time: float):
        """Update internal performance tracking statistics."""
        self.generation_stats["total_generations"] += 1
        self.generation_stats["last_generation_time"] = generation_time
        
        # Update rolling average
        current_avg = self.generation_stats["avg_generation_time"]
        total_gens = self.generation_stats["total_generations"]
        
        if total_gens == 1:
            self.generation_stats["avg_generation_time"] = generation_time
        else:
            self.generation_stats["avg_generation_time"] = (
                (current_avg * (total_gens - 1) + generation_time) / total_gens
            )

    async def get_factory_health_status(self) -> Dict[str, Any]:
        """Get health status of the campaign creation factory and all generators."""
        health_status = await self.generator_factory.health_check()
        
        health_status.update({
            "factory_type": "campaign_creation",
            "performance_stats": self.generation_stats,
            "llm_service_status": "connected" if self.llm_service else "disconnected",
            "supported_creation_types": [opt.value for opt in CampaignCreationOptions]
        })
        
        return health_status

    # ============================================================================
    # TASK 2: CAMPAIGN GENERATION FROM SCRATCH (TO BE IMPLEMENTED)
    # ============================================================================
    
    async def _create_campaign_from_scratch(self, concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create a complete campaign from scratch using LLM generation.
        Implements REQ-CAM-001-018: AI-Driven Campaign Generation Requirements
        """
        logger.info(f"Creating complete campaign from concept: {concept[:50]}...")
        
        # Extract parameters with defaults
        genre = kwargs.get('genre', CampaignGenre.FANTASY)
        complexity = kwargs.get('complexity', CampaignComplexity.MEDIUM)
        session_count = kwargs.get('session_count', 8)
        themes = kwargs.get('themes', [])
        setting_theme = kwargs.get('setting_theme', SettingTheme.STANDARD_FANTASY)
        party_level = kwargs.get('party_level', 1)
        party_size = kwargs.get('party_size', 4)
        use_character_service = kwargs.get('use_character_service', True)
        include_psychological_experiments = kwargs.get('include_psychological_experiments', False)
        experiment_types = kwargs.get('experiment_types', [])
        
        try:
            # Generate campaign title and description using LLM
            campaign_prompt = self._build_campaign_prompt(
                concept, genre, complexity, themes, setting_theme,
                include_psychological_experiments, experiment_types
            )
            
            # Request LLM to generate campaign structure
            llm_response = await self.llm_service.generate_completion(
                prompt=campaign_prompt,
                max_tokens=3000,
                temperature=0.8,
                system_prompt="You are an expert D&D Dungeon Master creating compelling campaigns."
            )
            
            # Parse LLM response into structured campaign data
            campaign_structure = self._parse_campaign_response(llm_response)
            
            # Generate chapters using the chapter generator
            chapters = await self._generate_campaign_chapters(
                campaign_structure, session_count, party_level, party_size,
                genre, setting_theme, use_character_service
            )
            
            # Build final campaign data
            campaign_data = {
                "id": f"campaign_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "title": campaign_structure.get("title", "Generated Campaign"),
                "description": campaign_structure.get("description", concept),
                "concept": concept,
                "genre": genre.value if hasattr(genre, 'value') else str(genre),
                "complexity": complexity.value if hasattr(complexity, 'value') else str(complexity),
                "setting_theme": setting_theme.value if hasattr(setting_theme, 'value') else str(setting_theme),
                "themes": themes,
                "session_count": session_count,
                "party_level": party_level,
                "party_size": party_size,
                "chapters": chapters,
                "plot_summary": campaign_structure.get("plot_summary", ""),
                "main_antagonist": campaign_structure.get("main_antagonist", {}),
                "key_npcs": campaign_structure.get("key_npcs", []),
                "major_locations": campaign_structure.get("major_locations", []),
                "campaign_hooks": campaign_structure.get("campaign_hooks", []),
                "psychological_experiments": experiment_types if include_psychological_experiments else [],
                "created_at": datetime.utcnow().isoformat(),
                "use_character_service": use_character_service
            }
            
            return {
                "success": True,
                "campaign": campaign_data,
                "generation_source": "llm_from_scratch",
                "chapters_generated": len(chapters)
            }
            
        except Exception as e:
            logger.error(f"Failed to create campaign from scratch: {str(e)}")
            return {
                "success": False,
                "error": f"Campaign creation failed: {str(e)}",
                "generation_source": "llm_from_scratch"
            }
    
    async def _create_campaign_skeleton(self, concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create a campaign skeleton with major plot points and chapter outlines.
        Implements REQ-CAM-023-037: Skeleton Plot and Campaign Generation
        """
        logger.info(f"Creating campaign skeleton from concept: {concept[:50]}...")
        
        # Extract parameters with defaults
        campaign_title = kwargs.get('campaign_title', 'Generated Campaign')
        campaign_description = kwargs.get('campaign_description', concept)
        themes = kwargs.get('themes', [])
        session_count = kwargs.get('session_count', 8)
        detail_level = kwargs.get('detail_level', 'medium')  # basic, medium, detailed
        genre = kwargs.get('genre', CampaignGenre.FANTASY)
        setting_theme = kwargs.get('setting_theme', SettingTheme.STANDARD_FANTASY)
        
        try:
            # Generate skeleton prompt
            skeleton_prompt = self._build_skeleton_prompt(
                concept, campaign_title, campaign_description, themes,
                session_count, detail_level, genre, setting_theme
            )
            
            # Request LLM to generate campaign skeleton
            llm_response = await self.llm_service.generate_completion(
                prompt=skeleton_prompt,
                max_tokens=2000,
                temperature=0.7,
                system_prompt="You are an expert D&D campaign designer creating structured campaign outlines."
            )
            
            # Parse skeleton response
            skeleton_structure = self._parse_skeleton_response(llm_response)
            
            # Generate chapter outlines (less detailed than full chapters)
            chapter_outlines = await self._generate_chapter_outlines(
                skeleton_structure, session_count, detail_level
            )
            
            # Build skeleton data
            skeleton_data = {
                "id": f"skeleton_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "title": campaign_title,
                "description": campaign_description,
                "concept": concept,
                "genre": genre.value if hasattr(genre, 'value') else str(genre),
                "setting_theme": setting_theme.value if hasattr(setting_theme, 'value') else str(setting_theme),
                "themes": themes,
                "session_count": session_count,
                "detail_level": detail_level,
                "plot_overview": skeleton_structure.get("plot_overview", ""),
                "act_structure": skeleton_structure.get("act_structure", []),
                "major_plot_points": skeleton_structure.get("major_plot_points", []),
                "chapter_outlines": chapter_outlines,
                "key_antagonists": skeleton_structure.get("key_antagonists", []),
                "important_npcs": skeleton_structure.get("important_npcs", []),
                "primary_locations": skeleton_structure.get("primary_locations", []),
                "campaign_themes": skeleton_structure.get("campaign_themes", themes),
                "plot_hooks": skeleton_structure.get("plot_hooks", []),
                "created_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "skeleton": skeleton_data,
                "generation_source": "llm_skeleton",
                "chapter_outlines_generated": len(chapter_outlines)
            }
            
        except Exception as e:
            logger.error(f"Failed to create campaign skeleton: {str(e)}")
            return {
                "success": False,
                "error": f"Skeleton creation failed: {str(e)}",
                "generation_source": "llm_skeleton"
            }
    
    async def _create_psychological_experiment(self, concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create psychological experiment integration for campaigns.
        Implements REQ-CAM-118-132: Psychological Experiment Integration
        """
        # TODO: Implement in TASK 6
        raise NotImplementedError("TASK 6: Psychological experiment integration - to be implemented")
    
    async def _create_setting_theme(self, concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create custom setting theme based on concept.
        Implements REQ-CAM-133-147: Universal Setting Theme System
        """
        # TODO: Implement in TASK 6
        raise NotImplementedError("TASK 6: Setting theme creation - to be implemented")
    
    async def _create_backend_content(self, creation_type: CampaignCreationOptions, 
                                    concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create campaign content using backend service integration.
        Implements REQ-CAM-064-078: Auto-Generation via Backend Integration
        """
        # TODO: Implement in TASK 5
        raise NotImplementedError("TASK 5: Backend service integration - to be implemented")
    
    # ============================================================================
    # TASK 4: ITERATIVE REFINEMENT SYSTEM (TO BE IMPLEMENTED)
    # ============================================================================
    
    async def _evolve_campaign(self, existing_data: Dict[str, Any], 
                             refinement_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Evolve existing campaign using refinement prompts and player feedback.
        Implements REQ-CAM-007-012: Iterative Campaign Refinement System
        """
        logger.info(f"Evolving campaign with refinement: {refinement_prompt[:50]}...")
        
        # Extract refinement parameters
        refinement_type = kwargs.get('refinement_type', 'general')
        preserve_elements = kwargs.get('preserve_elements', [])
        player_feedback = kwargs.get('player_feedback', '')
        refinement_cycles = kwargs.get('refinement_cycles', 1)
        
        try:
            # Build refinement context from existing data
            campaign_context = self._build_campaign_context(existing_data)
            
            # Create refinement prompt
            evolution_prompt = self._build_refinement_prompt(
                campaign_context, refinement_prompt, refinement_type,
                preserve_elements, player_feedback
            )
            
            # Perform iterative refinement cycles
            evolved_data = existing_data.copy()
            refinement_history = []
            
            for cycle in range(refinement_cycles):
                logger.info(f"Refinement cycle {cycle + 1}/{refinement_cycles}")
                
                # Generate refinement using LLM
                llm_response = await self.llm_service.generate_completion(
                    prompt=evolution_prompt,
                    max_tokens=2500,
                    temperature=0.6,
                    system_prompt="You are an expert D&D campaign designer refining campaigns based on feedback."
                )
                
                # Parse and apply refinements
                refinements = self._parse_refinement_response(llm_response)
                evolved_data = self._apply_refinements(evolved_data, refinements, preserve_elements)
                
                # Track refinement history
                refinement_history.append({
                    "cycle": cycle + 1,
                    "refinements_applied": len(refinements.get("changes", [])),
                    "preserved_elements": preserve_elements,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Update context for next cycle if multiple cycles
                if cycle < refinement_cycles - 1:
                    campaign_context = self._build_campaign_context(evolved_data)
                    evolution_prompt = self._build_refinement_prompt(
                        campaign_context, refinement_prompt, refinement_type,
                        preserve_elements, player_feedback
                    )
            
            # Update metadata
            evolved_data["last_refined"] = datetime.utcnow().isoformat()
            evolved_data["refinement_history"] = evolved_data.get("refinement_history", []) + refinement_history
            evolved_data["refinement_count"] = evolved_data.get("refinement_count", 0) + refinement_cycles
            
            return {
                "success": True,
                "campaign": evolved_data,
                "generation_source": "llm_refinement",
                "cycles_completed": refinement_cycles,
                "refinements_applied": sum(len(h.get("refinements_applied", [])) for h in refinement_history),
                "refinement_type": refinement_type
            }
            
        except Exception as e:
            logger.error(f"Failed to evolve campaign: {str(e)}")
            return {
                "success": False,
                "error": f"Campaign evolution failed: {str(e)}",
                "generation_source": "llm_refinement",
                "cycles_completed": 0
            }
    
    async def _evolve_campaign_skeleton(self, existing_data: Dict[str, Any],
                                      refinement_prompt: str, **kwargs) -> Dict[str, Any]:
        """Evolve campaign skeleton structure while maintaining story coherence."""
        # TODO: Implement in TASK 4
        raise NotImplementedError("TASK 4: Skeleton refinement - to be implemented")
    
    async def _evolve_chapter(self, existing_data: Dict[str, Any],
                            refinement_prompt: str, **kwargs) -> Dict[str, Any]:
        """Evolve individual chapter content based on feedback."""
        # TODO: Implement in TASK 4
        raise NotImplementedError("TASK 4: Chapter refinement - to be implemented")
    
    async def _refine_campaign_iteratively(self, existing_data: Dict[str, Any],
                                         refinement_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Perform iterative campaign refinement with multiple cycles.
        Implements REQ-CAM-008: Support multiple refinement cycles
        """
        # TODO: Implement in TASK 4
        raise NotImplementedError("TASK 4: Iterative refinement - to be implemented")
    
    async def _adapt_to_player_feedback(self, existing_data: Dict[str, Any],
                                      refinement_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Adapt campaign based on player feedback and behavior.
        Implements REQ-CAM-055-063: Adaptive Campaign System
        """
        # TODO: Implement in TASK 4
        raise NotImplementedError("TASK 4: Player feedback adaptation - to be implemented")


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def create_campaign_factory(llm_service: Optional[LLMService] = None, 
                           settings: Optional[Settings] = None) -> CampaignCreationFactory:
    """Create and return a campaign creation factory instance."""
    return CampaignCreationFactory(llm_service, settings)

async def create_campaign_quick(llm_service: LLMService, concept: str, **kwargs) -> Dict[str, Any]:
    """Quick campaign creation function for simple use cases."""
    factory = create_campaign_factory(llm_service)
    return await factory.create_from_scratch(
        CampaignCreationOptions.CAMPAIGN_FROM_SCRATCH, 
        concept, 
        **kwargs
    )
    
    # ============================================================================
    # TASK 2: CAMPAIGN GENERATION FROM SCRATCH
    # ============================================================================
    
    async def _create_campaign_from_scratch(self, concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create a complete campaign from scratch using LLM generation.
        
        Implements REQ-CAM-001-006: AI-Driven Campaign Generation Requirements
        """
        logger.info(f"Creating campaign from concept: {concept[:50]}...")
        
        # Extract parameters
        genre = kwargs.get('genre', CampaignGenre.FANTASY)
        complexity = kwargs.get('complexity', CampaignComplexity.MEDIUM)
        session_count = kwargs.get('session_count', 10)
        themes = kwargs.get('themes', [])
        setting_theme = kwargs.get('setting_theme')
        include_experiments = kwargs.get('include_psychological_experiments', False)
        
        # Validate session count per REQ-CAM-027
        if not (3 <= session_count <= 20):
            raise ValueError(f"Session count {session_count} outside supported range (3-20)")
        
        # Get campaign generator
        campaign_generator = self.generator_factory.get_generator("campaign")
        if not campaign_generator:
            raise RuntimeError("Campaign generator not available")
        
        # Generate base campaign
        campaign_data = await campaign_generator.generate_campaign_from_concept(
            concept=concept,
            genre=genre,
            complexity=complexity,
            session_count=session_count,
            themes=themes,
            setting_theme=setting_theme
        )
        
        # Apply setting theme if specified (REQ-CAM-133-147)
        if setting_theme and setting_theme != SettingTheme.STANDARD_FANTASY:
            campaign_data = await self._apply_setting_theme(campaign_data, setting_theme)
        
        # Add psychological experiments if requested (REQ-CAM-118-132)
        if include_experiments:
            campaign_data = await self._integrate_psychological_experiments(
                campaign_data, kwargs.get('experiment_types', [])
            )
        
        # Ensure narrative quality requirements (REQ-CAM-013-018)
        campaign_data = self._validate_narrative_quality(campaign_data)
        
        return {
            "campaign": campaign_data,
            "creation_type": "campaign_from_scratch",
            "success": True
        }
    
    async def _create_campaign_skeleton(self, concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create a campaign skeleton with major plot points and chapter outlines.
        
        Implements REQ-CAM-023-027: Skeleton Plot and Campaign Generation
        """
        logger.info(f"Creating campaign skeleton from concept: {concept[:50]}...")
        
        # Extract parameters
        campaign_title = kwargs.get('campaign_title', f"Campaign: {concept[:30]}")
        campaign_description = kwargs.get('campaign_description', concept)
        themes = kwargs.get('themes', [])
        session_count = kwargs.get('session_count', 10)
        detail_level = kwargs.get('detail_level', 'standard')
        
        # Get skeleton generator
        skeleton_generator = self.generator_factory.get_generator("skeleton")
        if not skeleton_generator:
            raise RuntimeError("Skeleton generator not available")
        
        # Generate campaign skeleton
        skeleton_data = await skeleton_generator.generate_campaign_skeleton(
            campaign_title=campaign_title,
            campaign_description=campaign_description,
            themes=themes,
            session_count=session_count,
            detail_level=detail_level
        )
        
        # Validate skeleton structure (REQ-CAM-024-026)
        skeleton_data = self._validate_skeleton_structure(skeleton_data, session_count)
        
        return {
            "skeleton": skeleton_data,
            "creation_type": "campaign_skeleton",
            "success": True
        }
    
    async def _create_chapter_content(self, concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create comprehensive chapter content including NPCs, encounters, locations.
        
        Implements REQ-CAM-033-037: Chapter Content Generation
        """
        logger.info(f"Creating chapter content from concept: {concept[:50]}...")
        
        # Extract parameters
        campaign_title = kwargs.get('campaign_title', 'Campaign')
        campaign_description = kwargs.get('campaign_description', '')
        chapter_title = kwargs.get('chapter_title', f"Chapter: {concept[:30]}")
        chapter_summary = kwargs.get('chapter_summary', concept)
        themes = kwargs.get('themes', [])
        chapter_theme = kwargs.get('chapter_theme')
        
        # Campaign context for character service integration
        campaign_context = {
            "genre": kwargs.get('genre', CampaignGenre.FANTASY),
            "theme": kwargs.get('setting_theme', SettingTheme.STANDARD_FANTASY),
            "complexity": kwargs.get('complexity', CampaignComplexity.MEDIUM),
            "party_level": kwargs.get('party_level', 1),
            "party_size": kwargs.get('party_size', 4),
            "title": campaign_title,
            "description": campaign_description
        }
        
        # Content inclusion flags
        include_npcs = kwargs.get('include_npcs', True)
        include_encounters = kwargs.get('include_encounters', True)
        include_locations = kwargs.get('include_locations', True)
        include_items = kwargs.get('include_items', True)
        use_character_service = kwargs.get('use_character_service', True)
        
        # Get chapter generator
        chapter_generator = self.generator_factory.get_generator("chapter")
        if not chapter_generator:
            raise RuntimeError("Chapter generator not available")
        
        # Generate chapter content with campaign context
        chapter_data = await chapter_generator.generate_chapter_content(
            campaign_title=campaign_title,
            campaign_description=campaign_description,
            chapter_title=chapter_title,
            chapter_summary=chapter_summary,
            themes=themes,
            include_npcs=include_npcs,
            include_encounters=include_encounters,
            include_locations=include_locations,
            include_items=include_items,
            chapter_theme=chapter_theme,
            campaign_context=campaign_context,
            use_character_service=use_character_service
        )
        
        # Legacy backend enhancement methods (keep for compatibility)
        if include_npcs and chapter_data.get('npcs') and not use_character_service:
            chapter_data['npcs'] = await self._enhance_npcs_via_backend(
                chapter_data['npcs'], campaign_title
            )
        
        if include_encounters and chapter_data.get('encounters'):
            chapter_data['encounters'] = await self._enhance_encounters_via_backend(
                chapter_data['encounters'], campaign_title
            )
        
        return {
            "chapter": chapter_data,
            "creation_type": "chapter_content",
            "success": True
        }
    
    async def _create_psychological_experiment(self, concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create psychological experiment integration for campaigns.
        
        Implements REQ-CAM-118-132: Psychological Experiment Integration
        """
        logger.info(f"Creating psychological experiment from concept: {concept[:50]}...")
        
        # Extract parameters
        experiment_type = kwargs.get('experiment_type', PsychologicalExperimentType.CUSTOM)
        campaign_context = kwargs.get('campaign_context', '')
        custom_concept = concept if experiment_type == PsychologicalExperimentType.CUSTOM else ""
        
        # Get experiment generator
        experiment_generator = self.generator_factory.get_generator("experiment")
        if not experiment_generator:
            raise RuntimeError("Psychological experiment generator not available")
        
        # Generate experiment integration
        experiment_data = await experiment_generator.generate_experiment_integration(
            experiment_type=experiment_type,
            campaign_context=campaign_context,
            custom_concept=custom_concept
        )
        
        # Add content warnings and ethical considerations (REQ-CAM-132)
        experiment_data = self._add_ethical_guidelines(experiment_data)
        
        return {
            "experiment": experiment_data,
            "creation_type": "psychological_experiment",
            "success": True
        }
    
    async def _create_setting_theme(self, concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create custom setting theme based on concept.
        
        Implements REQ-CAM-133-147: Universal Setting Theme System
        """
        logger.info(f"Creating setting theme from concept: {concept[:50]}...")
        
        # Extract parameters
        base_genre = kwargs.get('base_genre', CampaignGenre.FANTASY)
        enhance_existing = kwargs.get('enhance_existing_theme')
        
        # Get theme generator
        theme_generator = self.generator_factory.get_generator("theme")
        if not theme_generator:
            raise RuntimeError("Setting theme generator not available")
        
        if enhance_existing:
            # Enhance existing theme
            theme_data = await theme_generator.enhance_existing_theme(
                base_theme=enhance_existing,
                enhancement_concept=concept
            )
        else:
            # Create custom theme
            theme_data = await theme_generator.generate_custom_theme(
                theme_concept=concept,
                genre=base_genre
            )
        
        return {
            "theme": theme_data,
            "creation_type": "setting_theme",
            "success": True
        }
    
    # ============================================================================
    # HELPER METHODS FOR CAMPAIGN CREATION
    # ============================================================================
    
    def _validate_narrative_quality(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate campaign meets narrative quality requirements (REQ-CAM-013-018).
        """
        required_elements = [
            "title", "description", "themes", "plot_hooks", 
            "antagonists", "moral_dilemmas"
        ]
        
        for element in required_elements:
            if element not in campaign_data:
                logger.warning(f"Campaign missing required narrative element: {element}")
                campaign_data[element] = f"[Missing {element} - needs development]"
        
        # Ensure complex storylines (REQ-CAM-003)
        if isinstance(campaign_data.get('description'), str):
            desc_length = len(campaign_data['description'].split())
            if desc_length < 50:
                logger.warning(f"Campaign description may be too brief ({desc_length} words)")
        
        # Ensure moral complexity (REQ-CAM-005)
        if not campaign_data.get('moral_dilemmas'):
            campaign_data['moral_dilemmas'] = [
                "Heroes must choose between saving allies and protecting innocent civilians",
                "A reformed enemy offers crucial aid but cannot be fully trusted"
            ]
        
        return campaign_data
    
    def _validate_skeleton_structure(self, skeleton_data: Dict[str, Any], 
                                   session_count: int) -> Dict[str, Any]:
        """
        Validate skeleton structure meets requirements (REQ-CAM-024-026).
        """
        # Ensure main story arc phases (REQ-CAM-024)
        required_phases = ["beginning", "middle", "end"]
        if "story_phases" in skeleton_data:
            for phase in required_phases:
                if phase not in skeleton_data["story_phases"]:
                    logger.warning(f"Skeleton missing story phase: {phase}")
        
        # Ensure 3-5 major plot points (REQ-CAM-025)
        plot_points = skeleton_data.get("major_plot_points", [])
        if len(plot_points) < 3 or len(plot_points) > 8:
            logger.warning(f"Plot points count ({len(plot_points)}) outside recommended range (3-8)")
        
        # Ensure chapter count matches session count
        chapters = skeleton_data.get("chapter_outlines", [])
        if len(chapters) != session_count:
            logger.warning(f"Chapter count ({len(chapters)}) doesn't match session count ({session_count})")
        
        return skeleton_data
    
    def _add_ethical_guidelines(self, experiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add ethical guidelines and content warnings for psychological experiments.
        
        Implements REQ-CAM-132: Content warnings and opt-out mechanisms
        """
        experiment_data["ethical_guidelines"] = {
            "content_warning": "This chapter includes psychological experiment elements that may involve moral dilemmas and social pressure scenarios.",
            "opt_out_available": True,
            "facilitation_notes": "DM should ensure all players are comfortable with psychological content and provide alternatives if requested.",
            "educational_context": "This experiment is designed to provide insights into human behavior and decision-making in a safe, fictional context.",
            "discussion_recommended": "Consider post-session discussion about choices and real-world applications."
        }
        
        return experiment_data
    
    def _update_performance_stats(self, generation_time: float):
        """Update internal performance tracking statistics."""
        self.generation_stats["total_generations"] += 1
        self.generation_stats["last_generation_time"] = generation_time
        
        # Update rolling average
        current_avg = self.generation_stats["avg_generation_time"]
        total_gens = self.generation_stats["total_generations"]
        
        if total_gens == 1:
            self.generation_stats["avg_generation_time"] = generation_time
        else:
            self.generation_stats["avg_generation_time"] = (
                (current_avg * (total_gens - 1) + generation_time) / total_gens
            )
    
    async def get_factory_health_status(self) -> Dict[str, Any]:
        """Get health status of the campaign creation factory and all generators."""
        health_status = await self.generator_factory.health_check()
        
        health_status.update({
            "factory_type": "campaign_creation",
            "performance_stats": self.generation_stats,
            "llm_service_status": "connected" if self.llm_service else "disconnected",
            "backend_integration_status": "available",  # TODO: Add actual backend health check
            "supported_creation_types": [opt.value for opt in CampaignCreationOptions]
        })
        
        return health_status
    
    # ============================================================================
    # TASK 3: CAMPAIGN REFINEMENT AND EVOLUTION
    # ============================================================================
    
    async def _evolve_campaign(self, existing_data: Dict[str, Any], 
                             refinement_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Evolve existing campaign using refinement prompts and player feedback.
        
        Implements REQ-CAM-007-012: Iterative Campaign Refinement System
        """
        logger.info(f"Evolving campaign with refinement: {refinement_prompt[:50]}...")
        
        # Preserve original data (REQ-CAM-009: maintain narrative consistency)
        original_data = existing_data.copy()
        
        # Extract refinement parameters
        refinement_type = kwargs.get('refinement_type', 'enhance')  # enhance, modify, expand
        preserve_elements = kwargs.get('preserve_elements', ['title', 'core_concept', 'main_characters'])
        player_feedback = kwargs.get('player_feedback', [])
        
        # Get adaptive generator for evolution
        adaptive_generator = self.generator_factory.get_generator("adaptive")
        if not adaptive_generator:
            raise RuntimeError("Adaptive generator not available")
        
        if refinement_type == 'enhance':
            # Enhance specific aspects (REQ-CAM-012)
            enhanced_data = await self._enhance_campaign_aspects(
                existing_data, refinement_prompt, preserve_elements
            )
        elif refinement_type == 'modify':
            # Modify specific plot elements (REQ-CAM-011)
            enhanced_data = await self._modify_campaign_elements(
                existing_data, refinement_prompt, preserve_elements
            )
        elif refinement_type == 'player_driven':
            # Adapt based on player feedback (REQ-CAM-055-063)
            enhanced_data = await self._adapt_to_player_feedback(
                existing_data, player_feedback, refinement_prompt
            )
        else:
            raise ValueError(f"Unknown refinement type: {refinement_type}")
        
        # Maintain version history (REQ-CAM-010)
        enhanced_data = self._track_refinement_version(original_data, enhanced_data, refinement_prompt)
        
        return {
            "campaign": enhanced_data,
            "evolution_type": "campaign_refinement",
            "success": True
        }
    
    async def _evolve_campaign_skeleton(self, existing_data: Dict[str, Any],
                                      refinement_prompt: str, **kwargs) -> Dict[str, Any]:
        """Evolve campaign skeleton structure while maintaining story coherence."""
        logger.info(f"Evolving campaign skeleton: {refinement_prompt[:50]}...")
        
        # Get skeleton generator
        skeleton_generator = self.generator_factory.get_generator("skeleton")
        if not skeleton_generator:
            raise RuntimeError("Skeleton generator not available")
        
        # Extract current skeleton structure
        current_title = existing_data.get('title', 'Campaign')
        current_description = existing_data.get('description', '')
        current_themes = existing_data.get('themes', [])
        session_count = len(existing_data.get('chapter_outlines', []))
        
        # Regenerate skeleton with refinement context
        enhanced_skeleton = await skeleton_generator.generate_campaign_skeleton(
            campaign_title=current_title,
            campaign_description=f"{current_description}\n\nRefinement: {refinement_prompt}",
            themes=current_themes,
            session_count=session_count,
            detail_level='detailed'
        )
        
        # Merge with existing data to preserve continuity
        enhanced_data = self._merge_skeleton_refinements(existing_data, enhanced_skeleton)
        
        return {
            "skeleton": enhanced_data,
            "evolution_type": "skeleton_refinement",
            "success": True
        }
    
    async def _evolve_chapter(self, existing_data: Dict[str, Any],
                            refinement_prompt: str, **kwargs) -> Dict[str, Any]:
        """Evolve individual chapter content based on feedback."""
        logger.info(f"Evolving chapter: {refinement_prompt[:50]}...")
        
        # Get chapter generator
        chapter_generator = self.generator_factory.get_generator("chapter")
        if not chapter_generator:
            raise RuntimeError("Chapter generator not available")
        
        # Extract chapter parameters
        campaign_title = existing_data.get('campaign_title', 'Campaign')
        chapter_title = existing_data.get('title', 'Chapter')
        current_summary = existing_data.get('summary', '')
        themes = existing_data.get('themes', [])
        
        # Create enhanced chapter summary
        enhanced_summary = f"{current_summary}\n\nEvolution guidance: {refinement_prompt}"
        
        # Generate evolved chapter content
        evolved_chapter = await chapter_generator.generate_chapter_content(
            campaign_title=campaign_title,
            campaign_description="",
            chapter_title=chapter_title,
            chapter_summary=enhanced_summary,
            themes=themes,
            include_npcs=True,
            include_encounters=True,
            include_locations=True,
            include_items=True
        )
        
        # Merge evolved content with existing data
        enhanced_data = self._merge_chapter_evolution(existing_data, evolved_chapter)
        
        return {
            "chapter": enhanced_data,
            "evolution_type": "chapter_refinement",
            "success": True
        }
    
    async def _refine_campaign_iteratively(self, existing_data: Dict[str, Any],
                                         refinement_prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Perform iterative campaign refinement with multiple cycles.
        
        Implements REQ-CAM-008: Support multiple refinement cycles
        """
        logger.info(f"Starting iterative refinement: {refinement_prompt[:50]}...")
        
        refinement_cycles = kwargs.get('refinement_cycles', 1)
        current_data = existing_data.copy()
        refinement_log = []
        
        for cycle in range(refinement_cycles):
            logger.info(f"Refinement cycle {cycle + 1}/{refinement_cycles}")
            
            # Apply refinement
            cycle_result = await self._evolve_campaign(
                current_data, 
                refinement_prompt, 
                refinement_type='enhance'
            )
            
            current_data = cycle_result['campaign']
            refinement_log.append({
                "cycle": cycle + 1,
                "prompt": refinement_prompt,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Allow for different prompts in subsequent cycles
            if cycle < refinement_cycles - 1:
                next_prompt = kwargs.get(f'cycle_{cycle + 2}_prompt')
                if next_prompt:
                    refinement_prompt = next_prompt
        
        current_data['iterative_refinement_log'] = refinement_log
        
        return {
            "campaign": current_data,
            "evolution_type": "iterative_refinement",
            "cycles_completed": refinement_cycles,
            "success": True
        }
    
    # ============================================================================
    # REFINEMENT HELPER METHODS
    # ============================================================================
    
    async def _enhance_campaign_aspects(self, existing_data: Dict[str, Any],
                                      refinement_prompt: str, 
                                      preserve_elements: List[str]) -> Dict[str, Any]:
        """Enhance specific campaign aspects while preserving core elements."""
        
        # Create enhancement context
        enhancement_context = f"""
        Enhance this campaign based on the following guidance: {refinement_prompt}
        
        Preserve these elements unchanged: {', '.join(preserve_elements)}
        
        Current campaign data: {json.dumps(existing_data, indent=2)}
        """
        
        # Get campaign generator for enhancement
        campaign_generator = self.generator_factory.get_generator("campaign")
        
        # Use adaptive generator to enhance content
        adaptive_generator = self.generator_factory.get_generator("adaptive")
        if adaptive_generator:
            enhancement_result = await adaptive_generator.generate_adaptive_content(
                content=json.dumps(existing_data),
                player_analysis={"behavior_summary": refinement_prompt}
            )
            
            if enhancement_result and enhancement_result.get('adapted_content'):
                try:
                    enhanced_data = json.loads(enhancement_result['adapted_content'])
                    # Ensure preserved elements remain unchanged
                    for element in preserve_elements:
                        if element in existing_data:
                            enhanced_data[element] = existing_data[element]
                    
                    return enhanced_data
                except json.JSONDecodeError:
                    logger.warning("Could not parse enhanced content as JSON, using original")
        
        # Fallback: manual enhancement
        enhanced_data = existing_data.copy()
        enhanced_data['enhancement_notes'] = refinement_prompt
        enhanced_data['last_enhanced'] = datetime.utcnow().isoformat()
        
        return enhanced_data
    
    async def _modify_campaign_elements(self, existing_data: Dict[str, Any],
                                      refinement_prompt: str,
                                      preserve_elements: List[str]) -> Dict[str, Any]:
        """Modify specific campaign elements while maintaining narrative consistency."""
        
        modified_data = existing_data.copy()
        
        # Identify modification targets from prompt
        modification_targets = self._identify_modification_targets(refinement_prompt)
        
        for target in modification_targets:
            if target not in preserve_elements and target in existing_data:
                # Apply targeted modification
                modified_data[target] = await self._apply_targeted_modification(
                    existing_data[target], refinement_prompt, target
                )
        
        # Track modifications
        if 'modification_history' not in modified_data:
            modified_data['modification_history'] = []
        
        modified_data['modification_history'].append({
            "prompt": refinement_prompt,
            "targets": modification_targets,
            "modified_at": datetime.utcnow().isoformat()
        })
        
        return modified_data
    
    async def _adapt_to_player_feedback(self, existing_data: Dict[str, Any],
                                      player_feedback: List[str],
                                      refinement_prompt: str) -> Dict[str, Any]:
        """
        Adapt campaign based on player feedback and behavior.
        
        Implements REQ-CAM-055-063: Adaptive Campaign System
        """
        
        # Get adaptive generator
        adaptive_generator = self.generator_factory.get_generator("adaptive")
        if not adaptive_generator:
            return existing_data
        
        # Analyze player feedback
        session_data = [{"feedback": feedback} for feedback in player_feedback]
        player_analysis = await adaptive_generator.analyze_player_behavior(session_data)
        
        # Generate campaign adjustments
        adjustment_suggestions = await adaptive_generator.suggest_campaign_adjustments(
            existing_data, player_feedback
        )
        
        # Apply adaptations
        adapted_data = existing_data.copy()
        adapted_data['player_adaptations'] = {
            "feedback_analyzed": player_feedback,
            "analysis_results": player_analysis,
            "suggested_adjustments": adjustment_suggestions,
            "adapted_at": datetime.utcnow().isoformat()
        }
        
        # Apply specific adaptations based on feedback patterns
        adapted_data = await self._apply_feedback_adaptations(adapted_data, player_analysis)
        
        return adapted_data
    
    def _track_refinement_version(self, original_data: Dict[str, Any],
                                enhanced_data: Dict[str, Any],
                                refinement_prompt: str) -> Dict[str, Any]:
        """
        Track refinement versions for rollback capability.
        
        Implements REQ-CAM-010: Track refinement history and allow reverting
        """
        
        if 'version_history' not in enhanced_data:
            enhanced_data['version_history'] = []
        
        # Create version snapshot
        version_entry = {
            "version_number": len(enhanced_data['version_history']) + 1,
            "refinement_prompt": refinement_prompt,
            "refined_at": datetime.utcnow().isoformat(),
            "previous_version_hash": hash(str(original_data)),
            "changes_summary": "Automated refinement applied"
        }
        
        enhanced_data['version_history'].append(version_entry)
        enhanced_data['current_version'] = version_entry['version_number']
        
        return enhanced_data
    
    def _merge_skeleton_refinements(self, existing_data: Dict[str, Any],
                                  enhanced_skeleton: Dict[str, Any]) -> Dict[str, Any]:
        """Merge skeleton refinements while preserving existing structure."""
        
        merged_data = existing_data.copy()
        
        # Merge major plot points
        if 'major_plot_points' in enhanced_skeleton:
            merged_data['major_plot_points'] = enhanced_skeleton['major_plot_points']
        
        # Merge story phases
        if 'story_phases' in enhanced_skeleton:
            merged_data['story_phases'] = enhanced_skeleton['story_phases']
        
        # Update chapter outlines while preserving existing content
        if 'chapter_outlines' in enhanced_skeleton:
            existing_chapters = merged_data.get('chapter_outlines', [])
            new_chapters = enhanced_skeleton['chapter_outlines']
            
            # Merge chapter data
            merged_chapters = []
            for i, new_chapter in enumerate(new_chapters):
                if i < len(existing_chapters):
                    # Merge with existing chapter
                    merged_chapter = existing_chapters[i].copy()
                    merged_chapter.update(new_chapter)
                    merged_chapters.append(merged_chapter)
                else:
                    # Add new chapter
                    merged_chapters.append(new_chapter)
            
            merged_data['chapter_outlines'] = merged_chapters
        
        return merged_data
    
    def _merge_chapter_evolution(self, existing_data: Dict[str, Any],
                               evolved_chapter: Dict[str, Any]) -> Dict[str, Any]:
        """Merge evolved chapter content with existing chapter data."""
        
        merged_data = existing_data.copy()
        
        # Update narrative content
        if 'narrative' in evolved_chapter:
            merged_data['narrative'] = evolved_chapter['narrative']
        
        # Merge NPCs (add new, preserve existing)
        if 'npcs' in evolved_chapter:
            existing_npcs = merged_data.get('npcs', [])
            new_npcs = evolved_chapter['npcs']
            
            # Combine NPC lists (could implement more sophisticated merging)
            merged_data['npcs'] = existing_npcs + new_npcs.get('content', [])
        
        # Similar merging for other content types
        for content_type in ['encounters', 'locations', 'items', 'hooks']:
            if content_type in evolved_chapter:
                existing_content = merged_data.get(content_type, [])
                new_content = evolved_chapter[content_type]
                
                if isinstance(new_content, dict) and 'content' in new_content:
                    new_content = new_content['content']
                
                merged_data[content_type] = existing_content + (new_content if isinstance(new_content, list) else [])
        
        return merged_data
    
    def _identify_modification_targets(self, refinement_prompt: str) -> List[str]:
        """Identify which campaign elements should be modified based on refinement prompt."""
        
        targets = []
        prompt_lower = refinement_prompt.lower()
        
        # Map keywords to campaign elements
        target_mapping = {
            'plot': ['main_storyline', 'major_plot_points', 'subplots'],
            'character': ['antagonists', 'npcs'],
            'theme': ['themes', 'moral_dilemmas'],
            'encounter': ['encounters', 'conflicts'],
            'setting': ['locations', 'world_stakes'],
            'pacing': ['story_phases', 'chapter_outlines']
        }
        
        for keyword, elements in target_mapping.items():
            if keyword in prompt_lower:
                targets.extend(elements)
        
        return list(set(targets))  # Remove duplicates
    
    async def _apply_targeted_modification(self, current_value: Any,
                                         refinement_prompt: str,
                                         target_element: str) -> Any:
        """Apply targeted modification to a specific campaign element."""
        
        # For now, add modification notes - could be enhanced with LLM generation
        if isinstance(current_value, dict):
            modified_value = current_value.copy()
            modified_value['modification_note'] = f"Modified based on: {refinement_prompt}"
            return modified_value
        elif isinstance(current_value, list):
            return current_value + [f"[Modified: {refinement_prompt}]"]
        elif isinstance(current_value, str):
            return f"{current_value}\n\n[Modification note: {refinement_prompt}]"
        else:
            return current_value
    
    async def _apply_feedback_adaptations(self, campaign_data: Dict[str, Any],
                                        player_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply specific adaptations based on player behavior analysis."""
        
        adapted_data = campaign_data.copy()
        
        # Extract behavior patterns from analysis
        behavior_summary = player_analysis.get('behavior_summary', '')
        
        # Apply common adaptations based on patterns
        if 'social' in behavior_summary.lower():
            adapted_data['adaptation_notes'] = adapted_data.get('adaptation_notes', [])
            adapted_data['adaptation_notes'].append("Increased social encounter opportunities")
        
        if 'combat' in behavior_summary.lower():
            adapted_data['adaptation_notes'] = adapted_data.get('adaptation_notes', [])
            adapted_data['adaptation_notes'].append("Enhanced tactical combat scenarios")
        
        if 'exploration' in behavior_summary.lower():
            adapted_data['adaptation_notes'] = adapted_data.get('adaptation_notes', [])
            adapted_data['adaptation_notes'].append("Added exploration and discovery elements")
        
        return adapted_data
    
    # ============================================================================
    # TASK 4: BACKEND SERVICE INTEGRATION
    # ============================================================================
    
    async def _create_campaign_content_via_backend(self, creation_type: CampaignCreationOptions,
                                                 concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create campaign content using backend service integration.
        
        Implements REQ-CAM-064-078: Auto-Generation via Backend Integration
        """
        logger.info(f"Creating {creation_type.value} via backend integration: {concept[:50]}...")
        
        if creation_type == CampaignCreationOptions.NPC_FOR_CAMPAIGN:
            return await self._create_npc_via_backend(concept, **kwargs)
        elif creation_type == CampaignCreationOptions.MONSTER_FOR_CAMPAIGN:
            return await self._create_monster_via_backend(concept, **kwargs)
        else:
            raise ValueError(f"Backend integration not supported for: {creation_type}")
    
    async def _create_npc_via_backend(self, concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create NPC using backend /api/v2/factory/create endpoint.
        
        Implements REQ-CAM-064-068: NPC Generation for Chapters
        """
        
        # Extract NPC parameters
        npc_type = kwargs.get('npc_type', 'commoner')
        campaign_context = kwargs.get('campaign_context', '')
        complexity = kwargs.get('complexity', 'medium')
        setting_theme = kwargs.get('setting_theme')
        
        # Prepare backend request parameters
        backend_params = {
            "creation_type": "npc",
            "prompt": concept,
            "user_preferences": {
                "npc_type": npc_type,
                "complexity": complexity,
                "campaign_context": campaign_context
            }
        }
        
        # Apply setting theme if specified (REQ-CAM-138)
        if setting_theme:
            backend_params["user_preferences"]["setting_theme"] = setting_theme.value
            backend_params["prompt"] = self._apply_theme_to_prompt(concept, setting_theme)
        
        try:
            # TODO: Replace with actual backend API call
            # For now, create a mock NPC structure
            npc_data = await self._mock_backend_npc_creation(backend_params)
            
            return {
                "npc": npc_data,
                "creation_type": "npc_via_backend",
                "backend_integration": True,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Backend NPC creation failed: {e}")
            # Fallback to local generation
            return await self._fallback_npc_creation(concept, **kwargs)
    
    async def _create_monster_via_backend(self, concept: str, **kwargs) -> Dict[str, Any]:
        """
        Create monster using backend /api/v2/factory/create endpoint.
        
        Implements REQ-CAM-069-073: Monster and Encounter Generation
        """
        
        # Extract monster parameters
        challenge_rating = kwargs.get('challenge_rating', 1.0)
        creature_type = kwargs.get('creature_type', 'monstrosity')
        campaign_context = kwargs.get('campaign_context', '')
        setting_theme = kwargs.get('setting_theme')
        encounter_type = kwargs.get('encounter_type', 'combat')
        
        # Prepare backend request parameters
        backend_params = {
            "creation_type": "monster",
            "prompt": concept,
            "user_preferences": {
                "challenge_rating": challenge_rating,
                "creature_type": creature_type,
                "campaign_context": campaign_context,
                "encounter_type": encounter_type
            }
        }
        
        # Apply setting theme if specified (REQ-CAM-139)
        if setting_theme:
            backend_params["user_preferences"]["setting_theme"] = setting_theme.value
            backend_params["prompt"] = self._apply_theme_to_prompt(concept, setting_theme)
        
        try:
            # TODO: Replace with actual backend API call
            # For now, create a mock monster structure
            monster_data = await self._mock_backend_monster_creation(backend_params)
            
            # Generate encounter context if requested (REQ-CAM-071)
            if encounter_type and encounter_type != 'combat':
                encounter_context = await self._generate_encounter_context(
                    monster_data, encounter_type, campaign_context
                )
                monster_data['encounter_context'] = encounter_context
            
            return {
                "monster": monster_data,
                "creation_type": "monster_via_backend",
                "backend_integration": True,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Backend monster creation failed: {e}")
            # Fallback to local generation
            return await self._fallback_monster_creation(concept, **kwargs)
    
    async def _enhance_npcs_via_backend(self, npcs_data: Dict[str, Any], 
                                      campaign_title: str) -> Dict[str, Any]:
        """
        Enhance generated NPCs with detailed stats using backend services.
        
        Implements REQ-CAM-065: NPC diversity and complexity
        """
        
        enhanced_npcs = npcs_data.copy()
        
        if isinstance(npcs_data.get('content'), list):
            enhanced_content = []
            
            for npc in npcs_data['content']:
                if isinstance(npc, dict):
                    # Add detailed stats via backend
                    enhanced_npc = await self._add_npc_stats_via_backend(npc, campaign_title)
                    enhanced_content.append(enhanced_npc)
                else:
                    enhanced_content.append(npc)
            
            enhanced_npcs['content'] = enhanced_content
            enhanced_npcs['backend_enhanced'] = True
        
        return enhanced_npcs
    
    async def _enhance_encounters_via_backend(self, encounters_data: Dict[str, Any],
                                            campaign_title: str) -> Dict[str, Any]:
        """
        Enhance generated encounters with balanced stats using backend services.
        
        Implements REQ-CAM-070: Balanced encounter creation
        """
        
        enhanced_encounters = encounters_data.copy()
        
        if isinstance(encounters_data.get('content'), list):
            enhanced_content = []
            
            for encounter in encounters_data['content']:
                if isinstance(encounter, dict):
                    # Add encounter balance and tactical elements
                    enhanced_encounter = await self._balance_encounter_via_backend(
                        encounter, campaign_title
                    )
                    enhanced_content.append(enhanced_encounter)
                else:
                    enhanced_content.append(encounter)
            
            enhanced_encounters['content'] = enhanced_content
            enhanced_encounters['backend_enhanced'] = True
        
        return enhanced_encounters
    
    async def _apply_setting_theme(self, campaign_data: Dict[str, Any], 
                                 setting_theme: SettingTheme) -> Dict[str, Any]:
        """
        Apply setting theme to all campaign elements.
        
        Implements REQ-CAM-133-147: Universal Setting Theme System
        """
        logger.info(f"Applying setting theme: {setting_theme.value}")
        
        themed_data = campaign_data.copy()
        
        # Get theme generator
        theme_generator = self.generator_factory.get_generator("theme")
        if not theme_generator:
            logger.warning("Theme generator not available, skipping theme application")
            return campaign_data
        
        # Apply theme to campaign title and description
        if 'title' in themed_data:
            themed_data['title'] = self._apply_theme_to_text(
                themed_data['title'], setting_theme
            )
        
        if 'description' in themed_data:
            themed_data['description'] = self._apply_theme_to_text(
                themed_data['description'], setting_theme
            )
        
        # Apply theme to major plot points
        if 'major_plot_points' in themed_data:
            themed_data['major_plot_points'] = [
                self._apply_theme_to_text(point, setting_theme) if isinstance(point, str)
                else self._apply_theme_to_dict(point, setting_theme)
                for point in themed_data['major_plot_points']
            ]
        
        # Apply theme to antagonists (REQ-CAM-140: themed NPCs)
        if 'antagonists' in themed_data:
            themed_data['antagonists'] = [
                self._apply_theme_to_dict(antagonist, setting_theme)
                for antagonist in themed_data['antagonists']
            ]
        
        # Track theme application
        themed_data['applied_setting_theme'] = {
            "theme": setting_theme.value,
            "applied_at": datetime.utcnow().isoformat(),
            "elements_themed": ["title", "description", "plot_points", "antagonists"]
        }
        
        return themed_data
    
    async def _integrate_psychological_experiments(self, campaign_data: Dict[str, Any],
                                                 experiment_types: List[PsychologicalExperimentType]) -> Dict[str, Any]:
        """
        Integrate psychological experiments into campaign structure.
        
        Implements REQ-CAM-118-132: Psychological Experiment Integration
        """
        logger.info(f"Integrating {len(experiment_types)} psychological experiments")
        
        experiment_data = campaign_data.copy()
        
        # Get experiment generator
        experiment_generator = self.generator_factory.get_generator("experiment")
        if not experiment_generator:
            logger.warning("Experiment generator not available, skipping integration")
            return campaign_data
        
        integrated_experiments = []
        
        for exp_type in experiment_types:
            try:
                # Generate experiment integration
                experiment_integration = await experiment_generator.generate_experiment_integration(
                    experiment_type=exp_type,
                    campaign_context=campaign_data.get('description', ''),
                    custom_concept=""
                )
                
                # Add ethical guidelines (REQ-CAM-132)
                experiment_integration = self._add_ethical_guidelines(experiment_integration)
                
                integrated_experiments.append(experiment_integration)
                
            except Exception as e:
                logger.warning(f"Failed to integrate experiment {exp_type.value}: {e}")
        
        if integrated_experiments:
            experiment_data['psychological_experiments'] = {
                "experiments": integrated_experiments,
                "integration_notes": "Experiments are optional content requiring DM approval",
                "ethical_guidelines_included": True,
                "integrated_at": datetime.utcnow().isoformat()
            }
        
        return experiment_data
    
    # ============================================================================
    # ESSENTIAL HELPER METHODS FOR TASK 2 IMPLEMENTATION
    # ============================================================================
    
    def _build_campaign_prompt(self, concept: str, genre: CampaignGenre, 
                              complexity: CampaignComplexity, themes: List[str],
                              setting_theme: SettingTheme, include_psychological_experiments: bool,
                              experiment_types: List[str]) -> str:
        """Build LLM prompt for complete campaign generation."""
        
        themes_text = ", ".join(themes) if themes else "adventure, heroism"
        experiments_text = ""
        if include_psychological_experiments and experiment_types:
            experiments_text = f"\n\nIncorporate these psychological experiments naturally into the campaign: {', '.join(experiment_types)}"
        
        return f"""Create a complete D&D campaign with the following requirements:

CONCEPT: {concept}

PARAMETERS:
- Genre: {genre.value}
- Setting Theme: {setting_theme.value}
- Complexity: {complexity.value}
- Themes: {themes_text}
{experiments_text}

Please generate a structured campaign with:
1. Title (engaging and thematic)
2. Description (compelling 2-3 sentence overview)
3. Plot Summary (3-4 paragraphs covering beginning, middle, end)
4. Main Antagonist (name, motivation, methods, background)
5. Key NPCs (3-5 important supporting characters)
6. Major Locations (4-6 significant places)
7. Campaign Hooks (3-4 ways to draw players in)

Focus on creating morally complex scenarios with interconnected plot threads.
The campaign should have compelling narrative hooks and meaningful player choices.

Format as JSON with clear sections."""
    
    def _build_skeleton_prompt(self, concept: str, campaign_title: str, 
                              campaign_description: str, themes: List[str],
                              session_count: int, detail_level: str,
                              genre: CampaignGenre, setting_theme: SettingTheme) -> str:
        """Build LLM prompt for campaign skeleton generation."""
        
        themes_text = ", ".join(themes) if themes else "adventure, heroism"
        detail_instruction = {
            'basic': 'Provide brief, high-level outlines',
            'medium': 'Provide moderate detail with key plot points',
            'detailed': 'Provide comprehensive outlines with scene details'
        }.get(detail_level, 'Provide moderate detail')
        
        return f"""Create a D&D campaign skeleton with the following structure:

CAMPAIGN: {campaign_title}
DESCRIPTION: {campaign_description}
CONCEPT: {concept}
GENRE: {genre.value}
SETTING: {setting_theme.value}
THEMES: {themes_text}
SESSIONS: {session_count}
DETAIL LEVEL: {detail_level}

Generate:
1. Plot Overview (campaign arc summary)
2. Act Structure (beginning/middle/end breakdown)
3. Major Plot Points (5-8 key story beats)
4. Chapter Outlines (one per session, {detail_instruction})
5. Key Antagonists (primary villains and their goals)
6. Important NPCs (major supporting characters)
7. Primary Locations (main settings)
8. Plot Hooks (ways to engage players)

Each chapter outline should include:
- Title and 1-2 sentence summary
- Key scenes or encounters
- Plot advancement
- Character development opportunities

Format as structured JSON."""
    
    def _build_refinement_prompt(self, campaign_context: str, refinement_prompt: str,
                                refinement_type: str, preserve_elements: List[str],
                                player_feedback: str) -> str:
        """Build LLM prompt for campaign refinement."""
        
        preserve_text = f"PRESERVE: {', '.join(preserve_elements)}" if preserve_elements else ""
        feedback_text = f"PLAYER FEEDBACK: {player_feedback}" if player_feedback else ""
        
        return f"""Refine this D&D campaign based on the guidance provided:

CURRENT CAMPAIGN:
{campaign_context}

REFINEMENT REQUEST: {refinement_prompt}
REFINEMENT TYPE: {refinement_type}
{preserve_text}
{feedback_text}

Instructions:
1. Maintain narrative consistency while implementing requested changes
2. Preserve specified elements exactly as they are
3. Enhance the campaign based on the refinement guidance
4. If player feedback is provided, address their specific concerns
5. Improve story coherence and player engagement

Provide the refined campaign in the same JSON structure as the original.
Highlight what changes were made and why."""
    
    def _parse_campaign_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into structured campaign data."""
        try:
            # Try to parse as JSON first
            if llm_response.strip().startswith('{'):
                return json.loads(llm_response)
            
            # Fallback: extract structured information from text
            lines = llm_response.split('\n')
            campaign_data = {}
            
            # Extract basic information
            for line in lines:
                if line.startswith('Title:') or line.startswith('TITLE:'):
                    campaign_data['title'] = line.split(':', 1)[1].strip()
                elif line.startswith('Description:') or line.startswith('DESCRIPTION:'):
                    campaign_data['description'] = line.split(':', 1)[1].strip()
            
            # Default structure if parsing fails
            if not campaign_data:
                campaign_data = {
                    'title': 'Generated Campaign',
                    'description': 'A campaign generated from the provided concept.',
                    'plot_summary': llm_response[:500],
                    'main_antagonist': {'name': 'Generated Antagonist', 'motivation': 'Unknown'},
                    'key_npcs': [],
                    'major_locations': [],
                    'campaign_hooks': []
                }
            
            return campaign_data
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON, using fallback structure")
            return {
                'title': 'Generated Campaign',
                'description': 'A campaign generated from the provided concept.',
                'plot_summary': llm_response[:500],
                'main_antagonist': {'name': 'Generated Antagonist', 'motivation': 'Unknown'},
                'key_npcs': [],
                'major_locations': [],
                'campaign_hooks': []
            }
    
    def _parse_skeleton_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into structured skeleton data."""
        try:
            if llm_response.strip().startswith('{'):
                return json.loads(llm_response)
            
            # Fallback structure
            return {
                'plot_overview': llm_response[:300],
                'act_structure': [],
                'major_plot_points': [],
                'key_antagonists': [],
                'important_npcs': [],
                'primary_locations': [],
                'plot_hooks': []
            }
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse skeleton response, using fallback")
            return {
                'plot_overview': llm_response[:300],
                'act_structure': [],
                'major_plot_points': [],
                'key_antagonists': [],
                'important_npcs': [],
                'primary_locations': [],
                'plot_hooks': []
            }
    
    def _parse_refinement_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM refinement response into structured changes."""
        try:
            if llm_response.strip().startswith('{'):
                return json.loads(llm_response)
            
            return {
                'changes': [],
                'reasoning': llm_response[:200]
            }
            
        except json.JSONDecodeError:
            return {
                'changes': [],
                'reasoning': 'Refinement applied based on guidance'
            }
    
    async def _generate_campaign_chapters(self, campaign_structure: Dict[str, Any],
                                        session_count: int, party_level: int, party_size: int,
                                        genre: CampaignGenre, setting_theme: SettingTheme,
                                        use_character_service: bool) -> List[Dict[str, Any]]:
        """Generate detailed chapters for the campaign."""
        chapters = []
        
        for i in range(session_count):
            chapter_title = f"Chapter {i + 1}"
            chapter_summary = f"Session {i + 1} of the campaign"
            
            # Basic chapter structure
            chapter = {
                "id": f"chapter_{i + 1}",
                "number": i + 1,
                "title": chapter_title,
                "summary": chapter_summary,
                "party_level": party_level,
                "party_size": party_size,
                "encounters": [],
                "npcs": [],
                "locations": [],
                "items": [],
                "plot_advancement": f"Advances main plot thread {i + 1}",
                "created_at": datetime.utcnow().isoformat()
            }
            
            chapters.append(chapter)
        return chapters
    
    async def _generate_chapter_outlines(self, skeleton_structure: Dict[str, Any],
                                       session_count: int, detail_level: str) -> List[Dict[str, Any]]:
        """Generate chapter outlines for skeleton."""
        outlines = []
        
        for i in range(session_count):
            outline = {
                "chapter_number": i + 1,
                "title": f"Chapter {i + 1}",
                "summary": f"Session {i + 1} outline",
                "key_scenes": [],
                "plot_advancement": f"Advances story arc",
                "detail_level": detail_level
            }
            
            outlines.append(outline)
        
        return outlines
    
    def _build_campaign_context(self, existing_data: Dict[str, Any]) -> str:
        """Build context string from existing campaign data for refinement."""
        title = existing_data.get('title', 'Campaign')
        description = existing_data.get('description', '')
        plot_summary = existing_data.get('plot_summary', '')
        
        context = f"TITLE: {title}\n"
        if description:
            context += f"DESCRIPTION: {description}\n"
        if plot_summary:
            context += f"PLOT: {plot_summary}\n"
        
        # Add chapter information if available
        chapters = existing_data.get('chapters', [])
        if chapters:
            context += f"CHAPTERS: {len(chapters)} chapters planned\n"
        
        return context
    
    def _apply_refinements(self, existing_data: Dict[str, Any], 
                          refinements: Dict[str, Any], 
                          preserve_elements: List[str]) -> Dict[str, Any]:
        """Apply refinements to existing data while preserving specified elements."""
        refined_data = existing_data.copy()
        
        # Apply changes from refinements, but preserve specified elements
        changes = refinements.get('changes', [])
        for change in changes:
            field = change.get('field')
            if field and field not in preserve_elements:
                new_value = change.get('new_value')
                if new_value is not None:
                    refined_data[field] = new_value
        
        return refined_data