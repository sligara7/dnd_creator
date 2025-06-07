import requests
import json
import logging
from typing import Dict, Any, Optional, List, Union, Generator

logger = logging.getLogger(__name__)

class OllamaService:
    """
    Service to connect to locally running Ollama LLM instances.
    
    Provides methods to generate text, chat completions, and streamed responses
    using local Ollama models.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3"):
        """
        Initialize the Ollama service.
        
        Args:
            base_url: URL of the Ollama API (default: http://localhost:11434)
            default_model: Default model to use for generations (default: llama3)
        """
        self.base_url = base_url
        self.default_model = default_model
    
    def generate_text(self, 
                     prompt: str, 
                     system_message: str = None,
                     model: str = None,
                     max_tokens: int = 1500,
                     temperature: float = 0.7) -> str:
        """
        Send a prompt to Ollama and get a simple text response.
        
        Args:
            prompt: User input prompt
            system_message: Optional system message to guide the model behavior
            model: Model to use (defaults to the instance's default_model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (higher = more creative, lower = more deterministic)
            
        Returns:
            str: Generated text response
            
        Raises:
            ConnectionError: If connection to Ollama fails
            ValueError: If the request is invalid
        """
        url = f"{self.base_url}/api/generate"
        
        # Prepare full prompt with system message if provided
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"
            
        payload = {
            "model": model or self.default_model,
            "prompt": full_prompt,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.RequestException as e:
            logger.error(f"Error calling Ollama: {e}")
            raise ConnectionError(f"Failed to connect to Ollama service: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Ollama: {e}")
            raise ValueError(f"Invalid response from Ollama: {e}")
    
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model: str = None,
                       max_tokens: int = 1500,
                       temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate a chat completion from a list of messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Model to use (defaults to the instance's default_model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Dict: Response containing the generated message and metadata
        """
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error calling Ollama chat API: {e}")
            raise ConnectionError(f"Failed to connect to Ollama service: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Ollama: {e}")
            raise ValueError(f"Invalid response from Ollama: {e}")
            
    def stream_generation(self, 
                         prompt: str, 
                         system_message: str = None,
                         model: str = None,
                         max_tokens: int = 1500) -> Generator[str, None, None]:
        """
        Stream a response from Ollama token by token.
        
        Args:
            prompt: User input prompt
            system_message: Optional system message to guide the model behavior
            model: Model to use (defaults to the instance's default_model)
            max_tokens: Maximum tokens to generate
            
        Yields:
            str: Generated text tokens as they become available
        """
        url = f"{self.base_url}/api/generate"
        
        # Prepare full prompt with system message if provided
        full_prompt = prompt
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"
            
        payload = {
            "model": model or self.default_model,
            "prompt": full_prompt,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        try:
            with requests.post(url, json=payload, stream=True) as response:
                response.raise_for_status()
                
                # Process the streaming response
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                        except json.JSONDecodeError:
                            continue
                            
        except requests.RequestException as e:
            logger.error(f"Error streaming from Ollama: {e}")
            raise ConnectionError(f"Failed to connect to Ollama service: {e}")