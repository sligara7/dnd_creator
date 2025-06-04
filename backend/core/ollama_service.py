import requests
import json

class OllamaService:
    """Simple service to connect to locally running Ollama"""
    
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
    
    def generate(self, prompt, model="llama3", max_tokens=1500):
        """Send a prompt to Ollama and get a response"""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.json().get("response", "")
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return f"Error generating response: {e}"
        