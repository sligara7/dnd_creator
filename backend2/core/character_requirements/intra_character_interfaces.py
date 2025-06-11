# # Character Creation/Development Methods

# ## Ability Scores
# - calculate_modifier(score)
# - get_point_buy_cost(score)
# - validate_ability_scores(scores_dict)
# - generate_standard_array()
# - generate_random_scores()
# - apply_species_bonuses(scores_dict, species_bonuses)
# - calculate_total_point_buy_cost(scores_dict)
# - apply_ability_score_improvement(scores_dict, improvements)
# - get_all_modifiers(scores_dict)
# - suggest_ability_score_distribution(character_class)

# ## Alignment
# - get_all_alignments()
# - get_alignment_description(ethical, moral)
# - validate_alignment(ethical, moral)
# - is_compatible_with_deity(ethical, moral, deity_alignment)

# ## Background
# - get_all_backgrounds()
# - get_background_details(background)
# - get_background_proficiencies(background)
# - get_background_equipment(background)
# - get_background_feature(background)
# - get_background_feat(background)
# - validate_custom_background(background_data)
# - create_custom_background(background_data)
# - apply_background_benefits(character_data, background)
# - set_character_background(background)

# ## Character Class
# - get_hit_die()
# - get_saving_throw_proficiencies()
# - get_armor_proficiencies()
# - get_weapon_proficiencies()
# - get_tool_proficiencies()
# - get_skill_choices()
# - get_starting_equipment()
# - get_features_by_level(level)
# - get_ability_score_improvement_levels()
# - get_spellcasting_ability()
# - get_spellcasting_type()
# - get_spell_slots_by_level(class_level)
# - get_cantrips_known(class_level)
# - get_spells_known(class_level, ability_modifier)
# - get_subclass_type()
# - get_class_resources(level)

# ## Multiclassing
# - get_available_classes_for_multiclass()
# - can_multiclass_into(new_class)
# - get_multiclass_requirements()
# - get_multiclass_proficiencies(new_class)
# - calculate_multiclass_spellcaster_level()
# - get_multiclass_spell_slots()
# - calculate_multiclass_hit_points(new_class, is_first_level)
# - get_level_in_class(class_name)
# - get_features_for_multiclass(class_name, level)

# ## Personality & Backstory
# - get_personality_options(background)
# - validate_personality(traits, ideals, bonds, flaws)
# - get_personality_suggested_by_alignment(alignment)
# - format_backstory_template(background)
# - set_character_personality(personality_elements)
# - set_backstory(backstory)

# ## Proficiencies
# - calculate_proficiency_bonus(character_level)
# - set_proficiency_level(prof_type, specific_prof, level)
# - add_proficiency(prof_type, specific_prof)
# - add_expertise(prof_type, specific_prof)
# - add_saving_throw_proficiency(ability)
# - add_proficiencies_from_class(class_name)
# - add_proficiencies_from_background(background)
# - add_proficiencies_from_species(species)

# ## Skills
# - set_skill_proficiency(skill_name, proficiency_level)
# - get_class_skills(character_class)
# - get_background_skills(background)

# ## Species
# - get_all_species()
# - get_species_details(species_name)
# - get_species_by_size(size)
# - get_species_by_ability_bonus(ability)
# - get_species_by_feature(feature)
# - get_ability_score_increases()
# - get_vision_types()
# - get_languages()
# - get_traits()
# - get_proficiencies()
# - get_lineages()
# - get_lineage_details(lineage)
# - register_custom_species(species_data)
# - validate_custom_species(species_data)
# - apply_to_character(character_data)

# ## Feats
# - get_all_feats()
# - get_feat_details(feat_name)
# - get_available_feats(character_data)
# - validate_feat_prerequisites(character_data, feat_name)
# - apply_feat_benefits(character_data, feat_name)
# - get_feats_by_category(category)
# - get_background_feats()
# - get_asi_replacement_feats(character_data)
# - create_custom_feat(feat_data)
# - validate_custom_feat(feat_data)
# - get_suggested_feat_progressions(character_concept)

# ## Equipment
# - get_starting_equipment_options(character_class)
# - calculate_carrying_capacity(strength_score, size_multiplier)
# - create_custom_equipment(equipment_data)

# ## Spells
# - get_spells_by_class(character_class)
# - get_spells_by_level(level)
# - get_spells_by_school(school)
# - filter_spells(filters)
# - create_custom_spell(spell_data)
# - validate_spell_creation(spell_data)

# The list covers many core aspects of D&D character creation, but it's not fully exhaustive. Here are some important areas that appear to be missing:

# ## Key Missing Areas

# ### Core Character Statistics
# - Methods for calculating and managing hit points (starting HP, HP per level)
# - Methods for calculating and tracking speed/movement
# - Methods for determining character size

# ### Combat & Actions
# - Methods for calculating attack bonuses
# - Methods for determining armor class based on equipment and abilities
# - Methods for calculating initiative bonus

# ### Character Integration
# - Methods for validating a complete character build
# - Methods for calculating derived statistics from multiple sources
# - Methods for determining a character's passive scores (Perception, Investigation, etc.)

# ### Character Management
# - Methods for character level management and level-up procedures
# - Methods for tracking experience points
# - Methods for managing character name, age, appearance
# - Methods for saving/loading characters

# ### Economic Elements
# - Methods for managing starting wealth
# - Methods for tracking currency

# ### Additional Character Elements
# - Methods for managing languages (beyond species)
# - Methods for managing inspiration
# - Methods for integrating senses (darkvision, blindsight, etc.)
# - Methods for setting and validating subclass choices

# ### Character Building Workflows
# - Methods for guiding the character creation process step-by-step
# - Methods for applying optional rules variations
# - Methods for handling homebrew content integration

# A complete character creation system would need interfaces between these components as well, which is what your original question was addressing. The layered approach with dependency tracking I described previously would be even more valuable with these additional components included.

# Missing Character Creation Methods
# Character Identity & Appearance
# Methods for generating/setting physical characteristics (height, weight, eye color, etc.)
# Methods for determining age and its effects on attributes
# Methods for name generation based on cultural background
# Methods for pronoun and gender identity settings
# Advanced Character Options
# Methods for handling variant species features (e.g., variant human)
# Methods for implementing custom origin rules (Tasha's)
# Methods for handling lineage transformations (e.g., Reborn, Hexblood)
# Methods for choosing fighting styles
# Campaign Integration
# Methods for selecting character origins tied to campaign settings
# Methods for establishing faction/organization memberships
# Methods for creating character connections to locations/NPCs
# Methods for implementing character secrets
# Advanced Creation Rules
# Methods for validating Adventurers League compliance
# Methods for implementing sourcebook restrictions
# Methods for handling starting at higher levels
# Methods for character retirement and legacy
# Character Documentation
# Methods for formatting and exporting character sheets
# Methods for creating character portraits/tokens
# Methods for generating shareable character summaries
# Methods for exporting to virtual tabletop formats
# Character History Generation
# Methods for generating formative life events
# Methods for creating timeline-integrated backstories
# Methods for determining background-appropriate contacts
# Methods for establishing mentor/rival relationships
# Character Goals & Motivations
# Methods for defining character goals
# Methods for establishing character fears and weaknesses
# Methods for setting long-term character development arcs
# Methods for determining character secrets
# System Configuration
# Methods for toggling optional character creation rules
# Methods for implementing house rules in character