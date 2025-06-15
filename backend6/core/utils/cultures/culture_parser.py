"""
Culture Response Parser - Pure Functions for LLM Response Processing.

Transforms raw LLM responses into structured culture data without side effects.
Follows Clean Architecture principles by maintaining infrastructure independence
and focusing on pure functional text processing and data transformation.

This module provides:
- LLM response parsing into structured culture data
- Name list extraction from various text formats
- Data validation and normalization
- Pure functional approach with no external dependencies
- Educational focus on cultural data integrity
"""

import re
import json
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

# Import core types (inward dependencies only)
from ...enums.culture_types import (
    CultureNamingStructure,
    CultureGenderSystem,
    CultureValidationCategory,
    CultureValidationSeverity
)
from ...exceptions.culture import (
    CultureParsingError,
    CultureValidationError,
    CultureStructureError
)
from ..validation.culture_validator import ValidationResult


class ResponseFormat(Enum):
    """Supported LLM response formats for parsing."""
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"
    STRUCTURED_TEXT = "structured_text"
    MIXED = "mixed"


class NameCategory(Enum):
    """Categories of names that can be extracted."""
    MALE_NAMES = "male_names"
    FEMALE_NAMES = "female_names"
    NEUTRAL_NAMES = "neutral_names"
    UNISEX_NAMES = "unisex_names"
    FAMILY_NAMES = "family_names"
    SURNAMES = "surnames"
    CLAN_NAMES = "clan_names"
    TITLES = "titles"
    EPITHETS = "epithets"
    NICKNAMES = "nicknames"
    HONORIFICS = "honorifics"


