# creature.py
# Description: Core creature class for beasts, monsters, and other non-player entities.

# must adhere to abstract_creature.py interface for creature management in D&D 2024.

# Methods:

# create_creature(creature_data) - Create a new creature from input data
# validate_creature(creature_data) - Validate complete creature against monster creation rules
# calculate_challenge_rating(creature_stats) - Calculate appropriate CR for creature
# calculate_hit_points(hit_dice, constitution) - Calculate creature HP
# generate_attack_options(creature_type, cr) - Generate appropriate attacks based on creature type
# get_available_traits(creature_type, environment) - Get available traits for creature type
# export_creature_statblock(creature_id, format='pdf') - Export creature to different formats

# Mass creation methods:
# create_creatures_from_list(creature_list) - Create multiple creatures from a list
# validate_creatures(creature_list) - Validate multiple creatures against rules
# calculate_average_cr(creature_list) - Calculate average CR for a list of creatures

from backend.core.creature.abstract_creature import AbstractCreature
from backend.core.creature.llm_creature_advisor import LLMCreatureAdvisor
from backend.core.creature.llm_mass_creature_advisor import LLMMassCreatureAdvisor


