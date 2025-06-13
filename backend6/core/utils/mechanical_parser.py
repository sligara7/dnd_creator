"""
Mechanical keyword extraction and parsing utilities.

This module provides functions to extract and analyze mechanical keywords
from content descriptions, supporting the Creative Content Framework's
mechanical validation and balance assessment.
"""

import re
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from ..enums.dnd_constants import Ability, DamageType, Condition
from ..enums.mechanical_category import MechanicalCategory


@dataclass
class MechanicalElement:
    """Represents a parsed mechanical element."""
    category: MechanicalCategory
    element_type: str
    value: str
    modifiers: List[str]
    context: str  # Original text context


# === MECHANICAL PATTERN DEFINITIONS ===

# Mechanical keyword patterns for each category
MECHANICAL_PATTERNS: Dict[MechanicalCategory, List[str]] = {
    
    MechanicalCategory.DAMAGE: [
        r"(\d+d\d+(?:\s*[+\-]\s*\d+)?)\s+(\w+)\s+damage",  # "2d6 fire damage"
        r"deals?\s+(\d+d\d+(?:\s*[+\-]\s*\d+)?)\s+(\w+)\s+damage",
        r"takes?\s+(\d+d\d+(?:\s*[+\-]\s*\d+)?)\s+(\w+)\s+damage",
        r"(\d+)\s+(\w+)\s+damage",  # "5 fire damage"
        r"(\d+d\d+(?:\s*[+\-]\s*\d+)?)\s+damage",  # Generic damage
    ],
    
    MechanicalCategory.HEALING: [
        r"(?:heals?|regains?)\s+(\d+d\d+(?:\s*[+\-]\s*\d+)?)\s+hit\s+points",
        r"(?:heals?|regains?)\s+(\d+)\s+hit\s+points",
        r"(\d+d\d+(?:\s*[+\-]\s*\d+)?)\s+healing",
        r"restore\s+(\d+d\d+(?:\s*[+\-]\s*\d+)?)\s+hit\s+points",
    ],
    
    MechanicalCategory.ATTACK: [
        r"attack\s+roll",
        r"weapon\s+attack",
        r"spell\s+attack",
        r"melee\s+attack",
        r"ranged\s+attack",
        r"\+(\d+)\s+to\s+hit",
    ],
    
    MechanicalCategory.DEFENSE: [
        r"armor\s+class",
        r"AC\s+(\d+)",
        r"(\d+)\s+AC",
        r"damage\s+resistance",
        r"damage\s+immunity",
        r"temporary\s+hit\s+points",
    ],
    
    MechanicalCategory.CONDITION: [
        r"(?:becomes?|is|are)\s+(blinded|charmed|deafened|frightened|grappled|incapacitated|invisible|paralyzed|petrified|poisoned|prone|restrained|stunned|unconscious)",
        r"(?:inflicts?|causes?|applies?)\s+the\s+(blinded|charmed|deafened|frightened|grappled|incapacitated|invisible|paralyzed|petrified|poisoned|prone|restrained|stunned|unconscious)\s+condition",
        r"(blinded|charmed|deafened|frightened|grappled|incapacitated|invisible|paralyzed|petrified|poisoned|prone|restrained|stunned|unconscious)\s+for",
    ],
    
    MechanicalCategory.BUFF: [
        r"advantage\s+on",
        r"bonus\s+to",
        r"increases?\s+by\s+(\d+)",
        r"gains?\s+a\s+\+(\d+)\s+bonus",
        r"doubled\s+proficiency\s+bonus",
    ],
    
    MechanicalCategory.DEBUFF: [
        r"disadvantage\s+on",
        r"penalty\s+to",
        r"reduces?\s+by\s+(\d+)",
        r"suffers?\s+a\s+\-(\d+)\s+penalty",
        r"speed\s+is\s+reduced",
    ],
    
    MechanicalCategory.ABILITY_CHECK: [
        r"(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+(?:\([^)]+\))?\s+check",
        r"ability\s+check\s+using\s+(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)",
        r"make\s+an?\s+(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+check",
    ],
    
    MechanicalCategory.SAVING_THROW: [
        r"(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+saving\s+throw",
        r"DC\s+(\d+)\s+(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+saving\s+throw",
        r"make\s+a\s+(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)\s+saving\s+throw",
        r"save\s+DC\s+(\d+)",
    ],
    
    MechanicalCategory.SKILL_CHECK: [
        r"(Acrobatics|Animal Handling|Arcana|Athletics|Deception|History|Insight|Intimidation|Investigation|Medicine|Nature|Perception|Performance|Persuasion|Religion|Sleight of Hand|Stealth|Survival)\s+check",
        r"proficiency\s+in\s+(Acrobatics|Animal Handling|Arcana|Athletics|Deception|History|Insight|Intimidation|Investigation|Medicine|Nature|Perception|Performance|Persuasion|Religion|Sleight of Hand|Stealth|Survival)",
    ],
    
    MechanicalCategory.RESOURCE: [
        r"expend\s+(\d+)\s+(\w+)",
        r"costs?\s+(\d+)\s+(\w+)",
        r"uses?\s+(\d+)\s+(\w+)",
        r"spend\s+(\d+)\s+(\w+)",
        r"(\d+)\s+charges?",
    ],
    
    MechanicalCategory.USAGE_LIMIT: [
        r"once\s+per\s+(turn|round|short\s+rest|long\s+rest|day)",
        r"(\d+)\s+times?\s+per\s+(short\s+rest|long\s+rest|day)",
        r"can\s+be\s+used\s+(\d+)\s+times?",
        r"regains?\s+all\s+expended\s+uses",
    ],
    
    MechanicalCategory.RECHARGE: [
        r"recharge\s+(\d+)\-(\d+)",
        r"recharges?\s+on\s+a\s+(\d+)\s+or\s+higher",
        r"roll\s+a\s+d(\d+)",
    ],
    
    MechanicalCategory.DURATION: [
        r"for\s+(\d+)\s+(minutes?|hours?|days?)",
        r"lasts?\s+(\d+)\s+(minutes?|hours?|days?)",
        r"until\s+the\s+(start|end)\s+of\s+your\s+next\s+turn",
        r"instantaneous",
        r"permanent",
        r"concentration,?\s+up\s+to\s+(\d+)\s+(minutes?|hours?|days?)",
    ],
    
    MechanicalCategory.RANGE: [
        r"range\s+(\d+)\s+feet",
        r"within\s+(\d+)\s+feet",
        r"up\s+to\s+(\d+)\s+feet",
        r"touch",
        r"self",
        r"(\d+)\s+miles?",
    ],
    
    MechanicalCategory.AREA: [
        r"(\d+)\-foot\s+(radius|cube|cone|line|sphere)",
        r"(\d+)\s+feet\s+(radius|wide)",
        r"(\d+)\s+by\s+(\d+)\s+foot\s+(area|square)",
    ],
    
    MechanicalCategory.SCALING: [
        r"increases?\s+by\s+(\d+d\d+)\s+for\s+each\s+slot\s+level\s+above",
        r"when\s+you\s+reach\s+(\d+)(?:st|nd|rd|th)\s+level",
        r"at\s+(\d+)(?:st|nd|rd|th)\s+level\s+and\s+higher",
        r"per\s+level\s+above\s+(\d+)(?:st|nd|rd|th)",
    ],
    
    MechanicalCategory.LEVEL_REQUIREMENT: [
        r"(\d+)(?:st|nd|rd|th)\s+level",
        r"level\s+(\d+)",
        r"requires?\s+(\d+)(?:st|nd|rd|th)\s+level",
        r"minimum\s+level\s+(\d+)",
    ],
    
    MechanicalCategory.REACTION: [
        r"as\s+a\s+reaction",
        r"use\s+your\s+reaction",
        r"when\s+.+\s+you\s+can\s+use\s+your\s+reaction",
    ],
    
    MechanicalCategory.BONUS_ACTION: [
        r"as\s+a\s+bonus\s+action",
        r"bonus\s+action\s+to",
        r"use\s+a\s+bonus\s+action",
    ],
    
    MechanicalCategory.LEGENDARY_ACTION: [
        r"legendary\s+action",
        r"can\s+take\s+(\d+)\s+legendary\s+actions",
        r"costs?\s+(\d+)\s+actions?",
    ],
    
    MechanicalCategory.RITUAL: [
        r"ritual",
        r"cast\s+as\s+a\s+ritual",
        r"ritual\s+casting",
    ],
    
    MechanicalCategory.CONCENTRATION: [
        r"concentration",
        r"requires?\s+concentration",
        r"while\s+concentrating",
        r"lose\s+concentration",
    ],
}


