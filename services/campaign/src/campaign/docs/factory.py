"""API documentation for campaign factory endpoints."""

# Example responses for documentation
CAMPAIGN_GENERATION_RESPONSE = {
    "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "success",
    "message": "Campaign generated successfully",
    "details": {
        "structure": {
            "narrative_arc": "A rising darkness threatens the kingdom...",
            "chapters": [
                {
                    "title": "Dark Omens",
                    "summary": "Strange occurrences plague the city...",
                    "objectives": [
                        "Investigate the mysterious deaths",
                        "Discover the cultist connection",
                        "Save the merchant's daughter"
                    ],
                    "key_elements": {
                        "npcs": ["High Priest Aldrich", "Guard Captain Sarah"],
                        "locations": ["Temple District", "Old Town"],
                        "items": ["Ancient Scroll", "Cultist Symbol"]
                    }
                }
            ],
            "plot_points": [
                "The cult's first ritual",
                "Discovery of the ancient prophecy",
                "The betrayal of the High Priest"
            ],
            "key_npcs": [
                {
                    "name": "High Priest Aldrich",
                    "role": "Hidden Antagonist",
                    "motivation": "Power through dark rituals"
                }
            ],
            "key_locations": [
                {
                    "name": "Temple District",
                    "type": "urban",
                    "significance": "Center of religious power"
                }
            ]
        },
        "applied_themes": ["dark_fantasy", "conspiracy"]
    },
    "generated_content": {
        "description": "A dark fantasy campaign where corruption...",
        "themes": ["dark_fantasy", "conspiracy"],
        "style": "grim and gritty",
        "pacing": "measured tension"
    }
}

CAMPAIGN_REFINEMENT_RESPONSE = {
    "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "success",
    "message": "Campaign refined successfully",
    "changes": [
        {
            "type": "theme",
            "element": "tone",
            "from": "dark",
            "to": "darker"
        },
        {
            "type": "content",
            "element": "subplot",
            "action": "add",
            "details": "Conspiracy within the temple"
        }
    ],
    "preserved": ["core_plot", "key_npcs"]
}

NPC_GENERATION_RESPONSE = {
    "npc_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "success",
    "message": "NPC generated successfully",
    "npc_data": {
        "name": "Aldrich the Corrupted",
        "type": "major",
        "role": "villain",
        "description": "A once-noble priest turned to darkness...",
        "motivation": "Achieve immortality through forbidden rituals",
        "personality": {
            "traits": ["ambitious", "manipulative", "charismatic"],
            "quirks": ["Always speaks in whispers", "Constantly checks reflection"],
            "fears": ["Death", "Loss of power"]
        },
        "stats": {
            "level": 12,
            "class": "Cleric/Warlock",
            "key_abilities": ["charisma", "wisdom"]
        }
    },
    "relationships": [
        {
            "type": "rival",
            "target": "party_leader",
            "dynamic": "public ally, secret enemy"
        },
        {
            "type": "mentor",
            "target": "cultist_leader",
            "dynamic": "teaching forbidden knowledge"
        }
    ],
    "theme_elements": ["corruption", "religious", "darkness"]
}

LOCATION_GENERATION_RESPONSE = {
    "location_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "success",
    "message": "Location generated successfully",
    "location_data": {
        "name": "The Twisted Spires",
        "type": "settlement",
        "importance": "major",
        "description": "A city of dark towers and winding streets...",
        "features": {
            "architecture": "Gothic spires and gargoyles",
            "atmosphere": "Perpetual twilight",
            "population": "10,000 souls"
        },
        "areas": [
            {
                "name": "Temple District",
                "description": "Ancient temples loom over narrow streets...",
                "points_of_interest": [
                    "The Dark Cathedral",
                    "Whispers Market",
                    "Scholar's Quarter"
                ]
            }
        ],
        "hooks": [
            "Strange lights in the cathedral at night",
            "Missing temple acolytes",
            "Mysterious symbols appearing on doors"
        ]
    },
    "connections": [
        {
            "type": "road",
            "target": "capital_city",
            "description": "The King's Highway, heavily patrolled"
        },
        {
            "type": "river",
            "target": "port_town",
            "description": "The Dark River, carrying mysterious cargo"
        }
    ],
    "theme_elements": ["gothic", "mysterious", "religious"]
}

MAP_GENERATION_RESPONSE = {
    "map_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "success",
    "message": "Map generated successfully",
    "map_data": {
        "name": "The Twisted Spires - City Map",
        "type": "settlement",
        "scale": "detailed",
        "dimensions": {
            "width": 2000,
            "height": 2000,
            "scale": "1 inch = 100 feet"
        },
        "style": {
            "base": "parchment",
            "ink": "dark sepia",
            "labels": "gothic script"
        }
    },
    "image_url": "https://example.com/maps/twisted_spires.jpg",
    "features": [
        {
            "type": "landmark",
            "name": "Dark Cathedral",
            "position": {"x": 1000, "y": 1000},
            "icon": "cathedral",
            "label": "The Dark Cathedral"
        },
        {
            "type": "district",
            "name": "Temple District",
            "bounds": {
                "top_left": {"x": 800, "y": 800},
                "bottom_right": {"x": 1200, "y": 1200}
            },
            "label": "Temple District"
        }
    ],
    "theme_elements": ["gothic", "dark", "religious"]
}

