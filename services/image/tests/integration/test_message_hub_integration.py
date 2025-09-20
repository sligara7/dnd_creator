"""Integration tests for Message Hub interaction."""

import pytest
import asyncio
from uuid import uuid4

@pytest.mark.integration
@pytest.mark.asyncio
async def test_image_generation_events(
    message_hub_client,
    storage_client,
    test_image_data,
):
    """Test image generation event flow through Message Hub."""
    # Set up test data
    request_id = str(uuid4())
    image_data = test_image_data["portrait"]
    image_data["request_id"] = request_id

    # Subscribe to completion events
    completion_future = asyncio.Future()
    async def handle_completion(message):
        if message["request_id"] == request_id:
            completion_future.set_result(message)
    
    await message_hub_client.subscribe(
        "image.generation.completed",
        handle_completion,
    )

    # Publish generation request
    await message_hub_client.publish(
        "image.generation.requested",
        {
            "request_id": request_id,
            "type": "portrait",
            "data": image_data,
        },
    )

    # Wait for completion or timeout
    try:
        completion_message = await asyncio.wait_for(
            completion_future,
            timeout=30.0,
        )
        assert completion_message["status"] == "success"
        assert completion_message["request_id"] == request_id
        
        # Verify image was stored
        image_id = completion_message["image_id"]
        stored_image = await storage_client.get_image(image_id)
        assert stored_image is not None
    except asyncio.TimeoutError:
        pytest.fail("Generation request timed out")

@pytest.mark.integration
@pytest.mark.asyncio
async def test_theme_update_events(
    message_hub_client,
    theme_client,
    storage_client,
    test_theme_data,
    test_image_data,
):
    """Test theme update event propagation."""
    # Set up test theme and image
    theme_id = test_theme_data["id"]
    image_id = str(uuid4())
    image_data = {
        **test_image_data["portrait"],
        "id": image_id,
        "theme_id": theme_id,
    }
    
    await storage_client.store_image(image_id, image_data)
    
    # Set up event monitoring
    update_future = asyncio.Future()
    async def handle_update(message):
        if message["image_id"] == image_id:
            update_future.set_result(message)
    
    await message_hub_client.subscribe(
        "image.theme.updated",
        handle_update,
    )
    
    # Update theme
    updated_theme = {
        **test_theme_data,
        "style_attributes": {
            "lighting": "bright",
            "mood": "cheerful",
        },
    }
    await theme_client.update_theme(theme_id, updated_theme)
    
    # Wait for update notification
    try:
        update_message = await asyncio.wait_for(
            update_future,
            timeout=10.0,
        )
        assert update_message["theme_id"] == theme_id
        assert update_message["status"] == "updated"
        
        # Verify image was updated
        updated_image = await storage_client.get_image(image_id)
        assert updated_image["theme_id"] == theme_id
        assert "theme_updated_at" in updated_image
    except asyncio.TimeoutError:
        pytest.fail("Theme update event not received")

@pytest.mark.integration
@pytest.mark.asyncio
async def test_error_handling_events(
    message_hub_client,
    storage_client,
    test_image_data,
):
    """Test error handling and dead letter queue functionality."""
    # Set up test data with invalid parameters
    request_id = str(uuid4())
    invalid_data = {
        **test_image_data["portrait"],
        "style": {"invalid_param": "will_fail"},
    }

    # Monitor error events
    error_future = asyncio.Future()
    async def handle_error(message):
        if message["request_id"] == request_id:
            error_future.set_result(message)
    
    await message_hub_client.subscribe(
        "image.generation.failed",
        handle_error,
    )

    # Publish invalid request
    await message_hub_client.publish(
        "image.generation.requested",
        {
            "request_id": request_id,
            "type": "portrait",
            "data": invalid_data,
        },
    )

    # Wait for error event
    try:
        error_message = await asyncio.wait_for(
            error_future,
            timeout=10.0,
        )
        assert error_message["request_id"] == request_id
        assert error_message["status"] == "error"
        assert "error_details" in error_message
    except asyncio.TimeoutError:
        pytest.fail("Error event not received")

    # Verify message in dead letter queue
    dlq_message = await message_hub_client.get_from_dlq(
        "image.generation.requested",
        request_id,
    )
    assert dlq_message is not None
    assert dlq_message["request_id"] == request_id