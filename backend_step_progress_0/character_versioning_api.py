"""
Example API endpoints for the Character Versioning System.
This shows how to integrate the Git-like character versioning with FastAPI.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from database_models_new import (
    get_db, CharacterRepositoryManager, CharacterVersioningAPI,
    CharacterRepository, CharacterBranch, CharacterCommit
)

router = APIRouter(prefix="/api/character-versioning", tags=["Character Versioning"])

# ============================================================================
# REPOSITORY MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/repositories", response_model=Dict[str, Any])
async def create_character_repository(
    character_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Create a new character repository with initial commit.
    
    Example request:
    {
        "name": "Gandalf the Grey",
        "player_name": "Tolkien",
        "species": "Wizard",
        "level": 1,
        "character_classes": {"Wizard": 1},
        "abilities": {"strength": 10, "intelligence": 18, ...},
        "description": "A wise wizard character"
    }
    """
    try:
        result = CharacterVersioningAPI.create_new_character_repository(db, character_data)
        return {
            "success": True,
            "repository_id": result["repository_id"],
            "repository_uuid": result["repository_uuid"],
            "initial_commit_hash": result["initial_commit_hash"],
            "message": f"Created character repository for {character_data.get('name', 'New Character')}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create repository: {str(e)}")


@router.get("/repositories/{repository_id}/tree")
async def get_repository_tree(
    repository_id: int,
    db: Session = Depends(get_db)
):
    """
    Get complete repository structure for visualization.
    Returns data formatted for frontend graph display.
    """
    try:
        tree_data = CharacterVersioningAPI.get_character_timeline_for_frontend(db, repository_id)
        if not tree_data:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        return {
            "success": True,
            "data": tree_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get repository tree: {str(e)}")


# ============================================================================
# BRANCH MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/repositories/{repository_id}/branches")
async def create_branch(
    repository_id: int,
    branch_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Create a new branch from a specific commit.
    
    Example request:
    {
        "branch_name": "multiclass-fighter",
        "source_commit_hash": "abcd1234...",
        "description": "Exploring multiclass with Fighter"
    }
    """
    try:
        branch = CharacterRepositoryManager.create_branch(
            db=db,
            repository_id=repository_id,
            new_branch_name=branch_data["branch_name"],
            source_commit_hash=branch_data["source_commit_hash"],
            description=branch_data.get("description")
        )
        
        return {
            "success": True,
            "branch": branch.to_dict(),
            "message": f"Created branch '{branch_data['branch_name']}'"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create branch: {str(e)}")


@router.get("/repositories/{repository_id}/branches")
async def list_branches(
    repository_id: int,
    db: Session = Depends(get_db)
):
    """List all branches in a repository."""
    try:
        branches = db.query(CharacterBranch).filter(
            CharacterBranch.repository_id == repository_id
        ).all()
        
        return {
            "success": True,
            "branches": [branch.to_dict() for branch in branches]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to list branches: {str(e)}")


# ============================================================================
# COMMIT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/repositories/{repository_id}/commits")
async def create_commit(
    repository_id: int,
    commit_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Create a new commit with character changes.
    
    Example request:
    {
        "branch_name": "main",
        "character_data": {...},
        "commit_message": "Level 2: Gained Arcane Recovery",
        "commit_type": "level_up",
        "milestone_name": "First Level Up",
        "campaign_context": "After defeating the goblins"
    }
    """
    try:
        commit = CharacterRepositoryManager.commit_character_change(
            db=db,
            repository_id=repository_id,
            branch_name=commit_data["branch_name"],
            character_data=commit_data["character_data"],
            commit_message=commit_data["commit_message"],
            commit_type=commit_data.get("commit_type", "update"),
            milestone_name=commit_data.get("milestone_name"),
            campaign_context=commit_data.get("campaign_context"),
            created_by=commit_data.get("created_by")
        )
        
        return {
            "success": True,
            "commit": commit.to_dict(),
            "message": f"Created commit {commit.short_hash}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create commit: {str(e)}")


@router.get("/repositories/{repository_id}/commits")
async def get_commit_history(
    repository_id: int,
    branch_name: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get commit history for a repository or branch."""
    try:
        commits = CharacterRepositoryManager.get_commit_history(
            db=db,
            repository_id=repository_id,
            branch_name=branch_name,
            limit=limit
        )
        
        return {
            "success": True,
            "commits": [commit.to_dict() for commit in commits],
            "total": len(commits)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get commit history: {str(e)}")


@router.get("/commits/{commit_hash}/character")
async def get_character_at_commit(
    commit_hash: str,
    db: Session = Depends(get_db)
):
    """Get character data at a specific commit."""
    try:
        character_data = CharacterRepositoryManager.get_character_at_commit(db, commit_hash)
        if not character_data:
            raise HTTPException(status_code=404, detail="Commit not found")
        
        return {
            "success": True,
            "character_data": character_data,
            "commit_hash": commit_hash
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get character data: {str(e)}")


# ============================================================================
# LEVEL UP ENDPOINT (HIGH-LEVEL OPERATION)
# ============================================================================

@router.post("/repositories/{repository_id}/level-up")
async def level_up_character(
    repository_id: int,
    level_up_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Handle character level up with automatic commit creation.
    
    Example request:
    {
        "branch_name": "main",
        "new_character_data": {...},
        "level_info": {
            "old_level": 1,
            "new_level": 2,
            "class_leveled": "Wizard",
            "asi_applied": false
        },
        "session_context": "Session 3: Tower Defense"
    }
    """
    try:
        result = CharacterVersioningAPI.level_up_character(
            db=db,
            repository_id=repository_id,
            branch_name=level_up_data["branch_name"],
            new_character_data=level_up_data["new_character_data"],
            level_info=level_up_data["level_info"]
        )
        
        return {
            "success": True,
            "commit": result,
            "message": f"Character leveled up to {level_up_data['level_info']['new_level']}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to level up character: {str(e)}")


# ============================================================================
# VISUALIZATION ENDPOINTS
# ============================================================================

@router.get("/repositories/{repository_id}/visualization")
async def get_visualization_data(
    repository_id: int,
    db: Session = Depends(get_db)
):
    """
    Get data formatted specifically for frontend graph visualization.
    Returns nodes, edges, and layout information for the character timeline.
    """
    try:
        timeline_data = CharacterVersioningAPI.get_character_timeline_for_frontend(db, repository_id)
        if not timeline_data:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Format for graph visualization library (e.g., D3.js, vis.js, etc.)
        nodes = []
        edges = []
        
        # Create nodes for each commit
        for commit in timeline_data["commits"]:
            nodes.append({
                "id": commit["id"],
                "label": f"Level {commit['level']}\\n{commit['message'][:30]}...",
                "level": commit["level"],
                "type": commit["type"],
                "branch": commit["branch"],
                "color": get_commit_color(commit["type"]),
                "size": get_commit_size(commit["level"]),
                "title": commit["message"]  # Hover tooltip
            })
        
        # Create edges for commit relationships
        for connection in timeline_data["connections"]:
            edges.append({
                "from": connection["from"],
                "to": connection["to"],
                "type": connection["type"],
                "color": get_edge_color(connection["type"])
            })
        
        return {
            "success": True,
            "visualization": {
                "nodes": nodes,
                "edges": edges,
                "character_name": timeline_data["character_name"],
                "player_name": timeline_data["player_name"],
                "branches": timeline_data["branches"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get visualization data: {str(e)}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_commit_color(commit_type: str) -> str:
    """Get color for commit based on type."""
    colors = {
        "initial": "#4CAF50",     # Green
        "level_up": "#2196F3",    # Blue
        "equipment": "#FF9800",   # Orange
        "story": "#9C27B0",       # Purple
        "death": "#F44336",       # Red
        "resurrection": "#00BCD4", # Cyan
        "update": "#607D8B"       # Blue Grey
    }
    return colors.get(commit_type, "#607D8B")

def get_commit_size(level: int) -> int:
    """Get node size based on character level."""
    return min(20 + level * 2, 60)  # Scale with level, max size 60

def get_edge_color(edge_type: str) -> str:
    """Get edge color based on relationship type."""
    colors = {
        "progression": "#666666",
        "branch": "#FF5722",
        "merge": "#4CAF50"
    }
    return colors.get(edge_type, "#666666")


# ============================================================================
# USAGE EXAMPLE FOR FRONTEND
# ============================================================================

"""
FRONTEND USAGE EXAMPLE (JavaScript/React):

1. Create a new character repository:
   ```javascript
   const createCharacter = async (characterData) => {
     const response = await fetch('/api/character-versioning/repositories', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify(characterData)
     });
     return response.json();
   };
   ```

2. Get visualization data:
   ```javascript
   const getCharacterTimeline = async (repositoryId) => {
     const response = await fetch(`/api/character-versioning/repositories/${repositoryId}/visualization`);
     const data = await response.json();
     
     // Use with vis.js or D3.js for graph visualization
     const network = new vis.Network(container, {
       nodes: data.visualization.nodes,
       edges: data.visualization.edges
     }, options);
   };
   ```

3. Level up character:
   ```javascript
   const levelUpCharacter = async (repositoryId, levelUpData) => {
     const response = await fetch(`/api/character-versioning/repositories/${repositoryId}/level-up`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify(levelUpData)
     });
     return response.json();
   };
   ```

4. Create alternate branch:
   ```javascript
   const createAlternatePath = async (repositoryId, branchData) => {
     const response = await fetch(`/api/character-versioning/repositories/${repositoryId}/branches`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify(branchData)
     });
     return response.json();
   };
   ```

This creates a rich, interactive character development experience where players can:
- See their character's complete development history
- Explore "what-if" scenarios with branches
- Compare different character builds
- Rollback to previous states
- Visualize their character's journey as an interactive timeline
"""
