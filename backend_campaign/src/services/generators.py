"""
Campaign Content Generators
===========================
AI-powered generation services for D&D campaign creation, content generation, and adaptive storytelling.
Based on requirements in campaign_creation.md for comprehensive campaign management.
"""

from typing import Dict, Any, List, Optional, Union
import json
import logging
import asyncio
import aiohttp
from datetime import datetime
from enum import Enum

from src.core.config import Settings
from src.services.llm_service import LLMService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CAMPAIGN GENERATION ENUMS AND CONSTANTS
# ============================================================================

class CampaignGenre(str, Enum):
    FANTASY = "fantasy"
    SCI_FI = "sci_fi"
    HORROR = "horror"
    MYSTERY = "mystery"
    HISTORICAL = "historical"
    CYBERPUNK = "cyberpunk"
    STEAMPUNK = "steampunk"
    WESTERN = "western"
    POST_APOCALYPTIC = "post_apocalyptic"
    DYSTOPIAN_FICTION = "dystopian_fiction"
    APOCALYPTIC_FICTION = "apocalyptic_fiction"
    CUSTOM = "custom"  # Allows user-defined genres with LLM assistance

class CampaignComplexity(str, Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"

class SettingTheme(str, Enum):
    STANDARD_FANTASY = "standard_fantasy"
    WESTERN = "western"
    CYBERPUNK = "cyberpunk"
    STEAMPUNK = "steampunk"
    HORROR = "horror"
    NOIR = "noir"
    SPACE_FANTASY = "space_fantasy"
    URBAN_FANTASY = "urban_fantasy"
    CUSTOM = "custom"  # Allows user-defined themes with LLM assistance

class PsychologicalExperimentType(str, Enum):
    # Classic psychological experiments
    OBEDIENCE = "obedience"
    BYSTANDER_EFFECT = "bystander_effect"
    CONFORMITY = "conformity"
    COGNITIVE_DISSONANCE = "cognitive_dissonance"
    ANCHORING_BIAS = "anchoring_bias"
    SOCIAL_LEARNING = "social_learning"
    DIFFUSION_RESPONSIBILITY = "diffusion_responsibility"
    
    # Game theory experiments
    PRISONERS_DILEMMA = "prisoners_dilemma"
    ULTIMATUM_GAME = "ultimatum_game"
    TRAGEDY_OF_COMMONS = "tragedy_of_commons"
    COOPERATION_COMPETITION = "cooperation_competition"
    TRUST_RECIPROCITY = "trust_reciprocity"
    
    # Economic psychology
    LOSS_AVERSION = "loss_aversion"
    SUNK_COST_FALLACY = "sunk_cost_fallacy"
    ENDOWMENT_EFFECT = "endowment_effect"
    
    # Social psychology  
    IN_GROUP_OUT_GROUP = "in_group_out_group"
    AUTHORITY_LEGITIMACY = "authority_legitimacy"
    SOCIAL_PROOF = "social_proof"
    STEREOTYPE_THREAT = "stereotype_threat"
    
    # Decision making
    FRAMING_EFFECTS = "framing_effects"
    AVAILABILITY_HEURISTIC = "availability_heuristic"
    CONFIRMATION_BIAS = "confirmation_bias"
    
    # Custom/extensible option for user-defined or LLM-assisted experiments
    CUSTOM = "custom"

# Campaign theme constants for generation
CAMPAIGN_THEMES = {
    "puzzle_solving": "Logic puzzles, riddles, environmental challenges",
    "mystery_investigation": "Clues, red herrings, deductive reasoning",
    "tactical_combat": "Strategic positioning, terrain usage, complex battles",
    "character_interaction": "Dialogue, negotiations, relationship building",
    "political_intrigue": "Power dynamics, conspiracies, court politics",
    "exploration": "Discovery, mapping, survival in unknown territories",
    "horror_survival": "Fear, resource scarcity, psychological pressure",
    "heist_infiltration": "Planning, stealth, contingency management",
    "moral_philosophy": "Ethical dilemmas, complex moral choices",
    "time_travel": "Temporal mechanics, causality, historical events",
    "educational_historical": "Learning through historical recreation"
}

# ============================================================================
# BASE CAMPAIGN GENERATOR CLASS
# ============================================================================

class BaseCampaignGenerator:
    """Base class for all campaign content generators with common utilities."""
    
    def __init__(self, llm_service: LLMService, settings: Optional[Settings] = None):
        self.llm_service = llm_service
        self.settings = settings or Settings()
        self.base_timeout = 30  # Longer timeout for campaign generation
        self.max_retries = 3
    
    async def _generate_with_fallback(self, prompt: str, fallback_func, max_tokens: int = 800, 
                                    temperature: float = 0.8) -> Dict[str, Any]:
        """Generate content with LLM and provide fallback if needed."""
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting LLM generation (attempt {attempt + 1})")
                response = await self.llm_service.generate_content(
                    prompt, 
                    max_tokens=max_tokens, 
                    temperature=temperature
                )
                
                if response and len(response.strip()) > 10:
                    return {"content": response.strip(), "source": "llm", "attempt": attempt + 1}
                else:
                    logger.warning(f"Empty or insufficient LLM response on attempt {attempt + 1}")
                    
            except Exception as e:
                logger.warning(f"LLM generation failed on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    logger.info("Using fallback generation")
                    return {"content": fallback_func(), "source": "fallback", "attempt": attempt + 1}
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return {"content": fallback_func(), "source": "fallback", "attempt": self.max_retries}
    
    def _clean_json_response(self, response: str) -> str:
        """Clean and extract JSON from LLM response."""
        if not response:
            raise ValueError("Empty response")
        
        response = response.strip()
        # Remove markdown code blocks
        response = response.replace('```json', '').replace('```', '')
        
        # Find JSON boundaries
        start = response.find('{')
        end = response.rfind('}')
        
        if start == -1 or end == -1:
            # Try to find array boundaries
            start = response.find('[')
            end = response.rfind(']')
            
        if start == -1 or end == -1:
            raise ValueError("No JSON found in response")
            
        return response[start:end+1]
    
    def _parse_json_safely(self, response: str) -> Optional[Dict[str, Any]]:
        """Safely parse JSON response with error handling."""
        try:
            cleaned = self._clean_json_response(response)
            return json.loads(cleaned)
        except (ValueError, json.JSONDecodeError) as e:
            logger.warning(f"JSON parsing failed: {e}")
            return None

# ============================================================================
# CORE CAMPAIGN GENERATOR
# ============================================================================

class CampaignGenerator(BaseCampaignGenerator):
    """
    Generate complete D&D campaigns from user concepts.
    Implements REQ-CAM-001-018: LLM-Powered Campaign Creation Requirements
    """
    
    async def generate_campaign_from_concept(self, concept: str, genre: CampaignGenre = CampaignGenre.FANTASY,
                                           complexity: CampaignComplexity = CampaignComplexity.MEDIUM,
                                           session_count: int = 10, themes: List[str] = None,
                                           setting_theme: Optional[SettingTheme] = None) -> Dict[str, Any]:
        """
        Generate a complete campaign from a user concept.
        Implements REQ-CAM-001: AI-Driven Campaign Generation from Scratch
        """
        
        logger.info(f"Generating campaign from concept: {concept[:50]}...")
        
        prompt = self._build_campaign_generation_prompt(concept, genre, complexity, session_count, themes, setting_theme)
        
        fallback_func = lambda: self._get_fallback_campaign(concept, genre, complexity, session_count, themes)
        
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=1200, temperature=0.8)
        
        # Parse and structure the campaign data
        if result["source"] == "llm":
            parsed_campaign = self._parse_json_safely(result["content"])
            if parsed_campaign:
                campaign_data = self._structure_campaign_data(parsed_campaign, concept, genre, complexity, session_count, themes)
            else:
                campaign_data = self._get_fallback_campaign(concept, genre, complexity, session_count, themes)
        else:
            campaign_data = result["content"]
        
        campaign_data["generation_metadata"] = {
            "source": result["source"],
            "attempts": result["attempt"],
            "generated_at": datetime.utcnow().isoformat(),
            "input_concept": concept,
            "genre": genre.value,
            "complexity": complexity.value
        }
        
        return campaign_data
    
    def _build_campaign_generation_prompt(self, concept: str, genre: CampaignGenre, 
                                        complexity: CampaignComplexity, session_count: int, 
                                        themes: List[str], setting_theme: Optional[SettingTheme]) -> str:
        """Build comprehensive campaign generation prompt."""
        
        theme_descriptions = ""
        if themes:
            theme_descriptions = "\n".join([f"- {theme}: {CAMPAIGN_THEMES.get(theme, 'Custom theme')}" for theme in themes])
        
        setting_context = ""
        if setting_theme and setting_theme != SettingTheme.STANDARD_FANTASY:
            setting_context = f"\nSetting Theme: Adapt all content to fit {setting_theme.value.replace('_', ' ')} theme"
        
        prompt = f"""
Generate a complete D&D campaign based on this concept:

Concept: {concept}
Genre: {genre.value}
Complexity: {complexity.value}
Sessions: {session_count}
Themes: {theme_descriptions if themes else 'General adventure'}
{setting_context}

Requirements:
1. Create compelling and complex storylines with multiple layers of intrigue
2. Generate interconnected plot threads and character motivations  
3. Include morally complex scenarios with no clear "good vs evil" dichotomies
4. Develop multi-layered plots with main storylines and interconnected subplots
5. Create complex antagonists with understandable motivations and believable goals

Return ONLY this JSON structure:
{{
  "title": "Compelling campaign title",
  "description": "2-3 paragraph campaign description with rich narrative",
  "main_storyline": "Core story arc with beginning, middle, end",
  "major_plot_points": ["5-8 major story milestones"],
  "antagonists": [
    {{
      "name": "Primary antagonist name",
      "motivation": "Complex, understandable motivation",
      "methods": "How they pursue their goals",
      "backstory": "Rich background that explains their actions"
    }}
  ],
  "themes": ["3-5 major campaign themes"],
  "plot_hooks": ["3-5 compelling hooks to engage players"],
  "moral_dilemmas": ["2-3 complex ethical scenarios"],
  "subplots": ["3-4 interconnected subplots"],
  "world_stakes": "What happens if the heroes fail",
  "gm_notes": "Guidance for running this campaign effectively"
}}
"""
        
        return prompt
    
    def _structure_campaign_data(self, parsed_data: Dict[str, Any], concept: str, 
                                genre: CampaignGenre, complexity: CampaignComplexity,
                                session_count: int, themes: List[str]) -> Dict[str, Any]:
        """Structure and validate parsed campaign data."""
        
        # Ensure required fields exist
        required_fields = ["title", "description", "themes", "gm_notes"]
        for field in required_fields:
            if field not in parsed_data:
                parsed_data[field] = self._get_default_field_value(field, concept, genre)
        
        # Add metadata
        parsed_data.update({
            "status": "draft",
            "session_count": session_count,
            "complexity": complexity.value,
            "genre": genre.value,
            "input_concept": concept,
            "estimated_duration": f"{session_count * 4} hours"
        })
        
        return parsed_data
    
    def _get_fallback_campaign(self, concept: str, genre: CampaignGenre, 
                             complexity: CampaignComplexity, session_count: int, 
                             themes: List[str]) -> Dict[str, Any]:
        """Generate fallback campaign using templates."""
        
        logger.info("Using fallback campaign generation")
        
        title = f"Campaign: {concept[:30]}{'...' if len(concept) > 30 else ''}"
        
        fallback_campaign = {
            "title": title,
            "description": f"An epic {genre.value} campaign where heroes must {concept}. "
                          f"This {complexity.value} campaign will challenge players with "
                          f"complex moral choices and interconnected storylines over {session_count} sessions.",
            "main_storyline": f"Heroes discover that {concept} is part of a larger conspiracy that threatens the realm.",
            "major_plot_points": [
                "Initial discovery of the threat",
                "First confrontation with minor antagonists", 
                "Revelation of the true scope of danger",
                "Gathering allies and resources",
                "Major setback or betrayal",
                "Final preparation for climax",
                "Climactic confrontation",
                "Resolution and consequences"
            ],
            "antagonists": [{
                "name": "The Shadow Orchestrator",
                "motivation": "Believes that only through controlled chaos can true order emerge",
                "methods": "Manipulates events from behind the scenes using networks of unwitting pawns",
                "backstory": "Once a hero who lost everything to random catastrophe, now seeks to eliminate uncertainty"
            }],
            "themes": themes or ["heroism", "sacrifice", "moral_complexity", "discovery"],
            "plot_hooks": [
                "A mysterious message arrives asking for help",
                "Strange events begin occurring in familiar places",
                "An old ally goes missing under suspicious circumstances"
            ],
            "moral_dilemmas": [
                "Save the many by sacrificing the few, or risk everyone to save all",
                "Trust a reformed enemy who offers crucial information"
            ],
            "subplots": [
                "A character's past comes back to haunt them",
                "Political tensions threaten to undermine the heroes' mission",
                "A powerful artifact tempts heroes with easy solutions"
            ],
            "world_stakes": "The realm falls into chaos, with innocent people suffering the consequences",
            "gm_notes": f"This {complexity.value} campaign emphasizes {', '.join(themes or ['adventure'])}. "
                       f"Focus on player agency and meaningful choices throughout {session_count} sessions.",
            "status": "draft",
            "session_count": session_count,
            "complexity": complexity.value,
            "genre": genre.value,
            "input_concept": concept,
            "estimated_duration": f"{session_count * 4} hours"
        }
        
        return fallback_campaign
    
    def _get_default_field_value(self, field: str, concept: str, genre: CampaignGenre) -> str:
        """Get default value for missing required fields."""
        
        defaults = {
            "title": f"{genre.value.title()} Campaign: {concept[:30]}",
            "description": f"An engaging {genre.value} campaign centered around: {concept}",
            "themes": ["adventure", "discovery", "heroism"],
            "gm_notes": f"Campaign generated from concept: {concept}. Customize as needed."
        }
        
        return defaults.get(field, f"Generated {field} for {concept}")

# ============================================================================
# CAMPAIGN SKELETON AND CHAPTER GENERATORS
# ============================================================================

class CampaignSkeletonGenerator(BaseCampaignGenerator):
    """
    Generate campaign skeletons with major plot points and chapter outlines.
    Implements REQ-CAM-023-027: Skeleton Plot and Campaign Generation
    """
    
    async def generate_campaign_skeleton(self, campaign_title: str, campaign_description: str,
                                       themes: List[str], session_count: int = 10,
                                       detail_level: str = "standard") -> Dict[str, Any]:
        """
        Generate a structured campaign skeleton with plot points and chapter outlines.
        Implements REQ-CAM-023: Generate high-level campaign outline
        """
        
        logger.info(f"Generating campaign skeleton for: {campaign_title}")
        
        prompt = self._build_skeleton_generation_prompt(
            campaign_title, campaign_description, themes, session_count, detail_level
        )
        
        fallback_func = lambda: self._get_fallback_skeleton(
            campaign_title, campaign_description, themes, session_count
        )
        
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=1500, temperature=0.75)
        
        if result["source"] == "llm":
            parsed_skeleton = self._parse_json_safely(result["content"])
            if parsed_skeleton:
                skeleton_data = self._structure_skeleton_data(parsed_skeleton, session_count)
            else:
                skeleton_data = fallback_func()
        else:
            skeleton_data = result["content"]
        
        skeleton_data["generation_metadata"] = {
            "source": result["source"],
            "attempts": result["attempt"],
            "generated_at": datetime.utcnow().isoformat(),
            "detail_level": detail_level
        }
        
        return skeleton_data
    
    def _build_skeleton_generation_prompt(self, title: str, description: str, themes: List[str],
                                        session_count: int, detail_level: str) -> str:
        """Build prompt for campaign skeleton generation."""
        
        detail_instructions = {
            "basic": "Brief outlines and simple descriptions",
            "standard": "Moderate detail with key plot points and connections",
            "detailed": "Comprehensive descriptions with full narrative context"
        }
        
        detail_desc = detail_instructions.get(detail_level, "moderate detail")
        
        prompt = f"""
Generate a campaign skeleton for this D&D campaign:

Title: {title}
Description: {description}
Themes: {', '.join(themes)}
Sessions: {session_count}
Detail Level: {detail_level} ({detail_desc})

Create a campaign skeleton with:
1. 5-8 major plot points/milestones that form the story backbone
2. {session_count} chapter outlines with titles and summaries
3. Story arc progression (beginning, middle, end phases)
4. Key conflicts and resolution points
5. Character hooks and engagement opportunities

Return ONLY this JSON structure:
{{
  "major_plot_points": [
    {{
      "order": 1,
      "title": "Plot point title",
      "description": "What happens in this milestone",
      "story_phase": "beginning|middle|end",
      "prerequisites": ["What must happen before this"],
      "consequences": ["What this leads to"]
    }}
  ],
  "story_phases": {{
    "beginning": {{
      "description": "Opening phase goals and events",
      "sessions": [1, 2, 3],
      "key_objectives": ["Primary goals for this phase"]
    }},
    "middle": {{
      "description": "Development phase with complications",
      "sessions": [4, 5, 6, 7],
      "key_objectives": ["Primary goals for this phase"]
    }},
    "end": {{
      "description": "Resolution phase and climax",
      "sessions": [8, 9, 10],
      "key_objectives": ["Primary goals for this phase"]
    }}
  }},
  "chapter_outlines": [
    {{
      "session": 1,
      "title": "Chapter title",
      "summary": "2-3 sentence chapter summary",
      "objectives": ["What players should accomplish"],
      "conflicts": ["Main challenges or obstacles"],
      "hooks": ["Engagement hooks for players"],
      "connections": ["How this connects to other chapters"]
    }}
  ],
  "narrative_threads": [
    {{
      "name": "Thread name",
      "description": "Ongoing storyline description",
      "introduction_session": 1,
      "resolution_session": 8,
      "key_moments": ["Important beats in this thread"]
    }}
  ],
  "campaign_progression": "Overall flow and pacing notes"
}}
"""
        
        return prompt
    
    def _structure_skeleton_data(self, parsed_data: Dict[str, Any], session_count: int) -> Dict[str, Any]:
        """Structure and validate skeleton data."""
        
        # Ensure chapter outlines match session count
        if "chapter_outlines" in parsed_data:
            current_count = len(parsed_data["chapter_outlines"])
            if current_count != session_count:
                logger.warning(f"Chapter count mismatch: {current_count} vs {session_count}")
                parsed_data["chapter_outlines"] = self._adjust_chapter_count(
                    parsed_data["chapter_outlines"], session_count
                )
        
        return parsed_data
    
    def _adjust_chapter_count(self, chapters: List[Dict], target_count: int) -> List[Dict]:
        """Adjust chapter list to match target session count."""
        
        current_count = len(chapters)
        
        if current_count < target_count:
            # Add missing chapters
            for i in range(current_count, target_count):
                chapters.append({
                    "session": i + 1,
                    "title": f"Chapter {i + 1}: To Be Determined",
                    "summary": "Chapter outline to be developed",
                    "objectives": ["TBD"],
                    "conflicts": ["TBD"],
                    "hooks": ["TBD"],
                    "connections": ["TBD"]
                })
        elif current_count > target_count:
            # Trim excess chapters
            chapters = chapters[:target_count]
        
        return chapters
    
    def _get_fallback_skeleton(self, title: str, description: str, themes: List[str], 
                             session_count: int) -> Dict[str, Any]:
        """Generate fallback skeleton using templates."""
        
        logger.info("Using fallback skeleton generation")
        
        # Calculate session distribution
        beginning_sessions = max(2, session_count // 4)
        end_sessions = max(2, session_count // 4) 
        middle_sessions = session_count - beginning_sessions - end_sessions
        
        fallback_skeleton = {
            "major_plot_points": [
                {
                    "order": 1,
                    "title": "Initial Hook",
                    "description": "Heroes discover the central conflict",
                    "story_phase": "beginning",
                    "prerequisites": [],
                    "consequences": ["Investigation begins", "Stakes become clear"]
                },
                {
                    "order": 2,
                    "title": "First Challenge",
                    "description": "Initial confrontation with the threat",
                    "story_phase": "beginning",
                    "prerequisites": ["Initial Hook"],
                    "consequences": ["Heroes understand the scope", "Antagonist reveals themselves"]
                },
                {
                    "order": 3,
                    "title": "Rising Action",
                    "description": "Complications arise and stakes increase",
                    "story_phase": "middle",
                    "prerequisites": ["First Challenge"],
                    "consequences": ["Allies and enemies defined", "Resources gathered"]
                },
                {
                    "order": 4,
                    "title": "Major Setback",
                    "description": "Significant failure or betrayal",
                    "story_phase": "middle",
                    "prerequisites": ["Rising Action"],
                    "consequences": ["Heroes must regroup", "New strategy needed"]
                },
                {
                    "order": 5,
                    "title": "Final Preparation",
                    "description": "Heroes prepare for final confrontation",
                    "story_phase": "end",
                    "prerequisites": ["Major Setback"],
                    "consequences": ["All pieces in place", "Final battle ready"]
                },
                {
                    "order": 6,
                    "title": "Climax",
                    "description": "Final confrontation with main antagonist",
                    "story_phase": "end",
                    "prerequisites": ["Final Preparation"],
                    "consequences": ["Conflict resolved", "Consequences revealed"]
                }
            ],
            "story_phases": {
                "beginning": {
                    "description": "Introduce the threat and engage heroes in the conflict",
                    "sessions": list(range(1, beginning_sessions + 1)),
                    "key_objectives": ["Establish hooks", "Define stakes", "Introduce major NPCs"]
                },
                "middle": {
                    "description": "Develop complications and deepen involvement",
                    "sessions": list(range(beginning_sessions + 1, beginning_sessions + middle_sessions + 1)),
                    "key_objectives": ["Escalate conflicts", "Develop characters", "Build toward climax"]
                },
                "end": {
                    "description": "Resolve conflicts and conclude storylines",
                    "sessions": list(range(session_count - end_sessions + 1, session_count + 1)),
                    "key_objectives": ["Final confrontation", "Resolution", "Epilogue"]
                }
            },
            "chapter_outlines": self._generate_fallback_chapters(session_count),
            "narrative_threads": [
                {
                    "name": "Main Quest",
                    "description": "Primary storyline following the central conflict",
                    "introduction_session": 1,
                    "resolution_session": session_count,
                    "key_moments": ["Initial discovery", "Major revelation", "Final confrontation"]
                },
                {
                    "name": "Character Development",
                    "description": "Personal growth and backstory integration",
                    "introduction_session": 2,
                    "resolution_session": session_count - 1,
                    "key_moments": ["Character backgrounds revealed", "Personal conflicts", "Growth moments"]
                }
            ],
            "campaign_progression": f"Structured {session_count}-session campaign with clear beginning, middle, and end phases. Emphasizes {', '.join(themes[:3])} themes."
        }
        
        return fallback_skeleton
    
    def _generate_fallback_chapters(self, session_count: int) -> List[Dict[str, Any]]:
        """Generate fallback chapter outlines."""
        
        chapter_templates = [
            "Opening Hook", "Investigation Begins", "First Challenge", "Complications Arise",
            "Allies and Enemies", "Major Revelation", "Setback and Regrouping", 
            "Preparation", "Climax", "Resolution"
        ]
        
        chapters = []
        for i in range(session_count):
            template_index = min(i, len(chapter_templates) - 1)
            if i >= len(chapter_templates) - 2:
                # Last two sessions get climax/resolution
                template_index = len(chapter_templates) - 2 + (i - (session_count - 2))
            
            chapters.append({
                "session": i + 1,
                "title": f"Chapter {i + 1}: {chapter_templates[template_index]}",
                "summary": f"Session focusing on {chapter_templates[template_index].lower()} within the campaign narrative.",
                "objectives": [f"Advance {chapter_templates[template_index].lower()} storyline"],
                "conflicts": ["Challenge appropriate to story phase"],
                "hooks": ["Engage players with current narrative thread"],
                "connections": ["Links to previous and future chapters"]
            })
        
        return chapters

# ============================================================================
# CHAPTER CONTENT GENERATOR
# ============================================================================

class ChapterContentGenerator(BaseCampaignGenerator):
    """
    Generate comprehensive chapter content including NPCs, encounters, locations.
    Implements REQ-CAM-033-037: Chapter Content Generation
    """
    
    async def generate_chapter_content(self, campaign_title: str, campaign_description: str,
                                     chapter_title: str, chapter_summary: str,
                                     themes: List[str], include_npcs: bool = True,
                                     include_encounters: bool = True, include_locations: bool = True,
                                     include_items: bool = True, chapter_theme: Optional[str] = None,
                                     campaign_context: Optional[Dict[str, Any]] = None,
                                     use_character_service: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive chapter content with all required elements.
        Implements REQ-CAM-033: Include location descriptions and maps
        Implements REQ-CAM-034: Include key NPCs with motivations and dialogue
        Implements REQ-CAM-035: Include appropriate encounters
        """
        
        logger.info(f"Generating content for chapter: {chapter_title}")
        
        # Generate main chapter narrative
        narrative_result = await self._generate_chapter_narrative(
            campaign_title, campaign_description, chapter_title, chapter_summary, themes, chapter_theme
        )
        
        chapter_content = {
            "narrative": narrative_result,
            "npcs": [],
            "encounters": [],
            "locations": [],
            "items": [],
            "hooks": []
        }
        
        # Generate supporting content in parallel for efficiency
        tasks = []
        
        if include_npcs:
            tasks.append(self._generate_chapter_npcs(campaign_title, chapter_title, themes, campaign_context, use_character_service))
        
        if include_encounters:
            tasks.append(self._generate_chapter_encounters(campaign_title, chapter_title, themes, chapter_theme))
        
        if include_locations:
            tasks.append(self._generate_chapter_locations(campaign_title, chapter_title, themes))
        
        if include_items:
            tasks.append(self._generate_chapter_items(campaign_title, chapter_title, themes))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            result_index = 0
            if include_npcs:
                npcs_result = results[result_index] if not isinstance(results[result_index], Exception) else {"content": [], "source": "fallback"}
                chapter_content["npcs"] = npcs_result
                result_index += 1
            
            if include_encounters:
                encounters_result = results[result_index] if not isinstance(results[result_index], Exception) else {"content": [], "source": "fallback"}
                chapter_content["encounters"] = encounters_result
                result_index += 1
            
            if include_locations:
                locations_result = results[result_index] if not isinstance(results[result_index], Exception) else {"content": [], "source": "fallback"}
                chapter_content["locations"] = locations_result
                result_index += 1
            
            if include_items:
                items_result = results[result_index] if not isinstance(results[result_index], Exception) else {"content": [], "source": "fallback"}
                chapter_content["items"] = items_result
        
        # Generate chapter hooks
        hooks_result = await self._generate_chapter_hooks(campaign_title, chapter_title, themes)
        chapter_content["hooks"] = hooks_result
        
        chapter_content["generation_metadata"] = {
            "generated_at": datetime.utcnow().isoformat(),
            "includes": {
                "npcs": include_npcs,
                "encounters": include_encounters,
                "locations": include_locations,
                "items": include_items
            },
            "chapter_theme": chapter_theme
        }
        
        return chapter_content
    
    async def _generate_chapter_narrative(self, campaign_title: str, campaign_description: str,
                                        chapter_title: str, chapter_summary: str,
                                        themes: List[str], chapter_theme: Optional[str]) -> Dict[str, Any]:
        """Generate detailed chapter narrative content."""
        
        theme_context = f"Chapter Theme: {chapter_theme}\n" if chapter_theme else ""
        
        prompt = f"""
Generate detailed narrative content for this D&D chapter:

Campaign: {campaign_title}
Campaign Context: {campaign_description}
Chapter: {chapter_title}
Summary: {chapter_summary}
Campaign Themes: {', '.join(themes)}
{theme_context}

Create detailed chapter content including:
1. Scene descriptions with vivid atmosphere
2. Key events and story beats
3. Dialogue suggestions for important moments
4. Pacing notes and transition guidance
5. Connection to overall campaign story

Write 500-800 words of engaging narrative content that a DM can use to run this chapter.
Focus on creating immersive scenes and meaningful story progression.
"""
        
        fallback_func = lambda: self._get_fallback_narrative(chapter_title, chapter_summary, themes)
        
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=1200, temperature=0.8)
        
        return result
    
    async def _generate_chapter_npcs(self, campaign_title: str, chapter_title: str, themes: List[str], 
                                   campaign_context: Optional[Dict[str, Any]] = None,
                                   use_character_service: bool = True) -> Dict[str, Any]:
        """
        Generate NPCs for the chapter with optional backend character service integration.
        
        Args:
            campaign_title: Title of the campaign
            chapter_title: Title of the chapter
            themes: List of chapter themes
            campaign_context: Full campaign context for character service integration
            use_character_service: Whether to use backend character creation service
        """
        
        if use_character_service and campaign_context:
            # Use integrated character service for detailed NPCs
            try:
                async with CharacterServiceClient() as char_client:
                    integrator = CampaignCharacterIntegrator(char_client, self.llm_service)
                    
                    chapter_data = {
                        "title": chapter_title,
                        "themes": themes,
                        "description": f"Chapter from {campaign_title}"
                    }
                    
                    character_result = await integrator.generate_chapter_characters(campaign_context, chapter_data)
                    
                    # Format result to match expected structure
                    return {
                        "npcs": character_result["npcs"],
                        "detailed_analysis": character_result["requirements_analysis"],
                        "generation_method": "character_service_integration"
                    }
                    
            except Exception as e:
                logger.warning(f"Character service integration failed, falling back to LLM-only generation: {str(e)}")
                # Fall through to LLM-only generation
        
        # Fallback to LLM-only generation (original method)
        prompt = f"""
Generate 2-3 NPCs for this D&D chapter:

Campaign: {campaign_title}
Chapter: {chapter_title}
Themes: {', '.join(themes)}

For each NPC, provide:
- Name and basic description
- Role in the chapter (ally, neutral, antagonist, merchant, etc.)
- Motivation and goals
- Personality traits
- Key dialogue or quotes
- Relationship to the plot
- Suggested species/race (can be custom for non-fantasy genres)
- Basic stats if combat-capable

Return as a structured list of NPCs with all details.
"""
        
        fallback_func = lambda: self._get_fallback_npcs(chapter_title)
        
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=800, temperature=0.9)
        result["generation_method"] = "llm_only"
        
        return result
    
    async def _generate_chapter_encounters(self, campaign_title: str, chapter_title: str, 
                                         themes: List[str], chapter_theme: Optional[str]) -> Dict[str, Any]:
        """Generate encounters for the chapter."""
        
        encounter_types = {
            "tactical_combat": "Strategic combat encounters with positioning and terrain",
            "mystery_investigation": "Investigation and puzzle-solving encounters",
            "character_interaction": "Social and negotiation encounters",
            "exploration": "Discovery and survival encounters"
        }
        
        encounter_focus = encounter_types.get(chapter_theme, "Varied encounter types")
        
        prompt = f"""
Generate 1-2 encounters for this D&D chapter:

Campaign: {campaign_title}
Chapter: {chapter_title}
Themes: {', '.join(themes)}
Encounter Focus: {encounter_focus}

For each encounter, provide:
- Encounter type (combat, social, exploration, puzzle)
- Setting and environment
- Objectives and victory conditions
- Challenges and obstacles
- Potential tactics and strategies
- Rewards or consequences

Create engaging encounters that advance the story and utilize the chapter themes.
"""
        
        fallback_func = lambda: self._get_fallback_encounters(chapter_title, chapter_theme)
        
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=600, temperature=0.8)
        
        return result
    
    async def _generate_chapter_locations(self, campaign_title: str, chapter_title: str, themes: List[str]) -> Dict[str, Any]:
        """Generate locations for the chapter."""
        
        prompt = f"""
Generate 2-3 locations for this D&D chapter:

Campaign: {campaign_title}
Chapter: {chapter_title}
Themes: {', '.join(themes)}

For each location, provide:
- Location name and type
- Detailed description with atmosphere
- Important features and areas
- Inhabitants or creatures
- Secrets or hidden elements
- Connection to chapter events

Create immersive locations that support the chapter's story and themes.
"""
        
        fallback_func = lambda: self._get_fallback_locations(chapter_title)
        
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=600, temperature=0.8)
        
        return result
    
    async def _generate_chapter_items(self, campaign_title: str, chapter_title: str, themes: List[str]) -> Dict[str, Any]:
        """Generate items and treasures for the chapter."""
        
        prompt = f"""
Generate appropriate items and treasures for this D&D chapter:

Campaign: {campaign_title}
Chapter: {chapter_title}
Themes: {', '.join(themes)}

Include:
- 1-2 magical or unique items
- Appropriate mundane treasure
- Story-relevant objects
- Consumable items or tools

For each item, provide:
- Name and description
- Mechanical properties
- Story significance
- How players obtain it

Ensure items are thematically appropriate and balanced for the campaign.
"""
        
        fallback_func = lambda: self._get_fallback_items(chapter_title)
        
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=500, temperature=0.8)
        
        return result
    
    async def _generate_chapter_hooks(self, campaign_title: str, chapter_title: str, themes: List[str]) -> Dict[str, Any]:
        """Generate hooks to connect to subsequent chapters."""
        
        prompt = f"""
Generate 2-3 plot hooks for this D&D chapter that connect to future storylines:

Campaign: {campaign_title}
Chapter: {chapter_title}
Themes: {', '.join(themes)}

Create hooks that:
- Connect to subsequent chapters
- Introduce future plot elements
- Create mysteries or unresolved questions
- Provide character development opportunities

Each hook should be intriguing and leave players wanting to know more.
"""
        
        fallback_func = lambda: self._get_fallback_hooks(chapter_title)
        
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=400, temperature=0.8)
        
        return result
    
    # Fallback methods
    def _get_fallback_narrative(self, chapter_title: str, chapter_summary: str, themes: List[str]) -> str:
        """Generate fallback narrative content."""
        return f"""
{chapter_title}

{chapter_summary}

The chapter unfolds with the heroes facing challenges that test their {', '.join(themes[:2])}. 
Key scenes include investigation, character interaction, and meaningful choices that advance both 
personal character development and the overall campaign storyline.

Scene 1: Opening - The heroes arrive at the location and begin to understand the situation.
Scene 2: Development - Complications arise that require creative problem-solving.
Scene 3: Climax - A significant challenge or revelation changes the stakes.
Scene 4: Resolution - The immediate situation is resolved, but larger questions remain.

Throughout the chapter, emphasize player agency and the consequences of their choices.
"""
    
    def _get_fallback_npcs(self, chapter_title: str) -> List[Dict[str, str]]:
        """Generate fallback NPCs."""
        return [
            {
                "name": "Concerned Local",
                "description": "A worried resident who knows more than they initially reveal",
                "role": "Information provider and potential ally",
                "motivation": "Protect their community from growing threats",
                "personality": "Cautious but ultimately helpful when trust is earned",
                "dialogue": "I've seen strange things lately... things that shouldn't be possible."
            },
            {
                "name": "Mysterious Contact",
                "description": "An enigmatic figure with hidden connections to the plot",
                "role": "Plot advancement and future storyline setup",
                "motivation": "Pursue hidden agenda that may align with or oppose heroes",
                "personality": "Cryptic, intelligent, potentially manipulative",
                "dialogue": "You're not the first to ask these questions... but you might be the last."
            }
        ]
    
    def _get_fallback_encounters(self, chapter_title: str, chapter_theme: Optional[str]) -> List[Dict[str, str]]:
        """Generate fallback encounters."""
        encounters = [
            {
                "type": "Investigation",
                "setting": "Key location related to chapter events",
                "objective": "Gather information and uncover clues",
                "challenges": "Hidden information, misleading evidence, time pressure",
                "tactics": "Careful observation, social interaction, logical deduction",
                "rewards": "Crucial information, potential allies, story advancement"
            }
        ]
        
        if chapter_theme == "tactical_combat":
            encounters.append({
                "type": "Strategic Combat",
                "setting": "Terrain with tactical opportunities",
                "objective": "Defeat enemies while achieving secondary goals",
                "challenges": "Environmental hazards, multiple objectives, enemy tactics",
                "tactics": "Positioning, teamwork, creative use of environment",
                "rewards": "Victory, resources, prisoner for interrogation"
            })
        
        return encounters
    
    def _get_fallback_locations(self, chapter_title: str) -> List[Dict[str, str]]:
        """Generate fallback locations."""
        return [
            {
                "name": "Central Hub",
                "type": "Settlement or important building",
                "description": "A bustling location where information and rumors flow freely",
                "features": "Common areas, private meeting spaces, multiple entry/exit points",
                "inhabitants": "Mix of locals, travelers, and persons of interest",
                "secrets": "Hidden areas or concealed information relevant to the plot"
            },
            {
                "name": "Challenge Site",
                "type": "Location of main chapter events",
                "description": "Where the primary action or investigation takes place",
                "features": "Environment that supports chapter objectives and encounters",
                "inhabitants": "Key NPCs and potential antagonists",
                "secrets": "Clues or revelations that advance the story"
            }
        ]
    
    def _get_fallback_items(self, chapter_title: str) -> List[Dict[str, str]]:
        """Generate fallback items."""
        return [
            {
                "name": "Clue Object",
                "description": "An item that provides important information",
                "properties": "No mechanical benefit, high story value",
                "significance": "Reveals plot details or character background",
                "acquisition": "Found during investigation or given by NPC"
            },
            {
                "name": "Useful Tool",
                "description": "Practical item that aids in chapter objectives",
                "properties": "Provides advantage on specific skill checks",
                "significance": "Helps overcome chapter challenges",
                "acquisition": "Reward for completing objectives or clever thinking"
            }
        ]
    
    def _get_fallback_hooks(self, chapter_title: str) -> List[str]:
        """Generate fallback plot hooks."""
        return [
            "A mysterious message is discovered that hints at larger conspiracies",
            "An NPC mentions strange occurrences in a distant location",
            "Evidence suggests the current threat is part of a broader pattern"
        ]

# ============================================================================
# SETTING THEME GENERATOR
# ============================================================================

class SettingThemeGenerator:
    """
    Generator for creating custom setting themes that can be used in campaigns.
    Supports extending beyond predefined themes with LLM assistance.
    """
    
    def __init__(self, llm_service: LLMService, settings: Optional[Settings] = None):
        self.llm_service = llm_service
        self.settings = settings
    
    async def generate_custom_theme(self, theme_concept: str, genre: CampaignGenre = CampaignGenre.FANTASY) -> Dict[str, Any]:
        """Generate a custom setting theme based on a concept."""
        
        prompt = f"""
Create a detailed D&D campaign setting theme based on this concept: {theme_concept}

For genre: {genre.value}

Generate:
1. Theme Name: A memorable name for this setting theme
2. Core Atmosphere: The mood, tone, and feel of this theme
3. Key Elements: 5-7 distinctive features that define this theme
4. Typical Locations: Common places and environments 
5. Character Archetypes: Types of NPCs and characters that fit
6. Conflict Sources: Natural sources of tension and adventure
7. Unique Mechanics: Special rules or gameplay elements
8. Visual Style: How this theme looks and feels
9. Example Scenarios: 3 sample adventure hooks

Make it rich, immersive, and distinctive from standard themes.
Format as a detailed guide for DMs to implement.
"""
        
        fallback_func = lambda: self._get_fallback_custom_theme(theme_concept, genre)
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=800)
        
        theme_data = {
            "theme_concept": theme_concept,
            "genre": genre.value,
            "content": result["content"],
            "metadata": {
                "source": result["source"],
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        return theme_data
    
    async def enhance_existing_theme(self, base_theme: SettingTheme, enhancement_concept: str) -> Dict[str, Any]:
        """Enhance an existing theme with additional elements."""
        
        prompt = f"""
Take the existing D&D setting theme "{base_theme.value}" and enhance it with this concept: {enhancement_concept}

Build upon the base theme while adding:
1. New Atmosphere Elements: How the enhancement changes the mood
2. Additional Features: New distinctive elements to incorporate
3. Enhanced Locations: New or modified environments
4. Character Variations: How existing archetypes are affected
5. New Conflict Types: Additional sources of tension
6. Mechanical Additions: New rules or gameplay elements
7. Visual Enhancements: How the look and feel evolves
8. Enhanced Scenarios: Adventure hooks that combine both themes

Keep the original theme recognizable while meaningfully expanding it.
"""
        
        fallback_func = lambda: self._get_fallback_enhanced_theme(base_theme, enhancement_concept)
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=600)
        
        enhanced_theme = {
            "base_theme": base_theme.value,
            "enhancement_concept": enhancement_concept,
            "content": result["content"],
            "metadata": {
                "source": result["source"],
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        return enhanced_theme
    
    async def _generate_with_fallback(self, prompt: str, fallback_func, max_tokens: int = 500, temperature: float = 0.8) -> Dict[str, str]:
        """Generate content with LLM fallback."""
        try:
            if self.llm_service:
                content = await self.llm_service.generate_content(prompt, max_tokens=max_tokens, temperature=temperature)
                return {"content": content, "source": "llm"}
        except Exception as e:
            logger.warning(f"LLM generation failed for theme, using fallback: {str(e)}")
        
        return {"content": fallback_func(), "source": "fallback"}
    
    def _get_fallback_custom_theme(self, theme_concept: str, genre: CampaignGenre) -> str:
        """Generate fallback custom theme content."""
        return f"""
Custom Theme: {theme_concept}
Genre: {genre.value}

Core Atmosphere:
- Mysterious and evocative atmosphere centered around {theme_concept}
- Blends {genre.value} elements with unique thematic focus

Key Elements:
- Central theme of {theme_concept} influences all campaign aspects
- Distinctive visual and narrative motifs
- Unique cultural or environmental features
- Specialized equipment, magic, or technology
- Thematic conflicts and moral dilemmas

Typical Locations:
- Settings that embody the {theme_concept} theme
- Both familiar and exotic environments
- Locations that create opportunities for thematic exploration

Character Archetypes:
- NPCs that represent different aspects of {theme_concept}
- Allies and antagonists shaped by the theme
- Complex characters with thematic motivations

Adventure Hooks:
1. Investigate mysteries related to {theme_concept}
2. Navigate conflicts arising from thematic elements
3. Discover hidden aspects of the theme's influence

[Expand and customize based on specific campaign needs]
"""
    
    def _get_fallback_enhanced_theme(self, base_theme: SettingTheme, enhancement: str) -> str:
        """Generate fallback enhanced theme content."""
        return f"""
Enhanced Theme: {base_theme.value} + {enhancement}

The classic {base_theme.value} setting is enhanced with {enhancement} elements:

Enhanced Atmosphere:
- Retains core {base_theme.value} feel while incorporating {enhancement}
- New layers of complexity and interest
- Evolved visual and narrative elements

Additional Features:
- {enhancement} influences existing {base_theme.value} elements
- New mechanics and systems blend both themes
- Enhanced role-playing opportunities

Adventure Opportunities:
- Scenarios that blend {base_theme.value} with {enhancement}
- Conflicts arising from the combination
- New types of challenges and mysteries

[Develop specific combinations based on campaign requirements]
"""


# ============================================================================
# PSYCHOLOGICAL EXPERIMENT GENERATOR
# ============================================================================

class PsychologicalExperimentGenerator:
    """
    Generator for integrating psychological and game-theory experiments into campaigns.
    Supports both predefined experiments and custom experimental scenarios.
    """
    
    def __init__(self, llm_service: LLMService, settings: Optional[Settings] = None):
        self.llm_service = llm_service
        self.settings = settings
        
        # Predefined experiment templates for fallback
        self.experiment_templates = {
            "obedience": "Authority figures giving questionable orders",
            "bystander_effect": "Situations where group size affects helping behavior",
            "conformity": "Peer pressure and social influence scenarios",
            "cognitive_dissonance": "Conflicting beliefs and justification mechanisms",
            "prisoners_dilemma": "Cooperation vs. betrayal dilemmas",
            "ultimatum_game": "Fair division and rejection of unfair offers",
            "tragedy_of_commons": "Shared resource management conflicts",
            "trust_reciprocity": "Building and testing trust relationships",
            "loss_aversion": "Fear of losing vs. potential for gain",
            "framing_effects": "How presentation affects decision making"
        }
    
    async def generate_experiment_integration(self, experiment_type: PsychologicalExperimentType, 
                                            campaign_context: str = "", custom_concept: str = "") -> Dict[str, Any]:
        """Generate integration of a psychological experiment into campaign scenarios."""
        
        if experiment_type == PsychologicalExperimentType.CUSTOM and custom_concept:
            return await self._generate_custom_experiment(custom_concept, campaign_context)
        
        experiment_name = experiment_type.value.replace("_", " ").title()
        
        prompt = f"""
Create a D&D campaign integration for the psychological experiment: {experiment_name}

Campaign Context: {campaign_context}

Design:
1. Scenario Setup: How to naturally introduce this experiment in D&D
2. Player Roles: How PCs become subjects or observers
3. Variables to Test: What psychological aspects to examine
4. Measurement Methods: How to track player responses (without breaking immersion)
5. Narrative Integration: Making it feel like natural story elements
6. Expected Outcomes: Possible player behaviors and responses
7. DM Guidelines: How to facilitate without bias
8. Ethical Considerations: Keeping it fun and educational
9. Debrief Opportunities: How to discuss insights afterward

Make it engaging, educational, and true to the psychological principle while maintaining D&D fun.
"""
        
        fallback_func = lambda: self._get_fallback_experiment_integration(experiment_type, campaign_context)
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=800)
        
        integration_data = {
            "experiment_type": experiment_type.value,
            "experiment_name": experiment_name,
            "campaign_context": campaign_context,
            "integration_content": result["content"],
            "metadata": {
                "source": result["source"],
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        return integration_data
    
    async def _generate_custom_experiment(self, custom_concept: str, campaign_context: str) -> Dict[str, Any]:
        """Generate a custom psychological experiment integration."""
        
        prompt = f"""
Create a D&D campaign integration for this custom psychological/behavioral concept: {custom_concept}

Campaign Context: {campaign_context}

Design a novel experimental scenario that:
1. Explores the psychological principle: {custom_concept}
2. Uses D&D mechanics and narrative naturally
3. Creates meaningful player choices and observations
4. Maintains game enjoyment while being educational
5. Allows for data collection without breaking immersion
6. Provides insights into human behavior and decision-making
7. Includes clear setup, execution, and debrief phases
8. Considers ethical implications and player comfort

Make it innovative, engaging, and scientifically interesting while being a great D&D experience.
"""
        
        fallback_func = lambda: self._get_fallback_custom_experiment(custom_concept, campaign_context)
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=900)
        
        custom_experiment = {
            "experiment_type": "custom",
            "custom_concept": custom_concept,
            "campaign_context": campaign_context,
            "integration_content": result["content"],
            "metadata": {
                "source": result["source"],
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        return custom_experiment
    
    async def generate_experiment_series(self, theme: str, experiment_count: int = 3) -> Dict[str, Any]:
        """Generate a series of related psychological experiments for a campaign theme."""
        
        prompt = f"""
Create a series of {experiment_count} related psychological experiments for a D&D campaign with theme: {theme}

Each experiment should:
1. Build on previous experiments in the series
2. Explore different aspects of human psychology
3. Use increasingly complex D&D scenarios
4. Maintain narrative continuity
5. Allow for comparative analysis
6. Progress in sophistication and depth

For each experiment, provide:
- Psychological principle being tested
- D&D scenario integration
- Expected learning outcomes
- Connection to overall theme
- How it builds on previous experiments

Make this a comprehensive psychological exploration through D&D gameplay.
"""
        
        fallback_func = lambda: self._get_fallback_experiment_series(theme, experiment_count)
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=1000)
        
        series_data = {
            "theme": theme,
            "experiment_count": experiment_count,
            "series_content": result["content"],
            "metadata": {
                "source": result["source"],
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        return series_data
    
    async def _generate_with_fallback(self, prompt: str, fallback_func, max_tokens: int = 600, temperature: float = 0.8) -> Dict[str, str]:
        """Generate content with LLM fallback."""
        try:
            if self.llm_service:
                content = await self.llm_service.generate_content(prompt, max_tokens=max_tokens, temperature=temperature)
                return {"content": content, "source": "llm"}
        except Exception as e:
            logger.warning(f"LLM generation failed for psychological experiment, using fallback: {str(e)}")
        
        return {"content": fallback_func(), "source": "fallback"}
    
    def _get_fallback_experiment_integration(self, experiment_type: PsychologicalExperimentType, context: str) -> str:
        """Generate fallback experiment integration."""
        template = self.experiment_templates.get(experiment_type.value, "General psychological principle exploration")
        
        return f"""
Psychological Experiment Integration: {experiment_type.value.replace('_', ' ').title()}

Core Principle: {template}
Campaign Context: {context}

Scenario Setup:
- Create natural D&D situations that trigger the psychological principle
- Ensure player choices reflect real psychological phenomena
- Maintain immersion while allowing observation

Implementation:
1. Introduce scenario organically within campaign narrative
2. Present choices that test the psychological principle
3. Observe player responses without judgment
4. Record outcomes for later analysis
5. Continue story naturally regardless of choices

Measurement:
- Track decision patterns without breaking character
- Note group dynamics and individual responses
- Document unexpected behaviors and insights

Debrief Opportunities:
- Post-session discussions about choices and motivations
- Exploration of real-world applications
- Analysis of group vs. individual decision making

Educational Value:
- Insights into human psychology and behavior
- Understanding of decision-making processes
- Improved empathy and social awareness

[Customize specific scenarios based on campaign needs and player comfort levels]
"""
    
    def _get_fallback_custom_experiment(self, concept: str, context: str) -> str:
        """Generate fallback custom experiment content."""
        return f"""
Custom Psychological Experiment: {concept}

Campaign Context: {context}

Experimental Design:
- Novel exploration of {concept} through D&D mechanics
- Player-driven scenarios that naturally test the principle
- Observational methods that maintain immersion
- Multiple measurement opportunities throughout campaign

Implementation Framework:
1. Scenario Introduction: Organic presentation within story
2. Choice Architecture: Meaningful decisions that reveal psychology
3. Data Collection: Unobtrusive observation and recording
4. Analysis Opportunities: Pattern recognition and insight development
5. Educational Integration: Natural learning and discussion

Key Considerations:
- Player comfort and consent
- Ethical implementation
- Scientific validity within game context
- Entertainment value and story coherence
- Long-term educational benefits

Expected Outcomes:
- Novel insights into {concept}
- Enhanced understanding of human behavior
- Improved game experience through psychological depth
- Educational value for all participants

[Develop specific scenarios and mechanics based on the psychological principle and campaign requirements]
"""
    
    def _get_fallback_experiment_series(self, theme: str, count: int) -> str:
        """Generate fallback experiment series content."""
        return f"""
Psychological Experiment Series: {theme}

Series Overview:
A progressive sequence of {count} psychological experiments integrated into D&D campaign with {theme} theme.

Series Design Principles:
- Each experiment builds on previous learnings
- Increasing complexity and sophistication
- Thematic coherence throughout the series
- Comparative analysis opportunities
- Comprehensive psychological exploration

Experiment Progression:
1. Foundation: Basic psychological principles related to {theme}
2. Development: More complex interactions and group dynamics
3. Integration: Advanced scenarios combining multiple principles
[Continue pattern for additional experiments]

Learning Objectives:
- Deep understanding of psychological principles
- Recognition of patterns in human behavior
- Application of psychological insights to real situations
- Enhanced empathy and social awareness
- Scientific thinking and observation skills

Implementation Guidelines:
- Maintain player engagement throughout series
- Ensure ethical considerations at all stages
- Provide opportunities for reflection and discussion
- Document insights and patterns across experiments
- Adapt based on player responses and interests

[Customize specific experiments based on theme, player group, and learning objectives]
"""

# ============================================================================
# ADAPTIVE CAMPAIGN GENERATOR  
# ============================================================================

class AdaptiveCampaignGenerator:
    """
    Generator for adapting campaign content based on player behavior and preferences.
    Analyzes player choices and generates adaptive content accordingly.
    """
    
    def __init__(self, llm_service: LLMService, settings: Optional[Settings] = None):
        self.llm_service = llm_service
        self.settings = settings
    
    async def analyze_player_behavior(self, session_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze player behavior patterns from session data."""
        
        if not session_data:
            return self._get_default_analysis()
        
        # Extract behavior patterns from session data
        behavior_summary = self._extract_behavior_patterns(session_data)
        
        prompt = f"""
Analyze these D&D player behavior patterns from recent sessions:

{behavior_summary}

Provide analysis on:
1. Combat Preferences: How players approach fights
2. Social Interactions: How they handle NPCs and dialogue
3. Problem Solving: Their approach to puzzles and challenges
4. Risk Taking: How cautious or bold they are
5. Group Dynamics: How they work together
6. Story Engagement: What story elements they respond to most
7. Exploration Style: How they approach new areas and secrets
8. Character Development: How they grow their characters

For each category, provide:
- Observed patterns
- Player preferences
- Recommended content adjustments
- Potential new content types to try

Format as actionable insights for campaign adaptation.
"""
        
        fallback_func = lambda: self._get_fallback_behavior_analysis(session_data)
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=800)
        
        analysis = {
            "session_count": len(session_data),
            "behavior_summary": behavior_summary,
            "analysis_content": result["content"],
            "metadata": {
                "source": result["source"],
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }
        
        return analysis
    
    async def generate_adaptive_content(self, content: str, player_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate adapted content based on player analysis."""
        
        analysis_summary = player_analysis.get("behavior_summary", "No specific player patterns identified")
        
        prompt = f"""
Adapt this D&D campaign content based on player analysis:

Original Content:
{content}

Player Analysis:
{analysis_summary}

Adapt the content to:
1. Better match observed player preferences
2. Address areas where engagement was low
3. Incorporate elements players responded to positively
4. Adjust challenge levels based on player behavior
5. Enhance aspects that drive player investment
6. Add opportunities for preferred play styles
7. Improve pacing based on player attention patterns
8. Include hooks that connect to player interests

Return adapted content that maintains the original's core purpose while being more engaging for this specific player group.
"""
        
        fallback_func = lambda: self._get_fallback_adaptive_content(content, player_analysis)
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=900)
        
        adaptation = {
            "original_content": content,
            "adapted_content": result["content"],
            "player_analysis_used": analysis_summary,
            "metadata": {
                "source": result["source"],
                "adapted_at": datetime.utcnow().isoformat()
            }
        }
        
        return adaptation
    
    async def suggest_campaign_adjustments(self, campaign_data: Dict[str, Any], 
                                         player_feedback: List[str] = None) -> Dict[str, Any]:
        """Suggest adjustments to campaign based on player feedback and behavior."""
        
        feedback_summary = "; ".join(player_feedback) if player_feedback else "No specific feedback provided"
        campaign_summary = campaign_data.get("title", "Campaign") + ": " + campaign_data.get("description", "")[:200]
        
        prompt = f"""
Suggest campaign adjustments for this D&D campaign:

Campaign: {campaign_summary}

Player Feedback: {feedback_summary}

Provide specific, actionable suggestions for:
1. Story Adjustments: Plot elements to modify or enhance
2. Encounter Changes: Combat and challenge modifications
3. NPC Improvements: Character interaction enhancements
4. Pacing Adjustments: Session flow and timing changes
5. Content Additions: New elements to incorporate
6. Mechanical Tweaks: Rule modifications or additions
7. Setting Enhancements: World-building improvements
8. Player Agency: Ways to increase meaningful choices

For each suggestion, explain:
- Why this change would improve the campaign
- How to implement it smoothly
- Expected player response
- Integration with existing content

Focus on practical, implementable improvements.
"""
        
        fallback_func = lambda: self._get_fallback_campaign_adjustments(campaign_data, player_feedback)
        result = await self._generate_with_fallback(prompt, fallback_func, max_tokens=800)
        
        suggestions = {
            "campaign_title": campaign_data.get("title", "Unknown Campaign"),
            "player_feedback": feedback_summary,
            "suggestions_content": result["content"],
            "metadata": {
                "source": result["source"],
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        return suggestions
    
    def _extract_behavior_patterns(self, session_data: List[Dict[str, Any]]) -> str:
        """Extract behavior patterns from session data."""
        patterns = []
        
        for session in session_data:
            session_info = f"Session {session.get('session_number', 'Unknown')}: "
            
            # Extract key behaviors
            if 'combat_actions' in session:
                patterns.append(f"{session_info}Combat style: {session['combat_actions']}")
            if 'social_choices' in session:
                patterns.append(f"{session_info}Social approach: {session['social_choices']}")
            if 'exploration_behavior' in session:
                patterns.append(f"{session_info}Exploration: {session['exploration_behavior']}")
            if 'problem_solving' in session:
                patterns.append(f"{session_info}Problem solving: {session['problem_solving']}")
        
        return "; ".join(patterns) if patterns else "Limited behavior data available"
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when no session data is available."""
        return {
            "session_count": 0,
            "behavior_summary": "No session data available for analysis",
            "analysis_content": "Unable to provide player behavior analysis without session data. Consider gathering information about player preferences through direct feedback or observation.",
            "metadata": {
                "source": "default",
                "analyzed_at": datetime.utcnow().isoformat()
            }
        }
    
    async def _generate_with_fallback(self, prompt: str, fallback_func, max_tokens: int = 600, temperature: float = 0.8) -> Dict[str, str]:
        """Generate content with LLM fallback."""
        try:
            if self.llm_service:
                content = await self.llm_service.generate_content(prompt, max_tokens=max_tokens, temperature=temperature)
                return {"content": content, "source": "llm"}
        except Exception as e:
            logger.warning(f"LLM generation failed for adaptive content, using fallback: {str(e)}")
        
        return {"content": fallback_func(), "source": "fallback"}
    
    def _get_fallback_behavior_analysis(self, session_data: List[Dict[str, Any]]) -> str:
        """Generate fallback behavior analysis."""
        return f"""
Player Behavior Analysis ({len(session_data)} sessions analyzed)

General Observations:
- Players have participated in {len(session_data)} documented sessions
- Behavior patterns require additional observation for detailed analysis
- Recommend gathering more specific player preference data

Suggested Content Adjustments:
1. Monitor player engagement with different content types
2. Ask for direct feedback on preferred activities
3. Observe reaction to various challenge levels
4. Note which story elements generate most interest
5. Track preferred interaction styles

Adaptive Recommendations:
- Experiment with different encounter types
- Vary social interaction opportunities
- Adjust challenge difficulty based on response
- Incorporate player character backgrounds more
- Provide multiple solution paths for problems

[Requires additional player data for more specific recommendations]
"""
    
    def _get_fallback_adaptive_content(self, content: str, analysis: Dict[str, Any]) -> str:
        """Generate fallback adaptive content."""
        return f"""
{content}

[ADAPTIVE MODIFICATIONS]
Based on available player analysis, consider these potential improvements:

1. Enhanced Player Engagement:
   - Add multiple solution approaches
   - Include character-specific hooks
   - Provide meaningful choices with consequences

2. Balanced Challenge:
   - Adjust difficulty based on group capabilities
   - Include both combat and non-combat challenges
   - Offer optional complexity layers

3. Story Integration:
   - Connect to player character motivations
   - Reference previous player decisions
   - Build on established group dynamics

4. Interactive Elements:
   - Encourage player creativity and problem-solving
   - Provide opportunities for character development
   - Support different play styles within the group

[Customize based on specific player feedback and observed preferences]
"""
    
    def _get_fallback_campaign_adjustments(self, campaign_data: Dict[str, Any], feedback: List[str]) -> str:
        """Generate fallback campaign adjustment suggestions."""
        return f"""
Campaign Adjustment Suggestions

Campaign: {campaign_data.get('title', 'Current Campaign')}

General Improvement Areas:
1. Story Pacing: Review session flow and adjust for optimal engagement
2. Player Agency: Ensure meaningful choices affect outcomes
3. Challenge Balance: Monitor difficulty and adjust as needed
4. Character Integration: Connect plot to player character backgrounds
5. Variety: Mix different types of encounters and activities

Based on Available Feedback:
{'; '.join(feedback) if feedback else 'No specific feedback available'}

Recommended Actions:
1. Conduct regular check-ins with players about campaign satisfaction
2. Experiment with different content types to find optimal mix
3. Adapt NPCs and plots based on player interactions
4. Adjust encounter difficulty based on group performance
5. Incorporate player suggestions where possible

Implementation Strategy:
- Make gradual adjustments rather than major overhauls
- Test changes with smaller elements before larger modifications
- Maintain core campaign vision while adapting presentation
- Document what works well for future reference

[Customize recommendations based on specific player feedback and campaign needs]
"""

# ============================================================================
# CHARACTER SERVICE INTEGRATION
# ============================================================================

class CharacterServiceClient:
    """
    Client for integrating with the D&D character creation backend service.
    Handles automatic NPC/monster generation with campaign context.
    """
    
    def __init__(self, backend_url: str = "http://localhost:8001", timeout: int = 30):
        self.backend_url = backend_url.rstrip('/')
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def generate_character(self, creation_type: str, campaign_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a character using the backend character creation service.
        
        Args:
            creation_type: Type of character to create ('npc', 'monster', etc.)
            campaign_context: Context from campaign including genre, theme, requirements
            
        Returns:
            Generated character data from backend service
        """
        if not self.session:
            raise RuntimeError("CharacterServiceClient not initialized. Use async context manager.")
        
        # Build request payload with campaign context
        payload = {
            "creation_type": creation_type,
            "options": {
                "genre": campaign_context.get("genre", "fantasy"),
                "theme": campaign_context.get("theme", "standard_fantasy"),
                "complexity": campaign_context.get("complexity", "medium"),
                "challenge_rating": campaign_context.get("challenge_rating"),
                "party_level": campaign_context.get("party_level", 1),
                "narrative_role": campaign_context.get("narrative_role", "supporting"),
                "custom_species": campaign_context.get("custom_species"),
                "custom_classes": campaign_context.get("custom_classes"),
                "cultural_background": campaign_context.get("cultural_background"),
                "motivations": campaign_context.get("motivations", []),
                "relationships": campaign_context.get("relationships", [])
            }
        }
        
        try:
            url = f"{self.backend_url}/api/v2/factory/create"
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Character generation failed: {response.status} - {error_text}")
                    return await self._get_fallback_character(creation_type, campaign_context)
        
        except Exception as e:
            logger.error(f"Character service request failed: {str(e)}")
            return await self._get_fallback_character(creation_type, campaign_context)
    
    async def generate_multiple_characters(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate multiple characters in batch for efficiency.
        
        Args:
            requests: List of character generation requests
            
        Returns:
            List of generated characters
        """
        results = []
        for request in requests:
            result = await self.generate_character(
                request["creation_type"], 
                request["campaign_context"]
            )
            results.append(result)
        
        return results
    
    async def _get_fallback_character(self, creation_type: str, campaign_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a fallback character when backend service fails.
        """
        genre = campaign_context.get("genre", "fantasy")
        theme = campaign_context.get("theme", "standard_fantasy")
        
        fallback_data = {
            "id": f"fallback_{creation_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "creation_type": creation_type,
            "name": f"Generated {creation_type.title()}",
            "description": f"A {genre} {creation_type} with {theme} characteristics",
            "stats": self._get_default_stats(creation_type),
            "traits": [f"{genre.title()} heritage", f"{theme.replace('_', ' ').title()} background"],
            "motivations": campaign_context.get("motivations", ["Pursue personal goals"]),
            "challenge_rating": campaign_context.get("challenge_rating", 1),
            "source": "campaign_fallback"
        }
        
        return fallback_data
    
    def _get_default_stats(self, creation_type: str) -> Dict[str, int]:
        """Get default stats based on creation type."""
        if creation_type == "monster":
            return {
                "strength": 14, "dexterity": 12, "constitution": 13,
                "intelligence": 10, "wisdom": 11, "charisma": 8,
                "armor_class": 12, "hit_points": 15
            }
        else:  # NPC or other
            return {
                "strength": 10, "dexterity": 10, "constitution": 10,
                "intelligence": 10, "wisdom": 10, "charisma": 10,
                "armor_class": 10, "hit_points": 8
            }


class CampaignCharacterIntegrator:
    """
    Integrates campaign generation with character creation service.
    Automatically determines quantities, challenge ratings, and character types
    based on campaign context and requirements.
    """
    
    def __init__(self, character_client: CharacterServiceClient, llm_service: LLMService):
        self.character_client = character_client
        self.llm_service = llm_service
    
    async def generate_chapter_characters(self, campaign_data: Dict[str, Any], 
                                        chapter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate all NPCs and monsters needed for a chapter based on campaign context.
        
        Args:
            campaign_data: Campaign information (genre, theme, complexity, etc.)
            chapter_data: Chapter information (title, description, themes, etc.)
            
        Returns:
            Dictionary containing generated NPCs and monsters
        """
        # Determine character requirements based on chapter complexity and narrative needs
        character_requirements = await self._analyze_character_requirements(campaign_data, chapter_data)
        
        # Generate NPCs
        npcs = await self._generate_chapter_npcs(campaign_data, chapter_data, character_requirements["npcs"])
        
        # Generate monsters for encounters
        monsters = await self._generate_chapter_monsters(campaign_data, chapter_data, character_requirements["monsters"])
        
        return {
            "npcs": npcs,
            "monsters": monsters,
            "requirements_analysis": character_requirements
        }
    
    async def _analyze_character_requirements(self, campaign_data: Dict[str, Any], 
                                           chapter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to analyze chapter needs and determine character requirements.
        """
        genre = campaign_data.get("genre", "fantasy")
        theme = campaign_data.get("theme", "standard_fantasy")
        complexity = campaign_data.get("complexity", "medium")
        party_level = campaign_data.get("party_level", 1)
        party_size = campaign_data.get("party_size", 4)
        
        prompt = f"""
Analyze this D&D chapter and determine character requirements:

Campaign Genre: {genre}
Campaign Theme: {theme}
Campaign Complexity: {complexity}
Party Level: {party_level}
Party Size: {party_size}

Chapter: {chapter_data.get('title', 'Untitled Chapter')}
Description: {chapter_data.get('description', 'No description')}
Themes: {', '.join(chapter_data.get('themes', []))}

Determine and return as JSON:
1. NPCs needed:
   - Number of major NPCs (2-4 recurring/important characters)
   - Number of minor NPCs (3-8 one-scene characters)
   - Appropriate challenge ratings or social complexity levels
   - Species/races that fit the genre and theme
   - Custom species if needed for the setting
   - Narrative roles (ally, neutral, antagonist, merchant, etc.)

2. Monsters needed:
   - Number of different monster types (1-4 types)
   - Quantity of each type (1-8 creatures per type)
   - Challenge ratings appropriate for party level
   - Monster types that fit genre and theme
   - Custom creatures if traditional D&D monsters don't fit

3. Special considerations:
   - Custom species/classes needed
   - Cultural backgrounds specific to the setting
   - Unique abilities or traits for the genre

Return only valid JSON with this structure.
"""
        
        try:
            response = await self.llm_service.generate_content(prompt, max_tokens=800, temperature=0.7)
            
            # Try to parse JSON response
            if isinstance(response, str):
                requirements = json.loads(response)
            else:
                requirements = response
                
            return requirements
            
        except Exception as e:
            logger.error(f"Failed to analyze character requirements: {str(e)}")
            return self._get_fallback_requirements(party_level, complexity)
    
    def _get_fallback_requirements(self, party_level: int, complexity: str) -> Dict[str, Any]:
        """Fallback character requirements if LLM analysis fails."""
        base_cr = max(1, party_level - 1)
        
        if complexity == "simple":
            npc_multiplier, monster_multiplier = 0.7, 0.8
        elif complexity == "complex":
            npc_multiplier, monster_multiplier = 1.3, 1.2
        else:  # medium
            npc_multiplier, monster_multiplier = 1.0, 1.0
        
        return {
            "npcs": {
                "major": int(2 * npc_multiplier),
                "minor": int(4 * npc_multiplier),
                "challenge_ratings": [base_cr, base_cr + 1],
                "species": ["human", "elf", "dwarf", "halfling"],
                "roles": ["ally", "neutral", "merchant", "guard"]
            },
            "monsters": {
                "types": int(2 * monster_multiplier),
                "quantities": [2, 1, 3],
                "challenge_ratings": [base_cr, base_cr + 1, base_cr - 1],
                "creature_types": ["humanoid", "beast", "undead"]
            },
            "special_considerations": {
                "custom_species": [],
                "custom_classes": [],
                "cultural_backgrounds": ["local", "foreign"]
            }
        }
    
    async def _generate_chapter_npcs(self, campaign_data: Dict[str, Any], 
                                   chapter_data: Dict[str, Any], 
                                   npc_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate NPCs for the chapter based on requirements."""
        npcs = []
        
        # Generate major NPCs
        for i in range(npc_requirements.get("major", 2)):
            campaign_context = self._build_character_context(
                campaign_data, chapter_data, "npc", "major", npc_requirements
            )
            npc = await self.character_client.generate_character("npc", campaign_context)
            npc["importance"] = "major"
            npcs.append(npc)
        
        # Generate minor NPCs
        for i in range(npc_requirements.get("minor", 4)):
            campaign_context = self._build_character_context(
                campaign_data, chapter_data, "npc", "minor", npc_requirements
            )
            npc = await self.character_client.generate_character("npc", campaign_context)
            npc["importance"] = "minor"
            npcs.append(npc)
        
        return npcs
    
    async def _generate_chapter_monsters(self, campaign_data: Dict[str, Any], 
                                       chapter_data: Dict[str, Any], 
                                       monster_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate monsters for the chapter based on requirements."""
        monsters = []
        
        monster_types = monster_requirements.get("types", 2)
        quantities = monster_requirements.get("quantities", [2, 1])
        challenge_ratings = monster_requirements.get("challenge_ratings", [1, 2])
        
        for i in range(monster_types):
            quantity = quantities[i] if i < len(quantities) else 1
            cr = challenge_ratings[i] if i < len(challenge_ratings) else 1
            
            campaign_context = self._build_character_context(
                campaign_data, chapter_data, "monster", "combat", monster_requirements
            )
            campaign_context["challenge_rating"] = cr
            
            # Generate multiple of the same monster type if needed
            for j in range(quantity):
                monster = await self.character_client.generate_character("monster", campaign_context)
                monster["encounter_group"] = i
                monster["group_size"] = quantity
                monsters.append(monster)
        
        return monsters
    
    def _build_character_context(self, campaign_data: Dict[str, Any], 
                               chapter_data: Dict[str, Any], 
                               creation_type: str, 
                               importance: str,
                               requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Build context for character generation request."""
        context = {
            "genre": campaign_data.get("genre", "fantasy"),
            "theme": campaign_data.get("theme", "standard_fantasy"),
            "complexity": campaign_data.get("complexity", "medium"),
            "party_level": campaign_data.get("party_level", 1),
            "party_size": campaign_data.get("party_size", 4),
            "chapter_title": chapter_data.get("title", ""),
            "chapter_themes": chapter_data.get("themes", []),
            "narrative_role": importance,
            "creation_type": creation_type
        }
        
        # Add requirements-specific context
        if creation_type == "npc":
            context.update({
                "available_species": requirements.get("species", []),
                "possible_roles": requirements.get("roles", []),
                "custom_species": requirements.get("custom_species", []),
                "cultural_backgrounds": requirements.get("cultural_backgrounds", [])
            })
        elif creation_type == "monster":
            context.update({
                "creature_types": requirements.get("creature_types", []),
                "custom_creatures": requirements.get("custom_creatures", [])
            })
        
        return context


# ============================================================================
# CAMPAIGN GENERATOR FACTORY
# ============================================================================

class CampaignGeneratorFactory:
    """
    Factory class for creating and managing all campaign generators.
    Provides unified interface for campaign content generation.
    """
    
    def __init__(self, llm_service: LLMService, settings: Optional[Settings] = None):
        self.llm_service = llm_service
        self.settings = settings
        
        # Initialize all generators
        self.campaign_generator = CampaignGenerator(llm_service, settings)
        self.skeleton_generator = CampaignSkeletonGenerator(llm_service, settings)
        self.chapter_generator = ChapterContentGenerator(llm_service, settings)
        self.theme_generator = SettingThemeGenerator(llm_service, settings)
        self.experiment_generator = PsychologicalExperimentGenerator(llm_service, settings)
        self.adaptive_generator = AdaptiveCampaignGenerator(llm_service, settings)
    
    async def generate_complete_campaign(self, concept: str, genre: CampaignGenre = CampaignGenre.FANTASY,
                                       complexity: CampaignComplexity = CampaignComplexity.MEDIUM,
                                       session_count: int = 10, themes: List[str] = None,
                                       generate_skeleton: bool = True,
                                       generate_first_chapters: int = 3) -> Dict[str, Any]:
        """
        Generate a complete campaign with skeleton and initial chapters.
        One-stop method for comprehensive campaign creation.
        """
        
        logger.info(f"Generating complete campaign from concept: {concept[:50]}...")
        
        # Generate base campaign
        campaign_data = await self.campaign_generator.generate_campaign_from_concept(
            concept, genre, complexity, session_count, themes
        )
        
        complete_campaign = {
            "campaign": campaign_data,
            "skeleton": None,
            "chapters": [],
            "generation_summary": {
                "concept": concept,
                "genre": genre.value,
                "complexity": complexity.value,
                "session_count": session_count,
                "themes": themes or [],
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        # Generate skeleton if requested
        if generate_skeleton:
            try:
                skeleton_data = await self.skeleton_generator.generate_campaign_skeleton(
                    campaign_data["title"],
                    campaign_data["description"],
                    campaign_data.get("themes", []),
                    session_count
                )
                complete_campaign["skeleton"] = skeleton_data
            except Exception as e:
                logger.warning(f"Skeleton generation failed: {e}")
                complete_campaign["skeleton"] = {"error": str(e)}
        
        # Generate initial chapters if requested
        if generate_first_chapters > 0 and complete_campaign["skeleton"]:
            chapter_outlines = complete_campaign["skeleton"].get("chapter_outlines", [])
            chapters_to_generate = min(generate_first_chapters, len(chapter_outlines))
            
            for i in range(chapters_to_generate):
                try:
                    chapter_outline = chapter_outlines[i]
                    chapter_content = await self.chapter_generator.generate_chapter_content(
                        campaign_data["title"],
                        campaign_data["description"],
                        chapter_outline["title"],
                        chapter_outline["summary"],
                        campaign_data.get("themes", [])
                    )
                    complete_campaign["chapters"].append({
                        "chapter_number": i + 1,
                        "outline": chapter_outline,
                        "content": chapter_content
                    })
                except Exception as e:
                    logger.warning(f"Chapter {i+1} generation failed: {e}")
                    complete_campaign["chapters"].append({
                        "chapter_number": i + 1,
                        "outline": chapter_outlines[i] if i < len(chapter_outlines) else {},
                        "content": {"error": str(e)}
                    })
        
        complete_campaign["generation_summary"]["chapters_generated"] = len(complete_campaign["chapters"])
        complete_campaign["generation_summary"]["skeleton_generated"] = complete_campaign["skeleton"] is not None
        
        return complete_campaign
    
    def get_generator(self, generator_type: str):
        """Get specific generator by type."""
        
        generators = {
            "campaign": self.campaign_generator,
            "skeleton": self.skeleton_generator,
            "chapter": self.chapter_generator,
            "theme": self.theme_generator,
            "experiment": self.experiment_generator,
            "adaptive": self.adaptive_generator
        }
        
        return generators.get(generator_type)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if all generators are functioning properly."""
        
        health_status = {
            "factory_status": "healthy",
            "llm_service": "connected" if self.llm_service else "disconnected",
            "generators": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Test each generator
        generator_names = ["campaign", "skeleton", "chapter", "theme", "experiment", "adaptive"]
        
        for name in generator_names:
            generator = self.get_generator(name)
            health_status["generators"][name] = {
                "status": "initialized" if generator else "missing",
                "class": generator.__class__.__name__ if generator else None
            }
        
        return health_status


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def create_campaign_generator_factory(llm_service: LLMService, settings: Optional[Settings] = None) -> CampaignGeneratorFactory:
    """Create and return a campaign generator factory instance."""
    return CampaignGeneratorFactory(llm_service, settings)

async def generate_campaign_quick(llm_service: LLMService, concept: str, **kwargs) -> Dict[str, Any]:
    """Quick campaign generation function for simple use cases."""
    factory = create_campaign_generator_factory(llm_service)
    return await factory.campaign_generator.generate_campaign_from_concept(concept, **kwargs)