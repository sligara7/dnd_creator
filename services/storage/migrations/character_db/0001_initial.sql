-- Create character_db schema
CREATE SCHEMA IF NOT EXISTS character_db;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION character_db.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Characters table
CREATE TABLE character_db.characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES character_db.characters(id),
    theme VARCHAR NOT NULL DEFAULT 'traditional',
    name VARCHAR NOT NULL,
    user_id UUID NOT NULL,
    campaign_id UUID NOT NULL,
    character_data JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_characters_name ON character_db.characters(name);
CREATE INDEX idx_characters_user_id ON character_db.characters(user_id);
CREATE INDEX idx_characters_campaign_id ON character_db.characters(campaign_id);
CREATE INDEX idx_characters_theme ON character_db.characters(theme);

-- Inventory items table
CREATE TABLE character_db.inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    root_id UUID REFERENCES character_db.inventory_items(id),
    theme VARCHAR NOT NULL DEFAULT 'traditional',
    character_id UUID NOT NULL REFERENCES character_db.characters(id),
    item_data JSONB NOT NULL DEFAULT '{}',
    quantity INTEGER NOT NULL DEFAULT 1,
    equipped BOOLEAN NOT NULL DEFAULT false,
    container VARCHAR,
    notes TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inventory_items_character_id ON character_db.inventory_items(character_id);
CREATE INDEX idx_inventory_items_container ON character_db.inventory_items(container);
CREATE INDEX idx_inventory_items_equipped ON character_db.inventory_items(equipped);

-- Journal entries table
CREATE TABLE character_db.journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID NOT NULL REFERENCES character_db.characters(id),
    entry_type VARCHAR NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    title VARCHAR NOT NULL,
    content TEXT NOT NULL,
    data JSONB NOT NULL DEFAULT '{}',
    tags JSONB NOT NULL DEFAULT '[]',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT true,
    session_number INTEGER,
    session_date TIMESTAMPTZ,
    dm_name VARCHAR,
    session_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_journal_entries_character_id ON character_db.journal_entries(character_id);
CREATE INDEX idx_journal_entries_entry_type ON character_db.journal_entries(entry_type);
CREATE INDEX idx_journal_entries_session_number ON character_db.journal_entries(session_number);

-- Experience entries table
CREATE TABLE character_db.experience_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES character_db.journal_entries(id),
    amount INTEGER NOT NULL,
    source VARCHAR NOT NULL,
    reason VARCHAR NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    session_id UUID,
    data JSONB NOT NULL DEFAULT '{}',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_experience_entries_journal_entry_id ON character_db.experience_entries(journal_entry_id);
CREATE INDEX idx_experience_entries_session_id ON character_db.experience_entries(session_id);

-- Quests table
CREATE TABLE character_db.quests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES character_db.journal_entries(id),
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'active',
    importance VARCHAR NOT NULL DEFAULT 'normal',
    assigned_by VARCHAR,
    rewards JSONB NOT NULL DEFAULT '{}',
    progress JSONB NOT NULL DEFAULT '[]',
    data JSONB NOT NULL DEFAULT '{}',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quests_journal_entry_id ON character_db.quests(journal_entry_id);
CREATE INDEX idx_quests_status ON character_db.quests(status);
CREATE INDEX idx_quests_importance ON character_db.quests(importance);

-- NPC relationships table
CREATE TABLE character_db.npc_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journal_entry_id UUID NOT NULL REFERENCES character_db.journal_entries(id),
    npc_id UUID NOT NULL,
    npc_name VARCHAR NOT NULL,
    relationship_type VARCHAR NOT NULL,
    standing INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    last_interaction TIMESTAMPTZ,
    data JSONB NOT NULL DEFAULT '{}',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_npc_relationships_journal_entry_id ON character_db.npc_relationships(journal_entry_id);
CREATE INDEX idx_npc_relationships_npc_id ON character_db.npc_relationships(npc_id);
CREATE INDEX idx_npc_relationships_relationship_type ON character_db.npc_relationships(relationship_type);

