# ## **5. `llm_services.py`**
# **Infrastructure layer for AI services**
# - **Classes**: `LLMService` (abstract), `OllamaLLMService`, `OpenAILLMService`
# - **Functions**: `create_llm_service`, `check_ollama_setup`
# - **Purpose**: AI service abstraction, Ollama and OpenAI integration, connection management
# - **Dependencies**: None (infrastructure layer)

from typing import Dict, Any
from abc import ABC, abstractmethod
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# TIMEOUT CONFIGURATION - Adjust these for slow hardware
# ============================================================================

# Default timeouts optimized for slow hardware
DEFAULT_GENERATION_TIMEOUT = 300  # 5 minutes for text generation
DEFAULT_CONNECTION_TIMEOUT = 30   # 30 seconds for connection tests  
DEFAULT_API_TIMEOUT = 30          # 30 seconds for API requests
DEFAULT_COMMAND_TIMEOUT = 20      # 20 seconds for command execution
MAX_CONNECTION_ATTEMPTS = 5       # Number of connection retry attempts
CONNECTION_RETRY_DELAY = 5        # Seconds between connection attempts

# For extremely slow hardware, you can increase these values:
# - SLOW_HARDWARE_GENERATION_TIMEOUT = 300 (5 minutes)
# - SLOW_HARDWARE_CONNECTION_TIMEOUT = 30 (30 seconds)
# - SLOW_HARDWARE_API_TIMEOUT = 30 (30 seconds)

# ============================================================================
# LLM SERVICE LAYER
# ============================================================================

class LLMService(ABC):
    """Abstract base class for LLM services."""
    
    @abstractmethod
    def generate(self, prompt: str, timeout_seconds: int = DEFAULT_GENERATION_TIMEOUT) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the LLM service is available."""
        pass

class OllamaLLMService(LLMService):
    """Ollama LLM service implementation with enhanced timeout and error handling."""
    
    def __init__(self, model: str = "llama3", host: str = "http://localhost:11434"):
        try:
            import ollama
            self.model = model
            self.client = ollama.Client(host=host)
            self.executor = ThreadPoolExecutor(max_workers=1)
        except ImportError:
            raise ImportError("Ollama package not installed. Run: pip install ollama")
    
    def generate(self, prompt: str, timeout_seconds: int = DEFAULT_GENERATION_TIMEOUT) -> str:
        """Generate response with robust timeout protection and fallback."""
        
        # Pre-validate prompt
        if not prompt or not prompt.strip():
            raise ValueError("Empty prompt provided")
        
        # Shorten prompt if too long to prevent timeouts
        if len(prompt) > 8000:
            logger.warning("Prompt too long, truncating...")
            prompt = prompt[:8000] + "\n\nCRITICAL: Return complete valid JSON only."
        
        try:
            logger.info(f"Sending request to Ollama (timeout: {timeout_seconds}s)...")
            
            # Use ThreadPoolExecutor for better timeout control
            future = self.executor.submit(self._make_ollama_request, prompt)
            
            try:
                content = future.result(timeout=timeout_seconds)
                logger.info(f"Received response: {len(content)} characters")
                return content
                
            except FutureTimeoutError:
                logger.error(f"Request timed out after {timeout_seconds} seconds")
                future.cancel()  # Try to cancel the request
                print(f"\n⏰ LLM request timed out after {timeout_seconds} seconds")
                print("💡 For very slow hardware, you can increase timeout values in llm_services.py:")
                print("   - Set DEFAULT_GENERATION_TIMEOUT = 300 (5 minutes)")
                print("   - Or call generate() with a larger timeout_seconds parameter")
                raise TimeoutError(f"LLM request timed out after {timeout_seconds} seconds")
                
        except TimeoutError:
            raise  # Re-raise timeout errors
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise Exception(f"LLM generation failed: {e}")
    
    def _make_ollama_request(self, prompt: str) -> str:
        """Make the actual Ollama request (to be run in thread)."""
        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a D&D assistant. Respond ONLY with valid JSON. No explanations, no markdown, no extra text. Just JSON."
                },
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 1024,  # Further reduced for speed
                "num_ctx": 2048,     # Reduced context window
                "stop": ["```", "Note:", "Here's", "I'll", "**"],
                "stream": False      # Ensure non-streaming response
            }
        )
        
        # Handle the Ollama response object correctly
        if hasattr(response, 'message') and hasattr(response.message, 'content'):
            content = response.message.content
        elif isinstance(response, dict) and "message" in response:
            content = response["message"]["content"]
        else:
            raise Exception(f"Unexpected response format: {type(response)}")
        
        if not content or not content.strip():
            raise Exception("Empty response from Ollama")
        
        return content
    
    def test_connection(self) -> bool:
        """Test connection with extended timeout for slow hardware."""
        try:
            future = self.executor.submit(
                self.client.chat,
                model=self.model,
                messages=[{"role": "user", "content": "Test"}],
                options={"stream": False}
            )
            result = future.result(timeout=DEFAULT_CONNECTION_TIMEOUT)
            return result is not None
        except Exception:
            return False
    
    def __del__(self):
        """Clean up executor on deletion."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

