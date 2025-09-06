"""Locust performance test suite for LLM service."""
import json
import random
import uuid

from locust import HttpUser, task, tag, between
from locust.exception import StopUser


class LLMServiceUser(HttpUser):
    """Simulated user for LLM service performance testing."""
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Initialize test data."""
        # Character generation data
        self.character_prompts = [
            {
                "prompt": "Generate a backstory for a Human Wizard, level 5, from a noble background",
                "parameters": {
                    "character_class": "Wizard",
                    "character_race": "Human",
                    "level": 5,
                    "background": "Noble",
                },
                "theme": {
                    "style": "epic fantasy",
                    "tone": "serious",
                },
            },
            {
                "prompt": "Create a personality profile for an Elf Rogue, level 3, from a criminal background",
                "parameters": {
                    "character_class": "Rogue",
                    "character_race": "Elf",
                    "level": 3,
                    "background": "Criminal",
                },
                "theme": {
                    "style": "dark fantasy",
                    "tone": "gritty",
                },
            },
        ]

        # Campaign generation data
        self.campaign_prompts = [
            {
                "element_type": "plot",
                "context": {
                    "campaign_theme": "epic fantasy",
                    "party_level": 5,
                    "party_size": 4,
                    "duration": "medium",
                },
            },
            {
                "element_type": "location",
                "context": {
                    "campaign_theme": "dark fantasy",
                    "party_level": 3,
                    "party_size": 5,
                    "duration": "short",
                },
            },
        ]

        # Image generation data
        self.image_prompts = [
            {
                "prompt": "Portrait of a noble human wizard",
                "model": {
                    "name": "stable-diffusion-v1-5",
                    "steps": 30,
                    "cfg_scale": 7.5,
                },
                "size": {"width": 512, "height": 512},
                "parameters": {
                    "style_preset": "fantasy art",
                    "negative_prompt": "poor quality, blurry",
                },
            },
            {
                "prompt": "Ancient magical library interior",
                "model": {
                    "name": "stable-diffusion-v1-5",
                    "steps": 30,
                    "cfg_scale": 7.5,
                },
                "size": {"width": 512, "height": 512},
                "parameters": {
                    "style_preset": "digital art",
                    "negative_prompt": "poor quality, blurry",
                },
            },
        ]

    @tag("text")
    @task(4)  # Higher weight for text generation
    def generate_character_content(self):
        """Test character content generation endpoint."""
        try:
            # Select random prompt
            prompt_data = random.choice(self.character_prompts)

            # Make request
            with self.client.post(
                "/api/v2/text/character",
                json={
                    "content_type": "backstory",
                    "request_id": str(uuid.uuid4()),
                    **prompt_data,
                },
                catch_response=True,
            ) as response:
                if response.status_code == 429:  # Rate limit
                    response.success()  # Don't count as error
                    raise StopUser()  # Stop this user
                elif response.status_code != 200:
                    response.failure(f"Failed with status {response.status_code}")
                else:
                    response.success()

        except Exception as e:
            if "429" in str(e):  # Rate limit
                raise StopUser()
            else:
                self.environment.runner.quit()
                raise

    @tag("text")
    @task(3)
    def generate_campaign_content(self):
        """Test campaign content generation endpoint."""
        try:
            # Select random prompt
            prompt_data = random.choice(self.campaign_prompts)

            # Make request
            with self.client.post(
                "/api/v2/text/campaign",
                json={
                    "request_id": str(uuid.uuid4()),
                    **prompt_data,
                },
                catch_response=True,
            ) as response:
                if response.status_code == 429:  # Rate limit
                    response.success()
                    raise StopUser()
                elif response.status_code != 200:
                    response.failure(f"Failed with status {response.status_code}")
                else:
                    response.success()

        except Exception as e:
            if "429" in str(e):
                raise StopUser()
            else:
                self.environment.runner.quit()
                raise

    @tag("image")
    @task(2)
    def generate_image(self):
        """Test image generation endpoint."""
        try:
            # Select random prompt
            prompt_data = random.choice(self.image_prompts)

            # Make request
            with self.client.post(
                "/api/v2/image/generate",
                json={
                    "request_id": str(uuid.uuid4()),
                    **prompt_data,
                },
                catch_response=True,
            ) as response:
                if response.status_code == 429:  # Rate limit
                    response.success()
                    raise StopUser()
                elif response.status_code != 200:
                    response.failure(f"Failed with status {response.status_code}")
                else:
                    response.success()

        except Exception as e:
            if "429" in str(e):
                raise StopUser()
            else:
                self.environment.runner.quit()
                raise

    @tag("validation")
    @task(2)
    def validate_content(self):
        """Test content validation endpoint."""
        try:
            # Create validation request
            validation_data = {
                "content": "Test content for validation",
                "content_type": "backstory",
                "parameters": {
                    "character_class": "Wizard",
                    "level": 5,
                    "theme": "epic fantasy",
                },
            }

            # Make request
            with self.client.post(
                "/api/v2/text/validate",
                json=validation_data,
                catch_response=True,
            ) as response:
                if response.status_code == 429:  # Rate limit
                    response.success()
                    raise StopUser()
                elif response.status_code != 200:
                    response.failure(f"Failed with status {response.status_code}")
                else:
                    response.success()

        except Exception as e:
            if "429" in str(e):
                raise StopUser()
            else:
                self.environment.runner.quit()
                raise


class LongRunningUser(LLMServiceUser):
    """User class for long-running workflow tests."""

    def get_character_id(self):
        """Get or create test character ID."""
        return str(uuid.uuid4())

    @tag("workflow")
    @task
    def character_creation_workflow(self):
        """Test complete character creation workflow."""
        try:
            character_id = self.get_character_id()

            # 1. Generate backstory
            with self.client.post(
                f"/api/v2/character/{character_id}/generate/backstory",
                json=self.character_prompts[0],
                catch_response=True,
            ) as response:
                if response.status_code == 429:
                    response.success()
                    raise StopUser()
                elif response.status_code != 200:
                    response.failure(f"Backstory generation failed: {response.status_code}")
                    return
                response.success()
                self.wait()

            # 2. Generate personality
            with self.client.post(
                f"/api/v2/character/{character_id}/generate/personality",
                json=self.character_prompts[0],
                catch_response=True,
            ) as response:
                if response.status_code == 429:
                    response.success()
                    raise StopUser()
                elif response.status_code != 200:
                    response.failure(f"Personality generation failed: {response.status_code}")
                    return
                response.success()
                self.wait()

            # 3. Generate portrait
            with self.client.post(
                f"/api/v2/character/{character_id}/generate/portrait",
                json=self.image_prompts[0],
                catch_response=True,
            ) as response:
                if response.status_code == 429:
                    response.success()
                    raise StopUser()
                elif response.status_code != 200:
                    response.failure(f"Portrait generation failed: {response.status_code}")
                    return
                response.success()
                self.wait()

            # 4. Validate generated content
            with self.client.post(
                f"/api/v2/character/{character_id}/validate",
                json={
                    "content_types": ["backstory", "personality"],
                    "theme": self.character_prompts[0]["theme"],
                },
                catch_response=True,
            ) as response:
                if response.status_code == 429:
                    response.success()
                    raise StopUser()
                elif response.status_code != 200:
                    response.failure(f"Content validation failed: {response.status_code}")
                    return
                response.success()

        except Exception as e:
            if "429" in str(e):
                raise StopUser()
            else:
                self.environment.runner.quit()
                raise
