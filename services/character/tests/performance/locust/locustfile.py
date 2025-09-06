"""Load testing with Locust."""
import json
import os
from typing import Dict, Any
from locust import FastHttpUser, task, between
from locust.contrib.fasthttp import ResponseContextManager


class CharacterUser(FastHttpUser):
    """User class for character service load testing."""

    # Wait between 1-2.5 seconds between tasks
    wait_time = between(1, 2.5)

    def on_start(self) -> None:
        """Initialize user context before testing."""
        # Create a test character for operations
        payload = {
            "name": "Load Test Character",
            "theme": "traditional",
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "campaign_id": "123e4567-e89b-12d3-a456-426614174111",
            "character_data": {
                "race": "Human",
                "class": "Fighter",
                "level": 1,
                "ability_scores": {
                    "strength": 15,
                    "dexterity": 14,
                    "constitution": 13,
                    "intelligence": 12,
                    "wisdom": 10,
                    "charisma": 8
                }
            }
        }
        response = self.client.post(
            "/api/v2/characters",
            json=payload,
            headers={"Authorization": "Bearer test-token"}
        )
        if response.status_code == 200:
            self.character_id = response.json()["id"]
        else:
            self.character_id = None

    @task(10)  # High priority task - health check
    def health_check(self) -> None:
        """Test the health check endpoint."""
        with self.client.get(
            "/health",
            catch_response=True,
            name="/health"
        ) as response:
            validate_health_response(response)

    @task(5)  # Medium priority - get character sheet
    def get_character_sheet(self) -> None:
        """Test character sheet retrieval."""
        if not self.character_id:
            return

        with self.client.get(
            f"/api/v2/characters/{self.character_id}",
            headers={"Authorization": "Bearer test-token"},
            catch_response=True,
            name="/api/v2/characters/{id}"
        ) as response:
            validate_character_response(response)


def validate_health_response(response: ResponseContextManager) -> None:
    """Validate health check response."""
    try:
        if response.status_code != 200:
            response.failure(f"Health check failed: {response.status_code}")
            return

        data = response.json()
        if data.get("status") != "healthy":
            response.failure(f"Unexpected health status: {data.get('status')}")
            return

        response.success()
    except json.JSONDecodeError:
        response.failure("Invalid JSON response")
    except Exception as e:
        response.failure(f"Validation error: {str(e)}")


def validate_character_response(response: ResponseContextManager) -> None:
    """Validate character response."""
    try:
        if response.status_code != 200:
            response.failure(f"Character request failed: {response.status_code}")
            return

        data = response.json()
        required_fields = ["id", "name", "theme", "character_data"]
        missing = [field for field in required_fields if field not in data]
        if missing:
            response.failure(f"Missing fields in response: {missing}")
            return

        response.success()
    except json.JSONDecodeError:
        response.failure("Invalid JSON response")
    except Exception as e:
        response.failure(f"Validation error: {str(e)}")
