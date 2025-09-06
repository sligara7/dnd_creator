"""Content parsing utilities for campaign content."""
import re
from typing import Dict, List, Optional

import structlog
from pydantic import BaseModel

from ..core.exceptions import ParsingError
from ..schemas.campaign import StoryElement


class StoryParts(BaseModel):
    """Parsed story content parts."""
    title: str
    description: str
    plot_points: List[str]
    npcs: List[Dict[str, str]]
    locations: List[Dict[str, str]]
    hooks: List[str]
    summary: str


class NPCParts(BaseModel):
    """Parsed NPC parts."""
    name: str
    title: Optional[str]
    description: str
    personality: str
    motivations: List[str]
    secrets: List[str]
    relationships: Dict[str, str]
    summary: str


class LocationParts(BaseModel):
    """Parsed location parts."""
    name: str
    description: str
    points_of_interest: List[str]
    occupants: List[str]
    secrets: List[str]
    hooks: List[str]
    summary: str


def parse_story_content(content: str, element_type: StoryElement) -> StoryParts:
    """Parse generated story content into structured parts."""
    try:
        logger = structlog.get_logger()
        
        # Extract title (usually the first line)
        lines = content.strip().split("\n")
        title = lines[0].strip()
        
        # Extract description (usually the first paragraph after title)
        description = ""
        plot_points = []
        npcs = []
        locations = []
        hooks = []
        current_section = None
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            lower_line = line.lower()
            if any(marker in lower_line for marker in ["plot point", "story beat", "event"]):
                current_section = "plot"
            elif any(marker in lower_line for marker in ["character", "npc", "notable figure"]):
                current_section = "npc"
            elif any(marker in lower_line for marker in ["location", "place", "area"]):
                current_section = "location"
            elif any(marker in lower_line for marker in ["hook", "lead", "possibility"]):
                current_section = "hook"
            elif not current_section and len(description.split()) < 100:
                description += " " + line
                continue
                
            # Parse content based on section
            if current_section == "plot":
                match = re.match(r"^[0-9.-]*\s*(.+)$", line)
                if match and not any(marker in lower_line for marker in ["plot point", "story beat"]):
                    plot_points.append(match.group(1))
            elif current_section == "npc":
                if ":" in line and not any(marker in lower_line for marker in ["character", "npc"]):
                    name, desc = line.split(":", 1)
                    npcs.append({"name": name.strip(), "description": desc.strip()})
            elif current_section == "location":
                if ":" in line and not any(marker in lower_line for marker in ["location", "place"]):
                    name, desc = line.split(":", 1)
                    locations.append({"name": name.strip(), "description": desc.strip()})
            elif current_section == "hook":
                match = re.match(r"^[0-9.-]*\s*(.+)$", line)
                if match and not any(marker in lower_line for marker in ["hook", "lead"]):
                    hooks.append(match.group(1))
                    
        # Generate summary
        summary = f"{len(plot_points)} plot points"
        if npcs:
            summary += f", {len(npcs)} NPCs"
        if locations:
            summary += f", {len(locations)} locations"
        if hooks:
            summary += f", {len(hooks)} hooks"
            
        return StoryParts(
            title=title,
            description=description.strip(),
            plot_points=plot_points,
            npcs=npcs,
            locations=locations,
            hooks=hooks,
            summary=summary
        )
        
    except Exception as e:
        logger.error("story_content_parsing_failed", error=str(e))
        raise ParsingError(f"Failed to parse story content: {str(e)}")


def parse_npc_content(content: str) -> NPCParts:
    """Parse generated NPC content into structured parts."""
    try:
        logger = structlog.get_logger()
        
        # Initialize parts
        name = ""
        title = None
        description = ""
        personality = ""
        motivations = []
        secrets = []
        relationships = {}
        
        # Parse sections
        current_section = None
        section_content = []
        
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for name/title in first line
            if not name and ":" in line:
                name_part = line.split(":", 1)[0]
                if "," in name_part:
                    name, title = map(str.strip, name_part.split(",", 1))
                else:
                    name = name_part.strip()
                continue
                
            # Check for sections
            lower_line = line.lower()
            if "description" in lower_line or "appearance" in lower_line:
                if section_content and current_section != "description":
                    _process_npc_section(current_section, section_content, locals())
                current_section = "description"
                section_content = []
            elif "personality" in lower_line or "behavior" in lower_line:
                if section_content:
                    _process_npc_section(current_section, section_content, locals())
                current_section = "personality"
                section_content = []
            elif "motivation" in lower_line or "goal" in lower_line:
                if section_content:
                    _process_npc_section(current_section, section_content, locals())
                current_section = "motivation"
                section_content = []
            elif "secret" in lower_line or "hidden" in lower_line:
                if section_content:
                    _process_npc_section(current_section, section_content, locals())
                current_section = "secret"
                section_content = []
            elif "relationship" in lower_line or "connection" in lower_line:
                if section_content:
                    _process_npc_section(current_section, section_content, locals())
                current_section = "relationship"
                section_content = []
            else:
                section_content.append(line)
                
        # Process final section
        if section_content:
            _process_npc_section(current_section, section_content, locals())
            
        # Generate summary
        summary_parts = []
        if title:
            summary_parts.append(title)
        if personality:
            summary_parts.append(personality.split(".", 1)[0])
        if motivations:
            summary_parts.append(f"seeks {motivations[0].lower()}")
            
        summary = f"{name}, " + " - ".join(summary_parts)
        
        return NPCParts(
            name=name,
            title=title,
            description=description.strip(),
            personality=personality.strip(),
            motivations=motivations,
            secrets=secrets,
            relationships=relationships,
            summary=summary
        )
        
    except Exception as e:
        logger.error("npc_content_parsing_failed", error=str(e))
        raise ParsingError(f"Failed to parse NPC content: {str(e)}")


