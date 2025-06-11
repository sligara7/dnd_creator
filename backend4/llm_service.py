from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json
import json5
import re


# # Using Ollama (default)
# llm_service = OllamaLLMService(model="llama3")

# # Using OpenAI
# llm_service = OpenAILLMService(api_key="your-api-key", model="gpt-4")

# # Using Anthropic
# llm_service = AnthropicLLMService(api_key="your-api-key", model="claude-3-sonnet-20240229")

# # Using factory
# llm_service = create_llm_service('ollama', model="llama3")
# llm_service = create_llm_service('openai', api_key="your-key", model="gpt-4")

class LLMService(ABC):
    """Abstract base class for LLM services."""
    
    @abstractmethod
    def generate(self, prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the LLM service is available."""
        pass


class OllamaLLMService(LLMService):
    """Ollama implementation of LLM service."""
    
    def __init__(self, model: str = "llama3", host: str = "http://localhost:11434"):
        import ollama
        
        self.model = model
        self.ollama_client = ollama.Client(host=host)
        self.conversation_history = []
        
        # Enhanced system prompt for specialized equipment and detailed backgrounds
        self.system_prompt = """
        You are a D&D character creation assistant that ONLY responds with valid JSON.

        IMPORTANT: Your entire response must be a single valid JSON object with NO explanatory text before or after.
        Do not include markdown formatting like ```json or ``` around your response.

        ALWAYS include a character name. Generate an appropriate fantasy name if none is provided.

        When creating characters:
        1. Create specialized equipment that fits the character concept (e.g., lightsaber for Jedi, magic staff for wizards)
        2. Develop detailed, immersive backstories (minimum 3-4 paragraphs)
        3. Scale abilities and equipment to the specified character level
        4. Include unique magical items or artifacts when appropriate
        5. Maximize detail while maintaining JSON validity

        Create character data using this exact schema:
        {
          "name": "ALWAYS provide a character name here - generate one if needed",
          "species": "Species",
          "level": X,
          "classes": {"Class Name": Level},
          "subclasses": {"Class Name": "Subclass"},
          "background": "Background",
          "alignment": ["Ethical", "Moral"],
          "ability_scores": {
            "strength": X, "dexterity": X, "constitution": X, 
            "intelligence": X, "wisdom": X, "charisma": X
          },
          "skill_proficiencies": ["Skill1", "Skill2"],
          "saving_throw_proficiencies": ["Ability1", "Ability2"],
          "personality_traits": ["Trait1", "Trait2", "Trait3"],
          "ideals": ["Ideal1", "Ideal2"],
          "bonds": ["Bond1", "Bond2"],
          "flaws": ["Flaw1", "Flaw2"],
          "armor": {
            "name": "Armor Name",
            "type": "light/medium/heavy",
            "ac_base": X,
            "special_properties": ["property1", "property2"],
            "description": "Detailed description of the armor"
          },
          "weapons": [
            {
              "name": "Weapon Name",
              "type": "simple/martial/exotic",
              "damage": "XdY + modifier",
              "damage_type": "slashing/piercing/bludgeoning/force/etc",
              "properties": ["property1", "property2"],
              "special_abilities": ["ability1", "ability2"],
              "description": "Detailed description including special features",
              "magical": true/false,
              "rarity": "common/uncommon/rare/very rare/legendary/artifact"
            }
          ],
          "magical_items": [
            {
              "name": "Item Name",
              "type": "wondrous item/ring/amulet/etc",
              "rarity": "common/uncommon/rare/very rare/legendary/artifact",
              "attunement": true/false,
              "properties": ["property1", "property2"],
              "description": "Detailed description of magical properties"
            }
          ],
          "equipment": [
            {
              "name": "Item Name",
              "quantity": X,
              "description": "Item description"
            }
          ],
          "backstory": "Detailed backstory (minimum 3-4 paragraphs covering origin, motivations, key events, current goals)",
          "personality_details": {
            "mannerisms": ["mannerism1", "mannerism2"],
            "interaction_traits": ["trait1", "trait2"],
            "appearance": "Detailed physical description",
            "voice_and_speech": "How they speak and sound"
          }
        }

        If character is a spellcaster, include:
        {
          "spellcasting_ability": "ability",
          "spell_save_dc": X,
          "spell_attack_bonus": X,
          "spells_known": {
            "0": ["Cantrip1", "Cantrip2"],
            "1": ["1st Level Spell1", "1st Level Spell2"],
            "2": ["2nd Level Spell1"],
            etc.
          },
          "spell_slots": {
            "1": X, "2": X, "3": X, etc.
          }
        }

        For special character concepts (Jedi, etc.), create appropriate abilities:
        {
          "special_abilities": [
            {
              "name": "Ability Name",
              "type": "supernatural/spell-like/extraordinary",
              "uses": "X/day" or "at will" or "constant",
              "description": "Detailed description of the ability"
            }
          ]
        }

        REMEMBER: 
        1. Respond ONLY with valid JSON. No other text.
        2. ALWAYS include a character name - generate one if needed.
        3. Scale everything to the specified character level.
        4. Create specialized, thematic equipment and abilities.
        5. Write detailed, immersive backstories.
        """
        
        self._ensure_model_available()
    
    def _ensure_model_available(self) -> None:
        """Verify that the required model is available, attempt to pull if not."""
        try:
            models = self.ollama_client.list()
            model_exists = False
            if 'models' in models:
                model_exists = any(model.get('name', '') == self.model for model in models['models'])
            
            if not model_exists:
                print(f"Model {self.model} not found. Attempting to pull...")
                self.ollama_client.pull(self.model)
                print(f"Successfully pulled {self.model}")
                
        except Exception as e:
            print(f"Warning: Could not verify model availability: {str(e)}")
    
    def generate(self, prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response from Ollama."""
        try:
            if conversation_history is None:
                conversation_history = self.conversation_history
            
            response = self.ollama_client.chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    *conversation_history,
                    {'role': 'user', 'content': prompt}
                ]
            )
            
            # Add to conversation history
            self.conversation_history.append({'role': 'user', 'content': prompt})
            self.conversation_history.append({'role': 'assistant', 'content': response['message']['content']})
            
            return response['message']['content']
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "{}"
    
    def test_connection(self) -> bool:
        """Test the connection to the Ollama service."""
        try:
            response = self.ollama_client.generate(
                model=self.model,
                prompt="Hello, are you working properly?"
            )
            print(f"Connection test successful: {response['response'][:50]}...")
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


