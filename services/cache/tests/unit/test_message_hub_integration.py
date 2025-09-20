"""Unit tests for Message Hub integration."""

import json
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone

import pytest
from cache_service.integrations.message_hub import CacheServiceIntegration
from tests.utils import build_test_event, generate_test_key

@pytest.mark.unit
class TestMessageHubIntegration:
    """Test Message Hub integration."""

    @pytest.fixture
    async def integration(self, mock_config):
        """Create CacheServiceIntegration instance."""
        with patch("cache_service.integrations.message_hub.MessageHubClient") as mock_client:
            instance = mock_client.return_value
            instance.connect = AsyncMock()
            instance.close = AsyncMock()
            instance.publish_event = AsyncMock()
            instance.subscribe = AsyncMock()
            
            integration = CacheServiceIntegration(mock_config)
            integration.message_hub = instance
            yield integration

    async def test_start_and_stop(self, integration):
        """Test starting and stopping the integration."""
        # Act
        await integration.start()

        # Assert
        integration.message_hub.connect.assert_awaited_once()
        integration.message_hub.subscribe.assert_awaited_once()
        
        # Act
        await integration.stop()
        
        # Assert
        integration.message_hub.close.assert_awaited_once()

    async def test_service_registration(self, integration):
        """Test service registration with Message Hub."""
        # Act
        await integration.register_service()

        # Assert
        integration.message_hub.publish_event.assert_awaited_once_with(
            "service.register",
            {
                "service_name": "cache-service",
                "service_type": "cache",
                "capabilities": [
                    "distributed_cache",
                    "local_cache",
                    "pattern_matching",
                    "statistics"
                ],
                "health_check_endpoint": "/health",
                "version": "1.0.0"
            }
        )

    async def test_health_status_reporting(self, integration):
        """Test health status reporting."""
        # Arrange
        with patch("asyncio.create_task") as mock_create_task:
            # Act
            await integration.start_health_reporting()
            
            # Assert
            mock_create_task.assert_called_once()

    async def test_cache_operation_event(self, integration):
        """Test publishing cache operation events."""
        # Arrange
        operation = "set"
        key_pattern = "test:*"
        service = "test-service"

        # Act
        await integration.notify_cache_operation(
            operation=operation,
            key_pattern=key_pattern,
            service=service
        )

        # Assert
        integration.message_hub.publish_event.assert_awaited_once()
        args = integration.message_hub.publish_event.call_args
        assert args[0][0] == f"cache.{operation}"
        event_data = args[0][1]
        assert event_data["operation"] == operation
        assert event_data["key_pattern"] == key_pattern
        assert event_data["service"] == service

    @pytest.mark.parametrize("event_type,payload", [
        (
            "cache.invalidate",
            {"pattern": "test:*", "service": "test-service"}
        ),
        (
            "cache.clear",
            {"service": "test-service"}
        ),
        (
            "cache.preload",
            {"items": [{"key": "test:1", "value": "test"}], "service": "test-service"}
        ),
        (
            "cache.status_request",
            {"request_id": "123", "service": "test-service"}
        )
    ])
    async def test_handle_cache_operation(
        self,
        integration,
        event_type,
        payload
    ):
        """Test handling various cache operations."""
        # Arrange
        event = build_test_event(event_type, payload)
        event_json = json.dumps(event)

        # Act
        await integration.handle_cache_operation(event_json)

        # Assert
        # Verify appropriate response event was published
        integration.message_hub.publish_event.assert_awaited_once()
        args = integration.message_hub.publish_event.call_args
        response_type = args[0][0]
        response_data = args[0][1]

        if event_type == "cache.invalidate":
            assert response_type == "cache.invalidated"
            assert response_data["pattern"] == payload["pattern"]
        elif event_type == "cache.clear":
            assert response_type == "cache.cleared"
            assert response_data["service"] == payload["service"]
        elif event_type == "cache.preload":
            assert response_type == "cache.preloaded"
            assert response_data["count"] == len(payload["items"])
        elif event_type == "cache.status_request":
            assert response_type == "cache.status_response"
            assert response_data["request_id"] == payload["request_id"]
            assert "stats" in response_data

    async def test_setup_subscriptions(self, integration):
        """Test setting up event subscriptions."""
        # Arrange
        expected_events = [
            "cache.invalidate",
            "cache.clear",
            "cache.preload",
            "cache.status_request"
        ]

        # Act
        await integration.setup_subscriptions()

        # Assert
        integration.message_hub.subscribe.assert_awaited_once_with(
            expected_events,
            integration.handle_cache_operation
        )
        assert all(event in integration.subscribed_events for event in expected_events)

    async def test_error_handling(self, integration):
        """Test error handling in event processing."""
        # Arrange
        invalid_json = "{"  # Invalid JSON
        
        # Act/Assert
        await integration.handle_cache_operation(invalid_json)  # Should not raise
        integration.message_hub.publish_event.assert_not_awaited()

    async def test_unknown_event_type(self, integration):
        """Test handling unknown event type."""
        # Arrange
        event = build_test_event(
            "cache.unknown",
            {"data": "test"}
        )
        event_json = json.dumps(event)

        # Act
        await integration.handle_cache_operation(event_json)

        # Assert
        integration.message_hub.publish_event.assert_not_awaited()

    @pytest.mark.parametrize("error", [
        Exception("Generic error"),
        ConnectionError("Connection error"),
        TimeoutError("Timeout error")
    ])
    async def test_message_hub_error_handling(self, integration, error):
        """Test handling Message Hub errors."""
        # Arrange
        integration.message_hub.publish_event.side_effect = error

        # Act/Assert
        # Should not raise but log error
        await integration.notify_cache_operation("set", "test:*", "test-service")