# Common mechanical keywords by category
MECHANICAL_KEYWORDS: Dict[MechanicalCategory, List[str]] = {
    
    MechanicalCategory.DAMAGE: [
        "damage", "deals", "takes", "inflicts", "suffers", "piercing", "slashing", 
        "bludgeoning", "fire", "cold", "lightning", "thunder", "acid", "poison", 
        "psychic", "radiant", "necrotic", "force"
    ],
    
    MechanicalCategory.HEALING: [
        "healing", "heals", "restore", "regain", "hit points", "temporary hit points"
    ],
    
    MechanicalCategory.ATTACK: [
        "attack", "hit", "strike", "weapon", "spell", "melee", "ranged", "target"
    ],
    
    MechanicalCategory.DEFENSE: [
        "armor class", "AC", "resistance", "immunity", "vulnerability", "shield", "cover"
    ],
    
    MechanicalCategory.CONDITION: [
        "blinded", "charmed", "deafened", "frightened", "grappled", "incapacitated", 
        "invisible", "paralyzed", "petrified", "poisoned", "prone", "restrained", 
        "stunned", "unconscious"
    ],
    
    MechanicalCategory.BUFF: [
        "advantage", "bonus", "benefit", "increase", "enhance", "improve", "double"
    ],
    
    MechanicalCategory.DEBUFF: [
        "disadvantage", "penalty", "reduce", "decrease", "impair", "hinder", "half"
    ],
    
    MechanicalCategory.ABILITY_CHECK: [
        "Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma", 
        "ability check", "check"
    ],
    
    MechanicalCategory.SAVING_THROW: [
        "saving throw", "save", "DC"
    ],
    
    MechanicalCategory.SKILL_CHECK: [
        "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception", 
        "History", "Insight", "Intimidation", "Investigation", "Medicine", 
        "Nature", "Perception", "Performance", "Persuasion", "Religion", 
        "Sleight of Hand", "Stealth", "Survival", "proficiency"
    ],
    
    MechanicalCategory.RESOURCE: [
        "expend", "cost", "use", "spend", "charge", "point", "slot"
    ],
    
    MechanicalCategory.USAGE_LIMIT: [
        "once per", "times per", "per day", "per rest", "regain", "recharge"
    ],
    
    MechanicalCategory.DURATION: [
        "minute", "hour", "day", "turn", "round", "until", "instantaneous", 
        "permanent", "concentration"
    ],
    
    MechanicalCategory.RANGE: [
        "range", "feet", "touch", "self", "within", "mile"
    ],
    
    MechanicalCategory.AREA: [
        "radius", "cube", "cone", "line", "sphere", "area", "square"
    ],
    
    MechanicalCategory.SCALING: [
        "level", "increases", "slot level", "higher level"
    ],
}


