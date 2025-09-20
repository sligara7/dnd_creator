"""Tests for Message Hub client."""

from unittest.mock import AsyncMock

import pytest

from image_service.integration.message_hub import MessageHubClient, EventMetadata


@pytest.fixture
def mock_aio_pika_connection(mocker):
    """Mock aio_pika connection."""
    mock = mocker.patch("aio_pika.connect_robust")
    mock.return_value = AsyncMock()
    return mock


@pytest.fixture
def mock_aio_pika_channel(mocker):
    """Mock aio_pika channel."""
    mock = AsyncMock()
    mock.declare_exchange = AsyncMock()
    mock.declare_queue = AsyncMock()
    return mock


@pytest.fixture
def mock_aio_pika_exchange(mocker):
    """Mock aio_pika exchange."""
    mock = AsyncMock()
    mock.publish = AsyncMock()
    return mock


@pytest.fixture
def mock_aio_pika_queue(mocker):
    """Mock aio_pika queue."""
    mock = AsyncMock()
    mock.bind = AsyncMock()
    mock.consume = AsyncMock()
    return mock


@pytest.fixture
async def message_hub(
    mock_aio_pika_connection,
    mock_aio_pika_channel,
    mock_aio_pika_exchange,
    mock_aio_pika_queue,
):
    """Create Message Hub client for testing."""
    mock_aio_pika_connection.return_value.channel = AsyncMock(
        return_value=mock_aio_pika_channel
    )
    mock_aio_pika_channel.declare_exchange.return_value = mock_aio_pika_exchange
    mock_aio_pika_channel.declare_queue.return_value = mock_aio_pika_queue

    client = MessageHubClient(
        url="amqp://localhost",
        exchange_name="test_exchange",
        queue_name="test_queue",
    )
    await client.connect()
    yield client
    await client.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_hub_connection(message_hub: MessageHubClient):
    """Test connecting to Message Hub."""
    assert message_hub.connection is not None
    assert message_hub.channel is not None
    assert message_hub.exchange is not None
    assert message_hub.queue is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_hub_publish(message_hub: MessageHubClient):
    """Test publishing a message."""
    test_data = {"key": "value"}
    await message_hub.publish(
        event_type="test.event",
        data=test_data,
        correlation_id="test-123",
        source_id="test-source",
    )

    # Verify message was published with correct properties
    assert message_hub.exchange.publish.called
    args = message_hub.exchange.publish.call_args
    message = args[0][0]
    assert message.content_type == "application/json"
    assert message.headers["event_type"] == "test.event"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_hub_subscribe(message_hub: MessageHubClient):
    """Test subscribing to events."""
    # Create mock handler
    mock_handler = AsyncMock()
    message_hub.subscribe("test.event", mock_handler)

    assert "test.event" in message_hub.handlers
    assert mock_handler in message_hub.handlers["test.event"]

    # Verify queue was bound to exchange
    assert message_hub.queue.bind.called
    args = message_hub.queue.bind.call_args
    assert args[0][0] == message_hub.exchange  # exchange
    assert args[1]["routing_key"] == "test.event"  # routing_key


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_hub_close(message_hub: MessageHubClient):
    """Test closing connection."""
    await message_hub.close()
    assert message_hub.connection.close.called