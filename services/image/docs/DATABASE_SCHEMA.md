# Image Service Database Schema

## Base Model

All models inherit from `BaseModel` which provides:

- `id`: UUID primary key
- `created_at`: Timestamp with timezone
- `updated_at`: Timestamp with timezone
- `deleted_at`: Nullable timestamp with timezone
- `is_deleted`: Boolean flag for soft delete

## Models

### Image
Core image storage model.

```sql
CREATE TABLE images (
    -- Inherited fields from BaseModel
    id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Basic information
    type VARCHAR(50) NOT NULL,
    subtype VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Image data
    url VARCHAR(1024) NOT NULL,
    format VARCHAR(50) NOT NULL DEFAULT 'png',
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    size INTEGER NOT NULL,
    
    -- Theme and style
    theme VARCHAR(50) NOT NULL,
    style_data JSONB,
    
    -- Generation metadata
    generation_params JSONB,
    source_id UUID,
    source_type VARCHAR(50)
);
```

### ImageOverlay
Overlay information for images.

```sql
CREATE TABLE image_overlays (
    -- Inherited fields from BaseModel
    id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Basic information
    image_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Overlay data
    data JSONB NOT NULL,
    style JSONB NOT NULL,
    
    FOREIGN KEY (image_id) REFERENCES images(id),
    INDEX (image_id)
);
```

### MapGrid
Grid configuration for map images.

```sql
CREATE TABLE map_grids (
    -- Inherited fields from BaseModel
    id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Configuration
    image_id UUID NOT NULL UNIQUE,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    size INTEGER NOT NULL DEFAULT 50,
    color VARCHAR(50) NOT NULL DEFAULT '#000000',
    opacity FLOAT NOT NULL DEFAULT 0.5,
    
    FOREIGN KEY (image_id) REFERENCES images(id),
    INDEX (image_id)
);
```

### GenerationTask
Tracks image generation tasks and their status.

```sql
CREATE TABLE generation_tasks (
    -- Inherited fields from BaseModel
    id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Task information
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    priority INTEGER NOT NULL,
    
    -- Task data
    params JSONB NOT NULL,
    result JSONB,
    
    -- Error tracking
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    last_attempt TIMESTAMP WITH TIME ZONE,
    
    -- Retry configuration
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    retry_delay INTEGER NOT NULL DEFAULT 5
);
```

### Theme
Theme configuration for image generation.

```sql
CREATE TABLE themes (
    -- Inherited fields from BaseModel
    id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Basic information
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Theme configuration
    config JSONB NOT NULL,
    variables JSONB NOT NULL,
    prompts JSONB NOT NULL,
    styles JSONB NOT NULL
);
```

### ThemeVariation
Variations of base themes.

```sql
CREATE TABLE theme_variations (
    -- Inherited fields from BaseModel
    id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Basic information
    theme_id UUID NOT NULL,
    name VARCHAR(50) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Configuration
    config_override JSONB NOT NULL,
    variable_override JSONB NOT NULL,
    
    FOREIGN KEY (theme_id) REFERENCES themes(id),
    INDEX (theme_id)
);
```

### StylePreset
Reusable style configurations.

```sql
CREATE TABLE style_presets (
    -- Inherited fields from BaseModel
    id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Basic information
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    
    -- Configuration
    config JSONB NOT NULL,
    prompts JSONB NOT NULL,
    compatibility JSONB NOT NULL
);
```

### ThemeElement
Theme elements (e.g., architecture, clothing, technology).

```sql
CREATE TABLE theme_elements (
    -- Inherited fields from BaseModel
    id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Basic information
    category VARCHAR(50) NOT NULL,
    name VARCHAR(50) NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Configuration
    config JSONB NOT NULL,
    prompts JSONB NOT NULL,
    compatibility JSONB NOT NULL,
    
    UNIQUE (category, name)
);
```

## Relationships

1. Image -> ImageOverlay: One-to-many
2. Image -> MapGrid: One-to-one
3. Theme -> ThemeVariation: One-to-many
4. ThemeElement: Independent table with category/name uniqueness constraint
5. StylePreset: Independent table with unique name constraint