@dataclass(frozen=True)
class ParsedCultureData:
    """
    Immutable structure for parsed culture data.
    
    Represents the result of parsing LLM responses into structured
    culture information with validation metadata.
    """
    raw_response: str
    detected_format: ResponseFormat
    
    # Core culture information
    culture_name: Optional[str] = None
    culture_description: Optional[str] = None
    
    # Name categories
    male_names: List[str] = field(default_factory=list)
    female_names: List[str] = field(default_factory=list)
    neutral_names: List[str] = field(default_factory=list)
    family_names: List[str] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)
    epithets: List[str] = field(default_factory=list)
    
    # Extended cultural data
    cultural_traits: Dict[str, Any] = field(default_factory=dict)
    linguistic_patterns: Dict[str, str] = field(default_factory=dict)
    historical_context: Dict[str, str] = field(default_factory=dict)
    
    # Parsing metadata
    confidence_score: float = 0.0
    parsing_warnings: List[str] = field(default_factory=list)
    extraction_stats: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate parsed data structure on creation."""
        if not self.raw_response:
            raise CultureParsingError("Raw response cannot be empty")
        
        if self.confidence_score < 0.0 or self.confidence_score > 1.0:
            raise CultureParsingError("Confidence score must be between 0.0 and 1.0")


class CultureParser:
    """
    Pure functional culture response parser.
    
    Provides static methods for parsing LLM responses into structured
    culture data without side effects or external dependencies.
    
    All methods are pure functions that produce consistent results
    for the same inputs while maintaining Clean Architecture principles.
    """
    
    @staticmethod
    def parse_culture_response(llm_response: str) -> ParsedCultureData:
        """
        Parse LLM response into structured culture data.
        
        Pure function that transforms raw LLM response text into
        structured culture information without side effects.
        
        Args:
            llm_response: Raw response text from LLM provider
            
        Returns:
            ParsedCultureData with structured culture information
            
        Raises:
            CultureParsingError: If parsing fails
            CultureStructureError: If parsed structure is invalid
            
        Example:
            >>> response = '''
            ... **Norse Culture**
            ... Male Names: Erik, Olaf, Magnus, Thor
            ... Female Names: Astrid, Ingrid, Freydis
            ... '''
            >>> parsed = CultureParser.parse_culture_response(response)
            >>> print(f"Found {len(parsed.male_names)} male names")
        """
        if not llm_response or not llm_response.strip():
            raise CultureParsingError("LLM response cannot be empty")
        
        try:
            # Detect response format
            detected_format = CultureParser._detect_response_format(llm_response)
            
            # Parse based on detected format
            if detected_format == ResponseFormat.JSON:
                parsed_data = CultureParser._parse_json_response(llm_response)
            elif detected_format == ResponseFormat.YAML:
                parsed_data = CultureParser._parse_yaml_response(llm_response)
            elif detected_format == ResponseFormat.MARKDOWN:
                parsed_data = CultureParser._parse_markdown_response(llm_response)
            elif detected_format == ResponseFormat.STRUCTURED_TEXT:
                parsed_data = CultureParser._parse_structured_text(llm_response)
            else:
                parsed_data = CultureParser._parse_plain_text(llm_response)
            
            # Calculate confidence score
            confidence = CultureParser._calculate_parsing_confidence(parsed_data, llm_response)
            
            # Generate extraction statistics
            stats = CultureParser._generate_extraction_stats(parsed_data)
            
            # Create final parsed data structure
            return ParsedCultureData(
                raw_response=llm_response,
                detected_format=detected_format,
                culture_name=parsed_data.get('culture_name'),
                culture_description=parsed_data.get('culture_description'),
                male_names=parsed_data.get('male_names', []),
                female_names=parsed_data.get('female_names', []),
                neutral_names=parsed_data.get('neutral_names', []),
                family_names=parsed_data.get('family_names', []),
                titles=parsed_data.get('titles', []),
                epithets=parsed_data.get('epithets', []),
                cultural_traits=parsed_data.get('cultural_traits', {}),
                linguistic_patterns=parsed_data.get('linguistic_patterns', {}),
                historical_context=parsed_data.get('historical_context', {}),
                confidence_score=confidence,
                parsing_warnings=parsed_data.get('warnings', []),
                extraction_stats=stats
            )
            
        except Exception as e:
            if isinstance(e, (CultureParsingError, CultureStructureError)):
                raise
            raise CultureParsingError(f"Failed to parse culture response: {str(e)}") from e
    
    @staticmethod
    def extract_name_lists(response_text: str) -> Dict[str, List[str]]:
        """
        Extract name lists from response text using pattern matching.
        
        Pure function that identifies and extracts categorized name lists
        from various text formats without side effects.
        
        Args:
            response_text: Text containing name lists
            
        Returns:
            Dictionary mapping name categories to extracted names
            
        Example:
            >>> text = "Male names: Erik, Olaf, Magnus\\nFemale names: Astrid, Ingrid"
            >>> names = CultureParser.extract_name_lists(text)
            >>> print(names['male_names'])  # ['Erik', 'Olaf', 'Magnus']
        """
        if not response_text:
            return {}
        
        try:
            name_lists = {}
            
            # Define patterns for different name categories
            category_patterns = {
                'male_names': [
                    r'(?:male\s+names?|men\'?s?\s+names?|masculine\s+names?)[:：]\s*([^\n\r]+)',
                    r'(?:boys?\s+names?|male)[:：]\s*([^\n\r]+)',
                    r'(?:♂|男|M)[:：]\s*([^\n\r]+)'
                ],
                'female_names': [
                    r'(?:female\s+names?|women\'?s?\s+names?|feminine\s+names?)[:：]\s*([^\n\r]+)',
                    r'(?:girls?\s+names?|female)[:：]\s*([^\n\r]+)',
                    r'(?:♀|女|F)[:：]\s*([^\n\r]+)'
                ],
                'neutral_names': [
                    r'(?:neutral\s+names?|unisex\s+names?|gender.neutral)[:：]\s*([^\n\r]+)',
                    r'(?:non.binary|nb|enby).*names?[:：]\s*([^\n\r]+)'
                ],
                'family_names': [
                    r'(?:family\s+names?|surnames?|last\s+names?)[:：]\s*([^\n\r]+)',
                    r'(?:clan\s+names?|house\s+names?)[:：]\s*([^\n\r]+)'
                ],
                'titles': [
                    r'(?:titles?|ranks?|positions?)[:：]\s*([^\n\r]+)',
                    r'(?:honorifics?|appellations?)[:：]\s*([^\n\r]+)'
                ],
                'epithets': [
                    r'(?:epithets?|nicknames?|bynames?)[:：]\s*([^\n\r]+)',
                    r'(?:descriptive\s+names?|kennings?)[:：]\s*([^\n\r]+)'
                ]
            }
            
            # Extract names for each category
            for category, patterns in category_patterns.items():
                names = []
                
                for pattern in patterns:
                    matches = re.findall(pattern, response_text, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        extracted_names = CultureParser._parse_name_string(match)
                        names.extend(extracted_names)
                
                if names:
                    # Deduplicate and clean names
                    name_lists[category] = CultureParser._clean_and_deduplicate_names(names)
            
            # Try fallback extraction if no structured lists found
            if not name_lists:
                fallback_names = CultureParser._extract_names_fallback(response_text)
                if fallback_names:
                    name_lists.update(fallback_names)
            
            return name_lists
            
        except Exception as e:
            # Return empty dict on parsing error rather than failing
            return {'parsing_error': [str(e)]}
    
    @staticmethod
    def validate_parsed_data(parsed_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate parsed culture data for completeness and consistency.
        
        Pure function that analyzes parsed data structure and content
        for validation issues without side effects.
        
        Args:
            parsed_data: Dictionary containing parsed culture data
            
        Returns:
            ValidationResult with detailed validation information
            
        Example:
            >>> parsed = {'male_names': ['Erik', 'Olaf'], 'female_names': []}
            >>> result = CultureParser.validate_parsed_data(parsed)
            >>> print(f"Valid: {result.is_valid}, Issues: {len(result.issues)}")
        """
        issues = []
        warnings = []
        metadata = {'validation_categories': []}
        
        try:
            # Validate structure
            structure_validation = CultureParser._validate_data_structure(parsed_data)
            issues.extend(structure_validation['issues'])
            warnings.extend(structure_validation['warnings'])
            metadata['validation_categories'].append('structure')
            
            # Validate name lists
            names_validation = CultureParser._validate_name_lists(parsed_data)
            issues.extend(names_validation['issues'])
            warnings.extend(names_validation['warnings'])
            metadata['validation_categories'].append('names')
            
            # Validate cultural content
            content_validation = CultureParser._validate_cultural_content(parsed_data)
            issues.extend(content_validation['issues'])
            warnings.extend(content_validation['warnings'])
            metadata['validation_categories'].append('content')
            
            # Validate consistency
            consistency_validation = CultureParser._validate_data_consistency(parsed_data)
            issues.extend(consistency_validation['issues'])
            warnings.extend(consistency_validation['warnings'])
            metadata['validation_categories'].append('consistency')
            
            # Determine overall validation status
            is_valid = len(issues) == 0
            severity = CultureValidationSeverity.CRITICAL if issues else (
                CultureValidationSeverity.MEDIUM if warnings else CultureValidationSeverity.INFO
            )
            
            # Add metadata
            metadata.update({
                'total_names': CultureParser._count_total_names(parsed_data),
                'categories_found': CultureParser._count_categories_with_data(parsed_data),
                'completeness_score': CultureParser._calculate_completeness_score(parsed_data)
            })
            
            return ValidationResult(
                is_valid=is_valid,
                severity=severity,
                issues=issues,
                warnings=warnings,
                metadata=metadata
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                severity=CultureValidationSeverity.CRITICAL,
                issues=[f"Validation error: {str(e)}"],
                warnings=[],
                metadata={'error': str(e)}
            )
    
    @staticmethod
    def normalize_culture_data(parsed_data: ParsedCultureData) -> Dict[str, Any]:
        """
        Normalize parsed culture data into standard format.
        
        Pure function that transforms parsed data into a consistent
        format suitable for culture generation systems.
        
        Args:
            parsed_data: ParsedCultureData to normalize
            
        Returns:
            Dictionary with normalized culture data
            
        Example:
            >>> parsed = CultureParser.parse_culture_response(response)
            >>> normalized = CultureParser.normalize_culture_data(parsed)
            >>> print(normalized.keys())
        """
        return {
            'name': parsed_data.culture_name or 'Unknown Culture',
            'description': parsed_data.culture_description or 'Generated culture',
            'male_names': CultureParser._normalize_name_list(parsed_data.male_names),
            'female_names': CultureParser._normalize_name_list(parsed_data.female_names),
            'neutral_names': CultureParser._normalize_name_list(parsed_data.neutral_names),
            'family_names': CultureParser._normalize_name_list(parsed_data.family_names),
            'titles': CultureParser._normalize_name_list(parsed_data.titles),
            'epithets': CultureParser._normalize_name_list(parsed_data.epithets),
            'cultural_traits': parsed_data.cultural_traits or {},
            'linguistic_patterns': parsed_data.linguistic_patterns or {},
            'historical_context': parsed_data.historical_context or {},
            'metadata': {
                'source_format': parsed_data.detected_format.value,
                'confidence_score': parsed_data.confidence_score,
                'parsing_warnings': parsed_data.parsing_warnings,
                'extraction_stats': parsed_data.extraction_stats
            }
        }
    
    @staticmethod
    def extract_cultural_context(response_text: str) -> Dict[str, str]:
        """
        Extract cultural context information from response text.
        
        Pure function that identifies cultural traits, historical context,
        and linguistic patterns from LLM responses.
        
        Args:
            response_text: Text to analyze for cultural context
            
        Returns:
            Dictionary with extracted cultural context information
            
        Example:
            >>> context = CultureParser.extract_cultural_context(response_text)
            >>> print(context.get('historical_period', 'Unknown'))
        """
        if not response_text:
            return {}
        
        context = {}
        
        try:
            # Extract historical periods
            period_patterns = [
                r'(?:period|era|age)[:：]\s*([^\n\r]+)',
                r'(?:time|epoch|century)[:：]\s*([^\n\r]+)',
                r'(?:ancient|medieval|renaissance|modern)\s+([^\n\r,.]+)'
            ]
            
            for pattern in period_patterns:
                matches = re.findall(pattern, response_text, re.IGNORECASE)
                if matches:
                    context['historical_period'] = matches[0].strip()
                    break
            
            # Extract cultural traits
            trait_patterns = [
                r'(?:traits?|characteristics?)[:：]\s*([^\n\r]+)',
                r'(?:known\s+for|famous\s+for)[:：]\s*([^\n\r]+)',
                r'(?:culture|society).*?[:：]\s*([^\n\r]+)'
            ]
            
            for pattern in trait_patterns:
                matches = re.findall(pattern, response_text, re.IGNORECASE)
                if matches:
                    context['cultural_traits'] = matches[0].strip()
                    break
            
            # Extract linguistic information
            linguistic_patterns = [
                r'(?:language|linguistic|dialect)[:：]\s*([^\n\r]+)',
                r'(?:pronunciation|phonetic)[:：]\s*([^\n\r]+)',
                r'(?:naming\s+pattern|name\s+structure)[:：]\s*([^\n\r]+)'
            ]
            
            for pattern in linguistic_patterns:
                matches = re.findall(pattern, response_text, re.IGNORECASE)
                if matches:
                    context['linguistic_info'] = matches[0].strip()
                    break
            
            # Extract geographical context
            geo_patterns = [
                r'(?:region|location|geography)[:：]\s*([^\n\r]+)',
                r'(?:from|of|in)\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'(?:homeland|territory|domain)[:：]\s*([^\n\r]+)'
            ]
            
            for pattern in geo_patterns:
                matches = re.findall(pattern, response_text, re.IGNORECASE)
                if matches:
                    context['geographical_context'] = matches[0].strip()
                    break
            
            return context
            
        except Exception:
            return {}
    
    @staticmethod
    def merge_parsed_responses(
        primary: ParsedCultureData, 
        secondary: ParsedCultureData
    ) -> ParsedCultureData:
        """
        Merge two parsed culture responses intelligently.
        
        Pure function that combines data from multiple LLM responses
        while preserving data quality and avoiding conflicts.
        
        Args:
            primary: Primary parsed response (takes precedence)
            secondary: Secondary parsed response (fills gaps)
            
        Returns:
            New ParsedCultureData with merged information
            
        Example:
            >>> response1 = CultureParser.parse_culture_response(llm_response1)
            >>> response2 = CultureParser.parse_culture_response(llm_response2)
            >>> merged = CultureParser.merge_parsed_responses(response1, response2)
        """
        # Merge name lists (deduplicate)
        merged_male_names = list(set(primary.male_names + secondary.male_names))
        merged_female_names = list(set(primary.female_names + secondary.female_names))
        merged_neutral_names = list(set(primary.neutral_names + secondary.neutral_names))
        merged_family_names = list(set(primary.family_names + secondary.family_names))
        merged_titles = list(set(primary.titles + secondary.titles))
        merged_epithets = list(set(primary.epithets + secondary.epithets))
        
        # Merge cultural data
        merged_traits = {**secondary.cultural_traits, **primary.cultural_traits}
        merged_patterns = {**secondary.linguistic_patterns, **primary.linguistic_patterns}
        merged_context = {**secondary.historical_context, **primary.historical_context}
        
        # Merge warnings
        merged_warnings = list(set(primary.parsing_warnings + secondary.parsing_warnings))
        
        # Calculate merged confidence (weighted average)
        primary_weight = 0.7  # Primary response gets higher weight
        secondary_weight = 0.3
        merged_confidence = (primary.confidence_score * primary_weight + 
                           secondary.confidence_score * secondary_weight)
        
        # Merge extraction stats
        merged_stats = {}
        for key in set(primary.extraction_stats.keys()) | set(secondary.extraction_stats.keys()):
            merged_stats[key] = (primary.extraction_stats.get(key, 0) + 
                               secondary.extraction_stats.get(key, 0))
        
        return ParsedCultureData(
            raw_response=f"{primary.raw_response}\n\n--- MERGED WITH ---\n\n{secondary.raw_response}",
            detected_format=primary.detected_format,  # Use primary format
            culture_name=primary.culture_name or secondary.culture_name,
            culture_description=primary.culture_description or secondary.culture_description,
            male_names=merged_male_names,
            female_names=merged_female_names,
            neutral_names=merged_neutral_names,
            family_names=merged_family_names,
            titles=merged_titles,
            epithets=merged_epithets,
            cultural_traits=merged_traits,
            linguistic_patterns=merged_patterns,
            historical_context=merged_context,
            confidence_score=merged_confidence,
            parsing_warnings=merged_warnings,
            extraction_stats=merged_stats
        )
    
    # ============================================================================
    # PRIVATE HELPER METHODS (Pure Functions)
    # ============================================================================
    
    @staticmethod
    def _detect_response_format(response_text: str) -> ResponseFormat:
        """Detect the format of the LLM response."""
        text_stripped = response_text.strip()
        
        # Check for JSON
        if ((text_stripped.startswith('{') and text_stripped.endswith('}')) or
            (text_stripped.startswith('[') and text_stripped.endswith(']'))):
            try:
                json.loads(text_stripped)
                return ResponseFormat.JSON
            except json.JSONDecodeError:
                pass
        
        # Check for YAML (basic detection)
        if re.search(r'^\w+:\s*$', text_stripped, re.MULTILINE):
            return ResponseFormat.YAML
        
        # Check for Markdown
        if re.search(r'^#{1,6}\s+', text_stripped, re.MULTILINE) or '**' in text_stripped:
            return ResponseFormat.MARKDOWN
        
        # Check for structured text (lists with colons)
        if re.search(r'(?:names?|titles?)[:：]\s*', text_stripped, re.IGNORECASE):
            return ResponseFormat.STRUCTURED_TEXT
        
        return ResponseFormat.PLAIN_TEXT
    
    @staticmethod
    def _parse_json_response(response_text: str) -> Dict[str, Any]:
        """Parse JSON formatted response."""
        try:
            data = json.loads(response_text.strip())
            return CultureParser._normalize_json_keys(data)
        except json.JSONDecodeError as e:
            raise CultureParsingError(f"Invalid JSON format: {str(e)}")
    
    @staticmethod
    def _parse_yaml_response(response_text: str) -> Dict[str, Any]:
        """Parse YAML-like formatted response (basic implementation)."""
        data = {}
        warnings = []
        
        lines = response_text.split('\n')
        current_key = None
        current_list = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for key-value pair
            if ':' in line and not line.startswith('-'):
                if current_key and current_list:
                    data[current_key] = current_list
                    current_list = []
                
                key, value = line.split(':', 1)
                current_key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                if value:
                    if value.startswith('[') and value.endswith(']'):
                        # Parse list in brackets
                        data[current_key] = CultureParser._parse_bracketed_list(value)
                    else:
                        data[current_key] = value
            elif line.startswith('-') and current_key:
                # List item
                item = line[1:].strip()
                if item:
                    current_list.append(item)
            elif current_key and line:
                # Continuation or comma-separated list
                if ',' in line:
                    items = [item.strip() for item in line.split(',')]
                    current_list.extend(items)
                else:
                    current_list.append(line)
        
        # Add final list if exists
        if current_key and current_list:
            data[current_key] = current_list
        
        if warnings:
            data['warnings'] = warnings
        
        return data
    
    @staticmethod
    def _parse_markdown_response(response_text: str) -> Dict[str, Any]:
        """Parse Markdown formatted response."""
        data = {}
        warnings = []
        
        # Extract culture name from headers
        header_match = re.search(r'^#{1,3}\s+(.+)$', response_text, re.MULTILINE)
        if header_match:
            data['culture_name'] = header_match.group(1).strip('*').strip()
        
        # Extract name lists from sections
        name_lists = CultureParser.extract_name_lists(response_text)
        data.update(name_lists)
        
        # Extract cultural context
        context = CultureParser.extract_cultural_context(response_text)
        if context:
            data['cultural_traits'] = context.get('cultural_traits', {})
            data['linguistic_patterns'] = context.get('linguistic_info', {})
            data['historical_context'] = context.get('historical_period', {})
        
        # Look for description in paragraphs
        paragraphs = re.findall(r'^(?!#)([^:\n]+)$', response_text, re.MULTILINE)
        if paragraphs:
            # Use first substantial paragraph as description
            for paragraph in paragraphs:
                if len(paragraph.strip()) > 20:
                    data['culture_description'] = paragraph.strip()
                    break
        
        return data
    
    @staticmethod
    def _parse_structured_text(response_text: str) -> Dict[str, Any]:
        """Parse structured text with labeled sections."""
        data = {}
        
        # Extract name lists
        name_lists = CultureParser.extract_name_lists(response_text)
        data.update(name_lists)
        
        # Extract cultural context
        context = CultureParser.extract_cultural_context(response_text)
        data.update(context)
        
        # Look for culture name at the beginning
        first_line = response_text.split('\n')[0].strip()
        if first_line and not ':' in first_line:
            data['culture_name'] = first_line.strip('*').strip('#').strip()
        
        return data
    
    @staticmethod
    def _parse_plain_text(response_text: str) -> Dict[str, Any]:
        """Parse plain text response using pattern matching."""
        data = {}
        warnings = ['Plain text format - limited extraction capabilities']
        
        # Try to extract any structured information
        name_lists = CultureParser.extract_name_lists(response_text)
        if name_lists:
            data.update(name_lists)
        else:
            # Fallback: extract any capitalized words as potential names
            potential_names = re.findall(r'\b[A-Z][a-z]+\b', response_text)
            if potential_names:
                data['extracted_names'] = list(set(potential_names))
                warnings.append('Names extracted from capitalized words - may need manual categorization')
        
        # Try to extract cultural context
        context = CultureParser.extract_cultural_context(response_text)
        data.update(context)
        
        data['warnings'] = warnings
        return data
    
    @staticmethod
    def _parse_name_string(name_string: str) -> List[str]:
        """Parse a string containing multiple names."""
        if not name_string:
            return []
        
        # Clean the string
        cleaned = name_string.strip()
        
        # Handle different separators
        separators = [',', ';', '|', '\n', '\t']
        names = [cleaned]
        
        for sep in separators:
            if sep in cleaned:
                names = cleaned.split(sep)
                break
        
        # Clean and filter names
        result = []
        for name in names:
            cleaned_name = name.strip().strip('"').strip("'")
            if cleaned_name and len(cleaned_name) > 1:
                # Remove common prefixes/suffixes that aren't part of names
                if not cleaned_name.lower().startswith(('and ', 'or ', 'the ')):
                    result.append(cleaned_name)
        
        return result
    
    @staticmethod
    def _clean_and_deduplicate_names(names: List[str]) -> List[str]:
        """Clean and deduplicate a list of names."""
        cleaned = []
        seen = set()
        
        for name in names:
            # Basic cleaning
            clean_name = name.strip().title()
            
            # Skip invalid names
            if len(clean_name) < 2 or not clean_name.replace(' ', '').replace('-', '').isalpha():
                continue
            
            # Skip duplicates (case-insensitive)
            if clean_name.lower() not in seen:
                cleaned.append(clean_name)
                seen.add(clean_name.lower())
        
        return sorted(cleaned)
    
    @staticmethod
    def _extract_names_fallback(text: str) -> Dict[str, List[str]]:
        """Fallback name extraction from unstructured text."""
        # Extract all potential names (capitalized words)
        potential_names = re.findall(r'\b[A-Z][a-z]+(?:\-[A-Z][a-z]+)?\b', text)
        
        if not potential_names:
            return {}
        
        # Basic categorization based on context clues
        male_indicators = ['he', 'him', 'his', 'king', 'lord', 'sir', 'man', 'boy', 'father', 'son']
        female_indicators = ['she', 'her', 'hers', 'queen', 'lady', 'dame', 'woman', 'girl', 'mother', 'daughter']
        
        categorized = {'male_names': [], 'female_names': [], 'neutral_names': []}
        
        for name in set(potential_names):
            context = CultureParser._get_name_context(name, text, 50)  # 50 character window
            
            if any(indicator in context.lower() for indicator in male_indicators):
                categorized['male_names'].append(name)
            elif any(indicator in context.lower() for indicator in female_indicators):
                categorized['female_names'].append(name)
            else:
                categorized['neutral_names'].append(name)
        
        return {k: v for k, v in categorized.items() if v}
    
    @staticmethod
    def _get_name_context(name: str, text: str, window_size: int) -> str:
        """Get context around a name in text."""
        name_index = text.find(name)
        if name_index == -1:
            return ""
        
        start = max(0, name_index - window_size)
        end = min(len(text), name_index + len(name) + window_size)
        
        return text[start:end]
    
    @staticmethod
    def _calculate_parsing_confidence(parsed_data: Dict[str, Any], original_text: str) -> float:
        """Calculate confidence score for parsing results."""
        score = 0.0
        max_score = 5.0
        
        # Check for structured format indicators
        if any(key in parsed_data for key in ['male_names', 'female_names', 'family_names']):
            score += 2.0  # Found categorized names
        
        # Check for culture name
        if parsed_data.get('culture_name'):
            score += 1.0
        
        # Check for description
        if parsed_data.get('culture_description'):
            score += 1.0
        
        # Check for additional cultural data
        if any(key in parsed_data for key in ['cultural_traits', 'linguistic_patterns', 'historical_context']):
            score += 1.0
        
        # Penalty for warnings
        warnings = parsed_data.get('warnings', [])
        if warnings:
            score -= len(warnings) * 0.2
        
        return max(0.0, min(1.0, score / max_score))
    
    @staticmethod
    def _generate_extraction_stats(parsed_data: Dict[str, Any]) -> Dict[str, int]:
        """Generate statistics about extracted data."""
        stats = {}
        
        name_categories = ['male_names', 'female_names', 'neutral_names', 'family_names', 'titles', 'epithets']
        
        for category in name_categories:
            if category in parsed_data and isinstance(parsed_data[category], list):
                stats[category] = len(parsed_data[category])
        
        stats['total_names'] = sum(stats.values())
        stats['categories_with_data'] = len([k for k, v in stats.items() if v > 0 and k != 'total_names'])
        
        return stats
    
    @staticmethod
    def _validate_data_structure(parsed_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate basic data structure."""
        issues = []
        warnings = []
        
        # Check for required structure
        if not isinstance(parsed_data, dict):
            issues.append("Parsed data must be a dictionary")
            return {'issues': issues, 'warnings': warnings}
        
        # Check name lists are actually lists
        name_categories = ['male_names', 'female_names', 'neutral_names', 'family_names', 'titles', 'epithets']
        
        for category in name_categories:
            if category in parsed_data:
                if not isinstance(parsed_data[category], list):
                    issues.append(f"{category} must be a list")
                elif not all(isinstance(name, str) for name in parsed_data[category]):
                    issues.append(f"All items in {category} must be strings")
        
        return {'issues': issues, 'warnings': warnings}
    
    @staticmethod
    def _validate_name_lists(parsed_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate name lists content."""
        issues = []
        warnings = []
        
        name_categories = ['male_names', 'female_names', 'neutral_names', 'family_names', 'titles', 'epithets']
        total_names = 0
        
        for category in name_categories:
            if category in parsed_data and isinstance(parsed_data[category], list):
                names = parsed_data[category]
                total_names += len(names)
                
                # Check for empty names
                empty_names = [name for name in names if not name or not name.strip()]
                if empty_names:
                    issues.append(f"Empty names found in {category}")
                
                # Check for suspiciously short names
                short_names = [name for name in names if len(name.strip()) < 2]
                if short_names:
                    warnings.append(f"Very short names found in {category}: {short_names}")
                
                # Check for duplicates within category
                if len(names) != len(set(names)):
                    warnings.append(f"Duplicate names found in {category}")
        
        if total_names == 0:
            warnings.append("No names extracted from response")
        elif total_names < 10:
            warnings.append(f"Low name count: only {total_names} names extracted")
        
        return {'issues': issues, 'warnings': warnings}
    
    @staticmethod
    def _validate_cultural_content(parsed_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate cultural content quality."""
        issues = []
        warnings = []
        
        # Check cultural traits
        if 'cultural_traits' in parsed_data:
            traits = parsed_data['cultural_traits']
            if not isinstance(traits, dict):
                issues.append("Cultural traits must be a dictionary")
            elif not traits:
                warnings.append("Cultural traits dictionary is empty")
        
        # Check linguistic patterns
        if 'linguistic_patterns' in parsed_data:
            patterns = parsed_data['linguistic_patterns']
            if not isinstance(patterns, dict):
                issues.append("Linguistic patterns must be a dictionary")
        
        # Check historical context
        if 'historical_context' in parsed_data:
            context = parsed_data['historical_context']
            if not isinstance(context, dict):
                issues.append("Historical context must be a dictionary")
        
        return {'issues': issues, 'warnings': warnings}
    
    @staticmethod
    def _validate_data_consistency(parsed_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate data consistency across categories."""
        issues = []
        warnings = []
        
        # Check for name overlap between categories
        name_categories = ['male_names', 'female_names', 'neutral_names']
        name_sets = {}
        
        for category in name_categories:
            if category in parsed_data and isinstance(parsed_data[category], list):
                name_sets[category] = set(name.lower() for name in parsed_data[category])
        
        # Check for overlaps
        for cat1, names1 in name_sets.items():
            for cat2, names2 in name_sets.items():
                if cat1 != cat2:
                    overlap = names1 & names2
                    if overlap:
                        warnings.append(f"Name overlap between {cat1} and {cat2}: {list(overlap)}")
        
        return {'issues': issues, 'warnings': warnings}
    
    @staticmethod
    def _normalize_json_keys(data: Any) -> Dict[str, Any]:
        """Normalize JSON keys to standard format."""
        if isinstance(data, dict):
            normalized = {}
            for key, value in data.items():
                # Normalize key
                norm_key = key.lower().replace(' ', '_').replace('-', '_')
                
                # Handle common variations
                if norm_key in ['men_names', 'mens_names', 'masculine_names']:
                    norm_key = 'male_names'
                elif norm_key in ['women_names', 'womens_names', 'feminine_names']:
                    norm_key = 'female_names'
                elif norm_key in ['unisex_names', 'gender_neutral_names']:
                    norm_key = 'neutral_names'
                elif norm_key in ['surnames', 'last_names', 'clan_names']:
                    norm_key = 'family_names'
                
                # Recursively normalize nested data
                normalized[norm_key] = CultureParser._normalize_json_keys(value)
            
            return normalized
        elif isinstance(data, list):
            return [CultureParser._normalize_json_keys(item) for item in data]
        else:
            return data
    
    @staticmethod
    def _parse_bracketed_list(text: str) -> List[str]:
        """Parse list in brackets format: [item1, item2, item3]"""
        content = text.strip('[]')
        if not content:
            return []
        
        items = [item.strip().strip('"').strip("'") for item in content.split(',')]
        return [item for item in items if item]
    
    @staticmethod
    def _normalize_name_list(names: List[str]) -> List[str]:
        """Normalize a list of names."""
        if not names:
            return []
        
        return CultureParser._clean_and_deduplicate_names(names)
    
    @staticmethod
    def _count_total_names(parsed_data: Dict[str, Any]) -> int:
        """Count total names across all categories."""
        name_categories = ['male_names', 'female_names', 'neutral_names', 'family_names', 'titles', 'epithets']
        total = 0
        
        for category in name_categories:
            if category in parsed_data and isinstance(parsed_data[category], list):
                total += len(parsed_data[category])
        
        return total
    
    @staticmethod
    def _count_categories_with_data(parsed_data: Dict[str, Any]) -> int:
        """Count categories that have data."""
        name_categories = ['male_names', 'female_names', 'neutral_names', 'family_names', 'titles', 'epithets']
        count = 0
        
        for category in name_categories:
            if category in parsed_data and isinstance(parsed_data[category], list) and parsed_data[category]:
                count += 1
        
        return count
    
    @staticmethod
    def _calculate_completeness_score(parsed_data: Dict[str, Any]) -> float:
        """Calculate completeness score for parsed data."""
        max_score = 6.0  # 6 main categories
        score = 0.0
        
        name_categories = ['male_names', 'female_names', 'neutral_names', 'family_names', 'titles', 'epithets']
        
        for category in name_categories:
            if category in parsed_data and isinstance(parsed_data[category], list) and parsed_data[category]:
                score += 1.0
        
        return score / max_score


# ============================================================================
# UTILITY FUNCTIONS (Pure Functions)
# ============================================================================

def parse_multiple_responses(responses: List[str]) -> List[ParsedCultureData]:
    """
    Parse multiple LLM responses in batch.
    
    Pure function that processes multiple responses efficiently
    while maintaining error isolation.
    
    Args:
        responses: List of LLM response strings
        
    Returns:
        List of ParsedCultureData objects
        
    Example:
        >>> responses = [response1, response2, response3]
        >>> parsed_list = parse_multiple_responses(responses)
        >>> print(f"Parsed {len(parsed_list)} responses")
    """
    results = []
    
    for i, response in enumerate(responses):
        try:
            parsed = CultureParser.parse_culture_response(response)
            results.append(parsed)
        except Exception as e:
            # Create error result rather than failing entire batch
            error_result = ParsedCultureData(
                raw_response=response,
                detected_format=ResponseFormat.PLAIN_TEXT,
                parsing_warnings=[f"Parsing failed: {str(e)}"],
                confidence_score=0.0
            )
            results.append(error_result)
    
    return results


def merge_multiple_parsed_data(parsed_data_list: List[ParsedCultureData]) -> ParsedCultureData:
    """
    Merge multiple parsed culture data objects.
    
    Pure function that combines multiple parsing results
    into a single comprehensive culture dataset.
    
    Args:
        parsed_data_list: List of ParsedCultureData to merge
        
    Returns:
        Single merged ParsedCultureData
        
    Example:
        >>> parsed_list = parse_multiple_responses(responses)
        >>> merged = merge_multiple_parsed_data(parsed_list)
        >>> print(f"Merged culture: {merged.culture_name}")
    """
    if not parsed_data_list:
        raise CultureParsingError("Cannot merge empty list of parsed data")
    
    if len(parsed_data_list) == 1:
        return parsed_data_list[0]
    
    # Start with first as base
    result = parsed_data_list[0]
    
    # Merge with subsequent responses
    for parsed_data in parsed_data_list[1:]:
        result = CultureParser.merge_parsed_responses(result, parsed_data)
    
    return result


def extract_names_from_text(text: str, categories: Optional[List[str]] = None) -> Dict[str, List[str]]:
    """
    Extract names from text with optional category filtering.
    
    Pure function for targeted name extraction.
    
    Args:
        text: Text to extract names from
        categories: Optional list of categories to extract (None = all)
        
    Returns:
        Dictionary of extracted names by category
        
    Example:
        >>> names = extract_names_from_text(text, ['male_names', 'female_names'])
        >>> print(f"Found {len(names)} categories")
    """
    all_names = CultureParser.extract_name_lists(text)
    
    if categories is None:
        return all_names
    
    return {cat: all_names.get(cat, []) for cat in categories if cat in all_names}


def validate_response_format(response: str) -> Tuple[bool, ResponseFormat, List[str]]:
    """
    Validate LLM response format before parsing.
    
    Pure function that checks response format validity.
    
    Args:
        response: LLM response to validate
        
    Returns:
        Tuple of (is_valid, detected_format, issues)
        
    Example:
        >>> valid, format_type, issues = validate_response_format(response)
        >>> print(f"Valid: {valid}, Format: {format_type.value}")
    """
    issues = []
    
    if not response or not response.strip():
        return False, ResponseFormat.PLAIN_TEXT, ["Response is empty"]
    
    detected_format = CultureParser._detect_response_format(response)
    
    # Format-specific validation
    if detected_format == ResponseFormat.JSON:
        try:
            json.loads(response.strip())
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON: {str(e)}")
    
    # Check for minimum content
    if len(response.strip()) < 20:
        issues.append("Response is too short")
    
    # Check for potential name content
    if not re.search(r'\b[A-Z][a-z]+\b', response):
        issues.append("No capitalized words found - may not contain names")
    
    is_valid = len(issues) == 0
    return is_valid, detected_format, issues


# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = "1.0.0"
__description__ = "Culture Response Parser for Clean Architecture"

# Clean Architecture compliance metadata
CLEAN_ARCHITECTURE_COMPLIANCE = {
    "layer": "core/utils/cultures",
    "dependencies": [
        "re", "json", "typing", "dataclasses", "enum",
        "../../enums/culture_types", "../../exceptions/culture", "../validation/culture_validator"
    ],
    "dependents": ["domain/services", "infrastructure/llm", "application/use_cases"],
    "infrastructure_independent": True,
    "pure_functions": True,
    "side_effects": "none",
    "focuses_on": "LLM response parsing and data transformation",
    "immutable_data": True,
    "stateless_operations": True
}

# Usage examples in docstring
"""
Usage Examples:

1. Parse single LLM response:
   >>> response = "Male Names: Erik, Olaf\\nFemale Names: Astrid, Ingrid"
   >>> parsed = CultureParser.parse_culture_response(response)
   >>> print(f"Found {len(parsed.male_names)} male names")

2. Extract specific name categories:
   >>> names = CultureParser.extract_name_lists(response)
   >>> print(f"Categories found: {list(names.keys())}")

3. Validate parsed data:
   >>> parsed_dict = CultureParser.normalize_culture_data(parsed)
   >>> result = CultureParser.validate_parsed_data(parsed_dict)
   >>> print(f"Valid: {result.is_valid}")

4. Parse multiple responses:
   >>> responses = [response1, response2, response3]
   >>> parsed_list = parse_multiple_responses(responses)
   >>> merged = merge_multiple_parsed_data(parsed_list)

5. Extract cultural context:
   >>> context = CultureParser.extract_cultural_context(response)
   >>> print(f"Historical period: {context.get('historical_period')}")

6. Validate response format:
   >>> valid, format_type, issues = validate_response_format(response)
   >>> print(f"Format: {format_type.value}, Issues: {len(issues)}")
"""