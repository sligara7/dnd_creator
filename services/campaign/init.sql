-- Initialize database with required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "hstore";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create user with appropriate permissions
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'campaign_user') THEN
    CREATE USER campaign_user WITH PASSWORD 'campaign_pass';
  END IF;
END
$$;

-- Grant permissions
ALTER USER campaign_user WITH CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE campaign TO campaign_user;

-- Create schemas if needed
CREATE SCHEMA IF NOT EXISTS campaign AUTHORIZATION campaign_user;

-- Set search path
ALTER DATABASE campaign SET search_path TO campaign, public;

-- Grant schema permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA campaign TO campaign_user;
GRANT USAGE, CREATE ON SCHEMA campaign TO campaign_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA campaign GRANT ALL PRIVILEGES ON TABLES TO campaign_user;
