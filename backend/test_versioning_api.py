#!/usr/bin/env python3
"""
Example usage of the Character Versioning REST API.
This demonstrates how the frontend would interact with the Git-like character versioning system.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

# Base API URL (adjust as needed)
BASE_URL = "http://localhost:8000/api/v1"

class CharacterVersioningAPIClient:
    """Client for interacting with the Character Versioning API."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
    
    async def create_character_repository(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new character repository with initial commit."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/character-repositories",
                json=character_data
            ) as response:
                return await response.json()
    
    async def get_character_timeline(self, repository_id: int) -> Dict[str, Any]:
        """Get character timeline for visualization."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/character-repositories/{repository_id}/timeline"
            ) as response:
                return await response.json()
    
    async def get_character_visualization(self, repository_id: int) -> Dict[str, Any]:
        """Get character visualization data for graph libraries."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/character-repositories/{repository_id}/visualization"
            ) as response:
                return await response.json()
    
    async def create_branch(self, repository_id: int, branch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new character development branch."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/character-repositories/{repository_id}/branches",
                json=branch_data
            ) as response:
                return await response.json()
    
    async def create_commit(self, repository_id: int, commit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new character commit."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/character-repositories/{repository_id}/commits",
                json=commit_data
            ) as response:
                return await response.json()
    
    async def level_up_character(self, repository_id: int, level_up_data: Dict[str, Any]) -> Dict[str, Any]:
        """Level up character with auto-commit."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/character-repositories/{repository_id}/level-up",
                json=level_up_data
            ) as response:
                return await response.json()
    
    async def get_character_at_commit(self, commit_hash: str) -> Dict[str, Any]:
        """Get character data at specific commit."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/character-commits/{commit_hash}/character"
            ) as response:
                return await response.json()


async def demo_character_versioning():
    """Demonstrate the character versioning workflow."""
    client = CharacterVersioningAPIClient()
    
    print("🎲 Character Versioning API Demo")
    print("=" * 50)
    
    # Step 1: Create initial character repository
    print("\n1. Creating initial character repository...")
    
    initial_character = {
        "name": "Gandalf the Grey",
        "player_name": "Tolkien",
        "description": "A wise wizard character with multiple storylines",
        "character_data": {
            "name": "Gandalf the Grey",
            "species": "Maiar",
            "level": 1,
            "character_classes": {"Wizard": 1},
            "abilities": {
                "strength": 12,
                "dexterity": 14,
                "constitution": 16,
                "intelligence": 20,
                "wisdom": 18,
                "charisma": 16
            },
            "backstory": "A wise wizard sent to Middle-earth to guide and protect the free peoples.",
            "equipment": {"staff": "Staff of Power", "robe": "Grey Robes"},
            "experience_points": 0
        }
    }
    
    try:
        repo_response = await client.create_character_repository(initial_character)
        print(f"✅ Repository created: {repo_response['name']}")
        print(f"   Repository ID: {repo_response['id']}")
        print(f"   Initial commit: {repo_response['initial_commit_hash']}")
        
        repository_id = repo_response['id']
    except Exception as e:
        print(f"❌ Failed to create repository: {e}")
        return
    
    # Step 2: Level up the character (main branch)
    print("\n2. Leveling up character to level 2...")
    
    level_2_data = initial_character["character_data"].copy()
    level_2_data.update({
        "level": 2,
        "character_classes": {"Wizard": 2},
        "experience_points": 300,
        "features": {"Arcane Recovery": "Recover spell slots on short rest"}
    })
    
    level_up_request = {
        "branch_name": "main",
        "new_character_data": level_2_data,
        "level_info": {
            "old_level": 1,
            "new_level": 2,
            "class_leveled": "Wizard",
            "asi_applied": False
        },
        "session_context": "Session 1: First adventure completed"
    }
    
    try:
        level_up_response = await client.level_up_character(repository_id, level_up_request)
        print(f"✅ Character leveled up!")
        print(f"   Commit hash: {level_up_response['level_up']['commit_hash']}")
        level_2_commit = level_up_response['level_up']['commit_hash']
    except Exception as e:
        print(f"❌ Failed to level up: {e}")
        return
    
    # Step 3: Create an alternate branch for multiclass exploration
    print("\n3. Creating alternate multiclass branch...")
    
    branch_data = {
        "branch_name": "multiclass-fighter",
        "source_commit_hash": level_2_commit,
        "description": "Exploring what if Gandalf became a wizard/fighter multiclass"
    }
    
    try:
        branch_response = await client.create_branch(repository_id, branch_data)
        print(f"✅ Branch created: {branch_response['branch_name']}")
        print(f"   Description: {branch_response['description']}")
    except Exception as e:
        print(f"❌ Failed to create branch: {e}")
        return
    
    # Step 4: Commit multiclass level on the new branch
    print("\n4. Committing multiclass progression...")
    
    multiclass_data = level_2_data.copy()
    multiclass_data.update({
        "level": 3,
        "character_classes": {"Wizard": 2, "Fighter": 1},
        "experience_points": 900,
        "features": {
            "Arcane Recovery": "Recover spell slots on short rest",
            "Fighting Style": "Defense (+1 AC when wearing armor)",
            "Second Wind": "Heal 1d10+1 hit points as bonus action"
        }
    })
    
    multiclass_commit = {
        "branch_name": "multiclass-fighter",
        "character_data": multiclass_data,
        "commit_message": "Level 3: Multiclassed into Fighter",
        "commit_type": "level_up",
        "milestone_name": "Multiclass Experiment",
        "campaign_context": "What if Gandalf learned sword fighting?",
        "created_by": "Player"
    }
    
    try:
        commit_response = await client.create_commit(repository_id, multiclass_commit)
        print(f"✅ Multiclass commit created!")
        print(f"   Commit: {commit_response['short_hash']} - {commit_response['commit_message']}")
        multiclass_commit_hash = commit_response['commit_hash']
    except Exception as e:
        print(f"❌ Failed to create multiclass commit: {e}")
        return
    
    # Step 5: Get visualization data for frontend
    print("\n5. Getting visualization data for frontend...")
    
    try:
        viz_data = await client.get_character_visualization(repository_id)
        print(f"✅ Visualization data retrieved!")
        print(f"   Character: {viz_data['character_name']}")
        print(f"   Nodes: {len(viz_data['nodes'])} commits")
        print(f"   Edges: {len(viz_data['edges'])} connections")
        print(f"   Branches: {len(viz_data['branches'])} development paths")
        
        # Display commit nodes
        print("\n   📊 Commit Timeline:")
        for node in viz_data['nodes']:
            print(f"   {node['id']} | Level {node['level']} | {node['type']} | {node['title'][:50]}...")
        
    except Exception as e:
        print(f"❌ Failed to get visualization data: {e}")
        return
    
    # Step 6: Demonstrate character state retrieval at specific commits
    print("\n6. Retrieving character state at different commits...")
    
    try:
        # Get character at level 2 (before multiclass)
        level_2_character = await client.get_character_at_commit(level_2_commit)
        print(f"✅ Character at level 2 commit:")
        char_data = level_2_character['character_data']
        print(f"   Level: {char_data['level']}")
        print(f"   Classes: {char_data['character_classes']}")
        print(f"   XP: {char_data['experience_points']}")
        
        # Get character at multiclass commit
        multiclass_character = await client.get_character_at_commit(multiclass_commit_hash)
        print(f"\n✅ Character at multiclass commit:")
        char_data = multiclass_character['character_data']
        print(f"   Level: {char_data['level']}")
        print(f"   Classes: {char_data['character_classes']}")
        print(f"   XP: {char_data['experience_points']}")
        
    except Exception as e:
        print(f"❌ Failed to retrieve character states: {e}")
        return
    
    print("\n🎉 Character versioning demo completed!")
    print("\nThis demonstrates how the frontend can:")
    print("- Create character repositories with version control")
    print("- Track character development across multiple branches")
    print("- Visualize character evolution timelines")
    print("- Explore 'what-if' scenarios with branching")
    print("- Retrieve character states at any point in history")
    print("- Create rich, interactive character development experiences")


