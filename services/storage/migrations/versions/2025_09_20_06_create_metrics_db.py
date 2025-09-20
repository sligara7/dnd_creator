"""Create metrics database schema.

This migration creates the metrics database schema and all required tables
within the metrics schema in the storage service. The schema is optimized
for time-series data storage and retrieval.

Revision ID: 2025_09_20_06
Revises: 2025_09_20_05
Create Date: 2025-09-20
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSON, JSONB

# revision identifiers, used by Alembic.
revision: str = '2025_09_20_06'
down_revision: Union[str, None] = '2025_09_20_05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Create metrics schema and all required tables."""
    # Create metrics schema
    op.execute('CREATE SCHEMA IF NOT EXISTS metrics')
    
    # Create enums
    op.execute("""
        CREATE TYPE metrics.metric_type AS ENUM (
            'counter',
            'gauge',
            'histogram',
            'summary',
            'set'
        )
    """)

    op.execute("""
        CREATE TYPE metrics.aggregation_type AS ENUM (
            'sum',
            'avg',
            'min',
            'max',
            'count',
            'percentile'
        )
    """)

    op.execute("""
        CREATE TYPE metrics.retention_policy AS ENUM (
            'raw',      -- Keep all data points
            'minutely',  -- Aggregate by minute
            'hourly',   -- Aggregate by hour
            'daily',    -- Aggregate by day
            'weekly',   -- Aggregate by week
            'monthly'   -- Aggregate by month
        )
    """)

    # Create metrics table
    op.create_table('metrics',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('type', sa.Enum('counter', 'gauge', 'histogram', 'summary', 'set',
                            name='metric_type', schema='metrics'), nullable=False),
        sa.Column('labels', ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('unit', sa.String(50)),
        sa.Column('aggregation', sa.Enum('sum', 'avg', 'min', 'max', 'count', 'percentile',
                                name='aggregation_type', schema='metrics'), nullable=False),
        sa.Column('retention', sa.Enum('raw', 'minutely', 'hourly', 'daily', 'weekly', 'monthly',
                                name='retention_policy', schema='metrics'), nullable=False),
        sa.Column('metadata', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='metrics'
    )

    # Create time series table - partitioned by time for better performance
    op.execute("""
        CREATE TABLE metrics.time_series (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            metric_id UUID NOT NULL REFERENCES metrics.metrics(id),
            timestamp TIMESTAMPTZ NOT NULL,
            value DOUBLE PRECISION NOT NULL,
            labels JSONB DEFAULT '{}' NOT NULL,
            PRIMARY KEY (metric_id, timestamp, id)
        ) PARTITION BY RANGE (timestamp)
    """)

    # Create initial partition - system will create more as needed
    op.execute("""
        CREATE TABLE metrics.time_series_y2025m09
        PARTITION OF metrics.time_series
        FOR VALUES FROM ('2025-09-01') TO ('2025-10-01')
    """)

    # Create aggregations table - also partitioned by time
    op.execute("""
        CREATE TABLE metrics.aggregations (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            metric_id UUID NOT NULL REFERENCES metrics.metrics(id),
            timestamp TIMESTAMPTZ NOT NULL,
            window_start TIMESTAMPTZ NOT NULL,
            window_end TIMESTAMPTZ NOT NULL,
            aggregation_type metrics.aggregation_type NOT NULL,
            value DOUBLE PRECISION NOT NULL,
            sample_count INTEGER NOT NULL,
            labels JSONB DEFAULT '{}' NOT NULL,
            PRIMARY KEY (metric_id, timestamp, aggregation_type, id)
        ) PARTITION BY RANGE (timestamp)
    """)

    # Create initial aggregations partition
    op.execute("""
        CREATE TABLE metrics.aggregations_y2025m09
        PARTITION OF metrics.aggregations
        FOR VALUES FROM ('2025-09-01') TO ('2025-10-01')
    """)

    # Create alerts table
    op.create_table('alerts',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('metric_id', UUID(as_uuid=True), sa.ForeignKey('metrics.metrics.id'), nullable=False),
        sa.Column('condition', sa.Text(), nullable=False),  # SQL-like condition
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('comparison', sa.String(50), nullable=False),  # gt, lt, gte, lte, eq, ne
        sa.Column('window', sa.Interval(), nullable=False),
        sa.Column('labels_filter', JSONB, nullable=False, server_default='{}'),
        sa.Column('severity', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),
        schema='metrics'
    )

    # Create alert history table - also partitioned
    op.execute("""
        CREATE TABLE metrics.alert_history (
            id UUID DEFAULT gen_random_uuid() NOT NULL,
            alert_id UUID NOT NULL REFERENCES metrics.alerts(id),
            timestamp TIMESTAMPTZ NOT NULL,
            status TEXT NOT NULL,
            value DOUBLE PRECISION NOT NULL,
            message TEXT,
            labels JSONB DEFAULT '{}' NOT NULL,
            PRIMARY KEY (alert_id, timestamp, id)
        ) PARTITION BY RANGE (timestamp)
    """)

    # Create initial alert history partition
    op.execute("""
        CREATE TABLE metrics.alert_history_y2025m09
        PARTITION OF metrics.alert_history
        FOR VALUES FROM ('2025-09-01') TO ('2025-10-01')
    """)

    # Create metrics_service_mapping table
    op.create_table('metrics_service_mapping',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('metric_id', UUID(as_uuid=True), sa.ForeignKey('metrics.metrics.id'), nullable=False),
        sa.Column('service_name', sa.String(255), nullable=False),
        sa.Column('instance_id', sa.String(255), nullable=False),
        sa.Column('labels', JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        schema='metrics'
    )

    # Create indices
    op.create_index('ix_metrics_metrics_name', 'metrics', ['name'], schema='metrics')
    op.create_index('ix_metrics_alerts_name', 'alerts', ['name'], schema='metrics')
    op.create_index('ix_metrics_alerts_metric_id', 'alerts', ['metric_id'], schema='metrics')
    op.create_index('ix_metrics_service_mapping_service_name', 'metrics_service_mapping',
                  ['service_name'], schema='metrics')
    op.create_index('ix_metrics_service_mapping_instance_id', 'metrics_service_mapping',
                  ['instance_id'], schema='metrics')

    # Create hypertable conversion function for TimescaleDB (if used)
    op.execute("""
        CREATE OR REPLACE FUNCTION metrics.create_metric_partitions()
        RETURNS void AS $$
        DECLARE
            current_month DATE;
            partition_name TEXT;
            start_date TEXT;
            end_date TEXT;
        BEGIN
            -- Create partitions for next 3 months
            FOR i IN 0..2 LOOP
                current_month := date_trunc('month', now()) + (interval '1 month' * i);
                partition_name := 'time_series_y' || 
                                 to_char(current_month, 'YYYY') || 
                                 'm' || 
                                 to_char(current_month, 'MM');
                start_date := to_char(current_month, 'YYYY-MM-DD');
                end_date := to_char(current_month + interval '1 month', 'YYYY-MM-DD');
                
                -- Create time series partition
                EXECUTE format(
                    'CREATE TABLE IF NOT EXISTS metrics.%I ' ||
                    'PARTITION OF metrics.time_series ' ||
                    'FOR VALUES FROM (%L) TO (%L)',
                    partition_name, start_date, end_date
                );
                
                -- Create aggregations partition
                EXECUTE format(
                    'CREATE TABLE IF NOT EXISTS metrics.aggregations_%s ' ||
                    'PARTITION OF metrics.aggregations ' ||
                    'FOR VALUES FROM (%L) TO (%L)',
                    substring(partition_name FROM 13),
                    start_date, end_date
                );
                
                -- Create alert history partition
                EXECUTE format(
                    'CREATE TABLE IF NOT EXISTS metrics.alert_history_%s ' ||
                    'PARTITION OF metrics.alert_history ' ||
                    'FOR VALUES FROM (%L) TO (%L)',
                    substring(partition_name FROM 13),
                    start_date, end_date
                );
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create updated_at trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION metrics.update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Add triggers
    for table in ['metrics', 'alerts', 'metrics_service_mapping']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_modtime
                BEFORE UPDATE ON metrics.{table}
                FOR EACH ROW
                EXECUTE FUNCTION metrics.update_updated_at_column();
        """)

def downgrade() -> None:
    """Remove metrics schema and all tables."""
    # Drop triggers
    for table in ['metrics', 'alerts', 'metrics_service_mapping']:
        op.execute(f'DROP TRIGGER IF EXISTS update_{table}_modtime ON metrics.{table}')
    op.execute('DROP FUNCTION IF EXISTS metrics.update_updated_at_column()')
    op.execute('DROP FUNCTION IF EXISTS metrics.create_metric_partitions()')

    # Drop indices
    op.drop_index('ix_metrics_service_mapping_instance_id', table_name='metrics_service_mapping',
                schema='metrics')
    op.drop_index('ix_metrics_service_mapping_service_name', table_name='metrics_service_mapping',
                schema='metrics')
    op.drop_index('ix_metrics_alerts_metric_id', table_name='alerts', schema='metrics')
    op.drop_index('ix_metrics_alerts_name', table_name='alerts', schema='metrics')
    op.drop_index('ix_metrics_metrics_name', table_name='metrics', schema='metrics')

    # Drop tables
    op.execute('DROP TABLE IF EXISTS metrics.alert_history_y2025m09')
    op.execute('DROP TABLE IF EXISTS metrics.alert_history')
    op.drop_table('metrics_service_mapping', schema='metrics')
    op.drop_table('alerts', schema='metrics')
    op.execute('DROP TABLE IF EXISTS metrics.aggregations_y2025m09')
    op.execute('DROP TABLE IF EXISTS metrics.aggregations')
    op.execute('DROP TABLE IF EXISTS metrics.time_series_y2025m09')
    op.execute('DROP TABLE IF EXISTS metrics.time_series')
    op.drop_table('metrics', schema='metrics')

    # Drop enums
    op.execute('DROP TYPE metrics.retention_policy')
    op.execute('DROP TYPE metrics.aggregation_type')
    op.execute('DROP TYPE metrics.metric_type')

    # Drop schema
    op.execute('DROP SCHEMA metrics')  