# === CORE PARSING FUNCTIONS ===

def extract_mechanical_elements(text: str) -> List[MechanicalElement]:
    """
    Extract all mechanical elements from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of found mechanical elements
    """
    elements = []
    
    for category in MechanicalCategory:
        patterns = get_category_patterns(category)
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                element = MechanicalElement(
                    category=category,
                    element_type=_determine_element_type(category, match),
                    value=match.group(0),
                    modifiers=_extract_modifiers(match),
                    context=_get_context(text, match.start(), match.end())
                )
                elements.append(element)
    
    return elements


def parse_damage_expression(damage_text: str) -> Dict[str, Any]:
    """
    Parse damage expression into components.
    
    Args:
        damage_text: Damage text like "2d6+3 fire damage"
        
    Returns:
        Dictionary with damage components
    """
    damage_patterns = get_category_patterns(MechanicalCategory.DAMAGE)
    
    for pattern in damage_patterns:
        match = re.search(pattern, damage_text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) >= 2:
                dice_expr = groups[0]
                damage_type = groups[1] if len(groups) > 1 else "untyped"
                
                # Parse dice expression
                dice_parts = _parse_dice_expression(dice_expr)
                
                return {
                    "dice_expression": dice_expr,
                    "damage_type": damage_type.lower(),
                    "average_damage": dice_parts["average"],
                    "num_dice": dice_parts["num_dice"],
                    "die_size": dice_parts["die_size"],
                    "bonus": dice_parts["bonus"]
                }
    
    return {}


