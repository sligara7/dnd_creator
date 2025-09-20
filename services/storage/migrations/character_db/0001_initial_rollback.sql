-- Drop all triggers first
DROP TRIGGER IF EXISTS update_character_progress_updated_at ON character_db.character_progress;
DROP TRIGGER IF EXISTS update_event_impacts_updated_at ON character_db.event_impacts;
DROP TRIGGER IF EXISTS update_campaign_events_updated_at ON character_db.campaign_events;
DROP TRIGGER IF EXISTS update_npc_relationships_updated_at ON character_db.npc_relationships;
DROP TRIGGER IF EXISTS update_quests_updated_at ON character_db.quests;
DROP TRIGGER IF EXISTS update_experience_entries_updated_at ON character_db.experience_entries;
DROP TRIGGER IF EXISTS update_journal_entries_updated_at ON character_db.journal_entries;
DROP TRIGGER IF EXISTS update_inventory_items_updated_at ON character_db.inventory_items;
DROP TRIGGER IF EXISTS update_characters_updated_at ON character_db.characters;

-- Drop all tables in reverse order of dependencies
DROP TABLE IF EXISTS character_db.character_progress;
DROP TABLE IF EXISTS character_db.event_impacts;
DROP TABLE IF EXISTS character_db.campaign_events;
DROP TABLE IF EXISTS character_db.npc_relationships;
DROP TABLE IF EXISTS character_db.quests;
DROP TABLE IF EXISTS character_db.experience_entries;
DROP TABLE IF EXISTS character_db.journal_entries;
DROP TABLE IF EXISTS character_db.inventory_items;
DROP TABLE IF EXISTS character_db.characters;

-- Drop the trigger function
DROP FUNCTION IF EXISTS character_db.update_updated_at();

-- Drop the schema
DROP SCHEMA IF EXISTS character_db;