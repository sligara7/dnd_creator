"""Integration tests for Message Hub communication."""

import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any

import pytest
from cache_service.integrations.message_hub import CacheServiceIntegration
from tests.utils import (
    generate_test_key,
    generate_test_value,
    build_test_event,
    wait_for_condition
)

@pytest.mark.integration
class TestMessageHubIntegration:
    """Test Message Hub integration."""

    @pytest.fixture
    async def integration(self, message_hub_client, mock_config):
        """Create CacheServiceIntegration instance with real Message Hub."""
        integration = CacheServiceIntegration(mock_config)
        integration.message_hub = message_hub_client
        await integration.start()
        yield integration
        await integration.stop()

    @pytest.fixture
    async def test_subscriber(self, message_hub_client):
        """Create a test subscriber to verify events."""
        received_events = []

        async def handle_event(event_data: str):
            event = json.loads(event_data)
            received_events.append(event)

        await message_hub_client.subscribe(
            ["cache.*"],
            handle_event
        )
        yield received_events

    async def test_service_registration(self, integration, test_subscriber):
        """Test service registration with Message Hub."""
        # Act
        await integration.register_service()

        # Assert
        # Wait for registration event
        def check_registration():
            return any(
                event["type"] == "service.register"
                for event in test_subscriber
            )

        assert await wait_for_condition(check_registration)

        # Verify registration data
        registration = next(
            event for event in test_subscriber
            if event["type"] == "service.register"
        )
        assert registration["payload"]["service_name"] == "cache-service"
        assert "capabilities" in registration["payload"]
        assert "health_check_endpoint" in registration["payload"]

    async def test_cache_operation_events(self, integration, test_subscriber):
        """Test publishing cache operation events."""
        # Arrange
        operations = [
            ("set", "test:key1", "test-service"),
            ("delete", "test:*", "test-service"),
            ("clear", "test-service:*", "test-service")
        ]

        # Act
        for operation, pattern, service in operations:
            await integration.notify_cache_operation(
                operation=operation,
                key_pattern=pattern,
                service=service
            )

        # Assert
        # Wait for all events
        def check_events():
            return len(test_subscriber) == len(operations)

        assert await wait_for_condition(check_events)

        # Verify each event
        for i, (operation, pattern, service) in enumerate(operations):
            event = test_subscriber[i]
            assert event["type"] == f"cache.{operation}"
            assert event["payload"]["key_pattern"] == pattern
            assert event["payload"]["service"] == service

    async def test_handle_invalidation_request(self, integration, test_subscriber):
        """Test handling cache invalidation requests."""
        # Arrange
        invalidation_request = build_test_event(
            "cache.invalidate",
            {
                "pattern": "test:*",
                "service": "test-service"
            }
        )

        # Act
        await integration.handle_cache_operation(
            json.dumps(invalidation_request)
        )

        # Assert
        # Wait for invalidation response
        def check_invalidation():
            return any(
                event["type"] == "cache.invalidated"
                for event in test_subscriber
            )

        assert await wait_for_condition(check_invalidation)

        # Verify response
        response = next(
            event for event in test_subscriber
            if event["type"] == "cache.invalidated"
        )
        assert response["payload"]["pattern"] == "test:*"
        assert response["payload"]["service"] == "test-service"

    async def test_health_reporting(self, integration, test_subscriber):
        """Test periodic health status reporting."""
        # Act
        await integration.start_health_reporting()

        # Assert
        # Wait for health status event
        def check_health():
            return any(
                event["type"] == "service.health_status"
                for event in test_subscriber
            )

        assert await wait_for_condition(check_health)

        # Verify health status
        status = next(
            event for event in test_subscriber
            if event["type"] == "service.health_status"
        )
        assert status["payload"]["service_name"] == "cache-service"
        assert "stats" in status["payload"]
        assert "timestamp" in status["payload"]

    async def test_concurrent_events(self, integration, test_subscriber):
        """Test handling concurrent events."""
        # Arrange
        num_events = 10
        events = [
            build_test_event(
                "cache.invalidate",
                {
                    "pattern": f"test{i}:*",
                    "service": "test-service"
                }
            )
            for i in range(num_events)
        ]

        # Act
        await asyncio.gather(*(
            integration.handle_cache_operation(json.dumps(event))
            for event in events
        ))

        # Assert
        # Wait for all responses
        def check_responses():
            return len([
                e for e in test_subscriber
                if e["type"] == "cache.invalidated"
            ]) == num_events

        assert await wait_for_condition(check_responses)

        # Verify all responses
        responses = [
            e for e in test_subscriber
            if e["type"] == "cache.invalidated"
        ]
        assert len(responses) == num_events
        patterns = set(r["payload"]["pattern"] for r in responses)
        assert len(patterns) == num_events

    @pytest.mark.parametrize("event_type,payload", [
        (
            "cache.clear",
            {"service": "test-service"}
        ),
        (
            "cache.preload",
            {
                "items": [
                    {"key": "test:1", "value": "test1"},
                    {"key": "test:2", "value": "test2"}
                ],
                "service": "test-service"
            }
        ),
        (
            "cache.status_request",
            {
                "request_id": "test-request",
                "service": "test-service"
            }
        )
    ])
    async def test_event_handling(
        self,
        integration,
        test_subscriber,
        event_type,
        payload
    ):
        """Test handling different event types."""
        # Arrange
        event = build_test_event(event_type, payload)

        # Act
        await integration.handle_cache_operation(json.dumps(event))

        # Assert
        # Wait for response event
        response_type = {
            "cache.clear": "cache.cleared",
            "cache.preload": "cache.preloaded",
            "cache.status_request": "cache.status_response"
        }[event_type]

        def check_response():
            return any(
                e["type"] == response_type
                for e in test_subscriber
            )

        assert await wait_for_condition(check_response)

        # Verify response
        response = next(
            e for e in test_subscriber
            if e["type"] == response_type
        )
        assert response["payload"]["service"] == payload["service"]

        if event_type == "cache.preload":
            assert response["payload"]["count"] == len(payload["items"])
        elif event_type == "cache.status_request":
            assert response["payload"]["request_id"] == payload["request_id"]
            assert "stats" in response["payload"]

    async def test_reconnection(self, integration, test_subscriber):
        """Test reconnection behavior."""
        # Arrange
        # Force disconnect
        await integration.message_hub.close()

        # Act
        # Try an operation that should trigger reconnect
        await integration.notify_cache_operation(
            operation="set",
            key_pattern="test:*",
            service="test-service"
        )

        # Assert
        # Wait for event to be received
        def check_event():
            return any(
                event["type"] == "cache.set"
                for event in test_subscriber
            )

        assert await wait_for_condition(check_event)

    async def test_error_recovery(self, integration, test_subscriber):
        """Test error recovery in event handling."""
        # Arrange
        # Invalid event that should be handled gracefully
        invalid_event = "{"  # Invalid JSON

        # Act
        # This should not raise but log an error
        await integration.handle_cache_operation(invalid_event)

        # Valid event after error
        valid_event = build_test_event(
            "cache.clear",
            {"service": "test-service"}
        )
        await integration.handle_cache_operation(json.dumps(valid_event))

        # Assert
        # Should still handle valid events after error
        def check_response():
            return any(
                event["type"] == "cache.cleared"
                for event in test_subscriber
            )

        assert await wait_for_condition(check_response)