class OpenAILLMService(LLMService):
    """OpenAI LLM service implementation for GPT models."""
    
    def __init__(self, api_key: str, model: str = "gpt-4.1-nano-2025-04-14"):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model
            self.executor = ThreadPoolExecutor(max_workers=1)
            logger.info(f"OpenAI service initialized with model: {model}")
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    def generate(self, prompt: str, timeout_seconds: int = DEFAULT_GENERATION_TIMEOUT) -> str:
        """Generate response using OpenAI API."""
        
        if not prompt or not prompt.strip():
            raise ValueError("Empty prompt provided")
        
        try:
            logger.info(f"Sending request to OpenAI {self.model} (timeout: {timeout_seconds}s)...")
            
            # Use ThreadPoolExecutor for timeout control
            future = self.executor.submit(self._make_openai_request, prompt)
            
            try:
                content = future.result(timeout=timeout_seconds)
                logger.info(f"Received OpenAI response: {len(content)} characters")
                return content
                
            except FutureTimeoutError:
                logger.error(f"OpenAI request timed out after {timeout_seconds} seconds")
                future.cancel()
                raise TimeoutError(f"OpenAI request timed out after {timeout_seconds} seconds")
                
        except TimeoutError:
            raise
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise Exception(f"OpenAI API error: {e}")
    
    def _make_openai_request(self, prompt: str) -> str:
        """Make the actual OpenAI API request."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful D&D character creation assistant. Always return valid JSON when requested."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content.strip()
            else:
                raise Exception("No response content from OpenAI")
                
        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}")
            raise Exception(f"OpenAI API request failed: {e}")
    
    def test_connection(self) -> bool:
        """Test OpenAI API connection."""
        try:
            logger.info("Testing OpenAI connection...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return bool(response.choices and response.choices[0].message)
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
    
    def __del__(self):
        """Clean up executor on deletion."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

# ============================================================================
# SERVICE FACTORY AND UTILITIES
# ============================================================================

