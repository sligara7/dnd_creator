"""OpenAPI configuration utilities."""
import os
import yaml
from typing import Any, Dict
from fastapi.openapi.utils import get_openapi


def load_openapi_spec() -> Dict[str, Any]:
    """Load the OpenAPI specification from openapi.yaml."""
    spec_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "openapi.yaml"
    )
    with open(spec_path, 'r') as f:
        return yaml.safe_load(f)


def customize_openapi_docs(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Customize the OpenAPI specification for the docs UI."""
    # Update servers for development environment
    spec["servers"] = [
        {"url": "/api/v2", "description": "Current environment"}
    ]

    # Add authentication configuration for docs UI
    if "components" not in spec:
        spec["components"] = {}
    if "securitySchemes" not in spec["components"]:
        spec["components"]["securitySchemes"] = {}
    
    spec["components"]["securitySchemes"]["bearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": """
            Enter your JWT token in the format: Bearer <token>
            
            You can obtain a token from the auth service at /auth/token.
            """
    }

    # Add tags metadata for better organization
    spec["tags"] = [
        {
            "name": "Character",
            "description": "Core character management operations",
        },
        {
            "name": "Theme",
            "description": "Character theme and transition management",
        },
        {
            "name": "Version",
            "description": "Character version control and history",
        },
        {
            "name": "Bulk",
            "description": "Bulk character operations",
        },
        {
            "name": "Inventory",
            "description": "Character inventory and equipment management",
        },
        {
            "name": "Health",
            "description": "Service health and monitoring",
        },
    ]

    return spec


def configure_openapi(app: Any) -> None:
    """Configure OpenAPI documentation for the FastAPI application."""
    # Load and customize the spec
    spec = load_openapi_spec()
    spec = customize_openapi_docs(spec)

    # Override FastAPI's default OpenAPI schema
    def custom_openapi() -> Dict[str, Any]:
        """Return the custom OpenAPI schema."""
        if app.openapi_schema:
            return app.openapi_schema

        # OpenAPI schema will be loaded from our file
        app.openapi_schema = spec
        return app.openapi_schema

    # Set the custom schema
    app.openapi = custom_openapi
