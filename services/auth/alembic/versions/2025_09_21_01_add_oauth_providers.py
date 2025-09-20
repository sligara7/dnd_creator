"""Add OAuth provider tables.

Revision ID: 2025_09_21_01
Revises: 2025_09_20_05
Create Date: 2025-09-21 01:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2025_09_21_01'
down_revision: Union[str, None] = '2025_09_20_05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create provider_type enum
    op.execute("""
        CREATE TYPE provider_type AS ENUM ('oidc', 'oauth2', 'saml');
    """)
    
    # Create oauth_providers table
    op.create_table(
        'oauth_providers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider_id', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=False),
        sa.Column('provider_type', sa.Enum('oidc', 'oauth2', 'saml',
                                         name='provider_type'),
                  nullable=False),
        sa.Column('authorization_url', sa.String(), nullable=False),
        sa.Column('token_url', sa.String(), nullable=False),
        sa.Column('userinfo_url', sa.String(), nullable=True),
        sa.Column('jwks_url', sa.String(), nullable=True),
        sa.Column('client_id', sa.String(), nullable=False),
        sa.Column('client_secret_hash', sa.String(), nullable=False),
        sa.Column('scopes', sa.String(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False,
                  server_default=sa.text('true')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False,
                  server_default=sa.text('false')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_id')
    )
    
    # Create indexes for oauth_providers
    op.create_index('idx_oauth_providers_id', 'oauth_providers', ['id'])
    op.create_index('idx_oauth_providers_provider_id', 'oauth_providers',
                    ['provider_id'])
    op.create_index('idx_oauth_providers_enabled', 'oauth_providers',
                    ['is_enabled'])
    
    # Create provider_accounts table
    op.create_table(
        'provider_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider_id', sa.String(), nullable=False),
        sa.Column('provider_user_id', sa.String(), nullable=False),
        sa.Column('provider_username', sa.String(), nullable=True),
        sa.Column('provider_email', sa.String(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()),
                  nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False,
                  server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['provider_id'], ['oauth_providers.provider_id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_id', 'provider_user_id',
                           name='uq_provider_accounts_provider_user')
    )
    
    # Create indexes for provider_accounts
    op.create_index('idx_provider_accounts_user_id', 'provider_accounts',
                    ['user_id'])
    op.create_index('idx_provider_accounts_provider', 'provider_accounts',
                    ['provider_id'])
    
    # Create updated_at trigger for oauth_providers
    op.execute("""
        CREATE TRIGGER update_oauth_providers_updated_at
            BEFORE UPDATE ON oauth_providers
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)
    
    # Create updated_at trigger for provider_accounts
    op.execute("""
        CREATE TRIGGER update_provider_accounts_updated_at
            BEFORE UPDATE ON provider_accounts
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop provider_accounts table and indexes
    op.drop_table('provider_accounts')
    
    # Drop oauth_providers table and indexes
    op.drop_table('oauth_providers')
    
    # Drop provider_type enum
    op.execute("""
        DROP TYPE provider_type;
    """)