def create_llm_service_with_custom_timeouts(
    generation_timeout: int = DEFAULT_GENERATION_TIMEOUT,
    connection_timeout: int = DEFAULT_CONNECTION_TIMEOUT,
    api_timeout: int = DEFAULT_API_TIMEOUT,
    max_attempts: int = MAX_CONNECTION_ATTEMPTS,
    retry_delay: int = CONNECTION_RETRY_DELAY
) -> OllamaLLMService:
    """
    Create an LLM service with custom timeout settings for very slow hardware.
    
    Args:
        generation_timeout: Timeout for text generation (default: 120s)
        connection_timeout: Timeout for connection tests (default: 15s)
        api_timeout: Timeout for API requests (default: 15s)
        max_attempts: Maximum connection attempts (default: 5)
        retry_delay: Delay between connection attempts (default: 5s)
    
    Returns:
        Configured OllamaLLMService instance
    
    Example for very slow hardware:
        llm_service = create_llm_service_with_custom_timeouts(
            generation_timeout=300,  # 5 minutes
            connection_timeout=30,   # 30 seconds
            api_timeout=30,         # 30 seconds
            max_attempts=10,        # More attempts
            retry_delay=10          # Longer delays
        )
    """
    # Temporarily override global constants
    global DEFAULT_GENERATION_TIMEOUT, DEFAULT_CONNECTION_TIMEOUT, DEFAULT_API_TIMEOUT
    global MAX_CONNECTION_ATTEMPTS, CONNECTION_RETRY_DELAY
    
    original_values = (
        DEFAULT_GENERATION_TIMEOUT, DEFAULT_CONNECTION_TIMEOUT, DEFAULT_API_TIMEOUT,
        MAX_CONNECTION_ATTEMPTS, CONNECTION_RETRY_DELAY
    )
    
    try:
        DEFAULT_GENERATION_TIMEOUT = generation_timeout
        DEFAULT_CONNECTION_TIMEOUT = connection_timeout
        DEFAULT_API_TIMEOUT = api_timeout
        MAX_CONNECTION_ATTEMPTS = max_attempts
        CONNECTION_RETRY_DELAY = retry_delay
        
        print(f"🐌 Creating LLM service with extended timeouts for slow hardware:")
        print(f"   Generation timeout: {generation_timeout}s")
        print(f"   Connection timeout: {connection_timeout}s")
        print(f"   API timeout: {api_timeout}s")
        print(f"   Max attempts: {max_attempts}")
        print(f"   Retry delay: {retry_delay}s")
        
        return create_llm_service()
        
    finally:
        # Restore original values
        (DEFAULT_GENERATION_TIMEOUT, DEFAULT_CONNECTION_TIMEOUT, DEFAULT_API_TIMEOUT,
         MAX_CONNECTION_ATTEMPTS, CONNECTION_RETRY_DELAY) = original_values