# OpenAPI tags
tags = [
    {
        "name": "factory",
        "description": "Campaign factory and content generation endpoints",
    }
]

# OpenAPI documentation strings
generate_campaign_docs = {
    "summary": "Generate a new campaign",
    "description": """
    Generate a complete D&D campaign based on specified parameters.
    
    The generation process includes:
    - Campaign structure and narrative arc
    - Chapter organization
    - Major plot points and NPCs
    - Key locations and items
    - Theme integration
    
    Optionally applies specified themes to shape the campaign's content and tone.
    
    Example themes:
    - Dark Fantasy: Grim and gritty atmosphere with corruption themes
    - High Fantasy: Epic and heroic with powerful magic
    - Political Intrigue: Complex relationships and power struggles
    - Horror: Fear and suspense with supernatural elements
    """,
    "responses": {
        200: {
            "description": "Campaign generated successfully",
            "content": {
                "application/json": {
                    "example": CAMPAIGN_GENERATION_RESPONSE
                }
            }
        },
        500: {
            "description": "Generation error"
        }
    }
}

refine_campaign_docs = {
    "summary": "Refine an existing campaign",
    "description": """
    Refine and adjust an existing campaign while preserving specified elements.
    
    Refinement types:
    - theme: Adjust the campaign's thematic elements and tone
    - content: Modify specific content like plots, NPCs, or locations
    - structure: Change campaign structure, chapters, or pacing
    
    The refinement process preserves specified elements while adjusting others
    to maintain consistency and narrative cohesion.
    
    Examples of preserved elements:
    - core_plot: Main storyline and key plot points
    - key_npcs: Important NPCs and their relationships
    - pacing: Story pacing and chapter structure
    - themes: Specific theme elements or motifs
    """,
    "responses": {
        200: {
            "description": "Campaign refined successfully",
            "content": {
                "application/json": {
                    "example": CAMPAIGN_REFINEMENT_RESPONSE
                }
            }
        },
        404: {
            "description": "Campaign not found"
        },
        500: {
            "description": "Refinement error"
        }
    }
}

generate_npc_docs = {
    "summary": "Generate a new NPC",
    "description": """
    Generate a themed NPC for a campaign with relationships and backstory.
    
    NPC types:
    - major: Key story characters with detailed backgrounds
    - minor: Supporting characters with basic roles
    - background: Simple NPCs for atmosphere
    
    Roles examples:
    - villain: Main antagonist or subordinate
    - ally: Friendly to the party
    - neutral: Could go either way
    - quest_giver: Provides missions and information
    
    Relationships can be specified to connect the NPC to:
    - Other NPCs (existing or new)
    - Player characters
    - Factions or organizations
    """,
    "responses": {
        200: {
            "description": "NPC generated successfully",
            "content": {
                "application/json": {
                    "example": NPC_GENERATION_RESPONSE
                }
            }
        },
        404: {
            "description": "Campaign not found"
        },
        500: {
            "description": "Generation error"
        }
    }
}

generate_location_docs = {
    "summary": "Generate a new location",
    "description": """
    Generate a themed location for a campaign with connections and features.
    
    Location types:
    - settlement: Towns, cities, villages
    - dungeon: Dungeons, caves, ruins
    - wilderness: Forests, mountains, plains
    - special: Unique or magical locations
    
    Importance levels:
    - major: Key story locations with detailed features
    - minor: Supporting locations with basic details
    - background: Simple locations for atmosphere
    
    Connections can be specified to link the location to:
    - Other locations
    - Trade routes
    - Natural features
    - Magical phenomena
    """,
    "responses": {
        200: {
            "description": "Location generated successfully",
            "content": {
                "application/json": {
                    "example": LOCATION_GENERATION_RESPONSE
                }
            }
        },
        404: {
            "description": "Campaign not found"
        },
        500: {
            "description": "Generation error"
        }
    }
}

generate_map_docs = {
    "summary": "Generate a new map",
    "description": """
    Generate a themed map for a campaign location.
    
    Map types:
    - world: World or region overview
    - settlement: Town or city layout
    - dungeon: Dungeon or building floor plan
    - wilderness: Natural area or terrain
    
    Scale options:
    - overview: Broad view with major features
    - detailed: Detailed view with specific elements
    
    Features can include:
    - Landmarks and points of interest
    - Districts or regions
    - Natural features
    - Roads and connections
    - Labels and annotations
    """,
    "responses": {
        200: {
            "description": "Map generated successfully",
            "content": {
                "application/json": {
                    "example": MAP_GENERATION_RESPONSE
                }
            }
        },
        404: {
            "description": "Campaign or location not found"
        },
        500: {
            "description": "Generation error"
        }
    }
}
