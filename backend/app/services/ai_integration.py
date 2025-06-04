import httpx
import json
import os
from fastapi import HTTPException

class AIService:
    def __init__(self):
        self.ollama_url = os.environ.get("OLLAMA_API_URL", "http://ollama:11434/api")
        self.sd_url = os.environ.get("SD_API_URL", "http://stable_diffusion:7860/api")
        
        # Load prompt templates
        self.templates = {}
        self._load_prompt_templates()
        
    def _load_prompt_templates(self):
        """Load prompt templates from the Ollama container"""
        # In a real implementation, these would be loaded from files or a database
        self.templates["character_creation"] = {
            "system": "You are a D&D 5e (2024 edition) character creation assistant. Help the user create a balanced and rule-compliant character.",
            "user_template": "I want to create a character with these attributes: {attributes}. Please help guide me through the process."
        }
        
        self.templates["rules_validation"] = {
            "system": "You are a D&D 5e rules expert. Validate if character attributes comply with official rules.",
            "user_template": "Validate if this character configuration complies with D&D 5e rules: {character_json}"
        }
    
    async def generate_character_guidance(self, prompt: str, character_data: dict = None):
        """Generate LLM guidance for character creation"""
        system_prompt = self.templates["character_creation"]["system"]
        
        context = ""
        if character_data:
            context = f"Current character data: {json.dumps(character_data)}\n\n"
        
        payload = {
            "model": "llama3:8b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context + prompt}
            ],
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.ollama_url}/chat", json=payload)
                response.raise_for_status()
                result = response.json()
                return result["message"]["content"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
    
    async def validate_character_rules(self, character_data: dict):
        """Use LLM to validate character against D&D rules"""
        system_prompt = self.templates["rules_validation"]["system"]
        user_prompt = self.templates["rules_validation"]["user_template"].format(
            character_json=json.dumps(character_data)
        )
        
        payload = {
            "model": "llama3:8b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.ollama_url}/chat", json=payload)
                response.raise_for_status()
                result = response.json()
                validation_response = result["message"]["content"]
                
                # Parse the validation response (assumes structured response from LLM)
                try:
                    # Try to extract a JSON response if the LLM returned one
                    import re
                    json_match = re.search(r'```json\n(.*?)\n```', validation_response, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(1))
                    else:
                        # Simple heuristic for validation - look for specific keywords
                        is_valid = "valid" in validation_response.lower() and "invalid" not in validation_response.lower()
                        return {"valid": is_valid, "message": validation_response}
                except:
                    # Fallback to simple text response
                    return {"valid": True, "message": validation_response}
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI validation error: {str(e)}")
    
    async def generate_character_portrait(self, character_data: dict):
        """Generate character portrait using Stable Diffusion"""
        # Extract relevant character details for the prompt
        species = character_data.get("species", "human")
        character_class = character_data.get("class", "adventurer")
        description = character_data.get("description", "")
        
        # Create a detailed prompt for the image generation
        prompt = f"fantasy character portrait of a {species} {character_class}, {description}, highly detailed, professional digital art, fantasy concept art, trending on artstation"
        
        payload = {
            "prompt": prompt,
            "negative_prompt": "deformed, distorted, disfigured, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, disconnected limbs, mutation, mutated, ugly, disgusting, duplicate, morbid, mutilated, out of frame, watermark, signature, text",
            "steps": 30,
            "width": 512,
            "height": 768,
            "guidance_scale": 7.5
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.sd_url}/txt2img", json=payload)
                response.raise_for_status()
                result = response.json()
                return result["images"][0]  # Returns base64-encoded image
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image generation error: {str(e)}")