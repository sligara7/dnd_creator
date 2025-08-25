"""Example of generating a WWII theme for D&D."""

async def demonstrate_ww2_theme(theme_generator: ThemeGenerator,
                              converter: DynamicThemeConverter,
                              db: GitDatabase):
    # Generate WWII theme
    ww2_theme = await theme_generator.generate_theme("""
    World War II era (1940s) with a focus on:
    - Military operations and equipment
    - Period-appropriate technology
    - Wartime atmosphere and tension
    - Special operations and resistance movements
    - Military ranks and organization
    - Experimental weapons programs
    """)

    # This would generate a complete theme definition like:
    """
    {
        "name": "World War II",
        "description": "1940s wartime setting with military focus",
        "key_concepts": [
            "Military hierarchy",
            "Combined arms warfare",
            "Resistance movements",
            "Experimental technology",
            "Wartime scarcity"
        ],
        "equipment_style": {
            "weapons": "Period military firearms and explosives",
            "armor": "Military uniforms and protective gear",
            "tools": "Military and survival equipment"
        },
        "magic_style": {
            "evocation": "Experimental weapons and explosives",
            "abjuration": "Defensive fortifications and equipment",
            "divination": "Military intelligence and reconnaissance",
            "enchantment": "Propaganda and psychological operations",
            "conjuration": "Supply drops and reinforcements",
            "transmutation": "Equipment modifications and repairs",
            "necromancy": "Forbidden experiments",
            "illusion": "Camouflage and deception"
        },
        "architectural_style": "Military bases, bunkers, and field fortifications",
        "clothing_style": "Military uniforms and civilian wartime fashion",
        "cultural_elements": [
            "Military discipline and hierarchy",
            "Wartime propaganda",
            "Resistance movements",
            "Rationing and scarcity",
            "International alliances"
        ],
        "technology_level": "1940s with some experimental advanced tech",
        "common_materials": [
            "Steel",
            "Canvas",
            "Leather",
            "Rubber",
            "Concrete",
            "Wood"
        ],
        "combat_style": "Combined arms warfare with firearms and explosives",
        "sample_names": [
            "Operation Thunderbolt",
            "Task Force Echo",
            "Special Unit 7"
        ]
    }
    """

    # Generate mappings for D&D elements
    mappings = await theme_generator.generate_theme_mappings(ww2_theme)
    
    # This would generate mappings like:
    """
    {
        "weapons": {
            "longsword": {
                "name": "Combat Knife",
                "damage": "1d8",
                "properties": ["melee", "light"]
            },
            "shortbow": {
                "name": "M1 Carbine",
                "damage": "1d6",
                "properties": ["ammunition", "range"]
            },
            "crossbow": {
                "name": "Thompson SMG",
                "damage": "1d8",
                "properties": ["ammunition", "range", "automatic"]
            }
        },
        "armor": {
            "leather": {
                "name": "Combat Uniform",
                "AC": 11
            },
            "chain mail": {
                "name": "Flak Jacket",
                "AC": 16
            },
            "plate": {
                "name": "Experimental Armor",
                "AC": 18
            }
        },
        "spells": {
            "fireball": {
                "name": "Hand Grenade",
                "description": "Throws an explosive device..."
            },
            "shield": {
                "name": "Take Cover",
                "description": "Quickly moves to nearby cover..."
            },
            "detect magic": {
                "name": "Detect Signals",
                "description": "Uses equipment to detect radio signals..."
            }
        },
        "classes": {
            "fighter": {
                "name": "Infantry Soldier",
                "features": ["Combat Training", "Squad Tactics"]
            },
            "wizard": {
                "name": "Field Scientist",
                "features": ["Experimental Tech", "Technical Knowledge"]
            },
            "rogue": {
                "name": "Special Operations",
                "features": ["Covert Ops", "Demolitions"]
            }
        }
    }
    """

    # Create a WWII-themed character
    base_concept = "A wise mentor who guides others with ancient knowledge"
    ww2_concept = await theme_generator.generate_themed_character_concept(
        base_concept, ww2_theme
    )
    # Might return: "A veteran officer who leads through experience and tactical wisdom"

    # Convert a fantasy character to WWII theme
    original_character = {
        "name": "Eldric the Wise",
        "class": "Wizard",
        "equipment": ["Staff", "Spellbook", "Robes"],
        "spells": ["Fireball", "Shield", "Detect Magic"],
        "abilities": ["Arcane Recovery", "Spell Mastery"]
    }

    ww2_character = await converter.convert_to_theme(
        original_character,
        "character",
        ww2_theme.description
    )
    # Would return something like:
    """
    {
        "name": "Major Harrison",
        "class": "Field Scientist",
        "equipment": ["Officer's Sidearm", "Technical Manual", "Officer's Uniform"],
        "abilities": ["Experimental Weapons", "Technical Analysis"],
        "special_equipment": ["Prototype Scanner", "Field Laboratory"]
    }
    """

    # Generate a themed location
    bunker = await theme_generator.generate_themed_location(
        "secret base",
        ww2_theme
    )
    # Would return something like:
    """
    {
        "name": "Bunker Complex Alpha",
        "type": "Military Installation",
        "features": [
            "Reinforced concrete walls",
            "Underground laboratories",
            "Command center",
            "Barracks",
            "Arsenal"
        ],
        "secrets": [
            "Experimental weapons vault",
            "Hidden escape tunnel",
            "Coded radio room"
        ]
    }
    """

    # Get themed descriptions of actions
    fireball_description = await converter.describe_themed_action(
        "Cast Fireball",
        ww2_theme.description
    )
    # Returns: "Lob an experimental phosphorus grenade that erupts in a
    # devastating explosion"

    shield_description = await converter.describe_themed_action(
        "Cast Shield",
        ww2_theme.description
    )
    # Returns: "Quickly deploy portable cover using experimental reactive armor"

    # Get suggestions for theme-specific elements
    new_weapons = await converter.suggest_theme_elements(
        ww2_theme.description,
        "weapon"
    )
    # Returns suggestions like:
    """
    [
        {
            "name": "Experimental Tesla Gun",
            "base_weapon": "Lightning Bolt spell",
            "description": "Prototype electrical weapon"
        },
        {
            "name": "Magnetic Mine",
            "base_weapon": "Delayed Blast Fireball spell",
            "description": "Advanced magnetic explosive"
        }
    ]
    """

    # The theme can handle any concept from the original game while
    # maintaining game balance and mechanics
    return ww2_theme, mappings
