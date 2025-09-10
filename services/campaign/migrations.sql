CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TABLE campaigns (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    campaign_type VARCHAR(50) NOT NULL DEFAULT 'traditional',
    state VARCHAR(50) NOT NULL DEFAULT 'draft',
    theme_id UUID,
    theme_data JSONB NOT NULL DEFAULT '{}',
    campaign_metadata JSONB NOT NULL DEFAULT '{}',
    creator_id UUID NOT NULL,
    owner_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE chapters (
    id UUID PRIMARY KEY,
    campaign_id UUID NOT NULL REFERENCES campaigns(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    chapter_type VARCHAR(50) NOT NULL DEFAULT 'story',
    state VARCHAR(50) NOT NULL DEFAULT 'draft',
    sequence_number INTEGER NOT NULL,
    content JSONB NOT NULL DEFAULT '{}',
    chapter_metadata JSONB NOT NULL DEFAULT '{}',
    prerequisites JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE TRIGGER update_campaigns_modtime 
    BEFORE UPDATE ON campaigns 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chapters_modtime 
    BEFORE UPDATE ON chapters 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE INDEX ix_campaigns_name ON campaigns(name);
CREATE INDEX ix_chapters_campaign_id ON chapters(campaign_id);
CREATE INDEX ix_chapters_sequence_number ON chapters(sequence_number);
