-- Create initial schema
CREATE TABLE characters (
    id UUID NOT NULL,
    name VARCHAR NOT NULL,
    species VARCHAR NOT NULL,
    background VARCHAR NOT NULL,
    level INTEGER NOT NULL,
    character_classes JSONB NOT NULL,
    ability_scores JSONB NOT NULL,
    equipment JSONB NOT NULL DEFAULT '[]'::jsonb,
    spells_known JSONB NOT NULL DEFAULT '[]'::jsonb,
    spells_prepared JSONB NOT NULL DEFAULT '[]'::jsonb,
    features JSONB NOT NULL DEFAULT '[]'::jsonb,
    racial_bonuses JSONB,
    warnings JSONB,
    hit_points INTEGER NOT NULL,
    armor_class INTEGER NOT NULL,
    proficiency_bonus INTEGER NOT NULL,
    spell_save_dc INTEGER,
    spellcasting_ability VARCHAR,
    user_id UUID NOT NULL,
    campaign_id UUID NOT NULL,
    CONSTRAINT pk_characters PRIMARY KEY (id)
);
