# ## **5. `llm_services.py`**
# **Infrastructure layer for AI services**
# - **Classes**: `LLMService` (abstract), `OllamaLLMService`
# - **Functions**: `create_llm_service`, `check_ollama_setup`
# - **Purpose**: AI service abstraction, Ollama integration, connection management
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
DEFAULT_GENERATION_TIMEOUT = 120  # 2 minutes for text generation
DEFAULT_CONNECTION_TIMEOUT = 15   # 15 seconds for connection tests  
DEFAULT_API_TIMEOUT = 15          # 15 seconds for API requests
DEFAULT_COMMAND_TIMEOUT = 10      # 10 seconds for command execution
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
        
        content = response["message"]["content"]
        if not content or not content.strip():
            raise Exception("Empty response from Ollama")
        
        return content
    
    def test_connection(self) -> bool:
        """Test connection with extended timeout for slow hardware."""
        try:
            future = self.executor.submit(
                self.client.generate, 
                model=self.model, 
                prompt="Test"
            )
            future.result(timeout=DEFAULT_CONNECTION_TIMEOUT)  # Use configured timeout
            return True
        except Exception:
            return False
    
    def __del__(self):
        """Clean up executor on deletion."""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

# ============================================================================
# SERVICE FACTORY AND UTILITIES
# ============================================================================

def create_llm_service() -> OllamaLLMService:
    """
    Create and configure an LLM service.
    
    Returns:
        Configured OllamaLLMService instance
        
    Raises:
        Exception: If Ollama service cannot be initialized
    """
    print("🔧 Initializing LLM service...")
    
    # Check if Ollama is accessible
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=DEFAULT_API_TIMEOUT)
        if response.status_code != 200:
            raise Exception(f"Ollama API returned status {response.status_code}")
        print("✅ Ollama API is accessible")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama API at http://localhost:11434")
        print("\n💡 SOLUTION STEPS:")
        print("1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. Pull a model: ollama pull llama3")
        print("3. Start service: ollama serve")
        print("4. Verify it's running: ollama list")
        raise Exception("Ollama service not accessible")
    except Exception as e:
        print(f"❌ Error checking Ollama API: {e}")
        raise Exception(f"Ollama API check failed: {e}")
    
    # Try to create LLM service
    max_connection_attempts = MAX_CONNECTION_ATTEMPTS
    
    for attempt in range(max_connection_attempts):
        try:
            logger.info(f"Attempting to connect to Ollama (attempt {attempt + 1}/{max_connection_attempts})")
            print(f"🔄 Connection attempt {attempt + 1}/{max_connection_attempts}...")
            
            llm_service = OllamaLLMService()
            
            if llm_service.test_connection():
                logger.info("Ollama connection successful")
                print("✅ Ollama connection established")
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
