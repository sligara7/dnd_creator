"""Constants for the image service."""

# Image types
IMAGE_TYPE_MAP = "map"
IMAGE_TYPE_PORTRAIT = "portrait"
IMAGE_TYPE_ITEM = "item"

# Map subtypes
MAP_SUBTYPE_TACTICAL = "tactical"
MAP_SUBTYPE_CAMPAIGN = "campaign"

# Portrait subtypes
PORTRAIT_SUBTYPE_CHARACTER = "character"
PORTRAIT_SUBTYPE_NPC = "npc"
PORTRAIT_SUBTYPE_MONSTER = "monster"

# Item subtypes
ITEM_SUBTYPE_WEAPON = "weapon"
ITEM_SUBTYPE_ARMOR = "armor"
ITEM_SUBTYPE_OTHER = "other"

# Overlay types
OVERLAY_TYPE_POSITION = "position"
OVERLAY_TYPE_RANGE = "range"
OVERLAY_TYPE_EFFECT = "effect"
OVERLAY_TYPE_PARTY = "party"
OVERLAY_TYPE_TERRITORY = "territory"
OVERLAY_TYPE_ROUTE = "route"

# Visual themes
THEME_FANTASY = "fantasy"
THEME_WESTERN = "western"
THEME_CYBERPUNK = "cyberpunk"
THEME_STEAMPUNK = "steampunk"
THEME_HORROR = "horror"
THEME_SPACE_FANTASY = "space_fantasy"

# Generation parameters
MIN_IMAGE_SIZE = 32
MAX_IMAGE_SIZE = 4096
DEFAULT_IMAGE_SIZE = 1024

# Style categories
STYLE_CATEGORY_ARCHITECTURE = "architecture"
STYLE_CATEGORY_CLOTHING = "clothing"
STYLE_CATEGORY_TECHNOLOGY = "technology"
STYLE_CATEGORY_ENVIRONMENT = "environment"

# Cache configuration
CACHE_KEY_THEME = "theme"
CACHE_KEY_STYLE = "style"
CACHE_KEY_IMAGE = "image"
CACHE_KEY_OVERLAY = "overlay"

# Queue priorities
QUEUE_PRIORITY_HIGH = 100
QUEUE_PRIORITY_NORMAL = 50
QUEUE_PRIORITY_LOW = 10

# Database schemas
DB_SCHEMA_IMAGE = "image"
DB_SCHEMA_THEME = "theme"
DB_SCHEMA_OVERLAY = "overlay"
DB_SCHEMA_QUEUE = "queue"

# Event types
EVENT_IMAGE_GENERATED = "image_generated"
EVENT_OVERLAY_UPDATED = "overlay_updated"
EVENT_THEME_APPLIED = "theme_applied"
EVENT_CHARACTER_UPDATED = "character_updated"
EVENT_CAMPAIGN_THEME_CHANGED = "campaign_theme_changed"
EVENT_MAP_STATE_CHANGED = "map_state_changed"

# API paths
PATH_MAPS = "/maps"
PATH_PORTRAITS = "/portraits"
PATH_ITEMS = "/items"
PATH_THEMES = "/themes"
PATH_OVERLAYS = "/overlays"

# Service health status
STATUS_HEALTHY = "healthy"
STATUS_DEGRADED = "degraded"
STATUS_UNHEALTHY = "unhealthy"

# Dependencies
DEPENDENCY_MESSAGE_HUB = "message_hub"
DEPENDENCY_GETIMG_API = "getimg_api"
DEPENDENCY_STORAGE = "storage"
DEPENDENCY_CACHE = "cache"

# Common error codes
ERROR_IMAGE_NOT_FOUND = "IMAGE_NOT_FOUND"
ERROR_INVALID_THEME = "INVALID_THEME"
ERROR_GENERATION_FAILED = "GENERATION_ERROR"
ERROR_OVERLAY_FAILED = "OVERLAY_ERROR"
ERROR_STORAGE_ERROR = "STORAGE_ERROR"
ERROR_API_ERROR = "API_ERROR"
ERROR_THEME_ERROR = "THEME_ERROR"
ERROR_PERMISSION_DENIED = "PERMISSION_DENIED"

# Image formats
FORMAT_JPEG = "image/jpeg"
FORMAT_PNG = "image/png"
FORMAT_WEBP = "image/webp"
FORMAT_SVG = "image/svg+xml"
FORMAT_GIF = "image/gif"

# Grid configuration
DEFAULT_GRID_SIZE = 64  # pixels
DEFAULT_GRID_COLOR = "#000000"
DEFAULT_GRID_OPACITY = 0.2

# Batch processing
DEFAULT_BATCH_SIZE = 5
MAX_BATCH_SIZE = 20
MIN_BATCH_SIZE = 1
