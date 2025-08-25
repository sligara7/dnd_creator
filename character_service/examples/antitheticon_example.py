"""Example of generating and evolving an Antitheticon."""

async def demonstrate_antitheticon(antitheticon_service: AntithesiconService):
    # Example party of heroes
    party_data = [
        {
            "id": "char1",
            "name": "Aethon the Radiant",
            "class": "Paladin",
            "alignment": "Lawful Good",
            "traits": ["Honorable", "Protective", "Just"],
            "methods": ["Direct confrontation", "Holy magic", "Leadership"],
            "beliefs": ["Light conquers darkness", "Protect the innocent"]
        },
        {
            "id": "char2",
            "name": "Sylvana Moonshadow",
            "class": "Druid",
            "alignment": "Neutral Good",
            "traits": ["Wise", "Patient", "Nurturing"],
            "methods": ["Natural magic", "Healing", "Transformation"],
            "beliefs": ["Balance in all things", "Preserve life"]
        }
    ]

    campaign_notes = [
        {
            "entry": "Party has been protecting villages from raids",
            "outcome": "Successfully defended three settlements",
            "party_methods": "Open confrontation, moral leadership",
            "impact": "Growing reputation as defenders of justice"
        }
    ]

    # Analyze the party
    party_profile = await antitheticon_service.analyze_party(
        party_data, campaign_notes)
    
    # This would analyze the party as:
    """
    {
        "members": [
            {
                "archetype": "Holy Warrior",
                "beliefs": ["Justice", "Protection", "Honor"],
                "methods": ["Direct", "Righteous", "Leadership"],
                "strengths": ["Holy magic", "Combat prowess", "Inspiration"],
                "weaknesses": ["Rigid morality", "Predictable", "Pride"]
            },
            {
                "archetype": "Nature Guardian",
                "beliefs": ["Balance", "Life", "Harmony"],
                "methods": ["Natural", "Healing", "Adaptive"],
                "strengths": ["Versatility", "Support", "Wisdom"],
                "weaknesses": ["Passive", "Hesitant", "Overextending"]
            }
        ],
        "shared_beliefs": ["Protect the weak", "Good triumphs"],
        "group_dynamics": "Leadership/Support synergy",
        "moral_alignment": "Strongly Good-aligned"
    }
    """

    # Generate initial Antitheticon
    dm_notes = {
        "theme": "Corruption of justice",
        "desired_conflicts": ["Moral gray areas", "Ends vs means"],
        "specific_oppositions": {
            "char1": "Former paladin who chose power over justice",
            "char2": "Nature corrupter who believes in survival of fittest"
        }
    }

    antitheticon = await antitheticon_service.generate_antitheticon(
        party_profile,
        dm_notes,
        AntithesisFocus.MORAL,
        AntithesisDevelopment.CORRUPTED
    )

    # This would generate something like:
    """
    {
        "leader": {
            "character_id": "anti1",
            "name": "Lord Duskbane",
            "class": "Oathbreaker Paladin",
            "opposes": "char1",
            "antithetical_traits": {
                "honor": "pragmatic brutality",
                "protection": "culling the weak",
                "justice": "might makes right"
            },
            "personal_grudge": "Was once like Aethon, learned the hard way that honor doesn't save lives",
            "methods": ["Fear", "Corruption", "Dark magic"]
        },
        "core_members": [
            {
                "character_id": "anti2",
                "name": "Thornheart",
                "class": "Blighted Druid",
                "opposes": "char2",
                "antithetical_traits": {
                    "nurturing": "parasitic",
                    "balance": "domination",
                    "preservation": "evolution through death"
                },
                "methods": ["Plague magic", "Toxic growth", "Corruption of nature"]
            }
        ],
        "henchmen": [
            {
                "name": "Fallen Crusaders",
                "role": "Corrupt holy warriors",
                "number": 5,
                "abilities": ["Dark smite", "Fear aura"]
            }
        ],
        "base_of_operations": {
            "name": "The Blackened Cathedral",
            "description": "Once-holy place corrupted by dark rituals",
            "features": ["Corrupted altar", "Dark armory", "Torture chambers"]
        }
    }
    """

    # Later, when party levels up...
    party_changes = [
        {
            "character_id": "char1",
            "type": "level_up",
            "new_abilities": ["Divine intervention", "Greater smite"],
            "character_growth": "Growing into inspiring leader"
        }
    ]

    # Evolve the Antitheticon
    evolved = await antitheticon_service.evolve_antitheticon(
        antitheticon,
        party_changes,
        dm_notes,
        [{"event": "Failed to corrupt a town", "reaction": "Growing desperate"}]
    )

    # This would evolve them like:
    """
    {
        "leader": {
            "new_abilities": ["Corrupt divine intervention", "Dark inspiration"],
            "evolution": "Becoming dark mirror of leadership",
            "new_methods": ["Corrupt followers", "Mock inspiration"]
        },
        "tactical_changes": {
            "strategy": "Target followers instead of leaders",
            "new_resources": ["Corrupted holy symbols", "Dark blessed weapons"]
        }
    }
    """

    # Generate an encounter
    encounter = await antitheticon_service.generate_encounter_plan(
        evolved,
        party_profile,
        "corrupted_church",
        {"type": "Defiled temple", "features": ["Corrupted altar", "Dark mists"]}
    )

    # This creates a tactical plan:
    """
    {
        "setup": {
            "initial_positions": {
                "leader": "At corrupted altar",
                "core_members": ["Shadow positions"],
                "henchmen": ["Guard points", "Ambush spots"]
            },
            "environmental_setup": {
                "dark_mists": "Separate party members",
                "corrupted_altar": "Power source for rituals"
            }
        },
        "phases": [
            {
                "name": "Separation",
                "tactics": "Use mists to isolate party members",
                "counters": {
                    "char1": "Corrupt holy energy to weaken",
                    "char2": "Toxic nature to prevent shapeshifting"
                }
            },
            {
                "name": "Corruption",
                "tactics": "Attempt to corrupt or break party's spirit",
                "special_actions": ["Dark ritual", "Show consequences"]
            }
        ]
    }
    """

    # As campaign progresses, evolve relationships
    relationship = await antitheticon_service.evolve_relationship(
        evolved,
        "char1",
        [{"type": "confrontation", "outcome": "Revealed shared past"}]
    )

    # This deepens the nemesis relationship:
    """
    {
        "relationship_stage": "Personal vendetta",
        "new_elements": {
            "shared_history": "Trained at same holy order",
            "point_of_divergence": "Choice during crisis",
            "current_dynamic": "Each believes they learned the true lesson"
        },
        "evolution": {
            "hatred": "Deepened by understanding",
            "tactical": "More focused on breaking spirit than body",
            "future": "Heading toward tragic confrontation"
        }
    }
    """

    return antitheticon, evolved

# The Antitheticon system ensures:
# 1. Perfect opposition to party
# 2. Evolution alongside party growth
# 3. Deep personal connections
# 4. Tactical counters to party strategies
# 5. Thematic opposition
# 6. Growing nemesis relationships