def _process_npc_section(section: str, content: List[str], data: Dict):
    """Process NPC content section."""
    text = " ".join(content)
    if section == "description":
        data["description"] = text
    elif section == "personality":
        data["personality"] = text
    elif section == "motivation":
        # Extract motivations from bullet points or numbered lists
        data["motivations"].extend(
            item.strip() for item in re.split(r"[•-]|\d+\.", text)
            if item.strip()
        )
    elif section == "secret":
        # Extract secrets from bullet points or numbered lists
        data["secrets"].extend(
            item.strip() for item in re.split(r"[•-]|\d+\.", text)
            if item.strip()
        )
    elif section == "relationship":
        # Parse relationship entries (Name: relationship)
        for line in content:
            if ":" in line:
                name, rel = line.split(":", 1)
                data["relationships"][name.strip()] = rel.strip()


def parse_location_content(content: str) -> LocationParts:
    """Parse generated location content into structured parts."""
    try:
        logger = structlog.get_logger()
        
        # Initialize parts
        name = ""
        description = ""
        points_of_interest = []
        occupants = []
        secrets = []
        hooks = []
        
        # Parse sections
        current_section = None
        section_content = []
        
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Extract name from first line
            if not name and ":" in line:
                name = line.split(":", 1)[0].strip()
                continue
                
            # Check for sections
            lower_line = line.lower()
            if "description" in lower_line or "overview" in lower_line:
                if section_content and current_section != "description":
                    _process_location_section(current_section, section_content, locals())
                current_section = "description"
                section_content = []
            elif any(x in lower_line for x in ["point of interest", "feature", "notable"]):
                if section_content:
                    _process_location_section(current_section, section_content, locals())
                current_section = "poi"
                section_content = []
            elif "occupant" in lower_line or "inhabitant" in lower_line:
                if section_content:
                    _process_location_section(current_section, section_content, locals())
                current_section = "occupant"
                section_content = []
            elif "secret" in lower_line or "mystery" in lower_line:
                if section_content:
                    _process_location_section(current_section, section_content, locals())
                current_section = "secret"
                section_content = []
            elif "hook" in lower_line or "plot" in lower_line:
                if section_content:
                    _process_location_section(current_section, section_content, locals())
                current_section = "hook"
                section_content = []
            else:
                section_content.append(line)
                
        # Process final section
        if section_content:
            _process_location_section(current_section, section_content, locals())
            
        # Generate summary
        summary_parts = []
        if points_of_interest:
            summary_parts.append(f"{len(points_of_interest)} points of interest")
        if occupants:
            summary_parts.append(f"{len(occupants)} occupants")
        if secrets:
            summary_parts.append(f"{len(secrets)} secrets")
        if hooks:
            summary_parts.append(f"{len(hooks)} hooks")
            
        summary = f"{name} - " + ", ".join(summary_parts)
        
        return LocationParts(
            name=name,
            description=description.strip(),
            points_of_interest=points_of_interest,
            occupants=occupants,
            secrets=secrets,
            hooks=hooks,
            summary=summary
        )
        
    except Exception as e:
        logger.error("location_content_parsing_failed", error=str(e))
        raise ParsingError(f"Failed to parse location content: {str(e)}")


def _process_location_section(section: str, content: List[str], data: Dict):
    """Process location content section."""
    text = " ".join(content)
    if section == "description":
        data["description"] = text
    elif section == "poi":
        # Extract points of interest from bullet points or numbered lists
        data["points_of_interest"].extend(
            item.strip() for item in re.split(r"[•-]|\d+\.", text)
            if item.strip()
        )
    elif section == "occupant":
        # Extract occupants from bullet points or numbered lists
        data["occupants"].extend(
            item.strip() for item in re.split(r"[•-]|\d+\.", text)
            if item.strip()
        )
    elif section == "secret":
        # Extract secrets from bullet points or numbered lists
        data["secrets"].extend(
            item.strip() for item in re.split(r"[•-]|\d+\.", text)
            if item.strip()
        )
    elif section == "hook":
        # Extract hooks from bullet points or numbered lists
        data["hooks"].extend(
            item.strip() for item in re.split(r"[•-]|\d+\.", text)
            if item.strip()
        )
