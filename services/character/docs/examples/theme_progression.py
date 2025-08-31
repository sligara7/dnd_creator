"""Example of how characters and items progress differently through themes."""

async def demonstrate_theme_progression(db: GitDatabase, graph: EntityGraph):
    # Create Yoda and his lightsaber
    yoda_id = await db.create_entity(EntityType.CHARACTER_PC, {
        "name": "Yoda",
        "class": "Monk",
        "level": 20,
        "theme": "fantasy"
    })
    await graph.add_node(yoda_id, NodeType.ROOT, {
        "name": "Yoda",
        "level": 20,
        "theme": "fantasy"
    })

    saber_id = await db.create_entity(EntityType.WEAPON, {
        "name": "Lightsaber",
        "damage": "1d8",
        "damage_type": "force",
        "theme": "fantasy"
    })

    # Create ownership relation
    await db.create_relation(yoda_id, saber_id, "owns")

    # Chapter 1: Original fantasy theme
    # Both use root versions

    # Chapter 2: Cyberpunk theme
    cyber_yoda_id = await db.create_themed_variant(yoda_id, "cyberpunk")
    await db.commit_changes(yoda_id, cyber_yoda_id, {
        "name": "Cyber-Yoda",
        "theme": "cyberpunk",
        "cybernetic_enhancements": ["Neural Interface", "Holo-projector"]
    }, "Convert to cyberpunk theme")
    await graph.add_node(yoda_id, NodeType.THEME, {
        "name": "Cyber-Yoda",
        "theme": "cyberpunk"
    }, parent_id=yoda_id)

    cyber_saber_id = await db.create_themed_variant(saber_id, "cyberpunk")
    await db.commit_changes(saber_id, cyber_saber_id, {
        "name": "Energy Blade",
        "theme": "cyberpunk",
        "damage_type": "energy"
    }, "Convert to cyberpunk theme")

    # Chapter 3: Cosmic theme
    # Yoda builds on cyberpunk experiences
    cosmic_yoda_id = await db.create_themed_variant(yoda_id, "cosmic")
    await db.commit_changes(yoda_id, cosmic_yoda_id, {
        "name": "Cosmic Yoda",
        "theme": "cosmic",
        "cosmic_powers": ["Star Manipulation", "Void Walking"],
        # Keeps cybernetic enhancements from previous theme
        "cybernetic_enhancements": ["Neural Interface", "Holo-projector"]
    }, "Convert to cosmic theme")
    await graph.add_node(yoda_id, NodeType.THEME, {
        "name": "Cosmic Yoda",
        "theme": "cosmic"
    }, parent_id=cyber_yoda_id)  # Branches from cyberpunk version

    # Lightsaber reverts to root and gets new theme
    cosmic_saber_id = await db.create_themed_variant(saber_id, "cosmic")
    await db.commit_changes(saber_id, cosmic_saber_id, {
        "name": "Star Blade",
        "theme": "cosmic",
        "damage_type": "cosmic"
    }, "Convert to cosmic theme")

    # Chapter 4: Back to fantasy
    # Get states for both
    yoda_state = await db.get_entity_state(yoda_id)  # Gets main branch
    saber_state = await db.get_entity_state(saber_id)  # Gets main branch

    # Demonstrate the difference
    print("Yoda's progression through themes:")
    yoda_diagram = await graph.generate_mermaid_diagram(yoda_id)
    print(yoda_diagram)

    print("\nLightsaber's progression (always from root):")
    saber_diagram = await graph.generate_mermaid_diagram(saber_id)
    print(saber_diagram)

    # Show retained character experiences
    print("\nYoda's final state when returning to fantasy theme:")
    final_yoda = await db.get_entity_state(yoda_id)
    print(f"- Still remembers cybernetic enhancements: {final_yoda.get('cybernetic_enhancements')}")
    print(f"- Still has cosmic powers: {final_yoda.get('cosmic_powers')}")

    print("\nLightsaber's final state when returning to fantasy theme:")
    final_saber = await db.get_entity_state(saber_id)
    print(f"- Basic lightsaber properties: {final_saber}")  # Just original stats

"""
This would produce diagrams like:

Yoda's progression:
```mermaid
graph TD
    yoda_0()["[root] Yoda (Fantasy)"]
    yoda_1[()]["[theme] Cyber-Yoda (Cyberpunk)"]
    yoda_2[()]["[theme] Cosmic Yoda (Cosmic)"]
    yoda_0 -.-=> yoda_1
    yoda_1 -.-=> yoda_2
```

Lightsaber's progression:
```mermaid
graph TD
    saber_0()["[root] Lightsaber (Fantasy)"]
    saber_1[()]["[theme] Energy Blade (Cyberpunk)"]
    saber_2[()]["[theme] Star Blade (Cosmic)"]
    saber_0 -.-=> saber_1
    saber_0 -.-=> saber_2
```

Note how the lightsaber variants all branch from root, while Yoda's
themes build upon each other, preserving experiences and growth.
"""
