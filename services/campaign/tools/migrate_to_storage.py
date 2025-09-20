#!/usr/bin/env python
"""Migration utilities for moving to storage service."""
import argparse
import asyncio
import json
from datetime import datetime
import os
from pathlib import Path
import sys
from typing import Any, Dict, List
from uuid import UUID

import asyncpg
import httpx
from pydantic import BaseModel, Field


class MigrationConfig(BaseModel):
    """Migration configuration."""
    source_dsn: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/campaign",
        description="Source database connection string",
    )
    schema_dir: Path = Field(
        default=Path("migrations/storage"),
        description="Directory for schema/data exports",
    )
    storage_url: str = Field(
        default="http://localhost:8000",
        description="Storage service URL",
    )
    storage_token: str = Field(
        default="",
        description="Storage service auth token",
    )
    batch_size: int = Field(
        default=1000,
        description="Batch size for data migration",
    )
    dry_run: bool = Field(
        default=False,
        description="Dry run mode",
    )


class DatabaseExporter:
    """Database schema and data exporter."""
    
    def __init__(self, config: MigrationConfig) -> None:
        """Initialize exporter.
        
        Args:
            config: Migration configuration
        """
        self.config = config
    
    async def export_schema(self) -> None:
        """Export database schema."""
        # Create output directory
        self.config.schema_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        conn = await asyncpg.connect(self.config.source_dsn)
        try:
            # Get table schemas
            tables = await conn.fetch("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
            """)
            
            schemas = {}
            for table in tables:
                table_name = table["table_name"]
                
                # Get column definitions
                columns = await conn.fetch("""
                    SELECT column_name, data_type, character_maximum_length,
                           is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = $1
                    ORDER BY ordinal_position
                """, table_name)
                
                # Get constraints
                constraints = await conn.fetch("""
                    SELECT c.conname, c.contype,
                           array_agg(a.attname ORDER BY a.attnum) as columns,
                           confrelid::regclass::text as referenced_table,
                           array_agg(af.attname ORDER BY af.attnum) as referenced_columns
                    FROM pg_constraint c
                    JOIN pg_attribute a ON a.attrelid = c.conrelid
                    AND a.attnum = ANY(c.conkey)
                    LEFT JOIN pg_attribute af ON af.attrelid = c.confrelid
                    AND af.attnum = ANY(c.confkey)
                    WHERE c.conrelid = $1::regclass
                    GROUP BY c.conname, c.contype, confrelid
                """, table_name)
                
                # Build schema definition
                schema = {
                    "columns": [
                        {
                            "name": col["column_name"],
                            "type": col["data_type"],
                            "length": col["character_maximum_length"],
                            "nullable": col["is_nullable"] == "YES",
                            "default": col["column_default"],
                        }
                        for col in columns
                    ],
                    "constraints": [
                        {
                            "name": con["conname"],
                            "type": con["contype"],
                            "columns": con["columns"],
                            "referenced_table": con["referenced_table"],
                            "referenced_columns": con["referenced_columns"],
                        }
                        for con in constraints
                    ],
                }
                schemas[table_name] = schema
                
            # Save schema
            schema_file = self.config.schema_dir / "schema.json"
            schema_file.write_text(
                json.dumps(schemas, indent=2)
            )
            print(f"Saved schema to {schema_file}")
            
        finally:
            await conn.close()
    
    async def export_data(self) -> None:
        """Export table data."""
        conn = await asyncpg.connect(self.config.source_dsn)
        try:
            # Get list of tables
            tables = await conn.fetch("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
            """)
            
            for table in tables:
                table_name = table["table_name"]
                print(f"Exporting {table_name}...")
                
                # Get total rows
                total = await conn.fetchval(f"""
                    SELECT count(*) FROM {table_name}
                """)
                
                # Export in batches
                offset = 0
                while offset < total:
                    rows = await conn.fetch(f"""
                        SELECT *
                        FROM {table_name}
                        ORDER BY id
                        LIMIT {self.config.batch_size}
                        OFFSET {offset}
                    """)
                    
                    # Convert to dicts
                    data = [dict(row) for row in rows]
                    
                    # Convert UUIDs and timestamps to strings
                    for row in data:
                        for key, value in row.items():
                            if isinstance(value, UUID):
                                row[key] = str(value)
                            elif isinstance(value, datetime):
                                row[key] = value.isoformat()
                    
                    # Save batch
                    batch_file = self.config.schema_dir / f"{table_name}_{offset}.json"
                    batch_file.write_text(
                        json.dumps(data, indent=2)
                    )
                    print(f"Saved {len(data)} rows to {batch_file}")
                    
                    offset += self.config.batch_size
            
        finally:
            await conn.close()