def analyze_mechanical_complexity(text: str) -> Dict[str, Any]:
    """
    Analyze the mechanical complexity of content text.
    
    Args:
        text: Content description text
        
    Returns:
        Complexity analysis results
    """
    elements = extract_mechanical_elements(text)
    
    # Count elements by category
    category_counts = {}
    for element in elements:
        category = element.category
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Calculate complexity metrics
    total_elements = len(elements)
    unique_categories = len(category_counts)
    
    # Complexity scoring
    complexity_score = min(1.0, total_elements / 20)  # Up to 20 elements for max complexity
    diversity_score = min(1.0, unique_categories / len(MechanicalCategory))
    
    return {
        "total_mechanical_elements": total_elements,
        "unique_categories": unique_categories,
        "category_distribution": category_counts,
        "complexity_score": complexity_score,
        "diversity_score": diversity_score,
        "overall_complexity": (complexity_score + diversity_score) / 2,
        "elements": elements
    }


def extract_spell_components(text: str) -> Dict[str, Any]:
    """
    Extract spell components (V, S, M) from spell text.
    
    Args:
        text: Spell description text
        
    Returns:
        Dictionary with component information
    """
    components = {
        "verbal": False,
        "somatic": False,
        "material": False,
        "material_components": [],
        "costly_components": [],
        "component_cost": 0
    }
    
    # Look for component indicators
    if re.search(r"\bV\b", text, re.IGNORECASE):
        components["verbal"] = True
    
    if re.search(r"\bS\b", text, re.IGNORECASE):
        components["somatic"] = True
    
    if re.search(r"\bM\b", text, re.IGNORECASE):
        components["material"] = True
        
        # Extract material component details
        material_match = re.search(r"M\s*\(([^)]+)\)", text, re.IGNORECASE)
        if material_match:
            material_desc = material_match.group(1)
            components["material_components"].append(material_desc)
            
            # Check for costly components
            cost_match = re.search(r"worth\s+(\d+)\s*gp", material_desc, re.IGNORECASE)
            if cost_match:
                components["component_cost"] = int(cost_match.group(1))
                components["costly_components"].append(material_desc)
    
    return components


def extract_scaling_information(text: str) -> Dict[str, Any]:
    """
    Extract level scaling information from content text.
    
    Args:
        text: Content description text
        
    Returns:
        Dictionary with scaling information
    """
    scaling_info = {
        "has_scaling": False,
        "scaling_type": "none",
        "scaling_levels": [],
        "scaling_effects": []
    }
    
    # Look for common scaling patterns
    level_patterns = [
        r"at\s+(\d+)(?:st|nd|rd|th)?\s+level",
        r"when\s+you\s+reach\s+(\d+)(?:st|nd|rd|th)?\s+level",
        r"starting\s+at\s+(\d+)(?:st|nd|rd|th)?\s+level",
    ]
    
    for pattern in level_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            level = int(match.group(1))
            scaling_info["scaling_levels"].append(level)
            scaling_info["has_scaling"] = True
    
    # Look for spell slot scaling
    if re.search(r"higher\s+level", text, re.IGNORECASE):
        scaling_info["has_scaling"] = True
        scaling_info["scaling_type"] = "spell_slot"
    
    # Look for proficiency bonus scaling
    if re.search(r"proficiency\s+bonus", text, re.IGNORECASE):
        scaling_info["has_scaling"] = True
        scaling_info["scaling_type"] = "proficiency"
    
    # Look for ability modifier scaling
    ability_patterns = [
        r"Strength\s+modifier",
        r"Dexterity\s+modifier", 
        r"Constitution\s+modifier",
        r"Intelligence\s+modifier",
        r"Wisdom\s+modifier",
        r"Charisma\s+modifier"
    ]
    
    for pattern in ability_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            scaling_info["has_scaling"] = True
            if scaling_info["scaling_type"] == "none":
                scaling_info["scaling_type"] = "ability_modifier"
    
    return scaling_info


