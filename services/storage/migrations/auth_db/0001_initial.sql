-- Create auth_db schema
CREATE SCHEMA IF NOT EXISTS auth_db;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION auth_db.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Users table
CREATE TABLE auth_db.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR NOT NULL UNIQUE,
    email VARCHAR NOT NULL UNIQUE,
    password_hash VARCHAR NOT NULL,
    mfa_enabled BOOLEAN NOT NULL DEFAULT false,
    mfa_secret VARCHAR,
    last_login TIMESTAMPTZ,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ,
    status VARCHAR NOT NULL DEFAULT 'active',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON auth_db.users(username);
CREATE INDEX idx_users_email ON auth_db.users(email);
CREATE INDEX idx_users_status ON auth_db.users(status);

-- Roles table
CREATE TABLE auth_db.roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL UNIQUE,
    description TEXT,
    is_system_role BOOLEAN NOT NULL DEFAULT false,
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_roles_name ON auth_db.roles(name);

-- Permissions table
CREATE TABLE auth_db.permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL UNIQUE,
    description TEXT,
    resource VARCHAR NOT NULL,
    action VARCHAR NOT NULL,
    is_system_permission BOOLEAN NOT NULL DEFAULT false,
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_permissions_name ON auth_db.permissions(name);
CREATE INDEX idx_permissions_resource ON auth_db.permissions(resource);
CREATE INDEX idx_permissions_action ON auth_db.permissions(action);

-- Role permissions mapping table
CREATE TABLE auth_db.role_permissions (
    role_id UUID NOT NULL REFERENCES auth_db.roles(id),
    permission_id UUID NOT NULL REFERENCES auth_db.permissions(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);

-- User roles mapping table
CREATE TABLE auth_db.user_roles (
    user_id UUID NOT NULL REFERENCES auth_db.users(id),
    role_id UUID NOT NULL REFERENCES auth_db.roles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id)
);

-- Sessions table
CREATE TABLE auth_db.sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth_db.users(id),
    access_token VARCHAR NOT NULL,
    refresh_token VARCHAR NOT NULL,
    token_type VARCHAR NOT NULL DEFAULT 'Bearer',
    expires_at TIMESTAMPTZ NOT NULL,
    client_info JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    revoked_at TIMESTAMPTZ,
    last_activity TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_user_id ON auth_db.sessions(user_id);
CREATE INDEX idx_sessions_access_token ON auth_db.sessions(access_token);
CREATE INDEX idx_sessions_refresh_token ON auth_db.sessions(refresh_token);

-- API keys table
CREATE TABLE auth_db.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth_db.users(id),
    key_hash VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    description TEXT,
    expires_at TIMESTAMPTZ,
    last_used TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_api_keys_user_id ON auth_db.api_keys(user_id);
CREATE INDEX idx_api_keys_key_hash ON auth_db.api_keys(key_hash);

-- Audit logs table
CREATE TABLE auth_db.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth_db.users(id),
    action VARCHAR NOT NULL,
    resource_type VARCHAR NOT NULL,
    resource_id UUID,
    old_data JSONB,
    new_data JSONB,
    client_info JSONB NOT NULL DEFAULT '{}',
    ip_address VARCHAR,
    success BOOLEAN NOT NULL DEFAULT true,
    failure_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON auth_db.audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON auth_db.audit_logs(action);
CREATE INDEX idx_audit_logs_resource_type ON auth_db.audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON auth_db.audit_logs(created_at);

-- Password reset tokens table
CREATE TABLE auth_db.password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth_db.users(id),
    token_hash VARCHAR NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    is_used BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_password_reset_tokens_user_id ON auth_db.password_reset_tokens(user_id);
CREATE INDEX idx_password_reset_tokens_token_hash ON auth_db.password_reset_tokens(token_hash);

-- Create updated_at triggers for all tables that need it
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON auth_db.users
    FOR EACH ROW
    EXECUTE FUNCTION auth_db.update_updated_at();

CREATE TRIGGER update_roles_updated_at
    BEFORE UPDATE ON auth_db.roles
    FOR EACH ROW
    EXECUTE FUNCTION auth_db.update_updated_at();

CREATE TRIGGER update_permissions_updated_at
    BEFORE UPDATE ON auth_db.permissions
    FOR EACH ROW
    EXECUTE FUNCTION auth_db.update_updated_at();

CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON auth_db.sessions
    FOR EACH ROW
    EXECUTE FUNCTION auth_db.update_updated_at();

CREATE TRIGGER update_api_keys_updated_at
    BEFORE UPDATE ON auth_db.api_keys
    FOR EACH ROW
    EXECUTE FUNCTION auth_db.update_updated_at();