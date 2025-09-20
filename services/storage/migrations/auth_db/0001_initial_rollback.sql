-- Drop triggers first
DROP TRIGGER IF EXISTS update_api_keys_updated_at ON auth_db.api_keys;
DROP TRIGGER IF EXISTS update_sessions_updated_at ON auth_db.sessions;
DROP TRIGGER IF EXISTS update_permissions_updated_at ON auth_db.permissions;
DROP TRIGGER IF EXISTS update_roles_updated_at ON auth_db.roles;
DROP TRIGGER IF EXISTS update_users_updated_at ON auth_db.users;

-- Drop tables in correct order (respect foreign key constraints)
DROP TABLE IF EXISTS auth_db.password_reset_tokens;
DROP TABLE IF EXISTS auth_db.audit_logs;
DROP TABLE IF EXISTS auth_db.api_keys;
DROP TABLE IF EXISTS auth_db.sessions;
DROP TABLE IF EXISTS auth_db.user_roles;
DROP TABLE IF EXISTS auth_db.role_permissions;
DROP TABLE IF EXISTS auth_db.permissions;
DROP TABLE IF EXISTS auth_db.roles;
DROP TABLE IF EXISTS auth_db.users;

-- Drop functions
DROP FUNCTION IF EXISTS auth_db.update_updated_at();

-- Drop schema
DROP SCHEMA IF EXISTS auth_db;