def validate_mechanical_consistency(elements: List[MechanicalElement]) -> List[str]:
    """
    Validate mechanical elements for consistency and rule compliance.
    
    Args:
        elements: List of extracted mechanical elements
        
    Returns:
        List of validation issues found
    """
    issues = []
    
    # Group elements by category for analysis
    categorized = {}
    for element in elements:
        category = element.category
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(element)
    
    # Check for damage type consistency
    damage_elements = categorized.get(MechanicalCategory.DAMAGE, [])
    damage_types = set()
    for damage_elem in damage_elements:
        if damage_elem.modifiers:
            damage_types.add(damage_elem.modifiers[0])
    
    if len(damage_types) > 3:
        issues.append("Too many different damage types (>3) may indicate inconsistent theming")
    
    # Check for saving throw DC consistency
    save_elements = categorized.get(MechanicalCategory.SAVING_THROW, [])
    dcs = []
    for save_elem in save_elements:
        for modifier in save_elem.modifiers:
            if modifier.startswith("DC"):
                try:
                    dc = int(modifier.split()[1])
                    dcs.append(dc)
                except (IndexError, ValueError):
                    pass
    
    if dcs and (max(dcs) - min(dcs)) > 5:
        issues.append("Large variation in saving throw DCs may indicate balance issues")
    
    # Check for resource cost appropriateness
    resource_elements = categorized.get(MechanicalCategory.RESOURCE, [])
    high_cost_resources = [
        elem for elem in resource_elements
        if any("long rest" in mod for mod in elem.modifiers)
    ]
    
    if len(high_cost_resources) > 2:
        issues.append("Multiple long rest resources may be too restrictive")
    
    # Check for condition stacking
    condition_elements = categorized.get(MechanicalCategory.CONDITION, [])
    conditions = [elem.value for elem in condition_elements]
    if len(set(conditions)) != len(conditions):
        issues.append("Duplicate conditions may indicate redundant effects")
    
    return issues


# === UTILITY FUNCTIONS ===

def get_category_patterns(category: MechanicalCategory) -> List[str]:
    """
    Get regex patterns for a specific mechanical category.
    
    Args:
        category: The mechanical category to get patterns for
        
    Returns:
        List of regex patterns for the category
    """
    return MECHANICAL_PATTERNS.get(category, [])


def get_category_keywords(category: MechanicalCategory) -> List[str]:
    """
    Get keywords for a specific mechanical category.
    
    Args:
        category: The mechanical category to get keywords for
        
    Returns:
        List of keywords for the category
    """
    return MECHANICAL_KEYWORDS.get(category, [])


def get_all_mechanical_keywords() -> List[str]:
    """
    Get all mechanical keywords across all categories.
    
    Returns:
        Combined list of all mechanical keywords
    """
    all_keywords = []
    for keywords in MECHANICAL_KEYWORDS.values():
        all_keywords.extend(keywords)
    return list(set(all_keywords))  # Remove duplicates


def categorize_keyword(keyword: str) -> List[MechanicalCategory]:
    """
    Determine which categories a keyword belongs to.
    
    Args:
        keyword: The keyword to categorize
        
    Returns:
        List of categories the keyword belongs to
    """
    keyword_lower = keyword.lower()
    categories = []
    
    for category, keywords in MECHANICAL_KEYWORDS.items():
        if any(keyword_lower in kw.lower() for kw in keywords):
            categories.append(category)
    
    return categories


