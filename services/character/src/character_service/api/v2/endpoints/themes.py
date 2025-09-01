"""Theme and version management endpoints."""

from uuid import UUID
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.services.theme_service import ThemeService
from character_service.core.database import get_db
from character_service.models.version import VersionNodeType, EdgeType

# Define response and request models (Pydantic models)
from character_service.schemas.themes import (
    ThemeTransitionRequest,
    ThemeTransitionResponse,
    VersionGraphResponse,
    VersionNodeResponse,
)

router = APIRouter()

@router.post("/characters/{character_id}/theme-transition",
           response_model=ThemeTransitionResponse,
           status_code=status.HTTP_200_OK)
async def transition_theme(
    character_id: UUID,
    request: ThemeTransitionRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Transition a character to a new theme.
    
    This endpoint:
    1. Creates a new character version with the new theme
    2. Preserves character memory (journal/relationships)
    3. Handles equipment theme transitions (reset/adapt)
    4. Updates version graph relationships
    """
    theme_service = ThemeService(db)
    try:
        result = await theme_service.transition_theme(
            character_id=character_id,
            new_theme=request.new_theme,
            chapter_id=request.chapter_id,
            equipment_transitions=request.equipment_transitions
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transitioning theme: {str(e)}"
        )

@router.get("/characters/{character_id}/version-graph",
          response_model=VersionGraphResponse)
async def get_character_version_graph(
    character_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the version graph for a character.
    
    Returns the complete version graph including:
    - All character versions
    - Equipment relationships
    - Theme transitions
    """
    theme_service = ThemeService(db)
    try:
        # Get character's graph node
        graph = await theme_service.version_repo.get_node_by_entity(
            character_id, VersionNodeType.CHARACTER)
        if not graph:
            raise ValueError(f"No version graph found for character {character_id}")
            
        # Get full graph state
        state = await theme_service._get_graph_state(graph.graph_id)
        return {
            "graph_id": str(graph.graph_id),
            "nodes": state["nodes"],
            "edges": state["edges"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting version graph: {str(e)}"
        )

@router.get("/characters/{character_id}/version-chain",
          response_model=List[VersionNodeResponse])
async def get_character_version_chain(
    character_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get the version chain for a character.
    
    Returns ordered list of character versions showing the progression
    through different themes.
    """
    theme_service = ThemeService(db)
    try:
        # Get character's current node
        node = await theme_service.version_repo.get_node_by_entity(
            character_id, VersionNodeType.CHARACTER)
        if not node:
            raise ValueError(f"No version history found for character {character_id}")
            
        # Get full version chain
        chain = await theme_service.version_repo.get_node_chain(
            node.id, EdgeType.PARENT)
            
        return [
            {
                "id": str(node.id),
                "entity_id": str(node.entity_id),
                "type": node.type,
                "theme": node.theme,
                "metadata": node.metadata
            }
            for node in chain
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting version chain: {str(e)}"
        )

@router.get("/characters/{character_id}/equipment-versions/{item_id}",
          response_model=List[VersionNodeResponse])
async def get_equipment_versions(
    character_id: UUID,
    item_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all theme versions of a piece of equipment.
    
    Returns all versions of the equipment including:
    - Root version
    - Theme adaptations
    - Usage relationships
    """
    theme_service = ThemeService(db)
    try:
        # Get item's node
        node = await theme_service.version_repo.get_node_by_entity(
            item_id, VersionNodeType.EQUIPMENT)
        if not node:
            raise ValueError(f"No version history found for item {item_id}")
            
        # Get root chain and relationships
        root_chain = await theme_service.version_repo.get_node_chain(
            node.id, EdgeType.ROOT)
        relationships = await theme_service.version_repo.get_node_relationships(
            node.id)
            
        # Combine into full version set
        versions = set()
        versions.update(root_chain)
        versions.update(node for _, node in relationships)
            
        return [
            {
                "id": str(node.id),
                "entity_id": str(node.entity_id),
                "type": node.type,
                "theme": node.theme,
                "metadata": node.metadata
            }
            for node in versions
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting equipment versions: {str(e)}"
        )
