"""
LLM Mass NPC Advisor Module

Uses LLM to make suggestions for groups of NPCs, settlements, organizations, and social encounters.
Provides intelligent NPC composition based on campaign themes, environments, and social situations.
Works in conjunction with LLMNPCAdvisor for detailed individual NPC creation.
"""

import json
import datetime
import re
import random
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

try:
    from backend.core.npc.llm_npc_advisor import LLMNPCAdvisor
    from backend.core.npc.abstract_npc import AbstractNPCAdvisor
    from backend.core.services.ollama_service import OllamaService
except ImportError:
    # Fallback for development
    class LLMNPCAdvisor:
        def __init__(self, llm_service=None, data_path=None): pass
    
    class AbstractNPCAdvisor:
        """Abstract base class placeholder"""
        pass
        
    class OllamaService:
        def __init__(self): pass
        def generate(self, prompt): return "LLM service not available"


class LLMMassNPCAdvisor(AbstractNPCAdvisor):
    """
    Provides AI-powered assistance for creating groups of NPCs for social encounters and settlements.
    
    This class integrates with Language Learning Models (LLMs) to suggest appropriate
    combinations of NPCs based on campaign themes, social contexts, and worldbuilding needs.
    It works alongside LLMNPCAdvisor which focuses on individual NPC creation.
    """

    def __init__(self, llm_service=None, data_path: str = None, npc_advisor=None):
        """
        Initialize the LLM mass NPC advisor.
        
        Args:
            llm_service: LLM service client for generating responses
            data_path: Optional path to NPC data
            npc_advisor: Optional LLMNPCAdvisor instance for individual NPC creation
        """
        # Initialize LLM service
        self.llm_service = llm_service or OllamaService()
            
        # Set up paths and data
        self.data_path = Path(data_path) if data_path else Path("backend/data/npcs")
        self.npc_advisor = npc_advisor or LLMNPCAdvisor(llm_service, data_path)
        self._load_reference_data()

    def _load_reference_data(self):
        """Load reference data for NPC creation."""
        try:
            # Load NPC archetypes
            archetype_path = self.data_path / "npc_archetypes.json"
            if archetype_path.exists():
                with open(archetype_path, "r") as f:
                    self.archetype_data = json.load(f)
            else:
                self.archetype_data = {}
                
            # Load profession reference data
            profession_path = self.data_path / "professions.json"
            if profession_path.exists():
                with open(profession_path, "r") as f:
                    self.profession_data = json.load(f)
            else:
                self.profession_data = {}
                
            # Load culture/faction data
            culture_path = self.data_path / "cultures.json"
            if culture_path.exists():
                with open(culture_path, "r") as f:
                    self.culture_data = json.load(f)
            else:
                self.culture_data = {}
                
        except Exception as e:
            print(f"Error loading reference data: {e}")
            self.archetype_data = {}
            self.profession_data = {}
            self.culture_data = {}

    def generate_adventuring_party(self, level_range: Tuple[int, int] = (1, 10),
                                  party_size: int = 4,
                                  alignment_tendency: str = None,
                                  campaign_theme: str = None) -> Dict[str, Any]:
        """
        Generate a cohesive adventuring party of NPCs.
        
        Args:
            level_range: Range of levels for party members (min, max)
            party_size: Number of NPCs in the party
            alignment_tendency: Optional alignment tendency for the party
            campaign_theme: Optional campaign theme to influence party design
            
        Returns:
            Dict[str, Any]: Generated NPC adventuring party
        """
        min_level, max_level = level_range
        
        # Build context for LLM
        context = f"Party Size: {party_size} NPCs\n"
        context += f"Level Range: {min_level} to {max_level}\n"
        
        if alignment_tendency:
            context += f"Alignment Tendency: {alignment_tendency}\n"
            
        if campaign_theme:
            context += f"Campaign Theme: {campaign_theme}\n"
            
        # Create prompt for adventuring party generation
        prompt = self._create_prompt(
            "generate adventuring party",
            context + "\n"
            f"Create a cohesive adventuring party of {party_size} NPCs with complementary abilities and personalities.\n"
            "For the party as a whole, provide:\n"
            "1. A name for the adventuring group\n"
            "2. Their reputation and typical contracts/quests\n"
            "3. Group dynamics and internal relationships\n"
            "4. A brief history of their notable accomplishments\n\n"
            "For each NPC member, provide:\n"
            "1. Name, race, class, and level\n"
            "2. Brief physical description and personality\n"
            "3. Motivations and personal goals\n"
            "4. Signature abilities or equipment\n"
            "5. Role in the party and relationship with other members\n\n"
            "Make sure each character has distinctive traits and conflicts that drive their interactions."
        )
        
        try:
            # Generate adventuring party with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured party data
            party_data = self._parse_adventuring_party(response)
            
            return {
                "success": True,
                "party_data": party_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate adventuring party: {str(e)}"
            }

    def generate_settlement_npcs(self, settlement_type: str,
                              population_size: str,
                              culture: str = None,
                              notable_count: int = 5) -> Dict[str, Any]:
        """
        Generate a set of NPCs for a settlement, including notable figures and general populace.
        
        Args:
            settlement_type: Type of settlement (village, town, city, etc.)
            population_size: Size descriptor or approximate number
            culture: Optional cultural influence
            notable_count: Number of detailed notable NPCs to generate
            
        Returns:
            Dict[str, Any]: Settlement NPCs data
        """
        # Build context for LLM
        context = f"Settlement Type: {settlement_type}\n"
        context += f"Population Size: {population_size}\n"
        
        if culture:
            context += f"Culture: {culture}\n"
            
        context += f"Notable NPCs: {notable_count}\n"
        
        # Create prompt for settlement NPCs
        prompt = self._create_prompt(
            "generate settlement npcs",
            context + "\n"
            f"Create a diverse and interconnected group of NPCs for a {settlement_type}.\n"
            "For the settlement as a whole, provide:\n"
            "1. The settlement's name and brief description\n"
            "2. Major industries, resources, or specialties\n"
            "3. General atmosphere and attitude toward outsiders\n"
            "4. Current issues or tensions affecting the community\n\n"
            f"Create {notable_count} detailed notable NPCs who represent important figures, including:\n"
            "1. Leadership (mayor, council, etc.)\n"
            "2. Commerce (merchants, guild leaders)\n"
            "3. Services (innkeeper, blacksmith, healer)\n"
            "4. Religion/culture (priest, storyteller, elder)\n"
            "5. Protection (guard captain, militia leader)\n\n"
            "For each notable NPC, provide:\n"
            "- Name, race, age, and occupation\n"
            "- Personality and motivations\n"
            "- Connections to other NPCs\n"
            "- Secrets or special knowledge they possess\n"
            "- How they might interact with player characters\n\n"
            "Additionally, describe 3-5 general NPC types that make up the common population."
        )
        
        try:
            # Generate settlement NPCs with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured settlement NPC data
            settlement_data = self._parse_settlement_npcs(response, notable_count)
            
            return {
                "success": True,
                "settlement_data": settlement_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate settlement NPCs: {str(e)}"
            }

    def generate_faction(self, faction_type: str,
                        size: str = "medium",
                        alignment: str = None,
                        goals: List[str] = None) -> Dict[str, Any]:
        """
        Generate a faction with leadership structure, members, and motivations.
        
        Args:
            faction_type: Type of faction (guild, cult, noble house, etc.)
            size: Size of the faction (small, medium, large)
            alignment: Optional alignment tendency
            goals: Optional list of faction goals
            
        Returns:
            Dict[str, Any]: Faction data with membership structure
        """
        # Build context for LLM
        context = f"Faction Type: {faction_type}\n"
        context += f"Size: {size}\n"
        
        if alignment:
            context += f"Alignment: {alignment}\n"
            
        if goals:
            context += f"Goals: {', '.join(goals)}\n"
        
        # Create prompt for faction generation
        prompt = self._create_prompt(
            "generate faction",
            context + "\n"
            f"Create a detailed {faction_type} with a compelling structure, goals, and key members.\n"
            "For the faction as a whole, provide:\n"
            "1. Name and symbol/identifying features\n"
            "2. History and founding purpose\n"
            "3. Current objectives and methods\n"
            "4. Resources and typical locations\n"
            "5. Allies, rivals, and enemies\n\n"
            "Describe the faction's organizational structure with:\n"
            "1. Leadership hierarchy (3-4 key leaders)\n"
            "2. Mid-level operatives or lieutenants (4-5 examples)\n"
            "3. Typical rank-and-file members\n"
            "4. Recruitment and advancement methods\n\n"
            "For each key NPC, include:\n"
            "- Name, position, and brief description\n"
            "- Personality and motivations\n"
            "- Special abilities or resources\n"
            "- Internal relationships and conflicts\n\n"
            "Also provide plot hooks for how this faction might interact with player characters."
        )
        
        try:
            # Generate faction with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured faction data
            faction_data = self._parse_faction(response)
            
            return {
                "success": True,
                "faction_data": faction_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate faction: {str(e)}"
            }

    def generate_social_encounter(self, situation_type: str,
                               importance: str = "moderate",
                               npc_count: int = 4,
                               setting: str = None) -> Dict[str, Any]:
        """
        Generate a social encounter with NPCs, including dynamics and possible outcomes.
        
        Args:
            situation_type: Type of social situation (negotiation, celebration, etc.)
            importance: Importance of the encounter (minor, moderate, major)
            npc_count: Number of key NPCs involved
            setting: Optional physical setting for the encounter
            
        Returns:
            Dict[str, Any]: Social encounter data
        """
        # Build context for LLM
        context = f"Situation Type: {situation_type}\n"
        context += f"Importance: {importance}\n"
        context += f"Key NPCs: {npc_count}\n"
        
        if setting:
            context += f"Setting: {setting}\n"
        
        # Create prompt for social encounter
        prompt = self._create_prompt(
            "generate social encounter",
            context + "\n"
            f"Create an engaging social encounter of {importance} importance centered around a {situation_type}.\n"
            "For the overall encounter, provide:\n"
            "1. Context and immediate situation\n"
            "2. Stakes and possible consequences\n"
            "3. Atmosphere and environmental factors\n"
            "4. Potential complications or twists\n\n"
            f"Create {npc_count} key NPCs involved in this situation, including:\n"
            "1. Name, position, and brief description\n"
            "2. Goals and motivations for this encounter\n"
            "3. Attitude toward player characters\n"
            "4. Social tactics or approaches they'll use\n"
            "5. Information or resources they possess\n\n"
            "Provide 3-4 possible developments or outcomes based on player choices, and suggest\n"
            "skill checks or social approaches that might be effective in this situation."
        )
        
        try:
            # Generate social encounter with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured social encounter data
            encounter_data = self._parse_social_encounter(response, npc_count)
            
            return {
                "success": True,
                "encounter_data": encounter_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate social encounter: {str(e)}"
            }

    def generate_rival_party(self, player_party: List[Dict[str, Any]],
                          rivalry_intensity: str = "competitive",
                          history: str = None) -> Dict[str, Any]:
        """
        Generate a rival adventuring party tailored to challenge the player characters socially.
        
        Args:
            player_party: List of player character data dictionaries
            rivalry_intensity: Intensity of rivalry (friendly, competitive, hostile)
            history: Optional history between the parties
            
        Returns:
            Dict[str, Any]: Rival adventuring party data
        """
        # Calculate appropriate levels and party size
        player_levels = [pc.get("level", 1) for pc in player_party]
        avg_level = sum(player_levels) / len(player_levels)
        party_size = len(player_party)
        
        # Build context for LLM
        context = f"Player Party Size: {party_size}\n"
        context += f"Average Player Level: {avg_level:.1f}\n"
        context += f"Player Classes: {', '.join([pc.get('class', 'Unknown') for pc in player_party])}\n"
        context += f"Rivalry Intensity: {rivalry_intensity}\n"
        
        if history:
            context += f"History: {history}\n"
            
        # Create prompt for rival party generation
        prompt = self._create_prompt(
            "generate rival party",
            context + "\n"
            "Create a rival adventuring party that serves as an interesting foil to the player characters.\n"
            "For the rival party as a whole, provide:\n"
            "1. Name and reputation\n"
            "2. Overall theme and aesthetic\n"
            "3. Reason for rivalry with the player characters\n"
            "4. Tactics they use in social confrontations\n"
            "5. Shared history or notable interactions with the players\n\n"
            f"Create {party_size} individual NPCs that mirror or counter the player characters:\n"
            "For each rival NPC, provide:\n"
            "- Name, race, class, and personality\n"
            "- Brief description and signature traits\n"
            "- Special abilities or equipment\n"
            "- Specific relationship or attitude toward a particular PC\n"
            "- Goals that might conflict with the players'\n\n"
            "Also include 3-4 potential encounter scenarios where these rivals might appear."
        )
        
        try:
            # Generate rival party with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured rival party data
            rival_data = self._parse_rival_party(response, player_party)
            
            return {
                "success": True,
                "rival_party": rival_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate rival party: {str(e)}"
            }

    def generate_npc_network(self, central_theme: str,
                           network_size: int = 6,
                           complexity: str = "moderate") -> Dict[str, Any]:
        """
        Generate an interconnected network of NPCs with relationships and conflicts.
        
        Args:
            central_theme: Central theme or focus of the network
            network_size: Number of NPCs in the network
            complexity: Complexity of relationships (simple, moderate, complex)
            
        Returns:
            Dict[str, Any]: NPC network with relationships
        """
        # Build context for LLM
        context = f"Central Theme: {central_theme}\n"
        context += f"Network Size: {network_size} NPCs\n"
        context += f"Relationship Complexity: {complexity}\n"
        
        # Create prompt for NPC network
        prompt = self._create_prompt(
            "generate npc network",
            context + "\n"
            f"Create an interconnected network of {network_size} NPCs centered around a {central_theme}.\n"
            "For the network as a whole, provide:\n"
            "1. Overview of how these individuals are connected\n"
            "2. Central tensions or conflicts driving relationships\n"
            "3. Hidden connections or secrets linking members\n"
            "4. How this network might impact a campaign\n\n"
            f"For each of the {network_size} NPCs, provide:\n"
            "- Name, occupation, and brief description\n"
            "- Personality and key motivations\n"
            "- Position and influence within the network\n"
            "- Connections to at least 2 other NPCs (positive and negative)\n"
            "- Secrets or hidden agendas\n\n"
            "Include a relationship map describing connections between NPCs, including:\n"
            "- Allies and friends\n"
            "- Rivals and enemies\n"
            "- Family connections\n"
            "- Business or political relationships\n"
            "- Romantic entanglements\n\n"
            f"Make the relationships {complexity} in nature, with multiple layers and potential conflicts."
        )
        
        try:
            # Generate NPC network with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured network data
            network_data = self._parse_npc_network(response, network_size)
            
            return {
                "success": True,
                "network_data": network_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate NPC network: {str(e)}"
            }

    def generate_organization_hierarchy(self, org_type: str,
                                     leadership_count: int = 3,
                                     mid_level_count: int = 5,
                                     specialty: str = None) -> Dict[str, Any]:
        """
        Generate an organization with hierarchical structure and key members at each level.
        
        Args:
            org_type: Type of organization (military, religious, academic, etc.)
            leadership_count: Number of leadership NPCs to generate
            mid_level_count: Number of mid-level NPCs to generate
            specialty: Optional specialty or focus of the organization
            
        Returns:
            Dict[str, Any]: Organization hierarchy with key NPCs
        """
        # Build context for LLM
        context = f"Organization Type: {org_type}\n"
        context += f"Leadership Positions: {leadership_count}\n"
        context += f"Mid-level Positions: {mid_level_count}\n"
        
        if specialty:
            context += f"Specialty/Focus: {specialty}\n"
        
        # Create prompt for organization hierarchy
        prompt = self._create_prompt(
            "generate organization hierarchy",
            context + "\n"
            f"Create a detailed {org_type} organization with a clear hierarchical structure and key NPCs at each level.\n"
            "For the organization as a whole, provide:\n"
            "1. Name and founding purpose\n"
            "2. Size, scope, and areas of influence\n"
            "3. Resources and headquarters/locations\n"
            "4. Distinctive traditions or protocols\n"
            "5. Current goals and challenges\n\n"
            "Design the organizational structure with clear hierarchy:\n"
            f"1. Top leadership ({leadership_count} positions with NPCs)\n"
            f"2. Middle management ({mid_level_count} positions with NPCs)\n"
            "3. General description of rank-and-file members\n"
            "4. Any specialized branches or divisions\n\n"
            "For each NPC, include:\n"
            "- Name and position/title\n"
            "- Brief description and distinguishing traits\n"
            "- Areas of responsibility\n"
            "- Leadership style and relationships\n"
            "- Personal ambitions or agendas\n\n"
            "Also include 2-3 internal conflicts or power struggles affecting the organization."
        )
        
        try:
            # Generate organization with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured organization data
            organization_data = self._parse_organization(response, leadership_count, mid_level_count)
            
            return {
                "success": True,
                "organization_data": organization_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate organization: {str(e)}"
            }

    def generate_npc_evolution(self, initial_npc: Dict[str, Any],
                            time_period: str,
                            life_events: List[str] = None) -> Dict[str, Any]:
        """
        Generate an NPC's evolution over time based on significant life events.
        
        Args:
            initial_npc: Initial NPC data
            time_period: Time period of evolution (months, years, decades)
            life_events: Optional list of significant events affecting the NPC
            
        Returns:
            Dict[str, Any]: NPC evolution stages
        """
        # Build context for LLM
        npc_name = initial_npc.get("name", "Unknown NPC")
        
        context = f"NPC: {npc_name}\n"
        context += f"Initial Details: {initial_npc.get('description', 'No description')}\n"
        context += f"Time Period: {time_period}\n"
        
        if life_events:
            context += "Life Events:\n"
            for event in life_events:
                context += f"- {event}\n"
        
        # Create prompt for NPC evolution
        prompt = self._create_prompt(
            "generate npc evolution",
            context + "\n"
            f"Create a character evolution for {npc_name} over {time_period}, showing how they change over time.\n"
            "Divide their evolution into 3-4 distinct stages, and for each stage, provide:\n\n"
            "1. Time period and circumstances\n"
            "2. Physical and personality changes\n"
            "3. New skills, abilities, or resources acquired\n"
            "4. Relationships formed or broken\n"
            "5. Goals and motivations at this stage\n"
            "6. Notable actions or decisions made\n\n"
            "Show a clear progression from the initial state to the final outcome, with meaningful\n"
            "character development influenced by experiences and choices.\n"
            "Include one major turning point that significantly alters their path."
        )
        
        try:
            # Generate NPC evolution with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured evolution data
            evolution_data = self._parse_npc_evolution(response)
            
            # Include original NPC data
            evolution_data["initial_npc"] = initial_npc
            
            return {
                "success": True,
                "npc_evolution": evolution_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate NPC evolution: {str(e)}"
            }

    def generate_cultural_npcs(self, culture_name: str,
                            npc_count: int = 5,
                            cultural_roles: List[str] = None) -> Dict[str, Any]:
        """
        Generate NPCs from a specific culture, emphasizing cultural elements and roles.
        
        Args:
            culture_name: Name of the culture
            npc_count: Number of NPCs to generate
            cultural_roles: Optional list of cultural roles to include
            
        Returns:
            Dict[str, Any]: Cultural NPCs with cultural elements
        """
        # Build context for LLM
        context = f"Culture: {culture_name}\n"
        context += f"NPC Count: {npc_count}\n"
        
        if cultural_roles:
            context += f"Cultural Roles: {', '.join(cultural_roles)}\n"
        
        # Create prompt for cultural NPCs
        prompt = self._create_prompt(
            "generate cultural npcs",
            context + "\n"
            f"Create {npc_count} distinct NPCs from {culture_name} culture that showcase its values and traditions.\n"
            "First, provide an overview of the culture, including:\n"
            "1. Core values and beliefs\n"
            "2. Social structure and important roles\n"
            "3. Traditions, customs, and taboos\n"
            "4. Distinctive clothing, appearance, or symbols\n"
            "5. Attitudes toward outsiders and other cultures\n\n"
            f"Then, create {npc_count} NPCs who represent different aspects of this culture:\n"
            "For each NPC, include:\n"
            "- Name and role/position within the culture\n"
            "- Brief physical description and personality\n"
            "- How they specifically embody cultural values\n"
            "- Distinctive cultural traits, speech patterns, or behaviors\n"
            "- Their view on cultural traditions (traditional or progressive)\n"
            "- A cultural custom or ritual they're particularly associated with\n\n"
            "Make each NPC feel authentically part of this culture while avoiding stereotypes."
        )
        
        try:
            # Generate cultural NPCs with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response into structured cultural NPC data
            cultural_data = self._parse_cultural_npcs(response, npc_count)
            
            return {
                "success": True,
                "culture_data": cultural_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate cultural NPCs: {str(e)}"
            }

    # Helper methods

    def _create_prompt(self, task: str, content: str) -> str:
        """Create a structured prompt for the LLM."""
        return f"Task: {task}\n\n{content}"
    
    # Parser methods
    
    def _parse_adventuring_party(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for adventuring party generation."""
        party_data = {
            "name": "Unknown Party",
            "reputation": "",
            "group_dynamics": "",
            "accomplishments": "",
            "members": []
        }
        
        # Try to extract party name
        name_match = re.search(r"(?:Party|Group|Company|Band)(?:\s+Name)?:\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            party_data["name"] = name_match.group(1).strip()
            
        # Try to extract reputation
        reputation_match = re.search(r"(?:Reputation|Known\s+For)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if reputation_match:
            party_data["reputation"] = reputation_match.group(1).strip()
            
        # Try to extract group dynamics
        dynamics_match = re.search(r"(?:Group\s+Dynamics|Relationships|Interaction)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if dynamics_match:
            party_data["group_dynamics"] = dynamics_match.group(1).strip()
            
        # Try to extract accomplishments
        accomplishments_match = re.search(r"(?:Accomplishments|History|Notable\s+Feats|Achievements)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if accomplishments_match:
            party_data["accomplishments"] = accomplishments_match.group(1).strip()
        
        # Try to find individual NPC blocks
        # Look for numbered members or headers like "Member 1:" or character names followed by details
        member_blocks = re.findall(r"(?:Member|Character|NPC)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Member|Character|NPC\s+\d+:)[^\n]+)*)", response, re.IGNORECASE)
        
        if not member_blocks:
            # Try to find numbered entries
            member_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", response)
            
        if not member_blocks:
            # Try to find sections separated by double newlines
            paragraphs = re.split(r'\n\s*\n', response)
            # Skip the first paragraph assuming it's about the group as a whole
            if len(paragraphs) > 1:
                member_blocks = paragraphs[1:]
        
        for block in member_blocks:
            member = {
                "name": "Unknown Member",
                "description": block.strip(),
                "class": "",
                "race": "",
                "level": 1,
                "personality": "",
                "motivations": "",
                "abilities": [],
                "role": ""
            }
            
            # Try to extract name, race, class, and level
            header_match = re.search(r"^([^,\n]+)(?:,\s*|\s+\-\s*|\s+is\s+a\s+|\s+the\s+)(?:a\s+)?([^,\n]+)(?:,\s*|\s+)(?:level\s+)?(\d+)?(?:\s+)?([^,\n]+)?", block, re.IGNORECASE)
            if header_match:
                member["name"] = header_match.group(1).strip()
                
                # Determine which group contains race and which contains class
                group2 = header_match.group(2).strip() if header_match.group(2) else ""
                group4 = header_match.group(4).strip() if header_match.group(4) else ""
                
                # Common D&D races and classes for identification
                races = ["human", "elf", "dwarf", "halfling", "gnome", "half-elf", "half-orc", "tiefling", "dragonborn"]
                classes = ["fighter", "wizard", "cleric", "rogue", "bard", "barbarian", "monk", "paladin", "ranger", "sorcerer", "warlock", "druid", "artificer"]
                
                # Try to determine race and class
                if group2.lower() in races:
                    member["race"] = group2
                    if group4.lower() in classes:
                        member["class"] = group4
                elif group2.lower() in classes:
                    member["class"] = group2
                    if group4.lower() in races:
                        member["race"] = group4
                else:
                    # If we can't determine clearly, make a best guess
                    if group4:
                        member["race"] = group2
                        member["class"] = group4
                    else:
                        member["class"] = group2
                        
                # Extract level if present
                if header_match.group(3):
                    try:
                        member["level"] = int(header_match.group(3))
                    except ValueError:
                        pass
            
            # Try to extract personality
            personality_match = re.search(r"(?:Personality|Character)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if personality_match:
                member["personality"] = personality_match.group(1).strip()
                
            # Try to extract motivations
            motivation_match = re.search(r"(?:Motivation|Goal|Desire|Aim)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if motivation_match:
                member["motivations"] = motivation_match.group(1).strip()
                
            # Try to extract abilities or equipment
            abilities_match = re.search(r"(?:Abilities|Equipment|Skills|Signature|Special)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if abilities_match:
                abilities_text = abilities_match.group(1).strip()
                # Split by commas or bullet points
                ability_items = re.findall(r"(?:[-•*]\s*|^|\n\s*)([^,\n-•*][^,\n]*)", abilities_text)
                if ability_items:
                    member["abilities"] = [item.strip() for item in ability_items if item.strip()]
                else:
                    member["abilities"] = [abilities_text]
                    
            # Try to extract role
            role_match = re.search(r"(?:Role|Position|Function)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if role_match:
                member["role"] = role_match.group(1).strip()
                
            party_data["members"].append(member)
            
        return party_data
    
    def _parse_settlement_npcs(self, response: str, notable_count: int) -> Dict[str, Any]:
        """Parse LLM response for settlement NPCs."""
        settlement_data = {
            "name": "Unknown Settlement",
            "description": "",
            "industries": [],
            "atmosphere": "",
            "issues": [],
            "notable_npcs": [],
            "common_npcs": []
        }
        
        # Try to extract settlement name
        name_match = re.search(r"(?:Settlement|Village|Town|City)(?:\s+Name)?:\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            settlement_data["name"] = name_match.group(1).strip()
            
        # Try to extract description
        desc_match = re.search(r"(?:Description|Overview|About)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if desc_match:
            settlement_data["description"] = desc_match.group(1).strip()
            
        # Try to extract industries
        industries_match = re.search(r"(?:Industries|Resources|Economy|Specialties)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if industries_match:
            industries_text = industries_match.group(1).strip()
            # Split by commas or bullet points
            industry_items = re.findall(r"(?:[-•*]\s*|^|\n\s*)([^,\n-•*][^,\n]*)", industries_text)
            if industry_items:
                settlement_data["industries"] = [item.strip() for item in industry_items if item.strip()]
            else:
                settlement_data["industries"] = [industries_text]
                
        # Try to extract atmosphere
        atmosphere_match = re.search(r"(?:Atmosphere|Attitude|Demeanor|Feel)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if atmosphere_match:
            settlement_data["atmosphere"] = atmosphere_match.group(1).strip()
            
        # Try to extract issues
        issues_match = re.search(r"(?:Issues|Tensions|Problems|Challenges|Conflicts)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if issues_match:
            issues_text = issues_match.group(1).strip()
            # Split by bullet points or numbers
            issue_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*|^|\n\s*)([^,\n-•*\d\.][^,\n]*)", issues_text)
            if issue_items:
                settlement_data["issues"] = [item.strip() for item in issue_items if item.strip()]
            else:
                settlement_data["issues"] = [issues_text]
        
        # Try to find notable NPC blocks
        notable_blocks = re.findall(r"(?:Notable NPC|Leader|Important Figure|Key Figure)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Notable NPC|Leader|Important Figure|Key Figure\s+\d+:)[^\n]+)*)", response, re.IGNORECASE)
        
        if not notable_blocks:
            # Try to find numbered entries
            notable_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", response)
            
        for i, block in enumerate(notable_blocks):
            if i >= notable_count:
                break
                
            npc = {
                "name": f"Notable NPC {i+1}",
                "occupation": "",
                "description": block.strip(),
                "personality": "",
                "connections": [],
                "secrets": "",
                "interactions": ""
            }
            
            # Try to extract name and occupation
            header_match = re.search(r"^([^,\n]+)(?:,\s*|\s+\-\s*|\s+is\s+(?:the|a)\s+)?([^,\n]+)?", block, re.IGNORECASE)
            if header_match:
                npc["name"] = header_match.group(1).strip()
                if header_match.group(2):
                    npc["occupation"] = header_match.group(2).strip()
                    
            # Try to extract personality
            personality_match = re.search(r"(?:Personality|Character|Demeanor)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if personality_match:
                npc["personality"] = personality_match.group(1).strip()
                
            # Try to extract connections
            connections_match = re.search(r"(?:Connection|Relationship|Network|Ties)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if connections_match:
                connections_text = connections_match.group(1).strip()
                # Split by bullet points or semicolons
                connection_items = re.findall(r"(?:[-•*]\s*|^|\n\s*)([^;\n-•*][^;\n]*)", connections_text)
                if connection_items:
                    npc["connections"] = [item.strip() for item in connection_items if item.strip()]
                else:
                    npc["connections"] = [connections_text]
                    
            # Try to extract secrets
            secrets_match = re.search(r"(?:Secret|Hidden|Unknown)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if secrets_match:
                npc["secrets"] = secrets_match.group(1).strip()
                
            # Try to extract interactions
            interactions_match = re.search(r"(?:Interaction|Player|PC)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if interactions_match:
                npc["interactions"] = interactions_match.group(1).strip()
                
            settlement_data["notable_npcs"].append(npc)
            
        # Try to find common NPC types
        common_match = re.search(r"(?:Common|General|Population|Regular)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if common_match:
            common_text = common_match.group(1).strip()
            # Try to split by bullet points or numbers
            common_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", common_text, re.MULTILINE)
            if common_items:
                for item in common_items:
                    if item.strip():
                        settlement_data["common_npcs"].append({
                            "type": item.strip(),
                            "description": ""
                        })
            else:
                # Split by periods or semicolons
                common_sentences = re.split(r'[.;]', common_text)
                for sentence in common_sentences:
                    if sentence.strip():
                        settlement_data["common_npcs"].append({
                            "type": sentence.strip(),
                            "description": ""
                        })
        
        return settlement_data
    
    def _parse_faction(self, response: str) -> Dict[str, Any]:
        """Parse LLM response for faction generation."""
        faction_data = {
            "name": "Unknown Faction",
            "symbol": "",
            "history": "",
            "objectives": [],
            "resources": [],
            "allies_rivals": {},
            "leadership": [],
            "mid_level": [],
            "rank_file": "",
            "recruitment": "",
            "plot_hooks": []
        }
        
        # Try to extract faction name
        name_match = re.search(r"(?:Name|Faction|Organization)(?:\s+Name)?:\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            faction_data["name"] = name_match.group(1).strip()
            
        # Try to extract symbol/identifying features
        symbol_match = re.search(r"(?:Symbol|Identifying Features|Emblem|Sigil)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if symbol_match:
            faction_data["symbol"] = symbol_match.group(1).strip()
            
        # Try to extract history
        history_match = re.search(r"(?:History|Founding|Origin|Background)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if history_match:
            faction_data["history"] = history_match.group(1).strip()
            
        # Try to extract objectives
        objectives_match = re.search(r"(?:Objectives|Goals|Aims|Current|Methods)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if objectives_match:
            objectives_text = objectives_match.group(1).strip()
            # Split by bullet points or numbers
            objective_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", objectives_text, re.MULTILINE)
            if objective_items:
                faction_data["objectives"] = [item.strip() for item in objective_items if item.strip()]
            else:
                # Split by periods or semicolons
                objective_sentences = re.split(r'[.;]', objectives_text)
                faction_data["objectives"] = [s.strip() for s in objective_sentences if s.strip()]
                
        # Try to extract resources
        resources_match = re.search(r"(?:Resources|Assets|Locations|Holdings)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if resources_match:
            resources_text = resources_match.group(1).strip()
            # Split by bullet points or commas
            resource_items = re.findall(r"(?:[-•*]\s*|^|\n\s*)([^,\n-•*][^,\n]*)", resources_text)
            if resource_items:
                faction_data["resources"] = [item.strip() for item in resource_items if item.strip()]
            else:
                faction_data["resources"] = [resources_text]
                
        # Try to extract allies and rivals
        allies_match = re.search(r"(?:Allies|Rivals|Enemies|Relations|Relationships)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if allies_match:
            allies_text = allies_match.group(1).strip()
            
            # Try to identify allies and enemies separately
            allies = []
            enemies = []
            
            ally_items = re.findall(r"(?:Ally|Alliance|Friendly|Aligned)(?:[^:]*?):\s*([^\n]+)", allies_text, re.IGNORECASE)
            if ally_items:
                for item in ally_items:
                    allies.extend([a.strip() for a in re.split(r'[,;]', item) if a.strip()])
                    
            enemy_items = re.findall(r"(?:Enemy|Rival|Hostile|Opposition|Opponent)(?:[^:]*?):\s*([^\n]+)", allies_text, re.IGNORECASE)
            if enemy_items:
                for item in enemy_items:
                    enemies.extend([e.strip() for e in re.split(r'[,;]', item) if e.strip()])
                    
            if not allies and not enemies:
                # If not clearly separated, put everything in one category
                relation_items = re.findall(r"(?:[-•*]\s*|^|\n\s*)([^,\n-•*][^,\n]*)", allies_text)
                if relation_items:
                    faction_data["allies_rivals"]["relations"] = [item.strip() for item in relation_items if item.strip()]
                else:
                    faction_data["allies_rivals"]["relations"] = [allies_text]
            else:
                if allies:
                    faction_data["allies_rivals"]["allies"] = allies
                if enemies:
                    faction_data["allies_rivals"]["enemies"] = enemies
        
        # Try to find leadership NPCs
        leadership_blocks = re.findall(r"(?:Leader|Head|Chief|Commander|Boss)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Leader|Head|Chief|Commander|Boss\s+\d+:)[^\n]+)*)", response, re.IGNORECASE)
        
        if not leadership_blocks:
            # Try to find leadership section and parse from there
            leadership_section = re.search(r"(?:Leadership|Leaders|Hierarchy|Command)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if leadership_section:
                leadership_text = leadership_section.group(1).strip()
                # Try to split by bullet points or numbers
                leadership_blocks = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+(?:\n(?![-•*]|\d+\.)[^\n]+)*)", leadership_text, re.MULTILINE)
                
        for block in leadership_blocks:
            leader = {
                "name": "Unknown Leader",
                "position": "",
                "description": block.strip(),
                "personality": "",
                "ambitions": ""
            }
            
            # Try to extract name and position
            header_match = re.search(r"^([^,\n]+)(?:,\s*|\s+\-\s*|\s+is\s+(?:the|a)\s+)?([^,\n]+)?", block, re.IGNORECASE)
            if header_match:
                leader["name"] = header_match.group(1).strip()
                if header_match.group(2):
                    leader["position"] = header_match.group(2).strip()
                    
            # Try to extract personality
            personality_match = re.search(r"(?:Personality|Character|Demeanor)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if personality_match:
                leader["personality"] = personality_match.group(1).strip()
                
            # Try to extract ambitions
            ambitions_match = re.search(r"(?:Ambition|Goal|Agenda|Aim)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if ambitions_match:
                leader["ambitions"] = ambitions_match.group(1).strip()
                
            faction_data["leadership"].append(leader)
            
        # Try to find mid-level operatives
        midlevel_blocks = re.findall(r"(?:Lieutenant|Officer|Mid[- ]Level|Second[- ]in[- ]Command)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Lieutenant|Officer|Mid[- ]Level|Second[- ]in[- ]Command\s+\d+:)[^\n]+)*)", response, re.IGNORECASE)
        
        if not midlevel_blocks:
            # Try to find mid-level section and parse from there
            midlevel_section = re.search(r"(?:Mid[- ]Level|Lieutenants|Officers)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
            if midlevel_section:
                midlevel_text = midlevel_section.group(1).strip()
                # Try to split by bullet points or numbers
                midlevel_blocks = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+(?:\n(?![-•*]|\d+\.)[^\n]+)*)", midlevel_text, re.MULTILINE)
                
        for block in midlevel_blocks:
            officer = {
                "name": "Unknown Officer",
                "position": "",
                "description": block.strip()
            }
            
            # Try to extract name and position
            header_match = re.search(r"^([^,\n]+)(?:,\s*|\s+\-\s*|\s+is\s+(?:the|a)\s+)?([^,\n]+)?", block, re.IGNORECASE)
            if header_match:
                officer["name"] = header_match.group(1).strip()
                if header_match.group(2):
                    officer["position"] = header_match.group(2).strip()
                    
            faction_data["mid_level"].append(officer)
            
        # Try to extract rank and file information
        rank_match = re.search(r"(?:Rank[- ]and[- ]File|Members|Regular|Common|Typical)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if rank_match:
            faction_data["rank_file"] = rank_match.group(1).strip()
            
        # Try to extract recruitment methods
        recruit_match = re.search(r"(?:Recruit|Advancement|Joining|Membership)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if recruit_match:
            faction_data["recruitment"] = recruit_match.group(1).strip()
            
        # Try to extract plot hooks
        hooks_match = re.search(r"(?:Plot Hooks|Adventure|Campaign|Story|Scenario)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if hooks_match:
            hooks_text = hooks_match.group(1).strip()
            # Split by bullet points or numbers
            hook_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", hooks_text, re.MULTILINE)
            if hook_items:
                faction_data["plot_hooks"] = [item.strip() for item in hook_items if item.strip()]
            else:
                # Split by periods
                hook_sentences = re.split(r'\.', hooks_text)
                faction_data["plot_hooks"] = [s.strip() for s in hook_sentences if s.strip()]
        
        return faction_data
    
    def _parse_social_encounter(self, response: str, npc_count: int) -> Dict[str, Any]:
        """Parse LLM response for social encounter generation."""
        encounter_data = {
            "context": "",
            "stakes": "",
            "atmosphere": "",
            "complications": [],
            "npcs": [],
            "possible_outcomes": [],
            "skill_checks": []
        }
        
        # Try to extract context
        context_match = re.search(r"(?:Context|Situation|Background|Setting)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if context_match:
            encounter_data["context"] = context_match.group(1).strip()
            
        # Try to extract stakes
        stakes_match = re.search(r"(?:Stakes|Consequences|Importance|Outcome)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if stakes_match:
            encounter_data["stakes"] = stakes_match.group(1).strip()
            
        # Try to extract atmosphere
        atmosphere_match = re.search(r"(?:Atmosphere|Environment|Mood|Setting|Ambiance)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if atmosphere_match:
            encounter_data["atmosphere"] = atmosphere_match.group(1).strip()
            
        # Try to extract complications
        complications_match = re.search(r"(?:Complications|Twists|Challenges|Surprises)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if complications_match:
            complications_text = complications_match.group(1).strip()
            # Split by bullet points or numbers
            complication_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", complications_text, re.MULTILINE)
            if complication_items:
                encounter_data["complications"] = [item.strip() for item in complication_items if item.strip()]
            else:
                # Split by periods
                complication_sentences = re.split(r'\.', complications_text)
                encounter_data["complications"] = [s.strip() for s in complication_sentences if s.strip()]
        
        # Try to find NPC blocks
        npc_blocks = re.findall(r"(?:NPC|Character|Key Figure|Important Person)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!NPC|Character|Key Figure|Important Person\s+\d+:)[^\n]+)*)", response, re.IGNORECASE)
        
        if not npc_blocks:
            # Try to find numbered entries
            npc_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", response)
            
        for i, block in enumerate(npc_blocks):
            if i >= npc_count:
                break
                
            npc = {
                "name": f"NPC {i+1}",
                "position": "",
                "description": block.strip(),
                "goals": "",
                "attitude": "",
                "tactics": "",
                "information": ""
            }
            
            # Try to extract name and position
            header_match = re.search(r"^([^,\n]+)(?:,\s*|\s+\-\s*|\s+is\s+(?:the|a)\s+)?([^,\n]+)?", block, re.IGNORECASE)
            if header_match:
                npc["name"] = header_match.group(1).strip()
                if header_match.group(2):
                    npc["position"] = header_match.group(2).strip()
                    
            # Try to extract goals
            goals_match = re.search(r"(?:Goals?|Motivation|Wants|Desires|Aims?)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if goals_match:
                npc["goals"] = goals_match.group(1).strip()
                
            # Try to extract attitude
            attitude_match = re.search(r"(?:Attitude|Demeanor|Stance|Disposition)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if attitude_match:
                npc["attitude"] = attitude_match.group(1).strip()
                
            # Try to extract tactics
            tactics_match = re.search(r"(?:Tactic|Approach|Method|Strategy)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if tactics_match:
                npc["tactics"] = tactics_match.group(1).strip()
                
            # Try to extract information
            info_match = re.search(r"(?:Information|Knowledge|Intel|Resource|Knows)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if info_match:
                npc["information"] = info_match.group(1).strip()
                
            encounter_data["npcs"].append(npc)
            
        # Try to extract possible outcomes
        outcomes_match = re.search(r"(?:Outcomes?|Developments?|Results?|Possibilities)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if outcomes_match:
            outcomes_text = outcomes_match.group(1).strip()
            # Split by bullet points or numbers
            outcome_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+(?:\n(?![-•*]|\d+\.)[^\n]+)*)", outcomes_text, re.MULTILINE)
            if outcome_items:
                encounter_data["possible_outcomes"] = [item.strip() for item in outcome_items if item.strip()]
            else:
                # Split by periods
                outcome_sentences = re.split(r'\.', outcomes_text)
                encounter_data["possible_outcomes"] = [s.strip() for s in outcome_sentences if s.strip()]
                
        # Try to extract skill checks
        skills_match = re.search(r"(?:Skill Checks?|Approaches?|Skills?|Checks?)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if skills_match:
            skills_text = skills_match.group(1).strip()
            # Split by bullet points or numbers
            skill_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", skills_text, re.MULTILINE)
            if skill_items:
                encounter_data["skill_checks"] = [item.strip() for item in skill_items if item.strip()]
            else:
                # Split by periods or commas
                skill_parts = re.split(r'[.,]', skills_text)
                encounter_data["skill_checks"] = [s.strip() for s in skill_parts if s.strip()]
        
        return encounter_data

    def _parse_rival_party(self, response: str, player_party: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse LLM response for rival party generation."""
        rival_data = {
            "name": "Unknown Rival Party",
            "theme": "",
            "rivalry_reason": "",
            "tactics": "",
            "history": "",
            "members": [],
            "encounter_scenarios": []
        }
        
        # Extract party name
        name_match = re.search(r"(?:Party|Group|Company|Band)(?:\s+Name)?:\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            rival_data["name"] = name_match.group(1).strip()
            
        # Extract theme
        theme_match = re.search(r"(?:Theme|Aesthetic|Style|Appearance)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if theme_match:
            rival_data["theme"] = theme_match.group(1).strip()
            
        # Extract rivalry reason
        reason_match = re.search(r"(?:Reason|Rivalry|Conflict|Motivation)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if reason_match:
            rival_data["rivalry_reason"] = reason_match.group(1).strip()
            
        # Extract tactics
        tactics_match = re.search(r"(?:Tactics|Strategy|Approach)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if tactics_match:
            rival_data["tactics"] = tactics_match.group(1).strip()
            
        # Extract history
        history_match = re.search(r"(?:History|Shared Past|Background|Previous)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if history_match:
            rival_data["history"] = history_match.group(1).strip()
        
        # Find rival NPC blocks - try various patterns
        member_blocks = re.findall(r"(?:Member|Character|NPC|Rival)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Member|Character|NPC|Rival\s+\d+:)[^\n]+)*)", response, re.IGNORECASE)
        
        if not member_blocks:
            # Try numbered entries
            member_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", response)
        
        # Try to match rivals with player party members
        player_classes = [pc.get("class", "").lower() for pc in player_party]
        
        for i, block in enumerate(member_blocks):
            rival = {
                "name": f"Rival {i+1}",
                "class": "",
                "race": "",
                "description": block.strip(),
                "abilities": [],
                "relationship": "",
                "goals": ""
            }
            
            # Extract name, race, class
            header_match = re.search(r"^([^,\n]+)(?:,\s*|\s+\-\s*|\s+is\s+a\s+|\s+the\s+)(?:a\s+)?([^,\n]+)(?:,\s*|\s+)([^,\n]+)?", block, re.IGNORECASE)
            if header_match:
                rival["name"] = header_match.group(1).strip()
                
                # Determine race and class
                group2 = header_match.group(2).strip() if header_match.group(2) else ""
                group3 = header_match.group(3).strip() if header_match.group(3) else ""
                
                races = ["human", "elf", "dwarf", "halfling", "gnome", "half-elf", "half-orc", "tiefling", "dragonborn"]
                classes = ["fighter", "wizard", "cleric", "rogue", "bard", "barbarian", "monk", "paladin", "ranger", "sorcerer", "warlock", "druid"]
                
                if group2.lower() in races:
                    rival["race"] = group2
                    if group3 and group3.lower() in classes:
                        rival["class"] = group3
                elif group2.lower() in classes:
                    rival["class"] = group2
                    if group3 and group3.lower() in races:
                        rival["race"] = group3
            
            # Extract abilities/equipment
            abilities_match = re.search(r"(?:Abilities|Equipment|Skills|Special)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if abilities_match:
                abilities_text = abilities_match.group(1).strip()
                ability_items = re.findall(r"(?:[-•*]\s*|^|\n\s*)([^,\n-•*][^,\n]*)", abilities_text)
                if ability_items:
                    rival["abilities"] = [item.strip() for item in ability_items if item.strip()]
                else:
                    rival["abilities"] = [abilities_text]
            
            # Extract relationship to player characters
            relationship_match = re.search(r"(?:Relationship|Attitude|Toward|Against)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if relationship_match:
                rival["relationship"] = relationship_match.group(1).strip()
                
                # Try to identify which PC this rival counters
                if i < len(player_party):
                    rival["counters_pc"] = player_party[i].get("name", f"PC {i+1}")
            
            # Extract goals
            goals_match = re.search(r"(?:Goals?|Motivation|Aims?)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if goals_match:
                rival["goals"] = goals_match.group(1).strip()
                
            rival_data["members"].append(rival)
        
        # Extract potential encounter scenarios
        scenarios_match = re.search(r"(?:Encounters?|Scenarios?|Situations?|Meetings?)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if scenarios_match:
            scenarios_text = scenarios_match.group(1).strip()
            scenario_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+(?:\n(?![-•*]|\d+\.)[^\n]+)*)", scenarios_text, re.MULTILINE)
            if scenario_items:
                rival_data["encounter_scenarios"] = [item.strip() for item in scenario_items if item.strip()]
            else:
                scenarios = re.split(r'\.(?=\s+[A-Z])', scenarios_text)
                rival_data["encounter_scenarios"] = [s.strip() for s in scenarios if s.strip()]
                
        return rival_data

    def generate_merchant_caravan(self, size: str = "medium", 
                                trade_focus: List[str] = None, 
                                route_dangers: List[str] = None) -> Dict[str, Any]:
        """
        Generate a traveling merchant caravan with traders, guards, and specialists.
        
        Args:
            size: Size of caravan (small, medium, large)
            trade_focus: Optional list of goods or trade specialties
            route_dangers: Optional list of dangers faced on their route
            
        Returns:
            Dict[str, Any]: Merchant caravan data with NPCs
        """
        # Calculate number of NPCs based on caravan size
        if size.lower() == "small":
            trader_count = 1
            guard_count = 2
            specialist_count = 1
        elif size.lower() == "large":
            trader_count = 3
            guard_count = 6
            specialist_count = 3
        else:  # medium
            trader_count = 2
            guard_count = 4
            specialist_count = 2
        
        # Build context for LLM
        context = f"Caravan Size: {size}\n"
        context += f"Traders: {trader_count}\n"
        context += f"Guards: {guard_count}\n"
        context += f"Specialists: {specialist_count}\n"
        
        if trade_focus:
            context += f"Trade Focus: {', '.join(trade_focus)}\n"
            
        if route_dangers:
            context += f"Route Dangers: {', '.join(route_dangers)}\n"
        
        # Create prompt for merchant caravan
        prompt = self._create_prompt(
            "generate merchant caravan",
            context + "\n"
            "Create a traveling merchant caravan with key NPCs and group dynamics.\n"
            "For the caravan as a whole, provide:\n"
            "1. Caravan name and description\n"
            "2. Route and destinations\n"
            "3. Notable wares and goods\n"
            "4. Travel customs and protocols\n"
            "5. Reputation among locals\n\n"
            f"Create {trader_count} merchant NPCs who lead or own the caravan:\n"
            "- Name, race, appearance, and personality\n"
            "- Trade specialty and business approach\n"
            "- Goals and current concerns\n"
            "- How they interact with customers\n\n"
            f"Create {guard_count} guard NPCs who protect the caravan:\n"
            "- Name, combat role, and equipment\n"
            "- Personality and loyalty level\n"
            "- Notable combat experience\n\n"
            f"Create {specialist_count} specialist NPCs with unique skills:\n"
            "- Name, specialty (guide, cook, animal handler, etc.)\n"
            "- Special skills or knowledge\n"
            "- Relationship with the merchants\n\n"
            "Also include 2-3 plot hooks involving the caravan that could spark adventures."
        )
        
        try:
            # Generate merchant caravan with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            caravan_data = self._parse_merchant_caravan(response, trader_count, guard_count, specialist_count)
            
            return {
                "success": True,
                "caravan_data": caravan_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate merchant caravan: {str(e)}"
            }

    def generate_noble_household(self, importance: str = "minor", 
                            cultural_background: str = None,
                            political_stance: str = None) -> Dict[str, Any]:
        """
        Generate a noble house or royal court with family members and staff.
        
        Args:
            importance: Importance of the house (minor, significant, major)
            cultural_background: Optional cultural influence on the noble house
            political_stance: Optional political alignment or motivation
            
        Returns:
            Dict[str, Any]: Noble house data with family and staff NPCs
        """
        # Determine NPC counts based on house importance
        if importance.lower() == "minor":
            family_count = 3
            staff_count = 4
            ally_rival_count = 2
        elif importance.lower() == "major":
            family_count = 6
            staff_count = 8
            ally_rival_count = 5
        else:  # significant
            family_count = 4
            staff_count = 6
            ally_rival_count = 3
        
        # Build context for LLM
        context = f"Noble House Importance: {importance}\n"
        context += f"Family Members: {family_count}\n"
        context += f"Household Staff: {staff_count}\n"
        context += f"Allies/Rivals: {ally_rival_count}\n"
        
        if cultural_background:
            context += f"Cultural Background: {cultural_background}\n"
            
        if political_stance:
            context += f"Political Stance: {political_stance}\n"
        
        # Create prompt for noble house
        prompt = self._create_prompt(
            "generate noble household",
            context + "\n"
            f"Create a {importance} noble house or royal court with family members and staff.\n"
            "For the noble house as a whole, provide:\n"
            "1. House name, heraldry, and motto\n"
            "2. Source of wealth and political influence\n"
            "3. Ancestral home or property description\n"
            "4. Family history and notable achievements\n"
            "5. Current ambitions and challenges\n\n"
            f"Create {family_count} key family members, including:\n"
            "- Name, title, age, and appearance\n"
            "- Personality and personal motivations\n"
            "- Role in family decision-making\n"
            "- Secrets or private ambitions\n"
            "- Notable skills or education\n\n"
            f"Create {staff_count} important household staff, including:\n"
            "- Name and position (steward, advisor, servant, etc.)\n"
            "- Length of service and loyalty level\n"
            "- Knowledge of family secrets\n"
            "- Relationships with family members\n\n"
            f"List {ally_rival_count} allies and/or rival houses with brief descriptions.\n\n"
            "Finally, include 3 political schemes or plots the house is currently involved in."
        )
        
        try:
            # Generate noble house with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            house_data = self._parse_noble_household(response, family_count, staff_count)
            
            return {
                "success": True,
                "noble_house": house_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate noble household: {str(e)}"
            }

    def generate_tavern_staff_and_patrons(self, tavern_type: str = "standard", 
                                        location: str = "town center",
                                        clientele: str = "mixed") -> Dict[str, Any]:
        """
        Generate tavern staff and regular patrons as an interconnected social hub.
        
        Args:
            tavern_type: Type of establishment (standard, upscale, seedy, etc.)
            location: Location of the tavern
            clientele: Primary clientele type
            
        Returns:
            Dict[str, Any]: Tavern data with staff and regular patrons
        """
        # Build context for LLM
        context = f"Tavern Type: {tavern_type}\n"
        context += f"Location: {location}\n"
        context += f"Clientele: {clientele}\n"
        
        # Create prompt for tavern
        prompt = self._create_prompt(
            "generate tavern staff and patrons",
            context + "\n"
            f"Create a {tavern_type} tavern or inn with staff and regular patrons.\n"
            "For the establishment as a whole, provide:\n"
            "1. Name and distinctive features\n"
            "2. Atmosphere and reputation\n"
            "3. Signature food, drinks, or entertainment\n"
            "4. Unique traditions or house rules\n"
            "5. Secret or unusual history\n\n"
            "Create the following staff members:\n"
            "- Owner/proprietor with personality and backstory\n"
            "- Bartender with unique traits and knowledge\n"
            "- Server(s) with personality and social connections\n"
            "- Other staff (cook, bouncer, entertainer) as appropriate\n\n"
            "Create 5-7 regular patrons who frequent the establishment, including:\n"
            "- Name, occupation, and appearance\n"
            "- Reason they come to the tavern\n"
            "- Relationship with staff and other patrons\n"
            "- Secrets or information they might share\n"
            "- Unusual habits or quirks\n\n"
            "Finally, include 3 rumors or plot hooks that players might encounter here."
        )
        
        try:
            # Generate tavern with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            tavern_data = self._parse_tavern(response)
            
            return {
                "success": True,
                "tavern_data": tavern_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate tavern: {str(e)}"
            }

    def generate_festival_or_celebration(self, celebration_type: str,
                                    cultural_context: str = None,
                                    scale: str = "town-wide",
                                    duration: str = "one day") -> Dict[str, Any]:
        """
        Generate a festival or celebration with key NPCs, events, and activities.
        
        Args:
            celebration_type: Type of celebration (harvest festival, religious holiday, etc.)
            cultural_context: Optional cultural context
            scale: Scale of the celebration
            duration: Duration of the celebration
            
        Returns:
            Dict[str, Any]: Festival data with NPCs and events
        """
        # Build context for LLM
        context = f"Celebration Type: {celebration_type}\n"
        context += f"Scale: {scale}\n"
        context += f"Duration: {duration}\n"
        
        if cultural_context:
            context += f"Cultural Context: {cultural_context}\n"
        
        # Create prompt for festival
        prompt = self._create_prompt(
            "generate festival or celebration",
            context + "\n"
            f"Create a detailed {celebration_type} with key NPCs, events, and social dynamics.\n"
            "For the celebration as a whole, provide:\n"
            "1. Name and origin of the celebration\n"
            "2. Cultural significance and traditions\n"
            "3. Typical activities and customs\n"
            "4. Decorations, food, and special items\n"
            "5. Overall mood and atmosphere\n\n"
            "Create 5-7 key NPCs involved in the celebration, including:\n"
            "- Name, role in the celebration, and appearance\n"
            "- Special duties or performances\n"
            "- Attitude toward the celebration\n"
            "- Interactions with attendees\n\n"
            "Describe 4-6 specific events or activities that occur during the celebration:\n"
            "- Name and description of the event\n"
            "- When and where it takes place\n"
            "- Key NPCs involved\n"
            "- How attendees participate\n"
            "- Potential complications or surprises\n\n"
            "Include 3 ways adventurers could meaningfully participate in or interact with the celebration."
        )
        
        try:
            # Generate festival with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            festival_data = self._parse_festival(response)
            
            return {
                "success": True,
                "festival_data": festival_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate festival: {str(e)}"
            }

    def generate_npc_relationships(self, npcs: List[Dict[str, Any]],
                                relationship_types: List[str] = None,
                                complexity: str = "moderate") -> Dict[str, Any]:
        """
        Generate detailed relationships between existing NPCs.
        
        Args:
            npcs: List of existing NPC data dictionaries
            relationship_types: Optional types of relationships to focus on
            complexity: Complexity of relationship web (simple, moderate, complex)
            
        Returns:
            Dict[str, Any]: Relationship data between NPCs
        """
        # Build context for LLM
        context = f"NPCs: {len(npcs)}\n"
        context += f"Relationship Complexity: {complexity}\n"
        
        npc_descriptions = ""
        for i, npc in enumerate(npcs, 1):
            npc_descriptions += f"{i}. {npc.get('name', 'Unknown')}"
            if "position" in npc:
                npc_descriptions += f" ({npc['position']})"
            elif "occupation" in npc:
                npc_descriptions += f" ({npc['occupation']})"
            npc_descriptions += "\n"
        
        context += f"NPC List:\n{npc_descriptions}\n"
        
        if relationship_types:
            context += f"Relationship Types: {', '.join(relationship_types)}\n"
        
        # Create prompt for relationships
        prompt = self._create_prompt(
            "generate npc relationships",
            context + "\n"
            "Create a web of detailed relationships between these existing NPCs.\n"
            "For each relationship, provide:\n"
            "1. The NPCs involved (pairs or small groups)\n"
            "2. Type of relationship (family, friendship, rivalry, romance, business, etc.)\n"
            "3. History of the relationship\n"
            "4. Current dynamics and feelings\n"
            "5. Hidden aspects or complications\n"
            "6. How the relationship affects their behavior\n\n"
            f"Create a {complexity} web with multiple relationship types:\n"
            "- Positive relationships (friendship, alliance, family, romance)\n"
            "- Negative relationships (rivalry, enmity, distrust, betrayal)\n"
            "- Complex relationships (mixed feelings, history of changes)\n"
            "- Secret relationships unknown to others\n\n"
            "Also include 2-3 relationship tensions or conflicts that could develop in the future."
        )
        
        try:
            # Generate relationships with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            relationship_data = self._parse_npc_relationships(response, npcs)
            
            return {
                "success": True,
                "relationship_data": relationship_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate relationships: {str(e)}"
            }

    def generate_response_to_event(self, npcs: List[Dict[str, Any]],
                                event: str,
                                impact_level: str = "significant") -> Dict[str, Any]:
        """
        Generate NPC group responses to a major event or crisis.
        
        Args:
            npcs: List of NPCs to generate responses for
            event: Description of the event or crisis
            impact_level: Level of impact on the NPCs
            
        Returns:
            Dict[str, Any]: NPC responses to the event
        """
        # Build context for LLM
        context = f"Event: {event}\n"
        context += f"Impact Level: {impact_level}\n"
        context += f"Number of NPCs: {len(npcs)}\n\n"
        
        npc_descriptions = ""
        for i, npc in enumerate(npcs, 1):
            npc_descriptions += f"{i}. {npc.get('name', 'Unknown')}"
            if "position" in npc:
                npc_descriptions += f" ({npc['position']})"
            elif "occupation" in npc:
                npc_descriptions += f" ({npc['occupation']})"
            npc_descriptions += "\n"
        
        context += f"NPC List:\n{npc_descriptions}\n"
        
        # Create prompt for responses
        prompt = self._create_prompt(
            "generate npc responses to event",
            context + "\n"
            f"Create detailed responses of these NPCs to the event: {event}\n"
            "For each NPC, provide:\n"
            "1. Initial reaction and emotional response\n"
            "2. Public actions and statements\n"
            "3. Private thoughts and concerns\n"
            "4. How this changes their plans or behavior\n"
            "5. Interactions with other NPCs about the event\n\n"
            "Also include:\n"
            "1. Group dynamics that form in response (alliances, oppositions)\n"
            "2. How different NPCs interpret the same event differently\n"
            "3. Unexpected or surprising responses\n"
            "4. Long-term impact on key relationships\n\n"
            "Finally, suggest 2-3 ways player characters might get involved with these reactions."
        )
        
        try:
            # Generate responses with LLM
            response = self.llm_service.generate(prompt)
            
            # Parse the response
            event_response_data = self._parse_event_responses(response, npcs, event)
            
            return {
                "success": True,
                "event_responses": event_response_data,
                "raw_response": response
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate event responses: {str(e)}"
            }

    # Helper parser methods for the new functions

    def _parse_merchant_caravan(self, response: str, trader_count: int, guard_count: int, specialist_count: int) -> Dict[str, Any]:
        """Parse LLM response for merchant caravan generation."""
        caravan_data = {
            "name": "Unknown Caravan",
            "description": "",
            "route": "",
            "wares": [],
            "customs": "",
            "reputation": "",
            "traders": [],
            "guards": [],
            "specialists": [],
            "plot_hooks": []
        }
        
        # Parse caravan details
        name_match = re.search(r"(?:Caravan|Name)(?:\s+Name)?:\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            caravan_data["name"] = name_match.group(1).strip()
        
        description_match = re.search(r"(?:Description|Overview|Appearance)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if description_match:
            caravan_data["description"] = description_match.group(1).strip()
        
        route_match = re.search(r"(?:Route|Destinations|Travels|Journey)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if route_match:
            caravan_data["route"] = route_match.group(1).strip()
        
        wares_match = re.search(r"(?:Wares|Goods|Merchandise|Products)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if wares_match:
            wares_text = wares_match.group(1).strip()
            wares_items = re.findall(r"(?:[-•*]\s*|^|\n\s*)([^,\n-•*][^,\n]*)", wares_text)
            if wares_items:
                caravan_data["wares"] = [item.strip() for item in wares_items if item.strip()]
            else:
                caravan_data["wares"] = [w.strip() for w in wares_text.split(",") if w.strip()]
        
        customs_match = re.search(r"(?:Customs|Protocols|Traditions|Rules)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if customs_match:
            caravan_data["customs"] = customs_match.group(1).strip()
        
        reputation_match = re.search(r"(?:Reputation|Known For|Standing|Perception)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if reputation_match:
            caravan_data["reputation"] = reputation_match.group(1).strip()
        
        # Parse traders
        trader_blocks = re.findall(r"(?:Trader|Merchant|Owner|Leader)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Trader|Merchant|Owner|Leader\s+\d+:|Guard|Specialist)[^\n]+)*)", response, re.IGNORECASE)
        
        if not trader_blocks:
            # Try to find numbered entries
            sections = re.split(r'\n\s*\n', response)
            # Look for sections that might contain trader info
            for section in sections:
                if re.search(r'(?:traders|merchants|owners)', section, re.IGNORECASE):
                    trader_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", section)
                    break
        
        for i, block in enumerate(trader_blocks[:trader_count]):
            trader = {
                "name": f"Trader {i+1}",
                "description": block.strip(),
                "specialty": "",
                "goals": ""
            }
            
            # Extract name
            header_match = re.search(r"^([^,\n]+)", block)
            if header_match:
                trader["name"] = header_match.group(1).strip()
            
            # Extract specialty
            specialty_match = re.search(r"(?:Specialty|Trade|Goods|Business)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if specialty_match:
                trader["specialty"] = specialty_match.group(1).strip()
            
            # Extract goals
            goals_match = re.search(r"(?:Goals?|Concerns|Motivation)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if goals_match:
                trader["goals"] = goals_match.group(1).strip()
            
            caravan_data["traders"].append(trader)
        
        # Parse guards
        guard_blocks = re.findall(r"(?:Guard|Protector|Warrior|Security)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Guard|Protector|Warrior|Security\s+\d+:|Trader|Merchant|Specialist)[^\n]+)*)", response, re.IGNORECASE)
        
        if not guard_blocks:
            # Try to find numbered entries in guard section
            sections = re.split(r'\n\s*\n', response)
            for section in sections:
                if re.search(r'(?:guards|protection|security)', section, re.IGNORECASE):
                    guard_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", section)
                    break
        
        for i, block in enumerate(guard_blocks[:guard_count]):
            guard = {
                "name": f"Guard {i+1}",
                "description": block.strip(),
                "equipment": "",
                "experience": ""
            }
            
            # Extract name
            header_match = re.search(r"^([^,\n]+)", block)
            if header_match:
                guard["name"] = header_match.group(1).strip()
            
            # Extract equipment
            equipment_match = re.search(r"(?:Equipment|Weapon|Armor|Gear)(?:[^:]*?):\s*([^\n]+)", block, re.IGNORECASE)
            if equipment_match:
                guard["equipment"] = equipment_match.group(1).strip()
            
            # Extract experience
            experience_match = re.search(r"(?:Experience|Background|History|Combat)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if experience_match:
                guard["experience"] = experience_match.group(1).strip()
            
            caravan_data["guards"].append(guard)
        
        # Parse specialists
        specialist_blocks = re.findall(r"(?:Specialist|Expert|Guide|Cook|Handler)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Specialist|Expert|Guide|Cook|Handler\s+\d+:|Trader|Merchant|Guard)[^\n]+)*)", response, re.IGNORECASE)
        
        if not specialist_blocks:
            # Try to find numbered entries in specialist section
            sections = re.split(r'\n\s*\n', response)
            for section in sections:
                if re.search(r'(?:specialists|experts|special)', section, re.IGNORECASE):
                    specialist_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", section)
                    break
        
        for i, block in enumerate(specialist_blocks[:specialist_count]):
            specialist = {
                "name": f"Specialist {i+1}",
                "description": block.strip(),
                "specialty": "",
                "skills": []
            }
            
            # Extract name and specialty
            header_match = re.search(r"^([^,\n]+)(?:,\s*|\s+\-\s*|\s+is\s+(?:the|a)\s+)?([^,\n]+)?", block, re.IGNORECASE)
            if header_match:
                specialist["name"] = header_match.group(1).strip()
                if header_match.group(2):
                    specialist["specialty"] = header_match.group(2).strip()
            
            # Extract skills
            skills_match = re.search(r"(?:Skills?|Abilities|Talents|Knowledge)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if skills_match:
                skills_text = skills_match.group(1).strip()
                skills_items = re.findall(r"(?:[-•*]\s*|^|\n\s*)([^,\n-•*][^,\n]*)", skills_text)
                if skills_items:
                    specialist["skills"] = [item.strip() for item in skills_items if item.strip()]
                else:
                    specialist["skills"] = [s.strip() for s in skills_text.split(",") if s.strip()]
            
            caravan_data["specialists"].append(specialist)
        
        # Parse plot hooks
        hooks_match = re.search(r"(?:Plot Hooks|Adventures|Quests|Scenarios)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if hooks_match:
            hooks_text = hooks_match.group(1).strip()
            hooks_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+(?:\n(?![-•*]|\d+\.)[^\n]+)*)", hooks_text, re.MULTILINE)
            if hooks_items:
                caravan_data["plot_hooks"] = [item.strip() for item in hooks_items if item.strip()]
            else:
                caravan_data["plot_hooks"] = [h.strip() for h in re.split(r'\.(?=\s+[A-Z])', hooks_text) if h.strip()]
        
        return caravan_data

    def _parse_noble_household(self, response: str, family_count: int, staff_count: int) -> Dict[str, Any]:
        """Parse LLM response for noble household generation."""
        house_data = {
            "name": "Unknown House",
            "heraldry": "",
            "motto": "",
            "wealth_source": "",
            "estate": "",
            "history": "",
            "ambitions": [],
            "family_members": [],
            "staff": [],
            "allies_rivals": [],
            "schemes": []
        }
        
        # Parse house details
        name_match = re.search(r"(?:House|Name|Noble House|Family)(?:\s+Name)?:\s*([^\n]+)", response, re.IGNORECASE)
        if name_match:
            house_data["name"] = name_match.group(1).strip()
        
        heraldry_match = re.search(r"(?:Heraldry|Crest|Symbol|Coat of Arms)(?:[^:]*?):\s*([^\n]+)", response, re.IGNORECASE)
        if heraldry_match:
            house_data["heraldry"] = heraldry_match.group(1).strip()
        
        motto_match = re.search(r"(?:Motto|Saying|Words)(?:[^:]*?):\s*([^\n]+)", response, re.IGNORECASE)
        if motto_match:
            house_data["motto"] = motto_match.group(1).strip()
        
        wealth_match = re.search(r"(?:Wealth|Income|Source|Resources)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if wealth_match:
            house_data["wealth_source"] = wealth_match.group(1).strip()
        
        estate_match = re.search(r"(?:Estate|Home|Property|Residence|Ancestral)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if estate_match:
            house_data["estate"] = estate_match.group(1).strip()
        
        history_match = re.search(r"(?:History|Background|Ancestry|Lineage)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if history_match:
            house_data["history"] = history_match.group(1).strip()
        
        ambitions_match = re.search(r"(?:Ambitions?|Goals?|Challenges?|Current)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if ambitions_match:
            ambitions_text = ambitions_match.group(1).strip()
            ambition_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", ambitions_text, re.MULTILINE)
            if ambition_items:
                house_data["ambitions"] = [item.strip() for item in ambition_items if item.strip()]
            else:
                house_data["ambitions"] = [a.strip() for a in re.split(r'\.(?=\s+[A-Z])', ambitions_text) if a.strip()]
        
        # Parse family members
        family_blocks = re.findall(r"(?:Family Member|Noble|Lord|Lady|Scion)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Family Member|Noble|Lord|Lady|Scion\s+\d+:|Staff|Servant)[^\n]+)*)", response, re.IGNORECASE)
        
        if not family_blocks:
            # Try to find family section
            sections = re.split(r'\n\s*\n', response)
            for section in sections:
                if re.search(r'(?:family members|nobles|relatives)', section, re.IGNORECASE):
                    family_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", section)
                    break
        
        for i, block in enumerate(family_blocks[:family_count]):
            member = {
                "name": f"Family Member {i+1}",
                "title": "",
                "description": block.strip(),
                "personality": "",
                "role": "",
                "secrets": ""
            }
            
            # Extract name and title
            header_match = re.search(r"^([^,\n]+)(?:,\s*|\s+\-\s*|\s+is\s+(?:the|a)\s+)?([^,\n]+)?", block, re.IGNORECASE)
            if header_match:
                member["name"] = header_match.group(1).strip()
                if header_match.group(2):
                    member["title"] = header_match.group(2).strip()
            
            # Extract personality
            personality_match = re.search(r"(?:Personality|Character|Demeanor)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if personality_match:
                member["personality"] = personality_match.group(1).strip()
            
            # Extract role
            role_match = re.search(r"(?:Role|Position|Status|Decision)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if role_match:
                member["role"] = role_match.group(1).strip()
            
            # Extract secrets
            secrets_match = re.search(r"(?:Secrets?|Private|Hidden|Ambitions?)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if secrets_match:
                member["secrets"] = secrets_match.group(1).strip()
            
            house_data["family_members"].append(member)
        
        # Parse staff
        staff_blocks = re.findall(r"(?:Staff|Servant|Retainer|Advisor|Steward)(?:\s+\d+)?(?:[^:]*?):\s*([^\n]+(?:\n(?!Staff|Servant|Retainer|Advisor|Steward\s+\d+:|Family Member|Noble|Lord|Lady)[^\n]+)*)", response, re.IGNORECASE)
        
        if not staff_blocks:
            # Try to find staff section
            sections = re.split(r'\n\s*\n', response)
            for section in sections:
                if re.search(r'(?:staff|servants|household)', section, re.IGNORECASE):
                    staff_blocks = re.findall(r"(?:\d+\.\s+)([^\n]+(?:\n(?!\d+\.\s+)[^\n]+)*)", section)
                    break
        
        for i, block in enumerate(staff_blocks[:staff_count]):
            staff = {
                "name": f"Staff {i+1}",
                "position": "",
                "description": block.strip(),
                "loyalty": "",
                "knowledge": ""
            }
            
            # Extract name and position
            header_match = re.search(r"^([^,\n]+)(?:,\s*|\s+\-\s*|\s+is\s+(?:the|a)\s+)?([^,\n]+)?", block, re.IGNORECASE)
            if header_match:
                staff["name"] = header_match.group(1).strip()
                if header_match.group(2):
                    staff["position"] = header_match.group(2).strip()
            
            # Extract loyalty
            loyalty_match = re.search(r"(?:Loyalty|Service|Dedication|Faithful)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if loyalty_match:
                staff["loyalty"] = loyalty_match.group(1).strip()
            
            # Extract knowledge
            knowledge_match = re.search(r"(?:Knowledge|Secrets?|Information|Aware)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", block, re.IGNORECASE)
            if knowledge_match:
                staff["knowledge"] = knowledge_match.group(1).strip()
            
            house_data["staff"].append(staff)
        
        # Parse allies and rivals
        allies_match = re.search(r"(?:Allies|Rivals|Relations|Houses)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if allies_match:
            allies_text = allies_match.group(1).strip()
            ally_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", allies_text, re.MULTILINE)
            if ally_items:
                house_data["allies_rivals"] = [item.strip() for item in ally_items if item.strip()]
            else:
                house_data["allies_rivals"] = [a.strip() for a in re.split(r'\.(?=\s+[A-Z])', allies_text) if a.strip()]
        
        # Parse schemes
        schemes_match = re.search(r"(?:Schemes?|Plots?|Political|Plans?)(?:[^:]*?):\s*([^\n]+(?:\n[^\n]+)*?)(?:\n\n|\Z)", response, re.IGNORECASE)
        if schemes_match:
            schemes_text = schemes_match.group(1).strip()
            scheme_items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+(?:\n(?![-•*]|\d+\.)[^\n]+)*)", schemes_text, re.MULTILINE)
            if scheme_items:
                house_data["schemes"] = [item.strip() for item in scheme_items if item.strip()]
            else:
                house_data["schemes"] = [s.strip() for s in re.split(r'\.(?=\s+[A-Z])', schemes_text) if s.strip()]
        
        return house_data