def create_llm_service(provider: str = "auto", api_key: str = None, model: str = None) -> LLMService:
    """
    Create and configure an LLM service with automatic provider detection.
    
    Args:
        provider: "openai", "ollama", or "auto" (default: auto-detect)
        api_key: API key for cloud providers (OpenAI)
        model: Model name (defaults: gpt-4o-mini for OpenAI, llama3 for Ollama)
    
    Returns:
        Configured LLMService instance
        
    Raises:
        Exception: If no LLM service can be initialized
    """
    print("🔧 Initializing LLM service...")
    
    # Extract OpenAI API key from the file if available
    if not api_key:
        try:
            # Check llm_service_new.py first (where the API key is stored)
            import os
            new_service_file = os.path.join(os.path.dirname(__file__), 'llm_service_new.py')
            if os.path.exists(new_service_file):
                with open(new_service_file, 'r') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('# '):
                        api_key = first_line[2:].strip()  # Remove '# ' prefix
                        print("🔑 Found OpenAI API key in llm_service_new.py")
            
            # Fallback: check current file
            if not api_key:
                with open(__file__, 'r') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('# '):
                        api_key = first_line[2:].strip()  # Remove '# ' prefix
                        print("🔑 Found OpenAI API key in current file")
        except Exception as e:
            print(f"⚠️  Could not read API key from file: {e}")
            pass
    
    # Auto-detect provider if not specified
    if provider == "auto":
        if api_key and api_key.startswith(''):
            provider = "openai"
            print("🤖 Auto-detected OpenAI (API key found)")
        else:
            provider = "ollama"
            print("🦙 Auto-detected Ollama (no API key)")
    
    # Try to create the requested service
    if provider.lower() == "openai":
        if not api_key:
            raise Exception("OpenAI API key required for OpenAI provider")
        
        try:
            model = model or "gpt-4.1-nano-2025-04-14"
            service = OpenAILLMService(api_key=api_key, model=model)
            
            # Test connection
            if service.test_connection():
                print(f"✅ OpenAI service ready ({model})")
                return service
            else:
                raise Exception("OpenAI connection test failed")
                
        except Exception as e:
            print(f"❌ OpenAI initialization failed: {e}")
            if provider != "auto":
                raise Exception(f"OpenAI service failed: {e}")
    
    # Fallback to Ollama or if Ollama was requested
    if provider.lower() in ["ollama", "auto"]:
        try:
            # Check if Ollama is accessible
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=DEFAULT_API_TIMEOUT)
            if response.status_code != 200:
                raise Exception(f"Ollama API returned status {response.status_code}")
            print("✅ Ollama API is accessible")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Ollama API at http://localhost:11434")
            if provider == "auto" and api_key:
                print("⚠️  Falling back to OpenAI...")
                return create_llm_service("openai", api_key, model)
            print("\n💡 SOLUTION STEPS:")
            print("1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
            print("2. Pull a model: ollama pull llama3")  
            print("3. Start service: ollama serve")
            print("4. Verify it's running: ollama list")
            raise Exception("Ollama service not accessible")
        except Exception as e:
            print(f"❌ Error checking Ollama API: {e}")
            if provider == "auto" and api_key:
                print("⚠️  Falling back to OpenAI...")
                return create_llm_service("openai", api_key, model)
            raise Exception(f"Ollama API check failed: {e}")
    
    # Try to create Ollama service
    try:
        model = model or "llama3"
        llm_service = OllamaLLMService(model=model)
        
        max_connection_attempts = MAX_CONNECTION_ATTEMPTS
        
        for attempt in range(max_connection_attempts):
            try:
                logger.info(f"Attempting to connect to Ollama (attempt {attempt + 1}/{max_connection_attempts})")
                print(f"🔄 Connection attempt {attempt + 1}/{max_connection_attempts}...")
                
                if llm_service.test_connection():
                    logger.info("Ollama connection successful")
                    print(f"✅ Ollama service ready ({model})")
                    return llm_service
                else:
                    logger.warning(f"Ollama connection test failed on attempt {attempt + 1}")
                    print(f"⚠️  Connection test failed (attempt {attempt + 1})")
                    if attempt < max_connection_attempts - 1:
                        print(f"   Retrying in {CONNECTION_RETRY_DELAY} seconds...")
                        time.sleep(CONNECTION_RETRY_DELAY)
                        continue
                    else:
                        raise Exception("Ollama connection test failed after all attempts")
                        
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt == max_connection_attempts - 1:
                    print("\n💡 TROUBLESHOOTING:")
                    print("- Make sure Ollama is installed and running")
                    print("- Check if port 11434 is available")
                    print("- Try: ollama serve")
                    print("- Verify with: curl http://localhost:11434/api/tags")
                    raise Exception(f"Failed to initialize Ollama service after {max_connection_attempts} attempts: {e}")
                time.sleep(CONNECTION_RETRY_DELAY)
                
    except Exception as e:
        if provider == "auto" and api_key:
            print("⚠️  Ollama failed, falling back to OpenAI...")
            return create_llm_service("openai", api_key, model)
        raise Exception(f"Ollama service initialization failed: {e}")
    
    # If we get here, no service could be created
    raise Exception("No LLM service could be initialized. Please check your configuration.")

def check_ollama_setup() -> Dict[str, Any]:
    """
    Check Ollama setup and provide diagnostic information.
    
    Returns:
        Dictionary with setup status and diagnostic information
    """
    status = {
        "ollama_installed": False,
        "ollama_running": False,
        "models_available": [],
        "api_accessible": False,
        "issues": [],
        "solutions": []
    }
    
    # Check if ollama command exists
    try:
        import subprocess
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=DEFAULT_COMMAND_TIMEOUT)
        if result.returncode == 0:
            status["ollama_installed"] = True
            print(f"✅ Ollama installed: {result.stdout.strip()}")
        else:
            status["issues"].append("Ollama command failed")
            status["solutions"].append("Reinstall Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
    except FileNotFoundError:
        status["issues"].append("Ollama not installed")
        status["solutions"].append("Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
    except Exception as e:
        status["issues"].append(f"Error checking Ollama installation: {e}")
    
    # Check if API is accessible
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=DEFAULT_API_TIMEOUT)
        if response.status_code == 200:
            status["api_accessible"] = True
            status["ollama_running"] = True
            
            # Get available models
            models_data = response.json()
            status["models_available"] = [model.get("name", "unknown") for model in models_data.get("models", [])]
            print(f"✅ Ollama API accessible with {len(status['models_available'])} models")
            
            if not status["models_available"]:
                status["issues"].append("No models available")
                status["solutions"].append("Pull a model: ollama pull llama3")
                
        else:
            status["issues"].append(f"Ollama API returned status {response.status_code}")
            status["solutions"].append("Restart Ollama: ollama serve")
            
    except requests.exceptions.ConnectionError:
        status["issues"].append("Cannot connect to Ollama API")
        status["solutions"].append("Start Ollama service: ollama serve")
    except Exception as e:
        status["issues"].append(f"API check failed: {e}")
    
    return status
