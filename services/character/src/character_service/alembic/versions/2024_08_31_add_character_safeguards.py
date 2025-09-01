"""Add character deletion safeguards

Revision ID: 2024_08_31_character_safeguards
Create Date: 2024-08-31 08:55:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2024_08_31_character_safeguards'
down_revision = '2024_08_31_inventory_items'  # Depends on inventory items
branch_labels = None
depends_on = None

def upgrade():
    # Add campaign and deletion tracking to characters
    op.add_column('characters', sa.Column('campaign_status', sa.String(), nullable=False, server_default='inactive'))
    op.add_column('characters', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('characters', sa.Column('deletion_reason', sa.Text(), nullable=True))
    
    # Add soft deletion tracking to inventory items
    op.add_column('inventory_items', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('inventory_items', sa.Column('deletion_reason', sa.Text(), nullable=True))
    op.add_column('inventory_items', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

    # Create character interactions table for explicit tracking
    op.create_table(
        'character_interactions',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('source_character_id', sa.String(), nullable=False),
        sa.Column('target_character_id', sa.String(), nullable=False),
        sa.Column('interaction_type', sa.String(), nullable=False),
        sa.Column('campaign_id', sa.String(), nullable=False),
        sa.Column('journal_entry_id', postgresql.UUID(), nullable=True),
        sa.Column('interaction_data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indices for better query performance
    op.create_index(
        'ix_character_interactions_campaign',
        'character_interactions',
        ['campaign_id', 'source_character_id', 'target_character_id']
    )
    op.create_index(
        'ix_character_interactions_journal',
        'character_interactions',
        ['journal_entry_id']
    )

    # Add foreign key to journal_entries but make it nullable and don't cascade
    op.add_column('journal_entries', 
        sa.Column('interaction_id', postgresql.UUID(), nullable=True)
    )
    op.create_foreign_key(
        'fk_journal_interaction',
        'journal_entries', 'character_interactions',
        ['interaction_id'], ['id'],
        ondelete='SET NULL'  # If interaction is deleted, preserve the journal entry
    )

    # Add triggers to prevent deletion of active campaign characters
    op.execute("""
    CREATE OR REPLACE FUNCTION prevent_active_character_deletion() 
    RETURNS TRIGGER AS $$
    BEGIN
        IF OLD.campaign_status = 'active' AND OLD.deleted_at IS NULL AND NEW.deleted_at IS NOT NULL THEN
            RAISE EXCEPTION 'Cannot delete character that is part of an active campaign';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER tr_prevent_active_character_deletion
    BEFORE UPDATE OF deleted_at ON characters
    FOR EACH ROW
    EXECUTE FUNCTION prevent_active_character_deletion();
    """)

def downgrade():
    # Remove trigger
    op.execute("DROP TRIGGER IF EXISTS tr_prevent_active_character_deletion ON characters")
    op.execute("DROP FUNCTION IF EXISTS prevent_active_character_deletion()")

    # Remove foreign key and column from journal_entries
    op.drop_constraint('fk_journal_interaction', 'journal_entries', type_='foreignkey')
    op.drop_column('journal_entries', 'interaction_id')

    # Drop indices
    op.drop_index('ix_character_interactions_journal')
    op.drop_index('ix_character_interactions_campaign')

    # Drop character interactions table
    op.drop_table('character_interactions')

    # Remove columns from inventory_items
    op.drop_column('inventory_items', 'is_active')
    op.drop_column('inventory_items', 'deletion_reason')
    op.drop_column('inventory_items', 'deleted_at')

    # Remove columns from characters
    op.drop_column('characters', 'deletion_reason')
    op.drop_column('characters', 'deleted_at')
    op.drop_column('characters', 'campaign_status')
