# npc.py
# Description: Core NPC class that integrates components for Dungeon Master use.

# must adhere to abstract_npc.py interface for NPC management in D&D 2024.

# Methods:

# create_npc(npc_data) - Create a new NPC from input data
# validate_npc(npc_data) - Validate NPC against simplified rules
# generate_quick_npc(role, importance_level) - Generate a simple NPC based on role
# calculate_challenge_rating(npc_data) - Estimate appropriate CR for an NPC
# create_npc_group(template, count, variation_level) - Generate a group of related NPCs
# get_npc_motivations(npc_id) - Get motivations and goals for an NPC
# export_npc_sheet(npc_id, format='pdf') - Export NPC to different formats

# Customizing NPC System with Llama 3/Ollama Integration
# Each function in npc.py can be enhanced through LLM interactions to provide rich NPC development:

# 1. create_npc(npc_data)
# LLM Enhancement: "Generate a compelling NPC based on campaign needs and setting"
# Implementation: Add parameter campaign_context to create setting-appropriate NPCs
# Prompt Example: "I need a shopkeeper for a frontier town who has a secret connection to the local thieves' guild. Create an NPC with appropriate stats and personality."

# 2. validate_npc(npc_data)
# LLM Enhancement: "Ensure NPC is balanced for intended role and suggest improvements"
# Implementation: Add parameter intended_role to validate NPCs against their purpose
# Prompt Example: "This NPC will be a recurring villain. Are their abilities appropriate for challenging a party of 4 level 6 characters without being overwhelming?"

# 3. generate_quick_npc(role, importance_level)
# LLM Enhancement: "Create instant NPCs with distinctive traits and voices"
# Implementation: Add parameter distinctive_feature to ensure memorable NPCs
# Prompt Example: "I need a town guard captain my players will meet in the next 5 minutes. Give me distinctive physical features, speech pattern, and key personality trait."

# 4. calculate_challenge_rating(npc_data)
# LLM Enhancement: "Provide tactical analysis and encounter design suggestions"
# Implementation: Add parameter encounter_context for situation-specific evaluation
# Prompt Example: "How challenging would this NPC be for my party in an ambush situation vs. a direct confrontation? How should I adjust tactics accordingly?"

# 5. create_npc_group(template, count, variation_level)
# LLM Enhancement: "Generate relationship dynamics and group behaviors"
# Implementation: Add parameter group_dynamics to create interconnected NPC groups
# Prompt Example: "Create 5 bandits with a clear hierarchy, internal conflicts, and varied combat tactics they might use together."

# 6. get_npc_motivations(npc_id)
# LLM Enhancement: "Develop complex, evolving motivations that respond to player actions"
# Implementation: Add parameter campaign_events to reflect evolving NPC goals
# Prompt Example: "How would this merchant's motivations change if the players exposed the corruption in the city guard that was extorting local businesses?"

# 7. export_npc_sheet(npc_id, format='pdf')
# LLM Enhancement: "Include roleplaying guides and plot hooks in NPC documentation"
# Implementation: Add parameters include_roleplaying_notes=True and plot_hooks_count=3
# Prompt Example: "Generate an NPC sheet with voice acting notes, 3 potential plot hooks, and suggested reactions to different player approaches."

# Implementation Approach
# Create an LLMNpcAdvisor class that integrates with Ollama/Llama3 specifically for NPC development
# Design system for rapid NPC generation during live sessions when DMs need quick characters
# Implement "NPC evolution" to suggest how NPCs might change based on player interactions
# Add capabilities for generating dialogue samples and roleplaying guidance for DMs
# Create integration with stable diffusion for generating NPC portraits with consistent visual identifiers
# Focus on DM experience with tools for tracking multiple NPCs and their relationships to the campaign

from backend.core.ollama_service import OllamaService

class LLMAbilityAdvisor:
    def __init__(self, llm_service=None):
        if llm_service is None:
            self.llm_service = OllamaService()
        else:
            self.llm_service = llm_service
        self.ability_scores = AbilityScores()