# Frontend JavaScript equivalent example
frontend_js_example = '''
// Frontend JavaScript example using the Character Versioning API

class CharacterVersioningClient {
    constructor(baseUrl = 'http://localhost:8000/api/v1') {
        this.baseUrl = baseUrl;
    }
    
    async createCharacterRepository(characterData) {
        const response = await fetch(`${this.baseUrl}/character-repositories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(characterData)
        });
        return response.json();
    }
    
    async getCharacterVisualization(repositoryId) {
        const response = await fetch(`${this.baseUrl}/character-repositories/${repositoryId}/visualization`);
        return response.json();
    }
    
    async createCharacterBranch(repositoryId, branchData) {
        const response = await fetch(`${this.baseUrl}/character-repositories/${repositoryId}/branches`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(branchData)
        });
        return response.json();
    }
    
    async levelUpCharacter(repositoryId, levelUpData) {
        const response = await fetch(`${this.baseUrl}/character-repositories/${repositoryId}/level-up`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(levelUpData)
        });
        return response.json();
    }
}

// Example usage in frontend
const client = new CharacterVersioningClient();

// Create character with versioning
const characterData = {
    name: "Aragorn",
    player_name: "Player1",
    character_data: { /* character details */ }
};
const repo = await client.createCharacterRepository(characterData);

// Get visualization data for graph library
const vizData = await client.getCharacterVisualization(repo.id);

// Use with vis.js or D3.js for interactive timeline
const network = new vis.Network(container, {
    nodes: vizData.nodes,
    edges: vizData.edges
}, options);

// Level up with automatic commit
const levelUpData = {
    branch_name: "main",
    new_character_data: { /* updated character */ },
    level_info: { old_level: 1, new_level: 2, class_leveled: "Ranger" }
};
await client.levelUpCharacter(repo.id, levelUpData);
'''

if __name__ == "__main__":
    try:
        asyncio.run(demo_character_versioning())
        
        print("\n" + "="*60)
        print("📝 FRONTEND INTEGRATION EXAMPLE")
        print("="*60)
        print(frontend_js_example)
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\nNote: This demo requires the FastAPI server to be running.")
        print("Start the server with: python backend/fastapi_main_new.py")
