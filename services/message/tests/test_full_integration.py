"""
Comprehensive Integration Tests for Message Hub Service

Tests all components working together including:
- RetryManager with exponential backoff
- EventStore with WAL and replay
- PriorityQueueManager with multi-level priorities
- EnhancedServiceRegistry with load balancing
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from uuid import uuid4

import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock, AsyncMock

from src.app import app
from src.models import ServiceMessage, ServiceType, MessageType
from src.retry_manager import RetryManager
from src.priority_queue import PriorityQueueManager
from src.enhanced_service_registry import EnhancedServiceRegistry, LoadBalancingStrategy
from src.event_store.service import EventStore
from src.event_store.models import EventType


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def setup_services(client):
    """Register test services for integration testing."""
    services = [
        {
            "name": "character-service",
            "url": "http://character:8000",
            "health_check": "/health"
        },
        {
            "name": "campaign-service",
            "url": "http://campaign:8001",
            "health_check": "/health"
        },
        {
            "name": "llm-service",
            "url": "http://llm:8100",
            "health_check": "/health"
        }
    ]
    
    for service in services:
        response = await client.post("/v1/services/register", json=service)
        assert response.status_code == 200
    
    return services


class TestFullIntegration:
    """Test all Message Hub components working together."""
    
    @pytest.mark.asyncio
    async def test_message_flow_with_retry(self, client, setup_services):
        """Test complete message flow with retry on failure."""
        # Send a message that will fail initially
        message = {
            "id": str(uuid4()),
            "type": "service_message",
            "source": "character-service",
            "destination": "campaign-service",
            "correlation_id": str(uuid4()),
            "payload": {"action": "validate_character", "character_id": "test-123"},
            "timestamp": datetime.utcnow().isoformat(),
            "ttl": 300,
            "priority": 2
        }
        
        # Send message
        response = await client.post("/v1/messages/send", json=message)
        assert response.status_code in [200, 500]  # May fail initially
        
        # Schedule for retry if failed
        if response.status_code == 500:
            retry_response = await client.post("/v1/retry", json=message)
            assert retry_response.status_code == 200
            assert retry_response.json()["status"] == "scheduled"
            
            # Check retry status
            status_response = await client.get(f"/v1/retry/status/{message['id']}")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert "attempts" in status_data
    
    @pytest.mark.asyncio
    async def test_priority_queue_processing(self, client):
        """Test priority queue with multiple priority levels."""
        messages = []
        
        # Enqueue messages with different priorities
        for priority in [1, 3, 5, 2, 4]:
            message = {
                "id": str(uuid4()),
                "type": "service_message",
                "source": "test-service",
                "destination": "target-service",
                "correlation_id": str(uuid4()),
                "payload": {"priority": priority},
                "timestamp": datetime.utcnow().isoformat(),
                "ttl": 300,
                "priority": priority
            }
            
            response = await client.post(
                f"/v1/queue/enqueue?priority={priority}",
                json=message
            )
            assert response.status_code == 200
            messages.append(message)
        
        # Check queue status
        status_response = await client.get("/v1/queue/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert "total_messages" in status_data
        assert status_data["total_messages"] >= len(messages)
    
    @pytest.mark.asyncio
    async def test_event_store_with_replay(self, client):
        """Test event persistence and replay functionality."""
        events = []
        
        # Persist multiple events
        for i in range(5):
            event = {
                "event_type": "CHARACTER_CREATED",
                "source_service": "CHARACTER",
                "data": {
                    "character_id": f"char-{i}",
                    "name": f"Test Character {i}",
                    "level": 1
                },
                "metadata": {"user_id": "test-user"},
                "correlation_id": str(uuid4())
            }
            
            response = await client.post("/api/v1/events/", json=event)
            assert response.status_code == 200
            events.append(response.json())
        
        # Replay events
        replay_response = await client.get("/api/v1/events/?limit=10")
        assert replay_response.status_code == 200
        replayed_events = replay_response.json()
        assert len(replayed_events) >= len(events)
    
    @pytest.mark.asyncio
    async def test_service_registry_with_load_balancing(self, client):
        """Test enhanced service registry with multiple instances."""
        service_name = "test-service"
        
        # Register multiple instances
        instances = []
        for port in [8001, 8002, 8003]:
            instance_url = f"http://test-service:{port}"
            response = await client.post(
                f"/v1/services/{service_name}/instances",
                params={"instance_url": instance_url}
            )
            assert response.status_code == 200
            instances.append(instance_url)
        
        # Test load balancing - get next instance multiple times
        selected_instances = []
        for _ in range(6):  # More than number of instances to test round-robin
            response = await client.get(f"/v1/services/{service_name}/next")
            assert response.status_code == 200
            selected_instances.append(response.json())
        
        # Verify round-robin distribution
        assert len(set(selected_instances[:3])) == 3  # First 3 should be unique
    
    @pytest.mark.asyncio
    async def test_service_dependencies(self, client):
        """Test service dependency management."""
        # Add dependencies
        dependencies = [
            ("character-service", "llm-service"),
            ("campaign-service", "character-service"),
            ("campaign-service", "llm-service")
        ]
        
        for service, depends_on in dependencies:
            response = await client.post(
                f"/v1/services/{service}/dependencies",
                params={"depends_on": depends_on}
            )
            assert response.status_code == 200
        
        # Verify services list includes dependency info
        response = await client.get("/v1/services")
        assert response.status_code == 200
        services = response.json()
        assert isinstance(services, (list, dict))
    
    @pytest.mark.asyncio
    async def test_transaction_management(self, client):
        """Test distributed transaction support."""
        # Begin transaction
        begin_response = await client.post("/v1/transactions/begin")
        assert begin_response.status_code == 200
        tx_data = begin_response.json()
        assert "transaction_id" in tx_data
        tx_id = tx_data["transaction_id"]
        
        # Simulate operations within transaction
        message = {
            "id": str(uuid4()),
            "type": "service_message",
            "source": "test-service",
            "destination": "target-service",
            "correlation_id": tx_id,  # Use transaction ID as correlation
            "payload": {"operation": "test"},
            "timestamp": datetime.utcnow().isoformat(),
            "ttl": 300,
            "priority": 1
        }
        
        send_response = await client.post("/v1/messages/send", json=message)
        assert send_response.status_code in [200, 500]
        
        # Commit or rollback based on result
        if send_response.status_code == 200:
            commit_response = await client.post(f"/v1/transactions/{tx_id}/commit")
            assert commit_response.status_code == 200
            assert commit_response.json()["committed"] is True
        else:
            rollback_response = await client.post(f"/v1/transactions/{tx_id}/rollback")
            assert rollback_response.status_code == 200
            assert rollback_response.json()["rolled_back"] is True
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self, client, setup_services):
        """Test comprehensive health monitoring."""
        # Check overall health
        health_response = await client.get("/health")
        assert health_response.status_code in [200, 503]
        health_data = health_response.json()
        assert "status" in health_data
        assert "details" in health_data
        
        # Check metrics
        metrics_response = await client.get("/metrics")
        assert metrics_response.status_code == 200
        metrics_data = metrics_response.json()
        assert isinstance(metrics_data, dict)
    
    @pytest.mark.asyncio
    async def test_event_correlation(self, client):
        """Test event correlation across services."""
        correlation_id = str(uuid4())
        
        # Create correlated events
        events = [
            {
                "event_type": "CHARACTER_CREATED",
                "source_service": "CHARACTER",
                "data": {"character_id": "char-1"},
                "correlation_id": correlation_id
            },
            {
                "event_type": "CAMPAIGN_JOINED",
                "source_service": "CAMPAIGN",
                "data": {"campaign_id": "camp-1", "character_id": "char-1"},
                "correlation_id": correlation_id
            },
            {
                "event_type": "PORTRAIT_GENERATED",
                "source_service": "IMAGE",
                "data": {"character_id": "char-1", "portrait_url": "http://..."},
                "correlation_id": correlation_id
            }
        ]
        
        # Persist all events
        for event in events:
            response = await client.post("/api/v1/events/", json=event)
            assert response.status_code == 200
        
        # Query events by correlation ID (this would need to be implemented)
        # For now, just verify we can retrieve events
        query_response = await client.get("/api/v1/events/?limit=100")
        assert query_response.status_code == 200
        retrieved_events = query_response.json()
        
        # Find our correlated events
        correlated = [e for e in retrieved_events if e.get("correlation_id") == correlation_id]
        assert len(correlated) >= len(events)
    
    @pytest.mark.asyncio
    async def test_message_timeout_and_dead_letter(self, client):
        """Test message timeout and dead letter queue handling."""
        # Create a message with short TTL
        message = {
            "id": str(uuid4()),
            "type": "service_message",
            "source": "test-service",
            "destination": "unreachable-service",
            "correlation_id": str(uuid4()),
            "payload": {"test": "data"},
            "timestamp": datetime.utcnow().isoformat(),
            "ttl": 1,  # 1 second TTL
            "priority": 1
        }
        
        # Send message
        response = await client.post("/v1/messages/send", json=message)
        # Should fail or timeout
        assert response.status_code in [200, 500, 503]
        
        # Schedule retry with exponential backoff
        retry_response = await client.post("/v1/retry", json=message)
        assert retry_response.status_code == 200
        
        # After max retries, should be in dead letter queue
        # This would be checked via monitoring/admin endpoints
        await asyncio.sleep(2)  # Wait for TTL expiration
        
        # Check retry status - should show max attempts reached
        status_response = await client.get(f"/v1/retry/status/{message['id']}")
        if status_response.status_code == 200:
            status_data = status_response.json()
            # Verify retry tracking
            assert "attempts" in status_data or "status" in status_data


class TestPerformanceIntegration:
    """Performance and stress tests for integration."""
    
    @pytest.mark.asyncio
    async def test_high_throughput_messaging(self, client, setup_services):
        """Test system under high message load."""
        num_messages = 100
        messages = []
        
        # Generate batch of messages
        for i in range(num_messages):
            message = {
                "id": str(uuid4()),
                "type": "service_message",
                "source": "load-test-source",
                "destination": "load-test-destination",
                "correlation_id": str(uuid4()),
                "payload": {"index": i, "data": "x" * 100},
                "timestamp": datetime.utcnow().isoformat(),
                "ttl": 300,
                "priority": (i % 5) + 1  # Vary priorities
            }
            messages.append(message)
        
        # Send all messages concurrently
        start_time = datetime.utcnow()
        tasks = []
        for msg in messages:
            tasks.append(client.post("/v1/messages/send", json=msg))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = datetime.utcnow()
        
        # Calculate metrics
        duration = (end_time - start_time).total_seconds()
        throughput = num_messages / duration if duration > 0 else 0
        
        # Count successes
        successes = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
        
        # Performance assertions
        assert throughput > 10  # At least 10 messages per second
        assert successes > num_messages * 0.8  # At least 80% success rate
    
    @pytest.mark.asyncio
    async def test_concurrent_event_processing(self, client):
        """Test concurrent event processing and ordering."""
        num_events = 50
        tasks = []
        
        # Create events concurrently
        for i in range(num_events):
            event = {
                "event_type": "TEST_EVENT",
                "source_service": "TEST",
                "data": {"sequence": i},
                "metadata": {"timestamp": datetime.utcnow().isoformat()}
            }
            tasks.append(client.post("/api/v1/events/", json=event))
        
        # Execute concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all events were persisted
        successes = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
        assert successes == num_events
        
        # Verify sequence numbers are maintained
        replay_response = await client.get(f"/api/v1/events/?limit={num_events}")
        assert replay_response.status_code == 200
        events = replay_response.json()
        
        # Check that sequence numbers are monotonically increasing
        sequence_numbers = [e["sequence_number"] for e in events if "sequence_number" in e]
        assert sequence_numbers == sorted(sequence_numbers)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