class OpenAILLMService(LLMService):
    """OpenAI implementation of LLM service."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", max_tokens: int = 4000):
        try:
            import openai
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.conversation_history = []
        
        # Same enhanced system prompt as Ollama
        self.system_prompt = """
        You are a D&D character creation assistant that ONLY responds with valid JSON.

        IMPORTANT: Your entire response must be a single valid JSON object with NO explanatory text before or after.
        Do not include markdown formatting like ```json or ``` around your response.

        ALWAYS include a character name. Generate an appropriate fantasy name if none is provided.

        When creating characters:
        1. Create specialized equipment that fits the character concept (e.g., lightsaber for Jedi, magic staff for wizards)
        2. Develop detailed, immersive backstories (minimum 3-4 paragraphs)
        3. Scale abilities and equipment to the specified character level
        4. Include unique magical items or artifacts when appropriate
        5. Maximize detail while maintaining JSON validity

        [Same detailed schema as Ollama service...]

        REMEMBER: 
        1. Respond ONLY with valid JSON. No other text.
        2. ALWAYS include a character name - generate one if needed.
        3. Scale everything to the specified character level.
        4. Create specialized, thematic equipment and abilities.
        5. Write detailed, immersive backstories.
        """
    
    def generate(self, prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response from OpenAI."""
        try:
            if conversation_history is None:
                conversation_history = self.conversation_history
            
            messages = [
                {'role': 'system', 'content': self.system_prompt},
                *conversation_history,
                {'role': 'user', 'content': prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Add to conversation history
            self.conversation_history.append({'role': 'user', 'content': prompt})
            self.conversation_history.append({'role': 'assistant', 'content': content})
            
            return content
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return "{}"
    
    def test_connection(self) -> bool:
        """Test the connection to the OpenAI service."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': 'Hello, are you working properly?'}],
                max_tokens=50
            )
            print(f"OpenAI connection test successful: {response.choices[0].message.content[:50]}...")
            return True
        except Exception as e:
            print(f"OpenAI connection test failed: {e}")
            return False


class AnthropicLLMService(LLMService):
    """Anthropic Claude implementation of LLM service."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", max_tokens: int = 4000):
        try:
            import anthropic
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.conversation_history = []
        
        # Same enhanced system prompt
        self.system_prompt = """
        You are a D&D character creation assistant that ONLY responds with valid JSON.

        IMPORTANT: Your entire response must be a single valid JSON object with NO explanatory text before or after.
        Do not include markdown formatting like ```json or ``` around your response.

        ALWAYS include a character name. Generate an appropriate fantasy name if none is provided.

        When creating characters:
        1. Create specialized equipment that fits the character concept (e.g., lightsaber for Jedi, magic staff for wizards)
        2. Develop detailed, immersive backstories (minimum 3-4 paragraphs)
        3. Scale abilities and equipment to the specified character level
        4. Include unique magical items or artifacts when appropriate
        5. Maximize detail while maintaining JSON validity

        [Same detailed schema as other services...]

        REMEMBER: 
        1. Respond ONLY with valid JSON. No other text.
        2. ALWAYS include a character name - generate one if needed.
        3. Scale everything to the specified character level.
        4. Create specialized, thematic equipment and abilities.
        5. Write detailed, immersive backstories.
        """
    
    def generate(self, prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response from Anthropic Claude."""
        try:
            if conversation_history is None:
                conversation_history = self.conversation_history
            
            # Convert conversation history to Claude format
            messages = []
            for msg in conversation_history:
                if msg['role'] != 'system':  # Claude handles system prompts separately
                    messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            # Add current prompt
            messages.append({'role': 'user', 'content': prompt})
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.system_prompt,
                messages=messages
            )
            
            content = response.content[0].text
            
            # Add to conversation history
            self.conversation_history.append({'role': 'user', 'content': prompt})
            self.conversation_history.append({'role': 'assistant', 'content': content})
            
            return content
        except Exception as e:
            print(f"Error calling Anthropic: {e}")
            return "{}"
    
    def test_connection(self) -> bool:
        """Test the connection to the Anthropic service."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                system="You are a helpful assistant.",
                messages=[{'role': 'user', 'content': 'Hello, are you working properly?'}]
            )
            print(f"Anthropic connection test successful: {response.content[0].text[:50]}...")
            return True
        except Exception as e:
            print(f"Anthropic connection test failed: {e}")
            return False

class BedrockLLMService(LLMService):
    """AWS Bedrock implementation of LLM service."""
    
    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0", 
                 region: str = "us-east-1", max_tokens: int = 4000):
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 package not installed. Run: pip install boto3")
        
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.conversation_history = []
        
        # Initialize Bedrock client
        self.bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region
        )
        
        # Same enhanced system prompt as other services
        self.system_prompt = """
        You are a D&D character creation assistant that ONLY responds with valid JSON.
        [Same detailed prompt as other services...]
        """
    
    def generate(self, prompt: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response from AWS Bedrock."""
        try:
            if conversation_history is None:
                conversation_history = self.conversation_history
            
            # Build conversation for Claude via Bedrock
            messages = []
            for msg in conversation_history:
                if msg['role'] != 'system':
                    messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            messages.append({'role': 'user', 'content': prompt})
            
            # Bedrock request body for Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "system": self.system_prompt,
                "messages": messages,
                "temperature": 0.7
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            
            # Add to conversation history
            self.conversation_history.append({'role': 'user', 'content': prompt})
            self.conversation_history.append({'role': 'assistant', 'content': content})
            
            return content
            
        except Exception as e:
            print(f"Error calling Bedrock: {e}")
            return "{}"
    
    def test_connection(self) -> bool:
        """Test the connection to AWS Bedrock."""
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 50,
                "system": "You are a helpful assistant.",
                "messages": [{'role': 'user', 'content': 'Hello, are you working properly?'}]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            content = response_body['content'][0]['text']
            print(f"Bedrock connection test successful: {content[:50]}...")
            return True
            
        except Exception as e:
            print(f"Bedrock connection test failed: {e}")
            return False


class JSONExtractor:
    """Utility class for extracting JSON from LLM responses."""
    
    @staticmethod
    def extract_json(text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response with multi-layered fallback strategies."""
        try:
            print(f"Processing response: {text[:100]}..." if len(text) > 100 else text)
            
            # 1. First, try direct JSON parsing
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                print("Direct JSON parsing failed, trying alternatives...")
            
            # 2. Try to find JSON content using regex for code blocks
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
            if json_match:
                json_content = json_match.group(1)
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    print("Code block extraction failed...")
            
            # 3. Try to find the outermost JSON object
            json_match = re.search(r'({[\s\S]*})', text)
            if json_match:
                json_content = json_match.group(1)
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    print("Regex JSON extraction failed...")
            
            # 4. Try manual extraction of start/end braces
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx >= 0 and end_idx >= 0 and end_idx > start_idx:
                json_content = text[start_idx:end_idx+1]
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    print("Manual brace extraction failed...")
            
            # 5. Try with json5 for more lenient parsing
            try:
                return json5.loads(text)
            except Exception:
                print("JSON5 parsing failed...")
                
            # 6. Try cleaning and json5 parsing
            cleaned_text = text.replace('\n', ' ').replace('\r', '')
            try:
                return json5.loads(cleaned_text)
            except Exception:
                print("Clean JSON5 parsing failed...")
            
            # 7. Try fixing common JSON issues
            fixed_text = JSONExtractor._fix_common_json_issues(text)
            if fixed_text:
                try:
                    return json.loads(fixed_text)
                except json.JSONDecodeError:
                    pass
            
            print("All JSON parsing methods failed")
            return {}
            
        except Exception as e:
            print(f"Error extracting JSON: {str(e)}")
            return {}
    
    @staticmethod
    def _fix_common_json_issues(text: str) -> str:
        """Attempt to fix common JSON formatting issues."""
        try:
            # Remove any text before the first {
            start_idx = text.find('{')
            if start_idx > 0:
                text = text[start_idx:]
            
            # Remove any text after the last }
            end_idx = text.rfind('}')
            if end_idx >= 0:
                text = text[:end_idx + 1]
            
            # Fix trailing commas
            text = re.sub(r',(\s*[}\]])', r'\1', text)
            
            # Fix unquoted keys (basic attempt)
            text = re.sub(r'(\w+):', r'"\1":', text)
            
            # Fix single quotes to double quotes
            text = text.replace("'", '"')
            
            return text
        except Exception:
            return ""


# Factory function for easy LLM service creation
def create_llm_service(service_type: str, **kwargs) -> LLMService:
    """
    Factory function to create LLM services.
    
    Args:
        service_type: Type of service ('ollama', 'openai', 'anthropic', 'bedrock')
        **kwargs: Additional arguments for the specific service
    
    Returns:
        LLMService: Configured LLM service instance
    """
    if service_type.lower() == 'ollama':
        return OllamaLLMService(**kwargs)
    elif service_type.lower() == 'openai':
        return OpenAILLMService(**kwargs)
    elif service_type.lower() == 'anthropic':
        return AnthropicLLMService(**kwargs)
    elif service_type.lower() == 'bedrock':
        return BedrockLLMService(**kwargs)
    else:
        raise ValueError(f"Unknown service type: {service_type}")