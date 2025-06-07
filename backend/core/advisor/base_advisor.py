"""
Base Advisor Module

Provides a foundation for all LLM-powered advisors with shared functionality
for prompt creation, response parsing, and LLM interaction.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path

try:
    from backend.core.services.ollama_service import OllamaService
except ImportError:
    # Fallback for development
    class OllamaService:
        def generate_text(self, prompt, system_message=None):
            return "LLM service not available"
        
        def generate(self, prompt):
            return "LLM service not available"

logger = logging.getLogger(__name__)

class BaseAdvisor:
    """
    Base class for all LLM-powered D&D advisors.
    
    Provides common functionality for LLM interaction, prompt creation,
    response parsing, and error handling that all advisor classes can leverage.
    """

    def __init__(self, llm_service=None, system_prompt=None, cache_enabled=True):
        """
        Initialize the base advisor with LLM service and settings.
        
        Args:
            llm_service: LLM service client for generating responses
            system_prompt: Default system prompt for this advisor domain
            cache_enabled: Whether to cache LLM responses for efficiency
        """
        self.llm_service = llm_service or OllamaService()
        self.system_prompt = system_prompt or "You are a D&D 5e (2024 rules) expert assistant."
        self.cache_enabled = cache_enabled
        self.response_cache = {}
        self.data_path = Path("backend/data")
    
    def _create_prompt(self, task: str, context: str) -> str:
        """
        Create a well-structured prompt for the LLM.
        
        Args:
            task: Short description of the task
            context: Context information for the request
            
        Returns:
            Formatted prompt string
        """
        return f"{self.system_prompt}\n\nTask: {task}\n\nInformation: {context}"
    
    def _format_prompt(self, title: str, context: str, elements: List[str] = None) -> str:
        """
        Format a standard prompt with consistent structure.
        
        Args:
            title: Title of the request
            context: Context information
            elements: Optional list of elements to include in the response
            
        Returns:
            Formatted prompt string
        """
        prompt = f"# {title}\n\n{context}\n\n"
        
        if elements:
            elements_text = "\n".join([f"- {element}" for element in elements])
            prompt += f"Include the following elements:\n{elements_text}\n\n"
            
        prompt += "Format your response as structured data that can be parsed into a JSON object."
        return prompt
    
    def _get_llm_response(self, query_type: str, prompt: str, key_data: Dict[str, Any]) -> str:
        """
        Get response from LLM, using cache if enabled and available.
        
        Args:
            query_type: Type of query for cache identification
            prompt: The prompt to send to the LLM
            key_data: Key data elements for cache lookup
            
        Returns:
            LLM response text
        """
        if not self.cache_enabled:
            return self.llm_service.generate(prompt)
        
        # Create a cache key based on query type and key data
        cache_key = f"{query_type}_{json.dumps(key_data, sort_keys=True)}"
        
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]
            
        # Generate new response and cache it
        response = self.llm_service.generate(prompt)
        self.response_cache[cache_key] = response
        return response
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response with robust error handling.
        
        Args:
            text: LLM response text
            
        Returns:
            Extracted JSON data or None if parsing fails
        """
        try:
            # Find JSON pattern in response
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1).strip()
                return json.loads(json_text)
                
            # Try to find a naked JSON object
            json_match = re.search(r'(\{[\s\S]*\})', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
                
            # Try to find a naked JSON array
            json_match = re.search(r'(\[[\s\S]*\])', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
                
        except Exception as e:
            logger.error(f"Error parsing JSON from LLM response: {e}")
            
        # If all parsing attempts fail, try to extract structured text
        return self._parse_structured_text(text)
    
    def _parse_structured_text(self, text: str) -> Dict[str, Any]:
        """
        Parse structured text into a dictionary when JSON extraction fails.
        
        Args:
            text: Text to parse
            
        Returns:
            Parsed dictionary of data
        """
        result = {}
        current_key = None
        current_value = []
        
        # Simple parser for "key: value" formatted text
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if this line starts a new key
            key_match = re.match(r'^([A-Za-z_]+):\s*(.*)$', line)
            if key_match:
                # Save previous key-value pair if exists
                if current_key and current_value:
                    result[current_key] = '\n'.join(current_value).strip()
                
                # Start new key
                current_key = key_match.group(1).lower()
                value_part = key_match.group(2).strip()
                if value_part:
                    current_value = [value_part]
                else:
                    current_value = []
            elif current_key:
                # Continue previous value
                current_value.append(line)
        
        # Add the final key-value pair
        if current_key and current_value:
            result[current_key] = '\n'.join(current_value).strip()
            
        return result
    
    def _safe_get(self, data_dict: Dict[str, Any], key_path: List[str], default: Any = None) -> Any:
        """
        Safely get a nested value from a dictionary.
        
        Args:
            data_dict: Dictionary to extract from
            key_path: List of keys forming the path to the desired value
            default: Default value if path doesn't exist
            
        Returns:
            Value at key_path or default
        """
        current = data_dict
        for key in key_path:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current
    
    def _extract_list_items(self, text: str) -> List[str]:
        """
        Extract list items from text that might be formatted as bullets or numbered list.
        
        Args:
            text: Text that might contain a list
            
        Returns:
            List of extracted items
        """
        # Try to find bullet points or numbered items
        items = re.findall(r"(?:[-•*]\s*|^\d+\.\s*)([^\n]+)", text, re.MULTILINE)
        if items:
            return [item.strip() for item in items if item.strip()]
            
        # If no bullet/numbered format, try splitting by periods or commas
        if "," in text:
            return [s.strip() for s in re.split(r',|\band\b', text) if s.strip()]
        else:
            return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    
    def clear_cache(self) -> None:
        """Clear the LLM response cache."""
        self.response_cache = {}
        
    def export_cache(self, filepath: str) -> bool:
        """
        Export the current cache to a JSON file.
        
        Args:
            filepath: Path to save the cache file
            
        Returns:
            bool: True if export was successful
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.response_cache, f)
            return True
        except Exception as e:
            logger.error(f"Failed to export cache: {str(e)}")
            return False
            
    def import_cache(self, filepath: str) -> bool:
        """
        Import a previously exported cache from a JSON file.
        
        Args:
            filepath: Path to the cache file
            
        Returns:
            bool: True if import was successful
        """
        try:
            with open(filepath, 'r') as f:
                imported_cache = json.load(f)
                if self.cache_enabled:
                    self.response_cache.update(imported_cache)
                else:
                    self.response_cache = imported_cache
                    self.cache_enabled = True
            return True
        except Exception as e:
            logger.error(f"Failed to import cache: {str(e)}")
            return False