def find_mechanical_keywords_in_text(text: str) -> Dict[MechanicalCategory, List[str]]:
    """
    Find mechanical keywords in text, organized by category.
    
    Args:
        text: Text to search
        
    Returns:
        Dictionary mapping categories to found keywords
    """
    text_lower = text.lower()
    found_keywords = {}
    
    for category in MechanicalCategory:
        keywords = get_category_keywords(category)
        found_in_category = []
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_in_category.append(keyword)
        
        if found_in_category:
            found_keywords[category] = found_in_category
    
    return found_keywords


# === HELPER FUNCTIONS ===

def _determine_element_type(category: MechanicalCategory, match: re.Match) -> str:
    """Determine the specific type of mechanical element."""
    matched_text = match.group(0).lower()
    
    type_mappings = {
        MechanicalCategory.DAMAGE: {
            "fire": "fire_damage",
            "cold": "cold_damage",
            "lightning": "lightning_damage",
            "thunder": "thunder_damage",
            "acid": "acid_damage",
            "poison": "poison_damage",
            "psychic": "psychic_damage",
            "radiant": "radiant_damage",
            "necrotic": "necrotic_damage",
            "force": "force_damage",
            "piercing": "piercing_damage",
            "slashing": "slashing_damage",
            "bludgeoning": "bludgeoning_damage",
        },
        MechanicalCategory.CONDITION: {
            "blinded": "blind_condition",
            "charmed": "charm_condition",
            "deafened": "deaf_condition",
            "frightened": "fear_condition",
            "grappled": "grapple_condition",
            "incapacitated": "incapacitate_condition",
            "invisible": "invisibility_condition",
            "paralyzed": "paralysis_condition",
            "petrified": "petrify_condition",
            "poisoned": "poison_condition",
            "prone": "prone_condition",
            "restrained": "restrain_condition",
            "stunned": "stun_condition",
            "unconscious": "unconscious_condition",
        }
    }
    
    category_types = type_mappings.get(category, {})
    for keyword, element_type in category_types.items():
        if keyword in matched_text:
            return element_type
    
    return category.value  # Default to category name


def _extract_modifiers(match: re.Match) -> List[str]:
    """Extract modifiers from regex match."""
    modifiers = []
    matched_text = match.group(0)
    
    # Look for common modifiers
    if "advantage" in matched_text.lower():
        modifiers.append("advantage")
    if "disadvantage" in matched_text.lower():
        modifiers.append("disadvantage")
    if re.search(r"\+\d+", matched_text):
        modifiers.append("bonus")
    if re.search(r"\-\d+", matched_text):
        modifiers.append("penalty")
    
    # Extract specific values from groups
    groups = match.groups()
    if groups:
        for group in groups:
            if group and group not in matched_text:  # Avoid duplicating the full match
                modifiers.append(group)
    
    return modifiers


def _get_context(text: str, start: int, end: int, context_length: int = 50) -> str:
    """Get surrounding context for a match."""
    context_start = max(0, start - context_length)
    context_end = min(len(text), end + context_length)
    return text[context_start:context_end].strip()


def _parse_dice_expression(dice_expr: str) -> Dict[str, Any]:
    """Parse dice expression like '2d6+3' into components."""
    try:
        # Handle bonus
        bonus = 0
        if "+" in dice_expr:
            dice_part, bonus_str = dice_expr.split("+", 1)
            bonus = int(bonus_str.strip())
        elif "-" in dice_expr and dice_expr.count("-") == 1:
            dice_part, bonus_str = dice_expr.split("-", 1)
            bonus = -int(bonus_str.strip())
        else:
            dice_part = dice_expr
        
        # Parse dice
        num_dice, die_size = map(int, dice_part.strip().split("d"))
        average_per_die = (die_size + 1) / 2
        average_damage = (num_dice * average_per_die) + bonus
        
        return {
            "num_dice": num_dice,
            "die_size": die_size,
            "bonus": bonus,
            "average": average_damage
        }
    
    except (ValueError, AttributeError):
        return {
            "num_dice": 0,
            "die_size": 0,
            "bonus": 0,
            "average": 0.0
        }