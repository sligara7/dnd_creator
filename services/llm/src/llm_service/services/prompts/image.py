"""Image generation prompt templates."""
from typing import Dict, Optional

def get_character_portrait_prompt(
    character_class: str,
    character_race: str,
    character_level: int,
    equipment: Optional[Dict[str, str]] = None,
    theme: Optional[Dict[str, str]] = None
) -> str:
    """Create prompt for character portrait generation."""
    prompt = f"Portrait of a {character_race} {character_class}, level {character_level}. "
    
    if equipment:
        armor = equipment.get("armor", "")
        weapon = equipment.get("weapon", "")
        items = equipment.get("items", [])
        
        if armor:
            prompt += f"Wearing {armor}. "
        if weapon:
            prompt += f"Wielding {weapon}. "
        if items:
            prompt += f"Equipped with {', '.join(items)}. "
    
    if theme:
        style = theme.get("style", "")
        tone = theme.get("tone", "")
        details = theme.get("details", "")
        
        if style:
            prompt += f"Art style: {style}. "
        if tone:
            prompt += f"Mood/tone: {tone}. "
        if details:
            prompt += f"{details}. "
    
    return prompt.strip()


def get_character_action_prompt(
    character_class: str,
    character_race: str,
    action_type: str,
    equipment: Optional[Dict[str, str]] = None,
    theme: Optional[Dict[str, str]] = None
) -> str:
    """Create prompt for character action scene."""
    prompt = f"{character_race} {character_class} "
    
    if action_type == "combat":
        prompt += "engaged in dynamic combat, "
    elif action_type == "spellcasting":
        prompt += "casting a powerful spell, "
    elif action_type == "stealth":
        prompt += "moving stealthily through shadows, "
    else:
        prompt += f"performing {action_type}, "
    
    if equipment:
        armor = equipment.get("armor", "")
        weapon = equipment.get("weapon", "")
        
        if armor:
            prompt += f"clad in {armor}, "
        if weapon:
            prompt += f"wielding {weapon}, "
    
    if theme:
        style = theme.get("style", "")
        tone = theme.get("tone", "")
        
        if style:
            prompt += f"in {style} style, "
        if tone:
            prompt += f"with {tone} atmosphere, "
    
    return prompt.strip().rstrip(",") + "."


def get_location_prompt(
    location_type: str,
    size: str,
    purpose: str,
    features: Optional[list[str]] = None,
    theme: Optional[Dict[str, str]] = None
) -> str:
    """Create prompt for location visualization."""
    prompt = f"A {size} {location_type} serving as {purpose}. "
    
    if features:
        prompt += "Notable features include: " + ", ".join(features) + ". "
    
    if theme:
        style = theme.get("style", "")
        lighting = theme.get("lighting", "")
        weather = theme.get("weather", "")
        time = theme.get("time", "")
        
        if style:
            prompt += f"Art style: {style}. "
        if lighting:
            prompt += f"Lighting: {lighting}. "
        if weather:
            prompt += f"Weather: {weather}. "
        if time:
            prompt += f"Time of day: {time}. "
    
    return prompt.strip()


def get_map_prompt(
    location_type: str,
    size: str,
    important_areas: Optional[list[str]] = None,
    style: str = "fantasy map",
    details: Optional[Dict[str, str]] = None
) -> str:
    """Create prompt for map generation."""
    prompt = f"A {style} of a {size} {location_type}. "
    
    if important_areas:
        prompt += "Key areas include: " + ", ".join(important_areas) + ". "
    
    if details:
        terrain = details.get("terrain", "")
        landmarks = details.get("landmarks", "")
        borders = details.get("borders", "")
        
        if terrain:
            prompt += f"Terrain: {terrain}. "
        if landmarks:
            prompt += f"Landmarks: {landmarks}. "
        if borders:
            prompt += f"Borders: {borders}. "
    
    return prompt.strip()


def get_item_prompt(
    item_type: str,
    rarity: str = "common",
    magical: bool = False,
    properties: Optional[Dict[str, str]] = None,
    theme: Optional[Dict[str, str]] = None
) -> str:
    """Create prompt for item illustration."""
    prompt = f"A {rarity} "
    if magical:
        prompt += "magical "
    prompt += f"{item_type}. "
    
    if properties:
        appearance = properties.get("appearance", "")
        material = properties.get("material", "")
        effects = properties.get("effects", "")
        
        if appearance:
            prompt += f"Appearance: {appearance}. "
        if material:
            prompt += f"Made of {material}. "
        if effects and magical:
            prompt += f"Magical effects: {effects}. "
    
    if theme:
        style = theme.get("style", "")
        tone = theme.get("tone", "")
        
        if style:
            prompt += f"Art style: {style}. "
        if tone:
            prompt += f"Mood/tone: {tone}. "
    
    return prompt.strip()


def get_style_transfer_prompt(
    style: str,
    preserve_content: bool = True,
    intensity: float = 0.8,
    content_type: Optional[str] = None
) -> str:
    """Create prompt for style transfer."""
    prompt = f"Apply {style} art style"
    
    if preserve_content:
        prompt += " while preserving original content and composition"
    
    if content_type:
        prompt += f", optimized for {content_type} imagery"
    
    prompt += f". Style transfer intensity: {intensity}"
    
    return prompt + "."


def get_enhancement_prompt(
    enhancement_type: str,
    parameters: Optional[Dict[str, str]] = None
) -> str:
    """Create prompt for image enhancement."""
    if enhancement_type == "face":
        prompt = "Enhance and improve facial features, ensuring natural appearance"
        if parameters and parameters.get("focus_areas"):
            prompt += f", focusing on {parameters['focus_areas']}"
    
    elif enhancement_type == "details":
        prompt = "Enhance image details and clarity"
        if parameters and parameters.get("strength"):
            prompt += f" with {parameters['strength']} intensity"
    
    elif enhancement_type == "lighting":
        prompt = "Optimize image lighting and contrast"
        if parameters and parameters.get("style"):
            prompt += f" in {parameters['style']} style"
    
    else:
        prompt = f"Apply {enhancement_type} enhancement"
        if parameters and parameters.get("details"):
            prompt += f": {parameters['details']}"
    
    return prompt + "."
