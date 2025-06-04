# npc.py
# Description: Core NPC class that integrates components for Dungeon Master use.

from typing import Dict, List, Any, Optional, Union, Tuple
import json
import uuid
import os
from datetime import datetime

from backend.core.services.ollama_service import OllamaService
from backend.core.npc.llm_npc_advisor import LLMNPCAdvisor
from backend.core.npc.llm_mass_npc_advisor import LLMMassNPCAdvisor
from backend.core.npc.abstract_npc import AbstractNPC

class NPC(AbstractNPC):
    """
    Implementation of AbstractNPC for D&D 2024 edition.
    This class handles NPC creation, management, and evolution for Dungeon Masters.
    """
    
    def __init__(self):
        """Initialize the NPC system with LLM advisors."""
        self.llm_advisor = LLMNPCAdvisor()
        self.mass_npc_advisor = LLMMassNPCAdvisor()
        self.ollama_service = OllamaService()
        
        # Store NPCs in memory for this session
        # In a real implementation, this would use a database
        self._npcs = {}
        
        # Track NPC relationships and evolution
        self._npc_relationships = {}
        self._npc_evolution_history = {}
        
    def create_npc(self, npc_data: Dict[str, Any]) -> str:
        """
        Create a new NPC from input data.
        
        Args:
            npc_data: Dictionary containing NPC attributes
            
        Returns:
            str: Unique ID for the created NPC
        """
        # Validate NPC data
        validation_result = self.validate_npc(npc_data)
        if not validation_result["valid"]:
            raise ValueError(f"Invalid NPC data: {validation_result['errors']}")
            
        # Generate unique ID
        npc_id = npc_data.get("id", str(uuid.uuid4()))
        
        # Add creation timestamp
        npc_data["created_at"] = datetime.now().isoformat()
        
        # Add history tracking for evolution
        if "evolution_history" not in npc_data:
            npc_data["evolution_history"] = []
        
        # Use the LLM advisor to enhance the NPC if data is sparse
        if len(npc_data.keys()) < 5:  # Arbitrary threshold for "sparse" data
            enhanced_data = self.llm_advisor.enhance_npc_details(npc_data)
            npc_data.update(enhanced_data)
        
        # Store the NPC
        self._npcs[npc_id] = npc_data
        
        # Initialize relationship tracking
        self._npc_relationships[npc_id] = {}
        self._npc_evolution_history[npc_id] = []
        
        return npc_id
    
    def validate_npc(self, npc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate NPC against simplified rules.
        
        Args:
            npc_data: Dictionary containing NPC attributes
            
        Returns:
            Dict: Validation results with "valid" boolean and any errors
        """
        errors = []
        
        # Check required fields
        required_fields = ["name"]
        for field in required_fields:
            if field not in npc_data:
                errors.append(f"Missing required field: {field}")
                
        # Check ability scores if present
        if "ability_scores" in npc_data:
            ability_scores = npc_data["ability_scores"]
            for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                if ability in ability_scores:
                    score = ability_scores[ability]
                    if not (1 <= score <= 30):
                        errors.append(f"Invalid {ability} score: {score}. Must be between 1 and 30.")
        
        # Check challenge rating if present
        if "challenge_rating" in npc_data:
            cr = npc_data["challenge_rating"]
            valid_crs = [0, 0.125, 0.25, 0.5] + list(range(1, 31))
            if cr not in valid_crs:
                errors.append(f"Invalid challenge rating: {cr}")
                
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def generate_quick_npc(self, role: str, importance_level: str = "minor") -> Dict[str, Any]:
        """
        Generate a simple NPC based on role.
        
        Args:
            role: Role of the NPC (e.g., "shopkeeper", "guard")
            importance_level: Importance in the story ("minor", "supporting", "major")
            
        Returns:
            Dict: Generated NPC data
        """
        # Use the LLM advisor to generate an appropriate NPC
        npc_data = self.llm_advisor.generate_quick_npc(role, importance_level)
        
        # Create the NPC in our system
        npc_id = self.create_npc(npc_data)
        
        # Add the ID to the returned data
        npc_data["id"] = npc_id
        
        return npc_data
    
    def calculate_challenge_rating(self, npc_data: Dict[str, Any]) -> float:
        """
        Estimate appropriate Challenge Rating for an NPC.
        
        Args:
            npc_data: Dictionary containing NPC attributes
            
        Returns:
            float: Estimated Challenge Rating
        """
        # If CR is already defined, return it
        if "challenge_rating" in npc_data:
            return npc_data["challenge_rating"]
            
        # Otherwise estimate CR based on abilities, hp, damage, etc.
        # Simple estimation for demonstration purposes
        hp = npc_data.get("hit_points", 0)
        ac = npc_data.get("armor_class", 10)
        
        # Get attack damage
        attack_damage = 0
        if "actions" in npc_data:
            for action in npc_data["actions"]:
                if "damage" in action:
                    attack_damage = max(attack_damage, action["damage"].get("average", 0))
        
        # Very basic CR calculation
        if hp <= 0:
            return 0
            
        cr_estimate = (hp / 15) * (ac / 13) * (max(1, attack_damage) / 4)
        
        # Round to nearest standard CR
        valid_crs = [0, 0.125, 0.25, 0.5] + list(range(1, 31))
        
        # Find closest CR
        closest_cr = min(valid_crs, key=lambda x: abs(x - cr_estimate))
        
        return closest_cr
    
    def create_npc_group(self, template: Dict[str, Any], count: int, variation_level: str = "medium") -> List[Dict[str, Any]]:
        """
        Generate a group of related NPCs.
        
        Args:
            template: Base NPC template to use
            count: Number of NPCs to generate
            variation_level: How much variation between NPCs ("low", "medium", "high")
            
        Returns:
            List[Dict]: List of generated NPCs
        """
        # Use the mass NPC advisor to create variations
        npc_group = self.mass_npc_advisor.create_npc_group(template, count, variation_level)
        
        # Create each NPC in our system
        for npc in npc_group:
            npc_id = self.create_npc(npc)
            npc["id"] = npc_id
            
            # Establish relationships between members of the group
            for other_npc in npc_group:
                if "id" in other_npc and other_npc["id"] != npc_id:
                    self._add_relationship(npc_id, other_npc["id"], "group_member")
        
        return npc_group
    
    def get_npc_motivations(self, npc_id: str) -> Dict[str, Any]:
        """
        Get motivations and goals for an NPC.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            Dict: NPC motivations, goals, and internal conflicts
        """
        if npc_id not in self._npcs:
            raise ValueError(f"NPC with ID {npc_id} not found")
            
        npc_data = self._npcs[npc_id]
        
        # If motivations already exist, return them
        if "motivations" in npc_data:
            return {
                "motivations": npc_data["motivations"],
                "goals": npc_data.get("goals", []),
                "internal_conflicts": npc_data.get("internal_conflicts", [])
            }
            
        # Otherwise, use the LLM advisor to generate motivations
        motivations_data = self.llm_advisor.generate_npc_motivations(npc_data)
        
        # Update the NPC data
        npc_data.update(motivations_data)
        self._npcs[npc_id] = npc_data
        
        return motivations_data
    
    def export_npc_sheet(self, npc_id: str, format: str = 'pdf') -> str:
        """
        Export NPC to different formats.
        
        Args:
            npc_id: ID of the NPC
            format: Export format ('pdf', 'json', 'markdown')
            
        Returns:
            str: Path to exported file or raw content
        """
        if npc_id not in self._npcs:
            raise ValueError(f"NPC with ID {npc_id} not found")
            
        npc_data = self._npcs[npc_id]
        
        if format.lower() == 'json':
            return json.dumps(npc_data, indent=2)
            
        elif format.lower() == 'markdown':
            # Generate markdown representation
            md_content = f"# {npc_data['name']}\n\n"
            
            # Basic information
            if "description" in npc_data:
                md_content += f"{npc_data['description']}\n\n"
                
            # Ability scores
            if "ability_scores" in npc_data:
                md_content += "## Ability Scores\n\n"
                for ability, score in npc_data["ability_scores"].items():
                    modifier = (score - 10) // 2
                    md_content += f"**{ability.capitalize()}**: {score} ({modifier:+d})\n"
                md_content += "\n"
                
            # Actions
            if "actions" in npc_data:
                md_content += "## Actions\n\n"
                for action in npc_data["actions"]:
                    md_content += f"**{action['name']}**: {action['description']}\n\n"
            
            return md_content
            
        elif format.lower() == 'pdf':
            # In a real implementation, this would generate a PDF
            # For this example, we'll just indicate the process
            return f"PDF generation for {npc_data['name']} (ID: {npc_id}) would happen here"
            
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def update_npc_based_on_interaction(self, npc_id: str, interaction_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an NPC based on player interactions.
        
        Args:
            npc_id: ID of the NPC
            interaction_details: Details about the player interaction
            
        Returns:
            Dict: Updated NPC data
        """
        if npc_id not in self._npcs:
            raise ValueError(f"NPC with ID {npc_id} not found")
            
        npc_data = self._npcs[npc_id]
        
        # Record this interaction in the evolution history
        timestamp = datetime.now().isoformat()
        evolution_event = {
            "timestamp": timestamp,
            "interaction": interaction_details,
        }
        
        # Use the LLM to suggest how the NPC might evolve
        evolution_suggestion = self.llm_advisor.suggest_npc_evolution(npc_data, interaction_details)
        evolution_event["changes"] = evolution_suggestion
        
        # Update the NPC with suggested changes
        for key, value in evolution_suggestion.items():
            if key in npc_data and isinstance(npc_data[key], dict) and isinstance(value, dict):
                # Merge dictionaries for nested attributes
                npc_data[key].update(value)
            else:
                # Direct replacement for non-dict values
                npc_data[key] = value
        
        # Add to evolution history
        if "evolution_history" not in npc_data:
            npc_data["evolution_history"] = []
        npc_data["evolution_history"].append(evolution_event)
        
        # Track in our session history as well
        self._npc_evolution_history[npc_id].append(evolution_event)
        
        # Save the updated NPC
        self._npcs[npc_id] = npc_data
        
        return npc_data
    
    def generate_npc_dialogue(self, npc_id: str, context: str, responses_count: int = 3) -> List[str]:
        """
        Generate sample dialogue for an NPC in a given context.
        
        Args:
            npc_id: ID of the NPC
            context: Situation or prompt for the dialogue
            responses_count: Number of alternative responses to generate
            
        Returns:
            List[str]: Generated dialogue options
        """
        if npc_id not in self._npcs:
            raise ValueError(f"NPC with ID {npc_id} not found")
            
        npc_data = self._npcs[npc_id]
        
        # Use the LLM advisor to generate dialogue
        return self.llm_advisor.generate_dialogue(npc_data, context, responses_count)
    
    def generate_npc_portrait(self, npc_id: str) -> str:
        """
        Generate portrait for an NPC using stable diffusion integration.
        This is a placeholder - would require actual integration with an image generation API.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            str: Path or URL to generated portrait
        """
        if npc_id not in self._npcs:
            raise ValueError(f"NPC with ID {npc_id} not found")
            
        npc_data = self._npcs[npc_id]
        
        # Extract physical characteristics for the prompt
        species = npc_data.get("species", "human")
        gender = npc_data.get("gender", "")
        appearance = npc_data.get("appearance", "")
        
        # In a real implementation, this would call a stable diffusion API
        # For now, return a placeholder message
        return f"Portrait would be generated for {species} {gender} {npc_data['name']} with {appearance}"
    
    def _add_relationship(self, npc_id1: str, npc_id2: str, relationship_type: str, details: Dict[str, Any] = None) -> None:
        """
        Add or update relationship between two NPCs.
        
        Args:
            npc_id1: ID of first NPC
            npc_id2: ID of second NPC
            relationship_type: Type of relationship (e.g., "ally", "enemy", "family")
            details: Additional relationship details
        """
        if npc_id1 not in self._npcs or npc_id2 not in self._npcs:
            raise ValueError("One or both NPCs not found")
            
        if npc_id2 not in self._npc_relationships[npc_id1]:
            self._npc_relationships[npc_id1][npc_id2] = {}
            
        if npc_id1 not in self._npc_relationships[npc_id2]:
            self._npc_relationships[npc_id2][npc_id1] = {}
        
        # Update relationship data
        relationship_data = {
            "type": relationship_type,
            "updated_at": datetime.now().isoformat()
        }
        
        if details:
            relationship_data.update(details)
            
        self._npc_relationships[npc_id1][npc_id2] = relationship_data
        
        # Mirror relationship for the other NPC
        mirrored_data = relationship_data.copy()
        self._npc_relationships[npc_id2][npc_id1] = mirrored_data
    
    def get_npc_relationships(self, npc_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all relationships for an NPC.
        
        Args:
            npc_id: ID of the NPC
            
        Returns:
            Dict: Dictionary of relationships keyed by related NPC IDs
        """
        if npc_id not in self._npcs:
            raise ValueError(f"NPC with ID {npc_id} not found")
            
        return self._npc_relationships.get(npc_id, {})