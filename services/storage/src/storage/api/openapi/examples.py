"""OpenAPI examples for asset management endpoints."""

from uuid import uuid4
from datetime import datetime, timezone

# Example responses
ASSET_RESPONSE_EXAMPLE = {
    "id": str(uuid4()),
    "name": "character_portrait.png",
    "service": "character_service",
    "owner_id": str(uuid4()),
    "asset_type": "IMAGE",
    "s3_key": "character_service/owner_id/20240920/abc123_character_portrait.png",
    "s3_url": "https://storage.dndcreator.com/assets/character_portrait.png",
    "size": 1024567,
    "content_type": "image/png",
    "checksum": "sha256:abc123def456...",
    "current_version": 1,
    "tags": ["portrait", "character", "dwarf"],
    "metadata": {
        "character_id": "123",
        "campaign_id": "456",
        "resolution": "1024x1024"
    },
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "is_deleted": False,
    "deleted_at": None
}

PRESIGNED_URL_EXAMPLE = {
    "url": "https://storage.dndcreator.com/assets/presigned/abc123...",
    "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
}

STORAGE_STATS_EXAMPLE = {
    "total_assets": 1250,
    "total_size": 1073741824,  # 1GB
    "asset_types": {
        "IMAGE": 800,
        "DOCUMENT": 300,
        "AUDIO": 100,
        "VIDEO": 50
    },
    "service_stats": {
        "character_service": {
            "total_assets": 800,
            "total_size": 536870912  # 512MB
        },
        "campaign_service": {
            "total_assets": 450,
            "total_size": 536870912  # 512MB
        }
    }
}

ASSET_LIST_EXAMPLE = {
    "items": [ASSET_RESPONSE_EXAMPLE],
    "total": 1,
    "limit": 100,
    "offset": 0
}

# Example requests
UPLOAD_REQUEST_EXAMPLE = {
    "filename": "character_portrait.png",
    "content_type": "image/png",
    "service": "character_service",
    "owner_id": str(uuid4()),
    "metadata": {
        "character_id": "123",
        "campaign_id": "456",
        "resolution": "1024x1024"
    },
    "tags": ["portrait", "character", "dwarf"],
    "asset_type": "IMAGE"
}

BULK_UPLOAD_REQUEST_EXAMPLE = {
    "files": [
        {
            "filename": "character_portrait.png",
            "content_type": "image/png",
            "metadata": {
                "character_id": "123"
            }
        },
        {
            "filename": "character_map.jpg",
            "content_type": "image/jpeg",
            "metadata": {
                "campaign_id": "456"
            }
        }
    ],
    "service": "character_service",
    "owner_id": str(uuid4()),
    "metadata": {
        "batch_id": "789"
    },
    "tags": ["portrait", "map"]
}

UPDATE_REQUEST_EXAMPLE = {
    "metadata": {
        "character_id": "789",
        "updated_by": str(uuid4())
    },
    "tags": ["portrait", "character", "elf"],
    "created_by": str(uuid4())
}

# Error examples
ERROR_EXAMPLES = {
    "not_found": {
        "summary": "Asset not found",
        "value": {
            "message": "Asset abc123 not found",
            "details": {"asset_id": "abc123"}
        }
    },
    "validation_error": {
        "summary": "Validation error",
        "value": {
            "message": "Invalid request data",
            "details": {
                "errors": {
                    "filename": "Missing required field"
                }
            }
        }
    },
    "storage_error": {
        "summary": "Storage operation failed",
        "value": {
            "message": "Storage operation 'upload' failed: Connection timeout",
            "details": {
                "operation": "upload",
                "error": "Connection timeout"
            }
        }
    },
    "quota_exceeded": {
        "summary": "Storage quota exceeded",
        "value": {
            "message": "Storage quota exceeded",
            "details": {
                "service": "character_service",
                "current_usage": 1073741824,
                "limit": 1073741824
            }
        }
    }
}

# Example model documentation
MODELS = {
    "AssetResponse": {
        "description": "Detailed asset information",
        "example": ASSET_RESPONSE_EXAMPLE
    },
    "AssetListResponse": {
        "description": "Paginated list of assets",
        "example": ASSET_LIST_EXAMPLE
    },
    "UploadRequest": {
        "description": "Request body for asset upload",
        "example": UPLOAD_REQUEST_EXAMPLE
    },
    "BulkUploadRequest": {
        "description": "Request body for bulk asset upload",
        "example": BULK_UPLOAD_REQUEST_EXAMPLE
    },
    "UpdateAssetRequest": {
        "description": "Request body for asset update",
        "example": UPDATE_REQUEST_EXAMPLE
    },
    "PresignedUrlResponse": {
        "description": "Presigned URL for direct asset access",
        "example": PRESIGNED_URL_EXAMPLE
    },
    "StorageStatsResponse": {
        "description": "Storage service statistics",
        "example": STORAGE_STATS_EXAMPLE
    }
}