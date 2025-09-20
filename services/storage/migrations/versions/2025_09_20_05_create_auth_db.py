"""Create auth database schema.

This migration creates the auth database schema and all required tables
within the auth schema in the storage service.

Revision ID: 2025_09_20_05
Revises: 2025_09_20_04
Create Date: 2025-09-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON, JSONB

# revision identifiers, used by Alembic.
revision: str = '2025_09_20_05'
down_revision: Union[str, None] = '2025_09_20_04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Create auth schema and all required tables."""
    # Create auth schema
    op.execute('CREATE SCHEMA IF NOT EXISTS auth')
    
    # Create enums
    op.execute("""
        CREATE TYPE auth.user_role AS ENUM (
            'admin',
            'player',
            'game_master',
            'creator',
            'moderator',
            'api_user'
        )
    """)

    op.execute("""
        CREATE TYPE auth.login_method AS ENUM (
            'password',
            'oauth',
            'api_key',
            'session_token'
        )
    """)

    op.execute("""
        CREATE TYPE auth.token_type AS ENUM (
            'access',
            'refresh',
            'reset',
            'verify'
        )
    """)

    op.execute("""
        CREATE TYPE auth.audit_type AS ENUM (
            'login',
            'logout',
            'password_reset',
            'account_update',
            'role_change',
            'api_access',
            'oauth_token',
            'security_event'
        )
    """)

    # Create users table
    op.create_table('users',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('username', sa.String(255), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255)),
        sa.Column('full_name', sa.String(255)),
        sa.Column('role', sa.Enum('admin', 'player', 'game_master', 'creator', 'moderator', 'api_user',
                            name='user_role', schema='auth'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.Column('login_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('locked_until', sa.DateTime(timezone=True)),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='auth'
    )

    # Create roles table
    op.create_table('roles',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('permissions', ARRAY(sa.String()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='auth'
    )

    # Create user_roles table (many-to-many)
    op.create_table('user_roles',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_id', UUID(as_uuid=True), sa.ForeignKey('auth.roles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('granted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('granted_by', UUID(as_uuid=True), nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True)),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='auth',
        sqlite_on_conflict='IGNORE'
    )

    # Create permissions table
    op.create_table('permissions',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(50), unique=True, nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('constraints', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='auth'
    )

    # Create sessions table
    op.create_table('sessions',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(255), unique=True, nullable=False),
        sa.Column('login_method', sa.Enum('password', 'oauth', 'api_key', 'session_token',
                                name='login_method', schema='auth'), nullable=False),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(255)),
        sa.Column('device_id', sa.String(255)),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        schema='auth'
    )

    # Create tokens table
    op.create_table('tokens',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(255), unique=True, nullable=False),
        sa.Column('type', sa.Enum('access', 'refresh', 'reset', 'verify',
                            name='token_type', schema='auth'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        schema='auth'
    )

    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('auth.users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('key_hash', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('scope', ARRAY(sa.String()), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(timezone=True)),
        sa.Column('last_used_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='auth'
    )

    # Create audit_log table
    op.create_table('audit_log',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('auth.users.id', ondelete='CASCADE')),
        sa.Column('type', sa.Enum('login', 'logout', 'password_reset', 'account_update', 'role_change',
                            'api_access', 'oauth_token', 'security_event',
                            name='audit_type', schema='auth'), nullable=False),
        sa.Column('action', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(255)),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        schema='auth'
    )

    # Create indices
    op.create_index('ix_auth_users_email', 'users', ['email'], schema='auth')
    op.create_index('ix_auth_users_username', 'users', ['username'], schema='auth')
    op.create_index('ix_auth_sessions_user_id', 'sessions', ['user_id'], schema='auth')
    op.create_index('ix_auth_sessions_token', 'sessions', ['token'], schema='auth')
    op.create_index('ix_auth_tokens_user_id', 'tokens', ['user_id'], schema='auth')
    op.create_index('ix_auth_tokens_token', 'tokens', ['token'], schema='auth')
    op.create_index('ix_auth_api_keys_user_id', 'api_keys', ['user_id'], schema='auth')
    op.create_index('ix_auth_api_keys_key_hash', 'api_keys', ['key_hash'], schema='auth')
    op.create_index('ix_auth_audit_log_user_id', 'audit_log', ['user_id'], schema='auth')
    op.create_index('ix_auth_audit_log_type', 'audit_log', ['type'], schema='auth')
    op.create_index('ix_auth_audit_log_created_at', 'audit_log', ['created_at'], schema='auth')

    # Add unique constraints
    op.create_unique_constraint('uq_auth_user_roles_user_role', 'user_roles',
                             ['user_id', 'role_id'], schema='auth')

    # Create updated_at trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION auth.update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Add triggers
    for table in ['users', 'roles', 'permissions', 'api_keys']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_modtime
                BEFORE UPDATE ON auth.{table}
                FOR EACH ROW
                EXECUTE FUNCTION auth.update_updated_at_column();
        """)

def downgrade() -> None:
    """Remove auth schema and all tables."""
    # Drop triggers
    for table in ['users', 'roles', 'permissions', 'api_keys']:
        op.execute(f'DROP TRIGGER IF EXISTS update_{table}_modtime ON auth.{table}')
    op.execute('DROP FUNCTION IF EXISTS auth.update_updated_at_column()')

    # Drop indices
    op.drop_index('ix_auth_audit_log_created_at', table_name='audit_log', schema='auth')
    op.drop_index('ix_auth_audit_log_type', table_name='audit_log', schema='auth')
    op.drop_index('ix_auth_audit_log_user_id', table_name='audit_log', schema='auth')
    op.drop_index('ix_auth_api_keys_key_hash', table_name='api_keys', schema='auth')
    op.drop_index('ix_auth_api_keys_user_id', table_name='api_keys', schema='auth')
    op.drop_index('ix_auth_tokens_token', table_name='tokens', schema='auth')
    op.drop_index('ix_auth_tokens_user_id', table_name='tokens', schema='auth')
    op.drop_index('ix_auth_sessions_token', table_name='sessions', schema='auth')
    op.drop_index('ix_auth_sessions_user_id', table_name='sessions', schema='auth')
    op.drop_index('ix_auth_users_username', table_name='users', schema='auth')
    op.drop_index('ix_auth_users_email', table_name='users', schema='auth')

    # Drop tables
    op.drop_table('audit_log', schema='auth')
    op.drop_table('api_keys', schema='auth')
    op.drop_table('tokens', schema='auth')
    op.drop_table('sessions', schema='auth')
    op.drop_table('user_roles', schema='auth')
    op.drop_table('permissions', schema='auth')
    op.drop_table('roles', schema='auth')
    op.drop_table('users', schema='auth')

    # Drop enums
    op.execute('DROP TYPE auth.audit_type')
    op.execute('DROP TYPE auth.token_type')
    op.execute('DROP TYPE auth.login_method')
    op.execute('DROP TYPE auth.user_role')

    # Drop schema
    op.execute('DROP SCHEMA auth')