"""Tests for image API endpoints."""

import io
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image as PILImage

from image_service.api.routers.images import router
from image_service.domain.models import Image, ImageType, ImageSubtype
from image_service.integration.storage_service import StorageServiceClient


@pytest.fixture
def app(mocker) -> FastAPI:
    """Create FastAPI test application."""
    app = FastAPI()
    app.include_router(router)

    # Mock storage client
    storage = mocker.Mock(spec=StorageServiceClient)
    app.state.storage = storage

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_image() -> bytes:
    """Create test image file."""
    img = PILImage.new('RGB', (60, 30), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def test_upload_image(client: TestClient, app: FastAPI, test_image: bytes):
    """Test uploading an image."""
    # Mock storage service response
    mock_image = Image(
        id=UUID("00000000-0000-0000-0000-000000000000"),
        type=ImageType.PORTRAIT,
        subtype=ImageSubtype.CHARACTER,
        content={"url": "https://example.com/test.png", "format": "png", "size": {"width": 512, "height": 512}},
        metadata={"theme": "fantasy", "source_id": None, "service": "image_service", "generation_params": {}, 
                 "created_at": "2025-09-20T12:00:00", "updated_at": "2025-09-20T12:00:00"}
    )
    app.state.storage.create_image.return_value = mock_image

    # Make request
    files = {"image": ("test.png", test_image, "image/png")}
    data = {
        "type": "portrait",
        "subtype": "character",
        "name": "Test Portrait",
        "theme": "fantasy",
    }
    response = client.post("/api/v2/images/", files=files, data=data)
    
    assert response.status_code == 200
    assert response.json()["type"] == "portrait"
    assert response.json()["metadata"]["theme"] == "fantasy"


def test_get_image(client: TestClient, app: FastAPI):
    """Test getting an image by ID."""
    # Mock storage service response
    mock_image = Image(
        id=UUID("00000000-0000-0000-0000-000000000000"),
        type=ImageType.PORTRAIT,
        subtype=ImageSubtype.CHARACTER,
        content={"url": "https://example.com/test.png", "format": "png", "size": {"width": 512, "height": 512}},
        metadata={"theme": "fantasy", "source_id": None, "service": "image_service", "generation_params": {}, 
                 "created_at": "2025-09-20T12:00:00", "updated_at": "2025-09-20T12:00:00"}
    )
    app.state.storage.get_image.return_value = mock_image

    # Make request
    response = client.get("/api/v2/images/00000000-0000-0000-0000-000000000000")
    
    assert response.status_code == 200
    assert response.json()["type"] == "portrait"
    assert response.json()["metadata"]["theme"] == "fantasy"


def test_list_images(client: TestClient, app: FastAPI):
    """Test listing images."""
    # Mock storage service response
    mock_images = [
        Image(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            type=ImageType.PORTRAIT,
            subtype=ImageSubtype.CHARACTER,
            content={"url": "https://example.com/test1.png", "format": "png", "size": {"width": 512, "height": 512}},
            metadata={"theme": "fantasy", "source_id": None, "service": "image_service", "generation_params": {}, 
                     "created_at": "2025-09-20T12:00:00", "updated_at": "2025-09-20T12:00:00"}
        ),
        Image(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            type=ImageType.PORTRAIT,
            subtype=ImageSubtype.CHARACTER,
            content={"url": "https://example.com/test2.png", "format": "png", "size": {"width": 512, "height": 512}},
            metadata={"theme": "fantasy", "source_id": None, "service": "image_service", "generation_params": {}, 
                     "created_at": "2025-09-20T12:00:00", "updated_at": "2025-09-20T12:00:00"}
        ),
    ]
    app.state.storage.list_images.return_value = mock_images

    # Make request
    response = client.get("/api/v2/images/?type=portrait&theme=fantasy")
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(img["type"] == "portrait" for img in response.json())
    assert all(img["metadata"]["theme"] == "fantasy" for img in response.json())


def test_delete_image(client: TestClient, app: FastAPI):
    """Test deleting an image."""
    # Mock storage service
    app.state.storage.delete_image.return_value = None

    # Make request
    response = client.delete("/api/v2/images/00000000-0000-0000-0000-000000000000")
    
    assert response.status_code == 200
    app.state.storage.delete_image.assert_called_once_with(
        UUID("00000000-0000-0000-0000-000000000000")
    )