-- Campaign events table
CREATE TABLE character_db.campaign_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID NOT NULL REFERENCES character_db.characters(id),
    journal_entry_id UUID REFERENCES character_db.journal_entries(id),
    event_type VARCHAR NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}',
    impact_type VARCHAR NOT NULL,
    impact_magnitude INTEGER NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    applied BOOLEAN NOT NULL DEFAULT false,
    applied_at TIMESTAMPTZ,
    data JSONB NOT NULL DEFAULT '{}',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_campaign_events_character_id ON character_db.campaign_events(character_id);
CREATE INDEX idx_campaign_events_journal_entry_id ON character_db.campaign_events(journal_entry_id);
CREATE INDEX idx_campaign_events_event_type ON character_db.campaign_events(event_type);
CREATE INDEX idx_campaign_events_impact_type ON character_db.campaign_events(impact_type);

-- Event impacts table
CREATE TABLE character_db.event_impacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES character_db.campaign_events(id),
    character_id UUID NOT NULL REFERENCES character_db.characters(id),
    impact_type VARCHAR NOT NULL,
    impact_data JSONB NOT NULL DEFAULT '{}',
    applied BOOLEAN NOT NULL DEFAULT false,
    applied_at TIMESTAMPTZ,
    reversion_data JSONB,
    is_reverted BOOLEAN NOT NULL DEFAULT false,
    reverted_at TIMESTAMPTZ,
    notes TEXT,
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_event_impacts_event_id ON character_db.event_impacts(event_id);
CREATE INDEX idx_event_impacts_character_id ON character_db.event_impacts(character_id);
CREATE INDEX idx_event_impacts_impact_type ON character_db.event_impacts(impact_type);

-- Character progress table
CREATE TABLE character_db.character_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID NOT NULL REFERENCES character_db.characters(id),
    experience_points INTEGER NOT NULL DEFAULT 0,
    milestones JSONB NOT NULL DEFAULT '[]',
    achievements JSONB NOT NULL DEFAULT '[]',
    current_level INTEGER NOT NULL DEFAULT 1,
    previous_level INTEGER NOT NULL DEFAULT 1,
    level_updated_at TIMESTAMPTZ,
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_character_progress_character_id ON character_db.character_progress(character_id);
CREATE INDEX idx_character_progress_current_level ON character_db.character_progress(current_level);

-- Create updated_at triggers for all tables
CREATE TRIGGER update_characters_updated_at
    BEFORE UPDATE ON character_db.characters
    FOR EACH ROW
    EXECUTE FUNCTION character_db.update_updated_at();

CREATE TRIGGER update_inventory_items_updated_at
    BEFORE UPDATE ON character_db.inventory_items
    FOR EACH ROW
    EXECUTE FUNCTION character_db.update_updated_at();

CREATE TRIGGER update_journal_entries_updated_at
    BEFORE UPDATE ON character_db.journal_entries
    FOR EACH ROW
    EXECUTE FUNCTION character_db.update_updated_at();

CREATE TRIGGER update_experience_entries_updated_at
    BEFORE UPDATE ON character_db.experience_entries
    FOR EACH ROW
    EXECUTE FUNCTION character_db.update_updated_at();

CREATE TRIGGER update_quests_updated_at
    BEFORE UPDATE ON character_db.quests
    FOR EACH ROW
    EXECUTE FUNCTION character_db.update_updated_at();

CREATE TRIGGER update_npc_relationships_updated_at
    BEFORE UPDATE ON character_db.npc_relationships
    FOR EACH ROW
    EXECUTE FUNCTION character_db.update_updated_at();

CREATE TRIGGER update_campaign_events_updated_at
    BEFORE UPDATE ON character_db.campaign_events
    FOR EACH ROW
    EXECUTE FUNCTION character_db.update_updated_at();

CREATE TRIGGER update_event_impacts_updated_at
    BEFORE UPDATE ON character_db.event_impacts
    FOR EACH ROW
    EXECUTE FUNCTION character_db.update_updated_at();

CREATE TRIGGER update_character_progress_updated_at
    BEFORE UPDATE ON character_db.character_progress
    FOR EACH ROW
    EXECUTE FUNCTION character_db.update_updated_at();