"""Initialize database.

Revision ID: 2025_09_02_01
Revises: 
Create Date: 2025-09-02 02:35:00.000000

"""
import uuid
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2025_09_02_01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    op.execute("CREATE TYPE charactertype AS ENUM ('PLAYER', 'NPC', 'MONSTER')")
    op.execute("CREATE TYPE campaigntype AS ENUM ('TRADITIONAL', 'ANTITHETICON')")

    # Create characters table
    op.create_table('characters',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('character_type', postgresql.ENUM('PLAYER', 'NPC', 'MONSTER', name='charactertype'), nullable=False),
        sa.Column('campaign_type', postgresql.ENUM('TRADITIONAL', 'ANTITHETICON', name='campaigntype'), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('race', sa.String(), nullable=False),
        sa.Column('character_class', sa.String(), nullable=False),
        sa.Column('background', sa.String(), nullable=True),
        sa.Column('alignment', sa.String(), nullable=True),
        sa.Column('strength', sa.Integer(), nullable=False),
        sa.Column('dexterity', sa.Integer(), nullable=False),
        sa.Column('constitution', sa.Integer(), nullable=False),
        sa.Column('intelligence', sa.Integer(), nullable=False),
        sa.Column('wisdom', sa.Integer(), nullable=False),
        sa.Column('charisma', sa.Integer(), nullable=False),
        sa.Column('max_hit_points', sa.Integer(), nullable=False),
        sa.Column('current_hit_points', sa.Integer(), nullable=False),
        sa.Column('temporary_hit_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('armor_class', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('initiative', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('speed', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('experience_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('hit_dice_total', sa.Integer(), nullable=False),
        sa.Column('hit_dice_current', sa.Integer(), nullable=False),
        sa.Column('personality_traits', sa.String(), nullable=True),
        sa.Column('ideals', sa.String(), nullable=True),
        sa.Column('bonds', sa.String(), nullable=True),
        sa.Column('flaws', sa.String(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create inventories table
    op.create_table('inventories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('characters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('items', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('gold', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('silver', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('copper', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create journal_entries table
    op.create_table('journal_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('character_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('characters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('session_number', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create update_updated_at_column function
    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = now();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """)

    # Create triggers for updated_at
    for table in ['characters', 'inventories', 'journal_entries']:
        op.execute(f"""
        CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    # Drop triggers
    for table in ['characters', 'inventories', 'journal_entries']:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop tables
    op.drop_table('journal_entries')
    op.drop_table('inventories')
    op.drop_table('characters')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS charactertype")
    op.execute("DROP TYPE IF EXISTS campaigntype")
