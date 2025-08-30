"""Initial migration.

Create all initial database tables for the character service.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Import all models to get their table metadata
from character.db.models import (
    CharacterModel,
    AbilityModel,
    SkillModel,
    EquipmentModel,
    WeaponModel,
    ArmorModel,
    RaceModel,
    BackgroundModel,
)

# revision identifiers, used by Alembic
revision = "01_initial_tables"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create all initial tables."""
    # Create races table
    op.create_table(
        "races",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("size", sa.String(20), nullable=False),
        sa.Column("base_speed", sa.Integer, nullable=False),
        sa.Column("ability_bonuses", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("ability_choices", sa.JSON, nullable=True),
        sa.Column("languages", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("extra_languages", sa.Integer, nullable=False, server_default="0"),
        sa.Column("traits", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("subraces", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.UniqueConstraint("name", "source", name="uq_race_name_source"),
    )
    
    # Create backgrounds table
    op.create_table(
        "backgrounds",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("skill_proficiencies", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("tool_proficiencies", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("languages", sa.Integer, nullable=False, server_default="0"),
        sa.Column("equipment", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("feature", sa.JSON, nullable=False),
        sa.Column("personality_traits", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("ideals", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("bonds", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("flaws", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.UniqueConstraint("name", "source", name="uq_background_name_source"),
    )
    
    # Create characters table
    op.create_table(
        "characters",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("player_name", sa.String(100), nullable=True),
        sa.Column("campaign_id", UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("gender", sa.String(50), nullable=True),
        sa.Column("pronouns", sa.String(50), nullable=True),
        sa.Column("faith", sa.String(100), nullable=True),
        sa.Column("age", sa.Integer, nullable=True),
        sa.Column("height", sa.String(50), nullable=True),
        sa.Column("weight", sa.String(50), nullable=True),
        sa.Column("size", sa.String(20), nullable=False),
        sa.Column("eye_color", sa.String(50), nullable=True),
        sa.Column("hair_color", sa.String(50), nullable=True),
        sa.Column("skin_color", sa.String(50), nullable=True),
        sa.Column("appearance_notes", sa.Text, nullable=True),
        sa.Column("race_id", UUID(as_uuid=True), nullable=False),
        sa.Column("background_id", UUID(as_uuid=True), nullable=False),
        sa.Column("alignment_moral", sa.String(20), nullable=False),
        sa.Column("alignment_ethical", sa.String(20), nullable=False),
        sa.Column("personality_traits", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("ideals", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("bonds", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("flaws", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("armor_class", sa.Integer, nullable=False, server_default="10"),
        sa.Column("initiative_bonus", sa.Integer, nullable=False, server_default="0"),
        sa.Column("hit_point_maximum", sa.Integer, nullable=False, server_default="0"),
        sa.Column("current_hit_points", sa.Integer, nullable=False, server_default="0"),
        sa.Column("temporary_hit_points", sa.Integer, nullable=False, server_default="0"),
        sa.Column("hit_dice", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("death_save_successes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("death_save_failures", sa.Integer, nullable=False, server_default="0"),
        sa.Column("spellcasting_ability", sa.String(20), nullable=True),
        sa.Column("vision_types", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("movement_modes", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("damage_resistances", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("damage_immunities", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("damage_vulnerabilities", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("condition_immunities", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("active_conditions", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("active_effects", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("temporary_bonuses", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("background_story", sa.Text, nullable=True),
        sa.Column("notes", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("goals", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("connections", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("tags", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("custom_fields", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("flags", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["race_id"], ["races.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["background_id"], ["backgrounds.id"], ondelete="RESTRICT"),
    )
    
    # Create abilities table
    op.create_table(
        "abilities",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("character_id", UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("base_score", sa.Integer, nullable=False),
        sa.Column("bonuses", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("penalties", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("overrides", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("saving_throw_proficient", sa.Boolean, nullable=False, server_default="f"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("character_id", "type", name="uq_character_ability"),
    )
    
    # Create skills table
    op.create_table(
        "skills",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("character_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("ability", sa.String(20), nullable=False),
        sa.Column("proficiency", sa.String(20), nullable=False),
        sa.Column("bonuses", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("advantage_sources", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("disadvantage_sources", sa.JSON, nullable=False, server_default="[]"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("character_id", "name", name="uq_character_skill"),
    )
    
    # Create equipment table
    op.create_table(
        "equipment",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("character_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("weight", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("equipped", sa.Boolean, nullable=False, server_default="f"),
        sa.Column("attuned", sa.Boolean, nullable=False, server_default="f"),
        sa.Column("container", sa.String(100), nullable=True),
        sa.Column("properties", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("metadata", sa.JSON, nullable=False, server_default="{}"),
        sa.ForeignKeyConstraint(["character_id"], ["characters.id"], ondelete="CASCADE"),
    )
    
    # Create weapons table (inherits from equipment)
    op.create_table(
        "weapons",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("equipment_id", UUID(as_uuid=True), nullable=False),
        sa.Column("weapon_type", sa.String(50), nullable=False),
        sa.Column("damage_dice", sa.String(20), nullable=False),
        sa.Column("damage_type", sa.String(20), nullable=False),
        sa.Column("versatile_damage_dice", sa.String(20), nullable=True),
        sa.Column("range_normal", sa.Integer, nullable=True),
        sa.Column("range_long", sa.Integer, nullable=True),
        sa.Column("ammunition", sa.String(50), nullable=True),
        sa.Column("loading", sa.Boolean, nullable=False, server_default="f"),
        sa.Column("finesse", sa.Boolean, nullable=False, server_default="f"),
        sa.Column("reach", sa.Boolean, nullable=False, server_default="f"),
        sa.Column("thrown", sa.Boolean, nullable=False, server_default="f"),
        sa.Column("two_handed", sa.Boolean, nullable=False, server_default="f"),
        sa.Column("versatile", sa.Boolean, nullable=False, server_default="f"),
        sa.Column("special_properties", sa.JSON, nullable=False, server_default="[]"),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"], ondelete="CASCADE"),
    )
    
    # Create armor table (inherits from equipment)
    op.create_table(
        "armor",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("equipment_id", UUID(as_uuid=True), nullable=False),
        sa.Column("armor_type", sa.String(50), nullable=False),
        sa.Column("base_ac", sa.Integer, nullable=False),
        sa.Column("dex_bonus", sa.Boolean, nullable=False, server_default="t"),
        sa.Column("max_dex_bonus", sa.Integer, nullable=True),
        sa.Column("strength_requirement", sa.Integer, nullable=True),
        sa.Column("stealth_disadvantage", sa.Boolean, nullable=False, server_default="f"),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"], ondelete="CASCADE"),
    )
    
    # Create indexes
    op.create_index("ix_characters_name", "characters", ["name"])
    op.create_index("ix_characters_campaign_id", "characters", ["campaign_id"])
    op.create_index("ix_races_name", "races", ["name"])
    op.create_index("ix_backgrounds_name", "backgrounds", ["name"])
    op.create_index("ix_skills_name", "skills", ["name"])
    op.create_index("ix_equipment_name", "equipment", ["name"])
    op.create_index("ix_equipment_type", "equipment", ["type"])
    op.create_index("ix_weapons_weapon_type", "weapons", ["weapon_type"])
    op.create_index("ix_armor_armor_type", "armor", ["armor_type"])

def downgrade():
    """Remove all created tables."""
    # Drop in reverse order of creation to handle foreign key constraints
    op.drop_table("armor")
    op.drop_table("weapons")
    op.drop_table("equipment")
    op.drop_table("skills")
    op.drop_table("abilities")
    op.drop_table("characters")
    op.drop_table("backgrounds")
    op.drop_table("races")