class StorageImporter:
    """Storage service data importer."""
    
    def __init__(self, config: MigrationConfig) -> None:
        """Initialize importer.
        
        Args:
            config: Migration configuration
        """
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.storage_url,
            headers={
                "Authorization": f"Bearer {config.storage_token}",
            },
        )
    
    async def validate_schema(self) -> bool:
        """Validate schema against storage service.
        
        Returns:
            True if schema is valid
        """
        # Load schema
        schema_file = self.config.schema_dir / "schema.json"
        if not schema_file.exists():
            print("Schema file not found")
            return False
            
        schema = json.loads(schema_file.read_text())
        
        # Validate against storage service
        async with self.client as client:
            response = await client.post(
                "/api/v2/storage/validate_schema",
                json={"schema": schema},
            )
            
            if response.status_code != 200:
                print(f"Schema validation failed: {response.text}")
                return False
                
            result = response.json()
            if not result.get("valid"):
                print(f"Schema validation failed: {result.get('errors')}")
                return False
                
            return True
    
    async def import_data(self, table: str) -> bool:
        """Import data for table.
        
        Args:
            table: Table name
            
        Returns:
            True if import successful
        """
        if self.config.dry_run:
            print(f"[DRY RUN] Would import data for {table}")
            return True
            
        # Get data files
        data_files = sorted(
            self.config.schema_dir.glob(f"{table}_*.json")
        )
        if not data_files:
            print(f"No data files found for {table}")
            return False
            
        # Import each batch
        async with self.client as client:
            for data_file in data_files:
                data = json.loads(data_file.read_text())
                
                response = await client.post(
                    f"/api/v2/storage/tables/{table}/batch",
                    json={"records": data},
                )
                
                if response.status_code != 200:
                    print(f"Failed to import {data_file}: {response.text}")
                    return False
                    
                print(f"Imported {len(data)} rows from {data_file}")
            
        return True


async def run_migration(config_file: str, dry_run: bool = False) -> int:
    """Run database migration.
    
    Args:
        config_file: Path to config file
        dry_run: Dry run mode
        
    Returns:
        Exit code
    """
    # Load config
    if os.path.exists(config_file):
        config = MigrationConfig.model_validate(
            json.loads(Path(config_file).read_text())
        )
    else:
        config = MigrationConfig()
        
    # Override dry run
    config.dry_run = dry_run
    
    # Export schema and data
    exporter = DatabaseExporter(config)
    await exporter.export_schema()
    await exporter.export_data()
    
    # Import to storage service
    importer = StorageImporter(config)
    if not await importer.validate_schema():
        return 1
        
    # Get tables from schema
    schema_file = config.schema_dir / "schema.json"
    schema = json.loads(schema_file.read_text())
    
    # Import each table
    success = True
    for table in schema.keys():
        if not await importer.import_data(table):
            success = False
            
    return 0 if success else 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate database to storage service",
    )
    parser.add_argument(
        "--config",
        default="migrations/config.json",
        help="Path to config file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode",
    )
    
    args = parser.parse_args()
    
    return asyncio.run(run_migration(
        config_file=args.config,
        dry_run=args.dry_run,
    ))


if __name__ == "__main__":
    sys.exit(main())